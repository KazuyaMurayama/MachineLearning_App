"""
EC What-Ifシミュレーター サンプルデータ生成
"""
import numpy as np
import pandas as pd
import os

# === 共通マスター生成ブロック（3EC L3アプリで同一） ===
np.random.seed(42)

# 商品マスター (100商品)
N_PRODUCT = 100
categories = np.random.choice(["アパレル","食品","コスメ","家電","雑貨"], N_PRODUCT, p=[0.30,0.25,0.20,0.10,0.15])
products = pd.DataFrame({
    "商品ID": [f"P{i:03d}" for i in range(1, N_PRODUCT+1)],
    "カテゴリ": categories,
    "単価": np.random.choice([1000,2000,3000,5000,8000,12000,20000,50000], N_PRODUCT, p=[0.15,0.20,0.20,0.15,0.12,0.10,0.06,0.02]),
    "在庫数": np.random.poisson(80, N_PRODUCT).clip(0, 500),
    "原価率": np.round(np.random.uniform(0.3, 0.7, N_PRODUCT), 2),
})

# 顧客マスター (500顧客)
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

# 注文履歴 (13ヶ月 × 5チャネル × 5カテゴリ)
months = pd.date_range("2025-04-01", periods=13, freq="MS").strftime("%Y-%m").tolist()
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
            orders.append({
                "年月": m, "チャネル": ch, "カテゴリ": cat,
                "注文数": base, "売上": revenue, "粗利": gross_profit,
            })
orders_df = pd.DataFrame(orders)

# 広告実績 (13ヶ月 × 5チャネル)
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

# === What-If固有: 学習データ（13ヶ月×5チャネル×5カテゴリの特徴量フラット化）===
training_records = []
for m_idx, m in enumerate(months):
    for ch in channels:
        for cat in cat_list:
            # 特徴量
            ad_budget = np.random.randint(500000, 3000000)
            impressions = ad_budget * np.random.randint(10, 30)
            clicks = int(impressions * np.random.uniform(0.01, 0.03))
            price_index = round(np.random.uniform(0.8, 1.2), 2)
            inventory_level = np.random.randint(50, 500)
            month_num = m_idx + 1
            season_factor = round(1 + 0.2 * np.sin(month_num / 12 * 2 * np.pi), 2)
            champions_ratio = round(np.random.uniform(0.10, 0.30), 3)

            # 目的変数
            base_rev = ad_budget * np.random.uniform(1.5, 4.0) * season_factor * price_index
            revenue = int(base_rev)
            roas = round(revenue / ad_budget, 2)
            churn_rate = round(np.random.uniform(0.05, 0.30) / (champions_ratio + 0.1), 3)

            training_records.append({
                "年月": m, "チャネル": ch, "カテゴリ": cat,
                "広告費": ad_budget, "インプレッション": impressions, "クリック": clicks,
                "価格指数": price_index, "在庫水準": inventory_level,
                "月": month_num, "季節係数": season_factor,
                "Champions比率": champions_ratio,
                "売上": revenue, "ROAS": roas, "離脱率": churn_rate,
            })
training_df = pd.DataFrame(training_records)

out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(out_dir, exist_ok=True)

products.to_csv(os.path.join(out_dir, "products.csv"), index=False, encoding="utf-8-sig")
customers.to_csv(os.path.join(out_dir, "customers.csv"), index=False, encoding="utf-8-sig")
orders_df.to_csv(os.path.join(out_dir, "orders.csv"), index=False, encoding="utf-8-sig")
ads_df.to_csv(os.path.join(out_dir, "ads.csv"), index=False, encoding="utf-8-sig")
training_df.to_csv(os.path.join(out_dir, "training_data.csv"), index=False, encoding="utf-8-sig")

print(f"Saved products: {len(products)} rows")
print(f"Saved customers: {len(customers)} rows")
print(f"Saved orders: {len(orders_df)} rows")
print(f"Saved ads: {len(ads_df)} rows")
print(f"Saved training_data: {len(training_df)} rows")
