"""
EC経営ダッシュボード
====================
売上・広告・顧客・在庫を1画面に集約した EC 経営者向け統合ビュー
L3（月額26万円）コア機能
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
import os
import sys

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="EC経営ダッシュボード",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# 日本語フォント設定
# =====================================================================

def setup_japanese_font():
    japanese_fonts = [
        "Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic",
        "MS Gothic", "Meiryo", "DejaVu Sans",
    ]
    available = [f.name for f in fm.fontManager.ttflist]
    for font in japanese_fonts:
        if font in available:
            plt.rcParams["font.family"] = font
            plt.rcParams["font.sans-serif"] = [font]
            plt.rcParams["axes.unicode_minus"] = False
            return font
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    return None

_font = setup_japanese_font()

# =====================================================================
# CSS
# =====================================================================

st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #065F46 0%, #059669 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.2rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0; }
.kpi-card {
    text-align: center;
    padding: 18px 12px;
    background: linear-gradient(180deg, #ECFDF5, #FFFFFF);
    border-radius: 12px;
    border: 1px solid #A7F3D0;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #065F46; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.alert-box {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 8px;
    padding: 12px;
    margin: 4px 0;
}
.section-divider {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #059669, #e2e8f0);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# データ読み込み
# =====================================================================

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "sample_data")
    required_files = ["products.csv", "customers.csv", "orders.csv", "ads.csv", "cross_segment.csv"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(data_dir, f))]
    if missing:
        try:
            import subprocess
            subprocess.run(
                [sys.executable, os.path.join(base_dir, "create_sample_data.py")],
                check=True,
            )
        except Exception as e:
            st.error(f"サンプルデータの生成に失敗しました: {e}")
            return None, None, None, None, None

    products = pd.read_csv(os.path.join(data_dir, "products.csv"))
    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    ads = pd.read_csv(os.path.join(data_dir, "ads.csv"))
    cross = pd.read_csv(os.path.join(data_dir, "cross_segment.csv"))
    return products, customers, orders, ads, cross

# =====================================================================
# サイドバー
# =====================================================================

with st.sidebar:
    st.markdown("## 📈 EC経営ダッシュボード")
    st.markdown("**📅 対象月: 2026年4月**")
    st.divider()

    if st.button("🔄 サンプルデータ再生成"):
        load_data.clear()
        st.rerun()

    products_raw, customers_raw, orders_raw, ads_raw, cross_raw = load_data()

    if products_raw is None:
        st.error("データ読み込み失敗")
        st.stop()

    all_channels = sorted(orders_raw["チャネル"].unique().tolist())
    selected_channels = st.multiselect(
        "チャネルフィルタ",
        options=all_channels,
        default=all_channels,
    )

    all_categories = sorted(orders_raw["カテゴリ"].unique().tolist())
    selected_categories = st.multiselect(
        "カテゴリフィルタ",
        options=all_categories,
        default=all_categories,
    )

    risk_threshold = st.slider(
        "離脱リスクしきい値",
        min_value=50,
        max_value=90,
        value=70,
        step=1,
    )

    st.divider()
    st.markdown("""
**使い方**
1. チャネル・カテゴリフィルタで対象を絞り込む
2. 離脱リスクしきい値を調整して高リスク顧客を抽出
3. タブ1「経営サマリー」で月次トレンドを把握
4. タブ2「チャネル横断ROI」で広告効率を比較
5. タブ4「アラート」でCSVダウンロード

---
💡 **L3 プレミアムパック 月額26万円の価値**

GA4・Lookerでは見えない多軸分析を提供:
- **RFM×チャネルROI** 横断ヒートマップ
- **離脱放置コスト**を¥換算でリアルタイム表示
- **在庫切迫 × 機会損失額**を即時把握
- 月次CSVレポートをワンクリックで出力
""")

# =====================================================================
# フィルタ適用
# =====================================================================

orders = orders_raw[
    orders_raw["チャネル"].isin(selected_channels) &
    orders_raw["カテゴリ"].isin(selected_categories)
].copy()

ads = ads_raw[ads_raw["チャネル"].isin(selected_channels)].copy()
cross = cross_raw[cross_raw["チャネル"].isin(selected_channels)].copy()
products = products_raw.copy()
customers = customers_raw.copy()

# =====================================================================
# KPI 計算
# =====================================================================

months_sorted = sorted(orders["年月"].unique())
current_month = months_sorted[-1] if len(months_sorted) > 0 else None
prev_month = months_sorted[-2] if len(months_sorted) > 1 else None
yoy_month = months_sorted[-13] if len(months_sorted) >= 13 else None

if current_month:
    current_sales = int(orders[orders["年月"] == current_month]["売上"].sum())
else:
    current_sales = 0

if prev_month:
    prev_sales = int(orders[orders["年月"] == prev_month]["売上"].sum())
    mom = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales != 0 else 0
else:
    prev_sales = 0
    mom = 0

if yoy_month:
    yoy_sales = int(orders[orders["年月"] == yoy_month]["売上"].sum())
    yoy_pct = ((current_sales - yoy_sales) / yoy_sales * 100) if yoy_sales != 0 else 0
else:
    yoy_pct = 0

avg_roas = float(ads["ROAS"].mean()) if len(ads) > 0 else 0.0
high_risk_customers = customers[customers["離脱リスクスコア"] >= risk_threshold]
high_risk_count = len(high_risk_customers)

# =====================================================================
# Hero セクション
# =====================================================================

st.markdown("""
<div class="hero-section">
<h1>📈 EC経営ダッシュボード</h1>
<p>売上・広告・顧客・在庫を1画面で把握 — <strong>L3 プレミアムパック 月額26万円</strong>の中核機能<br>
<span style="font-size:0.95rem;opacity:0.9;">GA4・Lookerでは見えない "次の一手" を統合ビューで即座に提示。機会損失・離脱リスクを¥換算でリアルタイム表示。</span></p>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# KPI カード
# =====================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    sales_man = current_sales / 10000
    mom_sign = "+" if mom >= 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">¥{sales_man:,.0f}万</div>
        <div class="kpi-label">当月売上</div>
        <div style="color:#059669;font-weight:700;">前月比 {mom_sign}{mom:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    yoy_sign = "+" if yoy_pct >= 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{yoy_sign}{yoy_pct:.1f}%</div>
        <div class="kpi-label">前年同月比</div>
        <div style="color:#065F46;font-weight:700;">{current_month} vs {yoy_month if yoy_month else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_roas:.2f}</div>
        <div class="kpi-label">平均ROAS</div>
        <div style="color:#065F46;font-weight:700;">全チャネル平均</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{high_risk_count}人</div>
        <div class="kpi-label">離脱リスク高顧客</div>
        <div style="color:#DC2626;font-weight:700;">しきい値 ≥ {risk_threshold}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =====================================================================
# タブ
# =====================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 経営サマリー",
    "🔗 チャネル横断ROI分析",
    "👥 顧客×収益セグメント",
    "⚠️ アラート",
])

# ------------------------------------------------------------------
# タブ1: 経営サマリー
# ------------------------------------------------------------------
with tab1:
    st.subheader("📊 経営サマリー")

    # 月次売上推移ライン
    st.markdown("**月次売上推移（過去13ヶ月）**")
    monthly_sales = orders.groupby("年月")["売上"].sum().reset_index().sort_values("年月")
    fig, ax = plt.subplots(figsize=(10, 4))
    x_pos = range(len(monthly_sales))
    ax.plot(x_pos, monthly_sales["売上"], color="#059669", linewidth=2.5, marker="o", markersize=5)
    ax.fill_between(x_pos, monthly_sales["売上"], alpha=0.1, color="#059669")
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(monthly_sales["年月"].tolist(), rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("売上（円）")
    ax.set_title("月次売上推移")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x/10000):,}万"))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    col_a, col_b = st.columns(2)

    # チャネル別当月売上 横棒グラフ
    with col_a:
        st.markdown("**チャネル別 当月売上**")
        if current_month:
            ch_sales = orders[orders["年月"] == current_month].groupby("チャネル")["売上"].sum().sort_values()
        else:
            ch_sales = orders.groupby("チャネル")["売上"].sum().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(ch_sales.index, ch_sales.values, color="#059669", alpha=0.85)
        ax.set_xlabel("売上（円）")
        ax.set_title("チャネル別 当月売上")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x/10000):,}万"))
        for i, v in enumerate(ch_sales.values):
            ax.text(v + max(ch_sales.values) * 0.01, i, f"¥{int(v/10000):,}万", va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # カテゴリ別当月売上 円グラフ
    with col_b:
        st.markdown("**カテゴリ別 当月売上**")
        if current_month:
            cat_sales = orders[orders["年月"] == current_month].groupby("カテゴリ")["売上"].sum()
        else:
            cat_sales = orders.groupby("カテゴリ")["売上"].sum()
        fig, ax = plt.subplots(figsize=(6, 4))
        colors_pie = ["#059669", "#065F46", "#34D399", "#6EE7B7", "#A7F3D0"]
        ax.pie(
            cat_sales.values,
            labels=cat_sales.index.tolist(),
            colors=colors_pie[:len(cat_sales)],
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 9},
        )
        ax.set_title("カテゴリ別 当月売上")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 業績サマリーテーブル（チャネル×カテゴリのクロス集計）
    st.markdown("**業績サマリーテーブル（チャネル × カテゴリ）**")
    if current_month:
        summary_data = orders[orders["年月"] == current_month]
    else:
        summary_data = orders
    cross_table = summary_data.pivot_table(
        values="売上", index="チャネル", columns="カテゴリ", aggfunc="sum", fill_value=0
    )
    cross_table_disp = cross_table.map(lambda x: f"¥{int(x/10000):,}万")
    st.dataframe(cross_table_disp, use_container_width=True)

# ------------------------------------------------------------------
# タブ2: チャネル横断ROI分析
# ------------------------------------------------------------------
with tab2:
    st.subheader("🔗 チャネル横断ROI分析")

    # チャネル別ROAS推移ライン（13ヶ月）
    st.markdown("**チャネル別 ROAS推移（13ヶ月）**")
    fig, ax = plt.subplots(figsize=(10, 4))
    colors_line = ["#059669", "#065F46", "#34D399", "#0D9488", "#047857"]
    for idx, ch in enumerate(selected_channels):
        ch_ads = ads[ads["チャネル"] == ch].sort_values("年月")
        if len(ch_ads) > 0:
            x_pos = range(len(ch_ads))
            ax.plot(x_pos, ch_ads["ROAS"], linewidth=2, marker="o", markersize=4,
                    label=ch, color=colors_line[idx % len(colors_line)])
    if len(ads) > 0:
        x_labels = sorted(ads["年月"].unique())
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("ROAS")
    ax.set_title("チャネル別 ROAS推移")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("### 🔥 横断分析 — GA4・Lookerでは見えない「RFM×チャネルROI」")

    col_c, col_d = st.columns(2)

    # RFMセグメント × チャネル ROI ヒートマップ
    with col_c:
        st.markdown("**RFMセグメント × チャネル ROI ヒートマップ**")
        seg_order = ["Champions", "Loyal", "AtRisk", "Lost", "New"]
        heat_data = cross.pivot_table(values="ROI", index="RFMセグメント", columns="チャネル", aggfunc="mean", fill_value=0)
        # セグメント順に並べ替え
        heat_data = heat_data.reindex([s for s in seg_order if s in heat_data.index])
        fig, ax = plt.subplots(figsize=(7, 4))
        im = ax.imshow(heat_data.values, aspect="auto", cmap="Greens")
        ax.set_xticks(range(len(heat_data.columns)))
        ax.set_xticklabels(heat_data.columns.tolist(), fontsize=9)
        ax.set_yticks(range(len(heat_data.index)))
        ax.set_yticklabels(heat_data.index.tolist(), fontsize=9)
        plt.colorbar(im, ax=ax, label="ROI")
        for i in range(len(heat_data.index)):
            for j in range(len(heat_data.columns)):
                ax.text(j, i, f"{heat_data.values[i, j]:.1f}", ha="center", va="center", fontsize=8, color="black")
        ax.set_title("RFMセグメント × チャネル ROI")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 離脱リスク高セグメント（AtRisk+Lost）への広告ROI テーブル
    with col_d:
        st.markdown("**AtRisk + Lost セグメントへの広告ROI**")
        high_risk_seg = cross[cross["RFMセグメント"].isin(["AtRisk", "Lost"])].copy()
        if len(high_risk_seg) > 0:
            roi_table = high_risk_seg.groupby(["RFMセグメント", "チャネル"]).agg(
                売上=("売上", "sum"),
                広告費=("広告費", "sum"),
                ROI=("ROI", "mean"),
                離脱率=("離脱率", "mean"),
            ).reset_index()
            roi_table["売上"] = roi_table["売上"].apply(lambda x: f"¥{int(x):,}")
            roi_table["広告費"] = roi_table["広告費"].apply(lambda x: f"¥{int(x):,}")
            roi_table["ROI"] = roi_table["ROI"].round(2)
            roi_table["離脱率"] = (roi_table["離脱率"] * 100).round(1).astype(str) + "%"
            st.dataframe(roi_table.reset_index(drop=True), use_container_width=True)
        else:
            st.info("データがありません。")

    # チャネル別CPA × CV数 散布図
    st.markdown("**チャネル別 CPA × CV数 散布図**")
    fig, ax = plt.subplots(figsize=(8, 4))
    for idx, ch in enumerate(selected_channels):
        ch_ads = ads[ads["チャネル"] == ch]
        if len(ch_ads) > 0:
            ax.scatter(ch_ads["CPA"], ch_ads["CV数"], label=ch,
                       color=colors_line[idx % len(colors_line)], alpha=0.7, s=50)
    ax.set_xlabel("CPA（円）")
    ax.set_ylabel("CV数")
    ax.set_title("チャネル別 CPA × CV数")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ------------------------------------------------------------------
# タブ3: 顧客×収益セグメント
# ------------------------------------------------------------------
with tab3:
    st.subheader("👥 顧客×収益セグメント")

    # RFMセグメント別 顧客数・平均購入額・離脱率 テーブル
    st.markdown("**RFMセグメント別 統計**")
    rfm_summary = customers.groupby("RFMセグメント").agg(
        顧客数=("顧客ID", "count"),
        平均購入額=("累計購入額", "mean"),
        平均離脱リスクスコア=("離脱リスクスコア", "mean"),
    ).reset_index()
    rfm_summary["平均購入額"] = rfm_summary["平均購入額"].apply(lambda x: f"¥{int(x):,}")
    rfm_summary["平均離脱リスクスコア"] = rfm_summary["平均離脱リスクスコア"].round(1)
    st.dataframe(rfm_summary.reset_index(drop=True), use_container_width=True)

    col_e, col_f = st.columns(2)

    # 年齢層別累計購入額 横棒グラフ
    with col_e:
        st.markdown("**年齢層別 累計購入額（平均）**")
        age_purchase = customers.groupby("年齢層")["累計購入額"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(age_purchase.index, age_purchase.values, color="#059669", alpha=0.85)
        ax.set_xlabel("平均累計購入額（円）")
        ax.set_title("年齢層別 累計購入額（平均）")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
        for i, v in enumerate(age_purchase.values):
            ax.text(v + max(age_purchase.values) * 0.01, i, f"¥{int(v):,}", va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 離脱リスクスコア分布ヒストグラム
    with col_f:
        st.markdown("**離脱リスクスコア分布**")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(customers["離脱リスクスコア"], bins=20, color="#065F46", alpha=0.75, edgecolor="white")
        ax.axvline(x=risk_threshold, color="#DC2626", linestyle="--", linewidth=2, label=f"しきい値 {risk_threshold}")
        ax.set_xlabel("離脱リスクスコア")
        ax.set_ylabel("人数")
        ax.set_title("離脱リスクスコア分布")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # セグメント × 年齢層 クロステーブル
    st.markdown("**RFMセグメント × 年齢層 クロス集計（顧客数）**")
    seg_age_cross = pd.crosstab(customers["RFMセグメント"], customers["年齢層"])
    st.dataframe(seg_age_cross, use_container_width=True)

# ------------------------------------------------------------------
# タブ4: アラート
# ------------------------------------------------------------------
with tab4:
    st.subheader("⚠️ アラート")

    col_g, col_h = st.columns(2)

    # 在庫切迫TOP10（在庫 < 20の商品）
    with col_g:
        st.markdown("**在庫切迫 TOP10（在庫数 < 20）**")
        low_stock = products[products["在庫数"] < 20].sort_values("在庫数").head(10)
        if len(low_stock) > 0:
            disp_stock = low_stock[["商品ID", "カテゴリ", "単価", "在庫数", "原価率"]].copy()
            disp_stock["単価"] = disp_stock["単価"].apply(lambda x: f"¥{x:,}")
            st.dataframe(disp_stock.reset_index(drop=True), use_container_width=True)
        else:
            st.info("在庫切迫商品はありません。")

    # 離脱リスク高顧客TOP10
    with col_h:
        st.markdown(f"**離脱リスク高顧客 TOP10（スコア ≥ {risk_threshold}）**")
        top10_risk_cust = customers[customers["離脱リスクスコア"] >= risk_threshold].sort_values(
            "離脱リスクスコア", ascending=False
        ).head(10)
        if len(top10_risk_cust) > 0:
            disp_risk = top10_risk_cust[[
                "顧客ID", "年齢層", "RFMセグメント", "累計購入額", "最終購入経過日数", "離脱リスクスコア"
            ]].copy()
            disp_risk["累計購入額"] = disp_risk["累計購入額"].apply(lambda x: f"¥{x:,}")
            st.dataframe(disp_risk.reset_index(drop=True), use_container_width=True)
        else:
            st.info(f"スコア ≥ {risk_threshold} の顧客はいません。")

    col_i, col_j = st.columns(2)

    # 在庫切れ予想損失額 試算カード
    with col_i:
        stockout_products = products[products["在庫数"] == 0]
        potential_loss = int((stockout_products["単価"] * 10).sum())  # 仮: 想定10個販売機会
        low_stock_count = len(products[products["在庫数"] < 20])
        # 在庫切迫商品（1〜19個）の追加機会損失試算
        low_stock_products = products[(products["在庫数"] > 0) & (products["在庫数"] < 20)]
        low_stock_opp_loss = int((low_stock_products["単価"] * (20 - low_stock_products["在庫数"]).clip(0)).sum())
        total_inv_risk = potential_loss + low_stock_opp_loss
        st.markdown(f"""
        <div class="alert-box">
        <strong>📦 在庫リスク 機会損失試算</strong><br>
        在庫切れ商品数: <strong>{len(stockout_products)} 商品</strong><br>
        在庫切迫（< 20）商品数: <strong>{low_stock_count} 商品</strong><br>
        在庫切れ機会損失（10個×単価）:<br>
        <span style="font-size:1.5rem;font-weight:700;color:#DC2626;">¥{potential_loss:,}</span><br>
        <span style="font-size:0.9rem;color:#64748b;">切迫分含む合計機会損失: <strong style="color:#DC2626;">¥{total_inv_risk:,}</strong></span>
        </div>
        """, unsafe_allow_html=True)

    # 離脱放置コスト 試算カード
    with col_j:
        if len(high_risk_customers) > 0:
            avg_purchase = int(high_risk_customers["累計購入額"].mean())
            churn_loss = int(avg_purchase * len(high_risk_customers) * 0.3)  # 仮: 30%が離脱
            annual_purchase_freq = 2.5  # 年間購入頻度推定
            annual_loss = int(churn_loss * annual_purchase_freq)
        else:
            avg_purchase = 0
            churn_loss = 0
            annual_loss = 0
        st.markdown(f"""
        <div class="alert-box">
        <strong>👥 離脱放置コスト（試算）</strong><br>
        離脱リスク高顧客: <strong>{high_risk_count} 人</strong><br>
        平均累計購入額: <strong>¥{avg_purchase:,}</strong><br>
        30%離脱した場合の想定損失額（月次）:<br>
        <span style="font-size:1.5rem;font-weight:700;color:#DC2626;">¥{churn_loss:,}</span><br>
        <span style="font-size:0.9rem;color:#64748b;">年間換算（購入頻度×2.5）: <strong style="color:#DC2626;">¥{annual_loss:,}</strong></span><br>
        <span style="font-size:0.85rem;color:#64748b;">💡 L3プレミアム月額26万円で離脱を防止すれば投資回収比率 <strong>{annual_loss // 260000 if annual_loss > 0 else 0}倍</strong></span>
        </div>
        """, unsafe_allow_html=True)

    # 月次経営サマリーCSVダウンロード
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("**📥 月次経営サマリーCSVダウンロード**")

    # 月次売上サマリー
    monthly_summary = orders.groupby(["年月", "チャネル"]).agg(
        注文数=("注文数", "sum"),
        売上=("売上", "sum"),
        粗利=("粗利", "sum"),
    ).reset_index()
    monthly_summary["区分"] = "月次売上サマリー"

    # 広告サマリー
    ads_summary = ads.copy()
    ads_summary["区分"] = "広告実績"

    # 高リスク顧客
    risk_export = high_risk_customers[[
        "顧客ID", "年齢層", "RFMセグメント", "累計購入額", "最終購入経過日数", "離脱リスクスコア"
    ]].copy()
    risk_export["区分"] = "高リスク顧客"

    export_df = pd.concat([monthly_summary.rename(columns=str), risk_export], ignore_index=True, sort=False)
    csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 月次経営サマリーCSVをダウンロード",
        data=csv_bytes,
        file_name="ec_monthly_summary.csv",
        mime="text/csv",
    )

# =====================================================================
# フッター
# =====================================================================

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem; padding:0.5rem 0;">
    📈 EC経営ダッシュボード | <strong>L3 プレミアムパック 月額26万円</strong> | ECデータサイエンス v1.0<br>
    GA4・Lookerでは見えない "次の一手" — 売上・広告・顧客・在庫を統合し、機会損失と離脱を¥換算で即時可視化
</div>
""", unsafe_allow_html=True)
