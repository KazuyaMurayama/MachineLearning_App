"""
士業向けサンプルデータ生成
=========================
税理士事務所の顧問先データを合成生成する。
離反予測モデルのデモ用。
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
payment_delay_count = np.random.poisson(0.5, N).clip(0, 8)
staff_change_count = np.random.poisson(0.3, N).clip(0, 4)
fee_negotiation = np.random.binomial(1, 0.15, N)
service_usage_ratio = np.random.beta(3, 2, N).round(2)
company_size = np.random.choice(
    ["1-5名", "6-10名", "11-30名", "31-50名", "51-100名", "100名以上"], N,
    p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05]
)
industry = np.random.choice(
    ["製造業", "小売業", "IT", "飲食業", "建設業", "サービス業", "不動産", "医療"],
    N, p=[0.15, 0.15, 0.15, 0.10, 0.12, 0.13, 0.10, 0.10]
)

# --- 目的変数: 解約までの予測月数（低い=離反リスク高） ---
base_months = 36.0
churn_months = (
    base_months
    + contract_years * 0.8
    + np.log1p(monthly_fee / 10000) * 2.0
    + contact_freq_3m * 0.5
    + meeting_count_6m * 1.5
    + question_trend * 3.0
    - payment_delay_count * 4.0
    - staff_change_count * 5.0
    - fee_negotiation * 8.0
    + service_usage_ratio * 6.0
    + np.random.normal(0, 4, N)
)
churn_months = churn_months.clip(1, 80).round(1)

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
