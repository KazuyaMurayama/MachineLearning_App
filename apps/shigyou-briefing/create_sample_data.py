"""
月次AIブリーフィングレポート サンプルデータ生成
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)  # 他2アプリと同一seed
N = 150

# === 共通マスター（他アプリと同一） ===
client_ids = [f"C{i:03d}" for i in range(1, N+1)]
industries = np.random.choice(
    ["建設業","飲食業","不動産","小売業","製造業","サービス業","IT","医療"],
    N, p=[0.18,0.15,0.14,0.13,0.12,0.12,0.08,0.08]
)
monthly_fees = np.random.choice(
    [10000,20000,30000,50000,80000,100000,150000,200000,300000],
    N, p=[0.05,0.10,0.20,0.25,0.15,0.12,0.07,0.04,0.02]
)
churn_risk = (np.random.beta(2,5,N)*100).round(1)
crosssell_revenue = np.random.randint(0, 5, N) * np.random.choice([50000,80000,100000,150000,200000], N)

# === ブリーフィング固有列 ===
# 担当者
staff = np.random.choice(["担当A","担当B","担当C","担当D","担当E"], N)
# 入金遅延（直近月）
payment_delay_days = np.random.poisson(3, N).clip(0, 45)
payment_delayed = (payment_delay_days > 0).astype(int)
# 当月面談実施フラグ
meeting_done = np.random.binomial(1, 0.65, N)
# 前月比売上成長率
mom_growth = np.random.normal(2, 15, N).clip(-40, 60).round(1)
# 前年同月比
yoy_growth = np.random.normal(5, 20, N).clip(-50, 80).round(1)
# クレーム（当月）
complaint_flag = np.random.binomial(1, 0.08, N)

# briefing_master.csv (150行)
df_master = pd.DataFrame({
    "顧問先ID": client_ids,
    "顧問先名": [f"顧問先{id_}" for id_ in client_ids],
    "業種": industries,
    "担当者": staff,
    "月額顧問料": monthly_fees,
    "離反リスクスコア": churn_risk,
    "クロスセル推定増収額": crosssell_revenue,
    "入金遅延日数": payment_delay_days,
    "入金遅延フラグ": payment_delayed,
    "当月面談実施": meeting_done,
    "当月売上前月比": mom_growth,
    "当月売上前年比": yoy_growth,
    "当月クレームフラグ": complaint_flag,
})

# monthly_history.csv: 顧問先ID × 過去13ヶ月のMRR集計
months = pd.date_range("2025-03-01", periods=13, freq="MS")
records = []
for m in months:
    yr_mo = m.strftime("%Y-%m")
    base_mrr = monthly_fees.sum()
    noise = np.random.normal(0, base_mrr * 0.02)
    new_clients = np.random.randint(1, 4)
    lost_clients = np.random.randint(0, 2)
    records.append({
        "年月": yr_mo,
        "MRR合計": int(base_mrr + noise),
        "新規件数": new_clients,
        "解約件数": lost_clients,
        "高リスク件数": int((churn_risk >= 70).sum() + np.random.randint(-3, 4)),
        "入金遅延件数": int((payment_delayed.sum()) + np.random.randint(-5, 6)),
    })
df_history = pd.DataFrame(records)

# 保存先
base_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(base_dir, "sample_data")
os.makedirs(out_dir, exist_ok=True)

df_master.to_csv(os.path.join(out_dir, "briefing_master.csv"), index=False, encoding="utf-8-sig")
df_history.to_csv(os.path.join(out_dir, "monthly_history.csv"), index=False, encoding="utf-8-sig")

print(f"briefing_master.csv: {len(df_master)} 行")
print(f"monthly_history.csv: {len(df_history)} 行")
print("サンプルデータ生成完了")
