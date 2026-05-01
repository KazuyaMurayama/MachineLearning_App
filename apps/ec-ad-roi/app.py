"""
広告ROI分析ツール
=================
チャネル別ROAS分析・予算配分シミュレーション・トレンド分析
MVP #12
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import lightgbm as lgb
import shap

# === 日本語フォント ===
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

_font = setup_japanese_font()

# === ページ設定 ===
st.set_page_config(page_title="広告ROI分析ツール", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# === CSS ===
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(180deg, #ECFDF5, #FFFFFF);
    padding: 2rem 2rem 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hero-title {
    color: #059669;
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}
.hero-subtitle {
    color: #6B7280;
    font-size: 1rem;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #059669;
}
.kpi-label {
    font-size: 0.85rem;
    color: #6B7280;
    margin-top: 0.2rem;
}
.highlight-row {
    background-color: #ECFDF5 !important;
}
hr.section-divider {
    margin-top: 2rem;
    margin-bottom: 1rem;
    border: none;
    border-top: 1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# === Session State ===
for k, v in {"df": None, "loaded": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === データ読み込みユーティリティ ===
def load_csv(path_or_file):
    try:
        if isinstance(path_or_file, str):
            return pd.read_csv(path_or_file, encoding="utf-8-sig")
        return pd.read_csv(path_or_file, encoding="utf-8-sig")
    except Exception:
        try:
            if isinstance(path_or_file, str):
                return pd.read_csv(path_or_file, encoding="cp932")
            path_or_file.seek(0)
            return pd.read_csv(path_or_file, encoding="cp932")
        except Exception:
            return None

# === トレンド判定ユーティリティ（Tab1・Tab2・KPIで共用） ===
def compute_channel_trend(df, channel):
    ch_data = df[df["チャネル"] == channel].sort_values("月")
    roas_values = ch_data["ROAS"].values if "ROAS" in ch_data.columns else (ch_data["売上"] / ch_data["広告費"]).values
    n = len(roas_values)
    if n >= 9:
        first_half = roas_values[:6].mean()
        last_three = roas_values[-3:].mean()
    elif n >= 3:
        split = max(1, n - 3)
        first_half = roas_values[:split].mean()
        last_three = roas_values[-3:].mean()
    else:
        return "安定"
    change_pct = ((last_three - first_half) / first_half * 100) if first_half > 0 else 0
    if change_pct > 5:
        return "改善"
    elif change_pct < -5:
        return "悪化"
    return "安定"


def investment_judgment(roas, trend):
    if roas >= 2.0 and trend == "改善":
        return "🟢 増額推奨", f"ROAS {roas:.2f}x（≥2.0）& トレンド改善"
    elif roas >= 1.5 and trend in ("安定", "改善"):
        return "🔵 維持", f"ROAS {roas:.2f}x（≥1.5）& トレンド{trend}"
    elif roas < 1.0:
        return "🔴 減額推奨", f"ROAS {roas:.2f}x（<1.0）— 赤字チャネル"
    else:
        return "🟡 要注意", f"ROAS {roas:.2f}x / トレンド{trend} — 改善検討"

# === Auto-load サンプルデータ ===
if not st.session_state.loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "ad_performance.csv")
    if os.path.exists(p):
        st.session_state.df = load_csv(p)
        st.session_state.loaded = True

# === Sidebar ===
with st.sidebar:
    st.markdown("## 📈 広告ROI分析")
    st.markdown("---")
    st.markdown("#### CSVアップロード")
    uploaded = st.file_uploader("広告データCSVを選択", type=["csv"])
    if uploaded:
        df_up = load_csv(uploaded)
        if df_up is not None:
            required = {"月", "チャネル", "広告費", "売上", "CV数"}
            if required.issubset(set(df_up.columns)):
                st.session_state.df = df_up
                st.session_state.loaded = True
                st.success("✅ データを読み込みました")
            else:
                st.error("必須カラムが不足しています")
    st.info("**必須カラム:** 月 / チャネル / 広告費 / 売上 / CV数")
    st.markdown("---")

    # 目標CPA入力
    st.markdown("#### 🎯 目標CPA設定")
    _tmp_df = st.session_state.df
    if _tmp_df is not None:
        _tmp_cpa_median = int((_tmp_df["広告費"].sum() / _tmp_df["CV数"].sum())) if _tmp_df["CV数"].sum() > 0 else 10000
    else:
        _tmp_cpa_median = 10000
    target_cpa = st.number_input(
        "目標CPA（円）", min_value=1000, max_value=500000,
        value=_tmp_cpa_median, step=1000, format="%d",
        help="各チャネルの目標CPA。デフォルトはデータ全体のCPA中央値です。"
    )
    st.markdown("---")
    st.caption("AI経営パートナー × データサイエンス")

# === Hero ===
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📈 広告ROI分析ツール</div>
    <div class="hero-subtitle">チャネル別ROAS・CPAを一画面で比較。予算の無駄を即可視化。</div>
</div>
""", unsafe_allow_html=True)

# === データチェック ===
df = st.session_state.df
if df is None:
    st.warning("データが読み込まれていません。サイドバーからCSVをアップロードしてください。")
    st.stop()

# === 導入効果バナー ===
_b1, _b2, _b3 = st.columns(3)
_b1.error("**Before**\n\n媒体バラバラで効果不明")
_b2.success("**After**\n\n全チャネルROASを一画面比較")
_b3.info("**年間効果**\n\n広告効率30%改善・年間¥300万削減")

# === KPIカード ===
total_cost = df["広告費"].sum()
total_revenue = df["売上"].sum()
overall_roas = total_revenue / total_cost if total_cost > 0 else 0
ch_roas = df.groupby("チャネル").agg({"広告費": "sum", "売上": "sum"}).reset_index()
ch_roas["ROAS"] = ch_roas["売上"] / ch_roas["広告費"]
best_ch = ch_roas.loc[ch_roas["ROAS"].idxmax()]

k1, k2, k3, k4, k5 = st.columns(5)

_ch_trends = {ch: compute_channel_trend(df, ch) for ch in ch_roas["チャネル"]}
_danger_channels = []
for _, r in ch_roas.iterrows():
    label, _ = investment_judgment(float(r["ROAS"]), _ch_trends[r["チャネル"]])
    if "減額" in label:
        monthly_loss = int((r["広告費"] - r["売上"]) / 12)
        _danger_channels.append({"name": r["チャネル"], "roas": r["ROAS"], "loss": monthly_loss})

for col, label, value in [
    (k1, "年間広告費合計", f"¥{total_cost:,.0f}"),
    (k2, "年間売上合計（広告経由）", f"¥{total_revenue:,.0f}"),
    (k3, "全体ROAS", f"{overall_roas:.2f}x"),
    (k4, f"最優秀: {best_ch['チャネル']}", f"ROAS {best_ch['ROAS']:.2f}x"),
    (k5, "🔴 減額推奨", f"{len(_danger_channels)}個"),
]:
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

if _danger_channels:
    _sorted_danger = sorted(_danger_channels, key=lambda x: x["roas"])
    _alert_parts = [f"🔴 {c['name']}: ROAS {c['roas']:.1f}x, 月¥{abs(c['loss']):,}赤字" if c["roas"] < 1.0 else f"🟡 {c['name']}: ROAS {c['roas']:.1f}x, 要注意" for c in _sorted_danger]
    st.warning("⚡ 減額推奨チャネル — " + " / ".join(_alert_parts))
else:
    st.success("✅ 全チャネル黒字。現状維持で問題ありません")

st.markdown("<br>", unsafe_allow_html=True)

# === タブ ===
tab1, tab2, tab3, tab4 = st.tabs(["📊 チャネル別ROAS", "💰 予算配分シミュレーション", "📈 トレンド分析", "🤖 ML予測+SHAP分析"])

# ------------------------------------------------------------------
# タブ1: チャネル別ROAS
# ------------------------------------------------------------------
with tab1:
    st.markdown("### チャネル別ROAS（年間平均）")

    perf = df.groupby("チャネル").agg(
        広告費合計=("広告費", "sum"),
        売上合計=("売上", "sum"),
        CV数=("CV数", "sum"),
    ).reset_index()
    perf["ROAS"] = (perf["売上合計"] / perf["広告費合計"]).round(2)
    perf["CPA"] = (perf["広告費合計"] / perf["CV数"]).astype(int)
    perf = perf.sort_values("ROAS", ascending=False).reset_index(drop=True)

    all_channels = perf["チャネル"].tolist()
    selected_channels = st.multiselect("チャネルを絞込", all_channels, default=all_channels)
    perf_filtered = perf[perf["チャネル"].isin(selected_channels)]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#059669" if r >= perf_filtered["ROAS"].median() else "#6EE7B7" for r in perf_filtered["ROAS"]]
    bars = ax.bar(perf_filtered["チャネル"], perf_filtered["ROAS"], color=colors, edgecolor="white", linewidth=0.8)
    ax.axhline(y=1.0, color="#EF4444", linestyle="--", linewidth=1.5, label="損益分岐 (ROAS=1.0)")
    ax.set_ylabel("ROAS")
    ax.set_title("チャネル別 年間平均ROAS")
    ax.legend()
    for bar, val in zip(bars, perf_filtered["ROAS"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{val:.2f}x", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    perf_filtered = perf_filtered.copy()
    perf_filtered["トレンド"] = perf_filtered["チャネル"].apply(lambda ch: compute_channel_trend(df, ch))
    perf_filtered["投資判定"] = perf_filtered.apply(
        lambda r: investment_judgment(float(r["ROAS"]), r["トレンド"])[0], axis=1)
    perf_filtered["判定理由"] = perf_filtered.apply(
        lambda r: investment_judgment(float(r["ROAS"]), r["トレンド"])[1], axis=1)
    perf_filtered["目標CPA達成"] = perf_filtered["CPA"].apply(
        lambda x: "✅ 達成" if x <= target_cpa else "❌ 未達成")

    st.markdown("### チャネル別パフォーマンス")
    display_perf = perf_filtered.copy()
    display_perf["広告費合計"] = display_perf["広告費合計"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["売上合計"] = display_perf["売上合計"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["CV数"] = display_perf["CV数"].apply(lambda x: f"{x:,}")
    display_perf["CPA_raw"] = display_perf["CPA"]
    display_perf["CPA"] = display_perf["CPA"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["ROAS"] = display_perf["ROAS"].apply(lambda x: f"{x:.2f}x")
    display_perf.insert(0, "🏆", ["⭐" if i < 2 else "" for i in range(len(display_perf))])

    display_cols = ["🏆", "チャネル", "広告費合計", "売上合計", "CV数", "ROAS", "CPA",
                    "投資判定", "判定理由", "目標CPA達成"]
    st.dataframe(display_perf[display_cols], use_container_width=True, hide_index=True)

    missed = perf_filtered[perf_filtered["CPA"] > target_cpa].copy()
    if len(missed) > 0:
        st.markdown("#### 🎯 目標CPA未達成チャネルの改善試算")
        st.caption(f"目標CPA: ¥{target_cpa:,}")
        for _, row in missed.iterrows():
            current_cpa = int(row["CPA"])
            gap = current_cpa - target_cpa
            cost = row["広告費合計"]
            current_cv = int(row["CV数"].replace(",", "")) if isinstance(row["CV数"], str) else int(row["CV数"])
            target_cv = cost / target_cpa
            if current_cv > 0:
                needed_cv_increase = target_cv - current_cv
                needed_cv_increase_pct = (needed_cv_increase / current_cv * 100) if current_cv > 0 else 0
                st.info(
                    f"**{row['チャネル']}**: CPAを ¥{gap:,} 削減が必要 → "
                    f"CV数を現在の{current_cv}件から{int(target_cv)}件へ "
                    f"(+{needed_cv_increase_pct:.1f}% 改善が必要)"
                )

    csv_data = perf_filtered.drop(columns=["トレンド"]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 パフォーマンスデータをCSVダウンロード", csv_data,
                       "channel_performance.csv", "text/csv")

# ------------------------------------------------------------------
# タブ2: 予算配分シミュレーション
# ------------------------------------------------------------------
with tab2:
    st.markdown("### 予算配分シミュレーション")
    st.info("💡 **最適化ロジック**: 各チャネルのROAS（広告費用対効果）に比例して予算を配分します。チャネル別の最低・最大予算制約を設定でき、より現実的なシミュレーションが可能です。")

    total_budget = st.number_input(
        "月間総予算（円）", min_value=100000, max_value=100000000,
        value=1000000, step=100000, format="%d"
    )

    monthly_avg = df.groupby("チャネル")["広告費"].mean().reset_index()
    monthly_avg.columns = ["チャネル", "月平均広告費"]
    monthly_total = monthly_avg["月平均広告費"].sum()
    monthly_avg["現在比率"] = monthly_avg["月平均広告費"] / monthly_total

    ch_roas_map = perf.set_index("チャネル")["ROAS"].astype(float).to_dict()
    monthly_avg["ROAS"] = monthly_avg["チャネル"].map(ch_roas_map)
    roas_total = monthly_avg["ROAS"].sum()
    monthly_avg["最適比率"] = monthly_avg["ROAS"] / roas_total

    monthly_avg["現在予算"] = (monthly_avg["現在比率"] * total_budget).astype(int)
    monthly_avg["提案予算_制約なし"] = (monthly_avg["最適比率"] * total_budget).astype(int)
    monthly_avg["期待売上_制約なし"] = (monthly_avg["提案予算_制約なし"] * monthly_avg["ROAS"]).astype(int)

    st.markdown("#### チャネル別 予算上下限制約")
    st.caption("各チャネルの最低予算・最大予算を設定してください。制約付きで残り予算をROAS比例配分します。")

    budget_constraints = {}
    constraint_cols = st.columns(min(len(monthly_avg), 3))
    for idx, (_, row) in enumerate(monthly_avg.iterrows()):
        ch_name = row["チャネル"]
        col = constraint_cols[idx % len(constraint_cols)]
        with col:
            st.markdown(f"**{ch_name}** (ROAS: {row['ROAS']:.2f}x)")
            ch_min = st.number_input(
                f"最低予算", min_value=0, max_value=total_budget,
                value=0, step=10000, format="%d",
                key=f"min_{ch_name}"
            )
            ch_max = st.number_input(
                f"最大予算", min_value=0, max_value=total_budget,
                value=total_budget, step=10000, format="%d",
                key=f"max_{ch_name}"
            )
            budget_constraints[ch_name] = {"min": ch_min, "max": ch_max}

    def calc_constrained_allocation(monthly_avg_df, total_bgt, constraints):
        result = monthly_avg_df[["チャネル", "ROAS"]].copy()
        result["配分"] = result["チャネル"].map(lambda ch: constraints[ch]["min"])
        remaining = total_bgt - result["配分"].sum()
        if remaining < 0:
            ratio = total_bgt / result["配分"].sum() if result["配分"].sum() > 0 else 1
            result["配分"] = (result["配分"] * ratio).astype(int)
            remaining = 0

        unfixed = result["チャネル"].tolist()
        for _ in range(10):
            if remaining <= 0 or len(unfixed) == 0:
                break
            roas_sum = result.loc[result["チャネル"].isin(unfixed), "ROAS"].sum()
            if roas_sum == 0:
                break
            new_unfixed = []
            allocated_this_round = 0
            for i, row in result.iterrows():
                if row["チャネル"] not in unfixed:
                    continue
                share = int(remaining * row["ROAS"] / roas_sum)
                proposed = row["配分"] + share
                cap = constraints[row["チャネル"]]["max"]
                if proposed > cap:
                    allocated_this_round += (cap - row["配分"])
                    result.at[i, "配分"] = cap
                else:
                    allocated_this_round += share
                    result.at[i, "配分"] = proposed
                    new_unfixed.append(row["チャネル"])
            remaining -= allocated_this_round
            unfixed = new_unfixed

        result["期待売上"] = (result["配分"] * result["ROAS"]).astype(int)
        return result

    constrained = calc_constrained_allocation(monthly_avg, total_budget, budget_constraints)
    monthly_avg["提案予算"] = constrained["配分"].values
    monthly_avg["差分"] = monthly_avg["提案予算"] - monthly_avg["現在予算"]
    monthly_avg["期待売上"] = constrained["期待売上"].values

    _sim_current = (monthly_avg["現在予算"] * monthly_avg["ROAS"]).sum()
    _sim_proposed = (constrained["配分"] * constrained["ROAS"]).sum()
    _sim_diff = _sim_proposed - _sim_current
    _sim_pct = (_sim_diff / _sim_current * 100) if _sim_current > 0 else 0
    if _sim_diff > 0:
        st.success(f"💰 最適配分で月+¥{_sim_diff:,.0f}の期待売上増（現在比+{_sim_pct:.1f}%）")
    elif _sim_diff < 0:
        st.warning(f"⚠️ 制約付き配分では月¥{abs(_sim_diff):,.0f}の期待売上減（現在比{_sim_pct:.1f}%）")
    else:
        st.info("📊 最適配分と現在配分の期待売上は同等です")

    col_pie1, col_pie2 = st.columns(2)
    with col_pie1:
        st.markdown("#### 現在の配分")
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(monthly_avg["現在比率"], labels=monthly_avg["チャネル"],
                autopct="%1.1f%%", startangle=90,
                colors=["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"])
        ax1.set_title("現在の予算配分")
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    with col_pie2:
        st.markdown("#### ROAS加重 最適配分（制約付き提案）")
        proposed_ratios = monthly_avg["提案予算"] / monthly_avg["提案予算"].sum() if monthly_avg["提案予算"].sum() > 0 else monthly_avg["最適比率"]
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(proposed_ratios, labels=monthly_avg["チャネル"],
                autopct="%1.1f%%", startangle=90,
                colors=["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"])
        ax2.set_title("ROAS加重 最適配分（制約付き）")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    st.markdown("#### 最適配分の詳細（制約付き）")
    display_alloc = monthly_avg[["チャネル", "現在予算", "提案予算", "差分", "期待売上", "ROAS"]].copy()
    display_alloc = display_alloc.sort_values("期待売上", ascending=False).reset_index(drop=True)
    display_fmt = display_alloc.copy()
    display_fmt["現在予算"] = display_fmt["現在予算"].apply(lambda x: f"¥{x:,.0f}")
    display_fmt["提案予算"] = display_fmt["提案予算"].apply(lambda x: f"¥{x:,.0f}")
    display_fmt["差分"] = display_fmt["差分"].apply(lambda x: f"+¥{x:,.0f}" if x >= 0 else f"-¥{abs(x):,.0f}")
    display_fmt["期待売上"] = display_fmt["期待売上"].apply(lambda x: f"¥{x:,.0f}")
    display_fmt["ROAS"] = display_fmt["ROAS"].apply(lambda x: f"{x:.2f}x")
    st.dataframe(display_fmt, use_container_width=True, hide_index=True)

    csv_alloc = monthly_avg[["チャネル", "現在予算", "提案予算", "差分", "期待売上", "ROAS"]].to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 予算配分データをCSVダウンロード", csv_alloc, "budget_allocation.csv", "text/csv")

    st.markdown("#### 期待売上比較")
    current_expected = (monthly_avg["現在予算"] * monthly_avg["ROAS"]).sum()
    unconstrained_expected = monthly_avg["期待売上_制約なし"].sum()
    proposed_expected = monthly_avg["期待売上"].sum()
    diff_expected = proposed_expected - current_expected
    diff_pct = (diff_expected / current_expected * 100) if current_expected > 0 else 0

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("現在配分の期待売上", f"¥{current_expected:,.0f}")
    mc2.metric("制約なし最適配分", f"¥{unconstrained_expected:,.0f}")
    mc3.metric("制約付き最適配分", f"¥{proposed_expected:,.0f}")
    diff_uc = proposed_expected - unconstrained_expected
    mc4.metric("制約による影響", f"¥{diff_uc:,.0f}", f"現在比 {diff_pct:+.1f}%")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("### 🔄 予算移動シミュレーター")
    st.info("💡 「Google広告から¥50万をMeta広告に移したらROASはどう変わる？」をリアルタイムで試算します。")

    sim_channels = monthly_avg["チャネル"].tolist()
    mv_col1, mv_col2 = st.columns(2)
    with mv_col1:
        move_from = st.selectbox("予算移動元チャネル", sim_channels, key="move_from")
    with mv_col2:
        move_to_options = [ch for ch in sim_channels if ch != move_from]
        move_to = st.selectbox("予算移動先チャネル", move_to_options, key="move_to")

    from_budget_row = monthly_avg[monthly_avg["チャネル"] == move_from]
    from_current_budget = int(from_budget_row["現在予算"].values[0]) if len(from_budget_row) > 0 else 0

    move_amount = st.slider(
        "移動額（円）", min_value=0, max_value=max(from_current_budget, 1),
        value=min(100000, max(from_current_budget, 1)), step=10000,
        format="¥%d", key="move_amount"
    )

    move_result_rows = []
    total_before_sales = 0.0
    total_after_sales = 0.0

    for _, row in monthly_avg.iterrows():
        ch = row["チャネル"]
        current_bgt = int(row["現在予算"])
        roas_val = float(row["ROAS"])
        if ch == move_from:
            after_bgt = current_bgt - move_amount
        elif ch == move_to:
            after_bgt = current_bgt + move_amount
        else:
            after_bgt = current_bgt
        current_sales = current_bgt * roas_val
        after_sales = after_bgt * roas_val
        diff_sales = after_sales - current_sales
        total_before_sales += current_sales
        total_after_sales += after_sales
        move_result_rows.append({
            "チャネル": ch, "現在予算": current_bgt, "移動後予算": after_bgt,
            "現在期待売上": int(current_sales), "移動後期待売上": int(after_sales), "差分": int(diff_sales),
        })

    move_result_df = pd.DataFrame(move_result_rows)
    total_effect = total_after_sales - total_before_sales
    total_effect_man = total_effect / 10000
    effect_sign = "+" if total_effect >= 0 else ""
    st.metric(label="💰 移動効果（月間期待売上変動）", value=f"¥{total_effect:+,.0f}",
              delta=f"{effect_sign}{total_effect_man:.1f}万円/月")

    threshold = total_before_sales * 0.005
    if total_effect > threshold:
        st.success(f"この予算移動で月+¥{int(total_effect):,}（+{total_effect_man:.1f}万円）の売上増が期待できます")
    elif total_effect < -threshold:
        st.warning(f"この移動は売上減（月¥{int(abs(total_effect)):,} / {total_effect_man:.1f}万円）につながります。現状維持を推奨")
    else:
        st.info("売上への影響は軽微です（±0.5%以内）")

    st.markdown("#### Before / After 比較")
    display_move = move_result_df.copy()
    display_move["現在予算"] = display_move["現在予算"].apply(lambda x: f"¥{x:,.0f}")
    display_move["移動後予算"] = display_move["移動後予算"].apply(lambda x: f"¥{x:,.0f}")
    display_move["現在期待売上"] = display_move["現在期待売上"].apply(lambda x: f"¥{x:,.0f}")
    display_move["移動後期待売上"] = display_move["移動後期待売上"].apply(lambda x: f"¥{x:,.0f}")
    display_move["差分"] = display_move["差分"].apply(lambda x: f"+¥{x:,.0f}" if x >= 0 else f"-¥{abs(x):,.0f}")
    st.dataframe(display_move, use_container_width=True, hide_index=True)

    st.markdown("#### 💡 ワンクリック最適提案")
    st.caption("全チャネルペアの移動パターン（現在予算の10%刻み）を試算し、最も効果的な移動を自動提案します。")

    best_effect = 0.0
    best_from = None
    best_to = None
    best_amount = 0

    for i, from_row in monthly_avg.iterrows():
        from_ch = from_row["チャネル"]
        from_bgt = int(from_row["現在予算"])
        from_roas = float(from_row["ROAS"])
        if from_bgt <= 0:
            continue
        for j, to_row in monthly_avg.iterrows():
            to_ch = to_row["チャネル"]
            if from_ch == to_ch:
                continue
            to_roas = float(to_row["ROAS"])
            roas_diff = to_roas - from_roas
            for pct in range(10, 110, 10):
                trial_amount = int(from_bgt * pct / 100)
                if trial_amount > from_bgt:
                    trial_amount = from_bgt
                effect = trial_amount * roas_diff
                if effect > best_effect:
                    best_effect = effect
                    best_from = from_ch
                    best_to = to_ch
                    best_amount = trial_amount

    if best_from and best_to and best_effect > 0:
        best_amount_man = best_amount / 10000
        best_effect_man = best_effect / 10000
        st.success(
            f"💡 最適提案: **{best_from}** → **{best_to}** に ¥{best_amount:,}（{best_amount_man:.0f}万円）移動で "
            f"月 **+¥{int(best_effect):,}（+{best_effect_man:.1f}万円）** の改善が期待できます"
        )
    else:
        st.info("現在のROAS構成では、予算移動による有意な改善余地はありません")
    st.caption("※ ROASは過去実績の平均値を使用。季節変動・予算規模による収穫逓減は考慮外です。")

# ------------------------------------------------------------------
# タブ3: トレンド分析
# ------------------------------------------------------------------
with tab3:
    st.markdown("### トレンド分析")

    channels = df["チャネル"].unique()
    sorted_months = sorted(df["月"].unique())

    st.markdown("#### チャネル別 月次ROAS推移")
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    color_map = {"Google広告": "#059669", "Meta広告": "#3B82F6", "楽天広告": "#F59E0B",
                 "LINE広告": "#8B5CF6", "TikTok広告": "#EF4444"}
    for ch in channels:
        ch_data = df[df["チャネル"] == ch].sort_values("月")
        ax3.plot(ch_data["月"], ch_data["ROAS"], marker="o", linewidth=2,
                 label=ch, color=color_map.get(ch, None))
    ax3.axhline(y=1.0, color="#EF4444", linestyle="--", linewidth=1, alpha=0.5, label="損益分岐")
    ax3.set_ylabel("ROAS")
    ax3.set_title("チャネル別 月次ROAS推移")
    ax3.legend(loc="upper left", fontsize=9)
    ax3.tick_params(axis="x", rotation=45)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.markdown("#### チャネル別 月次広告費推移（積み上げ）")
    pivot_cost = df.pivot_table(index="月", columns="チャネル", values="広告費", aggfunc="sum").fillna(0)
    pivot_cost = pivot_cost.reindex(sorted_months)

    fig4, ax4 = plt.subplots(figsize=(12, 5))
    bottom = np.zeros(len(pivot_cost))
    for ch in channels:
        if ch in pivot_cost.columns:
            values = pivot_cost[ch].values
            ax4.bar(range(len(pivot_cost)), values, bottom=bottom,
                    label=ch, color=color_map.get(ch, None))
            bottom += values
    ax4.set_xticks(range(len(pivot_cost)))
    ax4.set_xticklabels(pivot_cost.index, rotation=45, ha="right")
    ax4.set_ylabel("広告費（円）")
    ax4.set_title("チャネル別 月次広告費推移（積み上げ）")
    ax4.legend(loc="upper left", fontsize=9)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    st.markdown("#### ROAS トレンドサマリー")
    st.caption("直近3ヶ月平均 vs 前半6ヶ月平均の比較")

    trend_records = []
    for ch in channels:
        ch_data = df[df["チャネル"] == ch].sort_values("月")
        roas_values = ch_data["ROAS"].values
        n = len(roas_values)
        if n >= 9:
            first_half = roas_values[:6].mean()
            last_three = roas_values[-3:].mean()
        elif n >= 3:
            split = max(1, n - 3)
            first_half = roas_values[:split].mean()
            last_three = roas_values[-3:].mean()
        else:
            first_half = roas_values.mean()
            last_three = roas_values.mean()

        change = last_three - first_half
        change_pct = (change / first_half * 100) if first_half > 0 else 0
        status = "📈 改善" if change > 0 else "📉 悪化" if change < 0 else "➡️ 横ばい"
        trend_records.append({
            "チャネル": ch,
            "前半6ヶ月平均ROAS": round(first_half, 2),
            "直近3ヶ月平均ROAS": round(last_three, 2),
            "変化": f"{change:+.2f}",
            "変化率": f"{change_pct:+.1f}%",
            "トレンド": status,
        })

    trend_df = pd.DataFrame(trend_records)
    st.dataframe(trend_df, use_container_width=True, hide_index=True)

# === 定期運用チェックリスト ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 📋 定期運用チェックリスト")

with st.expander("週次チェック", expanded=False):
    st.markdown(
        "- □ 各チャネルのCPA/ROASを確認\n"
        "- □ 減額推奨チャネルの対応を検討\n"
        "- □ 予算配分シミュレーションを実行"
    )

with st.expander("月次チェック", expanded=False):
    st.markdown(
        "- □ ROAS月次トレンドを確認\n"
        "- □ 予算上下限の見直し\n"
        "- □ 目標CPAの達成率を検証\n"
        "- □ RFM分析で獲得顧客の質を確認"
    )

# === 関連ツールカード ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")

_tool_cards_css = """
<style>
.tool-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.tool-card a {
    color: #059669;
    font-size: 1.1rem;
    font-weight: 700;
    text-decoration: none;
}
.tool-card a:hover { text-decoration: underline; }
.tool-card .tool-desc {
    color: #6B7280;
    font-size: 0.85rem;
    margin-top: 0.4rem;
}
</style>
"""
st.markdown(_tool_cards_css, unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3)
fc1.markdown(
    '<div class="tool-card">'
    '<a href="https://ec-rfm-analysis.streamlit.app" target="_blank">👥 顧客RFM分析</a>'
    '<div class="tool-desc">広告で獲得した顧客のセグメント分布を確認する</div>'
    '</div>',
    unsafe_allow_html=True,
)
fc2.markdown(
    '<div class="tool-card">'
    '<a href="https://ec-sales-dashboard.streamlit.app" target="_blank">📈 売上ダッシュボード</a>'
    '<div class="tool-desc">広告施策が売上に与えた影響を確認する</div>'
    '</div>',
    unsafe_allow_html=True,
)
fc3.markdown(
    '<div class="tool-card">'
    '<a href="https://km-ec-apps.streamlit.app" target="_blank">🛒 ECポータル</a>'
    '<div class="tool-desc">全ツール一覧に戻る</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.caption("AI経営パートナー × データサイエンス | 広告ROI分析 v2.0 — ML予測+SHAP対応")

# ------------------------------------------------------------------
# タブ4: ML予測 + SHAP分析
# ------------------------------------------------------------------
with tab4:
    st.markdown("### 🤖 広告ROAS予測 + SHAP要因分析")
    st.info("LightGBMでチャネル別ROASを予測し、SHAPで要因分解します。どの変数がROASに最も影響するかを可視化。")

    if st.session_state.df is not None:
        df_ml = st.session_state.df.copy()

        le_ch = LabelEncoder()
        df_ml["チャネル_enc"] = le_ch.fit_transform(df_ml["チャネル"])

        feature_cols = ["チャネル_enc", "広告費", "インプレッション数", "クリック数", "CV数"]
        feature_display = ["チャネル", "広告費", "インプレッション数", "クリック数", "CV数"]
        target_col = "ROAS"

        X = df_ml[feature_cols].copy()
        y = df_ml[target_col].copy()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = lgb.LGBMRegressor(
            n_estimators=300, learning_rate=0.05, num_leaves=31,
            random_state=42, verbose=-1
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        r2 = r2_score(y_test, pred)
        mae = mean_absolute_error(y_test, pred)

        st.markdown("#### モデル精度")
        m1, m2 = st.columns(2)
        m1.metric("R²スコア", f"{r2:.3f}")
        m2.metric("MAE", f"{mae:,.0f}")

        if r2 < 0.3:
            st.warning(f"R²={r2:.2f} — モデル精度が低いため、予測値は参考値として扱ってください。")

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("#### SHAP要因分析")
        explainer = shap.TreeExplainer(model)
        sample_size = min(200, len(X_test))
        X_shap = X_test.iloc[:sample_size].copy()
        sv = explainer.shap_values(X_shap)

        X_shap_display = X_shap.copy()
        X_shap_display.columns = feature_display

        fig_shap, ax_shap = plt.subplots(figsize=(10, 5))
        shap.summary_plot(sv, X_shap_display, plot_type="bar", show=False)
        plt.title("SHAP特徴量重要度（ROASへの影響度）", fontsize=14)
        plt.tight_layout()
        st.pyplot(fig_shap)
        plt.close(fig_shap)

        fig_bee, ax_bee = plt.subplots(figsize=(10, 5))
        shap.summary_plot(sv, X_shap_display, show=False)
        plt.title("SHAP Beeswarm（各特徴量の影響方向）", fontsize=14)
        plt.tight_layout()
        st.pyplot(fig_bee)
        plt.close(fig_bee)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("#### チャネル別ROAS予測")
        channels_ml = sorted(df_ml["チャネル"].unique())
        channel_preds = []
        for ch in channels_ml:
            ch_enc = le_ch.transform([ch])[0]
            ch_data = df_ml[df_ml["チャネル"] == ch]
            avg_row = pd.DataFrame({
                "チャネル_enc": [ch_enc],
                "広告費": [ch_data["広告費"].mean()],
                "インプレッション数": [ch_data["インプレッション数"].mean()],
                "クリック数": [ch_data["クリック数"].mean()],
                "CV数": [ch_data["CV数"].mean()],
            })
            pred_roas = model.predict(avg_row)[0]
            actual_roas = ch_data["ROAS"].mean()
            channel_preds.append({
                "チャネル": ch,
                "実績ROAS（平均）": round(actual_roas, 2),
                "予測ROAS": round(pred_roas, 2),
                "差分": round(pred_roas - actual_roas, 2),
            })

        pred_df = pd.DataFrame(channel_preds)
        st.dataframe(pred_df, use_container_width=True, hide_index=True)

    else:
        st.warning("データが読み込まれていません。サイドバーからCSVを読み込んでください。")
