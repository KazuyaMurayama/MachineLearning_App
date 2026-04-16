"""
EC月次AIブリーフィング サンプルデータ生成
"""
import numpy as np
import pandas as pd
import os

# === 共通マスター（ec-executive-dashboard と同一seed） ===
np.random.seed(42)

N_PRODUCT = 100
categories = np.random.choice(["アパレル","食品","コスメ","家電","雑貨"], N_PRODUCT, p=[0.30,0.25,0.20,0.10,0.15])
products = pd.DataFrame({
    "商品ID": [f"P{i:03d}" for i in range(1, N_PRODUCT+1)],
    "カテゴリ": categories,
    "単価": np.random.choice([1000,2000,3000,5000,8000,12000,20000,50000], N_PRODUCT, p=[0.15,0.20,0.20,0.15,0.12,0.10,0.06,0.02]),
    "在庫数": np.random.poisson(80, N_PRODUCT).clip(0, 500),
    "原価率": np.round(np.random.uniform(0.3, 0.7, N_PRODUCT), 2),
})

N_CUSTOMER = 500
customers = pd.DataFrame({
    "顧客ID": [f"U{i:04d}" for i in range(1, N_CUSTOMER+1)],
    "年齢層": np.random.choice(["20代","30代","40代","50代","60代+"], N_CUSTOMER, p=[0.20,0.30,0.25,0.15,0.10]),
    "累計購入回数": np.random.poisson(5, N_CUSTOMER).clip(1, 50),
    "累計購入額": np.random.lognormal(10, 1, N_CUSTOMER).astype(int).clip(10000, 2000000),
    "最終購入経過日数": np.random.randint(1, 365, N_CUSTOMER),
    "離脱リスクスコア": (np.random.beta(2,5,N_CUSTOMER)*100).round(1),
    "RFMセグメント": np.random.choice(["Champions","Loyal","AtRisk","Lost","New"], N_CUSTOMER, p=[0.15,0.25,0.20,0.20,0.20]),
})

months = pd.date_range("2025-04-01", periods=13, freq="MS").strftime("%Y-%m")
channels = ["Google","Yahoo","Meta","TikTok","LINE"]
cat_list = ["アパレル","食品","コスメ","家電","雑貨"]
orders = []
for m in months:
    for ch in channels:
        for cat in cat_list:
            base = np.random.randint(500, 3000)
            avg_price = np.random.randint(3000, 15000)
            revenue = base * avg_price
            gross_profit = int(revenue * np.random.uniform(0.3, 0.5))
            orders.append({"年月": m, "チャネル": ch, "カテゴリ": cat, "注文数": base, "売上": revenue, "粗利": gross_profit})
orders_df = pd.DataFrame(orders)

ads = []
for m in months:
    for ch in channels:
        budget = np.random.randint(500000, 3000000)
        impressions = budget * np.random.randint(10, 30)
        clicks = int(impressions * np.random.uniform(0.01, 0.03))
        cv = int(clicks * np.random.uniform(0.02, 0.08))
        revenue = cv * np.random.randint(5000, 20000)
        ads.append({
            "年月": m, "チャネル": ch, "広告費": budget,
            "インプレッション": impressions, "クリック": clicks, "CV数": cv,
            "売上": revenue, "ROAS": round(revenue/budget, 2), "CPA": round(budget/max(cv,1), 0),
        })
ads_df = pd.DataFrame(ads)

out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(out_dir, exist_ok=True)
products.to_csv(os.path.join(out_dir, "products.csv"), index=False, encoding="utf-8-sig")
customers.to_csv(os.path.join(out_dir, "customers.csv"), index=False, encoding="utf-8-sig")
orders_df.to_csv(os.path.join(out_dir, "orders.csv"), index=False, encoding="utf-8-sig")
ads_df.to_csv(os.path.join(out_dir, "ads.csv"), index=False, encoding="utf-8-sig")
print("Saved 4 CSVs")
