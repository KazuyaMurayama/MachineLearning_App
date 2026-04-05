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
    font-size: 1.6rem;
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
    <div class="hero-subtitle">チャネル別ROAS分析・予算配分最適化・トレンド分析でデータドリブンな広告戦略を実現</div>
</div>
""", unsafe_allow_html=True)

# === データチェック ===
df = st.session_state.df
if df is None:
    st.warning("データが読み込まれていません。サイドバーからCSVをアップロードしてください。")
    st.stop()

# === 導入効果 ===
st.info("💡 **導入効果**: 広告費の無駄を可視化し、ROAS 20%改善（月¥50万の広告費削減）")

# === KPIカード ===
total_cost = df["広告費"].sum()
total_revenue = df["売上"].sum()
overall_roas = total_revenue / total_cost if total_cost > 0 else 0
ch_roas = df.groupby("チャネル").agg({"広告費": "sum", "売上": "sum"}).reset_index()
ch_roas["ROAS"] = ch_roas["売上"] / ch_roas["広告費"]
best_ch = ch_roas.loc[ch_roas["ROAS"].idxmax()]

k1, k2, k3, k4, k5 = st.columns(5)

# 減額推奨チャネルを事前計算（投資判定ロジック活用）
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

# 冒頭アラート: 最も危険なチャネル or 全チャネル黒字
if _danger_channels:
    worst = max(_danger_channels, key=lambda x: abs(x["loss"]))
    st.warning(f"⚡ {worst['name']} ROAS {worst['roas']:.1f}x — 月¥{abs(worst['loss']):,}の赤字。減額を推奨します")
else:
    st.success("✅ 全チャネル黒字。現状維持で問題ありません")

st.markdown("<br>", unsafe_allow_html=True)

# === トレンド判定ユーティリティ（Tab1・Tab2で共用） ===
def compute_channel_trend(df, channel):
    """チャネルのROASトレンドを判定する。改善/安定/悪化を返す。"""
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
    """ROAS値とトレンドから投資判定ラベルと理由を返す。"""
    if roas >= 2.0 and trend == "改善":
        return "🟢 増額推奨", f"ROAS {roas:.2f}x（≥2.0）& トレンド改善"
    elif roas >= 1.5 and trend in ("安定", "改善"):
        return "🔵 維持", f"ROAS {roas:.2f}x（≥1.5）& トレンド{trend}"
    elif roas < 1.0:
        return "🔴 減額推奨", f"ROAS {roas:.2f}x（<1.0）— 赤字チャネル"
    else:
        return "🟡 要注意", f"ROAS {roas:.2f}x / トレンド{trend} — 改善検討"

# === タブ ===
tab1, tab2, tab3 = st.tabs(["📊 チャネル別ROAS", "💰 予算配分シミュレーション", "📈 トレンド分析"])

# ------------------------------------------------------------------
# タブ1: チャネル別ROAS
# ------------------------------------------------------------------
with tab1:
    st.markdown("### チャネル別ROAS（年間平均）")

    # パフォーマンステーブル作成
    perf = df.groupby("チャネル").agg(
        広告費合計=("広告費", "sum"),
        売上合計=("売上", "sum"),
        CV数=("CV数", "sum"),
    ).reset_index()
    perf["ROAS"] = (perf["売上合計"] / perf["広告費合計"]).round(2)
    perf["CPA"] = (perf["広告費合計"] / perf["CV数"]).astype(int)
    perf = perf.sort_values("ROAS", ascending=False).reset_index(drop=True)

    # チャネルフィルター
    all_channels = perf["チャネル"].tolist()
    selected_channels = st.multiselect("チャネルを絞込", all_channels, default=all_channels)
    perf_filtered = perf[perf["チャネル"].isin(selected_channels)]

    # 棒グラフ
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

    # 投資判定・CPA目標達成を計算
    perf_filtered = perf_filtered.copy()
    perf_filtered["トレンド"] = perf_filtered["チャネル"].apply(lambda ch: compute_channel_trend(df, ch))
    perf_filtered["投資判定"] = perf_filtered.apply(
        lambda r: investment_judgment(float(r["ROAS"]), r["トレンド"])[0], axis=1)
    perf_filtered["判定理由"] = perf_filtered.apply(
        lambda r: investment_judgment(float(r["ROAS"]), r["トレンド"])[1], axis=1)
    perf_filtered["目標CPA達成"] = perf_filtered["CPA"].apply(
        lambda x: "✅ 達成" if x <= target_cpa else "❌ 未達成")

    # テーブル（上位ハイライト）
    st.markdown("### チャネル別パフォーマンス")
    display_perf = perf_filtered.copy()
    display_perf["広告費合計"] = display_perf["広告費合計"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["売上合計"] = display_perf["売上合計"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["CV数"] = display_perf["CV数"].apply(lambda x: f"{x:,}")
    display_perf["CPA_raw"] = display_perf["CPA"]
    display_perf["CPA"] = display_perf["CPA"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["ROAS"] = display_perf["ROAS"].apply(lambda x: f"{x:.2f}x")

    # ハイライト: ROAS上位をマーク
    display_perf.insert(0, "🏆", ["⭐" if i < 2 else "" for i in range(len(display_perf))])

    display_cols = ["🏆", "チャネル", "広告費合計", "売上合計", "CV数", "ROAS", "CPA",
                    "投資判定", "判定理由", "目標CPA達成"]
    st.dataframe(display_perf[display_cols], use_container_width=True, hide_index=True)

    # 目標CPA未達成チャネルの改善試算
    missed = perf_filtered[perf_filtered["CPA"] > target_cpa].copy()
    if len(missed) > 0:
        st.markdown("#### 🎯 目標CPA未達成チャネルの改善試算")
        st.caption(f"目標CPA: ¥{target_cpa:,}")
        for _, row in missed.iterrows():
            current_cpa = int(row["CPA"])
            gap = current_cpa - target_cpa
            # 必要CVR改善: CPA = 広告費/CV数, CV数 = クリック数*CVR
            # 目標CV数 = 広告費合計 / 目標CPA
            cost = row["広告費合計"]
            current_cv = int(row["CV数"].replace(",", "")) if isinstance(row["CV数"], str) else int(row["CV数"])
            target_cv = cost / target_cpa
            if current_cv > 0:
                current_cvr_approx = current_cv / cost * target_cpa  # ratio
                needed_cv_increase = target_cv - current_cv
                needed_cv_increase_pct = (needed_cv_increase / current_cv * 100) if current_cv > 0 else 0
                st.info(
                    f"**{row['チャネル']}**: CPAを ¥{gap:,} 削減が必要 → "
                    f"CV数を現在の{current_cv}件から{int(target_cv)}件へ "
                    f"(+{needed_cv_increase_pct:.1f}% 改善が必要)"
                )

    # CSVダウンロード
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

    # 現在の配分比率
    monthly_avg = df.groupby("チャネル")["広告費"].mean().reset_index()
    monthly_avg.columns = ["チャネル", "月平均広告費"]
    monthly_total = monthly_avg["月平均広告費"].sum()
    monthly_avg["現在比率"] = monthly_avg["月平均広告費"] / monthly_total

    # ROAS加重最適配分（制約なし）
    ch_roas_map = perf.set_index("チャネル")["ROAS"].astype(float).to_dict()
    monthly_avg["ROAS"] = monthly_avg["チャネル"].map(ch_roas_map)
    roas_total = monthly_avg["ROAS"].sum()
    monthly_avg["最適比率"] = monthly_avg["ROAS"] / roas_total

    monthly_avg["現在予算"] = (monthly_avg["現在比率"] * total_budget).astype(int)
    monthly_avg["提案予算_制約なし"] = (monthly_avg["最適比率"] * total_budget).astype(int)
    monthly_avg["期待売上_制約なし"] = (monthly_avg["提案予算_制約なし"] * monthly_avg["ROAS"]).astype(int)

    # --- チャネル別予算制約 ---
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

    # 制約付き配分計算
    def calc_constrained_allocation(monthly_avg_df, total_bgt, constraints):
        """最低予算を確保した上で、残りをROAS比例配分（最大予算でキャップ）"""
        result = monthly_avg_df[["チャネル", "ROAS"]].copy()
        # まず最低予算を確保
        result["配分"] = result["チャネル"].map(lambda ch: constraints[ch]["min"])
        remaining = total_bgt - result["配分"].sum()
        if remaining < 0:
            # 最低予算の合計が総予算を超える場合は比例で縮小
            ratio = total_bgt / result["配分"].sum() if result["配分"].sum() > 0 else 1
            result["配分"] = (result["配分"] * ratio).astype(int)
            remaining = 0

        # 残りをROAS比例で配分（キャップ考慮で反復）
        unfixed = result["チャネル"].tolist()
        for _ in range(10):  # 最大10回反復で収束
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

    # シミュレーション結論ハイライト
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
        wedges, texts, autotexts = ax1.pie(
            monthly_avg["現在比率"], labels=monthly_avg["チャネル"],
            autopct="%1.1f%%", startangle=90,
            colors=["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"]
        )
        ax1.set_title("現在の予算配分")
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

    with col_pie2:
        st.markdown("#### ROAS加重 最適配分（制約付き提案）")
        proposed_ratios = monthly_avg["提案予算"] / monthly_avg["提案予算"].sum() if monthly_avg["提案予算"].sum() > 0 else monthly_avg["最適比率"]
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        wedges2, texts2, autotexts2 = ax2.pie(
            proposed_ratios, labels=monthly_avg["チャネル"],
            autopct="%1.1f%%", startangle=90,
            colors=["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"]
        )
        ax2.set_title("ROAS加重 最適配分（制約付き）")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # 結果テーブル
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

    # 現在 vs 制約なし vs 制約付き の期待売上比較
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
    mc4.metric("制約による影響", f"¥{diff_uc:,.0f}",
               f"現在比 {diff_pct:+.1f}%")

# ------------------------------------------------------------------
# タブ3: トレンド分析
# ------------------------------------------------------------------
with tab3:
    st.markdown("### トレンド分析")

    channels = df["チャネル"].unique()
    sorted_months = sorted(df["月"].unique())

    # 月次ROAS推移（折れ線）
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

    # 月次広告費推移（積み上げ棒グラフ）
    st.markdown("#### チャネル別 月次広告費推移（積み上げ）")
    pivot_cost = df.pivot_table(index="月", columns="チャネル", values="広告費", aggfunc="sum").fillna(0)
    # 月の順序を保証（文字列ソート: "2024年01月" < "2024年02月" ... で正しく動作）
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

    # ROAS改善/悪化トレンドサマリー
    st.markdown("#### ROAS トレンドサマリー")
    st.caption("直近3ヶ月平均 vs 前半6ヶ月平均の比較")

    month_list = list(sorted_months)
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
    '<a href="https://ec-ai-tools.streamlit.app" target="_blank">🛒 ECポータル</a>'
    '<div class="tool-desc">全ツール一覧に戻る</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.caption("AI経営パートナー × データサイエンス | 広告ROI分析 v1.0")
