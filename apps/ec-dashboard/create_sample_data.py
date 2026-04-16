"""
売上ダッシュボード サンプルデータ生成
2年分の日別売上データ（2023/1/1〜2024/12/31）
"""
import pandas as pd
import numpy as np
import os

rng = np.random.RandomState(42)
CATEGORIES = ["ファッション", "食品", "家電", "美容・コスメ", "日用品"]

start = pd.Timestamp("2023-01-01")
end = pd.Timestamp("2024-12-31")
dates = pd.date_range(start, end, freq="D")

records = []
for dt in dates:
    month = dt.month
    dow = dt.dayofweek  # 0=Mon, 6=Sun

    # 季節性: 3月・7月・12月がピーク
    seasonal = 1.0
    if month in [3, 7, 12]:
        seasonal = 1.4
    elif month in [1, 2, 8]:
        seasonal = 0.8
    elif month in [11]:
        seasonal = 1.2

    # 曜日効果: 週末は1.3倍
    dow_mult = 1.3 if dow >= 5 else 1.0

    # 年次成長: 2024年は2023年の1.15倍
    year_mult = 1.15 if dt.year == 2024 else 1.0

    for cat in CATEGORIES:
        # カテゴリ別ベース
        base = {"ファッション": 120000, "食品": 80000, "家電": 60000,
                "美容・コスメ": 50000, "日用品": 40000}[cat]

        daily_sales = int(base * seasonal * dow_mult * year_mult
                         * rng.uniform(0.7, 1.3))
        n_orders = max(1, int(daily_sales / rng.uniform(3000, 8000)))
        avg_price = int(daily_sales / n_orders) if n_orders > 0 else 0

        records.append({
            "日付": dt.strftime("%Y-%m-%d"),
            "カテゴリ": cat,
            "売上金額": daily_sales,
            "注文件数": n_orders,
            "客単価": avg_price,
        })

df = pd.DataFrame(records)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "daily_sales.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"✅ サンプルデータ生成完了: {len(df)}行, {df['日付'].nunique()}日分 → {out_path}")
print(df.head(3))
print(f"\n売上金額統計:\n{df['売上金額'].describe()}")
print(f"\nカテゴリ別合計:")
print(df.groupby("カテゴリ")["売上金額"].sum().sort_values(ascending=False))
