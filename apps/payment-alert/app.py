"""
請求・入金遅延アラートツール
============================
顧問先の入金遅延を可視化し、催促テンプレートを生成するStreamlitアプリ
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from datetime import date

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

# === 定数 ===
ALERT_GREEN = 5    # 0-5日: 正常
ALERT_YELLOW = 15  # 6-15日: 注意
# 16日以上: 危険

def get_status(days):
    if days <= ALERT_GREEN:
        return "🟢 正常"
    elif days <= ALERT_YELLOW:
        return "🟡 注意"
    else:
        return "🔴 危険"

def get_status_color(days):
    if days <= ALERT_GREEN:
        return "#16A34A"
    elif days <= ALERT_YELLOW:
        return "#D97706"
    else:
        return "#DC2626"

def load_csv(path_or_file):
    try:
        if isinstance(path_or_file, str):
            return pd.read_csv(path_or_file, encoding="utf-8-sig")
        return pd.read_csv(path_or_file, encoding="utf-8-sig")
    except Exception:
        try:
            return pd.read_csv(path_or_file, encoding="cp932")
        except Exception:
            return None

def classify_delay(days):
    if days <= ALERT_GREEN:
        return "正常"
    elif days <= ALERT_YELLOW:
        return "一時遅延"
    else:
        return "常習遅延"

def build_alert_df(df, target_month=None):
    """指定月（デフォルト最新月）の顧問先別アラート一覧を構築"""
    if target_month is None:
        target_month = df["請求年月"].max()
    latest = df[df["請求年月"] == target_month].copy()
    latest["ステータス"] = latest["入金遅延日数"].apply(get_status)
    latest["遅延分類"] = latest["入金遅延日数"].apply(classify_delay)

    # --- 催促優先度スコア & 機会損失額 ---
    latest["機会損失額"] = latest["入金遅延日数"] * latest["月額顧問料"]
    # 優先度スコア = 機会損失額を0-100に正規化（最大値ベース）
    max_loss = latest["機会損失額"].max()
    latest["優先度スコア"] = (
        (latest["機会損失額"] / max_loss * 100).round(1) if max_loss > 0 else 0.0
    )

    # --- 遅延パターン分析（常習先 vs 一時的） ---
    # 対象月以前の全データで遅延回数（ALERT_GREEN超）をカウント
    past_data = df[df["請求年月"] <= target_month]
    delay_counts = (
        past_data[past_data["入金遅延日数"] > ALERT_GREEN]
        .groupby("顧問先ID")
        .size()
        .rename("過去遅延回数")
    )
    latest = latest.merge(delay_counts, on="顧問先ID", how="left")
    latest["過去遅延回数"] = latest["過去遅延回数"].fillna(0).astype(int)

    def _delay_pattern(row):
        if row["入金遅延日数"] <= ALERT_GREEN:
            return ""
        if row["過去遅延回数"] >= 3:
            return "⚠️ 常習遅延先"
        elif row["過去遅延回数"] == 1:
            return "🆕 新規遅延"
        else:
            return "📌 要注意"

    latest["遅延パターン"] = latest.apply(_delay_pattern, axis=1)

    # 直近3ヶ月平均遅延
    months = sorted(df["請求年月"].unique())
    target_idx = months.index(target_month) if target_month in months else len(months) - 1
    if target_idx >= 2:
        recent3 = months[target_idx - 2 : target_idx + 1]
        avg3 = (df[df["請求年月"].isin(recent3)]
                .groupby("顧問先ID")["入金遅延日数"]
                .mean()
                .rename("直近3ヶ月平均遅延"))
        latest = latest.merge(avg3, on="顧問先ID", how="left")
        # 悪化傾向フラグ: 直近3ヶ月の最初の月と最後の月の遅延差が5日超なら悪化
        first_month = recent3[0]
        last_month = recent3[-1]
        first_delay = (df[df["請求年月"] == first_month]
                       .set_index("顧問先ID")["入金遅延日数"]
                       .rename("_first"))
        last_delay = (df[df["請求年月"] == last_month]
                      .set_index("顧問先ID")["入金遅延日数"]
                      .rename("_last"))
        trend = pd.concat([first_delay, last_delay], axis=1)
        trend["悪化傾向"] = ((trend["_last"] - trend["_first"]) > 5).map(
            {True: "⚠️ 悪化", False: ""}
        )
        latest = latest.merge(
            trend[["悪化傾向"]], on="顧問先ID", how="left"
        )
        latest["悪化傾向"] = latest["悪化傾向"].fillna("")
    else:
        latest["直近3ヶ月平均遅延"] = latest["入金遅延日数"]
        latest["悪化傾向"] = ""
    return latest, target_month

# === Page Config ===
st.set_page_config(
    page_title="入金遅延アラートツール",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS ===
st.markdown("""
<style>
.alert-hero{text-align:center;padding:28px 0 16px 0;background:linear-gradient(180deg,#FEF2F2,#FFFFFF);border-radius:16px;margin-bottom:12px;}
.alert-hero h1{font-size:2rem;color:#DC2626;}
.alert-hero p{font-size:1.05rem;color:#475569;}
.kpi-card{background:#FEF2F2;border-radius:12px;padding:16px;text-align:center;border:1px solid #FECACA;}
.section-divider{border:none;border-top:2px solid #E2E8F0;margin:24px 0;}
.status-red{color:#DC2626;font-weight:bold;}
.status-yellow{color:#D97706;font-weight:bold;}
.status-green{color:#16A34A;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# === Session State ===
for k, v in {"df": None, "loaded": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === Auto-load sample data ===
if not st.session_state.loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "payment_data.csv")
    if os.path.exists(p):
        st.session_state.df = load_csv(p)
    st.session_state.loaded = True

# === Sidebar ===
st.sidebar.markdown("# 🔴 入金遅延アラート")
st.sidebar.markdown("**顧問先の入金遅延を早期発見・催促を効率化**")
st.sidebar.markdown("---")
st.sidebar.subheader("📁 データアップロード")
uploaded = st.sidebar.file_uploader("請求・入金CSVをアップロード", type=["csv"])
if uploaded:
    df_up = load_csv(uploaded)
    if df_up is not None:
        st.session_state.df = df_up
        st.sidebar.success(f"✅ {len(df_up)}行読込完了")
    else:
        st.sidebar.error("❌ 読込失敗")
st.sidebar.markdown("---")
st.sidebar.markdown("**必須カラム**")
st.sidebar.caption("顧問先ID / 顧問先名 / 月額顧問料 / 請求年月 / 入金遅延日数 / 業種 / 従業員規模")
st.sidebar.markdown("---")
st.sidebar.caption("AI経営パートナー × データサイエンス")
st.sidebar.caption("入金遅延アラート v1.1")

# === Main ===
st.markdown("""
<div class="alert-hero">
<h1>🔴 請求・入金遅延アラートツール</h1>
<p>顧問先の入金遅延を自動検知し、<br>催促メールテンプレートを即座に生成します。</p>
</div>
""", unsafe_allow_html=True)

st.info("💡 **導入効果**: 遅延顧問先の見落としゼロ化 — 毎月の入金確認作業を **2時間→10分**（年間約¥120万相当の工数削減）")

df = st.session_state.df
if df is None:
    st.warning("サイドバーからCSVをアップロードするか、サンプルデータが自動読み込みされるのをお待ちください。")
    st.stop()

# === 月選択 ===
all_months = sorted(df["請求年月"].unique())
selected_month = st.selectbox(
    "📅 表示月を選択",
    all_months,
    index=len(all_months) - 1,
)

# === KPIカード ===
latest_df = df[df["請求年月"] == selected_month].copy()

n_total = len(latest_df)
n_danger = (latest_df["入金遅延日数"] > ALERT_YELLOW).sum()
n_warning = ((latest_df["入金遅延日数"] > ALERT_GREEN) & (latest_df["入金遅延日数"] <= ALERT_YELLOW)).sum()
total_overdue = latest_df[latest_df["入金遅延日数"] > ALERT_GREEN]["月額顧問料"].sum()
avg_delay = latest_df[latest_df["入金遅延日数"] > 0]["入金遅延日数"].mean()

# 前月比delta計算
sel_idx = all_months.index(selected_month)
if sel_idx > 0:
    prev_month = all_months[sel_idx - 1]
    prev_df = df[df["請求年月"] == prev_month]
    prev_danger = (prev_df["入金遅延日数"] > ALERT_YELLOW).sum()
    prev_warning = ((prev_df["入金遅延日数"] > ALERT_GREEN) & (prev_df["入金遅延日数"] <= ALERT_YELLOW)).sum()
    delta_danger = int(n_danger - prev_danger)
    delta_warning = int(n_warning - prev_warning)
    delta_danger_str = f"前月比 {'+' if delta_danger >= 0 else ''}{delta_danger}"
    delta_warning_str = f"前月比 {'+' if delta_warning >= 0 else ''}{delta_warning}"
else:
    delta_danger_str = f"全{n_total}件中"
    delta_warning_str = f"全{n_total}件中"
    delta_danger = None
    delta_warning = None

kc1, kc2, kc3, kc4 = st.columns(4)
kc1.metric("🔴 危険（16日以上）", f"{n_danger}件", delta_danger_str,
           delta_color="inverse" if delta_danger is not None else "off")
kc2.metric("🟡 注意（6-15日）", f"{n_warning}件", delta_warning_str,
           delta_color="inverse" if delta_warning is not None else "off")
kc3.metric("💰 遅延中の顧問料合計", f"¥{total_overdue:,.0f}", "注意+危険のみ")
kc4.metric("📅 平均遅延日数", f"{avg_delay:.1f}日" if not np.isnan(avg_delay) else "0.0日", "遅延あり顧問先")

# === 遅延パターンKPIカード ===
_alert_for_kpi, _ = build_alert_df(df, target_month=selected_month)
_delayed = _alert_for_kpi[_alert_for_kpi["入金遅延日数"] > ALERT_GREEN]
n_habitual = (_delayed["遅延パターン"] == "⚠️ 常習遅延先").sum()
n_new_delay = (_delayed["遅延パターン"] == "🆕 新規遅延").sum()
n_watch = (_delayed["遅延パターン"] == "📌 要注意").sum()

pk1, pk2, pk3 = st.columns(3)
pk1.metric("⚠️ 常習遅延先", f"{n_habitual}件", "過去3回以上遅延")
pk2.metric("🆕 新規遅延", f"{n_new_delay}件", "今回が初の遅延")
pk3.metric("📌 要注意", f"{n_watch}件", "過去2回目の遅延")

# === 冒頭インサイト1行 ===
if len(_delayed) > 0:
    _top = _delayed.nlargest(1, "機会損失額").iloc[0]
    _top_name = _top["顧問先名"]
    _top_days = int(_top["入金遅延日数"])
    _top_loss = _top["機会損失額"]
    _top_pattern = _top["遅延パターン"]
    _loss_str = f"¥{_top_loss / 10000:,.1f}万" if _top_loss >= 10000 else f"¥{_top_loss:,.0f}"
    _pattern_note = "常習遅延先のため早急な対応を推奨" if "常習" in _top_pattern else "遅延拡大前の早期対応を推奨"
    st.warning(f"⚡ 今月の最優先: **{_top_name}** — 遅延{_top_days}日・機会損失{_loss_str}。{_pattern_note}")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === タブ ===
tab1, tab2, tab3 = st.tabs(["📋 アラート一覧", "📊 遅延パターン分析", "✉️ 催促テンプレート"])

# ─────────────────────────────────────────
with tab1:
    st.header(f"📋 アラート一覧 — {selected_month}")

    alert_df, _ = build_alert_df(df, target_month=selected_month)

    # フィルター
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        status_filter = st.multiselect(
            "ステータスで絞込",
            ["🔴 危険", "🟡 注意", "🟢 正常"],
            default=["🔴 危険", "🟡 注意"]
        )
    with col_f2:
        industry_filter = st.multiselect(
            "業種で絞込",
            sorted(alert_df["業種"].unique()),
            default=[]
        )

    filtered = alert_df.copy()
    if status_filter:
        filtered = filtered[filtered["ステータス"].isin(status_filter)]
    if industry_filter:
        filtered = filtered[filtered["業種"].isin(industry_filter)]

    # ソート選択
    sort_col = st.radio(
        "並び順",
        ["優先度スコア（高→低）", "遅延日数（多→少）", "機会損失額（高→低）"],
        horizontal=True,
    )
    sort_map = {
        "優先度スコア（高→低）": "優先度スコア",
        "遅延日数（多→少）": "入金遅延日数",
        "機会損失額（高→低）": "機会損失額",
    }
    sort_key = sort_map[sort_col]

    # TOP10 要注意先
    st.subheader("🚨 TOP10 要注意先（優先度順）")
    top10_cols = ["ステータス", "顧問先名", "優先度スコア", "機会損失額", "入金遅延日数", "月額顧問料", "遅延パターン", "業種", "悪化傾向"]
    top10 = alert_df.nlargest(10, sort_key)[top10_cols]
    # 機会損失額を見やすくフォーマット
    top10_display = top10.copy()
    top10_display["機会損失額"] = top10_display["機会損失額"].apply(lambda x: f"¥{x:,.0f}")
    st.dataframe(top10_display.reset_index(drop=True), use_container_width=True, hide_index=True)

    st.markdown("---")
    filtered_sorted = filtered.sort_values(sort_key, ascending=False)
    st.subheader(f"📋 全顧問先アラート一覧（{len(filtered_sorted)}件）")
    show_cols = ["ステータス", "顧問先名", "優先度スコア", "機会損失額", "入金遅延日数", "月額顧問料", "遅延パターン", "業種", "従業員規模", "悪化傾向"]
    if "直近3ヶ月平均遅延" in filtered_sorted.columns:
        show_cols.insert(6, "直近3ヶ月平均遅延")
    all_display = filtered_sorted[show_cols].copy()
    all_display["機会損失額"] = all_display["機会損失額"].apply(lambda x: f"¥{x:,.0f}")
    st.dataframe(all_display.reset_index(drop=True), use_container_width=True, hide_index=True)

    # CSVダウンロード
    csv_data = filtered_sorted[show_cols].to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "📥 アラート一覧をCSVダウンロード",
        csv_data,
        f"payment_alert_{selected_month}.csv",
        "text/csv",
        use_container_width=True
    )

# ─────────────────────────────────────────
with tab2:
    st.header("📊 遅延パターン分析")
    setup_japanese_font()

    col_l, col_r = st.columns(2)

    # 左: 遅延分類の円グラフ（最新月）
    with col_l:
        st.subheader("遅延分類（最新月）")
        latest_df["遅延分類"] = latest_df["入金遅延日数"].apply(classify_delay)
        dist = latest_df["遅延分類"].value_counts()
        colors_pie = {"正常": "#16A34A", "一時遅延": "#D97706", "常習遅延": "#DC2626"}
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        pie_colors = [colors_pie.get(k, "#94A3B8") for k in dist.index]
        wedges, texts, autotexts = ax1.pie(
            dist.values,
            labels=dist.index,
            autopct="%1.1f%%",
            colors=pie_colors,
            startangle=90,
            textprops={"fontsize": 11}
        )
        ax1.set_title(f"遅延分類内訳（{selected_month}）", fontsize=12, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        # 分類内訳テーブル
        dist_df = dist.reset_index()
        dist_df.columns = ["遅延分類", "件数"]
        dist_df["割合"] = (dist_df["件数"] / dist_df["件数"].sum() * 100).round(1).astype(str) + "%"
        st.dataframe(dist_df, use_container_width=True, hide_index=True)

    # 右: 月次遅延推移（全顧問先の平均）
    with col_r:
        st.subheader("月別 平均遅延日数推移")
        monthly_avg = df.groupby("請求年月")["入金遅延日数"].mean().reset_index()
        monthly_avg.columns = ["月", "平均遅延日数"]
        monthly_danger = df[df["入金遅延日数"] > ALERT_YELLOW].groupby("請求年月").size().reset_index(name="危険件数")

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        months_list = monthly_avg["月"].tolist()
        ax2.plot(range(len(months_list)), monthly_avg["平均遅延日数"].values,
                 color="#DC2626", linewidth=2.5, marker="o", markersize=6, label="平均遅延日数")
        ax2.axhline(y=ALERT_GREEN, color="#16A34A", linestyle="--", alpha=0.6, label=f"正常基準({ALERT_GREEN}日)")
        ax2.axhline(y=ALERT_YELLOW, color="#D97706", linestyle="--", alpha=0.6, label=f"注意基準({ALERT_YELLOW}日)")
        ax2.set_xticks(range(len(months_list)))
        ax2.set_xticklabels([m[-3:] for m in months_list], fontsize=8, rotation=45)
        ax2.set_ylabel("平均遅延日数")
        ax2.set_title("月別 平均遅延日数推移", fontsize=12, fontweight="bold")
        ax2.legend(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # 業種別遅延分析
    st.subheader("業種別 平均遅延日数（最新月）")
    by_industry = (latest_df.groupby("業種")["入金遅延日数"]
                   .agg(["mean", "max", "count"])
                   .reset_index()
                   .rename(columns={"mean": "平均遅延", "max": "最大遅延", "count": "件数"}))
    by_industry["平均遅延"] = by_industry["平均遅延"].round(1)
    by_industry = by_industry.sort_values("平均遅延", ascending=False)

    fig3, ax3 = plt.subplots(figsize=(10, 3.5))
    bar_colors = [("#DC2626" if v > ALERT_YELLOW else "#D97706" if v > ALERT_GREEN else "#16A34A")
                  for v in by_industry["平均遅延"]]
    ax3.barh(by_industry["業種"], by_industry["平均遅延"], color=bar_colors, alpha=0.85)
    ax3.axvline(x=ALERT_GREEN, color="#16A34A", linestyle="--", alpha=0.6)
    ax3.axvline(x=ALERT_YELLOW, color="#D97706", linestyle="--", alpha=0.6)
    ax3.set_xlabel("平均遅延日数")
    ax3.set_title("業種別 平均遅延日数", fontsize=12, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

# ─────────────────────────────────────────
with tab3:
    st.header("✉️ 催促テンプレート")
    st.markdown("遅延状況に応じた3段階の催促メールテンプレートを生成します。")

    # 顧問先選択（要注意先から）
    danger_clients = alert_df[alert_df["入金遅延日数"] > ALERT_GREEN].sort_values("入金遅延日数", ascending=False)

    if len(danger_clients) == 0:
        st.success("🟢 現在、遅延中の顧問先はありません。")
    else:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            selected_client = st.selectbox(
                "対象顧問先を選択",
                danger_clients["顧問先名"].tolist()
            )
        client_row = danger_clients[danger_clients["顧問先名"] == selected_client].iloc[0]
        delay_days = int(client_row["入金遅延日数"])
        fee = int(client_row["月額顧問料"])
        month = selected_month

        with col_s2:
            office_name = st.text_input("事務所名", value="〇〇税理士事務所")

        # 段階判定
        if delay_days <= 10:
            stage = 1
            stage_label = "初回リマインド"
        elif delay_days <= 20:
            stage = 2
            stage_label = "2回目督促"
        else:
            stage = 3
            stage_label = "最終通告"

        st.markdown(f"**遅延日数: {delay_days}日 → 段階: {stage_label}（{get_status(delay_days)}）**")

        # テンプレート表示（3段階すべて）
        templates = {
            1: {
                "label": "📧 初回リマインド（遅延10日以内）",
                "color": "#D97706",
                "body": f"""件名：{month}分 顧問料ご入金のご確認

{selected_client} 御中

いつも大変お世話になっております。{office_name}でございます。

{month}分の月額顧問料（¥{fee:,}）につきまして、まだご入金が確認できておりません。
ご多忙のところ恐れ入りますが、お早めにご対応いただけますと幸いです。

ご不明な点がございましたら、お気軽にお問い合わせください。

よろしくお願い申し上げます。

{office_name}
""",
            },
            2: {
                "label": "📧 2回目督促（遅延11-20日）",
                "color": "#EA580C",
                "body": f"""件名：【重要】{month}分 顧問料 お支払いのお願い

{selected_client} 御中

いつもお世話になっております。{office_name}でございます。

先日もご連絡申し上げましたが、{month}分の月額顧問料（¥{fee:,}）のご入金が確認できておりません（現在 {delay_days}日経過）。

お忙しいところ恐れ入りますが、今週中にご対応いただけますよう、何卒よろしくお願い申し上げます。

ご入金が確認でき次第、本メールは無効となります。
すでにお手続き済みの場合は、行き違いをお詫び申し上げます。

{office_name}
""",
            },
            3: {
                "label": "📧 最終通告（遅延21日以上）",
                "color": "#DC2626",
                "body": f"""件名：【最終ご通知】{month}分 顧問料 早急なご対応のお願い

{selected_client} 御中

{office_name}でございます。

{month}分の月額顧問料（¥{fee:,}）につきまして、現在 {delay_days}日 が経過しておりますが、いまだご入金が確認できておりません。

誠に恐れ入りますが、○月○日までにご入金いただけない場合、顧問契約の継続につきまして改めてご相談させていただく場合がございます。

ご事情がある場合は、ご遠慮なくご連絡ください。早急なご返答をお願い申し上げます。

{office_name}
担当: 　　　　　TEL:
""",
            },
        }

        # 自動選択段階を先に表示
        rec = templates[stage]
        st.markdown(f"### ✅ 推奨テンプレート: {rec['label']}")
        st.text_area(f"テンプレート（コピーしてご使用ください）", rec["body"], height=250, key=f"tpl_rec")
        st.download_button(
            f"📥 {rec['label']}をダウンロード",
            rec["body"],
            f"催促メール_{selected_client}_{stage_label}.txt",
            "text/plain",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("### 📋 全段階テンプレート一覧")
        for s in [1, 2, 3]:
            t = templates[s]
            with st.expander(t["label"]):
                st.text_area("テンプレート", t["body"], height=220, key=f"tpl_{s}")
                st.download_button(
                    f"📥 ダウンロード",
                    t["body"],
                    f"催促メール_{s}段階.txt",
                    "text/plain",
                    key=f"dl_{s}"
                )

# === 定期運用チェックリスト ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 📋 定期運用チェックリスト")
with st.expander("週次チェック"):
    st.markdown("- □ 遅延一覧の確認・催促実施\n- □ 常習遅延先の対応状況確認")
with st.expander("月次チェック"):
    st.markdown("- □ 遅延パターン分析の更新\n- □ 機会損失額の累計確認")

# === 関連ツールカード（3列） ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1, fc2, fc3 = st.columns(3)
fc1.markdown("📊 **月次レポート自動生成**  \n試算表CSV→レポート自動作成  \n[▶ ツールを開く](https://shigyou-report.streamlit.app)")
fc2.markdown("🏢 **離反予測**  \n顧問先の離反リスクをAI予測  \n[▶ ツールを開く](https://shigyou-churn.streamlit.app)")
fc3.markdown("🏠 **士業ポータル**  \nAI経営パートナー総合メニュー  \n[▶ ツールを開く](https://shigyou-ai-tools.streamlit.app)")
st.caption("AI経営パートナー × データサイエンス | 入金遅延アラート v1.1")
