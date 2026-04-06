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

    # --- 月間売上目標トラッカー (データ読み込み後に表示) ---
    if st.session_state.loaded and st.session_state.df is not None:
        st.markdown("### 🎯 月間売上目標")
        # 当月実績の120%をデフォルト目標にする（後でdf/monthly確定後に使用）
        # デフォルト値はセッションで保持
        if "sales_target" not in st.session_state:
            st.session_state.sales_target = 0  # 仮; データ確定後に更新

        _target_input = st.number_input(
            "月間売上目標 (¥)",
            min_value=0,
            value=st.session_state.sales_target if st.session_state.sales_target > 0 else 1000000,
            step=100000,
            format="%d",
            key="sales_target_input",
        )
        st.session_state.sales_target = _target_input
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

# ---------------------------------------------------------------------------
# 売上予測ロジック（移動平均 + 線形回帰）
# ---------------------------------------------------------------------------

def _forecast_next_months(monthly_df: pd.DataFrame, n_forecast: int = 3, window: int = 6):
    """
    直近 window ヶ月の移動平均 + numpy.polyfit(degree=1) で翌 n_forecast ヶ月を予測する。
    Returns:
        forecast_vals (list[float]): 予測値リスト (長さ n_forecast)
        forecast_labels (list[str]): 予測月ラベル "YYYY-MM"
        ma_series (np.ndarray): 全月の移動平均（len == len(monthly_df)）
        slope (float): 傾き（線形回帰）
    """
    ms = monthly_df.sort_values("年月").reset_index(drop=True)
    sales = ms["売上金額"].values.astype(float)
    n = len(sales)

    # 移動平均
    ma = np.array([
        sales[max(0, i - window + 1): i + 1].mean() for i in range(n)
    ])

    # 線形回帰: 直近 window ヶ月のみ使用
    fit_start = max(0, n - window)
    x_fit = np.arange(fit_start, n)
    y_fit = sales[fit_start:]
    coeffs = np.polyfit(x_fit, y_fit, deg=1)  # [slope, intercept]
    slope, intercept = coeffs

    # 予測値 = 線形回帰の外挿
    forecast_vals = [slope * (n + i) + intercept for i in range(n_forecast)]

    # 予測月ラベル
    last_ym = ms["年月"].iloc[-1]
    y, m = int(last_ym[:4]), int(last_ym[5:7])
    forecast_labels = []
    for _ in range(n_forecast):
        m += 1
        if m > 12:
            m = 1
            y += 1
        forecast_labels.append(f"{y:04d}-{m:02d}")

    return forecast_vals, forecast_labels, ma, slope


forecast_vals, forecast_labels, ma_series, forecast_slope = _forecast_next_months(monthly, n_forecast=3, window=6)

# 来月予測 & 前月比
_next_month_pred = forecast_vals[0] if forecast_vals else None
_monthly_sorted_for_fc = monthly.sort_values("年月")
_last_actual_sales = _monthly_sorted_for_fc["売上金額"].iloc[-1] if len(_monthly_sorted_for_fc) else 0
_mom_forecast_pct = ((_next_month_pred / _last_actual_sales - 1) * 100) if (_next_month_pred and _last_actual_sales) else None
_confidence_margin = _next_month_pred * 0.10 if _next_month_pred else 0  # ±10%

# サイドバー: 月間目標のデフォルト値を当月実績の120%に設定
if st.session_state.get("sales_target", 0) <= 1000000:
    _default_target = int(cur_sales * 1.2) if cur_sales > 0 else 1000000
    st.session_state.sales_target = _default_target

# ---------------------------------------------------------------------------
# 予測サマリーバナー（KPIカード直下）
# ---------------------------------------------------------------------------
if _next_month_pred is not None and _mom_forecast_pct is not None:
    _pred_man = _next_month_pred / 10000
    _margin_man = _confidence_margin / 10000
    _pred_label = f"来月予測: ¥{_pred_man:,.0f}万（±{_margin_man:,.0f}万）"
    if _mom_forecast_pct >= 0:
        st.success(
            f"📈 {_pred_label}。前月比 **{_mom_forecast_pct:+.1f}%** — 成長トレンド継続中"
        )
    else:
        st.warning(
            f"📉 {_pred_label}。前月比 **{_mom_forecast_pct:+.1f}%** — 売上減少が予測されます。施策を検討してください"
        )

# ---------------------------------------------------------------------------
# 目標達成率トラッカー
# ---------------------------------------------------------------------------
_sales_target = st.session_state.get("sales_target", 0)
if _sales_target > 0 and cur_sales >= 0:
    _progress_ratio = min(cur_sales / _sales_target, 1.0)
    st.markdown("#### 🎯 月間目標達成状況")
    _pc1, _pc2 = st.columns([3, 1])
    with _pc1:
        st.progress(_progress_ratio)
    with _pc2:
        st.write(f"**{_progress_ratio * 100:.1f}%**")

    if cur_sales >= _sales_target:
        st.success("🎉 目標達成済み！素晴らしい結果です。")
    else:
        _remaining = _sales_target - cur_sales
        _remaining_man = _remaining / 10000
        st.info(f"目標達成まであと **¥{_remaining_man:,.0f}万**")

        # 残日数から必要日次売上を計算
        import datetime as _dt
        _today = _dt.date.today()
        _sel_year_t = int(selected_month.split("-")[0])
        _sel_month_t = int(selected_month.split("-")[1])
        # 当月最終日
        if _sel_month_t == 12:
            _last_day = _dt.date(_sel_year_t + 1, 1, 1) - _dt.timedelta(days=1)
        else:
            _last_day = _dt.date(_sel_year_t, _sel_month_t + 1, 1) - _dt.timedelta(days=1)
        _days_left = (_last_day - _today).days
        if _days_left > 0:
            _daily_needed = _remaining / _days_left / 10000
            st.caption(f"残 {_days_left} 日 → 必要な日次売上: **¥{_daily_needed:,.1f}万/日**")
        elif _days_left == 0:
            st.caption("本日が月末です。最終日の売上に注目！")

st.markdown("")

# ---------------------------------------------------------------------------
# Insight banner & factor decomposition banner (above tabs)
# ---------------------------------------------------------------------------
_m_idx_top = list(monthly.sort_values("年月")["年月"])
_sel_pos_top = _m_idx_top.index(selected_month) if selected_month in _m_idx_top else -1

# --- 1. 要因分解の主因バナー ---
if _sel_pos_top >= 1:
    _cur_r = monthly[monthly["年月"] == selected_month].iloc[0]
    _prev_m_ym = _m_idx_top[_sel_pos_top - 1]
    _prev_r = monthly[monthly["年月"] == _prev_m_ym].iloc[0]
    _d_sales = _cur_r["売上金額"] - _prev_r["売上金額"]
    _d_aov_c = (_cur_r["客単価"] - _prev_r["客単価"]) * _prev_r["注文件数"]
    _d_ord_c = (_cur_r["注文件数"] - _prev_r["注文件数"]) * _cur_r["客単価"]
    _ord_pct = (_cur_r["注文件数"] / _prev_r["注文件数"] - 1) * 100 if _prev_r["注文件数"] else 0
    _aov_pct = (_cur_r["客単価"] / _prev_r["客単価"] - 1) * 100 if _prev_r["客単価"] else 0
    if abs(_d_aov_c) >= abs(_d_ord_c):
        _cause = f"客単価 {_aov_pct:+.0f}%"
    else:
        _cause = f"注文件数 {_ord_pct:+.0f}%"
    _arrow = "▲" if _d_sales >= 0 else "▼"
    st.warning(f"📊 **前月比 {_arrow}¥{abs(_d_sales):,.0f}** — 主因: {_cause}")

# --- 2. 今月のインサイト (1-2行サマリー) ---
_insight_parts = []
if yoy_pct is not None:
    _insight_parts.append(f"売上は前年同月比 **{yoy_pct:+.1f}%**")
if _sel_pos_top >= 1:
    _mom_pct = (_cur_r["売上金額"] / _prev_r["売上金額"] - 1) * 100 if _prev_r["売上金額"] else 0
    _insight_parts.append(f"前月比 **{_mom_pct:+.1f}%**")
# Top growing category
_sel_y = int(selected_month.split("-")[0])
_sel_m = int(selected_month.split("-")[1])
_df_s = df[(df["年"] == _sel_y) & (df["月"] == _sel_m)]
_df_py = df[(df["年"] == _sel_y - 1) & (df["月"] == _sel_m)]
if not _df_s.empty and not _df_py.empty:
    _cc = _df_s.groupby("カテゴリ")["売上金額"].sum()
    _cp = _df_py.groupby("カテゴリ")["売上金額"].sum()
    _cg = ((_cc / _cp - 1) * 100).dropna().sort_values(ascending=False)
    if len(_cg):
        _insight_parts.append(f"カテゴリ「{_cg.index[0]}」が前年比 **{_cg.iloc[0]:+.0f}%** で牽引")
if _insight_parts:
    st.info("💡 **今月のインサイト**: " + "。".join(_insight_parts) + "。")

# ---------------------------------------------------------------------------
# Action List — auto-generated insights (placed above tabs)
# ---------------------------------------------------------------------------
def _generate_action_list(df, monthly, selected_month, months_sorted):
    """Analyse data and return a list of actionable insight strings."""
    actions = []

    # --- 1. Category YoY growth check ---
    sel_year = int(selected_month.split("-")[0])
    sel_month_num = int(selected_month.split("-")[1])
    df_sel = df[(df["年"] == sel_year) & (df["月"] == sel_month_num)]
    df_prev_y = df[(df["年"] == sel_year - 1) & (df["月"] == sel_month_num)]
    if not df_sel.empty and not df_prev_y.empty:
        cat_cur = df_sel.groupby("カテゴリ")["売上金額"].sum()
        cat_prev = df_prev_y.groupby("カテゴリ")["売上金額"].sum()
        cat_growth = ((cat_cur / cat_prev - 1) * 100).dropna().sort_values(ascending=False)
        if len(cat_growth) and cat_growth.iloc[0] > 10:
            actions.append(
                f"カテゴリ「{cat_growth.index[0]}」の売上が前年同月比 **{cat_growth.iloc[0]:+.0f}%** → 販促強化を推奨"
            )

    # --- 2. AOV trend (2-month consecutive decline) ---
    m_sorted = monthly.sort_values("年月")
    idx = list(m_sorted["年月"]).index(selected_month) if selected_month in list(m_sorted["年月"]) else -1
    if idx >= 2:
        aov_vals = m_sorted["客単価"].values
        if aov_vals[idx] < aov_vals[idx - 1] < aov_vals[idx - 2]:
            actions.append("客単価が **2ヶ月連続低下** → バンドル販売やアップセル施策を検討")

    # --- 3. Anomaly status ---
    df_month_tmp = df[df["年月"] == selected_month]
    daily_tmp = df_month_tmp.groupby("日付")["売上金額"].sum()
    mean_tmp = daily_tmp.mean()
    std_tmp = daily_tmp.std()
    n_anomaly = int(((daily_tmp > mean_tmp + 2 * std_tmp) | (daily_tmp < mean_tmp - 2 * std_tmp)).sum())
    if n_anomaly > 0:
        actions.append(f"当月に **{n_anomaly}件** の売上異常値を検出 → 「売上サマリー」タブで詳細を確認")
    else:
        actions.append("当月の売上に異常値なし → 現状施策を維持")

    # Fallback if empty
    if not actions:
        actions.append("特筆すべき変化はありません。現状施策を継続してください。")
    return actions


action_items = _generate_action_list(df, monthly, selected_month, months_sorted)
st.markdown("### 📝 今月のアクションリスト")
for i, item in enumerate(action_items, 1):
    st.markdown(f"**{i}.** {item}")
st.markdown("")

# ===================================================================
# TABS
# ===================================================================
tab1, tab2, tab3 = st.tabs(["📋 売上サマリー", "🏷️ カテゴリ分析", "📈 KPIトレンド"])

# ===================================================================
# Tab 1: 売上サマリー
# ===================================================================
with tab1:
    # ----- Sales variance decomposition (Factor Analysis) -----
    st.subheader("売上変動の要因分解（前月比）")
    _m_idx = list(monthly.sort_values("年月")["年月"])
    _sel_pos = _m_idx.index(selected_month) if selected_month in _m_idx else -1
    if _sel_pos >= 1:
        _cur_row = monthly[monthly["年月"] == selected_month].iloc[0]
        _prev_month_ym = _m_idx[_sel_pos - 1]
        _prev_row = monthly[monthly["年月"] == _prev_month_ym].iloc[0]
        _delta_aov = _cur_row["客単価"] - _prev_row["客単価"]
        _delta_orders = _cur_row["注文件数"] - _prev_row["注文件数"]
        _aov_contribution = _delta_aov * _prev_row["注文件数"]
        _orders_contribution = _delta_orders * _cur_row["客単価"]
        _delta_sales = _cur_row["売上金額"] - _prev_row["売上金額"]

        _fc1, _fc2, _fc3 = st.columns(3)
        _fc1.metric("売上変動額（前月比）", f"¥{_delta_sales:+,.0f}")
        _fc2.metric("客単価変化の寄与", f"¥{_aov_contribution:+,.0f}")
        _fc3.metric("注文件数変化の寄与", f"¥{_orders_contribution:+,.0f}")

        if abs(_aov_contribution) >= abs(_orders_contribution):
            _direction = "上昇" if _aov_contribution > 0 else "低下"
            st.info(
                f"📊 **売上変動の主因: 客単価の{_direction}**（寄与額 ¥{_aov_contribution:+,.0f}）"
            )
        else:
            _direction = "増加" if _orders_contribution > 0 else "減少"
            st.warning(
                f"📊 **売上変動の主因: 注文件数の{_direction}**（寄与額 ¥{_orders_contribution:+,.0f}）"
            )
    else:
        st.info("前月データがないため要因分解を表示できません。")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

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

    # ----- Anomaly root-cause analysis -----
    if not anomaly.empty:
        st.markdown("#### 異常値の推定原因と推奨アクション")
        for _, arow in anomaly.iterrows():
            _a_date = arow["日付"]
            _a_val = arow["売上金額"]
            _a_date_str = _a_date.strftime("%m/%d")
            # Get previous day data
            _prev_date = _a_date - pd.Timedelta(days=1)
            _prev_daily = daily[daily["日付"] == _prev_date]
            _prev_val = _prev_daily["売上金額"].values[0] if len(_prev_daily) else mean_val

            if _a_val > mean_val:
                # Sales spike — find category driver
                _cat_today = df_month[df_month["日付"] == _a_date].groupby("カテゴリ")["売上金額"].sum()
                _cat_prev = df_month[df_month["日付"] == _prev_date].groupby("カテゴリ")["売上金額"].sum()
                _cat_diff = (_cat_today - _cat_prev).dropna().sort_values(ascending=False)
                if len(_cat_diff) and _cat_diff.iloc[0] > 0:
                    _top_cat = _cat_diff.index[0]
                    _pct_chg = (_cat_today[_top_cat] / _cat_prev[_top_cat] - 1) * 100 if _top_cat in _cat_prev.index and _cat_prev[_top_cat] > 0 else 0
                    st.success(
                        f"📈 **{_a_date_str}** 売上急増（¥{_a_val:,.0f}）: "
                        f"「{_top_cat}」が前日比 **{_pct_chg:+.0f}%**。セール効果の可能性"
                    )
                else:
                    st.success(f"📈 **{_a_date_str}** 売上急増（¥{_a_val:,.0f}）: 複数カテゴリで売上増加")
            else:
                # Sales dip — check AOV vs order count
                _day_data = df_month[df_month["日付"] == _a_date]
                _prev_data = df_month[df_month["日付"] == _prev_date]
                _day_orders = _day_data["注文件数"].sum()
                _prev_orders = _prev_data["注文件数"].sum() if len(_prev_data) else _day_orders
                _day_aov = _day_data["客単価"].mean()
                _prev_aov = _prev_data["客単価"].mean() if len(_prev_data) else _day_aov

                _order_chg = ((_day_orders / _prev_orders - 1) * 100) if _prev_orders > 0 else 0
                _aov_chg = ((_day_aov / _prev_aov - 1) * 100) if _prev_aov > 0 else 0

                if abs(_order_chg) >= abs(_aov_chg):
                    st.warning(
                        f"📉 **{_a_date_str}** 売上急落（¥{_a_val:,.0f}）: "
                        f"注文件数が **{_order_chg:+.0f}%**。集客施策の見直しを推奨"
                    )
                else:
                    st.warning(
                        f"📉 **{_a_date_str}** 売上急落（¥{_a_val:,.0f}）: "
                        f"客単価が **{_aov_chg:+.0f}%**。商品単価・セット販売の見直しを推奨"
                    )

    # Monthly bar chart — highlight selected month + forecast line
    st.subheader("月別売上推移（全期間）＋売上予測")
    monthly_sorted = monthly.sort_values("年月")
    colors_bar = [THEME_COLOR if ym == selected_month else "#BFDBFE" for ym in monthly_sorted["年月"]]

    # 予測ラベル・値
    _fc_vals_tab = forecast_vals
    _fc_labels_tab = forecast_labels
    _ma_tab = ma_series

    # すべてのラベル（実績 + 予測）
    _all_labels = list(monthly_sorted["年月"]) + _fc_labels_tab
    _n_actual = len(monthly_sorted)
    _x_actual = list(range(_n_actual))
    _x_forecast = list(range(_n_actual, _n_actual + len(_fc_labels_tab)))
    _all_x = _x_actual + _x_forecast

    fig2, ax2 = plt.subplots(figsize=(13, 5))

    # 棒グラフ（実績）
    ax2.bar(_x_actual, monthly_sorted["売上金額"].values, color=colors_bar, zorder=2, label="実績")

    # 移動平均ライン（実績期間）
    ax2.plot(_x_actual, _ma_tab, color="#F59E0B", linewidth=1.5, linestyle="-", marker="", zorder=3, label="移動平均（6ヶ月）")

    # 予測ライン（点線）
    if _fc_vals_tab:
        # 実績最後の点から予測へ接続
        _connect_x = [_x_actual[-1]] + _x_forecast
        _connect_y = [monthly_sorted["売上金額"].values[-1]] + _fc_vals_tab
        ax2.plot(_connect_x, _connect_y, color="#DC2626", linewidth=2, linestyle="--", marker="o",
                 markersize=5, zorder=4, label="予測（線形回帰）")

        # 信頼区間 ±10%
        _fc_arr = np.array(_fc_vals_tab)
        _fc_upper = _fc_arr * 1.10
        _fc_lower = _fc_arr * 0.90
        # 接続点を含む fill_between
        _fill_x = [_x_actual[-1]] + _x_forecast
        _fill_upper = [monthly_sorted["売上金額"].values[-1] * 1.10] + list(_fc_upper)
        _fill_lower = [monthly_sorted["売上金額"].values[-1] * 0.90] + list(_fc_lower)
        ax2.fill_between(_fill_x, _fill_lower, _fill_upper, color="#FCA5A5", alpha=0.3, zorder=1, label="信頼区間（±10%）")

    # X軸ラベル
    ax2.set_xticks(_all_x)
    ax2.set_xticklabels(_all_labels, rotation=45, ha="right")
    ax2.set_ylabel("売上金額 (¥)")
    ax2.set_title("月別売上（選択月ハイライト）＋翌3ヶ月予測", fontsize=13)
    ax2.legend(fontsize=8, loc="upper left")
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # 予測値の詳細を metric で表示
    if _fc_vals_tab and len(_fc_labels_tab) >= 1:
        st.markdown("#### 📊 売上予測サマリー")
        _mc_list = st.columns(min(3, len(_fc_labels_tab)))
        for _i, (_lbl, _val) in enumerate(zip(_fc_labels_tab[:3], _fc_vals_tab[:3])):
            _man = _val / 10000
            _margin_man_tab = _val * 0.10 / 10000
            _delta_val = ((_val / _last_actual_sales - 1) * 100) if _last_actual_sales else 0
            _mc_list[_i].metric(
                label=f"{_lbl} 予測",
                value=f"¥{_man:,.0f}万",
                delta=f"{_delta_val:+.1f}% vs 直近実績",
            )
        _cf1, _cf2 = st.columns(2)
        _cf1.caption(f"予測方法: 直近6ヶ月移動平均 + 線形回帰（numpy.polyfit degree=1）")
        _cf2.caption(f"信頼区間: ±10%（簡易推定）")

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
# 定期運用チェックリスト
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 📋 定期運用チェックリスト")
with st.expander("週次チェック"):
    st.markdown("- □ 日別売上で異常値を確認\n- □ カテゴリ別の前週比を確認\n- □ 異常値の原因を特定しメモ")
with st.expander("月次チェック"):
    st.markdown(
        "- □ 月次レポートを確認（前月比・前年比）\n- □ カテゴリ別成長率ランキングを確認\n"
        "- □ 客単価トレンドを確認し施策検討\n- □ RFM分析で顧客セグメントを更新"
    )

# ---------------------------------------------------------------------------
# Footer — 関連ツールカード
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
_card = (
    '<div class="kpi-card" style="text-align:left;padding:1rem 1.2rem">'
    '<div style="font-size:1.3rem">{icon}</div>'
    '<div style="font-weight:700;margin:0.3rem 0">{name}</div>'
    '<div style="font-size:0.85rem;color:#475569;margin-bottom:0.5rem">{desc}</div>'
    '<div style="font-size:0.8rem">▶ {action}</div>'
    '<a href="{url}" target="_blank" style="font-size:0.8rem;color:#2563EB">ツールを開く →</a></div>'
)
fc1, fc2, fc3 = st.columns(3)
fc1.markdown(_card.format(icon="👥", name="顧客RFM分析", desc="顧客セグメントを自動分類",
             action="売上が落ちたセグメントを特定する", url="https://ec-rfm-analysis.streamlit.app"), unsafe_allow_html=True)
fc2.markdown(_card.format(icon="📣", name="広告ROI分析", desc="広告費用対効果を最適化",
             action="集客チャネルの費用対効果を確認する", url="https://ec-ad-roi.streamlit.app"), unsafe_allow_html=True)
fc3.markdown(_card.format(icon="🛒", name="EC離脱予測", desc="顧客離脱をAIで予測",
             action="離脱リスクの高い顧客を特定する", url="https://ec-demo.streamlit.app"), unsafe_allow_html=True)
st.caption("AI経営パートナー × データサイエンス | 売上ダッシュボード v1.0")
