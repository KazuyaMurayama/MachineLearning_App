"""
士業向けサンプルデータ生成
=========================
税理士事務所の顧問先データを合成生成する。
離反予測モデルのデモ用。
高リスク・中リスク・低リスクがバランスよく含まれるよう設計。
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 150  # 顧問先数

# --- 特徴量 ---
contract_years = np.random.exponential(5, N).clip(0.5, 25).round(1)
monthly_fee = np.random.choice([30000, 50000, 80000, 100000, 150000, 200000, 300000], N,
                               p=[0.10, 0.25, 0.25, 0.20, 0.10, 0.07, 0.03])
contact_freq_3m = np.random.poisson(6, N).clip(0, 30)
meeting_count_6m = np.random.poisson(3, N).clip(0, 12)
question_trend = np.random.normal(0, 1, N).round(2)  # 正=増加, 負=減少
payment_delay_count = np.random.poisson(0.8, N).clip(0, 8)
staff_change_count = np.random.poisson(0.5, N).clip(0, 4)
fee_negotiation = np.random.binomial(1, 0.20, N)
service_usage_ratio = np.random.beta(2, 3, N).round(2)  # 低め寄り
company_size = np.random.choice(
    ["1-5名", "6-10名", "11-30名", "31-50名", "51-100名", "100名以上"], N,
    p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05]
)
industry = np.random.choice(
    ["製造業", "小売業", "IT", "飲食業", "建設業", "サービス業", "不動産", "医療"],
    N, p=[0.15, 0.15, 0.15, 0.10, 0.12, 0.13, 0.10, 0.10]
)

# --- 目的変数: 解約までの予測月数（低い=離反リスク高） ---
# 高リスク(12ヶ月以内)が15-20%、中リスク(12-24ヶ月)が25-30%、低リスク(24ヶ月超)が残り
base_months = 20.0  # ベースを下げて分布を広げる
churn_months = (
    base_months
    + contract_years * 0.6
    + np.log1p(monthly_fee / 10000) * 1.5
    + contact_freq_3m * 0.4
    + meeting_count_6m * 1.2
    + question_trend * 3.5
    - payment_delay_count * 4.5
    - staff_change_count * 5.5
    - fee_negotiation * 7.0
    + service_usage_ratio * 5.0
    + np.random.normal(0, 5, N)
)
churn_months = churn_months.clip(2, 60).round(1)

df = pd.DataFrame({
    "顧問先ID": [f"C{str(i+1).zfill(3)}" for i in range(N)],
    "契約年数": contract_years,
    "月額顧問料": monthly_fee.astype(int),
    "直近3ヶ月連絡頻度": contact_freq_3m,
    "直近6ヶ月面談回数": meeting_count_6m,
    "質問数トレンド": question_trend,
    "入金遅延回数": payment_delay_count,
    "担当変更回数": staff_change_count,
    "価格交渉フラグ": fee_negotiation,
    "オプションサービス利用率": service_usage_ratio,
    "顧問先従業員規模": company_size,
    "顧問先業種": industry,
    "解約までの予測月数": churn_months,
})

# 分布確認
n_high = (churn_months <= 12).sum()
n_med = ((churn_months > 12) & (churn_months <= 24)).sum()
n_low = (churn_months > 24).sum()
print(f"Distribution: High-risk(<=12M)={n_high}, Mid-risk(12-24M)={n_med}, Low-risk(>24M)={n_low}")
print(f"Stats: min={churn_months.min():.1f}, median={np.median(churn_months):.1f}, max={churn_months.max():.1f}")

# 保存
out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(out_dir, exist_ok=True)

# 訓練用（目的変数あり）
df.to_csv(os.path.join(out_dir, "shigyou_train.csv"), index=False, encoding="utf-8-sig")

# 予測用（目的変数なし）
df_target = df.drop(columns=["解約までの予測月数"]).sample(30, random_state=99).reset_index(drop=True)
df_target.to_csv(os.path.join(out_dir, "shigyou_target.csv"), index=False, encoding="utf-8-sig")

print(f"Generated {len(df)} training samples and {len(df_target)} target samples")
print(f"Files saved to {out_dir}")
