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
from helpers import render_tab1, render_tab2, render_tab3, render_tab4

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="EC経営ダッシュボード",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


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

st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #065F46 0%, #059669 100%);
    color: white; padding: 2rem; border-radius: 16px;
    text-align: center; margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.2rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0; }
.kpi-card {
    text-align: center; padding: 18px 12px;
    background: linear-gradient(180deg, #ECFDF5, #FFFFFF);
    border-radius: 12px; border: 1px solid #A7F3D0;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #065F46; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.alert-box {
    background: #FEF2F2; border: 1px solid #FECACA;
    border-radius: 8px; padding: 12px; margin: 4px 0;
}
.section-divider {
    border: none; height: 2px;
    background: linear-gradient(to right, #059669, #e2e8f0); margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


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
                [sys.executable, os.path.join(base_dir, "create_sample_data.py")], check=True)
        except Exception as e:
            st.error(f"サンプルデータの生成に失敗しました: {e}")
            return None, None, None, None, None
    products = pd.read_csv(os.path.join(data_dir, "products.csv"))
    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    ads = pd.read_csv(os.path.join(data_dir, "ads.csv"))
    cross = pd.read_csv(os.path.join(data_dir, "cross_segment.csv"))
    return products, customers, orders, ads, cross


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
    selected_channels = st.multiselect("チャネルフィルタ", options=all_channels, default=all_channels)
    all_categories = sorted(orders_raw["カテゴリ"].unique().tolist())
    selected_categories = st.multiselect("カテゴリフィルタ", options=all_categories, default=all_categories)
    risk_threshold = st.slider("離脱リスクしきい値", min_value=50, max_value=90, value=70, step=1)
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
- **在庫切迫 × 機会損失額**を即時把握
- 月次CSVレポートをワンクリックで出力
""")

orders = orders_raw[
    orders_raw["チャネル"].isin(selected_channels) &
    orders_raw["カテゴリ"].isin(selected_categories)
].copy()
ads = ads_raw[ads_raw["チャネル"].isin(selected_channels)].copy()
cross = cross_raw[cross_raw["チャネル"].isin(selected_channels)].copy()
products = products_raw.copy()
customers = customers_raw.copy()

months_sorted = sorted(orders["年月"].unique())
current_month = months_sorted[-1] if len(months_sorted) > 0 else None
prev_month = months_sorted[-2] if len(months_sorted) > 1 else None
yoy_month = months_sorted[-13] if len(months_sorted) >= 13 else None

current_sales = int(orders[orders["年月"] == current_month]["売上"].sum()) if current_month else 0
prev_sales = int(orders[orders["年月"] == prev_month]["売上"].sum()) if prev_month else 0
mom = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales != 0 else 0
yoy_sales = int(orders[orders["年月"] == yoy_month]["売上"].sum()) if yoy_month else 0
yoy_pct = ((current_sales - yoy_sales) / yoy_sales * 100) if yoy_sales != 0 else 0
avg_roas = float(ads["ROAS"].mean()) if len(ads) > 0 else 0.0
high_risk_customers = customers[customers["離脱リスクスコア"] >= risk_threshold]
high_risk_count = len(high_risk_customers)

st.markdown("""
<div class="hero-section">
<h1>📈 EC経営ダッシュボード</h1>
<p>売上・広告・顧客・在庫を1画面で把握 — <strong>L3 プレミアムパック 月額26万円</strong>の中核機能<br>
<span style="font-size:0.95rem;opacity:0.9;">GA4・Lookerでは見えない "次の一手" を統合ビューで即座に提示。機会損失・離脱リスクを¥換算でリアルタイム表示。</span></p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    mom_sign = "+" if mom >= 0 else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">¥{current_sales/10000:,.0f}万</div>'
                f'<div class="kpi-label">当月売上</div>'
                f'<div style="color:#059669;font-weight:700;">前月比 {mom_sign}{mom:.1f}%</div></div>',
                unsafe_allow_html=True)
with col2:
    yoy_sign = "+" if yoy_pct >= 0 else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{yoy_sign}{yoy_pct:.1f}%</div>'
                f'<div class="kpi-label">前年同月比</div>'
                f'<div style="color:#065F46;font-weight:700;">{current_month} vs {yoy_month or "N/A"}</div></div>',
                unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_roas:.2f}</div>'
                f'<div class="kpi-label">平均ROAS</div>'
                f'<div style="color:#065F46;font-weight:700;">全チャネル平均</div></div>',
                unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_risk_count}人</div>'
                f'<div class="kpi-label">離脱リスク高顧客</div>'
                f'<div style="color:#DC2626;font-weight:700;">しきい値 ≥ {risk_threshold}</div></div>',
                unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 経営サマリー",
    "🔗 チャネル横断ROI分析",
    "👥 顧客×収益セグメント",
    "⚠️ アラート",
])

with tab1:
    render_tab1(orders, current_month)

with tab2:
    render_tab2(ads, cross, selected_channels)

with tab3:
    render_tab3(customers, risk_threshold)

with tab4:
    render_tab4(products, orders)

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem; padding:0.5rem 0;">
    📈 EC経営ダッシュボード | <strong>L3 プレミアムパック 月額26万円</strong> | ECデータサイエンス v1.0<br>
    GA4・Lookerでは見えない "次の一手" — 売上・広告・顧客・在庫を統合し、機会損失と離脱を¥換算で即時可視化
</div>
""", unsafe_allow_html=True)
