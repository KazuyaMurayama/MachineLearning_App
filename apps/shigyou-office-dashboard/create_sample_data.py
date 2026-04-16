"""
事務所経営ダッシュボード サンプルデータ生成
==========================================
共通マスター（3アプリ間で同一のseed・データ）
- office_master.csv: 顧問先150社の月次データ
- monthly_kpi.csv: 過去13ヶ月のMRR推移
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 150

# ============================================================
# 顧問先マスターデータ
# ============================================================

# 顧問先ID: C001〜C150
client_ids = [f"C{str(i + 1).zfill(3)}" for i in range(N)]

# 顧問先名（仮称）
prefixes = ["株式会社", "有限会社", "合同会社"]
suffixes = [
    "山田商事", "鈴木工業", "田中建設", "佐藤食品", "高橋不動産",
    "渡辺サービス", "伊藤製作所", "小林医院", "加藤商店", "吉田電機",
    "中村建工", "山本フーズ", "林産業", "清水ホーム", "松本運輸",
    "井上設計", "木村クリニック", "橋本IT", "池田商会", "阿部工務店",
]
client_names = []
for i in range(N):
    prefix = np.random.choice(prefixes, p=[0.6, 0.2, 0.2])
    suffix_base = suffixes[i % len(suffixes)]
    num = (i // len(suffixes)) + 1
    if num > 1:
        client_names.append(f"{prefix}{suffix_base}{num}号")
    else:
        client_names.append(f"{prefix}{suffix_base}")

# 業種
industry = np.random.choice(
    ["建設業", "飲食業", "不動産", "小売業", "製造業", "サービス業", "IT", "医療"],
    N,
    p=[0.18, 0.15, 0.14, 0.13, 0.12, 0.12, 0.08, 0.08],
)

# 月額顧問料（円）
monthly_fee = np.random.choice(
    [10000, 20000, 30000, 50000, 80000, 100000, 150000, 200000, 300000],
    N,
    p=[0.05, 0.10, 0.20, 0.25, 0.15, 0.12, 0.07, 0.04, 0.02],
)

# 担当者
staff = np.random.choice(
    ["担当A", "担当B", "担当C", "担当D", "担当E"],
    N,
    p=[0.20, 0.20, 0.20, 0.20, 0.20],
)

# 契約年数
contract_years = np.random.exponential(5, N).clip(0.5, 25).round(1)

# 離反リスクスコア: beta(2,5)*100
churn_risk_score = (np.random.beta(2, 5, N) * 100).round(1)

# 直近入金遅延日数: poisson(5).clip(0,45)
payment_delay_days = np.random.poisson(5, N).clip(0, 45).astype(int)

# 累計入金遅延回数: poisson(0.8).clip(0,8)
payment_delay_count = np.random.poisson(0.8, N).clip(0, 8).astype(int)

# クロスセル機会数: randint(0,6)
crosssell_opportunities = np.random.randint(0, 6, N)

# クロスセル推定増収額: 機会数 × choice([50000,80000,100000,150000,200000])の合計
crosssell_amounts = np.array([
    sum(np.random.choice([50000, 80000, 100000, 150000, 200000], k)) if k > 0 else 0
    for k in crosssell_opportunities
])

# 当月レポート異常フラグ: binomial(1, 0.12)
report_anomaly_flag = np.random.binomial(1, 0.12, N)

# 当月売上前月比(%): normal(2,15).clip(-30,50).round(1)
sales_mom_pct = np.random.normal(2, 15, N).clip(-30, 50).round(1)

# ============================================================
# DataFrame構築
# ============================================================
df = pd.DataFrame({
    "顧問先ID": client_ids,
    "顧問先名": client_names,
    "業種": industry,
    "月額顧問料": monthly_fee.astype(int),
    "担当者": staff,
    "契約年数": contract_years,
    "離反リスクスコア": churn_risk_score,
    "直近入金遅延日数": payment_delay_days,
    "累計入金遅延回数": payment_delay_count,
    "クロスセル機会数": crosssell_opportunities,
    "クロスセル推定増収額": crosssell_amounts.astype(int),
    "当月レポート異常フラグ": report_anomaly_flag,
    "当月売上前月比": sales_mom_pct,
})

# ============================================================
# 月次KPIデータ（過去13ヶ月）
# ============================================================
import pandas as pd

# 基準月: 2026年4月。過去13ヶ月 = 2025年3月〜2026年3月
months = pd.date_range(end="2026-03-01", periods=13, freq="MS")
year_months = [m.strftime("%Y年%m月") for m in months]

# MRR（月次経常収益）: 顧問先150社の月額顧問料合計をベースに上昇トレンド
base_mrr = int(monthly_fee.sum())
mrr_trend = np.linspace(base_mrr * 0.88, base_mrr, 13)
mrr_noise = np.random.normal(0, base_mrr * 0.02, 13)
mrr_values = (mrr_trend + mrr_noise).clip(0).round(0).astype(int)

# 新規件数: poisson(2)
new_clients = np.random.poisson(2, 13).clip(0, 8).astype(int)

# 解約件数: poisson(0.8)
churn_clients = np.random.poisson(0.8, 13).clip(0, 4).astype(int)

kpi_df = pd.DataFrame({
    "年月": year_months,
    "MRR合計": mrr_values,
    "新規件数": new_clients,
    "解約件数": churn_clients,
})

# ============================================================
# 保存
# ============================================================
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")
os.makedirs(out_dir, exist_ok=True)

master_path = os.path.join(out_dir, "office_master.csv")
kpi_path = os.path.join(out_dir, "monthly_kpi.csv")

df.to_csv(master_path, index=False, encoding="utf-8-sig")
kpi_df.to_csv(kpi_path, index=False, encoding="utf-8-sig")

print(f"office_master.csv: {len(df)} 行 → {master_path}")
print(f"monthly_kpi.csv: {len(kpi_df)} 行 → {kpi_path}")
print(f"月額顧問料合計（MRR）: ¥{monthly_fee.sum():,}")
print(f"離反リスクスコア: mean={churn_risk_score.mean():.1f}, max={churn_risk_score.max():.1f}")
print(f"クロスセル推定増収額合計: ¥{crosssell_amounts.sum():,}")
