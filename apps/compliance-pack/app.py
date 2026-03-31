"""
士業向け安心パッケージ（コンプライアンス対応テンプレート集）
==========================================================
守秘義務契約・データ取扱い規程・AI処理同意書の3点セットを
プレビュー＋ダウンロードできるStreamlitアプリ
"""
import streamlit as st
from datetime import date

# === テンプレート定数 ===

TEMPLATE_NDA="""# 守秘義務に関する契約書

## 当事者
- 甲（委託者）: {client_name}（以下「甲」という）
- 乙（受託者）: {office_name}（以下「乙」という）

## 第1条（目的）
本契約は、甲乙間の業務委託に関連して開示される秘密情報の取扱いについて定めることを目的とする。

## 第2条（秘密情報の定義）
本契約における「秘密情報」とは、以下のいずれかに該当する情報をいう。
1. 甲の顧問先・取引先に関する一切の情報（氏名、住所、連絡先、財務情報等）
2. 甲の経営に関する情報（売上、利益、事業計画等）
3. 甲の従業員に関する情報（氏名、給与、社会保険情報等）
4. その他、甲が秘密と指定した情報

## 第3条（秘密保持義務）
1. 乙は、秘密情報を本業務の目的以外に使用してはならない。
2. 乙は、秘密情報を第三者に開示・漏洩してはならない。
3. 乙は、秘密情報の管理について、善良な管理者の注意義務をもって行う。

## 第4条（AI処理に関する特約）
1. 乙が秘密情報をAI（人工知能）システムで処理する場合、以下の措置を講じる。
   - 個人を特定できる情報は匿名化した上でAIに入力する
   - Azure OpenAI Service等、データがモデル学習に使用されないサービスを利用する
   - AI処理の結果は甲への報告目的以外に使用しない
2. 甲は、別途「AI処理同意書」に署名することで、AI処理を承諾する。

## 第5条（情報の返還・廃棄）
業務終了時、乙は甲の秘密情報を速やかに返還または廃棄し、廃棄した場合はその旨を書面で通知する。

## 第6条（損害賠償）
乙が本契約に違反し、甲に損害を与えた場合、乙はその損害を賠償する責を負う。

## 第7条（有効期間）
本契約の有効期間は、締結日から{duration}間とする。ただし、秘密保持義務は契約終了後も{post_duration}間存続する。

## 第8条（管轄裁判所）
本契約に関する紛争は、{jurisdiction}地方裁判所を第一審の専属的合意管轄裁判所とする。

---
締結日: {contract_date}

甲: {client_name}　　　　印

乙: {office_name}　　　　印
"""

TEMPLATE_DATA_POLICY="""# データ取扱い規程

## 制定日: {policy_date}
## 制定者: {office_name}

---

## 第1章　総則

### 第1条（目的）
本規程は、{office_name}（以下「当社」という）が業務上取り扱う顧問先データの適正な管理について定め、情報漏洩の防止および顧問先の信頼確保を目的とする。

### 第2条（適用範囲）
本規程は、当社の全従業員（業務委託先を含む）が取り扱う全てのデータに適用する。

## 第2章　データの分類と管理

### 第3条（データの分類）
取り扱うデータを以下の3段階に分類する。

| 分類 | 定義 | 例 |
|------|------|-----|
| 機密 | 漏洩時に重大な損害を与えるデータ | マイナンバー、銀行口座情報、パスワード |
| 重要 | 漏洩時に業務上の損害を与えるデータ | 財務諸表、給与明細、顧問先一覧 |
| 一般 | 公開情報に準ずるデータ | 会社概要、公開済み決算情報 |

### 第4条（データの保管）
1. 機密データは暗号化した上で保管する（AES-256以上）。
2. 重要データはアクセス権限を設定し、業務上必要な者のみアクセスを許可する。
3. クラウドサービスを利用する場合は、国内リージョンを優先する。

### 第5条（データの転送）
1. 機密データのメール添付は原則禁止とし、セキュアなファイル共有サービスを利用する。
2. USBメモリ等の外部メディアへの機密データのコピーは原則禁止する。

## 第3章　AI処理に関する規定

### 第6条（AI処理の基本方針）
1. AIサービスの利用にあたっては、データがモデル学習に使用されないサービスを選定する。
   - 推奨: Azure OpenAI Service（データ学習オプトアウト保証）
   - 推奨: Anthropic Claude API（入力データの学習不使用保証）
2. AI処理を行う前に、以下の匿名化処理を必ず実施する。
   - 個人名 → ID番号に置換
   - 住所 → 都道府県レベルに抽象化
   - 電話番号・メールアドレス → 削除
   - マイナンバー → 入力禁止（絶対NG）

### 第7条（AI処理の記録）
AI処理を行った場合は、以下を記録する。
1. 処理日時
2. 使用したAIサービス名
3. 入力データの範囲（匿名化後）
4. 出力結果の概要
5. 担当者名

## 第4章　インシデント対応

### 第8条（情報漏洩時の対応）
1. 情報漏洩を発見した場合、直ちに管理責任者に報告する。
2. 管理責任者は、被害範囲を特定し、影響を受ける顧問先に速やかに通知する。
3. 再発防止策を策定し、記録する。

## 第5章　教育・監査

### 第9条（教育）
全従業員に対し、年1回以上のデータ取扱いに関する教育を実施する。

### 第10条（監査）
年1回以上、本規程の遵守状況を監査する。

---
制定: {policy_date}
{office_name} 代表
"""

TEMPLATE_AI_CONSENT="""# AI処理同意書

## 同意日: {consent_date}

---

{client_name} 殿

{office_name}では、貴社の業務効率化・経営支援の一環として、AI（人工知能）技術を活用したデータ分析・レポート生成を行います。

つきましては、以下の内容をご確認の上、AI処理へのご同意をお願いいたします。

---

## 1. AI処理の目的
- 顧問先の経営データ分析（売上推移、異常値検知等）
- 月次レポートの自動生成
- 離反リスクの早期検知と改善提案
- その他、顧問業務の品質向上に資する分析

## 2. AI処理の対象データ
- 財務データ（試算表、損益計算書等）
- 顧問先属性情報（業種、従業員数、契約年数等）

※ 以下のデータはAI処理の対象外とします:
- マイナンバー
- 銀行口座番号
- パスワード・認証情報

## 3. データの匿名化措置
AI処理にあたり、以下の匿名化を実施します。
- 個人名・法人名 → ID番号に置換
- 住所 → 都道府県レベルに抽象化
- 電話番号・メールアドレス → 削除

## 4. 使用するAIサービス
- **Azure OpenAI Service**（Microsoft社提供）
  - データがモデル学習に使用されないことが保証されています
- **Anthropic Claude API**
  - 入力データの学習不使用が保証されています
- **LightGBM**（オープンソース機械学習ライブラリ）
  - 貴社のローカル環境またはセキュアなクラウド環境で実行

## 5. セキュリティ対策
- データの暗号化（転送時: TLS 1.3、保管時: AES-256）
- アクセスログの記録・保管
- 業務終了時のデータ廃棄

## 6. 同意の撤回
本同意はいつでも撤回可能です。撤回の場合、AI処理を停止し、関連データを廃棄します。

## 7. お問い合わせ先
{office_name}
担当: {contact_person}
メール: {contact_email}

---

上記内容に同意します。

同意日: {consent_date}

{client_name}
代表者名:　　　　　　　　　印
"""

# === Page Config ===
st.set_page_config(page_title="安心パッケージ | 士業向けコンプライアンス",page_icon="🛡️",layout="wide",initial_sidebar_state="collapsed")

# === Custom CSS ===
st.markdown("""
<style>
.pack-card{border-radius:12px;padding:24px;text-align:center;border:2px solid #059669;background:linear-gradient(180deg,#05966908,#05966903);}
.pack-card h3{color:#059669;margin:0 0 8px 0;}
.hero-compliance{text-align:center;padding:36px 0 24px 0;background:linear-gradient(180deg,#F0FDF4,#FFFFFF);border-radius:16px;margin-bottom:12px;}
.hero-compliance h1{font-size:2.2rem;color:#059669;}
.hero-compliance p{font-size:1.1rem;color:#475569;line-height:1.7;}
.section-divider{border:none;border-top:2px solid #E2E8F0;margin:32px 0;}
</style>
""",unsafe_allow_html=True)

# === Session State ===
for k,v in {"office_name":"○○税理士事務所","client_name":"△△株式会社","contact_person":"山田太郎","contact_email":"info@example.com"}.items():
    if k not in st.session_state: st.session_state[k]=v

# === Main ===
st.title("🛡️ 安心パッケージ")
st.markdown("**士業向けAI導入コンプライアンス対応テンプレート集**")

# Hero
st.markdown("""
<div class="hero-compliance">
<h1>🛡️ AI導入 安心パッケージ</h1>
<p>士業の守秘義務に完全対応した3つのテンプレートで、<br>
AI活用への不安をゼロにします。</p>
</div>
""",unsafe_allow_html=True)

# 3-card overview
c1,c2,c3=st.columns(3)
with c1:
    st.markdown("""<div class="pack-card"><h3>📄 守秘義務契約書</h3>
    <p>AI処理に関する特約条項付き。<br>顧問先との信頼関係を文書で担保。</p></div>""",unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="pack-card"><h3>📋 データ取扱い規程</h3>
    <p>データ分類・AI処理ルール・<br>インシデント対応を網羅。</p></div>""",unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="pack-card"><h3>✅ AI処理同意書</h3>
    <p>匿名化措置・使用AI・撤回権を<br>明記。顧問先の安心を確保。</p></div>""",unsafe_allow_html=True)

st.markdown('<hr class="section-divider">',unsafe_allow_html=True)

# 3層防御の図解
st.markdown("### 🔐 AI導入の3層防御")
st.markdown("士業がAIを安全に活用するための**3つの防御層**を標準装備しています。")
d1,d2,d3=st.columns(3)
d1.metric("第1層","データ匿名化",help="個人名→ID、住所→都道府県、マイナンバー→入力禁止")
d2.metric("第2層","セキュアAI選定",help="Azure OpenAI / Claude API（データ学習なし保証）")
d3.metric("第3層","法的文書整備",help="守秘義務契約＋データ規程＋AI同意書の3点セット")
st.info("💡 **導入効果**: 守秘義務対応にかかる準備時間を**80%削減**（従来2週間→2日）。資格剥奪リスクを文書で明確に回避。")

st.markdown('<hr class="section-divider">',unsafe_allow_html=True)

# 共通情報の設定
st.markdown("### ⚙️ 共通情報の設定")
st.caption("以下の情報がテンプレートに反映されます。ご自身の事務所情報に書き換えてください。")
sc1,sc2=st.columns(2)
with sc1:
    office=st.text_input("事務所名",value=st.session_state["office_name"],key="inp_office")
    contact=st.text_input("担当者名",value=st.session_state["contact_person"],key="inp_contact")
    jurisdiction=st.text_input("管轄裁判所",value="東京",key="inp_jurisdiction")
with sc2:
    client=st.text_input("顧問先名",value=st.session_state["client_name"],key="inp_client")
    email=st.text_input("連絡先メール",value=st.session_state["contact_email"],key="inp_email")
    nda_duration=st.selectbox("守秘義務 契約期間",["1年","2年","3年"],index=0,key="inp_duration")
    nda_post=st.selectbox("守秘義務 終了後存続期間",["1年","2年","3年","5年"],index=1,key="inp_post")

today_str=date.today().strftime("%Y年%m月%d日")

st.markdown('<hr class="section-divider">',unsafe_allow_html=True)

# === Tabs ===
tab1,tab2,tab3=st.tabs(["📄 守秘義務契約書","📋 データ取扱い規程","✅ AI処理同意書"])

with tab1:
    st.header("📄 守秘義務契約書")
    st.caption("AI処理に関する特約条項（第4条）付きの守秘義務契約テンプレートです。")
    rendered_nda=TEMPLATE_NDA.format(
        client_name=client,office_name=office,duration=nda_duration,post_duration=nda_post,
        jurisdiction=jurisdiction,contract_date=today_str)
    st.markdown(rendered_nda)
    st.download_button("📥 守秘義務契約書をダウンロード",rendered_nda,"守秘義務契約書.md","text/markdown",use_container_width=True)

with tab2:
    st.header("📋 データ取扱い規程")
    st.caption("データ分類・AI処理ルール・匿名化手順・インシデント対応を網羅した規程テンプレートです。")
    rendered_policy=TEMPLATE_DATA_POLICY.format(office_name=office,policy_date=today_str)
    st.markdown(rendered_policy)
    st.download_button("📥 データ取扱い規程をダウンロード",rendered_policy,"データ取扱い規程.md","text/markdown",use_container_width=True)

with tab3:
    st.header("✅ AI処理同意書")
    st.caption("顧問先に署名いただく同意書テンプレートです。匿名化措置・使用AIサービス・撤回権を明記。")
    rendered_consent=TEMPLATE_AI_CONSENT.format(
        client_name=client,office_name=office,contact_person=contact,
        contact_email=email,consent_date=today_str)
    st.markdown(rendered_consent)
    st.download_button("📥 AI処理同意書をダウンロード",rendered_consent,"AI処理同意書.md","text/markdown",use_container_width=True)

# 一括ダウンロード
st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
st.markdown("### 📦 一括ダウンロード")
all_rendered=TEMPLATE_NDA.format(client_name=client,office_name=office,duration=nda_duration,post_duration=nda_post,jurisdiction=jurisdiction,contract_date=today_str)
all_rendered+="\n\n---\n\n"+TEMPLATE_DATA_POLICY.format(office_name=office,policy_date=today_str)
all_rendered+="\n\n---\n\n"+TEMPLATE_AI_CONSENT.format(client_name=client,office_name=office,contact_person=contact,contact_email=email,consent_date=today_str)
st.download_button("📥 安心パッケージ一括ダウンロード（3点セット）",all_rendered,"安心パッケージ一式.md","text/markdown",use_container_width=True)

# 相互リンク
st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
st.markdown("### 🔗 関連ツール")
fc1,fc2,fc3=st.columns(3)
fc1.markdown("📝 [契約書ドラフトAI](https://contract-draft.streamlit.app)  \n顧問契約書を自動生成")
fc2.markdown("📊 [月次レポート自動生成](https://report-gen.streamlit.app)  \n試算表CSV→レポート自動作成")
fc3.markdown("🏢 [離反予測デモ](https://shigyou-demo.streamlit.app)  \n顧問先の離反リスク予測")
st.caption("AI経営パートナー × データサイエンス | 安心パッケージ v1.1")
