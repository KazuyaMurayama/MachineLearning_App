"""
EC向けサンプルデータ生成
========================
品質チェック基準:
  1. 各特徴量のデータソース（Shopify API, GA4, MA等）を明記
  2. 現実的な数値分布（業界調査に基づく）
  3. アクション可能な特徴量を優先選定

2つのデータセット:
  A. 顧客離脱予測用（1,000顧客 × 15特徴量 + 離脱フラグ）
  B. 売上/需要予測用（50SKU × 365日 × 特徴量）
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

# ============================================================
# A. 顧客離脱予測データ（メイン）
# ============================================================
N_CUST = 1000

# --- 特徴量 ---

# 1. 直近購入からの経過日数 — Shopify注文API / 注文CSV
#    活発な顧客は7-30日、離脱気味は60-180日、完全離脱予備軍は180-365日
recency = np.concatenate([
    np.random.exponential(15, int(N_CUST * 0.5)).clip(1, 60),     # 活発層
    np.random.exponential(40, int(N_CUST * 0.3)).clip(30, 180),   # 中間層
    np.random.exponential(80, N_CUST - int(N_CUST * 0.5) - int(N_CUST * 0.3)).clip(90, 365),  # 離脱予備
])
np.random.shuffle(recency)
recency = recency.astype(int)

# 2. 過去90日購入回数 — Shopify注文API
#    EC中堅: 平均2回/90日。ヘビーユーザーは5-10回
frequency_90d = np.random.poisson(2, N_CUST).clip(0, 15)

# 3. 累計購入金額（円）— Shopify注文API
#    D2C中堅EC: ¥5,000-¥500,000。対数正規分布
monetary = np.random.lognormal(9.5, 1.0, N_CUST).clip(3000, 500000).astype(int)

# 4. 平均注文単価（円）— Shopify注文APIから算出
#    ¥2,000-¥20,000。アパレル/雑貨EC中心
avg_order_value = np.random.lognormal(8.5, 0.5, N_CUST).clip(1500, 25000).astype(int)

# 5. 直近30日ログイン回数 — GA4 / Shopifyアクセスログ
login_30d = np.random.poisson(3, N_CUST).clip(0, 30)

# 6. メール開封率(%) — Shopify Email / Klaviyo / MA
#    業界平均15-25%。beta分布で右裾
email_open_rate = (np.random.beta(2, 5, N_CUST) * 100).round(1)

# 7. カート放棄回数(90日) — GA4 / Shopify
#    平均1回。放棄の多い顧客は離脱シグナル
cart_abandon = np.random.poisson(1, N_CUST).clip(0, 8)

# 8. 問い合わせ回数(90日) — CS管理ツール / Zendesk
#    大半は0回。不満のある顧客は1-3回
support_tickets = np.random.poisson(0.3, N_CUST).clip(0, 5)

# 9. 決済失敗回数 — Shopify決済ログ / Stripe
#    大半は0。サブスクECでは重要な離脱シグナル
payment_failures = np.random.poisson(0.15, N_CUST).clip(0, 3)

# 10. クーポン利用率(%) — Shopify注文APIから算出
#     クーポン利用が多い=価格感度高い=離脱しやすい場合も
coupon_usage = (np.random.beta(1.5, 5, N_CUST) * 100).round(1)

# 11. 購入カテゴリ数 — Shopify注文APIから算出
#     多カテゴリ購入=エンゲージメント高い
category_count = (np.random.poisson(2, N_CUST) + 1).clip(1, 8)

# 12. 会員歴（月）— Shopify顧客DB
#     指数分布、中央値12ヶ月
tenure_months = np.random.exponential(12, N_CUST).clip(1, 60).astype(int)

# 13. 流入チャネル — GA4 / UTMパラメータ
channel = np.random.choice(
    ["検索", "SNS", "広告", "紹介", "直接アクセス"],
    N_CUST, p=[0.30, 0.25, 0.25, 0.10, 0.10],
)

# 14. 直近レビュー投稿からの日数 — Shopify Product Reviews
#     50%は未投稿（999で表現）。投稿者は30-180日前
_review_posted = np.random.binomial(1, 0.5, N_CUST)
review_recency = np.where(
    _review_posted == 1,
    np.random.exponential(60, N_CUST).clip(1, 365).astype(int),
    999,
)

# --- 目的変数: 90日以内離脱フラグ ---
# 離脱確率をロジスティック関数で設計。離脱率15-20%目標
logit = (
    -0.3                                  # ベース調整（離脱率15-20%目標）
    + recency * 0.018                     # 経過日数↑ → 離脱↑（強化）
    - frequency_90d * 0.6                 # 購入回数↑ → 離脱↓（強化）
    - np.log1p(monetary / 1000) * 0.2     # 累計金額↑ → 離脱↓
    - login_30d * 0.2                     # ログイン↑ → 離脱↓（強化）
    - email_open_rate * 0.03              # 開封率↑ → 離脱↓（強化）
    + cart_abandon * 0.35                 # カート放棄↑ → 離脱↑（強化）
    + support_tickets * 0.5              # 問い合わせ↑ → 離脱↑（強化）
    + payment_failures * 1.2             # 決済失敗↑ → 離脱↑（最強シグナル）
    + coupon_usage * 0.008               # クーポン依存↑ → やや離脱↑
    - category_count * 0.2               # 多カテゴリ → 離脱↓（強化）
    - np.minimum(tenure_months, 24) * 0.04  # 会員歴↑ → 離脱↓
    + np.where(review_recency == 999, 0.4, -0.3)  # 未投稿 → 離脱↑（強化）
    + np.random.normal(0, 0.3, N_CUST)   # ノイズ縮小: 0.5→0.3
)
churn_prob = 1 / (1 + np.exp(-logit))
churned = (np.random.random(N_CUST) < churn_prob).astype(int)

cust_df = pd.DataFrame({
    "顧客ID": [f"EC{str(i + 1).zfill(4)}" for i in range(N_CUST)],
    "直近購入からの経過日数": recency,
    "過去90日購入回数": frequency_90d,
    "累計購入金額": monetary,
    "平均注文単価": avg_order_value,
    "直近30日ログイン回数": login_30d,
    "メール開封率": email_open_rate,
    "カート放棄回数": cart_abandon,
    "問い合わせ回数": support_tickets,
    "決済失敗回数": payment_failures,
    "クーポン利用率": coupon_usage,
    "購入カテゴリ数": category_count,
    "会員歴月数": tenure_months,
    "流入チャネル": channel,
    "直近レビュー投稿からの日数": review_recency,
    "90日以内離脱": churned,
})

churn_rate = churned.mean()
print(f"[顧客離脱] N={N_CUST}, 離脱率={churn_rate:.1%}, Features={len(cust_df.columns) - 2}")

# ============================================================
# B. 売上/需要予測データ（サブ）
# ============================================================
N_SKU = 50
N_DAYS = 365

dates = pd.date_range("2025-04-01", periods=N_DAYS, freq="D")
categories = ["アパレル", "食品", "雑貨", "コスメ", "家電"]
sku_list = [f"SKU{str(i + 1).zfill(3)}" for i in range(N_SKU)]
sku_cat = {sku: np.random.choice(categories) for sku in sku_list}
sku_base_price = {sku: int(np.random.lognormal(8.2, 0.6)) for sku in sku_list}

rows = []
for sku in sku_list:
    base_demand = np.random.uniform(5, 40)
    for i, d in enumerate(dates):
        # 季節性（正弦波）
        season = 1 + 0.3 * np.sin(2 * np.pi * (d.month - 1) / 12)
        # 曜日効果（土日は1.3倍）
        dow_effect = 1.3 if d.dayofweek >= 5 else 1.0
        # トレンド（微増）
        trend = 1 + 0.0005 * i
        # プロモーション（15%の確率）
        promo = np.random.binomial(1, 0.15)
        promo_lift = 1.5 if promo else 1.0
        # 割引率
        discount = np.random.choice([0, 0, 0, 0, 5, 10, 15, 20, 30], p=[0.55, 0.1, 0.05, 0.05, 0.08, 0.07, 0.05, 0.03, 0.02])
        # 広告費
        ad_spend = int(np.random.lognormal(7, 1.2)) if np.random.random() < 0.4 else 0
        # 販売数量
        qty = max(0, int(base_demand * season * dow_effect * trend * promo_lift
                         * (1 + discount * 0.01) + np.random.normal(0, base_demand * 0.2)))
        price = sku_base_price[sku]
        sales = qty * price * (1 - discount / 100)

        rows.append({
            "日付": d.strftime("%Y-%m-%d"),
            "SKU": sku,
            "カテゴリ": sku_cat[sku],
            "販売数量": qty,
            "単価": price,
            "割引率": discount,
            "広告費": ad_spend,
            "プロモーション": promo,
            "曜日": d.day_name(),
            "月": d.month,
            "売上金額": int(sales),
        })

sales_df = pd.DataFrame(rows)

# Add lag features per SKU (shifted to avoid leakage)
sales_df["日付_dt"] = pd.to_datetime(sales_df["日付"])
sales_df = sales_df.sort_values(["SKU", "日付_dt"]).reset_index(drop=True)
sales_df["前週平均販売数量"] = sales_df.groupby("SKU")["販売数量"].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean()).fillna(0).round(1)
sales_df["前月平均販売数量"] = sales_df.groupby("SKU")["販売数量"].transform(lambda x: x.shift(1).rolling(30, min_periods=1).mean()).fillna(0).round(1)
sales_df = sales_df.drop(columns=["日付_dt"])

print(f"[売上予測] SKU={N_SKU}, Days={N_DAYS}, Rows={len(sales_df)}")

# ============================================================
# 保存
# ============================================================
out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(out_dir, exist_ok=True)

cust_df.to_csv(os.path.join(out_dir, "ec_customers_train.csv"), index=False, encoding="utf-8-sig")
cust_target = cust_df.drop(columns=["90日以内離脱"]).sample(200, random_state=99).reset_index(drop=True)
cust_target.to_csv(os.path.join(out_dir, "ec_customers_target.csv"), index=False, encoding="utf-8-sig")

sales_df.to_csv(os.path.join(out_dir, "ec_sales_train.csv"), index=False, encoding="utf-8-sig")
sales_target = sales_df[sales_df["日付"] >= "2026-03-01"]
sales_target_no_y = sales_target.drop(columns=["売上金額", "販売数量"])
sales_target_no_y.to_csv(os.path.join(out_dir, "ec_sales_target.csv"), index=False, encoding="utf-8-sig")

print(f"Saved to {out_dir}")
