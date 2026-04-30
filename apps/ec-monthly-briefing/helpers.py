"""EC月次AIブリーフィング — ルールベース関数 + タブ描画"""
import datetime
import streamlit as st
import matplotlib.pyplot as plt


# ===== ルールベース関数群 =====

def generate_summary(current_rev, prev_rev, avg_roas, high_risk_ratio):
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
    diff = roas - prev_roas
    trend = f"（前月比{diff:+.2f}）"
    if roas >= 3.0:
        return f"✅ {ch}: ROAS {roas:.2f}{trend}は優秀。現予算維持を推奨。"
    elif roas >= 1.5:
        return f"📊 {ch}: ROAS {roas:.2f}{trend}は標準。改善余地あり。"
    else:
        return f"⚠️ {ch}: ROAS {roas:.2f}{trend}は要警戒。予算20%削減を検討。"


def get_recommended_action(rfm_seg, risk_score):
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
    actions = []
    min_roas_ch = ads_current.sort_values("ROAS").iloc[0]
    actions.append(
        f"🔴 【予算最適化】{min_roas_ch['チャネル']}のROASは{min_roas_ch['ROAS']}。予算を20%削減し、高ROASチャネルへ再配分"
    )
    high_risk_count = len(customers_df[customers_df["離脱リスクスコア"] >= threshold])
    actions.append(f"🟡 【顧客維持】離脱リスク高顧客{high_risk_count}人へ再エンゲージキャンペーン実施")
    low_stock = products_df[products_df["在庫数"] < 20]
    if len(low_stock) > 0:
        top_cat = low_stock["カテゴリ"].mode().iloc[0]
        actions.append(f"🔵 【在庫】在庫切迫商品{len(low_stock)}件（TOPカテゴリ: {top_cat}）の追加発注を実施")
    else:
        over_stock = products_df[products_df["在庫数"] > 300]
        actions.append(f"🟢 【在庫】過剰在庫商品{len(over_stock)}件のセール企画を検討")
    return actions


def build_markdown_report(summary_text, current_rev, prev_rev, gross_margin, current_roas,
                           high_risk_ratio, channel_df, risk_top, actions):
    today = datetime.date.today()
    ch_rows = [
        f"| {r['チャネル']} | ¥{int(r['当月売上']):,} | {r['前月比']} | {r['ROAS']:.2f} |"
        for _, r in channel_df.iterrows()
    ]
    channel_md = "| チャネル | 当月売上 | 前月比 | ROAS |\n|---|---|---|---|\n" + "\n".join(ch_rows)
    risk_rows = [
        f"| {r['顧客ID']} | {r['RFMセグメント']} | ¥{int(r['累計購入額']):,} | {r['離脱リスクスコア']} |"
        for _, r in risk_top.head(10).iterrows()
    ]
    risk_md = "| 顧客ID | RFMセグメント | 累計購入額 | 離脱リスクスコア |\n|---|---|---|---|\n" + "\n".join(risk_rows)
    return (
        f"# EC月次ブリーフィングレポート\n\n対象月: 2026年4月\n作成日: {today}\n\n"
        f"## 1. エグゼクティブサマリー\n{summary_text}\n\n"
        f"## 2. KPI\n- 当月売上: ¥{current_rev:,}（約¥{current_rev // 10000:,}万円）\n"
        f"- 粗利率: {gross_margin:.1f}%\n- 平均ROAS: {current_roas:.2f}\n"
        f"- 離脱リスク高顧客比率: {high_risk_ratio:.1f}%\n\n"
        f"## 3. チャネル別ROI\n{channel_md}\n\n"
        f"## 4. 離脱リスク顧客TOP10\n{risk_md}\n\n"
        f"## 5. 次月の重点アクション\n1. {actions[0]}\n2. {actions[1]}\n3. {actions[2]}\n"
    )


# ===== タブ描画関数 =====

def render_tab1(orders_df, ads_df, current_m, prev_m, current_rev, prev_rev,
                current_roas, prev_roas, gross_margin, high_risk_ratio,
                high_risk_customers, risk_threshold):
    mom = (current_rev - prev_rev) / prev_rev * 100 if prev_rev != 0 else 0
    st.subheader("KPIサマリー")
    c1, c2, c3, c4 = st.columns(4)
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
    st.caption("📈 月次売上推移グラフ・チャネル詳細は「EC経営ダッシュボード」を参照してください。")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("自動生成エグゼクティブサマリー")
    summary_text = generate_summary(current_rev, prev_rev, current_roas, high_risk_ratio)
    if mom > 5:
        st.info(f"📈 {summary_text}")
    elif mom > -5:
        st.info(f"📊 {summary_text}")
    else:
        st.warning(f"⚠️ {summary_text}")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("チャネル別業績サマリー")
    cur_orders = orders_df[orders_df["年月"] == current_m].groupby("チャネル").agg(
        当月売上=("売上", "sum")).reset_index()
    prev_orders = orders_df[orders_df["年月"] == prev_m].groupby("チャネル").agg(
        前月売上=("売上", "sum")).reset_index()
    cur_ads = ads_df[ads_df["年月"] == current_m].groupby("チャネル").agg(
        ROAS=("ROAS", "mean")).reset_index()
    summary_tbl = cur_orders.merge(prev_orders, on="チャネル").merge(cur_ads, on="チャネル")
    summary_tbl["前月比"] = summary_tbl.apply(
        lambda r: f"{(r['当月売上'] - r['前月売上']) / r['前月売上'] * 100:+.1f}%"
        if r['前月売上'] != 0 else "N/A", axis=1)
    summary_tbl["当月売上"] = summary_tbl["当月売上"].apply(lambda x: f"¥{x:,}")
    summary_tbl["ROAS"] = summary_tbl["ROAS"].round(2)
    st.dataframe(summary_tbl[["チャネル", "当月売上", "前月比", "ROAS"]], use_container_width=True)


def render_tab2(ads_df, current_m, prev_m):
    st.subheader("チャネル別ROI詳細")
    cur_ads_detail = ads_df[ads_df["年月"] == current_m].groupby("チャネル").agg(
        当月売上=("売上", "sum"), 広告費=("広告費", "sum"), ROAS=("ROAS", "mean"),
        CV数=("CV数", "sum"), CPA=("CPA", "mean")).reset_index()
    prev_ads_detail = ads_df[ads_df["年月"] == prev_m].groupby("チャネル").agg(
        前月ROAS=("ROAS", "mean"), 前月売上=("売上", "sum")).reset_index()
    channel_detail = cur_ads_detail.merge(prev_ads_detail, on="チャネル")
    channel_detail["前月比"] = channel_detail.apply(
        lambda r: f"{(r['当月売上'] - r['前月売上']) / r['前月売上'] * 100:+.1f}%"
        if r['前月売上'] != 0 else "N/A", axis=1)
    channel_detail["ROAS"] = channel_detail["ROAS"].round(2)
    channel_detail["前月ROAS"] = channel_detail["前月ROAS"].round(2)
    channel_detail["CPA"] = channel_detail["CPA"].apply(lambda x: f"¥{int(x):,}")
    fmt_ch = channel_detail.copy()
    fmt_ch["当月売上"] = fmt_ch["当月売上"].apply(lambda x: f"¥{x:,}")
    fmt_ch["広告費"] = fmt_ch["広告費"].apply(lambda x: f"¥{x:,}")
    st.dataframe(fmt_ch[["チャネル", "当月売上", "広告費", "ROAS", "前月ROAS", "CV数", "CPA", "前月比"]],
                 use_container_width=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("チャネル別AI診断コメント")
    max_roas_ch = channel_detail.sort_values("ROAS", ascending=False).iloc[0]
    min_roas_ch = channel_detail.sort_values("ROAS").iloc[0]
    for _, row in channel_detail.iterrows():
        comment = generate_channel_comment(row["チャネル"], row["ROAS"], row["前月ROAS"])
        st.markdown(f'<div class="action-item">{comment}</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.success(f"🏆 最高ROAS: **{max_roas_ch['チャネル']}** (ROAS {max_roas_ch['ROAS']:.2f}) — 予算増配を推奨します。")
    st.warning(f"⚠️ 最低ROAS: **{min_roas_ch['チャネル']}** (ROAS {min_roas_ch['ROAS']:.2f}) — 予算削減または施策改善が急務です。")
    st.subheader("チャネル別ROAS比較")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    colors = ["#059669" if r >= 3.0 else "#D97706" if r >= 1.5 else "#DC2626"
              for r in channel_detail["ROAS"]]
    bars = ax2.bar(channel_detail["チャネル"], channel_detail["ROAS"],
                   color=colors, edgecolor="white", linewidth=1.5)
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
    return channel_detail


def render_tab3(customers, high_risk_customers, risk_threshold):
    st.subheader(f"離脱リスク高顧客 TOP20（スコア ≥ {risk_threshold}）")
    high_risk_top = high_risk_customers.sort_values("離脱リスクスコア", ascending=False).head(20).copy()
    high_risk_top["推奨アクション"] = high_risk_top.apply(
        lambda r: get_recommended_action(r["RFMセグメント"], r["離脱リスクスコア"]), axis=1)
    display_risk = high_risk_top[
        ["顧客ID", "年齢層", "RFMセグメント", "累計購入額", "離脱リスクスコア", "推奨アクション"]].copy()
    display_risk["累計購入額"] = display_risk["累計購入額"].apply(lambda x: f"¥{x:,}")
    st.dataframe(display_risk, use_container_width=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    if len(high_risk_customers) > 0:
        avg_purchase = customers["累計購入額"].mean()
        annual_loss_est = int(len(high_risk_customers) * avg_purchase * 2.5 * 0.3)
        roi_multiple = annual_loss_est // 260000 if annual_loss_est > 0 else 0
        monthly_loss_est = int(annual_loss_est / 12)
        st.markdown(
            f'<div class="highlight-box"><strong>💸 離脱放置による年間損失額試算</strong><br>'
            f'離脱リスク高顧客 <strong>{len(high_risk_customers)}人</strong>が30%流出した場合、<br>'
            f'月次損失: <span style="color:#92400E;font-size:1.1rem;font-weight:700;">¥{monthly_loss_est:,}</span>'
            f'／ 年間損失: <span style="color:#92400E;font-size:1.3rem;font-weight:700;">¥{annual_loss_est:,}</span><br>'
            f'<span style="font-size:0.9rem;color:#64748b;">💡 <strong>L3プレミアムパック 月額26万円</strong>で離脱防止施策を実行すれば、'
            f'投資回収比率 <strong style="color:#059669;">{roi_multiple}倍</strong>（年間換算）。'
            f'GA4・Lookerでは顧客ごとの離脱リスクスコアは算出不可。</span></div>',
            unsafe_allow_html=True)
    st.subheader("離脱リスク高顧客 RFMセグメント構成")
    rfm_counts = high_risk_customers["RFMセグメント"].value_counts()
    if len(rfm_counts) > 0:
        fig3, ax3 = plt.subplots(figsize=(7, 5))
        colors3 = ["#059669", "#D97706", "#F59E0B", "#EF4444", "#6B7280"]
        wedges, texts, autotexts = ax3.pie(
            rfm_counts.values, labels=rfm_counts.index.tolist(), autopct="%1.1f%%",
            colors=colors3[:len(rfm_counts)], startangle=140, pctdistance=0.85)
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color("white")
        ax3.set_title("RFMセグメント別構成", fontsize=12, color="#065F46", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)


def render_tab4(ads_df, products, customers, channel_detail, current_m,
                current_rev, prev_rev, gross_margin, current_roas, high_risk_ratio,
                risk_threshold, high_risk_customers):
    st.subheader("次月重点アクション（AI自動生成）")
    st.info("💼 **L3 プレミアムパック 月額26万円の伴走支援** — データドリブンな次月アクション3件をAIが自動生成。GA4・Lookerでは見えない「実行すべき施策」を即座に提示します。")
    if len(high_risk_customers) > 0:
        avg_p = customers["累計購入額"].mean()
        annual_loss_for_tab4 = int(len(high_risk_customers) * avg_p * 2.5 * 0.3)
        roi_x = annual_loss_for_tab4 // 260000 if annual_loss_for_tab4 > 0 else 0
        st.markdown(
            f'<div class="highlight-box"><strong>📊 月額26万円 投資対効果サマリー</strong><br>'
            f'年間損失回避額: <span style="color:#92400E;font-size:1.2rem;font-weight:700;">¥{annual_loss_for_tab4:,}</span>'
            f'／ 年間投資額: ¥3,120,000（月額26万×12）<br>'
            f'<strong style="color:#059669;font-size:1.1rem;">投資回収比率: {roi_x}倍</strong>'
            f'— 経営会議に提出できる定量根拠をワンクリックで生成。</div>',
            unsafe_allow_html=True)
    cur_ads_for_action = ads_df[ads_df["年月"] == current_m].groupby("チャネル").agg(
        ROAS=("ROAS", "mean"), 広告費=("広告費", "sum")).reset_index()
    actions = generate_actions(cur_ads_for_action, products, customers, risk_threshold)
    for action in actions:
        st.markdown(f'<div class="action-item">{action}</div>', unsafe_allow_html=True)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("📥 月次レポート全文ダウンロード")
    ch_md_df = channel_detail[["チャネル", "当月売上", "前月比", "ROAS"]].copy()
    risk_top10 = high_risk_customers.sort_values("離脱リスクスコア", ascending=False).head(10)
    summary_for_report = generate_summary(current_rev, prev_rev, current_roas, high_risk_ratio)
    md_report = build_markdown_report(
        summary_for_report, current_rev, prev_rev, gross_margin, current_roas,
        high_risk_ratio, ch_md_df, risk_top10, actions)
    st.download_button(
        label="📥 Markdownレポートをダウンロード",
        data=md_report.encode("utf-8"),
        file_name="ec_monthly_briefing_2026-04.md",
        mime="text/markdown")
    with st.expander("レポートプレビュー（クリックで展開）"):
        st.markdown(md_report)
