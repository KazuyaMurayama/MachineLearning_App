import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from datetime import datetime, timedelta
import io

# ── 日本語フォント設定 ──
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

font_name = setup_japanese_font()

# ── ページ設定 ──
st.set_page_config(page_title="顧客RFM分析", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# ── CSS ──
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(180deg, #F5F3FF, #FFFFFF);
    padding: 2rem 2rem 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.hero-title {
    color: #8B5CF6;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.hero-sub {
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
    color: #8B5CF6;
}
.kpi-label {
    font-size: 0.85rem;
    color: #6B7280;
    margin-top: 0.2rem;
}
hr.section-divider {
    border: none;
    border-top: 2px solid #E5E7EB;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ──
for k, v in {"df": None, "loaded": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── サイドバー ──
with st.sidebar:
    st.markdown("## 🎯 顧客RFM分析")
    st.markdown("---")
    uploaded = st.file_uploader("📂 CSVアップロード", type=["csv"])
    st.info("**必須カラム**: 顧客ID / 注文日 / 注文金額")
    if uploaded is not None:
        try:
            df_up = pd.read_csv(uploaded)
            required = {"顧客ID", "注文日", "注文金額"}
            if required.issubset(set(df_up.columns)):
                df_up["注文日"] = pd.to_datetime(df_up["注文日"])
                st.session_state.df = df_up
                st.session_state.loaded = True
                st.success("✅ データを読み込みました")
            else:
                st.error(f"必須カラムが不足: {required - set(df_up.columns)}")
        except Exception as e:
            st.error(f"読み込みエラー: {e}")
    st.markdown("---")
    st.caption("AI経営パートナー × データサイエンス")
    st.markdown("---")
    st.markdown("## 🔄 遷移分析 期間設定")
    _p_tmp = os.path.join(os.path.dirname(__file__), "sample_data", "purchase_history.csv")
    if os.path.exists(_p_tmp):
        _df_tmp = pd.read_csv(_p_tmp)
        _df_tmp["注文日"] = pd.to_datetime(_df_tmp["注文日"])
        _date_min = _df_tmp["注文日"].min().date()
        _date_max = _df_tmp["注文日"].max().date()
    else:
        import datetime as _dt
        _date_min = _dt.date(2022, 1, 1)
        _date_max = _dt.date.today()
    _date_mid_default = _date_min + (_date_max - _date_min) // 2
    split_date = st.date_input(
        "分析期間の分割点",
        value=_date_mid_default,
        min_value=_date_min,
        max_value=_date_max,
        key="split_date",
        help="この日付を境に前半/後半に分けてセグメント遷移を計算します",
    )
    st.markdown("---")
    st.markdown("## 📊 施策シミュレーション設定")
    slider_vip = st.slider("VIP維持率向上 (%)", 1, 30, 10, key="sl_vip") / 100
    st.caption("→ タブ3「施策提案」の期待売上（VIP維持）に反映")
    slider_good = st.slider("優良客単価向上 (%)", 1, 30, 15, key="sl_good") / 100
    st.caption("→ タブ3「施策提案」の期待売上（優良客）に反映")
    slider_normal = st.slider("一般リピート率向上 (%)", 1, 30, 10, key="sl_normal") / 100
    st.caption("→ タブ3「施策提案」の期待売上（一般客）に反映")
    slider_dormant = st.slider("休眠復帰率 (%)", 1, 20, 5, key="sl_dormant") / 100
    st.caption("→ タブ3「施策提案」の期待売上（休眠復帰）に反映")
    slider_churn = st.slider("離脱復帰率 (%)", 1, 20, 3, key="sl_churn") / 100
    st.caption("→ タブ3「施策提案」の期待売上（離脱復帰）に反映")

# ── サンプルデータ自動読み込み ──
if not st.session_state.loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "purchase_history.csv")
    if os.path.exists(p):
        df_sample = pd.read_csv(p)
        df_sample["注文日"] = pd.to_datetime(df_sample["注文日"])
        st.session_state.df = df_sample
        st.session_state.loaded = True

# ── Hero ──
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎯 顧客RFM分析＋セグメンテーション</div>
    <div class="hero-sub">購買データからVIP・休眠・離脱を自動分類。施策の期待売上までAIが試算。</div>
</div>
""", unsafe_allow_html=True)

_c1, _c2, _c3 = st.columns(3)
_c1.markdown('<div class="kpi-card"><div class="kpi-value">4h</div><div class="kpi-label">⏳ Before: 顧客分析に月4時間</div></div>', unsafe_allow_html=True)
_c2.markdown('<div class="kpi-card"><div class="kpi-value">5分</div><div class="kpi-label">⚡ After: 全顧客をセグメント分類</div></div>', unsafe_allow_html=True)
_c3.markdown('<div class="kpi-card"><div class="kpi-value">+¥200万</div><div class="kpi-label">💰 年間効果: LTV最大化で増収</div></div>', unsafe_allow_html=True)

if not st.session_state.loaded or st.session_state.df is None:
    st.warning("サイドバーからCSVをアップロードしてください。")
    st.stop()

df = st.session_state.df.copy()

# ── RFM計算 ──
reference_date = df["注文日"].max()

rfm = df.groupby("顧客ID").agg(
    顧客名=("顧客名", "first") if "顧客名" in df.columns else ("顧客ID", "first"),
    最終購買日=("注文日", "max"),
    購買回数=("注文日", "count"),
    累計金額=("注文金額", "sum"),
).reset_index()

rfm["Recency"] = (reference_date - rfm["最終購買日"]).dt.days


def safe_qcut(series, q, labels_asc=True):
    """pd.qcutで重複値を処理しつつ5段階に分割"""
    try:
        result = pd.qcut(series, q=q, labels=False, duplicates="drop") + 1
        # ラベル数が足りない場合の補正
        max_label = result.max()
        if max_label < q:
            result = ((result - 1) / (max_label - 1) * (q - 1)).round().astype(int) + 1
        return result
    except Exception:
        return pd.Series([3] * len(series), index=series.index)


# Rスコア: 少ないほど高スコア → 逆順
rfm["R"] = safe_qcut(rfm["Recency"], 5)
rfm["R"] = 6 - rfm["R"]  # 反転: Recency小 → スコア高

# Fスコア: 多いほど高スコア
rfm["F"] = safe_qcut(rfm["購買回数"], 5)

# Mスコア: 多いほど高スコア
rfm["M"] = safe_qcut(rfm["累計金額"], 5)

rfm["合計"] = rfm["R"] + rfm["F"] + rfm["M"]


def assign_segment(total):
    if total >= 13:
        return "VIP顧客"
    elif total >= 10:
        return "優良顧客"
    elif total >= 7:
        return "一般顧客"
    elif total >= 4:
        return "休眠顧客"
    else:
        return "離脱顧客"


rfm["セグメント"] = rfm["合計"].apply(assign_segment)

# ── 次回購買予測日の計算 ──
def calc_next_purchase(df, rfm_df, ref_date):
    """顧客ごとの平均購買間隔から次回購買予測日を算出"""
    intervals = []
    for cid, grp in df.groupby("顧客ID"):
        dates = grp["注文日"].sort_values()
        if len(dates) >= 2:
            diffs = dates.diff().dropna().dt.days
            avg_interval = diffs.mean()
        else:
            avg_interval = np.nan
        intervals.append({"顧客ID": cid, "平均購買間隔": avg_interval})
    interval_df = pd.DataFrame(intervals)
    merged = rfm_df.merge(interval_df, on="顧客ID", how="left")
    merged["次回予測日"] = merged.apply(
        lambda r: r["最終購買日"] + timedelta(days=r["平均購買間隔"])
        if pd.notna(r["平均購買間隔"]) else pd.NaT, axis=1
    )
    merged["ステータス"] = merged["次回予測日"].apply(
        lambda d: "要フォロー" if pd.notna(d) and d <= ref_date else
                  ("予測不可" if pd.isna(d) else "正常")
    )
    return merged

rfm = calc_next_purchase(df, rfm, reference_date)

# ── KPIカード ──
vip_count = (rfm["セグメント"] == "VIP顧客").sum()
dormant_count = rfm["セグメント"].isin(["休眠顧客", "離脱顧客"]).sum()
avg_ltv = rfm["累計金額"].mean()
repeat_rate = (rfm["購買回数"] >= 2).sum() / len(rfm) * 100
vip_pct = vip_count / len(rfm) * 100
dormant_pct = dormant_count / len(rfm) * 100

follow_up_count = (rfm["ステータス"] == "要フォロー").sum()
follow_up_avg_ltv = rfm.loc[rfm["ステータス"] == "要フォロー", "累計金額"].mean() if follow_up_count > 0 else 0
follow_up_expected = follow_up_count * follow_up_avg_ltv * slider_dormant

# ── セグメント遷移分析（前半/後半） ──
SEGMENT_ORDER = ["VIP顧客", "優良顧客", "一般顧客", "休眠顧客", "離脱顧客"]
SEGMENT_RANK = {s: i for i, s in enumerate(SEGMENT_ORDER)}

def compute_rfm_for_period(period_df, ref_date):
    """指定期間のDataFrameからRFMセグメントを計算して返す"""
    if period_df.empty:
        return pd.DataFrame(columns=["顧客ID", "セグメント"])
    cols = {"顧客名": ("顧客名", "first")} if "顧客名" in period_df.columns else {}
    agg_dict = {**cols,
                "最終購買日": ("注文日", "max"),
                "購買回数": ("注文日", "count"),
                "累計金額": ("注文金額", "sum")}
    p_rfm = period_df.groupby("顧客ID").agg(**agg_dict).reset_index()
    p_rfm["Recency"] = (ref_date - p_rfm["最終購買日"]).dt.days
    p_rfm["R"] = safe_qcut(p_rfm["Recency"], 5)
    p_rfm["R"] = 6 - p_rfm["R"]
    p_rfm["F"] = safe_qcut(p_rfm["購買回数"], 5)
    p_rfm["M"] = safe_qcut(p_rfm["累計金額"], 5)
    p_rfm["合計"] = p_rfm["R"] + p_rfm["F"] + p_rfm["M"]
    p_rfm["セグメント"] = p_rfm["合計"].apply(assign_segment)
    return p_rfm[["顧客ID", "セグメント"]]

split_dt = pd.Timestamp(split_date)
df_first = df[df["注文日"] < split_dt]
df_second = df[df["注文日"] >= split_dt]

rfm_first = compute_rfm_for_period(df_first, split_dt - pd.Timedelta(days=1))
rfm_second = compute_rfm_for_period(df_second, reference_date)

transition_df = rfm_first.merge(rfm_second, on="顧客ID", suffixes=("_前半", "_後半"))

# セグメント悪化人数（ランクが下がった顧客）
def count_degraded(trans_df):
    if trans_df.empty:
        return 0
    cnt = 0
    for _, row in trans_df.iterrows():
        r_before = SEGMENT_RANK.get(row["セグメント_前半"], 99)
        r_after = SEGMENT_RANK.get(row["セグメント_後半"], 99)
        if r_after > r_before:
            cnt += 1
    return cnt

degraded_count = count_degraded(transition_df)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.markdown(f'<div class="kpi-card"><div class="kpi-value">{vip_count}人</div><div class="kpi-label">VIP顧客数</div><div class="kpi-label">{vip_pct:.0f}% / 全顧客</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi-card"><div class="kpi-value">{dormant_count}人</div><div class="kpi-label">休眠+離脱顧客数</div><div class="kpi-label">{dormant_pct:.0f}% / 要フォロー</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi-card"><div class="kpi-value">¥{avg_ltv:,.0f}</div><div class="kpi-label">全顧客平均LTV</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi-card"><div class="kpi-value">{repeat_rate:.1f}%</div><div class="kpi-label">リピート率</div></div>', unsafe_allow_html=True)
k5.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:#DC2626;">⚠️ {follow_up_count}人</div><div class="kpi-label">要フォロー顧客</div><div class="kpi-label">予測日超過</div></div>', unsafe_allow_html=True)
k6.markdown(f'<div class="kpi-card"><div class="kpi-value" style="color:#DC2626;">📉 {degraded_count}人</div><div class="kpi-label">セグメント悪化</div><div class="kpi-label">前半比ランクダウン</div></div>', unsafe_allow_html=True)

if follow_up_count > 0:
    st.warning(f"⚡ 要フォロー顧客 {follow_up_count}人に今すぐクーポン配信で ¥{follow_up_expected:,.0f} の増収見込み（復帰率 {slider_dormant:.0%} 想定）")

st.markdown("<br>", unsafe_allow_html=True)

# ── タブ ──
tab1, tab2, tab3 = st.tabs(["📋 RFMスコア一覧", "🗺️ セグメントマップ", "💡 施策提案"])

# ── タブ1: RFMスコア一覧 ──
with tab1:
    st.subheader("RFMスコア一覧")

    with st.expander("📖 RFMとは？"):
        st.markdown("""
    | 指標 | 意味 | スコア高 = |
    |------|------|-----------|
    | **R（Recency）** | 最終購買からの経過日数 | 最近買った |
    | **F（Frequency）** | 購買回数 | よく買う |
    | **M（Monetary）** | 購買金額合計 | 多く使う |

    スコアは1〜5の5段階。**合計13〜15点がVIP顧客**、3点が離脱顧客です。
    """)

    segments_list = rfm["セグメント"].unique().tolist()
    selected_segments = st.multiselect(
        "セグメントで絞り込み",
        options=segments_list,
        default=segments_list,
    )

    display_df = rfm[rfm["セグメント"].isin(selected_segments)][
        ["顧客名", "R", "F", "M", "合計", "セグメント", "最終購買日", "購買回数", "累計金額",
         "次回予測日", "ステータス"]
    ].sort_values("合計", ascending=False).reset_index(drop=True)

    st.dataframe(display_df, use_container_width=True, height=450)

    csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 CSVダウンロード",
        csv_data,
        file_name="rfm_scores.csv",
        mime="text/csv",
    )

# ── タブ2: セグメントマップ ──
with tab2:
    st.subheader("セグメントマップ")

    # RFヒートマップ
    st.markdown("#### R×F ヒートマップ（顧客数）")
    heatmap_data = rfm.groupby(["F", "R"]).size().unstack(fill_value=0)
    # 全ての1-5を埋める
    for i in range(1, 6):
        if i not in heatmap_data.columns:
            heatmap_data[i] = 0
        if i not in heatmap_data.index:
            heatmap_data.loc[i] = 0
    heatmap_data = heatmap_data.sort_index(ascending=False)[sorted(heatmap_data.columns)]

    fig_hm, ax_hm = plt.subplots(figsize=(8, 5))
    im = ax_hm.imshow(heatmap_data.values, cmap="Purples", aspect="auto")
    ax_hm.set_xticks(range(len(heatmap_data.columns)))
    ax_hm.set_xticklabels(heatmap_data.columns)
    ax_hm.set_yticks(range(len(heatmap_data.index)))
    ax_hm.set_yticklabels(heatmap_data.index)
    ax_hm.set_xlabel("R (Recency)")
    ax_hm.set_ylabel("F (Frequency)")
    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):
            val = heatmap_data.values[i, j]
            color = "white" if val > heatmap_data.values.max() * 0.6 else "black"
            ax_hm.text(j, i, str(val), ha="center", va="center", color=color, fontsize=12)
    plt.colorbar(im, ax=ax_hm, label="顧客数")
    fig_hm.tight_layout()
    st.pyplot(fig_hm)
    plt.close(fig_hm)

    # 円グラフ
    st.markdown("#### セグメント別 顧客数・売上構成比")
    seg_stats = rfm.groupby("セグメント").agg(
        顧客数=("顧客ID", "count"),
        売上合計=("累計金額", "sum"),
    )

    colors_map = {
        "VIP顧客": "#7C3AED",
        "優良顧客": "#8B5CF6",
        "一般顧客": "#A78BFA",
        "休眠顧客": "#C4B5FD",
        "離脱顧客": "#DDD6FE",
    }
    pie_colors = [colors_map.get(s, "#E5E7EB") for s in seg_stats.index]

    fig_pie, (ax_p1, ax_p2) = plt.subplots(1, 2, figsize=(12, 5))
    ax_p1.pie(seg_stats["顧客数"], labels=seg_stats.index, autopct="%1.1f%%",
              colors=pie_colors, startangle=90)
    ax_p1.set_title("顧客数構成比")
    ax_p2.pie(seg_stats["売上合計"], labels=seg_stats.index, autopct="%1.1f%%",
              colors=pie_colors, startangle=90)
    ax_p2.set_title("売上構成比")
    fig_pie.tight_layout()
    st.pyplot(fig_pie)
    plt.close(fig_pie)

    # ヒストグラム
    st.markdown("#### R / F / M スコア分布")
    fig_hist, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, col, title in zip(axes, ["R", "F", "M"], ["Recency", "Frequency", "Monetary"]):
        ax.hist(rfm[col], bins=range(1, 7), align="left", rwidth=0.7, color="#8B5CF6", edgecolor="white")
        ax.set_title(f"{title} スコア分布")
        ax.set_xlabel("スコア")
        ax.set_ylabel("顧客数")
        ax.set_xticks(range(1, 6))
    fig_hist.tight_layout()
    st.pyplot(fig_hist)
    plt.close(fig_hist)

    # ── セグメント遷移マトリクス ──
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("### 📊 セグメント遷移分析（前半→後半）")
    st.caption("顧客がどのセグメントからどのセグメントに移動したかを可視化します")
    st.caption(f"分割点: {split_date}  |  前半期間: {df['注文日'].min().date()} ～ {(split_dt - pd.Timedelta(days=1)).date()}  |  後半期間: {split_dt.date()} ～ {reference_date.date()}")

    if transition_df.empty:
        st.info("遷移分析に必要なデータが不足しています（前半・後半どちらかに購買が存在しない）。サイドバーの分割点を調整してください。")
    else:
        # クロス集計
        present_segs = [s for s in SEGMENT_ORDER if s in transition_df["セグメント_前半"].values or s in transition_df["セグメント_後半"].values]
        matrix = pd.crosstab(
            transition_df["セグメント_前半"],
            transition_df["セグメント_後半"],
        ).reindex(index=SEGMENT_ORDER, columns=SEGMENT_ORDER, fill_value=0)
        matrix = matrix.loc[matrix.index.isin(present_segs), matrix.columns.isin(present_segs)]

        n_segs = len(matrix)
        fig_tr, ax_tr = plt.subplots(figsize=(max(7, n_segs * 1.4), max(5, n_segs * 1.1)))

        # セルごとに色を決定: 対角=青、改善(上)=緑、悪化(下)=赤
        color_matrix = np.zeros((n_segs, n_segs, 4))  # RGBA
        row_labels = list(matrix.index)
        col_labels = list(matrix.columns)
        max_val = matrix.values.max() if matrix.values.max() > 0 else 1

        for ri, rseg in enumerate(row_labels):
            for ci, cseg in enumerate(col_labels):
                val = matrix.loc[rseg, cseg]
                alpha = 0.15 + 0.75 * (val / max_val)
                r_rank = SEGMENT_RANK.get(rseg, 0)
                c_rank = SEGMENT_RANK.get(cseg, 0)
                if ri == ci:  # 対角: 維持 → 青
                    color_matrix[ri, ci] = [0.34, 0.45, 0.94, alpha]
                elif c_rank < r_rank:  # 改善（ランク上昇） → 緑
                    color_matrix[ri, ci] = [0.13, 0.65, 0.40, alpha]
                else:  # 悪化（ランク低下） → 赤
                    color_matrix[ri, ci] = [0.86, 0.20, 0.18, alpha]

        ax_tr.imshow(color_matrix, aspect="auto")
        ax_tr.set_xticks(range(n_segs))
        ax_tr.set_xticklabels(col_labels, rotation=30, ha="right", fontsize=10)
        ax_tr.set_yticks(range(n_segs))
        ax_tr.set_yticklabels(row_labels, fontsize=10)
        ax_tr.set_xlabel("後半セグメント", fontsize=11)
        ax_tr.set_ylabel("前半セグメント", fontsize=11)
        ax_tr.set_title("セグメント遷移マトリクス（行: 前半 → 列: 後半）", fontsize=12, pad=12)

        for ri in range(n_segs):
            for ci in range(n_segs):
                val = matrix.values[ri, ci]
                if val > 0:
                    ax_tr.text(ci, ri, str(val), ha="center", va="center",
                               fontsize=11, fontweight="bold",
                               color="white" if color_matrix[ri, ci, 3] > 0.55 else "#333333")

        fig_tr.tight_layout()
        st.pyplot(fig_tr)
        plt.close(fig_tr)

        # ── 悪化サマリー警告 ──
        seg_avg_ltv = rfm.groupby("セグメント")["累計金額"].mean().to_dict()
        warn_lines = []
        for rseg in row_labels:
            r_rank = SEGMENT_RANK.get(rseg, 0)
            for cseg in col_labels:
                c_rank = SEGMENT_RANK.get(cseg, 0)
                if c_rank > r_rank:
                    n_move = int(matrix.loc[rseg, cseg])
                    if n_move > 0:
                        ltv = seg_avg_ltv.get(rseg, avg_ltv)
                        recovery = n_move * ltv * slider_dormant
                        warn_lines.append(f"⚠️ {rseg}→{cseg} {n_move}人: 今すぐ{rseg}限定クーポン配信で¥{recovery/10000:.1f}万の復帰効果（復帰率{slider_dormant:.0%}想定）")

        if warn_lines:
            st.warning("**セグメント悪化アラート**\n\n" + "\n\n".join(warn_lines))
        else:
            st.success("悪化したセグメント遷移はありません。")

        # ── 改善施策の自動提示 ──
        st.markdown("##### 💡 改善施策テンプレート")
        TRANSITION_TACTICS = {
            ("VIP顧客", "優良顧客"): "VIP限定クーポン配信（15%OFF）で購買頻度を維持し、VIPランクへの復帰を促進",
            ("VIP顧客", "一般顧客"): "VIP専用リテンションプログラム（ポイント2倍 + 先行販売権）を即時展開",
            ("VIP顧客", "休眠顧客"): "VIP向け特別オファー（専任スタッフによる個別フォロー）で緊急復帰を図る",
            ("VIP顧客", "離脱顧客"): "VIP専用30%OFFオファーと離脱理由アンケートを実施し、ブランドロイヤルティ再構築",
            ("優良顧客", "一般顧客"): "アップセル提案（関連商品セット割引）と購入金額ポイント強化で優良ランク維持",
            ("優良顧客", "休眠顧客"): "再購入クーポン（20%OFF）＋リマインドメールで休眠からの早期復帰を促進",
            ("優良顧客", "離脱顧客"): "特別割引＋パーソナライズドメールで優良顧客の離脱を防止",
            ("一般顧客", "休眠顧客"): "リピート促進キャンペーン（初回リピートクーポン10%OFF）で定期購買習慣を形成",
            ("一般顧客", "離脱顧客"): "低単価エントリー商品のご案内とリマインドメールで再エンゲージを図る",
            ("休眠顧客", "離脱顧客"): "最終手段として期間限定30%OFFオファーを送付し、無反応の場合は広告除外リストへ",
        }

        shown_tactics = set()
        for rseg in row_labels:
            r_rank = SEGMENT_RANK.get(rseg, 0)
            for cseg in col_labels:
                c_rank = SEGMENT_RANK.get(cseg, 0)
                if c_rank > r_rank:
                    n_move = int(matrix.loc[rseg, cseg])
                    if n_move > 0:
                        key = (rseg, cseg)
                        tactic = TRANSITION_TACTICS.get(key)
                        if tactic and key not in shown_tactics:
                            shown_tactics.add(key)
                            st.info(f"**{rseg} → {cseg}（{n_move}人）**: {tactic}")

# ── タブ3: 施策提案 ──
with tab3:
    st.subheader("セグメント別 推奨施策")

    # ── 施策の期待売上自動試算 ──
    assumed_rates = {
        "VIP顧客": {"施策名": "維持率向上", "想定率": slider_vip, "率ラベル": f"維持率向上+{slider_vip:.0%}"},
        "優良顧客": {"施策名": "客単価向上", "想定率": slider_good, "率ラベル": f"客単価向上+{slider_good:.0%}"},
        "一般顧客": {"施策名": "リピート率向上", "想定率": slider_normal, "率ラベル": f"リピート率+{slider_normal:.0%}"},
        "休眠顧客": {"施策名": "復帰", "想定率": slider_dormant, "率ラベル": f"復帰率{slider_dormant:.0%}"},
        "離脱顧客": {"施策名": "復帰", "想定率": slider_churn, "率ラベル": f"復帰率{slider_churn:.0%}"},
    }

    st.markdown("#### 📊 施策実行時の期待売上効果シミュレーション")
    effect_rows = []
    total_expected = 0
    for seg_name in ["VIP顧客", "優良顧客", "一般顧客", "休眠顧客", "離脱顧客"]:
        seg_df = rfm[rfm["セグメント"] == seg_name]
        n = len(seg_df)
        avg_ltv = seg_df["累計金額"].mean() if n > 0 else 0
        rate_info = assumed_rates[seg_name]
        expected = n * avg_ltv * rate_info["想定率"]
        total_expected += expected
        effect_rows.append({
            "セグメント": seg_name,
            "対象人数": f"{n}人",
            "平均LTV": f"¥{avg_ltv:,.0f}",
            "想定効果率": rate_info["率ラベル"],
            "期待売上効果": f"¥{expected:,.0f}",
        })

    effect_df = pd.DataFrame(effect_rows)
    st.dataframe(effect_df, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div class="kpi-card" style="margin-bottom:1.5rem;">'
        f'<div class="kpi-value">¥{total_expected:,.0f}</div>'
        f'<div class="kpi-label">全セグメント合計 施策実行時の期待売上増加額</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── 施策テーブル（既存） ──
    strategies = pd.DataFrame({
        "セグメント": ["VIP顧客", "優良顧客", "一般顧客", "休眠顧客", "離脱顧客"],
        "スコア帯": ["13-15", "10-12", "7-9", "4-6", "3"],
        "推奨施策": [
            "限定オファー・ロイヤルティプログラム",
            "アップセル・クロスセル提案",
            "リピート促進キャンペーン",
            "再購入クーポン・リマインドメール",
            "特別割引・復帰キャンペーン",
        ],
        "優先度": ["★★★★★", "★★★★☆", "★★★☆☆", "★★★★☆", "★★★★★"],
    })

    st.dataframe(strategies, use_container_width=True, hide_index=True)

    # 施策アクションプラン詳細
    st.markdown("#### 🎯 施策アクションプラン詳細")
    action_plans = {
        "VIP顧客": {
            "施策": "ロイヤルティプログラム導入",
            "具体的アクション": "• 専用会員証・VIPバッジ発行\n• 新商品の先行購入権提供\n• 誕生日月に特別クーポン（15%OFF）",
            "期待効果": "LTV +20〜30%向上",
            "優先度": "★★★★★",
        },
        "優良顧客": {
            "施策": "アップセル・クロスセル促進",
            "具体的アクション": "• 購入履歴に基づくレコメンドメール\n• 関連商品セット割引提案\n• 次回購入時ポイント2倍キャンペーン",
            "期待効果": "客単価 +15〜20%向上",
            "優先度": "★★★★☆",
        },
        "一般顧客": {
            "施策": "リピート促進キャンペーン",
            "具体的アクション": "• 3ヶ月間隔でフォローアップメール\n• 初回限定リピートクーポン（10%OFF）\n• 購入金額に応じたポイント還元強化",
            "期待効果": "リピート率 +10%向上",
            "優先度": "★★★☆☆",
        },
        "休眠顧客": {
            "施策": "再購入クーポン配布",
            "具体的アクション": "• 「お久しぶりです」メール配信\n• 期間限定20%OFFクーポン発行\n• 購入しやすい低単価商品を入口に",
            "期待効果": "休眠復帰率 5〜10%",
            "優先度": "★★★★☆",
        },
        "離脱顧客": {
            "施策": "復帰キャンペーン実施",
            "具体的アクション": "• 最終手段として30%OFF特別オファー\n• アンケートで離脱理由を収集\n• 復帰不可能と判断したら広告除外リストへ",
            "期待効果": "コスト最小化・復帰率3〜5%",
            "優先度": "★★★★★",
        },
    }

    selected_seg = st.selectbox("詳細を見るセグメントを選択", list(action_plans.keys()), key="action_seg")
    plan = action_plans[selected_seg]
    col_act1, col_act2, col_act3 = st.columns(3)
    col_act1.info(f"**施策**: {plan['施策']}")
    col_act2.success(f"**期待効果**: {plan['期待効果']}")
    col_act3.warning(f"**優先度**: {plan['優先度']}")
    st.markdown(f"**具体的アクション:**\n{plan['具体的アクション']}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── セグメント別アクションリスト（顧客リスト + CSVダウンロード） ──
    st.markdown("#### 📋 セグメント別アクションリスト")
    st.caption("明日からメール配信に使える顧客リストをセグメントごとにCSVダウンロードできます。")

    # 推奨施策マッピング
    seg_action_map = {
        "VIP顧客": "限定オファー・ロイヤルティプログラム",
        "優良顧客": "アップセル・クロスセル提案",
        "一般顧客": "リピート促進キャンペーン",
        "休眠顧客": "再購入クーポン・リマインドメール",
        "離脱顧客": "特別割引・復帰キャンペーン",
    }

    for seg in ["VIP顧客", "優良顧客", "一般顧客", "休眠顧客", "離脱顧客"]:
        seg_df = rfm[rfm["セグメント"] == seg].copy()
        count = len(seg_df)
        with st.expander(f"{seg}（{count}人）"):
            if count > 0:
                action_list = seg_df[["顧客ID", "顧客名", "最終購買日", "R", "F", "M", "合計",
                                      "累計金額", "次回予測日", "ステータス"]].copy()
                action_list["推奨施策"] = seg_action_map.get(seg, "")
                action_list = action_list.sort_values("累計金額", ascending=False).reset_index(drop=True)
                st.dataframe(action_list, use_container_width=True)

                csv_buf = action_list.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    f"📥 {seg}リストをCSVダウンロード",
                    csv_buf,
                    file_name=f"action_list_{seg}.csv",
                    mime="text/csv",
                    key=f"dl_{seg}",
                )
            else:
                st.write("該当顧客なし")

# ── 定期運用チェックリスト ──
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 📋 定期運用チェックリスト")

with st.expander("週次チェック"):
    st.markdown("""
- □ 要フォロー顧客にメール/クーポン配信
- □ VIP顧客の購買状況を確認
- □ 新規→一般への移行状況を確認
""")

with st.expander("月次チェック"):
    st.markdown("""
- □ セグメント構成比の変化を確認
- □ 施策実施結果を振り返り
- □ 想定率スライダーを実績値に更新
- □ 売上ダッシュボードと突合
""")

# ── フッター（関連ツールカード） ──
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")

st.markdown("""
<style>
.tool-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    height: 100%;
}
.tool-card-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.tool-card-title { font-size: 1.1rem; font-weight: 700; color: #1F2937; margin-bottom: 0.3rem; }
.tool-card-desc { font-size: 0.85rem; color: #6B7280; margin-bottom: 0.8rem; }
.tool-card a {
    display: inline-block;
    background: #8B5CF6;
    color: #FFFFFF !important;
    padding: 0.4rem 1.2rem;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
}
.tool-card a:hover { background: #7C3AED; }
</style>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3)
fc1.markdown("""
<div class="tool-card">
    <div class="tool-card-icon">📈</div>
    <div class="tool-card-title">売上ダッシュボード</div>
    <div class="tool-card-desc">VIP顧客が売上に与える影響を確認する</div>
    <a href="https://ec-sales-dashboard.streamlit.app" target="_blank">開く →</a>
</div>
""", unsafe_allow_html=True)
fc2.markdown("""
<div class="tool-card">
    <div class="tool-card-icon">📣</div>
    <div class="tool-card-title">広告ROI分析</div>
    <div class="tool-card-desc">休眠顧客の復帰施策に必要な広告コストを確認する</div>
    <a href="https://ec-ad-roi.streamlit.app" target="_blank">開く →</a>
</div>
""", unsafe_allow_html=True)
fc3.markdown("""
<div class="tool-card">
    <div class="tool-card-icon">🛒</div>
    <div class="tool-card-title">ECポータル</div>
    <div class="tool-card-desc">全ツール一覧に戻る</div>
    <a href="https://ec-ai-tools.streamlit.app" target="_blank">開く →</a>
</div>
""", unsafe_allow_html=True)

st.caption("AI経営パートナー × データサイエンス | 顧客RFM分析 v1.0")
