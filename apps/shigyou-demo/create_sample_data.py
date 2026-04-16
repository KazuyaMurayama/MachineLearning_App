"""
士業向けサンプルデータ生成 v2
=============================
品質チェック結果に基づき改善:
- 月額顧問料の価格帯を現実に合わせ拡張（¥1万-30万の9段階）
- 業種分布を税理士事務所の実態に合わせ修正（建設・飲食・不動産の比率↑）
- 連絡頻度をpoisson(4)に修正（疎遠な先=0回も含む）
- 質問数トレンドの左裾を厚く（離反前の「沈黙」パターン）
- 4特徴量を追加: 最終面談経過日数、顧問料改定、顧問先売上成長率、レポート遅延

データソース対応:
- freee/MF API: 月額顧問料、入金遅延、顧問先売上成長率
- CRM/カレンダー: 契約年数、面談回数、最終面談経過日数、担当変更
- Chatwork/Slack/メール: 連絡頻度、質問数トレンド
- 営業管理Excel: 価格交渉、オプション利用率、顧問料改定、業種・規模
- 業務管理: 月次レポート提出遅延日数
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 150

# ============================================================
# 既存特徴量（修正版）
# ============================================================

# 1. 契約年数 — 営業管理Excel/CRM
#    業界平均5-8年。指数分布で新規先も含める
contract_years = np.random.exponential(5, N).clip(0.5, 25).round(1)

# 2. 月額顧問料（円）— freee/MFの請求データ
#    PRONIアイミツ調査: 個人¥1-3万, 小規模¥3-5万, 中規模¥5-10万, 大規模¥10-30万
monthly_fee = np.random.choice(
    [10000, 20000, 30000, 50000, 80000, 100000, 150000, 200000, 300000],
    N,
    p=[0.05, 0.10, 0.20, 0.25, 0.15, 0.12, 0.07, 0.04, 0.02],
)

# 3. 直近3ヶ月連絡頻度 — Chatwork/Slack/メール
#    poisson(4): 平均月1.3回。疎遠な先(0回)が約5%含まれる
contact_freq_3m = np.random.poisson(4, N).clip(0, 20)

# 4. 直近6ヶ月面談回数 — カレンダー/CRM
#    月次面談が理想だが実際は隔月程度。poisson(3)で0-8回
meeting_count_6m = np.random.poisson(3, N).clip(0, 12)

# 5. 質問数トレンド — Chatwork/Slack/メールの前期比
#    左裾を厚く: 離反前の「沈黙」パターンを反映
#    skewnorm的な分布を近似: 20%が-1以下（急減）
question_trend = np.concatenate([
    np.random.normal(-1.5, 0.8, int(N * 0.15)),  # 急減群（離反予備軍）
    np.random.normal(0, 0.8, int(N * 0.65)),      # 安定群
    np.random.normal(1.0, 0.6, N - int(N * 0.15) - int(N * 0.65)),  # 活発群
])
np.random.shuffle(question_trend)
question_trend = question_trend.round(2)

# 6. 直近12ヶ月の入金遅延回数 — freee/MFの入金消込データ
payment_delay_count = np.random.poisson(0.8, N).clip(0, 8)

# 7. 累計担当変更回数 — 営業管理Excel/CRM
staff_change_count = np.random.poisson(0.5, N).clip(0, 4)

# 8. 価格交渉フラグ — 営業管理/対応履歴（手動記録）
fee_negotiation = np.random.binomial(1, 0.20, N)

# 9. オプションサービス利用率 — 営業管理Excel
#    0%（基本顧問のみ）の先を20%含める
_base_ratio = np.random.beta(2, 3, N).round(2)
_zero_mask = np.random.binomial(1, 0.20, N).astype(bool)
service_usage_ratio = np.where(_zero_mask, 0.0, _base_ratio)

# 10. 顧問先従業員規模 — freee/MFの顧問先プロフィール
company_size = np.random.choice(
    ["1-5名", "6-10名", "11-30名", "31-50名", "51-100名", "100名以上"],
    N,
    p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05],
)

# 11. 顧問先業種 — freee/MFの業種コード
#     修正: 建設・飲食・不動産の比率を上げ、現実に近づける
industry = np.random.choice(
    ["建設業", "飲食業", "不動産", "小売業", "製造業", "サービス業", "IT", "医療"],
    N,
    p=[0.18, 0.15, 0.14, 0.13, 0.12, 0.12, 0.08, 0.08],
)

# ============================================================
# 新規追加特徴量（4つ）
# ============================================================

# A. 最終面談からの経過日数 — カレンダー/CRM
#    面談回数と相関させる。面談が少ない先ほど経過日数が長い
_base_days = 180 - meeting_count_6m * 25 + np.random.normal(0, 20, N)
days_since_last_meeting = _base_days.clip(7, 365).astype(int)

# B. 直近12ヶ月の顧問料改定 — 請求管理データ
#    -1=値下げ(5%), 0=据え置き(80%), 1=値上げ(15%)
fee_revision = np.random.choice([-1, 0, 1], N, p=[0.05, 0.80, 0.15])

# C. 顧問先売上成長率（前年比 %）— freee/MF API試算表データ
#    正規分布で平均+3%（GDP+α）。業績悪化先は-20%まで
client_revenue_growth = np.random.normal(3, 12, N).clip(-30, 50).round(1)

# D. 月次レポート提出遅延日数 — 業務管理データ
#    大半は0-3日。品質問題のある先は10日超
report_delay_days = np.random.exponential(2, N).clip(0, 20).round(0).astype(int)

# ============================================================
# 目的変数: 解約までの予測月数（低い=離反リスク高）
# ============================================================
# 目標分布: 高リスク(<=12M) 10-20%, 中リスク(12-24M) 25-35%, 低リスク(>24M) 残り

base_months = 24.0
churn_months = (
    base_months
    + contract_years * 0.6
    + np.log1p(monthly_fee / 10000) * 1.8
    + contact_freq_3m * 0.4
    + meeting_count_6m * 1.2
    + question_trend * 4.5       # 沈黙=離反リスク大
    - payment_delay_count * 5.0
    - staff_change_count * 5.5
    - fee_negotiation * 7.0
    + service_usage_ratio * 5.5
    - days_since_last_meeting * 0.04  # ★新: 疎遠=離反リスク大
    - fee_revision * 4.0             # ★新: 値上げ=離反リスク大
    + client_revenue_growth * 0.20   # ★新: 業績悪化=離反リスク大
    - report_delay_days * 1.0        # ★新: 遅延=品質問題=離反リスク大
    + np.random.normal(0, 3.0, N)   # ノイズ縮小: 4.5→3.0
)
churn_months = churn_months.clip(2, 60).round(1)

# ============================================================
# DataFrame構築
# ============================================================
df = pd.DataFrame({
    "顧問先ID": [f"C{str(i + 1).zfill(3)}" for i in range(N)],
    "契約年数": contract_years,
    "月額顧問料": monthly_fee.astype(int),
    "直近3ヶ月連絡頻度": contact_freq_3m,
    "直近6ヶ月面談回数": meeting_count_6m,
    "質問数トレンド": question_trend,
    "直近12ヶ月入金遅延回数": payment_delay_count,
    "累計担当変更回数": staff_change_count,
    "価格交渉フラグ": fee_negotiation,
    "オプションサービス利用率": service_usage_ratio,
    "顧問先従業員規模": company_size,
    "顧問先業種": industry,
    # --- 新規追加 ---
    "最終面談からの経過日数": days_since_last_meeting,
    "直近12ヶ月顧問料改定": fee_revision,
    "顧問先売上成長率": client_revenue_growth,
    "月次レポート提出遅延日数": report_delay_days,
    # --- 目的変数 ---
    "解約までの予測月数": churn_months,
})

# ============================================================
# 分布確認
# ============================================================
n_high = (churn_months <= 12).sum()
n_med = ((churn_months > 12) & (churn_months <= 24)).sum()
n_low = (churn_months > 24).sum()
print(f"Distribution: High-risk(<=12M)={n_high} ({n_high/N*100:.0f}%), "
      f"Mid-risk(12-24M)={n_med} ({n_med/N*100:.0f}%), "
      f"Low-risk(>24M)={n_low} ({n_low/N*100:.0f}%)")
print(f"Stats: min={churn_months.min():.1f}, median={np.median(churn_months):.1f}, "
      f"max={churn_months.max():.1f}")
print(f"Features: {len(df.columns) - 2} (excluding ID and target)")

# ============================================================
# 保存
# ============================================================
out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(out_dir, exist_ok=True)

df.to_csv(os.path.join(out_dir, "shigyou_train.csv"), index=False, encoding="utf-8-sig")

df_target = (df.drop(columns=["解約までの予測月数"])
             .sample(30, random_state=99)
             .reset_index(drop=True))
df_target.to_csv(os.path.join(out_dir, "shigyou_target.csv"), index=False, encoding="utf-8-sig")

print(f"Saved: {len(df)} train + {len(df_target)} target → {out_dir}")
