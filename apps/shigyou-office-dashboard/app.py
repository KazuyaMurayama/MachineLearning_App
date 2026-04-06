"""
事務所経営ダッシュボード
========================
8アプリのデータを1画面に集約した経営者向け統合ビュー
L3（月額30万円）コア機能
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
    page_title="事務所経営ダッシュボード",
    page_icon="🏛️",
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
    background: linear-gradient(135deg, #1e3a5f 0%, #2563EB 100%);
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
    background: linear-gradient(180deg, #EFF6FF, #FFFFFF);
    border-radius: 12px;
    border: 1px solid #BFDBFE;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.risk-high { color: #DC2626; font-weight: 700; }
.risk-medium { color: #D97706; font-weight: 700; }
.risk-low { color: #059669; font-weight: 700; }
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
    background: linear-gradient(to right, #2563EB, #e2e8f0);
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
    master_path = os.path.join(base_dir, "sample_data", "office_master.csv")
    kpi_path = os.path.join(base_dir, "sample_data", "monthly_kpi.csv")
    if not os.path.exists(master_path):
        try:
            import subprocess
            subprocess.run(
                [sys.executable, os.path.join(base_dir, "create_sample_data.py")],
                check=True,
            )
        except Exception as e:
            st.error(f"サンプルデータの生成に失敗しました: {e}")
            return None, None
    df = pd.read_csv(master_path)
    kpi_df = pd.read_csv(kpi_path)
    return df, kpi_df

# =====================================================================
# サイドバー
# =====================================================================

with st.sidebar:
    st.markdown("## 🏛️ 事務所経営ダッシュボード")
    st.markdown("**📅 対象月: 2026年4月**")
    st.divider()

    if st.button("🔄 サンプルデータ再生成"):
        load_data.clear()
        st.rerun()

    df_raw, kpi_df_raw = load_data()

    if df_raw is None:
        st.error("データ読み込み失敗")
        st.stop()

    st.success(f"✅ {len(df_raw)} 件読み込み済み")
    st.divider()

    # 業種フィルタ
    all_industries = sorted(df_raw["業種"].unique().tolist())
    selected_industries = st.multiselect(
        "業種フィルタ",
        options=all_industries,
        default=all_industries,
    )

    # 担当者フィルタ
    all_staff = sorted(df_raw["担当者"].unique().tolist())
    selected_staff = st.multiselect(
        "担当者フィルタ",
        options=all_staff,
        default=all_staff,
    )

    # リスクしきい値
    risk_threshold = st.slider(
        "リスクしきい値（離反リスクスコア）",
        min_value=50,
        max_value=90,
        value=70,
        step=1,
    )

    st.divider()
    st.markdown("""
**使い方**
1. 業種・担当者フィルタで対象を絞り込む
2. リスクしきい値を調整して高リスク先を抽出
3. タブ2「離反リスク管理」でCSVダウンロード
4. タブ3「入金・収益管理」でMRR推移を確認
5. タブ4「クロスセル機会」で増収案件を特定

💡 **L3 月額30万円の価値**: 離反リスク・入金遅延・クロスセルを一元管理し、年間数百万円の機会損失を防ぎます。
""")

# =====================================================================
# フィルタ適用
# =====================================================================

df = df_raw[
    df_raw["業種"].isin(selected_industries) &
    df_raw["担当者"].isin(selected_staff)
].copy()

kpi_df = kpi_df_raw.copy()

# =====================================================================
# Hero セクション
# =====================================================================

st.markdown("""
<div class="hero-section">
<h1>🏛️ 事務所経営ダッシュボード</h1>
<p>顧問先150社の経営状況を1画面で把握。月次コンサル資料を5分で完成。</p>
<p style="margin-top:0.6rem;font-size:0.95rem;color:rgba(255,255,255,0.75);">
💡 L3 月額30万円の価値 ― 離反リスク・入金遅延・クロスセル機会を一元管理し、年間数百万円の機会損失を防ぐ
</p>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# KPI カード
# =====================================================================

high_risk_df = df[df["離反リスクスコア"] >= risk_threshold]
total_clients = len(df)
high_risk_count = len(high_risk_df)

# MRR: monthly_kpi.csvの最新月と前月
mrr_current = int(kpi_df["MRR合計"].iloc[-1])
mrr_prev = int(kpi_df["MRR合計"].iloc[-2]) if len(kpi_df) >= 2 else mrr_current
mrr_mom = ((mrr_current - mrr_prev) / mrr_prev * 100) if mrr_prev != 0 else 0

# 入金遅延
delayed_df = df[df["直近入金遅延日数"] > 0]
delay_count = len(delayed_df)
delay_fee_sum = int(delayed_df["月額顧問料"].sum())

# クロスセル
crosssell_total = int(df["クロスセル推定増収額"].sum())
crosssell_opportunity_count = int((df["クロスセル機会数"] > 0).sum())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_clients}</div>
        <div class="kpi-label">顧問先総数</div>
        <div class="risk-high">高リスク: {high_risk_count} 件</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    mom_sign = "+" if mrr_mom >= 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">¥{mrr_current:,}</div>
        <div class="kpi-label">月次MRR合計</div>
        <div style="color:#2563EB;font-weight:700;">前月比 {mom_sign}{mrr_mom:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{delay_count} 件</div>
        <div class="kpi-label">当月入金遅延件数</div>
        <div class="risk-medium">遅延顧問料合計: ¥{delay_fee_sum:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">¥{crosssell_total:,}</div>
        <div class="kpi-label">クロスセル機会総額</div>
        <div class="risk-low">推定増収件数: {crosssell_opportunity_count} 件</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =====================================================================
# タブ
# =====================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 顧問先サマリー",
    "⚠️ 離反リスク管理",
    "💰 入金・収益管理",
    "🔄 クロスセル機会",
])

# ------------------------------------------------------------------
# タブ1: 顧問先サマリー
# ------------------------------------------------------------------
with tab1:
    st.subheader("📊 顧問先サマリー")

    col_a, col_b = st.columns(2)

    # 業種別顧問先数 横棒グラフ
    with col_a:
        st.markdown("**業種別 顧問先数**")
        industry_counts = df["業種"].value_counts().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(industry_counts.index, industry_counts.values, color="#2563EB", alpha=0.85)
        ax.set_xlabel("件数")
        ax.set_title("業種別 顧問先数")
        for i, v in enumerate(industry_counts.values):
            ax.text(v + 0.2, i, str(v), va="center", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 離反リスクスコア分布 ヒストグラム
    with col_b:
        st.markdown("**離反リスクスコア分布**")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df["離反リスクスコア"], bins=20, color="#1e3a5f", alpha=0.75, edgecolor="white")
        ax.axvline(x=risk_threshold, color="#DC2626", linestyle="--", linewidth=2, label=f"しきい値 {risk_threshold}")
        ax.set_xlabel("離反リスクスコア")
        ax.set_ylabel("件数")
        ax.set_title("離反リスクスコア分布")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    col_c, col_d = st.columns(2)

    # 担当者別MRR 横棒グラフ
    with col_c:
        st.markdown("**担当者別 月額顧問料合計**")
        staff_mrr = df.groupby("担当者")["月額顧問料"].sum().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = ["#2563EB", "#1e3a5f", "#3B82F6", "#1D4ED8", "#60A5FA"]
        ax.barh(staff_mrr.index, staff_mrr.values, color=colors[:len(staff_mrr)], alpha=0.85)
        ax.set_xlabel("月額顧問料合計（円）")
        ax.set_title("担当者別 月額顧問料合計")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 担当者×業種 クロス集計
    with col_d:
        st.markdown("**担当者 × 業種 クロス集計（件数）**")
        cross_table = pd.crosstab(df["担当者"], df["業種"])
        st.dataframe(cross_table, use_container_width=True)

# ------------------------------------------------------------------
# タブ2: 離反リスク管理
# ------------------------------------------------------------------
with tab2:
    st.subheader("⚠️ 離反リスク管理")

    # リスク判定関数
    def risk_label(score):
        if score >= risk_threshold:
            return "🔴 要緊急対応"
        elif score >= risk_threshold * 0.7:
            return "🟡 要注意"
        else:
            return "🟢 良好"

    # 高リスク顧問先テーブル
    st.markdown(f"**高リスク顧問先（スコア ≥ {risk_threshold}）**")
    if len(high_risk_df) == 0:
        st.info("高リスク顧問先はいません。")
    else:
        display_df = high_risk_df[[
            "顧問先ID", "顧問先名", "業種", "担当者", "月額顧問料", "離反リスクスコア"
        ]].copy().sort_values("離反リスクスコア", ascending=False)
        display_df["リスク判定"] = display_df["離反リスクスコア"].apply(risk_label)
        display_df["月額顧問料"] = display_df["月額顧問料"].apply(lambda x: f"¥{x:,}")
        st.dataframe(display_df.reset_index(drop=True), use_container_width=True)

    col_e, col_f = st.columns(2)

    # 散布図
    with col_e:
        st.markdown("**リスクスコア × 月額顧問料**")
        fig, ax = plt.subplots(figsize=(6, 4))
        colors_scatter = df["離反リスクスコア"].apply(
            lambda s: "#DC2626" if s >= risk_threshold else ("#D97706" if s >= risk_threshold * 0.7 else "#059669")
        )
        ax.scatter(df["離反リスクスコア"], df["月額顧問料"], c=colors_scatter, alpha=0.65, s=40)
        ax.axvline(x=risk_threshold, color="#DC2626", linestyle="--", linewidth=1.5, label=f"しきい値 {risk_threshold}")
        ax.set_xlabel("離反リスクスコア")
        ax.set_ylabel("月額顧問料（円）")
        ax.set_title("リスクスコア × 月額顧問料")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # リスク帯別集計
    with col_f:
        st.markdown("**リスク帯別 件数・月額顧問料合計**")
        df_risk = df.copy()
        df_risk["リスク帯"] = pd.cut(
            df_risk["離反リスクスコア"],
            bins=[-1, risk_threshold * 0.7, risk_threshold, 100],
            labels=["🟢 低リスク", "🟡 中リスク", "🔴 高リスク"],
        )
        risk_summary = df_risk.groupby("リスク帯", observed=True).agg(
            件数=("顧問先ID", "count"),
            月額顧問料合計=("月額顧問料", "sum"),
        ).reset_index()
        risk_summary["月額顧問料合計"] = risk_summary["月額顧問料合計"].apply(lambda x: f"¥{x:,}")
        st.dataframe(risk_summary, use_container_width=True, hide_index=True)

    # 高リスク放置コスト試算
    if len(high_risk_df) > 0:
        annual_loss = int(high_risk_df["月額顧問料"].sum() * 12)
        st.markdown(f"""
        <div class="alert-box">
        <strong>⚠️ 高リスク放置コスト試算</strong><br>
        高リスク顧問先（{len(high_risk_df)} 社）が全員解約した場合の年間損失額:<br>
        <span class="risk-high" style="font-size:1.5rem;">¥{annual_loss:,}</span>
        </div>
        """, unsafe_allow_html=True)

    # CSV出力
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("**📥 月次コンサル資料CSVをダウンロード**")

    # 高リスクTOP20
    top20_risk = df.sort_values("離反リスクスコア", ascending=False).head(20).copy()
    top20_risk["区分"] = "高リスクTOP20"

    # 遅延TOP10
    top10_delay = df.sort_values("直近入金遅延日数", ascending=False).head(10).copy()
    top10_delay["区分"] = "遅延TOP10"

    # クロスセルTOP10
    top10_cross = df.sort_values("クロスセル推定増収額", ascending=False).head(10).copy()
    top10_cross["区分"] = "クロスセルTOP10"

    export_df = pd.concat([top20_risk, top10_delay, top10_cross], ignore_index=True)
    csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 月次コンサル資料CSVをダウンロード",
        data=csv_bytes,
        file_name="monthly_consult_report.csv",
        mime="text/csv",
    )

# ------------------------------------------------------------------
# タブ3: 入金・収益管理
# ------------------------------------------------------------------
with tab3:
    st.subheader("💰 入金・収益管理")

    # MRR推移ライン
    st.markdown("**MRR推移（過去13ヶ月）**")
    fig, ax = plt.subplots(figsize=(10, 4))
    x_pos = range(len(kpi_df))
    ax.plot(x_pos, kpi_df["MRR合計"], color="#2563EB", linewidth=2.5, marker="o", markersize=5)
    ax.fill_between(x_pos, kpi_df["MRR合計"], alpha=0.1, color="#2563EB")
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(kpi_df["年月"].tolist(), rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("MRR（円）")
    ax.set_title("月次MRR推移")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    col_g, col_h = st.columns(2)

    # 入金遅延 散布図
    with col_g:
        st.markdown("**入金遅延日数 × 月額顧問料**")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(df["直近入金遅延日数"], df["月額顧問料"],
                   color="#1e3a5f", alpha=0.55, s=40)
        ax.set_xlabel("直近入金遅延日数")
        ax.set_ylabel("月額顧問料（円）")
        ax.set_title("入金遅延日数 × 月額顧問料")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 遅延金額TOP10
    with col_h:
        st.markdown("**遅延金額TOP10**")
        top10_delay_display = df[df["直近入金遅延日数"] > 0].sort_values(
            "直近入金遅延日数", ascending=False
        ).head(10)[["顧問先ID", "顧問先名", "業種", "担当者", "月額顧問料", "直近入金遅延日数"]].copy()
        top10_delay_display["月額顧問料"] = top10_delay_display["月額顧問料"].apply(lambda x: f"¥{x:,}")
        st.dataframe(top10_delay_display.reset_index(drop=True), use_container_width=True)

    # 業種別平均入金遅延日数
    st.markdown("**業種別 平均入金遅延日数**")
    industry_delay = df.groupby("業種")["直近入金遅延日数"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(industry_delay.index, industry_delay.values, color="#2563EB", alpha=0.8)
    ax.set_xlabel("平均遅延日数")
    ax.set_title("業種別 平均入金遅延日数")
    for bar, val in zip(bars, industry_delay.values):
        ax.text(val + 0.1, bar.get_y() + bar.get_height() / 2, f"{val:.1f}日", va="center", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ------------------------------------------------------------------
# タブ4: クロスセル機会
# ------------------------------------------------------------------
with tab4:
    st.subheader("🔄 クロスセル機会")

    col_i, col_j = st.columns(2)

    # クロスセル推定増収額TOP10
    with col_i:
        st.markdown("**クロスセル推定増収額 TOP10**")
        top10_cs = df[df["クロスセル機会数"] > 0].sort_values(
            "クロスセル推定増収額", ascending=False
        ).head(10)[["顧問先ID", "顧問先名", "業種", "担当者", "クロスセル機会数", "クロスセル推定増収額"]].copy()
        top10_cs["クロスセル推定増収額"] = top10_cs["クロスセル推定増収額"].apply(lambda x: f"¥{x:,}")
        st.dataframe(top10_cs.reset_index(drop=True), use_container_width=True)

    # 業種別クロスセル機会数
    with col_j:
        st.markdown("**業種別 クロスセル機会数**")
        industry_cs = df.groupby("業種")["クロスセル機会数"].sum().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(industry_cs.index, industry_cs.values, color="#1e3a5f", alpha=0.85)
        ax.set_xlabel("クロスセル機会数（合計）")
        ax.set_title("業種別 クロスセル機会数")
        for i, v in enumerate(industry_cs.values):
            ax.text(v + 0.1, i, str(v), va="center", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    col_k, col_l = st.columns(2)

    # 機会あり/なし 円グラフ
    with col_k:
        st.markdown("**クロスセル機会 あり/なし**")
        has_cs = (df["クロスセル機会数"] > 0).sum()
        no_cs = (df["クロスセル機会数"] == 0).sum()
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(
            [has_cs, no_cs],
            labels=[f"機会あり\n({has_cs}件)", f"機会なし\n({no_cs}件)"],
            colors=["#2563EB", "#CBD5E1"],
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 10},
        )
        ax.set_title("クロスセル機会 あり/なし")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 今月の推奨アクション TOP3
    with col_l:
        st.markdown("**今月の推奨アクション（TOP3案件）**")
        top3_cs = df[df["クロスセル機会数"] > 0].sort_values(
            "クロスセル推定増収額", ascending=False
        ).head(3)

        action_templates = [
            "決算対策・税務顧問の拡充をご提案ください。",
            "人事労務コンサルティングの追加契約を検討ください。",
            "補助金・助成金申請サポートを提案するチャンスです。",
        ]

        for idx, (_, row) in enumerate(top3_cs.iterrows()):
            action = action_templates[idx % len(action_templates)]
            st.markdown(f"""
            <div class="alert-box" style="background:#EFF6FF;border-color:#BFDBFE;">
            <strong>#{idx + 1} {row['顧問先名']}</strong>（{row['業種']} / {row['担当者']}）<br>
            推定増収額: <span style="color:#1e3a5f;font-weight:700;">¥{int(row['クロスセル推定増収額']):,}</span><br>
            推奨: {action}
            </div>
            """, unsafe_allow_html=True)

# =====================================================================
# フッター
# =====================================================================

st.markdown("---")
st.caption("事務所経営ダッシュボード | 士業AI経営パートナー L3 | v1.0")
