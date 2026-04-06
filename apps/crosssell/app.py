"""
顧問先クロスセル分析ツール
===========================
顧問先のサービス利用状況から未利用サービスを推奨し、
推定増収額を算出するStreamlitアプリ
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

# === サービスカタログ ===
SERVICES = {
    "記帳代行":    30000,
    "給与計算":    20000,
    "年末調整":    15000,
    "社保手続き":  20000,
    "助成金申請":  50000,
    "経営計画策定": 30000,
    "M&A支援":   100000,
    "IT導入支援":  30000,
}
SERVICE_NAMES = list(SERVICES.keys())

# === 業種別アドバイス ===
INDUSTRY_ADVICE = {
    "製造業": "原価管理強化→経営計画策定の提案が効果的",
    "IT業": "IT導入支援＋助成金申請のセット提案が有効",
    "医療・介護": "社保手続き＋給与計算の一括受託で工数削減を訴求",
    "建設業": "助成金申請＋社保手続きで法令遵守と資金確保を同時提案",
    "飲食業": "記帳代行＋給与計算のセットで日常業務の負担軽減を訴求",
    "小売業": "記帳代行＋経営計画策定で売上分析と資金繰り改善を提案",
    "不動産業": "M&A支援＋経営計画策定で資産活用の最適化を提案",
    "サービス業": "給与計算＋社保手続きの一括受託で管理部門のコスト削減を訴求",
}

# === サービス別効果フレーズ ===
SERVICE_EFFECTS = {
    "記帳代行": "経理業務の工数を月20時間削減",
    "給与計算": "給与計算ミスによるトラブルをゼロ化",
    "年末調整": "年末調整業務の工数を大幅削減し、届出漏れを防止",
    "社保手続き": "届出漏れ・手続きミスを完全防止",
    "助成金申請": "平均100〜300万円の助成金を獲得",
    "経営計画策定": "融資審査の通過率が大幅向上",
    "M&A支援": "事業承継・譲渡をスムーズに実現し企業価値を最大化",
    "IT導入支援": "IT導入補助金を活用し実質負担を1/2に",
}

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

# ============================================================
# Step 6-2: 分析ロジック
# ============================================================

def detect_service_columns(df):
    """データフレームからサービス列を自動検出"""
    return [c for c in SERVICE_NAMES if c in df.columns]

def calc_cooccurrence(df, service_cols):
    """
    サービス間の共起分析
    Returns: support_df(サービス単体の利用率), lift_df(サービス間のlift値)
    """
    n = len(df)
    svc_data = df[service_cols].values.astype(float)

    # support: 各サービスの利用率
    support = {svc: svc_data[:, i].mean() for i, svc in enumerate(service_cols)}

    # confidence & lift: サービスA → サービスB
    # confidence(A→B) = P(AかつB) / P(A)
    # lift(A→B) = confidence / P(B)
    lift_matrix = pd.DataFrame(1.0, index=service_cols, columns=service_cols)
    confidence_matrix = pd.DataFrame(0.0, index=service_cols, columns=service_cols)
    cooc_matrix = pd.DataFrame(0.0, index=service_cols, columns=service_cols)

    for i, svc_a in enumerate(service_cols):
        for j, svc_b in enumerate(service_cols):
            if i == j:
                continue
            a_mask = svc_data[:, i] == 1
            if a_mask.sum() == 0:
                continue
            p_ab = ((svc_data[:, i] == 1) & (svc_data[:, j] == 1)).mean()
            p_a = svc_data[:, i].mean()
            p_b = svc_data[:, j].mean()
            cooc = p_ab
            conf = p_ab / p_a if p_a > 0 else 0.0
            lift = conf / p_b if p_b > 0 else 1.0
            cooc_matrix.loc[svc_a, svc_b] = round(cooc, 3)
            confidence_matrix.loc[svc_a, svc_b] = round(conf, 3)
            lift_matrix.loc[svc_a, svc_b] = round(lift, 3)

    return support, cooc_matrix, confidence_matrix, lift_matrix

def calc_recommendations(df, service_cols, confidence_matrix, support):
    """
    顧問先ごとの推奨サービス計算
    未利用サービスのうち、confidence（既存サービスとの共起率）が高いものをランキング
    推定増収額 = 単価 × 平均confidence
    """
    rows = []
    for _, client in df.iterrows():
        using = [s for s in service_cols if client.get(s, 0) == 1]
        not_using = [s for s in service_cols if client.get(s, 0) == 0]

        for target_svc in not_using:
            if not using:
                avg_conf = support.get(target_svc, 0.1)
            else:
                confs = [confidence_matrix.loc[s, target_svc] for s in using
                         if s in confidence_matrix.index and target_svc in confidence_matrix.columns]
                avg_conf = np.mean(confs) if confs else support.get(target_svc, 0.1)

            unit_price = SERVICES.get(target_svc, 30000)
            expected_revenue = int(unit_price * avg_conf)

            rows.append({
                "顧問先ID": client.get("顧問先ID", ""),
                "顧問先名": client.get("顧問先名", ""),
                "業種": client.get("業種", ""),
                "従業員規模": client.get("従業員規模", ""),
                "月額顧問料": client.get("月額顧問料", 0),
                "推奨サービス": target_svc,
                "単価（月額）": unit_price,
                "Confidence": round(avg_conf, 3),
                "推定月間増収額": expected_revenue,
                "推定年間増収額": expected_revenue * 12,
            })

    rec_df = pd.DataFrame(rows)
    if len(rec_df) == 0:
        return rec_df
    # 顧問先ごとにTop3に絞る
    rec_df = (rec_df.sort_values(["顧問先ID", "推定月間増収額"], ascending=[True, False])
              .groupby("顧問先ID").head(3)
              .reset_index(drop=True))

    # 提案優先度ランク（A/B/C）
    def _priority(row):
        if row["Confidence"] >= 0.6 and row["推定年間増収額"] >= 300000:
            return "A（高）"
        elif row["Confidence"] >= 0.4 or row["推定年間増収額"] >= 150000:
            return "B（中）"
        else:
            return "C（低）"
    rec_df["優先度"] = rec_df.apply(_priority, axis=1)

    return rec_df

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="クロスセル分析ツール",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.crosssell-hero{text-align:center;padding:28px 0 16px 0;background:linear-gradient(180deg,#FFFBEB,#FFFFFF);border-radius:16px;margin-bottom:12px;}
.crosssell-hero h1{font-size:2rem;color:#D97706;}
.crosssell-hero p{font-size:1.05rem;color:#475569;}
.section-divider{border:none;border-top:2px solid #E2E8F0;margin:24px 0;}
.kpi-value{font-size:2.4rem;font-weight:700;}.effect-banner{display:flex;gap:12px;margin-bottom:16px;}.effect-card{flex:1;border-radius:12px;padding:14px 12px;text-align:center;font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Session State
# ============================================================
for k, v in {"df": None, "loaded": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-load sample data
if not st.session_state.loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "crosssell_data.csv")
    if os.path.exists(p):
        st.session_state.df = load_csv(p)
    st.session_state.loaded = True

# ============================================================
# Sidebar
# ============================================================
st.sidebar.markdown("# 💰 クロスセル分析")
st.sidebar.markdown("**顧問先への追加提案機会を発見**")
st.sidebar.markdown("---")
st.sidebar.subheader("📁 データアップロード")
uploaded = st.sidebar.file_uploader("顧問先×サービスCSVをアップロード", type=["csv"])
if uploaded:
    df_up = load_csv(uploaded)
    if df_up is not None:
        st.session_state.df = df_up
        st.sidebar.success(f"✅ {len(df_up)}件読込完了")
    else:
        st.sidebar.error("❌ 読込失敗")
st.sidebar.markdown("---")
st.sidebar.markdown("**期待カラム**")
st.sidebar.caption("顧問先ID / 顧問先名 / 月額顧問料 / 業種 / 従業員規模 / 契約年数 / [サービス名(0/1)]...")
st.sidebar.markdown("---")
st.sidebar.caption("AI経営パートナー × データサイエンス")
st.sidebar.caption("クロスセル分析 v1.0")

# ============================================================
# Main
# ============================================================
st.markdown("""
<div class="crosssell-hero">
<h1>💰 顧問先への追加提案、機会損失していませんか？</h1>
<p>AIが各顧問先の未導入サービスを分析。月1件の追加契約で年間¥120万の増収。</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="effect-banner">
<div class="effect-card" style="background:#FEF3C7;border:1px solid #FDE68A;">
<div style="font-size:1.1rem;font-weight:700;color:#92400E;margin-bottom:4px;">Before</div>
<div style="color:#78350F;">提案は担当者の勘と経験</div>
</div>
<div class="effect-card" style="background:#DBEAFE;border:1px solid #BFDBFE;">
<div style="font-size:1.1rem;font-weight:700;color:#1E40AF;margin-bottom:4px;">After</div>
<div style="color:#1E3A8A;">AI優先度スコアで提案先を自動選定</div>
</div>
<div class="effect-card" style="background:#D1FAE5;border:1px solid #A7F3D0;">
<div style="font-size:1.1rem;font-weight:700;color:#065F46;margin-bottom:4px;">年間効果</div>
<div style="color:#064E3B;font-weight:600;">顧問単価20%UP</div>
</div>
</div>
""", unsafe_allow_html=True)

df = st.session_state.df
if df is None:
    st.warning("サイドバーからCSVをアップロードするか、サンプルデータが自動読み込みされるのをお待ちください。")
    st.stop()

# サービス列の検出
svc_cols = detect_service_columns(df)
if not svc_cols:
    st.error("データにサービス列が見つかりません。サービス名（記帳代行、給与計算など）の列が必要です。")
    st.stop()

# 分析実行
support, cooc_matrix, confidence_matrix, lift_matrix = calc_cooccurrence(df, svc_cols)
rec_df = calc_recommendations(df, svc_cols, confidence_matrix, support)

# KPIカード
n_clients = len(df)
n_cs_clients = rec_df["顧問先ID"].nunique() if len(rec_df) > 0 else 0
total_annual = rec_df["推定年間増収額"].sum() if len(rec_df) > 0 else 0
avg_recs = rec_df.groupby("顧問先ID").size().mean() if len(rec_df) > 0 else 0

avg_unit_price = rec_df["単価（月額）"].mean() if len(rec_df) > 0 else 0

kc1, kc2, kc3, kc4 = st.columns(4)
kc1.metric("🎯 クロスセル対象顧問先数", f"{n_cs_clients}件", f"全{n_clients}件中")
kc2.metric("💰 推定年間増収額（合計）", f"¥{total_annual:,.0f}")
kc3.metric("📊 平均推奨サービス数", f"{avg_recs:.1f}件/顧問先")
kc4.metric("💵 平均提案単価", f"¥{avg_unit_price:,.0f}/月")

# 冒頭インサイト: クロスセル最優先顧問先
if len(rec_df) > 0:
    _top = rec_df.sort_values("推定年間増収額", ascending=False).iloc[0]
    st.markdown(
        f"⚡ **クロスセル最優先: {_top['顧問先名']}** — "
        f"推定追加売上 **¥{int(_top['推定年間増収額']):,}** /年"
        f"（推奨: {_top['推奨サービス']}）"
    )

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ============================================================
# Step 6-3: UI（4タブ）
# ============================================================
setup_japanese_font()

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 クロスセル機会一覧",
    "🔥 サービス共起分析",
    "📈 事務所全体インパクト",
    "📊 データプレビュー"
])

# ─────────────────────────────────────────
with tab1:
    st.header("🎯 クロスセル機会一覧")
    st.markdown("顧問先ごとの推奨サービスと推定増収額を表示します（Top3まで）。")

    if len(rec_df) == 0:
        st.info("推奨サービスが計算できませんでした。")
    else:
        # フィルター
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            min_revenue = st.slider(
                "推定年間増収額（下限）",
                min_value=0,
                max_value=int(rec_df["推定年間増収額"].max()),
                value=0,
                step=10000,
                format="¥%d"
            )
        with col_f2:
            svc_filter = st.multiselect(
                "推奨サービスで絞込",
                svc_cols,
                default=[]
            )
        with col_f3:
            industry_list = sorted(rec_df["業種"].dropna().unique().tolist())
            industry_filter = st.multiselect(
                "業種で絞込",
                industry_list,
                default=[]
            )
        with col_f4:
            priority_options = ["A（高）", "B（中）", "C（低）"]
            priority_filter = st.multiselect(
                "優先度で絞込",
                priority_options,
                default=[]
            )

        filtered_rec = rec_df[rec_df["推定年間増収額"] >= min_revenue]
        if svc_filter:
            filtered_rec = filtered_rec[filtered_rec["推奨サービス"].isin(svc_filter)]
        if industry_filter:
            filtered_rec = filtered_rec[filtered_rec["業種"].isin(industry_filter)]
        if priority_filter:
            filtered_rec = filtered_rec[filtered_rec["優先度"].isin(priority_filter)]

        st.markdown(f"**{len(filtered_rec)}件** の提案機会")
        show_cols = ["顧問先名", "業種", "推奨サービス", "優先度", "単価（月額）", "Confidence", "推定月間増収額", "推定年間増収額"]
        st.dataframe(
            filtered_rec[show_cols].sort_values("推定年間増収額", ascending=False).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_rec[show_cols].to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 クロスセル機会リストをCSVダウンロード",
            csv_data,
            "crosssell_opportunities.csv",
            "text/csv",
            use_container_width=True
        )

        # ─────────────────────────────────────────
        # 顧問先個別カルテ
        # ─────────────────────────────────────────
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.subheader("📋 顧問先個別カルテ")

        client_names = sorted(df["顧問先名"].dropna().unique().tolist()) if "顧問先名" in df.columns else []
        if client_names:
            selected_client = st.selectbox("顧問先を選択", client_names, key="client_card_select")

            client_row = df[df["顧問先名"] == selected_client].iloc[0]
            client_industry = client_row.get("業種", "不明")

            # 利用中サービス / 未利用サービス
            using_svcs = [s for s in svc_cols if client_row.get(s, 0) == 1]
            not_using_svcs = [s for s in svc_cols if client_row.get(s, 0) == 0]

            col_card1, col_card2 = st.columns(2)
            with col_card1:
                st.markdown("**現在利用中のサービス**")
                if using_svcs:
                    for s in using_svcs:
                        st.markdown(f"- ✅ {s}")
                else:
                    st.caption("利用中のサービスはありません")

            with col_card2:
                st.markdown("**未利用サービス＋推奨スコア**")
                client_recs = rec_df[rec_df["顧問先名"] == selected_client].sort_values("Confidence", ascending=False)
                if len(client_recs) > 0:
                    for _, r in client_recs.iterrows():
                        st.markdown(
                            f"- 🔹 {r['推奨サービス']}（Confidence: {r['Confidence']:.3f} / "
                            f"優先度: {r['優先度']}）"
                        )
                else:
                    st.caption("推奨サービスはありません")

            # 推定年間増収額合計
            client_annual_total = int(client_recs["推定年間増収額"].sum()) if len(client_recs) > 0 else 0
            st.metric("この顧問先の推定年間増収額合計", f"¥{client_annual_total:,.0f}")

            # 業種に応じたワンポイントアドバイス
            advice = INDUSTRY_ADVICE.get(client_industry, "複数サービスのセット提案で顧問先の業務効率化を訴求")
            st.info(f"💡 **この顧問先への提案ポイント**（{client_industry}）: {advice}")

            # ─────────────────────────────────────────
            # 提案トークスクリプト
            # ─────────────────────────────────────────
            if len(client_recs) > 0:
                if st.button("📝 提案トークスクリプトを生成", key="talk_script_btn"):
                    st.markdown("---")
                    st.markdown("#### 提案トークスクリプト")
                    for _, r in client_recs.iterrows():
                        svc_name = r["推奨サービス"]
                        unit_price = r["単価（月額）"]
                        effect = SERVICE_EFFECTS.get(svc_name, "業務効率の大幅な改善")
                        script = (
                            f"「{selected_client}様、いつもお世話になっております。\n"
                            f"御社と同じ{client_industry}のお客様で、{svc_name}を導入された事務所では、\n"
                            f"月額{unit_price:,}円で{effect}という成果が出ております。\n"
                            f"一度お話の機会をいただけないでしょうか。」"
                        )
                        st.text_area(
                            f"{svc_name}（優先度: {r['優先度']}）",
                            value=script,
                            height=130,
                            key=f"script_{selected_client}_{svc_name}"
                        )

# ─────────────────────────────────────────
with tab2:
    st.header("🔥 サービス共起分析（Liftヒートマップ）")
    st.markdown("Lift値 > 1.0 = 同時利用されやすい組み合わせ。数値が大きいほど強いクロスセル機会。")

    fig_hm, ax_hm = plt.subplots(figsize=(9, 7))
    lift_data = lift_matrix.loc[svc_cols, svc_cols].values.astype(float)
    # 対角を0に（自己比較を除外）
    np.fill_diagonal(lift_data, np.nan)

    im = ax_hm.imshow(lift_data, cmap="YlOrRd", aspect="auto", vmin=0.5, vmax=2.0)
    ax_hm.set_xticks(range(len(svc_cols)))
    ax_hm.set_yticks(range(len(svc_cols)))
    ax_hm.set_xticklabels(svc_cols, rotation=45, ha="right", fontsize=9)
    ax_hm.set_yticklabels(svc_cols, fontsize=9)
    ax_hm.set_title("サービス間 Lift値ヒートマップ\n（行→列の方向で解釈: 行サービス利用者が列サービスも利用する確率）",
                     fontsize=11, fontweight="bold")
    plt.colorbar(im, ax=ax_hm, label="Lift値")

    # 数値を表示
    for i in range(len(svc_cols)):
        for j in range(len(svc_cols)):
            if i != j and not np.isnan(lift_data[i, j]):
                ax_hm.text(j, i, f"{lift_data[i,j]:.2f}",
                           ha="center", va="center", fontsize=7.5,
                           color="black" if lift_data[i, j] < 1.5 else "white")
    plt.tight_layout()
    st.pyplot(fig_hm)
    plt.close(fig_hm)

    # Top組み合わせテーブル
    st.subheader("🔗 Lift値 TOP10 組み合わせ")
    lift_pairs = []
    for i, svc_a in enumerate(svc_cols):
        for j, svc_b in enumerate(svc_cols):
            if i < j:
                lift_val = lift_matrix.loc[svc_a, svc_b]
                conf_ab = confidence_matrix.loc[svc_a, svc_b]
                conf_ba = confidence_matrix.loc[svc_b, svc_a]
                lift_pairs.append({
                    "サービスA": svc_a,
                    "サービスB": svc_b,
                    "Lift": round(float(lift_val), 3),
                    "Confidence A→B": round(float(conf_ab), 3),
                    "Confidence B→A": round(float(conf_ba), 3),
                })
    lift_pairs_df = pd.DataFrame(lift_pairs).sort_values("Lift", ascending=False).head(10)
    st.dataframe(lift_pairs_df.reset_index(drop=True), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────
with tab3:
    st.header("📈 事務所全体インパクト")

    if len(rec_df) > 0:
        # サービス別 集計
        by_svc = (rec_df.groupby("推奨サービス")
                  .agg(
                      対象顧問先数=("顧問先ID", "nunique"),
                      推定年間増収額合計=("推定年間増収額", "sum"),
                      平均Confidence=("Confidence", "mean")
                  )
                  .reset_index()
                  .sort_values("推定年間増収額合計", ascending=False))
        by_svc["単価（月額）"] = by_svc["推奨サービス"].map(SERVICES)
        by_svc["平均Confidence"] = by_svc["平均Confidence"].round(3)

        col_l, col_r = st.columns(2)

        with col_l:
            st.subheader("サービス別 推定年間増収額")
            fig_bar, ax_bar = plt.subplots(figsize=(6, 4.5))
            colors_bar = ["#D97706" if i == 0 else "#FCD34D" for i in range(len(by_svc))]
            ax_bar.barh(by_svc["推奨サービス"], by_svc["推定年間増収額合計"] / 10000,
                        color=colors_bar, alpha=0.85)
            ax_bar.set_xlabel("推定年間増収額（万円）")
            ax_bar.set_title("サービス別 推定年間増収額", fontsize=11, fontweight="bold")
            plt.tight_layout()
            st.pyplot(fig_bar)
            plt.close(fig_bar)

        with col_r:
            st.subheader("サービス別 対象顧問先数")
            fig_bar2, ax_bar2 = plt.subplots(figsize=(6, 4.5))
            ax_bar2.barh(by_svc["推奨サービス"], by_svc["対象顧問先数"], color="#0891B2", alpha=0.75)
            ax_bar2.set_xlabel("対象顧問先数（件）")
            ax_bar2.set_title("サービス別 クロスセル対象顧問先数", fontsize=11, fontweight="bold")
            plt.tight_layout()
            st.pyplot(fig_bar2)
            plt.close(fig_bar2)

        # サマリーテーブル
        st.subheader("📊 サービス別インパクトサマリー")
        by_svc_disp = by_svc.copy()
        by_svc_disp["推定年間増収額合計"] = by_svc_disp["推定年間増収額合計"].apply(lambda x: f"¥{x:,.0f}")
        by_svc_disp["単価（月額）"] = by_svc_disp["単価（月額）"].apply(lambda x: f"¥{x:,}")
        st.dataframe(by_svc_disp.reset_index(drop=True), use_container_width=True, hide_index=True)

        # 全体サマリー
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("### 🏆 事務所全体サマリー")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("全提案機会", f"{len(rec_df)}件")
        col_s2.metric("推定年間増収額（合計）", f"¥{total_annual:,.0f}")
        col_s3.metric("推定月間増収額（合計）", f"¥{total_annual//12:,.0f}")

        st.info(f"💡 全提案が実現した場合、年間 **¥{total_annual:,.0f}** の増収が見込まれます。"
                f"（Confidence加重の期待値ベースの試算）")

# ─────────────────────────────────────────
with tab4:
    st.header("📊 データプレビュー")
    st.markdown("顧問先×サービスマトリクス（現在利用状況）")

    # サービス利用率サマリー
    st.subheader("サービス利用率")
    usage_rate = pd.DataFrame({
        "サービス": svc_cols,
        "利用顧問先数": [int(df[s].sum()) for s in svc_cols],
        "利用率": [f"{df[s].mean()*100:.1f}%" for s in svc_cols],
        "月額単価": [f"¥{SERVICES.get(s, 0):,}" for s in svc_cols],
    })
    st.dataframe(usage_rate, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("顧問先×サービスマトリクス（全件）")
    disp_cols = ["顧問先名", "業種", "従業員規模", "月額顧問料", "契約年数"] + svc_cols
    disp_cols = [c for c in disp_cols if c in df.columns]
    st.dataframe(df[disp_cols], use_container_width=True, hide_index=True)

# ============================================================
# 定期運用チェックリスト
# ============================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 📋 定期運用チェックリスト")
with st.expander("週次チェック"):
    st.markdown("- □ 最優先提案先への面談準備\n- □ トークスクリプトの確認")
with st.expander("月次チェック"):
    st.markdown("- □ 提案実績の振り返り\n- □ 新規クロスセル機会の分析更新")

# ============================================================
# 相互リンク
# ============================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
_fc1, _fc2, _fc3 = st.columns(3)
with _fc1:
    st.markdown("""<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:12px;padding:18px 14px;text-align:center;">
<div style="font-size:1.3rem;font-weight:700;color:#D97706;margin:4px 0;">🔮 離反予測</div>
<div style="font-size:0.85rem;color:#64748B;">提案前に離反リスクを確認</div>
</div>""", unsafe_allow_html=True)
    st.link_button("離反予測を開く", "https://shigyou-churn.streamlit.app", use_container_width=True)
with _fc2:
    st.markdown("""<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:12px;padding:18px 14px;text-align:center;">
<div style="font-size:1.3rem;font-weight:700;color:#D97706;margin:4px 0;">📊 月次レポート</div>
<div style="font-size:0.85rem;color:#64748B;">提案根拠を月次データで裏付け</div>
</div>""", unsafe_allow_html=True)
    st.link_button("月次レポートを開く", "https://shigyou-report.streamlit.app", use_container_width=True)
with _fc3:
    st.markdown("""<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:12px;padding:18px 14px;text-align:center;">
<div style="font-size:1.3rem;font-weight:700;color:#D97706;margin:4px 0;">🏢 士業ポータル</div>
<div style="font-size:0.85rem;color:#64748B;">全ツール一覧</div>
</div>""", unsafe_allow_html=True)
    st.link_button("士業ポータルを開く", "https://shigyou-ai-tools.streamlit.app", use_container_width=True)
st.caption("AI経営パートナー × データサイエンス | クロスセル分析 v1.0")
