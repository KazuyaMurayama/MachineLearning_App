"""
EC月次AIブリーフィングレポート
============================
月次経営会議の資料が5分で完成。月額26万円プレミアムパックの伴走支援を可視化。
L3 AIブリーフィング機能
"""
import os
import subprocess
import sys
import datetime

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from helpers import render_tab1, render_tab2, render_tab3, render_tab4


def setup_japanese_font():
    japanese_fonts = ["Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic", "MS Gothic", "Meiryo", "DejaVu Sans"]
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

st.set_page_config(
    page_title="EC月次AIブリーフィング",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #059669 0%, #D97706 100%);
    color: white; padding: 2rem; border-radius: 16px;
    text-align: center; margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.2rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0; }
.kpi-card {
    text-align: center; padding: 18px 12px;
    background: linear-gradient(180deg, #FFFBEB, #FFFFFF);
    border-radius: 12px; border: 1px solid #FDE68A;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #92400E; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.action-item {
    background: #ECFDF5; border: 1px solid #A7F3D0;
    border-radius: 10px; padding: 16px; margin: 8px 0;
}
.highlight-box {
    background: #FFFBEB; border: 1px solid #FDE68A;
    border-radius: 10px; padding: 16px; margin: 8px 0;
}
.section-divider { border: none; height: 2px; background: linear-gradient(to right, #D97706, #e2e8f0); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    products_path = os.path.join(base_dir, "sample_data", "products.csv")
    customers_path = os.path.join(base_dir, "sample_data", "customers.csv")
    orders_path = os.path.join(base_dir, "sample_data", "orders.csv")
    ads_path = os.path.join(base_dir, "sample_data", "ads.csv")
    if not os.path.exists(products_path):
        try:
            subprocess.run([sys.executable, os.path.join(base_dir, "create_sample_data.py")],
                           check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            st.error(f"サンプルデータ生成に失敗しました: {e.stderr}")
            st.stop()
    products = pd.read_csv(products_path, encoding="utf-8-sig")
    customers = pd.read_csv(customers_path, encoding="utf-8-sig")
    orders_df = pd.read_csv(orders_path, encoding="utf-8-sig")
    ads_df = pd.read_csv(ads_path, encoding="utf-8-sig")
    return products, customers, orders_df, ads_df


with st.sidebar:
    st.title("📰 EC月次AIブリーフィング")
    st.markdown("**📅 対象月: 2026年4月**")
    st.markdown("---")
    risk_threshold = st.slider(
        "離脱リスクしきい値", min_value=50, max_value=90, value=70, step=5,
        help="このスコア以上の顧客を高リスクと判定します")
    if st.button("🔄 データ再生成"):
        try:
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "create_sample_data.py")],
                           check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            st.error(f"サンプルデータ生成に失敗しました: {e.stderr}")
            st.stop()
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("""
**使い方**
1. 離脱リスクしきい値を調整
2. 各タブで詳細データを確認
3. アクションタブからレポートをダウンロード

---
💡 **L3 プレミアムパック 月額26万円の価値**

- AIが自動生成するエグゼクティブサマリー
- チャネル別AI診断コメント（ROAS改善提案付き）
- 離脱放置による年間損失額を¥換算で試算
- 翌月アクション3件をデータドリブンで自動生成
- Markdownレポートをワンクリックでダウンロード

GA4・Lookerでは見えない "次の一手" を5分で経営会議に提出。
""")

products, customers, orders_df, ads_df = load_data()

today = datetime.date.today()
monthly_orders = orders_df.groupby("年月").agg(
    売上合計=("売上", "sum"), 粗利合計=("粗利", "sum"), 注文数合計=("注文数", "sum")).reset_index()
monthly_ads = ads_df.groupby("年月").agg(
    広告費合計=("広告費", "sum"), CV数合計=("CV数", "sum"), 広告売上合計=("売上", "sum")).reset_index()
monthly_ads["ROAS平均"] = (monthly_ads["広告売上合計"] / monthly_ads["広告費合計"]).round(2)

current_month_orders = monthly_orders.iloc[-1]
prev_month_orders = monthly_orders.iloc[-2]
current_rev = int(current_month_orders["売上合計"])
prev_rev = int(prev_month_orders["売上合計"])
current_gross = int(current_month_orders["粗利合計"])
gross_margin = current_gross / current_rev * 100 if current_rev > 0 else 0
current_month_ads = monthly_ads.iloc[-1]
prev_month_ads = monthly_ads.iloc[-2]
current_roas = float(current_month_ads["ROAS平均"])
prev_roas = float(prev_month_ads["ROAS平均"])
high_risk_customers = customers[customers["離脱リスクスコア"] >= risk_threshold]
high_risk_ratio = len(high_risk_customers) / len(customers) * 100

mom = (current_rev - prev_rev) / prev_rev * 100 if prev_rev != 0 else 0
sign = "+" if mom >= 0 else ""

st.markdown(f"""
<div class="hero-section">
<h1>📰 EC月次AIブリーフィング</h1>
<p>月次経営会議の資料が5分で完成 — <strong>L3 プレミアムパック 月額26万円</strong>の伴走支援を可視化<br>
<span style="font-size:0.95rem;opacity:0.9;">GA4・Lookerでは見えない "次の一手" を、AI自動生成のエグゼクティブサマリーとアクション提案で即座に提示</span></p>
</div>
""", unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">¥{current_rev // 10000:,}万</div>'
                f'<div class="kpi-label">当月売上<br>前月比 {sign}{mom:.1f}%</div></div>',
                unsafe_allow_html=True)
with kpi_col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{gross_margin:.1f}%</div>'
                f'<div class="kpi-label">粗利率</div></div>', unsafe_allow_html=True)
with kpi_col3:
    roas_diff = current_roas - prev_roas
    sign3 = "+" if roas_diff >= 0 else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{current_roas:.2f}</div>'
                f'<div class="kpi-label">平均ROAS<br>前月比 {sign3}{roas_diff:.2f}</div></div>',
                unsafe_allow_html=True)
with kpi_col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_risk_ratio:.1f}%</div>'
                f'<div class="kpi-label">離脱リスク高顧客比率<br>({len(high_risk_customers)}人)</div></div>',
                unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ===== タブ =====
current_m = monthly_orders["年月"].iloc[-1]
prev_m = monthly_orders["年月"].iloc[-2]

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 今月のサマリー",
    "🔗 チャネル別ROIレビュー",
    "👥 離脱リスク顧客TOP20",
    "🎯 次月アクション & レポート"
])

with tab1:
    render_tab1(orders_df, ads_df, current_m, prev_m, current_rev, prev_rev,
                current_roas, prev_roas, gross_margin, high_risk_ratio,
                high_risk_customers, risk_threshold)

with tab2:
    channel_detail = render_tab2(ads_df, current_m, prev_m)

with tab3:
    render_tab3(customers, high_risk_customers, risk_threshold)

with tab4:
    render_tab4(ads_df, products, customers, channel_detail, current_m,
                current_rev, prev_rev, gross_margin, current_roas, high_risk_ratio,
                risk_threshold, high_risk_customers)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem; padding: 1rem 0;">
EC月次AIブリーフィング | 月額26万円プレミアムパック L3キラー機能<br>
データはサンプルです。実運用では実際のECデータを接続してください。
</div>
""", unsafe_allow_html=True)
