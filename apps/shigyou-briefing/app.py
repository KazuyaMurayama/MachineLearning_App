"""
月次AIブリーフィングレポート
============================
月額30万円のコンサル価値を具体化する月次レポート自動生成ツール
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

# ===== 日本語フォント設定 =====
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

# ===== ページ設定 =====
st.set_page_config(
    page_title="月次AIブリーフィング",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSSスタイル =====
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #1e3a5f 0%, #0891B2 100%);
    color: white; padding: 2rem; border-radius: 16px;
    text-align: center; margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.2rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0; }
.kpi-card {
    text-align: center; padding: 18px 12px;
    background: linear-gradient(180deg, #ECFEFF, #FFFFFF);
    border-radius: 12px; border: 1px solid #A5F3FC;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.highlight-box {
    background: #F0F9FF; border: 1px solid #BAE6FD;
    border-radius: 10px; padding: 16px; margin: 8px 0;
}
.alert-box {
    background: #FEF2F2; border: 1px solid #FECACA;
    border-radius: 10px; padding: 16px; margin: 8px 0;
}
.action-item {
    background: #F0FDF4; border: 1px solid #BBF7D0;
    border-radius: 8px; padding: 12px 16px; margin: 6px 0;
}
.section-divider { border: none; height: 2px; background: linear-gradient(to right, #0891B2, #e2e8f0); margin: 1.5rem 0; }
.print-header { font-size: 1.4rem; font-weight: 700; color: #1e3a5f; border-bottom: 2px solid #0891B2; padding-bottom: 8px; margin-bottom: 16px; }
.print-view { font-family: 'Meiryo', sans-serif; max-width: 800px; margin: 0 auto; }
.print-section { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# ===== データ読み込み =====
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    master = os.path.join(base_dir, "sample_data", "briefing_master.csv")
    history = os.path.join(base_dir, "sample_data", "monthly_history.csv")
    if not os.path.exists(master):
        try:
            subprocess.run([sys.executable, os.path.join(base_dir, "create_sample_data.py")], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            st.error(f"サンプルデータ生成に失敗しました: {e.stderr}")
            st.stop()
    df = pd.read_csv(master)
    hist = pd.read_csv(history)
    return df, hist

# ===== サイドバー =====
with st.sidebar:
    st.title("📋 月次AIブリーフィング")
    st.markdown("**📅 対象月: 2026年4月**")
    st.markdown("---")

    # データ読み込み（フィルタ前）
    df_all, hist_all = load_data()

    # 担当者フィルタ
    all_staff = sorted(df_all["担当者"].unique().tolist())
    selected_staff = st.multiselect(
        "担当者フィルタ",
        options=all_staff,
        default=all_staff
    )

    # 高リスクしきい値
    risk_threshold = st.slider(
        "高リスクしきい値",
        min_value=50,
        max_value=90,
        value=70,
        step=5
    )

    # データ再生成ボタン
    if st.button("🔄 データ再生成"):
        base_dir = os.path.dirname(__file__) if "__file__" in dir() else "."
        try:
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "create_sample_data.py")], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            st.error(f"サンプルデータ生成に失敗しました: {e.stderr}")
            st.stop()
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("""
**使い方**
1. 担当者フィルタで対象を絞り込み
2. 各タブで詳細データを確認
3. 印刷タブからPDF出力可能
""")

# ===== フィルタ適用 =====
df, hist = load_data()
if selected_staff:
    df = df[df["担当者"].isin(selected_staff)]

# ===== 計算ヘルパー =====
today = datetime.date.today()
target_month = "2026年4月"

# MRR計算
current_mrr = hist.iloc[-1]["MRR合計"]
prev_mrr = hist.iloc[-2]["MRR合計"]
mrr_delta_pct = ((current_mrr - prev_mrr) / prev_mrr * 100) if prev_mrr != 0 else 0

# 高リスク
high_risk_df = df[df["離反リスクスコア"] >= risk_threshold]
high_risk_count = len(high_risk_df)
prev_high_risk = int(hist.iloc[-2]["高リスク件数"])
high_risk_delta = high_risk_count - prev_high_risk

# クロスセル
crosssell_total = df["クロスセル推定増収額"].sum()
crosssell_man = crosssell_total / 10000

# 入金遅延
delay_df = df[df["入金遅延フラグ"] == 1]
delay_count = len(delay_df)
delay_total_fee = delay_df["月額顧問料"].sum()

# ===== Hero =====
st.markdown("""
<div class="hero-section">
<h1>📋 月次AIブリーフィングレポート</h1>
<p>30分かかっていた月次経営会議の資料が5分で完成。月額30万円のコンサル価値を可視化。</p>
<p style="margin-top:0.6rem;font-size:0.95rem;color:rgba(255,255,255,0.75);">
💡 L3 月額30万円の価値 ― 離反リスク・入金遅延・クロスセル機会を毎月自動レポート化。高リスク先放置による年間損失を事前に防ぐ
</p>
</div>
""", unsafe_allow_html=True)

# ===== KPIカード（4個）=====
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    delta_sign = "+" if mrr_delta_pct >= 0 else ""
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">¥{current_mrr:,}</div>
    <div class="kpi-label">当月MRR合計<br>前月比 {delta_sign}{mrr_delta_pct:.1f}%</div>
</div>
""", unsafe_allow_html=True)

with kpi_col2:
    delta_sign2 = "+" if high_risk_delta >= 0 else ""
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{high_risk_count}社</div>
    <div class="kpi-label">高リスク顧問先<br>前月比 {delta_sign2}{high_risk_delta}社</div>
</div>
""", unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">¥{crosssell_man:,.0f}万</div>
    <div class="kpi-label">クロスセル機会総額</div>
</div>
""", unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{delay_count}件</div>
    <div class="kpi-label">入金遅延件数<br>遅延合計 ¥{delay_total_fee:,}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ===== タブ =====
tab1, tab2, tab3 = st.tabs(["📊 エグゼクティブサマリー", "📝 詳細レポート", "🖨️ 印刷・PDF用ビュー"])

# ===========================
# タブ1: エグゼクティブサマリー
# ===========================
with tab1:
    st.subheader("今月のハイライト")

    # MRR前月比テキスト
    delta_sign = "+" if mrr_delta_pct >= 0 else ""
    trend_word = "増加" if mrr_delta_pct >= 0 else "減少"
    st.info(f"📈 **MRR動向**: 4月のMRR合計は¥{current_mrr:,}。前月比{delta_sign}{mrr_delta_pct:.1f}%で{trend_word}しました。")

    # 高リスク
    if len(high_risk_df) > 0:
        top_risk = high_risk_df.sort_values("離反リスクスコア", ascending=False).iloc[0]
        st.info(f"⚠️ **離反リスク**: 離反リスク高（スコア{risk_threshold}以上）の顧問先は{high_risk_count}社。特に{top_risk['顧問先名']}（スコア{top_risk['離反リスクスコア']}）は{top_risk['担当者']}が今月中に面談を実施してください。")
    else:
        st.info(f"✅ **離反リスク**: 離反リスク高（スコア{risk_threshold}以上）の顧問先は現在0社です。")

    # クロスセル
    top_cross = df.sort_values("クロスセル推定増収額", ascending=False).iloc[0]
    st.info(f"💰 **クロスセル**: 今月の最有望クロスセル案件は{top_cross['顧問先名']}（推定増収{int(top_cross['クロスセル推定増収額']):,}円）。{top_cross['担当者']}がフォローを推奨します。")

    # 入金遅延
    if delay_count > 0:
        top_delay = delay_df.sort_values("入金遅延日数", ascending=False).iloc[0]
        st.warning(f"🔔 **入金遅延**: 入金遅延{delay_count}社。{top_delay['顧問先名']}（{int(top_delay['入金遅延日数'])}日超過）は早急な催促が必要です。")
    else:
        st.success("✅ **入金遅延**: 当月の入金遅延はありません。")

    # 高リスク放置コスト試算
    if len(high_risk_df) > 0:
        annual_loss_est = int(high_risk_df["月額顧問料"].sum() * 12)
        st.markdown(f"""
<div class="alert-box">
<strong>⚠️ 高リスク先を放置した場合の損失試算</strong><br>
高リスク顧問先 <strong>{high_risk_count}社</strong>が全員解約した場合、年間損失は
<span style="color:#DC2626;font-size:1.3rem;font-weight:700;">¥{annual_loss_est:,}</span>
に相当します。今月中の面談・フォローが急務です。
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # MRR推移グラフ（13ヶ月, matplotlib 折れ線）
    st.subheader("MRR推移（過去13ヶ月）")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(hist["年月"], hist["MRR合計"], marker="o", color="#0891B2", linewidth=2.5, markersize=6)
    ax.fill_between(range(len(hist)), hist["MRR合計"], alpha=0.1, color="#0891B2")
    ax.set_xticks(range(len(hist)))
    ax.set_xticklabels(hist["年月"].tolist(), rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("MRR合計（円）", fontsize=10)
    ax.set_title("月次MRR推移", fontsize=12, color="#1e3a5f", fontweight="bold")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 業種別顧問先構成 円グラフ
    st.subheader("業種別顧問先構成")
    industry_counts = df["業種"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    colors = ["#1e3a5f", "#0891B2", "#0ea5e9", "#38bdf8", "#7dd3fc", "#bae6fd", "#e0f2fe", "#f0f9ff"]
    wedges, texts, autotexts = ax2.pie(
        industry_counts.values,
        labels=industry_counts.index.tolist(),
        autopct="%1.1f%%",
        colors=colors[:len(industry_counts)],
        startangle=140,
        pctdistance=0.85
    )
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
    ax2.set_title("業種別顧問先構成", fontsize=12, color="#1e3a5f", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 担当者別KPIサマリー テーブル
    st.subheader("担当者別KPIサマリー")
    staff_summary = df.groupby("担当者").agg(
        担当件数=("顧問先ID", "count"),
        MRR合計=("月額顧問料", "sum"),
        高リスク件数=("離反リスクスコア", lambda x: (x >= risk_threshold).sum()),
        平均離反スコア=("離反リスクスコア", "mean")
    ).reset_index()
    staff_summary["MRR合計"] = staff_summary["MRR合計"].apply(lambda x: f"¥{int(x):,}")
    staff_summary["平均離反スコア"] = staff_summary["平均離反スコア"].round(1)
    st.dataframe(staff_summary, use_container_width=True, hide_index=True)


# ===========================
# タブ2: 詳細レポート
# ===========================
with tab2:

    # セクション①: 離反リスクTOP5
    st.markdown('<p class="print-header">① 離反リスク TOP5</p>', unsafe_allow_html=True)

    top5_risk = df.sort_values("離反リスクスコア", ascending=False).head(5).copy()

    def get_risk_action(row):
        if row["離反リスクスコア"] >= 80 and row["当月面談実施"] == 0:
            return "今月中に面談を設定し、顧問継続の意向確認"
        elif row["離反リスクスコア"] >= 70 and row["入金遅延フラグ"] == 1:
            return "入金催促と合わせて面談設定"
        else:
            return "定期的な状況確認の連絡を入れる"

    top5_risk["面談状況"] = top5_risk["当月面談実施"].map({1: "実施済み", 0: "未実施"})
    top5_risk["推奨アクション"] = top5_risk.apply(get_risk_action, axis=1)

    display_risk = top5_risk[["顧問先名", "業種", "担当者", "離反リスクスコア", "月額顧問料", "面談状況", "推奨アクション"]].copy()
    display_risk["月額顧問料"] = display_risk["月額顧問料"].apply(lambda x: f"¥{int(x):,}")
    st.dataframe(display_risk, use_container_width=True, hide_index=True)

    annual_loss = int(top5_risk["月額顧問料"].sum()) * 12
    st.warning(f"⚠️ これら5社が全社解約した場合の年間損失: ¥{annual_loss // 10000:,}万")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # セクション②: 入金遅延対応推奨
    st.markdown('<p class="print-header">② 入金遅延対応推奨</p>', unsafe_allow_html=True)

    if len(delay_df) > 0:
        delay_display = delay_df.sort_values("入金遅延日数", ascending=False).copy()

        def get_priority(days):
            if days > 30:
                return "高"
            elif days > 15:
                return "中"
            else:
                return "低"

        delay_display["対応優先度"] = delay_display["入金遅延日数"].apply(get_priority)
        delay_display_show = delay_display[["顧問先名", "業種", "担当者", "月額顧問料", "入金遅延日数", "対応優先度"]].copy()
        delay_display_show["月額顧問料"] = delay_display_show["月額顧問料"].apply(lambda x: f"¥{int(x):,}")

        high_priority = delay_display_show[delay_display_show["対応優先度"] == "高"]
        mid_priority = delay_display_show[delay_display_show["対応優先度"] == "中"]
        low_priority = delay_display_show[delay_display_show["対応優先度"] == "低"]

        if len(high_priority) > 0:
            st.error(f"🔴 優先度「高」: {len(high_priority)}件（30日超過）")
            st.dataframe(high_priority, use_container_width=True, hide_index=True)
        if len(mid_priority) > 0:
            st.warning(f"🟡 優先度「中」: {len(mid_priority)}件（15〜30日超過）")
            st.dataframe(mid_priority, use_container_width=True, hide_index=True)
        if len(low_priority) > 0:
            st.info(f"🔵 優先度「低」: {len(low_priority)}件（15日以内）")
            st.dataframe(low_priority, use_container_width=True, hide_index=True)
    else:
        st.success("✅ 入金遅延はありません。")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # セクション③: クロスセル機会ランキング（TOP10）
    st.markdown('<p class="print-header">③ クロスセル機会ランキング（TOP10）</p>', unsafe_allow_html=True)

    top10_cross = df[df["クロスセル推定増収額"] > 0].sort_values("クロスセル推定増収額", ascending=False).head(10).copy()

    def get_crosssell_reason(industry):
        if industry == "建設業":
            return "許認可申請が未利用。建設業者の多くが必要"
        elif industry == "飲食業":
            return "社保手続きが未利用。従業員増加期に効果的"
        elif industry == "IT":
            return "補助金申請が未利用。IT導入補助金が利用可能な可能性"
        else:
            return "既存サービスの見直しで付加価値を提供"

    top10_cross["推薦理由"] = top10_cross["業種"].apply(get_crosssell_reason)
    top10_cross_show = top10_cross[["顧問先名", "業種", "担当者", "クロスセル推定増収額", "推薦理由"]].copy()
    top10_cross_show["クロスセル推定増収額"] = top10_cross_show["クロスセル推定増収額"].apply(lambda x: f"¥{int(x):,}")
    st.dataframe(top10_cross_show, use_container_width=True, hide_index=True)

    total_cross = int(top10_cross["クロスセル推定増収額"].sum())
    st.success(f"💰 TOP10の推定増収額合計: ¥{total_cross:,}（¥{total_cross // 10000:,}万）")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # セクション④: 翌月の重点アクション
    st.markdown('<p class="print-header">④ 翌月の重点アクション（3件）</p>', unsafe_allow_html=True)

    actions = []
    # 最高リスク先
    top_risk_action = df.sort_values("離反リスクスコア", ascending=False).iloc[0]
    actions.append(f"🔴 【最優先】{top_risk_action['顧問先名']}（離反スコア{top_risk_action['離反リスクスコア']}）への面談設定 ― {top_risk_action['担当者']}が翌月第1週に実施")
    # 最大クロスセル
    top_cross_action = df.sort_values("クロスセル推定増収額", ascending=False).iloc[0]
    actions.append(f"🟡 【増収】{top_cross_action['顧問先名']}へのクロスセル提案（推定+{int(top_cross_action['クロスセル推定増収額']):,}円/月）― 来月の訪問時に提案")
    # 入金遅延
    top_delay_action = df[df["入金遅延日数"] > 15].sort_values("入金遅延日数", ascending=False)
    if len(top_delay_action) > 0:
        d = top_delay_action.iloc[0]
        actions.append(f"🔵 【入金】{d['顧問先名']}（{int(d['入金遅延日数'])}日超過）への催促連絡 ― {d['担当者']}が週内に実施")
    else:
        actions.append("🟢 【維持】入金遅延なし。現状の管理体制を継続")

    for i, action in enumerate(actions, 1):
        st.markdown(f'<div class="action-item"><b>{i}.</b> {action}</div>', unsafe_allow_html=True)


# ===========================
# タブ3: 印刷・PDF用ビュー
# ===========================
with tab3:
    # 印刷ビュー用CSS（サイドバー非表示）
    st.markdown("""
<style>
@media print {
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    .stTabs [data-baseweb="tab-list"] { display: none !important; }
}
.print-view { font-family: 'Meiryo', sans-serif; max-width: 800px; margin: 0 auto; }
.print-section { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

    # 1. レポートヘッダー
    st.markdown(f"""
<div class="print-view">
<div class="print-section">
<div class="print-header">月次AIブリーフィングレポート</div>

| 項目 | 内容 |
|------|------|
| 事務所名 | サンプル税理士事務所 |
| 対象月 | {target_month} |
| 作成日 | {today.strftime('%Y年%m月%d日')} |

</div>
</div>
""", unsafe_allow_html=True)

    # 2. 【1. 経営サマリー】
    st.markdown('<div class="print-header">1. 経営サマリー</div>', unsafe_allow_html=True)
    summary_df = pd.DataFrame({
        "指標": ["当月MRR合計", "高リスク顧問先数", "クロスセル機会総額", "入金遅延件数"],
        "値": [
            f"¥{current_mrr:,}",
            f"{high_risk_count}社",
            f"¥{int(crosssell_man):,}万",
            f"{delay_count}件"
        ],
        "前月比/補足": [
            f"{'+' if mrr_delta_pct >= 0 else ''}{mrr_delta_pct:.1f}%",
            f"しきい値: スコア{risk_threshold}以上",
            f"合計 ¥{int(crosssell_total):,}",
            f"遅延合計 ¥{delay_total_fee:,}"
        ]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 3. 【2. 離反リスクTOP5】
    st.markdown('<div class="print-header">2. 離反リスク TOP5</div>', unsafe_allow_html=True)
    top5_print = df.sort_values("離反リスクスコア", ascending=False).head(5).copy()
    top5_print["面談状況"] = top5_print["当月面談実施"].map({1: "実施済み", 0: "未実施"})
    top5_print["推奨アクション"] = top5_print.apply(get_risk_action, axis=1)
    top5_print_show = top5_print[["顧問先名", "業種", "担当者", "離反リスクスコア", "月額顧問料", "面談状況", "推奨アクション"]].copy()
    top5_print_show["月額顧問料"] = top5_print_show["月額顧問料"].apply(lambda x: f"¥{int(x):,}")
    st.dataframe(top5_print_show, use_container_width=True, hide_index=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 4. 【3. 入金遅延対応リスト】
    st.markdown('<div class="print-header">3. 入金遅延対応リスト</div>', unsafe_allow_html=True)
    if len(delay_df) > 0:
        delay_print = delay_df.sort_values("入金遅延日数", ascending=False).copy()
        delay_print["対応優先度"] = delay_print["入金遅延日数"].apply(get_priority)
        delay_print_show = delay_print[["顧問先名", "業種", "担当者", "月額顧問料", "入金遅延日数", "対応優先度"]].copy()
        delay_print_show["月額顧問料"] = delay_print_show["月額顧問料"].apply(lambda x: f"¥{int(x):,}")
        st.dataframe(delay_print_show, use_container_width=True, hide_index=True)
    else:
        st.markdown("入金遅延はありません。")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 5. 【4. クロスセル機会TOP5】
    st.markdown('<div class="print-header">4. クロスセル機会 TOP5</div>', unsafe_allow_html=True)
    top5_cross_print = df[df["クロスセル推定増収額"] > 0].sort_values("クロスセル推定増収額", ascending=False).head(5).copy()
    top5_cross_print["推薦理由"] = top5_cross_print["業種"].apply(get_crosssell_reason)
    top5_cross_print_show = top5_cross_print[["顧問先名", "業種", "担当者", "クロスセル推定増収額", "推薦理由"]].copy()
    top5_cross_print_show["クロスセル推定増収額"] = top5_cross_print_show["クロスセル推定増収額"].apply(lambda x: f"¥{int(x):,}")
    st.dataframe(top5_cross_print_show, use_container_width=True, hide_index=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 6. 【5. 来月の重点アクション】
    st.markdown('<div class="print-header">5. 来月の重点アクション</div>', unsafe_allow_html=True)
    for i, action in enumerate(actions, 1):
        st.markdown(f"**{i}.** {action}")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 7. Markdownダウンロードボタン
    def build_markdown_report():
        lines = []
        lines.append(f"# 月次AIブリーフィングレポート")
        lines.append(f"")
        lines.append(f"- **事務所名**: サンプル税理士事務所")
        lines.append(f"- **対象月**: {target_month}")
        lines.append(f"- **作成日**: {today.strftime('%Y年%m月%d日')}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 1. 経営サマリー")
        lines.append(f"")
        lines.append(f"| 指標 | 値 | 補足 |")
        lines.append(f"|------|-----|------|")
        lines.append(f"| 当月MRR合計 | ¥{current_mrr:,} | 前月比 {'+' if mrr_delta_pct >= 0 else ''}{mrr_delta_pct:.1f}% |")
        lines.append(f"| 高リスク顧問先数 | {high_risk_count}社 | しきい値: スコア{risk_threshold}以上 |")
        lines.append(f"| クロスセル機会総額 | ¥{int(crosssell_man):,}万 | 合計 ¥{int(crosssell_total):,} |")
        lines.append(f"| 入金遅延件数 | {delay_count}件 | 遅延合計 ¥{delay_total_fee:,} |")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 2. 離反リスク TOP5")
        lines.append(f"")
        lines.append(f"| 顧問先名 | 業種 | 担当者 | 離反リスクスコア | 月額顧問料 | 面談状況 | 推奨アクション |")
        lines.append(f"|---------|------|-------|----------------|-----------|---------|--------------|")
        for _, row in top5_print_show.iterrows():
            lines.append(f"| {row['顧問先名']} | {row['業種']} | {row['担当者']} | {row['離反リスクスコア']} | {row['月額顧問料']} | {row['面談状況']} | {row['推奨アクション']} |")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 3. 入金遅延対応リスト")
        lines.append(f"")
        if len(delay_df) > 0:
            lines.append(f"| 顧問先名 | 業種 | 担当者 | 月額顧問料 | 遅延日数 | 対応優先度 |")
            lines.append(f"|---------|------|-------|-----------|---------|----------|")
            for _, row in delay_print_show.iterrows():
                lines.append(f"| {row['顧問先名']} | {row['業種']} | {row['担当者']} | {row['月額顧問料']} | {row['入金遅延日数']} | {row['対応優先度']} |")
        else:
            lines.append(f"入金遅延はありません。")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 4. クロスセル機会 TOP5")
        lines.append(f"")
        lines.append(f"| 顧問先名 | 業種 | 担当者 | 推定増収額 | 推薦理由 |")
        lines.append(f"|---------|------|-------|-----------|---------|")
        for _, row in top5_cross_print_show.iterrows():
            lines.append(f"| {row['顧問先名']} | {row['業種']} | {row['担当者']} | {row['クロスセル推定増収額']} | {row['推薦理由']} |")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 5. 来月の重点アクション")
        lines.append(f"")
        for i, action in enumerate(actions, 1):
            lines.append(f"{i}. {action}")
        lines.append(f"")
        return "\n".join(lines)

    md_content = build_markdown_report()
    st.download_button(
        label="📥 このレポートをMarkdownでダウンロード",
        data=md_content,
        file_name=f"briefing_report_{today.strftime('%Y%m%d')}.md",
        mime="text/markdown"
    )

    st.info("🖨️ ブラウザの印刷機能（Ctrl+P）を使用することでPDF形式でも保存できます。印刷時はサイドバーが非表示になります。")
