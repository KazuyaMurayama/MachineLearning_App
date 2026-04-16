"""
RFM分析サンプルデータ生成
500顧客 × 購買履歴データ（過去2年分: 2023-01-01〜2024-12-31）
2023年・2024年の件数バランスを均等に保ち、現実的なRFM分布を再現
"""
import pandas as pd
import numpy as np
import os

rng = np.random.RandomState(42)
N_CUSTOMERS = 500
BASE_DATE = pd.Timestamp("2024-12-31")
START_DATE = pd.Timestamp("2023-01-01")
PERIOD_DAYS = (BASE_DATE - START_DATE).days  # 730日
CATEGORIES = ["ファッション", "食品", "家電", "美容・コスメ", "日用品", "スポーツ", "書籍", "インテリア"]

def generate_unique_names(n, rng):
    last_names = ["田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "小林", "加藤",
                  "吉田", "山田", "佐々木", "松本", "井上", "木村", "林", "斎藤", "清水", "山口",
                  "池田", "橋本", "阿部", "石川", "前田", "藤田", "小川", "岡田", "後藤", "長谷川"]
    first_names = ["太郎", "花子", "一郎", "美咲", "健太", "由美", "翔", "真由", "大輝", "さくら",
                   "拓也", "陽子", "直樹", "恵", "剛", "智子", "優", "愛", "誠", "裕子"]
    names = set()
    while len(names) < n:
        names.add(rng.choice(last_names) + " " + rng.choice(first_names))
    return list(names)

customer_names = generate_unique_names(N_CUSTOMERS, rng)

# 顧客タイプ: VIP(10%), 優良(20%), 一般(40%), 休眠(20%), 離脱(10%)
types = (["VIP"] * 50 + ["優良"] * 100 + ["一般"] * 200 + ["休眠"] * 100 + ["離脱"] * 50)
rng.shuffle(types)

records = []
for i in range(N_CUSTOMERS):
    ctype = types[i]
    cid = f"EC{str(i+1).zfill(4)}"
    name = customer_names[i]

    if ctype == "VIP":
        # VIP: 直近30日以内に最終購入、2年間で15〜40回
        n_orders = rng.randint(15, 40)
        recency_days = rng.randint(1, 30)          # 最終購入: 1〜30日前
        window_days = PERIOD_DAYS                   # 活動期間: 全2年間
        avg_amount = rng.uniform(8000, 25000)
    elif ctype == "優良":
        n_orders = rng.randint(8, 20)
        recency_days = rng.randint(10, 60)          # 最終購入: 10〜60日前
        window_days = PERIOD_DAYS
        avg_amount = rng.uniform(5000, 15000)
    elif ctype == "一般":
        n_orders = rng.randint(3, 12)
        recency_days = rng.randint(30, 180)         # 最終購入: 30〜180日前
        window_days = PERIOD_DAYS
        avg_amount = rng.uniform(3000, 10000)
    elif ctype == "休眠":
        # 休眠: 180〜400日前が最終購入
        n_orders = rng.randint(2, 6)
        recency_days = rng.randint(180, 365)        # 最終購入: 180〜365日前
        window_days = min(recency_days + 180, PERIOD_DAYS)  # 活動期間は最終購入前180日まで
        avg_amount = rng.uniform(2000, 7000)
    else:  # 離脱
        # 離脱: 365〜700日前が最終購入（全体の後半に活動が集中）
        n_orders = rng.randint(1, 4)
        recency_days = rng.randint(365, 700)        # 最終購入: 1〜2年前
        window_days = min(recency_days + 180, PERIOD_DAYS)  # 活動期間は最終購入前180日まで
        avg_amount = rng.uniform(1500, 5000)

    # 注文日を [recency_days, recency_days + window_days] の範囲でランダム生成
    # ただし START_DATE より前にならないよう制限
    oldest_allowed = PERIOD_DAYS  # = 730日前 = START_DATE
    newest_allowed = recency_days
    oldest_order = min(window_days, oldest_allowed)

    if oldest_order <= newest_allowed:
        # 有効な期間がない場合は最終購入1件のみ
        order_days = [newest_allowed]
    else:
        # n_orders 個の注文日を有効範囲内でランダムサンプリング
        # 最終購入(recency_days)は必ず含める
        candidate_days = [newest_allowed]
        for _ in range(n_orders - 1):
            d = int(rng.uniform(newest_allowed + 1, oldest_order))
            candidate_days.append(d)
        order_days = sorted(set(candidate_days))

    for days_ago in order_days:
        order_date = BASE_DATE - pd.Timedelta(days=int(days_ago))
        if order_date < START_DATE:
            continue

        amount = max(500, int(rng.normal(avg_amount, avg_amount * 0.3)))
        category = rng.choice(CATEGORIES)
        records.append({
            "顧客ID": cid,
            "顧客名": name,
            "注文日": order_date.strftime("%Y-%m-%d"),
            "注文金額": amount,
            "商品カテゴリ": category,
        })

df = pd.DataFrame(records)
df = df.sort_values(["顧客ID", "注文日"]).reset_index(drop=True)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "purchase_history.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"✅ サンプルデータ生成完了: {len(df)}行, {df['顧客ID'].nunique()}顧客 → {out_path}")
print(df.head(3))
print(f"\n注文金額統計:\n{df['注文金額'].describe()}")
print(f"\n顧客別注文回数:\n{df.groupby('顧客ID').size().describe()}")
