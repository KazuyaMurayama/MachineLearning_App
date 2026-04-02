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

k1, k2, k3, k4 = st.columns(4)
for col, label, value in [
    (k1, "年間広告費合計", f"¥{total_cost:,.0f}"),
    (k2, "年間売上合計（広告経由）", f"¥{total_revenue:,.0f}"),
    (k3, "全体ROAS", f"{overall_roas:.2f}x"),
    (k4, f"最優秀: {best_ch['チャネル']}", f"ROAS {best_ch['ROAS']:.2f}x"),
]:
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

    # テーブル（上位ハイライト）
    st.markdown("### チャネル別パフォーマンス")
    display_perf = perf_filtered.copy()
    display_perf["広告費合計"] = display_perf["広告費合計"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["売上合計"] = display_perf["売上合計"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["CV数"] = display_perf["CV数"].apply(lambda x: f"{x:,}")
    display_perf["CPA"] = display_perf["CPA"].apply(lambda x: f"¥{x:,.0f}")
    display_perf["ROAS"] = display_perf["ROAS"].apply(lambda x: f"{x:.2f}x")

    # ハイライト: ROAS上位をマーク
    display_perf.insert(0, "🏆", ["⭐" if i < 2 else "" for i in range(len(display_perf))])

    st.dataframe(display_perf, use_container_width=True, hide_index=True)

    # CSVダウンロード
    csv_data = perf_filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 パフォーマンスデータをCSVダウンロード", csv_data,
                       "channel_performance.csv", "text/csv")

# ------------------------------------------------------------------
# タブ2: 予算配分シミュレーション
# ------------------------------------------------------------------
with tab2:
    st.markdown("### 予算配分シミュレーション")
    st.info("💡 **最適化ロジック**: 各チャネルのROAS（広告費用対効果）に比例して予算を配分します。ROASが高いチャネルに多く投資することで、同じ予算でより多くの売上が期待できます。")

    total_budget = st.number_input(
        "月間総予算（円）", min_value=100000, max_value=100000000,
        value=1000000, step=100000, format="%d"
    )

    # 現在の配分比率
    monthly_avg = df.groupby("チャネル")["広告費"].mean().reset_index()
    monthly_avg.columns = ["チャネル", "月平均広告費"]
    monthly_total = monthly_avg["月平均広告費"].sum()
    monthly_avg["現在比率"] = monthly_avg["月平均広告費"] / monthly_total

    # ROAS加重最適配分
    ch_roas_map = perf.set_index("チャネル")["ROAS"].astype(float).to_dict()
    monthly_avg["ROAS"] = monthly_avg["チャネル"].map(ch_roas_map)
    roas_total = monthly_avg["ROAS"].sum()
    monthly_avg["最適比率"] = monthly_avg["ROAS"] / roas_total

    monthly_avg["現在予算"] = (monthly_avg["現在比率"] * total_budget).astype(int)
    monthly_avg["提案予算"] = (monthly_avg["最適比率"] * total_budget).astype(int)
    monthly_avg["差分"] = monthly_avg["提案予算"] - monthly_avg["現在予算"]
    monthly_avg["期待売上"] = (monthly_avg["提案予算"] * monthly_avg["ROAS"]).astype(int)

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
        st.markdown("#### ROAS加重 最適配分（提案）")
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        wedges2, texts2, autotexts2 = ax2.pie(
            monthly_avg["最適比率"], labels=monthly_avg["チャネル"],
            autopct="%1.1f%%", startangle=90,
            colors=["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"]
        )
        ax2.set_title("ROAS加重 最適配分")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # 結果テーブル
    st.markdown("#### 最適配分の詳細")
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

    # 現在 vs 提案 の期待売上比較
    st.markdown("#### 期待売上比較")
    current_expected = (monthly_avg["現在予算"] * monthly_avg["ROAS"]).sum()
    proposed_expected = monthly_avg["期待売上"].sum()
    diff_expected = proposed_expected - current_expected
    diff_pct = (diff_expected / current_expected * 100) if current_expected > 0 else 0

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("現在配分の期待売上", f"¥{current_expected:,.0f}")
    mc2.metric("最適配分の期待売上", f"¥{proposed_expected:,.0f}")
    mc3.metric("改善額", f"¥{diff_expected:,.0f}", f"{diff_pct:+.1f}%")

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

# === 相互リンクフッター ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1, fc2, fc3 = st.columns(3)
fc1.markdown("👥 [顧客RFM分析](https://ec-rfm.streamlit.app)  \n顧客セグメントを自動分類")
fc2.markdown("📊 [売上ダッシュボード](https://ec-dashboard.streamlit.app)  \n日別/月別売上を自動可視化")
fc3.markdown("🛒 [EC離脱予測](https://ec-demo.streamlit.app)  \n顧客離脱をAIで予測")
st.caption("AI経営パートナー × データサイエンス | 広告ROI分析 v1.0")
