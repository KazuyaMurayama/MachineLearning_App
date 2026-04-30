"""EC経営ダッシュボード — タブ描画関数"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

_COLORS = ["#059669", "#065F46", "#34D399", "#0D9488", "#047857"]


def render_tab1(orders, current_month):
    st.subheader("📊 経営サマリー")
    st.markdown("**月次売上推移（過去13ヶ月）**")
    monthly_sales = orders.groupby("年月")["売上"].sum().reset_index().sort_values("年月")
    fig, ax = plt.subplots(figsize=(10, 4))
    x_pos = range(len(monthly_sales))
    ax.plot(x_pos, monthly_sales["売上"], color="#059669", linewidth=2.5, marker="o", markersize=5)
    ax.fill_between(x_pos, monthly_sales["売上"], alpha=0.1, color="#059669")
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(monthly_sales["年月"].tolist(), rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("売上（円）")
    ax.set_title("月次売上推移")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x/10000):,}万"))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**チャネル別 当月売上**")
        data = orders[orders["年月"] == current_month] if current_month else orders
        ch_sales = data.groupby("チャネル")["売上"].sum().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(ch_sales.index, ch_sales.values, color="#059669", alpha=0.85)
        ax.set_xlabel("売上（円）")
        ax.set_title("チャネル別 当月売上")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x/10000):,}万"))
        for i, v in enumerate(ch_sales.values):
            ax.text(v + max(ch_sales.values) * 0.01, i, f"¥{int(v/10000):,}万", va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with col_b:
        st.markdown("**カテゴリ別 当月売上**")
        data = orders[orders["年月"] == current_month] if current_month else orders
        cat_sales = data.groupby("カテゴリ")["売上"].sum()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(cat_sales.values, labels=cat_sales.index.tolist(),
               colors=_COLORS[:len(cat_sales)], autopct="%1.1f%%", startangle=90,
               textprops={"fontsize": 9})
        ax.set_title("カテゴリ別 当月売上")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    st.markdown("**業績サマリーテーブル（チャネル × カテゴリ）**")
    data = orders[orders["年月"] == current_month] if current_month else orders
    cross_table = data.pivot_table(
        values="売上", index="チャネル", columns="カテゴリ", aggfunc="sum", fill_value=0)
    st.dataframe(cross_table.map(lambda x: f"¥{int(x/10000):,}万"), use_container_width=True)


def render_tab2(ads, cross, selected_channels):
    st.subheader("🔗 チャネル横断ROI分析")
    st.markdown("**チャネル別 ROAS推移（13ヶ月）**")
    fig, ax = plt.subplots(figsize=(10, 4))
    for idx, ch in enumerate(selected_channels):
        ch_ads = ads[ads["チャネル"] == ch].sort_values("年月")
        if len(ch_ads) > 0:
            ax.plot(range(len(ch_ads)), ch_ads["ROAS"], linewidth=2, marker="o", markersize=4,
                    label=ch, color=_COLORS[idx % len(_COLORS)])
    if len(ads) > 0:
        x_labels = sorted(ads["年月"].unique())
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("ROAS")
    ax.set_title("チャネル別 ROAS推移")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("### 🔥 横断分析 — GA4・Lookerでは見えない「RFM×チャネルROI」")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**RFMセグメント × チャネル ROI ヒートマップ**")
        seg_order = ["Champions", "Loyal", "AtRisk", "Lost", "New"]
        heat_data = cross.pivot_table(
            values="ROI", index="RFMセグメント", columns="チャネル", aggfunc="mean", fill_value=0)
        heat_data = heat_data.reindex([s for s in seg_order if s in heat_data.index])
        fig, ax = plt.subplots(figsize=(7, 4))
        im = ax.imshow(heat_data.values, aspect="auto", cmap="Greens")
        ax.set_xticks(range(len(heat_data.columns)))
        ax.set_xticklabels(heat_data.columns.tolist(), fontsize=9)
        ax.set_yticks(range(len(heat_data.index)))
        ax.set_yticklabels(heat_data.index.tolist(), fontsize=9)
        plt.colorbar(im, ax=ax, label="ROI")
        for i in range(len(heat_data.index)):
            for j in range(len(heat_data.columns)):
                ax.text(j, i, f"{heat_data.values[i, j]:.1f}",
                        ha="center", va="center", fontsize=8, color="black")
        ax.set_title("RFMセグメント × チャネル ROI")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with col_d:
        st.markdown("**AtRisk + Lost セグメントへの広告ROI**")
        high_risk_seg = cross[cross["RFMセグメント"].isin(["AtRisk", "Lost"])].copy()
        if len(high_risk_seg) > 0:
            roi_table = high_risk_seg.groupby(["RFMセグメント", "チャネル"]).agg(
                売上=("売上", "sum"), 広告費=("広告費", "sum"),
                ROI=("ROI", "mean"), 離脱率=("離脱率", "mean")).reset_index()
            roi_table["売上"] = roi_table["売上"].apply(lambda x: f"¥{int(x):,}")
            roi_table["広告費"] = roi_table["広告費"].apply(lambda x: f"¥{int(x):,}")
            roi_table["ROI"] = roi_table["ROI"].round(2)
            roi_table["離脱率"] = (roi_table["離脱率"] * 100).round(1).astype(str) + "%"
            st.dataframe(roi_table.reset_index(drop=True), use_container_width=True)
        else:
            st.info("データがありません。")
    st.markdown("**チャネル別 CPA × CV数 散布図**")
    fig, ax = plt.subplots(figsize=(8, 4))
    for idx, ch in enumerate(selected_channels):
        ch_ads = ads[ads["チャネル"] == ch]
        if len(ch_ads) > 0:
            ax.scatter(ch_ads["CPA"], ch_ads["CV数"], label=ch,
                       color=_COLORS[idx % len(_COLORS)], alpha=0.7, s=50)
    ax.set_xlabel("CPA（円）")
    ax.set_ylabel("CV数")
    ax.set_title("チャネル別 CPA × CV数")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def render_tab3(customers, risk_threshold):
    st.subheader("👥 顧客×収益セグメント")
    st.markdown("**RFMセグメント別 統計**")
    rfm_summary = customers.groupby("RFMセグメント").agg(
        顧客数=("顧客ID", "count"),
        平均購入額=("累計購入額", "mean"),
        平均離脱リスクスコア=("離脱リスクスコア", "mean"),
    ).reset_index()
    rfm_summary["平均購入額"] = rfm_summary["平均購入額"].apply(lambda x: f"¥{int(x):,}")
    rfm_summary["平均離脱リスクスコア"] = rfm_summary["平均離脱リスクスコア"].round(1)
    st.dataframe(rfm_summary.reset_index(drop=True), use_container_width=True)
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown("**年齢層別 累計購入額（平均）**")
        age_purchase = customers.groupby("年齢層")["累計購入額"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(age_purchase.index, age_purchase.values, color="#059669", alpha=0.85)
        ax.set_xlabel("平均累計購入額（円）")
        ax.set_title("年齢層別 累計購入額（平均）")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"¥{int(x):,}"))
        for i, v in enumerate(age_purchase.values):
            ax.text(v + max(age_purchase.values) * 0.01, i, f"¥{int(v):,}", va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with col_f:
        st.markdown("**離脱リスクスコア分布**")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(customers["離脱リスクスコア"], bins=20, color="#065F46", alpha=0.75, edgecolor="white")
        ax.axvline(x=risk_threshold, color="#DC2626", linestyle="--",
                   linewidth=2, label=f"しきい値 {risk_threshold}")
        ax.set_xlabel("離脱リスクスコア")
        ax.set_ylabel("人数")
        ax.set_title("離脱リスクスコア分布")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    st.markdown("**RFMセグメント × 年齢層 クロス集計（顧客数）**")
    seg_age_cross = pd.crosstab(customers["RFMセグメント"], customers["年齢層"])
    st.dataframe(seg_age_cross, use_container_width=True)


def render_tab4(products, orders):
    st.subheader("⚠️ アラート")
    col_g, col_h = st.columns(2)
    with col_g:
        st.markdown("**在庫切迫 TOP10（在庫数 < 20）**")
        low_stock = products[products["在庫数"] < 20].sort_values("在庫数").head(10)
        if len(low_stock) > 0:
            disp_stock = low_stock[["商品ID", "カテゴリ", "単価", "在庫数", "原価率"]].copy()
            disp_stock["単価"] = disp_stock["単価"].apply(lambda x: f"¥{x:,}")
            st.dataframe(disp_stock.reset_index(drop=True), use_container_width=True)
        else:
            st.info("在庫切迫商品はありません。")
    with col_h:
        st.info("👥 離脱リスク高顧客リスト・離脱放置コスト試算は「EC月次AIブリーフィング」を参照してください。")
    col_i, col_j = st.columns(2)
    with col_i:
        stockout_products = products[products["在庫数"] == 0]
        potential_loss = int((stockout_products["単価"] * 10).sum())
        low_stock_count = len(products[products["在庫数"] < 20])
        low_stock_products = products[(products["在庫数"] > 0) & (products["在庫数"] < 20)]
        low_stock_opp_loss = int(
            (low_stock_products["単価"] * (20 - low_stock_products["在庫数"]).clip(0)).sum())
        total_inv_risk = potential_loss + low_stock_opp_loss
        st.markdown(f"""
        <div class="alert-box">
        <strong>📦 在庫リスク 機会損失試算</strong><br>
        在庫切れ商品数: <strong>{len(stockout_products)} 商品</strong><br>
        在庫切迫（< 20）商品数: <strong>{low_stock_count} 商品</strong><br>
        在庫切れ機会損失（10個×単価）:<br>
        <span style="font-size:1.5rem;font-weight:700;color:#DC2626;">¥{potential_loss:,}</span><br>
        <span style="font-size:0.9rem;color:#64748b;">切迫分含む合計機会損失: <strong style="color:#DC2626;">¥{total_inv_risk:,}</strong></span>
        </div>
        """, unsafe_allow_html=True)
    with col_j:
        st.info("💸 離脱放置コスト試算・顧客別アクション提案は「EC月次AIブリーフィング」を参照してください。")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("**📥 月次経営サマリーCSVダウンロード**")
    monthly_summary = orders.groupby(["年月", "チャネル"]).agg(
        注文数=("注文数", "sum"), 売上=("売上", "sum"), 粗利=("粗利", "sum")).reset_index()
    monthly_summary["区分"] = "月次売上サマリー"
    export_df = monthly_summary.rename(columns=str)
    csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 月次経営サマリーCSVをダウンロード",
        data=csv_bytes,
        file_name="ec_monthly_summary.csv",
        mime="text/csv")
