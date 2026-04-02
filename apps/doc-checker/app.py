"""
申請書類チェッカー
==================
建設業許可申請・飲食店営業許可・就業規則届出・社会保険新規適用届の
書類準備状況をチェックし、不備を即座に特定するStreamlitアプリ
"""
import streamlit as st
from datetime import date

# ============================================================
# チェックリスト定数
# ============================================================
CHECKLISTS = {
    "建設業許可申請": {
        "icon": "🏗️",
        "description": "都道府県知事・国土交通大臣への建設業許可申請に必要な書類チェック",
        "authority": "都道府県知事 / 国土交通大臣",
        "standard_days": "30〜60日（審査期間）",
        "items": [
            {
                "name": "建設業許可申請書（様式第1号）",
                "required": True,
                "point": "押印漏れ・記載ミスに注意。法人の場合は代表者印必須",
                "ng_example": "代表者氏名の旧字体・略字の使用、印鑑の欠落",
            },
            {
                "name": "工事経歴書（様式第2号）",
                "required": True,
                "point": "過去5年分の主要完成工事を記載。件数・金額の整合性を確認",
                "ng_example": "記載件数が少ない、金額が財務諸表と不一致",
            },
            {
                "name": "直前3年の財務諸表（貸借対照表・損益計算書）",
                "required": True,
                "point": "決算期ごとに作成。自己資本額の確認（一般許可: 500万円以上）",
                "ng_example": "確定申告書との数値乖離、税理士署名なし",
            },
            {
                "name": "誓約書（様式第6号）",
                "required": True,
                "point": "欠格要件に該当しないことの誓約。全役員・令3条使用人の分が必要",
                "ng_example": "役員全員分がそろっていない",
            },
            {
                "name": "専任技術者の資格証明書類",
                "required": True,
                "point": "資格証のコピーまたは実務経験証明書。有効期限・業種の一致を確認",
                "ng_example": "資格と申請業種が一致しない、実務経験年数の不足",
            },
            {
                "name": "経営業務の管理責任者の証明書類",
                "required": True,
                "point": "5年以上の経営経験を証明する書類（決算書・契約書等）",
                "ng_example": "経験年数の根拠書類が薄い、期間に空白がある",
            },
            {
                "name": "登記されていないことの証明書",
                "required": True,
                "point": "成年後見・被保佐人に登記されていないことの証明。発行後3ヶ月以内",
                "ng_example": "有効期限切れ（発行から3ヶ月超過）",
            },
            {
                "name": "身分証明書（本籍地の市区町村発行）",
                "required": True,
                "point": "禁治産・準禁治産・破産の登録がないことの証明。発行後3ヶ月以内",
                "ng_example": "住民票では不可（身分証明書と別物）",
            },
            {
                "name": "法人の登記事項証明書",
                "required": True,
                "point": "法人の場合必須。発行後3ヶ月以内のもの",
                "ng_example": "個人事業主申請に法人登記を添付する誤り",
            },
            {
                "name": "納税証明書（法人税・消費税）",
                "required": True,
                "point": "未納がないことの証明。都道府県・国税の両方が必要な場合あり",
                "ng_example": "消費税分の証明書が漏れている",
            },
        ],
    },
    "飲食店営業許可申請": {
        "icon": "🍽️",
        "description": "食品衛生法に基づく飲食店営業許可の申請書類チェック",
        "authority": "保健所（都道府県/政令市）",
        "standard_days": "10〜20日（施設検査を含む）",
        "items": [
            {
                "name": "飲食店営業許可申請書",
                "required": True,
                "point": "保健所指定の様式を使用。開業予定日の2〜3週間前に申請",
                "ng_example": "古い様式の使用、開業後の申請",
            },
            {
                "name": "食品衛生責任者資格証明書（コピー）",
                "required": True,
                "point": "調理師免許・栄養士免許または講習会修了証。1施設につき1名以上",
                "ng_example": "資格者が他店舗との兼任（原則不可）",
            },
            {
                "name": "施設の平面図（厨房レイアウト）",
                "required": True,
                "point": "設備の配置・寸法を記載。手洗い設備の位置・2槽シンクの確認",
                "ng_example": "縮尺不明・設備の省略、手洗い場の位置が不適切",
            },
            {
                "name": "水質検査成績書（井戸水使用の場合）",
                "required": False,
                "point": "水道水の場合は不要。井戸水・地下水を使用する場合は直近の検査結果",
                "ng_example": "1年以上前の古い検査結果の使用",
            },
            {
                "name": "営業許可申請手数料（収入証紙/現金）",
                "required": True,
                "point": "都道府県により金額が異なる（例: 東京都 18,300円）。支払方法要確認",
                "ng_example": "金額不足、収入証紙の貼付方法の誤り",
            },
            {
                "name": "建物の使用権限を証明する書類",
                "required": True,
                "point": "自己所有: 登記事項証明書。賃貸: 賃貸借契約書（飲食店可の記載確認）",
                "ng_example": "賃貸借契約書に飲食店可の明記なし",
            },
            {
                "name": "法人の登記事項証明書（法人の場合）",
                "required": False,
                "point": "法人申請の場合のみ必要。発行後3ヶ月以内",
                "ng_example": "個人事業主申請に法人書類を混同",
            },
            {
                "name": "既存施設の検査済証（リノベーションの場合）",
                "required": False,
                "point": "既存建物の改装の場合は建築確認済証等が必要になることがある",
                "ng_example": "無確認で大規模改装後に申請",
            },
        ],
    },
    "就業規則届出": {
        "icon": "📋",
        "description": "常時10人以上の従業員がいる事業場の就業規則届出（労働基準法第89条）",
        "authority": "所轄労働基準監督署",
        "standard_days": "受理即日〜1週間（届出のみ）",
        "items": [
            {
                "name": "就業規則届（様式第9号）",
                "required": True,
                "point": "事業場単位で提出。本社・支店別に届出が必要。2部提出（控え受領）",
                "ng_example": "本社のみ提出で支店分が漏れる",
            },
            {
                "name": "就業規則本文",
                "required": True,
                "point": "絶対的必要記載事項（始業・終業時刻、休日、賃金等）の欠落がないか確認",
                "ng_example": "育児・介護休業、ハラスメント防止規程の未整備",
            },
            {
                "name": "意見書（労働者代表の署名・押印付き）",
                "required": True,
                "point": "過半数労働組合または過半数代表者の意見書。同意でなく意見書でOK",
                "ng_example": "代表者の選出方法が適切でない（挙手・互選でなく使用者指名）",
            },
            {
                "name": "労働者代表者の選出根拠書類",
                "required": True,
                "point": "代表者の選出方法・日時・氏名を記録。メール・投票の記録が望ましい",
                "ng_example": "「管理職が代表者」は不可（法定違反）",
            },
            {
                "name": "別規程（育児・介護休業規程）",
                "required": True,
                "point": "育児介護休業法改正対応の内容か確認。2022年・2023年改正への対応",
                "ng_example": "古いバージョンのまま提出（産後パパ育休未対応）",
            },
            {
                "name": "別規程（ハラスメント防止規程）",
                "required": True,
                "point": "パワハラ防止措置（指針対応）、セクハラ・マタハラ規定を含む",
                "ng_example": "パワハラの定義が法律と乖離している",
            },
            {
                "name": "別規程（テレワーク・副業に関する規程）",
                "required": False,
                "point": "テレワーク実施・副業許可の場合は別規程または本規程への記載推奨",
                "ng_example": "テレワーク実施中なのに労働時間管理の規定がない",
            },
            {
                "name": "賃金規程（賃金に関する別規程）",
                "required": False,
                "point": "本規程に賃金の詳細を定めず別規程とする場合は別途届出が必要",
                "ng_example": "賃金規程を別規程にしたが未届出",
            },
            {
                "name": "36協定（時間外・休日労働協定）",
                "required": False,
                "point": "時間外労働がある場合は36協定も届出が必要（就業規則とセットで確認）",
                "ng_example": "就業規則の時間外規定と36協定の上限が矛盾",
            },
            {
                "name": "旧就業規則（変更届の場合）",
                "required": False,
                "point": "変更届の場合は変更前の就業規則の写しを添付（署の指示による）",
                "ng_example": "変更届なのに旧版を添付しない",
            },
        ],
    },
    "社会保険新規適用届": {
        "icon": "🏥",
        "description": "法人設立・従業員雇用時の社会保険（健康保険・厚生年金）新規適用手続き",
        "authority": "所轄年金事務所",
        "standard_days": "受理後5〜10日（保険証交付）",
        "items": [
            {
                "name": "健康保険・厚生年金保険新規適用届",
                "required": True,
                "point": "事業所の所在地・名称・事業主氏名を正確に記載。法人番号の記入を忘れずに",
                "ng_example": "法人番号の誤り、事業所名が登記と不一致",
            },
            {
                "name": "法人の登記事項証明書（原本）",
                "required": True,
                "point": "発行後3ヶ月以内のもの。事業内容・所在地が申請書と一致しているか確認",
                "ng_example": "本店移転後の旧住所で申請",
            },
            {
                "name": "被保険者資格取得届（従業員全員分）",
                "required": True,
                "point": "採用日・生年月日・基本給・報酬月額を正確に記入。マイナンバー記載",
                "ng_example": "試用期間中の従業員を漏らす、報酬月額の計算誤り",
            },
            {
                "name": "事業所の賃貸借契約書または登記事項証明書",
                "required": True,
                "point": "実態のある事業所があることを証明。自宅兼事務所の場合も必要",
                "ng_example": "バーチャルオフィスのみで実態なしと判断される",
            },
            {
                "name": "労働保険関係成立届の控え（雇用保険適用事業所の場合）",
                "required": False,
                "point": "雇用保険の適用事業所である場合は、労働保険の成立届控えを添付",
                "ng_example": "雇用保険を未手続きのまま社保のみ申請",
            },
            {
                "name": "役員報酬を決めた議事録（役員の場合）",
                "required": False,
                "point": "役員の報酬月額の根拠として株主総会議事録・取締役会議事録が必要",
                "ng_example": "議事録がなく役員報酬の根拠を証明できない",
            },
            {
                "name": "賃金台帳・タイムカード等の写し",
                "required": False,
                "point": "求められる場合あり。報酬月額の根拠として使用。直近3ヶ月分が目安",
                "ng_example": "給与明細だけでタイムカードがない",
            },
            {
                "name": "マイナンバー収集同意書・本人確認書類",
                "required": True,
                "point": "従業員のマイナンバーを収集する際の同意書と本人確認（コピー）が必要",
                "ng_example": "マイナンバーのみ提供でID確認書類がない",
            },
        ],
    },
}

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="申請書類チェッカー",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.checker-hero{text-align:center;padding:32px 0 20px 0;background:linear-gradient(180deg,#ECFEFF,#FFFFFF);border-radius:16px;margin-bottom:16px;}
.checker-hero h1{font-size:2.1rem;color:#0891B2;}
.checker-hero p{font-size:1.05rem;color:#475569;}
.check-item-ok{background:#F0FDF4;border-left:4px solid #16A34A;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;}
.check-item-ng{background:#FEF2F2;border-left:4px solid #DC2626;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;}
.check-item-na{background:#F8FAFC;border-left:4px solid #94A3B8;padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0;}
.section-divider{border:none;border-top:2px solid #E2E8F0;margin:24px 0;}
.result-ok{color:#16A34A;font-weight:bold;}
.result-ng{color:#DC2626;font-weight:bold;}
.progress-label{font-size:1.1rem;font-weight:bold;color:#0891B2;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Main
# ============================================================
st.markdown("""
<div class="checker-hero">
<h1>✅ 申請書類チェッカー</h1>
<p>建設業許可・飲食店営業許可・就業規則・社会保険の申請書類を<br>
チェックリストで漏れなく確認し、不備を即座に特定します。</p>
</div>
""", unsafe_allow_html=True)

st.info("💡 **導入効果**: 申請書類の不備による差し戻しをゼロ化 — 準備チェック時間を **1時間→10分**（1申請あたり50分短縮）")

tab1, tab2 = st.tabs(["✅ 書類チェッカー", "📚 チェックリスト一覧"])

# ─────────────────────────────────────────
with tab1:
    st.header("✅ 書類チェッカー")

    # 書類種別選択
    doc_type = st.selectbox(
        "書類種別を選択してください",
        list(CHECKLISTS.keys()),
        format_func=lambda x: f"{CHECKLISTS[x]['icon']} {x}"
    )

    cl = CHECKLISTS[doc_type]
    st.markdown(f"**{cl['icon']} {doc_type}**")
    col_info1, col_info2 = st.columns(2)
    col_info1.markdown(f"- **申請先**: {cl['authority']}")
    col_info2.markdown(f"- **標準処理期間**: {cl['standard_days']}")
    st.markdown(f"_{cl['description']}_")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # チェックフォーム
    with st.form(f"check_form_{doc_type}"):
        st.markdown("#### 📝 各書類の準備状況を選択してください")
        results = []
        for idx, item in enumerate(cl["items"]):
            req_label = "【必須】" if item["required"] else "【任意】"
            req_color = "#DC2626" if item["required"] else "#64748B"
            st.markdown(
                f'<span style="color:{req_color};font-weight:bold;">{req_label}</span> '
                f'**{item["name"]}**',
                unsafe_allow_html=True
            )
            st.caption(f"📌 チェック観点: {item['point']}")
            st.caption(f"⚠️ よくある不備: {item['ng_example']}")
            status = st.radio(
                f"準備状況",
                ["✅ 済", "❌ 未済", "➖ 該当なし"],
                horizontal=True,
                key=f"item_{doc_type}_{idx}",
                label_visibility="collapsed"
            )
            results.append({"item": item, "status": status})
            st.markdown("---")

        applicant_name = st.text_input("顧問先名（任意）", placeholder="例: 〇〇株式会社")
        submitted = st.form_submit_button("📊 チェック結果を確認する", type="primary", use_container_width=True)

    # 結果表示
    if submitted:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.header("📊 チェック結果")

        ok_items = [r for r in results if r["status"] == "✅ 済"]
        ng_items = [r for r in results if r["status"] == "❌ 未済" and r["item"]["required"]]
        ng_optional = [r for r in results if r["status"] == "❌ 未済" and not r["item"]["required"]]
        na_items = [r for r in results if r["status"] == "➖ 該当なし"]

        required_total = sum(1 for r in results if r["item"]["required"])
        required_ok = sum(1 for r in results if r["item"]["required"] and r["status"] == "✅ 済")
        completion_rate = (required_ok / required_total * 100) if required_total > 0 else 0

        # KPIカード
        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("必須項目 完了率", f"{completion_rate:.0f}%", f"{required_ok}/{required_total}件")
        kc2.metric("✅ 準備完了", f"{len(ok_items)}件")
        kc3.metric("❌ 未済（必須）", f"{len(ng_items)}件",
                   delta=f"-{len(ng_items)}" if ng_items else None,
                   delta_color="inverse")
        kc4.metric("➖ 該当なし", f"{len(na_items)}件")

        # プログレスバー
        st.markdown(f'<div class="progress-label">必須書類 完了率: {completion_rate:.0f}%</div>', unsafe_allow_html=True)
        st.progress(completion_rate / 100)

        if completion_rate == 100:
            st.success("🎉 必須書類はすべて準備完了です！申請可能な状態です。")
        elif completion_rate >= 80:
            st.warning(f"📋 あと少し！必須書類 {len(ng_items)}件 の準備を完了させてから申請してください。")
        else:
            st.error(f"⚠️ 必須書類 {len(ng_items)}件 が未済です。申請前に必ずご対応ください。")

        # 不備リスト（必須）
        if ng_items:
            st.markdown("### ❌ 未済の必須書類（要対応）")
            for r in ng_items:
                st.markdown(
                    f'<div class="check-item-ng">❌ <b>{r["item"]["name"]}</b><br>'
                    f'<small>📌 {r["item"]["point"]}</small><br>'
                    f'<small>⚠️ よくある不備: {r["item"]["ng_example"]}</small></div>',
                    unsafe_allow_html=True
                )

        # 任意・未済
        if ng_optional:
            st.markdown("### ⚠️ 未済の任意書類（状況により必要）")
            for r in ng_optional:
                st.markdown(
                    f'<div class="check-item-ng">❌ <b>{r["item"]["name"]}</b>【任意】<br>'
                    f'<small>📌 {r["item"]["point"]}</small></div>',
                    unsafe_allow_html=True
                )

        # 完了済みリスト
        if ok_items:
            with st.expander(f"✅ 準備完了の書類 ({len(ok_items)}件)"):
                for r in ok_items:
                    req = "【必須】" if r["item"]["required"] else "【任意】"
                    st.markdown(f'<div class="check-item-ok">✅ {req} {r["item"]["name"]}</div>', unsafe_allow_html=True)

        # PDFチェックシート風Markdownダウンロード
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        md_lines = [
            f"# {doc_type} チェックシート",
            f"",
            f"**顧問先**: {applicant_name if applicant_name else '（未記入）'}",
            f"**作成日**: {date.today().strftime('%Y年%m月%d日')}",
            f"**申請先**: {cl['authority']}",
            f"**標準処理期間**: {cl['standard_days']}",
            f"",
            f"---",
            f"",
            f"## 必須書類 完了率: {completion_rate:.0f}% ({required_ok}/{required_total}件)",
            f"",
        ]
        if ng_items:
            md_lines.append("## ❌ 未済の必須書類（要対応）\n")
            for r in ng_items:
                md_lines.append(f"- ❌ **{r['item']['name']}**")
                md_lines.append(f"  - 観点: {r['item']['point']}")
                md_lines.append(f"  - よくある不備: {r['item']['ng_example']}")
            md_lines.append("")
        md_lines.append("## 全チェック項目\n")
        md_lines.append("| # | 必須/任意 | 書類名 | 状況 |")
        md_lines.append("|---|---------|--------|------|")
        for idx, r in enumerate(results, 1):
            req = "必須" if r["item"]["required"] else "任意"
            md_lines.append(f"| {idx} | {req} | {r['item']['name']} | {r['status']} |")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("*本チェックシートはAI経営パートナーの申請書類チェッカーで作成されました。*")
        md_content = "\n".join(md_lines)

        st.download_button(
            "📥 チェックシートをダウンロード（Markdown）",
            md_content,
            f"{doc_type}_チェックシート_{date.today().strftime('%Y%m%d')}.md",
            "text/markdown",
            use_container_width=True
        )

# ─────────────────────────────────────────
with tab2:
    st.header("📚 チェックリスト一覧")
    st.markdown("全書類種別のチェック項目を確認できます。")

    for doc_key, cl_data in CHECKLISTS.items():
        with st.expander(f"{cl_data['icon']} {doc_key} — {len(cl_data['items'])}項目"):
            st.markdown(f"**申請先**: {cl_data['authority']}　|　**標準処理期間**: {cl_data['standard_days']}")
            st.markdown(f"_{cl_data['description']}_")
            st.markdown("")
            for idx, item in enumerate(cl_data["items"], 1):
                req_label = "**【必須】**" if item["required"] else "【任意】"
                st.markdown(f"{idx}. {req_label} **{item['name']}**")
                st.caption(f"　📌 {item['point']}")
                st.caption(f"　⚠️ よくある不備: {item['ng_example']}")

# === 相互リンク ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1, fc2, fc3 = st.columns(3)
fc1.markdown("🛡️ [安心パッケージ](https://compliance-pack.streamlit.app)  \n守秘義務契約・AI処理同意書")
fc2.markdown("📝 [契約書ドラフトAI](https://contract-draft.streamlit.app)  \n顧問契約書を自動生成")
fc3.markdown("🔴 [入金遅延アラート](https://payment-alert.streamlit.app)  \n入金遅延を早期発見")
st.caption("AI経営パートナー × データサイエンス | 申請書類チェッカー v1.0")
