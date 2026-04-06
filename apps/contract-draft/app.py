"""
契約書ドラフトAI
================
税理士・社労士・行政書士向けの契約書テンプレート自動生成ツール
フォームに事務所情報を入力するだけで、業種に応じた契約書ドラフトを生成
"""
import streamlit as st
import re
from datetime import date,timedelta


def _extract_number(text:str)->int|None:
    """フリーテキストから数値を抽出する（カンマ・円記号・全角数字対応）"""
    if not text:
        return None
    # 全角数字→半角
    t=text.translate(str.maketrans('０１２３４５６７８９','0123456789'))
    t=t.replace('¥','').replace('￥','').replace('円','').replace(',','').replace('、','').replace(' ','')
    m=re.search(r'(\d+)',t)
    return int(m.group(1)) if m else None


# === 条項解説データ ===
CLAUSE_NOTES={
"税理士":{
    "第1条":{
        "title":"委託業務の範囲のポイント",
        "body":"記帳代行・給与計算を含める場合は追加業務欄に明記しましょう。業務範囲の曖昧さはトラブルの原因になります。",
    },
    "第2条":{
        "title":"顧問料のポイント",
        "body":"月額顧問料の目安: 同業種平均 ¥30,000〜¥80,000。決算料は月額の4〜6ヶ月分が相場です。年商規模・仕訳数で調整してください。",
    },
    "第5条":{
        "title":"守秘義務のポイント",
        "body":"AI処理を行う場合は「安心パッケージ」のAI処理同意書も必須です。クラウド会計連携時のデータ取扱いルールも別途定めることを推奨します。",
    },
    "第7条":{
        "title":"解約条項のポイント",
        "body":"1ヶ月前通知は最低基準です。決算期直前の解約トラブル防止には2ヶ月前通知を推奨します。引継ぎ期間の確保も重要です。",
    },
},
"社労士":{
    "第1条":{
        "title":"委託業務の範囲のポイント",
        "body":"就業規則の作成・改定や助成金申請は別料金になることが多いです。対象業務を明確にしておきましょう。",
    },
    "第2条":{
        "title":"顧問料のポイント",
        "body":"社労士の月額顧問料の目安: 従業員10名以下 ¥20,000〜¥40,000、30名以下 ¥40,000〜¥60,000。従業員数に応じた料金テーブルの別紙添付を推奨します。",
    },
    "第5条":{
        "title":"守秘義務・個人情報のポイント",
        "body":"従業員の個人情報（マイナンバー含む）を扱うため、個人情報保護法に加え番号法の遵守も必要です。AI処理時は匿名化が必須です。",
    },
    "第6条":{
        "title":"解約条項のポイント",
        "body":"1ヶ月前通知は最低基準。社会保険手続き中の解約は従業員に不利益が生じる可能性があるため、手続き完了までの引継ぎ義務を明記することを推奨します。",
    },
},
"行政書士":{
    "第1条":{
        "title":"委託業務の内容のポイント",
        "body":"許認可申請の場合、申請先の行政機関名・許可の種類を具体的に記載しましょう。業務範囲の明確化がトラブル防止の鍵です。",
    },
    "第2条":{
        "title":"報酬のポイント",
        "body":"着手金50%は一般的な水準です。建設業許可: ¥100,000〜¥200,000、会社設立: ¥80,000〜¥150,000 が相場の目安です。実費（印紙代等）は別途必要です。",
    },
    "第5条":{
        "title":"守秘義務のポイント",
        "body":"行政書士法第12条で守秘義務が法定されています。AI処理を行う場合は匿名化処理に加え、依頼者の同意取得が必須です。",
    },
    "第7条":{
        "title":"解約条項のポイント",
        "body":"業務着手後の解約は進捗に応じた報酬精算が必要です。着手前解約の場合でも着手金は返還されない点を依頼者に事前説明しておきましょう。",
    },
},
}

# === テンプレート定数 ===
TEMPLATES={
"税理士":{
    "title":"税務顧問契約書",
    "template":"""# 税務顧問契約書

{office_name}（以下「甲」という）と{client_name}（以下「乙」という）は、以下のとおり税務顧問契約を締結する。

## 第1条（委託業務の範囲）
乙は甲に対し、以下の業務を委託する。
1. 月次試算表の作成・報告
2. 決算書の作成
3. 法人税・消費税・地方税の確定申告書の作成・提出
4. 年末調整業務
5. 税務相談（随時）
{extra_services}

## 第2条（顧問料）
1. 月額顧問料: **{monthly_fee}**（消費税別）
2. 決算料: **{settlement_fee}**（消費税別）
3. 支払方法: 毎月末日締め、翌月{payment_day}日までに甲の指定口座へ振込
4. 振込手数料は乙の負担とする

## 第3条（契約期間）
1. 契約期間: {start_date} から {end_date} まで（{duration}）
2. 期間満了の1ヶ月前までに甲乙いずれからも書面による解約の申入れがない場合、同一条件にて1年間自動更新する

## 第4条（資料の提供）
1. 乙は、甲の業務遂行に必要な帳簿書類・証憑類を速やかに提供する
2. 資料の提供が遅延した場合、申告期限に間に合わない場合があることを乙は了承する

## 第5条（守秘義務）
1. 甲は、業務上知り得た乙の秘密情報を第三者に漏洩しない
2. AI処理を行う場合は、別途「AI処理同意書」の締結を要する
3. 守秘義務は契約終了後3年間存続する

## 第6条（免責事項）
1. 乙が提供した資料の記載内容に誤りがあった場合、それに基づく申告内容について甲は責任を負わない
2. 税法改正等による不利益について、甲は事前にその影響を説明するよう努める

## 第7条（解約）
1. 甲乙いずれも、1ヶ月前までに書面で通知することにより本契約を解約できる
2. 解約時、甲は受領済みの書類を速やかに乙に返還する

## 第8条（管轄裁判所）
本契約に関する紛争は、{jurisdiction}地方裁判所を第一審の専属的合意管轄裁判所とする。

---

{start_date} 締結

甲（税理士事務所）: {office_name}　　印

乙（顧問先）: {client_name}　　印
"""},
"社労士":{
    "title":"社会保険労務士業務委託契約書",
    "template":"""# 社会保険労務士業務委託契約書

{office_name}（以下「甲」という）と{client_name}（以下「乙」という）は、以下のとおり業務委託契約を締結する。

## 第1条（委託業務の範囲）
乙は甲に対し、以下の業務を委託する。
1. 社会保険（健康保険・厚生年金）の取得・喪失届の作成・提出
2. 雇用保険の取得・喪失届の作成・提出
3. 労働保険の年度更新手続き
4. 算定基礎届・月額変更届の作成・提出
5. 労務相談（随時）
{extra_services}

## 第2条（顧問料）
1. 月額顧問料: **{monthly_fee}**（消費税別）
2. 就業規則の作成・改定: 別途見積り
3. 支払方法: 毎月末日締め、翌月{payment_day}日までに甲の指定口座へ振込

## 第3条（契約期間）
1. 契約期間: {start_date} から {end_date} まで（{duration}）
2. 期間満了の1ヶ月前までに書面による解約の申入れがない場合、1年間自動更新する

## 第4条（届出の期限）
1. 乙は、従業員の入退社・異動等が生じた場合、速やかに甲に連絡する
2. 届出に必要な情報の提供が遅延した場合の不利益について、甲は責任を負わない

## 第5条（守秘義務）
1. 甲は、業務上知り得た乙の従業員に関する個人情報等を第三者に漏洩しない
2. 個人情報の取扱いは「個人情報の保護に関する法律」に準拠する
3. AI処理を行う場合は、個人を特定できる情報を匿名化した上で処理する

## 第6条（解約）
甲乙いずれも、1ヶ月前までに書面で通知することにより本契約を解約できる。

## 第7条（管轄裁判所）
本契約に関する紛争は、{jurisdiction}地方裁判所を第一審の専属的合意管轄裁判所とする。

---

{start_date} 締結

甲（社労士事務所）: {office_name}　　印

乙（顧問先）: {client_name}　　印
"""},
"行政書士":{
    "title":"行政書士業務委託契約書",
    "template":"""# 行政書士業務委託契約書

{office_name}（以下「甲」という）と{client_name}（以下「乙」という）は、以下のとおり業務委託契約を締結する。

## 第1条（委託業務の内容）
乙は甲に対し、以下の業務を委託する。
1. {main_service}
{extra_services}

## 第2条（報酬）
1. 報酬額: **{total_fee}**（消費税別）
2. 着手金: 報酬額の50%を契約締結時に支払う
3. 残金: 業務完了後{payment_day}日以内に支払う

## 第3条（業務の期限）
甲は、乙から必要書類を受領後、{delivery_days}営業日以内に業務を完了するよう努める。ただし、行政機関の審査期間は含まない。

## 第4条（必要書類の提供）
1. 乙は、甲が業務遂行に必要とする書類・情報を速やかに提供する
2. 乙の書類提供の遅延により業務が遅延した場合、甲は責任を負わない

## 第5条（守秘義務）
1. 甲は、業務上知り得た乙の秘密情報を第三者に漏洩しない
2. 行政書士法第12条の守秘義務に基づき、業務上の秘密を厳守する
3. AI処理を行う場合は、別途同意を得た上で匿名化処理を実施する

## 第6条（免責事項）
1. 乙が提供した情報・書類の内容に誤りがあった場合、それに基づく申請の却下について甲は責任を負わない
2. 行政機関の裁量により許可が得られなかった場合でも、甲の報酬請求権は消滅しない

## 第7条（解約）
1. 業務着手前: 乙は着手金を放棄して解約できる
2. 業務着手後: 進捗に応じた報酬を精算の上、解約できる

## 第8条（管轄裁判所）
本契約に関する紛争は、{jurisdiction}地方裁判所を第一審の専属的合意管轄裁判所とする。

---

{start_date} 締結

甲（行政書士事務所）: {office_name}　　印

乙（依頼者）: {client_name}　　印
"""},
}

# === Page Config ===
st.set_page_config(page_title="契約書ドラフトAI",page_icon="📝",layout="wide",initial_sidebar_state="expanded")

# === CSS ===
st.markdown("""
<style>
.draft-hero{text-align:center;padding:36px 0 24px 0;background:linear-gradient(180deg,#F5F3FF,#FFFFFF);border-radius:16px;margin-bottom:12px;}
.draft-hero h1{font-size:2.2rem;color:#7C3AED;}
.draft-hero p{font-size:1.1rem;color:#475569;}
.section-divider{border:none;border-top:2px solid #E2E8F0;margin:32px 0;}
.kpi-card{background:#F5F3FF;border:1px solid #DDD6FE;border-radius:12px;padding:18px 14px;text-align:center;}
.kpi-card .kpi-value{font-size:1.5rem;font-weight:700;color:#7C3AED;margin:4px 0;}
.kpi-card .kpi-label{font-size:0.85rem;color:#64748B;}
.effect-box{background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border:1px solid #DDD6FE;border-radius:12px;padding:20px;margin:8px 0;}
.effect-box .effect-title{font-size:0.9rem;color:#64748B;margin-bottom:2px;}
.effect-box .effect-value{font-size:1.3rem;font-weight:700;color:#7C3AED;}
.effect-box .effect-detail{font-size:0.8rem;color:#94A3B8;}
</style>
""",unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.markdown("## 📝 契約書ドラフトAI")
    st.markdown("---")
    st.markdown("### 使い方ガイド")
    st.markdown("""
**Step 1:** 士業の種別を選択
**Step 2:** 事務所・顧問先情報を入力
**Step 3:** 生成ボタンでドラフト作成＆ダウンロード
""")
    st.markdown("---")
    st.markdown("### こんな時に使えます")
    st.markdown("""
- 新規顧問先との契約時
- 契約更新時
- AI導入時の追加契約時
""")
    st.markdown("---")
    st.markdown("### 関連ツール")
    st.markdown("""
- 安心パッケージ（守秘義務契約・AI処理同意書）
- 月次レポート自動生成
- 離反予測デモ
""")
    st.markdown("---")
    st.caption("契約書ドラフトAI v1.2")

# === Main ===
st.markdown("""
<div class="draft-hero">
<h1>📝 契約書ドラフトAI</h1>
<p>士業の種別と顧問先情報を入力するだけで、<br>業種に応じた契約書ドラフトを自動生成します。</p>
</div>
""",unsafe_allow_html=True)

# === 導入効果セクション ===
st.markdown("#### 導入効果")
eff1,eff2,eff3=st.columns(3)
with eff1:
    st.markdown("""<div class="effect-box">
<div class="effect-title">契約書作成時間</div>
<div class="effect-value">2時間 → 10分</div>
<div class="effect-detail">92%削減</div>
</div>""",unsafe_allow_html=True)
with eff2:
    st.markdown("""<div class="effect-box">
<div class="effect-title">契約書作成コスト</div>
<div class="effect-value">¥50,000〜¥150,000 → 大幅削減</div>
<div class="effect-detail">テンプレート自動生成で作成コスト削減</div>
</div>""",unsafe_allow_html=True)
with eff3:
    st.markdown("""<div class="effect-box">
<div class="effect-title">年間削減額</div>
<div class="effect-value">約¥60万</div>
<div class="effect-detail">月5件の契約書作成想定</div>
</div>""",unsafe_allow_html=True)

# === KPIメトリクス ===
st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
kc1,kc2,kc3,kc4=st.columns(4)
with kc1:
    st.markdown("""<div class="kpi-card">
<div class="kpi-label">対応士業</div>
<div class="kpi-value">3種類</div>
<div class="kpi-label">税理士/社労士/行政書士</div>
</div>""",unsafe_allow_html=True)
with kc2:
    st.markdown("""<div class="kpi-card">
<div class="kpi-label">テンプレート条項数</div>
<div class="kpi-value">8条</div>
<div class="kpi-label">各テンプレートの条文数平均</div>
</div>""",unsafe_allow_html=True)
with kc3:
    st.markdown("""<div class="kpi-card">
<div class="kpi-label">AI対応条項</div>
<div class="kpi-value">含む</div>
<div class="kpi-label">守秘義務+AI同意連携</div>
</div>""",unsafe_allow_html=True)
with kc4:
    st.markdown("""<div class="kpi-card">
<div class="kpi-label">自動更新対応</div>
<div class="kpi-value">○</div>
<div class="kpi-label">契約期間自動計算</div>
</div>""",unsafe_allow_html=True)

st.markdown('<hr class="section-divider">',unsafe_allow_html=True)

# 業種選択
biz=st.radio("士業の種別を選択",list(TEMPLATES.keys()),horizontal=True)
tmpl=TEMPLATES[biz]

st.markdown(f"### 📝 {tmpl['title']} — 情報入力")
st.markdown('<hr class="section-divider">',unsafe_allow_html=True)

# === session_state 初期化 ===
for key in ["office","client","start","monthly_fee","settlement_fee","duration",
            "payment_day","total_fee","main_service","delivery_days","extra","jurisdiction"]:
    if key not in st.session_state:
        st.session_state[key]=None

# === 入力フォーム（st.form廃止 → リアルタイムプレビュー対応） ===
fc1,fc2=st.columns(2)
with fc1:
    office=st.text_input("事務所名（甲）",value="○○税理士事務所" if biz=="税理士" else f"○○{biz}事務所",key=f"office_{biz}")
    client=st.text_input("顧問先名（乙）",value="△△株式会社",key=f"client_{biz}")
    start=st.date_input("契約開始日",value=date.today(),key=f"start_{biz}")
with fc2:
    if biz in ["税理士","社労士"]:
        monthly_fee=st.text_input("月額顧問料",value="50,000円",key=f"fee_{biz}")
        if biz=="税理士":
            settlement_fee=st.text_input("決算料",value="月額顧問料の4〜6ヶ月分",key=f"settle_{biz}")
        duration=st.selectbox("契約期間",["1年間","2年間","3年間"],index=0,key=f"dur_{biz}")
        payment_day=st.selectbox("支払期日（翌月）",["10","15","20","25","末"],index=3,key=f"pay_{biz}")
    else:
        total_fee=st.text_input("報酬額",value="150,000円",key=f"tfee_{biz}")
        main_service=st.text_input("主な業務内容",value="建設業許可申請",key=f"svc_{biz}")
        delivery_days=st.number_input("納期（営業日）",value=15,min_value=5,max_value=60,key=f"del_{biz}")
extra=st.text_area("追加業務（1行に1項目）",value="",height=80,placeholder="例: 記帳代行\n給与計算代行",key=f"extra_{biz}")
jurisdiction=st.text_input("管轄裁判所",value="東京",key=f"jur_{biz}")

# === リアルタイムプレビュー ===
with st.expander("📋 プレビュー（入力内容が即反映されます）",expanded=False):
    extra_lines=extra.strip().split("\n") if extra.strip() else []
    extra_md=""
    for i,line in enumerate(extra_lines,6 if biz in ["税理士","社労士"] else 2):
        extra_md+=f"\n{i}. {line.strip()}"
    duration_str=duration if biz in ["税理士","社労士"] else "単発業務"
    years=int(duration[0]) if biz in ["税理士","社労士"] else 1
    end=(start.replace(year=start.year+years)-timedelta(days=1))
    preview_params={
        "office_name":office,"client_name":client,
        "start_date":start.strftime("%Y年%m月%d日"),
        "end_date":end.strftime("%Y年%m月%d日"),
        "duration":duration_str,"jurisdiction":jurisdiction,
        "extra_services":extra_md,
    }
    if biz in ["税理士","社労士"]:
        preview_params["monthly_fee"]=monthly_fee
        preview_params["payment_day"]=payment_day
        if biz=="税理士":
            preview_params["settlement_fee"]=settlement_fee
    else:
        preview_params["total_fee"]=total_fee
        preview_params["main_service"]=main_service
        preview_params["delivery_days"]=str(delivery_days)
        preview_params["payment_day"]="30"
    preview_rendered=tmpl["template"].format(**preview_params)
    st.markdown(preview_rendered)

# === 生成ボタン ===
submitted=st.button("📝 契約書を生成する",type="primary",use_container_width=True)

if submitted:
    # 追加業務の整形
    extra_lines=extra.strip().split("\n") if extra.strip() else []
    extra_md=""
    for i,line in enumerate(extra_lines,6 if biz in ["税理士","社労士"] else 2):
        extra_md+=f"\n{i}. {line.strip()}"
    # テンプレート変数
    duration_str=duration if biz in ["税理士","社労士"] else "単発業務"
    years=int(duration[0]) if biz in ["税理士","社労士"] else 1
    end=(start.replace(year=start.year+years)-timedelta(days=1))
    params={
        "office_name":office,"client_name":client,
        "start_date":start.strftime("%Y年%m月%d日"),
        "end_date":end.strftime("%Y年%m月%d日"),
        "duration":duration_str,"jurisdiction":jurisdiction,
        "extra_services":extra_md,
    }
    if biz in ["税理士","社労士"]:
        params["monthly_fee"]=monthly_fee
        params["payment_day"]=payment_day
        if biz=="税理士":
            params["settlement_fee"]=settlement_fee
    else:
        params["total_fee"]=total_fee
        params["main_service"]=main_service
        params["delivery_days"]=str(delivery_days)
        params["payment_day"]="30"
    # 生成
    rendered=tmpl["template"].format(**params)
    st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
    st.markdown("## 📄 生成された契約書ドラフト")

    # --- 契約総額の自動試算（税理士・社労士のみ） ---
    if biz in ["税理士","社労士"]:
        fee_num=_extract_number(monthly_fee)
        years=int(duration[0])
        months=years*12
        if fee_num is not None:
            settle_num=None
            if biz=="税理士":
                settle_num=_extract_number(settlement_fee)
            annual_fee=fee_num*months
            if settle_num is not None:
                total_est=annual_fee+settle_num*years
            else:
                total_est=annual_fee
            tax_amount=int(total_est*0.10)
            total_with_tax=total_est+tax_amount
            st.markdown("### 💰 契約総額の自動試算")
            mc1,mc2,mc3=st.columns(3)
            mc1.metric("月額顧問料 × 期間（税別）",f"¥{annual_fee:,}")
            if biz=="税理士" and settle_num is not None:
                mc2.metric(f"決算料 × {years}年分（税別）",f"¥{settle_num*years:,}")
            else:
                mc2.metric("決算料（税別）","別途見積り")
            mc3.metric("契約総額（税込）",f"¥{total_with_tax:,}",f"うち消費税 ¥{tax_amount:,}")
            st.caption(f"※ 月額 ¥{fee_num:,} × {months}ヶ月"
                       + (f" + 決算料 ¥{settle_num:,} × {years}年" if settle_num else "")
                       + f" + 消費税10% で算出")
            st.markdown('<hr class="section-divider">',unsafe_allow_html=True)

    st.markdown(rendered)

    # --- 各条項の解説・リスク注記 ---
    notes=CLAUSE_NOTES.get(biz,{})
    if notes:
        st.markdown("### 📖 各条項の解説・リスク注記")
        for clause_key in sorted(notes.keys(),key=lambda x:int(re.search(r'\d+',x).group())):
            note=notes[clause_key]
            with st.expander(f"{clause_key} — {note['title']}"):
                st.markdown(note["body"])

    st.download_button(f"📥 {tmpl['title']}をダウンロード",rendered,
        f"{tmpl['title']}.md","text/markdown",use_container_width=True)
    st.info("💡 このドラフトは雛形です。実際の契約締結前に、必ず内容をご確認ください。")
    st.warning("📌 **AI処理を行う場合**は、「安心パッケージ」のAI処理同意書も合わせてご利用ください。契約書第5条の守秘義務条項と連動しています。")

# Footer — 関連ツール（外部URLなし）
st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1,fc2,fc3=st.columns(3)
fc1.markdown("🛡️ **安心パッケージ**  \n守秘義務契約・AI処理同意書")
fc2.markdown("📊 **月次レポート自動生成**  \n試算表CSV→レポート自動作成")
fc3.markdown("🏢 **離反予測デモ**  \n顧問先の離反リスク予測")
st.caption("AI経営パートナー × データサイエンス | 契約書ドラフトAI v1.2")
