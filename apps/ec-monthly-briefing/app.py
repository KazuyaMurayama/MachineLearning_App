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
    page_title="EC月次AIブリーフィング",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSSスタイル =====
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

# ===== データ読み込み =====
@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    products_path = os.path.join(base_dir, "sample_data", "products.csv")
    customers_path = os.path.join(base_dir, "sample_data", "customers.csv")
    orders_path = os.path.join(base_dir, "sample_data", "orders.csv")
    ads_path = os.path.join(base_dir, "sample_data", "ads.csv")

    if not os.path.exists(products_path):
        subprocess.run([sys.executable, os.path.join(base_dir, "create_sample_data.py")])

    products = pd.read_csv(products_path, encoding="utf-8-sig")
    customers = pd.read_csv(customers_path, encoding="utf-8-sig")
    orders_df = pd.read_csv(orders_path, encoding="utf-8-sig")
    ads_df = pd.read_csv(ads_path, encoding="utf-8-sig")
    return products, customers, orders_df, ads_df

# ===== サイドバー =====
with st.sidebar:
    st.title("📰 EC月次AIブリーフィング")
    st.markdown("**📅 対象月: 2026年4月**")
    st.markdown("---")

    risk_threshold = st.slider(
        "離脱リスクしきい値",
        min_value=50,
        max_value=90,
        value=70,
        step=5,
        help="このスコア以上の顧客を高リスクと判定します"
    )

    if st.button("🔄 データ再生成"):
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "create_sample_data.py")])
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

# ===== データ読み込み =====
products, customers, orders_df, ads_df = load_data()

# ===== 計算ヘルパー =====
today = datetime.date.today()
target_month = "2026年4月"

# 月次集計
monthly_orders = orders_df.groupby("年月").agg(
    売上合計=("売上", "sum"),
    粗利合計=("粗利", "sum"),
    注文数合計=("注文数", "sum"),
).reset_index()

monthly_ads = ads_df.groupby("年月").agg(
    広告費合計=("広告費", "sum"),
    CV数合計=("CV数", "sum"),
    広告売上合計=("売上", "sum"),
).reset_index()
monthly_ads["ROAS平均"] = (monthly_ads["広告売上合計"] / monthly_ads["広告費合計"]).round(2)

# 当月・前月
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

# 離脱リスク
high_risk_customers = customers[customers["離脱リスクスコア"] >= risk_threshold]
high_risk_ratio = len(high_risk_customers) / len(customers) * 100

# ===== Hero =====
st.markdown("""
<div class="hero-section">
<h1>📰 EC月次AIブリーフィング</h1>
<p>月次経営会議の資料が5分で完成 — <strong>L3 プレミアムパック 月額26万円</strong>の伴走支援を可視化<br>
<span style="font-size:0.95rem;opacity:0.9;">GA4・Lookerでは見えない "次の一手" を、AI自動生成のエグゼクティブサマリーとアクション提案で即座に提示</span></p>
</div>
""", unsafe_allow_html=True)

# ===== KPIカード（4個）=====
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    mom = (current_rev - prev_rev) / prev_rev * 100 if prev_rev != 0 else 0
    sign = "+" if mom >= 0 else ""
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">¥{current_rev // 10000:,}万</div>
    <div class="kpi-label">当月売上<br>前月比 {sign}{mom:.1f}%</div>
</div>
""", unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{gross_margin:.1f}%</div>
    <div class="kpi-label">粗利率</div>
</div>
""", unsafe_allow_html=True)

with kpi_col3:
    roas_diff = current_roas - prev_roas
    sign3 = "+" if roas_diff >= 0 else ""
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{current_roas:.2f}</div>
    <div class="kpi-label">平均ROAS<br>前月比 {sign3}{roas_diff:.2f}</div>
</div>
""", unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{high_risk_ratio:.1f}%</div>
    <div class="kpi-label">離脱リスク高顧客比率<br>({len(high_risk_customers)}人)</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ===== ルールベース関数群 =====
def generate_summary(current_rev, prev_rev, avg_roas, high_risk_ratio):
    """エグゼクティブサマリーをルールベースで生成"""
    mom = (current_rev - prev_rev) / prev_rev * 100 if prev_rev != 0 else 0
    if mom > 5:
        msg = f"当月の売上は¥{current_rev:,}（約{current_rev // 10000:,}万円）で、前月比+{mom:.1f}%と**好調**です。"
    elif mom > -5:
        msg = f"当月の売上は¥{current_rev:,}（約{current_rev // 10000:,}万円）で、前月比{mom:+.1f}%と**横ばい**です。"
    else:
        msg = f"当月の売上は¥{current_rev:,}（約{current_rev // 10000:,}万円）で、前月比{mom:.1f}%と**要注意**です。改善施策を検討ください。"

    if avg_roas >= 3.0:
        roas_msg = f"広告ROASは{avg_roas:.2f}と優秀な水準を維持しています。"
    elif avg_roas >= 1.5:
        roas_msg = f"広告ROASは{avg_roas:.2f}と標準的な水準です。さらなる改善余地があります。"
    else:
        roas_msg = f"広告ROASは{avg_roas:.2f}と低水準です。広告配分の見直しを推奨します。"

    if high_risk_ratio > 20:
        risk_msg = f"離脱リスク高顧客が全体の{high_risk_ratio:.1f}%に達しており、早急な再エンゲージ施策が必要です。"
    elif high_risk_ratio > 10:
        risk_msg = f"離脱リスク高顧客は全体の{high_risk_ratio:.1f}%です。定期的なフォローアップを継続してください。"
    else:
        risk_msg = f"離脱リスク高顧客は全体の{high_risk_ratio:.1f}%と低水準です。現行の顧客維持施策を継続してください。"

    return f"{msg} {roas_msg} {risk_msg}"


def generate_channel_comment(ch, roas, prev_roas):
    """チャネル別コメントをルールベースで生成"""
    diff = roas - prev_roas
    trend = f"（前月比{diff:+.2f}）"
    if roas >= 3.0:
        return f"✅ {ch}: ROAS {roas:.2f}{trend}は優秀。現予算維持を推奨。"
    elif roas >= 1.5:
        return f"📊 {ch}: ROAS {roas:.2f}{trend}は標準。改善余地あり。"
    else:
        return f"⚠️ {ch}: ROAS {roas:.2f}{trend}は要警戒。予算20%削減を検討。"


def get_recommended_action(rfm_seg, risk_score):
    """顧客セグメント別推奨アクション"""
    if rfm_seg == "Champions":
        return "VIP特典クーポン+パーソナルDM"
    elif rfm_seg == "Loyal":
        return "再購入キャンペーン案内"
    elif rfm_seg == "AtRisk":
        return "割引クーポン+アンケート"
    elif rfm_seg == "Lost":
        return "再エンゲージキャンペーン（-30%クーポン）"
    else:
        return "ウェルカムシリーズメール送信"


def generate_actions(ads_current, products_df, customers_df, threshold):
    """次月アクション3件をルールベースで生成"""
    actions = []
    # 1. 最低ROASチャネルの予算削減
    min_roas_ch = ads_current.sort_values("ROAS").iloc[0]
    actions.append(
        f"🔴 【予算最適化】{min_roas_ch['チャネル']}のROASは{min_roas_ch['ROAS']}。予算を20%削減し、高ROASチャネルへ再配分"
    )
    # 2. 離脱リスク顧客への再エンゲージ
    high_risk_count = len(customers_df[customers_df["離脱リスクスコア"] >= threshold])
    actions.append(
        f"🟡 【顧客維持】離脱リスク高顧客{high_risk_count}人へ再エンゲージキャンペーン実施"
    )
    # 3. 在庫切迫 or 過剰対応
    low_stock = products_df[products_df["在庫数"] < 20]
    if len(low_stock) > 0:
        top_cat = low_stock["カテゴリ"].mode().iloc[0]
        actions.append(
            f"🔵 【在庫】在庫切迫商品{len(low_stock)}件（TOPカテゴリ: {top_cat}）の追加発注を実施"
        )
    else:
        over_stock = products_df[products_df["在庫数"] > 300]
        actions.append(
            f"🟢 【在庫】過剰在庫商品{len(over_stock)}件のセール企画を検討"
        )
    return actions


def build_markdown_report(summary_text, current_rev, gross_margin, current_roas, high_risk_ratio,
                           channel_df, risk_top, actions):
    """月次レポート全文Markdownを生成"""
    # チャネルテーブル
    ch_rows = []
    for _, row in channel_df.iterrows():
        ch_rows.append(
            f"| {row['チャネル']} | ¥{int(row['当月売上']):,} | {row['前月比']} | {row['ROAS']:.2f} |"
        )
    channel_table_markdown = "| チャネル | 当月売上 | 前月比 | ROAS |\n|---|---|---|---|\n" + "\n".join(ch_rows)

    # 離脱リスクテーブル
    risk_rows = []
    for _, row in risk_top.head(10).iterrows():
        risk_rows.append(
            f"| {row['顧客ID']} | {row['RFMセグメント']} | ¥{int(row['累計購入額']):,} | {row['離脱リスクスコア']} |"
        )
    risk_table_markdown = "| 顧客ID | RFMセグメント | 累計購入額 | 離脱リスクスコア |\n|---|---|---|---|\n" + "\n".join(risk_rows)

    md = f"""# EC月次ブリーフィングレポート

対象月: 2026年4月
作成日: {today}

## 1. エグゼクティブサマリー
{summary_text}

## 2. KPI
- 当月売上: ¥{current_rev:,}（約¥{current_rev // 10000:,}万円）
- 粗利率: {gross_margin:.1f}%
- 平均ROAS: {current_roas:.2f}
- 離脱リスク高顧客比率: {high_risk_ratio:.1f}%

## 3. チャネル別ROI
{channel_table_markdown}

## 4. 離脱リスク顧客TOP10
{risk_table_markdown}

## 5. 次月の重点アクション
1. {actions[0]}
2. {actions[1]}
3. {actions[2]}
"""
    return md


# ===== タブ =====
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 今月のサマリー",
    "🔗 チャネル別ROIレビュー",
    "👥 離脱リスク顧客TOP20",
    "🎯 次月アクション & レポート"
])

# ===========================
# タブ1: 今月のサマリー
# ===========================
with tab1:
    st.subheader("KPIサマリー")
    c1, c2, c3, c4 = st.columns(4)
    mom = (current_rev - prev_rev) / prev_rev * 100 if prev_rev != 0 else 0
    with c1:
        sign = "+" if mom >= 0 else ""
        st.metric("当月売上", f"¥{current_rev // 10000:,}万", f"{sign}{mom:.1f}%")
    with c2:
        st.metric("粗利率", f"{gross_margin:.1f}%")
    with c3:
        roas_diff = current_roas - prev_roas
        sign3 = "+" if roas_diff >= 0 else ""
        st.metric("平均ROAS", f"{current_roas:.2f}", f"{sign3}{roas_diff:.2f}")
    with c4:
        st.metric("離脱リスク高顧客比率", f"{high_risk_ratio:.1f}%", f"{len(high_risk_customers)}人")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 月次売上推移ライン（13ヶ月）
    st.subheader("月次売上推移（過去13ヶ月）")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(
        monthly_orders["年月"],
        monthly_orders["売上合計"],
        marker="o", color="#059669", linewidth=2.5, markersize=6
    )
    ax.fill_between(
        range(len(monthly_orders)),
        monthly_orders["売上合計"],
        alpha=0.12, color="#059669"
    )
    ax.set_xticks(range(len(monthly_orders)))
    ax.set_xticklabels(monthly_orders["年月"].tolist(), rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("売上合計（円）", fontsize=10)
    ax.set_title("月次売上推移", fontsize=12, color="#065F46", fontweight="bold")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 自動生成エグゼクティブサマリー
    st.subheader("自動生成エグゼクティブサマリー")
    summary_text = generate_summary(current_rev, prev_rev, current_roas, high_risk_ratio)
    if mom > 5:
        st.info(f"📈 {summary_text}")
    elif mom > -5:
        st.info(f"📊 {summary_text}")
    else:
        st.warning(f"⚠️ {summary_text}")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 業績サマリーテーブル: チャネル別
    st.subheader("チャネル別業績サマリー")
    current_m = monthly_orders["年月"].iloc[-1]
    prev_m = monthly_orders["年月"].iloc[-2]

    cur_orders = orders_df[orders_df["年月"] == current_m].groupby("チャネル").agg(
        当月売上=("売上", "sum")
    ).reset_index()
    prev_orders = orders_df[orders_df["年月"] == prev_m].groupby("チャネル").agg(
        前月売上=("売上", "sum")
    ).reset_index()
    cur_ads = ads_df[ads_df["年月"] == current_m].groupby("チャネル").agg(
        ROAS=("ROAS", "mean")
    ).reset_index()

    summary_tbl = cur_orders.merge(prev_orders, on="チャネル").merge(cur_ads, on="チャネル")
    summary_tbl["前月比"] = summary_tbl.apply(
        lambda r: f"{(r['当月売上'] - r['前月売上']) / r['前月売上'] * 100:+.1f}%" if r['前月売上'] != 0 else "N/A",
        axis=1
    )
    summary_tbl["当月売上"] = summary_tbl["当月売上"].apply(lambda x: f"¥{x:,}")
    summary_tbl["ROAS"] = summary_tbl["ROAS"].round(2)
    st.dataframe(summary_tbl[["チャネル", "当月売上", "前月比", "ROAS"]], use_container_width=True)


# ===========================
# タブ2: チャネル別ROIレビュー
# ===========================
with tab2:
    st.subheader("チャネル別ROI詳細")

    cur_ads_detail = ads_df[ads_df["年月"] == current_m].groupby("チャネル").agg(
        当月売上=("売上", "sum"),
        広告費=("広告費", "sum"),
        ROAS=("ROAS", "mean"),
        CV数=("CV数", "sum"),
        CPA=("CPA", "mean"),
    ).reset_index()
    prev_ads_detail = ads_df[ads_df["年月"] == prev_m].groupby("チャネル").agg(
        前月ROAS=("ROAS", "mean"),
        前月売上=("売上", "sum"),
    ).reset_index()

    channel_detail = cur_ads_detail.merge(prev_ads_detail, on="チャネル")
    channel_detail["前月比"] = channel_detail.apply(
        lambda r: f"{(r['当月売上'] - r['前月売上']) / r['前月売上'] * 100:+.1f}%" if r['前月売上'] != 0 else "N/A",
        axis=1
    )
    channel_detail["ROAS"] = channel_detail["ROAS"].round(2)
    channel_detail["前月ROAS"] = channel_detail["前月ROAS"].round(2)
    channel_detail["CPA"] = channel_detail["CPA"].apply(lambda x: f"¥{int(x):,}")

    display_cols = ["チャネル", "当月売上", "広告費", "ROAS", "前月ROAS", "CV数", "CPA", "前月比"]
    fmt_ch = channel_detail.copy()
    fmt_ch["当月売上"] = fmt_ch["当月売上"].apply(lambda x: f"¥{x:,}")
    fmt_ch["広告費"] = fmt_ch["広告費"].apply(lambda x: f"¥{x:,}")
    st.dataframe(fmt_ch[display_cols], use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # チャネル別コメント自動生成
    st.subheader("チャネル別AI診断コメント")
    max_roas_ch = channel_detail.sort_values("ROAS", ascending=False).iloc[0]
    min_roas_ch = channel_detail.sort_values("ROAS").iloc[0]

    for _, row in channel_detail.iterrows():
        comment = generate_channel_comment(row["チャネル"], row["ROAS"], row["前月ROAS"])
        st.markdown(f"""<div class="action-item">{comment}</div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ROAS最大/最小強調
    st.success(f"🏆 最高ROAS: **{max_roas_ch['チャネル']}** (ROAS {max_roas_ch['ROAS']:.2f}) — 予算増配を推奨します。")
    st.warning(f"⚠️ 最低ROAS: **{min_roas_ch['チャネル']}** (ROAS {min_roas_ch['ROAS']:.2f}) — 予算削減または施策改善が急務です。")

    # ROASバーチャート
    st.subheader("チャネル別ROAS比較")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    colors = ["#059669" if r >= 3.0 else "#D97706" if r >= 1.5 else "#DC2626"
              for r in channel_detail["ROAS"]]
    bars = ax2.bar(channel_detail["チャネル"], channel_detail["ROAS"], color=colors, edgecolor="white", linewidth=1.5)
    ax2.axhline(y=1.0, color="#DC2626", linestyle="--", linewidth=1, alpha=0.7, label="損益分岐点 (ROAS=1)")
    ax2.axhline(y=3.0, color="#059669", linestyle="--", linewidth=1, alpha=0.7, label="目標ライン (ROAS=3)")
    for bar, val in zip(bars, channel_detail["ROAS"]):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f"{val:.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax2.set_title("チャネル別ROAS", fontsize=12, color="#065F46", fontweight="bold")
    ax2.set_ylabel("ROAS", fontsize=10)
    ax2.legend(fontsize=9)
    ax2.grid(axis="y", alpha=0.3)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)


# ===========================
# タブ3: 離脱リスク顧客TOP20
# ===========================
with tab3:
    st.subheader(f"離脱リスク高顧客 TOP20（スコア ≥ {risk_threshold}）")

    high_risk_top = high_risk_customers.sort_values("離脱リスクスコア", ascending=False).head(20).copy()
    high_risk_top["推奨アクション"] = high_risk_top.apply(
        lambda r: get_recommended_action(r["RFMセグメント"], r["離脱リスクスコア"]),
        axis=1
    )

    display_risk = high_risk_top[["顧客ID", "年齢層", "RFMセグメント", "累計購入額", "離脱リスクスコア", "推奨アクション"]].copy()
    display_risk["累計購入額"] = display_risk["累計購入額"].apply(lambda x: f"¥{x:,}")
    st.dataframe(display_risk, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # 離脱放置による年間損失額試算
    if len(high_risk_customers) > 0:
        avg_purchase = customers["累計購入額"].mean()
        avg_annual_rate = 2.5  # 年間購入頻度推定
        annual_loss_est = int(len(high_risk_customers) * avg_purchase * avg_annual_rate * 0.3)
        roi_multiple = annual_loss_est // 260000 if annual_loss_est > 0 else 0
        monthly_loss_est = int(annual_loss_est / 12)
        st.markdown(f"""
<div class="highlight-box">
<strong>💸 離脱放置による年間損失額試算</strong><br>
離脱リスク高顧客 <strong>{len(high_risk_customers)}人</strong>が30%流出した場合、<br>
月次損失: <span style="color:#92400E;font-size:1.1rem;font-weight:700;">¥{monthly_loss_est:,}</span>
／ 年間損失: <span style="color:#92400E;font-size:1.3rem;font-weight:700;">¥{annual_loss_est:,}</span><br>
<span style="font-size:0.9rem;color:#64748b;">
💡 <strong>L3プレミアムパック 月額26万円</strong>で離脱防止施策を実行すれば、
投資回収比率 <strong style="color:#059669;">{roi_multiple}倍</strong>（年間換算）。
GA4・Lookerでは顧客ごとの離脱リスクスコアは算出不可。
</span>
</div>
""", unsafe_allow_html=True)

    # RFMセグメント構成円グラフ
    st.subheader("離脱リスク高顧客 RFMセグメント構成")
    rfm_counts = high_risk_customers["RFMセグメント"].value_counts()
    if len(rfm_counts) > 0:
        fig3, ax3 = plt.subplots(figsize=(7, 5))
        colors3 = ["#059669", "#D97706", "#F59E0B", "#EF4444", "#6B7280"]
        wedges, texts, autotexts = ax3.pie(
            rfm_counts.values,
            labels=rfm_counts.index.tolist(),
            autopct="%1.1f%%",
            colors=colors3[:len(rfm_counts)],
            startangle=140,
            pctdistance=0.85
        )
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color("white")
        ax3.set_title("RFMセグメント別構成", fontsize=12, color="#065F46", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)


# ===========================
# タブ4: 次月アクション & レポート
# ===========================
with tab4:
    st.subheader("次月重点アクション（AI自動生成）")
    st.info("💼 **L3 プレミアムパック 月額26万円の伴走支援** — データドリブンな次月アクション3件をAIが自動生成。GA4・Lookerでは見えない「実行すべき施策」を即座に提示します。")

    # 投資対効果サマリーカード
    if len(high_risk_customers) > 0:
        avg_p = customers["累計購入額"].mean()
        annual_loss_for_tab4 = int(len(high_risk_customers) * avg_p * 2.5 * 0.3)
        roi_x = annual_loss_for_tab4 // 260000 if annual_loss_for_tab4 > 0 else 0
        st.markdown(f"""
<div class="highlight-box">
<strong>📊 月額26万円 投資対効果サマリー</strong><br>
年間損失回避額: <span style="color:#92400E;font-size:1.2rem;font-weight:700;">¥{annual_loss_for_tab4:,}</span>
／ 年間投資額: ¥3,120,000（月額26万×12）<br>
<strong style="color:#059669;font-size:1.1rem;">投資回収比率: {roi_x}倍</strong>
— 経営会議に提出できる定量根拠をワンクリックで生成。
</div>
""", unsafe_allow_html=True)

    cur_ads_for_action = ads_df[ads_df["年月"] == current_m].groupby("チャネル").agg(
        ROAS=("ROAS", "mean"),
        広告費=("広告費", "sum"),
    ).reset_index()

    actions = generate_actions(cur_ads_for_action, products, customers, risk_threshold)

    for action in actions:
        st.markdown(f"""<div class="action-item">{action}</div>""", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # レポートダウンロード
    st.subheader("📥 月次レポート全文ダウンロード")

    # チャネルDFを再構築（Markdown用）
    ch_md_df = channel_detail[["チャネル", "当月売上", "前月比", "ROAS"]].copy()

    # 離脱リスクTOP10
    risk_top10 = high_risk_customers.sort_values("離脱リスクスコア", ascending=False).head(10)

    summary_text_for_report = generate_summary(current_rev, prev_rev, current_roas, high_risk_ratio)

    md_report = build_markdown_report(
        summary_text=summary_text_for_report,
        current_rev=current_rev,
        gross_margin=gross_margin,
        current_roas=current_roas,
        high_risk_ratio=high_risk_ratio,
        channel_df=ch_md_df,
        risk_top=risk_top10,
        actions=actions
    )

    st.download_button(
        label="📥 Markdownレポートをダウンロード",
        data=md_report.encode("utf-8"),
        file_name=f"ec_monthly_briefing_2026-04.md",
        mime="text/markdown",
    )

    # プレビュー
    with st.expander("レポートプレビュー（クリックで展開）"):
        st.markdown(md_report)

# ===== フッター =====
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem; padding: 1rem 0;">
EC月次AIブリーフィング | 月額26万円プレミアムパック L3キラー機能<br>
データはサンプルです。実運用では実際のECデータを接続してください。
</div>
""", unsafe_allow_html=True)
