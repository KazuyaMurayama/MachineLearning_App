import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ---------------------------------------------------------------------------
# Japanese font setup
# ---------------------------------------------------------------------------
def setup_japanese_font():
    candidates = ["Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic", "MS Gothic", "Meiryo", "DejaVu Sans"]
    available = {f.name for f in fm.fontManager.ttflist}
    for fn in candidates:
        if fn in available:
            plt.rcParams["font.family"] = fn
            plt.rcParams["axes.unicode_minus"] = False
            return fn
    plt.rcParams["font.family"] = "DejaVu Sans"
    return "DejaVu Sans"

FONT_NAME = setup_japanese_font()
THEME_COLOR = "#2563EB"

# ---------------------------------------------------------------------------
# Page config & CSS
# ---------------------------------------------------------------------------
st.set_page_config(page_title="EC売上ダッシュボード", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.hero-section {
    background: linear-gradient(180deg, #EFF6FF, #FFFFFF);
    padding: 2rem 2rem 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hero-title {
    color: #2563EB;
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
}
.hero-sub {
    color: #475569;
    font-size: 1.05rem;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-label {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1E293B;
}
.kpi-delta-up { color: #16A34A; font-size: 0.9rem; }
.kpi-delta-down { color: #DC2626; font-size: 0.9rem; }
hr.section-divider {
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State + Auto-load
# ---------------------------------------------------------------------------
for k, v in {"df": None, "loaded": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "daily_sales.csv")
    if os.path.exists(p):
        df = pd.read_csv(p, encoding="utf-8-sig")
        df["日付"] = pd.to_datetime(df["日付"])
        st.session_state.df = df
        st.session_state.loaded = True

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📊 EC売上ダッシュボード")
    st.markdown("---")

    uploaded = st.file_uploader("📂 CSVアップロード", type=["csv"])
    st.caption("**必須カラム:** 日付 / カテゴリ / 売上金額 / 注文件数 / 客単価")

    if uploaded is not None:
        try:
            df_up = pd.read_csv(uploaded, encoding="utf-8-sig")
            required = {"日付", "カテゴリ", "売上金額", "注文件数", "客単価"}
            if not required.issubset(set(df_up.columns)):
                st.error(f"必須カラムが不足しています: {required - set(df_up.columns)}")
            else:
                df_up["日付"] = pd.to_datetime(df_up["日付"])
                st.session_state.df = df_up
                st.session_state.loaded = True
                st.success("✅ データを読み込みました")
        except Exception as e:
            st.error(f"読み込みエラー: {e}")

    st.markdown("---")
    st.markdown("### 📖 使い方")
    st.markdown("1. CSVをアップロード（任意）\n2. 表示月を選択\n3. 3つのタブで分析")
    st.markdown("---")
    st.caption("Powered by **AI経営パートナー**")

# ---------------------------------------------------------------------------
# Guard: no data
# ---------------------------------------------------------------------------
if st.session_state.df is None:
    st.warning("データが読み込まれていません。サイドバーからCSVをアップロードしてください。")
    st.stop()

df: pd.DataFrame = st.session_state.df.copy()

# ---------------------------------------------------------------------------
# Derived columns
# ---------------------------------------------------------------------------
df["年月"] = df["日付"].dt.to_period("M").astype(str)  # "YYYY-MM"
df["年"] = df["日付"].dt.year
df["月"] = df["日付"].dt.month

months_sorted = sorted(df["年月"].unique())
latest_month = months_sorted[-1]

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📊 EC売上ダッシュボード</div>
    <div class="hero-sub">リアルタイム売上・KPI可視化ツール</div>
</div>
""", unsafe_allow_html=True)

st.info("💡 **導入効果**: 毎月のExcel集計を **3時間→3分** に短縮（年間¥150万相当）")

# ---------------------------------------------------------------------------
# Month selector (used by Tab1 and KPIs)
# ---------------------------------------------------------------------------
selected_month = st.selectbox("📅 分析する月を選択（最新月がデフォルト）", months_sorted, index=len(months_sorted) - 1)

# ---------------------------------------------------------------------------
# Helper: year-over-year
# ---------------------------------------------------------------------------

def _prev_year_month(ym_str: str) -> str:
    """Return 'YYYY-MM' for the same month one year prior."""
    y, m = ym_str.split("-")
    return f"{int(y) - 1}-{m}"


def _month_agg(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to monthly level."""
    return (
        dataframe.groupby("年月")
        .agg(売上金額=("売上金額", "sum"), 注文件数=("注文件数", "sum"), 客単価=("客単価", "mean"))
        .reset_index()
    )


monthly = _month_agg(df)

# Current month figures
cur = monthly[monthly["年月"] == selected_month]
cur_sales = int(cur["売上金額"].values[0]) if len(cur) else 0
cur_orders = int(cur["注文件数"].values[0]) if len(cur) else 0
cur_aov = int(cur["客単価"].values[0]) if len(cur) else 0

prev_ym = _prev_year_month(selected_month)
prev = monthly[monthly["年月"] == prev_ym]
prev_sales = int(prev["売上金額"].values[0]) if len(prev) else None
yoy_pct = ((cur_sales / prev_sales - 1) * 100) if prev_sales else None

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

def _kpi(col, label, value_str, delta_str=None, delta_up=True):
    delta_html = ""
    if delta_str is not None:
        cls = "kpi-delta-up" if delta_up else "kpi-delta-down"
        arrow = "▲" if delta_up else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta_str}</div>'
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value_str}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

_kpi(k1, "当月売上合計", f"¥{cur_sales:,.0f}")
if yoy_pct is not None:
    _kpi(k2, "前年同月比", f"{yoy_pct:+.1f}%", f"{yoy_pct:+.1f}%", yoy_pct >= 0)
else:
    _kpi(k2, "前年同月比", "—（前年データなし）")
_kpi(k3, "当月平均客単価", f"¥{cur_aov:,.0f}")
_kpi(k4, "当月注文件数", f"{cur_orders:,}")

st.markdown("")

# ===================================================================
# TABS
# ===================================================================
tab1, tab2, tab3 = st.tabs(["📋 売上サマリー", "🏷️ カテゴリ分析", "📈 KPIトレンド"])

# ===================================================================
# Tab 1: 売上サマリー
# ===================================================================
with tab1:
    st.subheader(f"日別売上推移（{selected_month}）")

    df_month = df[df["年月"] == selected_month]
    daily = df_month.groupby("日付")["売上金額"].sum().reset_index().sort_values("日付")

    mean_val = daily["売上金額"].mean()
    std_val = daily["売上金額"].std()
    daily["異常"] = (daily["売上金額"] > mean_val + 2 * std_val) | (daily["売上金額"] < mean_val - 2 * std_val)

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(daily["日付"], daily["売上金額"], color=THEME_COLOR, linewidth=1.5, zorder=2)
    anomaly = daily[daily["異常"]]
    if not anomaly.empty:
        ax1.scatter(anomaly["日付"], anomaly["売上金額"], color="red", s=60, zorder=3, label="異常値 (±2σ)")
        ax1.legend()
    ax1.axhline(mean_val, color="#94A3B8", linestyle="--", linewidth=0.8, label="平均")
    ax1.axhline(mean_val + 2 * std_val, color="#FCA5A5", linestyle=":", linewidth=0.8)
    ax1.axhline(mean_val - 2 * std_val, color="#FCA5A5", linestyle=":", linewidth=0.8)
    ax1.set_title(f"{selected_month} 日別売上", fontsize=13)
    ax1.set_ylabel("売上金額 (¥)")
    ax1.tick_params(axis="x", rotation=45)
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    # Monthly bar chart — highlight selected month
    st.subheader("月別売上推移（全期間）")
    monthly_sorted = monthly.sort_values("年月")
    colors_bar = [THEME_COLOR if ym == selected_month else "#BFDBFE" for ym in monthly_sorted["年月"]]

    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.bar(monthly_sorted["年月"], monthly_sorted["売上金額"], color=colors_bar)
    ax2.set_ylabel("売上金額 (¥)")
    ax2.set_title("月別売上（選択月をハイライト）", fontsize=13)
    ax2.tick_params(axis="x", rotation=45)
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # Year-over-year comparison table
    if prev_sales is not None:
        st.subheader("前年同月比較")
        comp = pd.DataFrame({
            "項目": ["売上金額", "注文件数", "客単価"],
            f"{selected_month}": [
                f"¥{cur_sales:,.0f}",
                f"{cur_orders:,}",
                f"¥{cur_aov:,.0f}",
            ],
            f"{prev_ym}": [
                f"¥{prev_sales:,.0f}",
                f"{int(prev['注文件数'].values[0]):,}",
                f"¥{int(prev['客単価'].values[0]):,.0f}",
            ],
            "前年同月比 (%)": [
                f"{(cur_sales / prev_sales - 1) * 100:+.1f}%",
                f"{(cur_orders / int(prev['注文件数'].values[0]) - 1) * 100:+.1f}%",
                f"{(cur_aov / int(prev['客単価'].values[0]) - 1) * 100:+.1f}%",
            ],
        })
        st.table(comp)

# ===================================================================
# Tab 2: カテゴリ分析
# ===================================================================
with tab2:
    st.subheader("カテゴリ別売上構成比")
    cat_sales = df_month.groupby("カテゴリ")["売上金額"].sum()

    fig3, ax3 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax3.pie(
        cat_sales, labels=cat_sales.index, autopct="%1.1f%%",
        startangle=140, colors=["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"],
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax3.set_title(f"{selected_month} カテゴリ別売上構成比", fontsize=13)
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    # Stacked bar: category x month
    st.subheader("カテゴリ別月次売上推移（積み上げ）")
    cat_monthly = df.groupby(["年月", "カテゴリ"])["売上金額"].sum().reset_index()
    pivot = cat_monthly.pivot(index="年月", columns="カテゴリ", values="売上金額").fillna(0)
    pivot = pivot.loc[sorted(pivot.index)]

    fig4, ax4 = plt.subplots(figsize=(14, 5))
    bottom = np.zeros(len(pivot))
    palette = ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
    for i, cat in enumerate(pivot.columns):
        ax4.bar(pivot.index, pivot[cat], bottom=bottom, label=cat, color=palette[i % len(palette)])
        bottom += pivot[cat].values
    ax4.set_ylabel("売上金額 (¥)")
    ax4.set_title("カテゴリ別月次売上推移", fontsize=13)
    ax4.legend(loc="upper left", fontsize=8)
    ax4.tick_params(axis="x", rotation=45)
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    # Growth rate ranking
    st.subheader("カテゴリ別成長率ランキング（前年比）")
    cat_yearly = df.groupby(["年", "カテゴリ"])["売上金額"].sum().reset_index()
    years = sorted(cat_yearly["年"].unique())
    if len(years) >= 2:
        last_year = years[-1]
        prev_year = years[-2]
        cy = cat_yearly[cat_yearly["年"] == last_year].set_index("カテゴリ")["売上金額"]
        py = cat_yearly[cat_yearly["年"] == prev_year].set_index("カテゴリ")["売上金額"]
        growth = ((cy / py - 1) * 100).dropna().sort_values(ascending=False).reset_index()
        growth.columns = ["カテゴリ", "前年比成長率 (%)"]
        growth["前年比成長率 (%)"] = growth["前年比成長率 (%)"].map(lambda x: f"{x:+.1f}%")
        growth.index = range(1, len(growth) + 1)
        growth.index.name = "順位"
        st.table(growth)
    else:
        st.info("前年データがないため成長率を算出できません。")

# ===================================================================
# Tab 3: KPIトレンド
# ===================================================================
with tab3:
    monthly_sorted = monthly.sort_values("年月")

    # 客単価推移
    st.subheader("月別 客単価推移")
    fig5, ax5 = plt.subplots(figsize=(12, 4))
    ax5.plot(monthly_sorted["年月"], monthly_sorted["客単価"], marker="o", color=THEME_COLOR, linewidth=1.5)
    ax5.set_ylabel("客単価 (¥)")
    ax5.set_title("客単価推移", fontsize=13)
    ax5.tick_params(axis="x", rotation=45)
    fig5.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

    # 注文件数推移
    st.subheader("月別 注文件数推移")
    fig6, ax6 = plt.subplots(figsize=(12, 4))
    ax6.plot(monthly_sorted["年月"], monthly_sorted["注文件数"], marker="o", color="#16A34A", linewidth=1.5)
    ax6.set_ylabel("注文件数")
    ax6.set_title("注文件数推移", fontsize=13)
    ax6.tick_params(axis="x", rotation=45)
    fig6.tight_layout()
    st.pyplot(fig6)
    plt.close(fig6)

    # 売上推移: 前年同月比較
    st.subheader("月別売上推移（前年同月比較）")
    monthly_sorted_copy = monthly_sorted.copy()
    monthly_sorted_copy["月num"] = monthly_sorted_copy["年月"].str[5:7]
    monthly_sorted_copy["年num"] = monthly_sorted_copy["年月"].str[:4]

    years_in_data = sorted(monthly_sorted_copy["年num"].unique())
    fig7, ax7 = plt.subplots(figsize=(12, 4))
    color_map = {years_in_data[-1]: THEME_COLOR}
    if len(years_in_data) >= 2:
        color_map[years_in_data[-2]] = "#93C5FD"
    for yr in reversed(years_in_data[-2:]):
        sub = monthly_sorted_copy[monthly_sorted_copy["年num"] == yr].sort_values("月num")
        style = "-" if yr == years_in_data[-1] else "--"
        ax7.plot(sub["月num"], sub["売上金額"], marker="o", linestyle=style,
                 color=color_map.get(yr, "#CBD5E1"), linewidth=1.5, label=f"{yr}年")
    ax7.set_ylabel("売上金額 (¥)")
    ax7.set_xlabel("月")
    ax7.set_title("売上推移 前年同月比較", fontsize=13)
    ax7.legend()
    fig7.tight_layout()
    st.pyplot(fig7)
    plt.close(fig7)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1, fc2, fc3 = st.columns(3)
fc1.markdown("👥 [顧客RFM分析](https://ec-rfm.streamlit.app)  \n顧客セグメントを自動分類")
fc2.markdown("📈 [広告ROI分析](https://ec-ad-roi.streamlit.app)  \n広告費用対効果を最適化")
fc3.markdown("🛒 [EC離脱予測](https://ec-demo.streamlit.app)  \n顧客離脱をAIで予測")
st.caption("AI経営パートナー × データサイエンス | 売上ダッシュボード v1.0")
