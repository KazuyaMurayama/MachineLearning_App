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
        "estimated_cost": "15〜30万円（行政書士報酬含む）",
        "prep_days": "2〜4週間",
        "window_info": "都道府県の建設業課（例: 東京都 都市整備局）",
        "items": [
            {
                "name": "建設業許可申請書（様式第1号）",
                "required": True,
                "point": "押印漏れ・記載ミスに注意。法人の場合は代表者印必須",
                "ng_example": "代表者氏名の旧字体・略字の使用、印鑑の欠落",
                "resolution": "都道府県の建設業課HPから最新様式をダウンロードし記入",
                "source": "都道府県建設業課HP",
                "days_needed": "1〜2日",
            },
            {
                "name": "工事経歴書（様式第2号）",
                "required": True,
                "point": "過去5年分の主要完成工事を記載。件数・金額の整合性を確認",
                "ng_example": "記載件数が少ない、金額が財務諸表と不一致",
                "resolution": "過去5年の完成工事台帳・請求書等を基に一覧を作成",
                "source": "自社の工事台帳・契約書控え",
                "days_needed": "3〜5日",
            },
            {
                "name": "直前3年の財務諸表（貸借対照表・損益計算書）",
                "required": True,
                "point": "決算期ごとに作成。自己資本額の確認（一般許可: 500万円以上）",
                "ng_example": "確定申告書との数値乖離、税理士署名なし",
                "resolution": "顧問税理士に建設業許可用の財務諸表作成を依頼",
                "source": "顧問税理士・会計事務所",
                "days_needed": "1〜2週間",
            },
            {
                "name": "誓約書（様式第6号）",
                "required": True,
                "point": "欠格要件に該当しないことの誓約。全役員・令3条使用人の分が必要",
                "ng_example": "役員全員分がそろっていない",
                "resolution": "全役員・令3条使用人の一覧を作成し、各人に署名押印を依頼",
                "source": "都道府県建設業課HP（様式ダウンロード）",
                "days_needed": "1〜3日",
            },
            {
                "name": "専任技術者の資格証明書類",
                "required": True,
                "point": "資格証のコピーまたは実務経験証明書。有効期限・業種の一致を確認",
                "ng_example": "資格と申請業種が一致しない、実務経験年数の不足",
                "resolution": "資格証のコピーを取得。実務経験の場合は経験証明書を元勤務先に依頼",
                "source": "資格証原本コピー／元勤務先",
                "days_needed": "1〜2週間",
            },
            {
                "name": "経営業務の管理責任者の証明書類",
                "required": True,
                "point": "5年以上の経営経験を証明する書類（決算書・契約書等）",
                "ng_example": "経験年数の根拠書類が薄い、期間に空白がある",
                "resolution": "過去の決算書・確定申告書・契約書等の年次一覧を整理",
                "source": "自社保管書類・税務署（過去の申告書控え）",
                "days_needed": "1〜2週間",
            },
            {
                "name": "登記されていないことの証明書",
                "required": True,
                "point": "成年後見・被保佐人に登記されていないことの証明。発行後3ヶ月以内",
                "ng_example": "有効期限切れ（発行から3ヶ月超過）",
                "how_to_get": "法務局（東京法務局後見登録課）で取得。郵送申請も可",
                "resolution": "法務局で「登記されていないことの証明書」を申請取得",
                "source": "法務局（東京法務局後見登録課）、郵送申請可",
                "days_needed": "3〜5営業日",
            },
            {
                "name": "身分証明書（本籍地の市区町村発行）",
                "required": True,
                "point": "禁治産・準禁治産・破産の登録がないことの証明。発行後3ヶ月以内",
                "ng_example": "住民票では不可（身分証明書と別物）",
                "resolution": "本籍地の市区町村役場で「身分証明書」を取得（郵送請求可）",
                "source": "本籍地の市区町村役場",
                "days_needed": "3〜7営業日（郵送の場合）",
            },
            {
                "name": "法人の登記事項証明書",
                "required": True,
                "point": "法人の場合必須。発行後3ヶ月以内のもの",
                "ng_example": "個人事業主申請に法人登記を添付する誤り",
                "how_to_get": "法務局（オンライン申請可: 登記・供託オンラインシステム）",
                "resolution": "法務局で取得（オンライン申請可）、手数料¥600",
                "source": "法務局（登記・供託オンラインシステム）",
                "days_needed": "3〜5営業日",
            },
            {
                "name": "納税証明書（法人税・消費税）",
                "required": True,
                "point": "未納がないことの証明。都道府県・国税の両方が必要な場合あり",
                "ng_example": "消費税分の証明書が漏れている",
                "how_to_get": "税務署（e-Taxで取得可能）。都道府県税は各都道府県税事務所",
                "resolution": "税務署でe-Tax申請、都道府県税事務所で都道府県税分を取得",
                "source": "税務署（e-Tax）／都道府県税事務所",
                "days_needed": "3〜5営業日",
            },
        ],
    },
    "飲食店営業許可申請": {
        "icon": "🍽️",
        "description": "食品衛生法に基づく飲食店営業許可の申請書類チェック",
        "authority": "保健所（都道府県/政令市）",
        "standard_days": "10〜20日（施設検査を含む）",
        "estimated_cost": "3〜10万円",
        "prep_days": "1〜2週間",
        "window_info": "管轄の保健所 衛生課（事前相談推奨）",
        "items": [
            {
                "name": "飲食店営業許可申請書",
                "required": True,
                "point": "保健所指定の様式を使用。開業予定日の2〜3週間前に申請",
                "ng_example": "古い様式の使用、開業後の申請",
                "resolution": "管轄保健所HPから最新の申請書様式をダウンロードし記入",
                "source": "管轄保健所HP",
                "days_needed": "1日",
            },
            {
                "name": "食品衛生責任者資格証明書（コピー）",
                "required": True,
                "point": "調理師免許・栄養士免許または講習会修了証。1施設につき1名以上",
                "ng_example": "資格者が他店舗との兼任（原則不可）",
                "how_to_get": "各都道府県の食品衛生協会で養成講習会を受講（1日・約1万円）",
                "resolution": "食品衛生協会の養成講習会を受講し修了証を取得（約1万円）",
                "source": "各都道府県の食品衛生協会",
                "days_needed": "1日（講習）+ 予約待ち1〜2週間",
            },
            {
                "name": "施設の平面図（厨房レイアウト）",
                "required": True,
                "point": "設備の配置・寸法を記載。手洗い設備の位置・2槽シンクの確認",
                "ng_example": "縮尺不明・設備の省略、手洗い場の位置が不適切",
                "resolution": "内装業者または設計士に平面図作成を依頼。保健所で事前相談推奨",
                "source": "内装業者・設計士／保健所で事前相談",
                "days_needed": "3〜7日",
            },
            {
                "name": "水質検査成績書（井戸水使用の場合）",
                "required": False,
                "point": "水道水の場合は不要。井戸水・地下水を使用する場合は直近の検査結果",
                "ng_example": "1年以上前の古い検査結果の使用",
                "resolution": "登録検査機関に水質検査を依頼（検査費用約1〜3万円）",
                "source": "登録水質検査機関",
                "days_needed": "1〜2週間",
            },
            {
                "name": "営業許可申請手数料（収入証紙/現金）",
                "required": True,
                "point": "都道府県により金額が異なる（例: 東京都 18,300円）。支払方法要確認",
                "ng_example": "金額不足、収入証紙の貼付方法の誤り",
                "resolution": "管轄保健所に金額・支払方法を確認のうえ準備",
                "source": "管轄保健所窓口",
                "days_needed": "即日",
            },
            {
                "name": "建物の使用権限を証明する書類",
                "required": True,
                "point": "自己所有: 登記事項証明書。賃貸: 賃貸借契約書（飲食店可の記載確認）",
                "ng_example": "賃貸借契約書に飲食店可の明記なし",
                "resolution": "自己所有は法務局で登記事項証明書を取得。賃貸は契約書コピーを準備",
                "source": "法務局／不動産管理会社",
                "days_needed": "1〜5日",
            },
            {
                "name": "法人の登記事項証明書（法人の場合）",
                "required": False,
                "point": "法人申請の場合のみ必要。発行後3ヶ月以内",
                "ng_example": "個人事業主申請に法人書類を混同",
                "resolution": "法務局で登記事項証明書を取得（オンライン申請可）、手数料¥600",
                "source": "法務局（登記・供託オンラインシステム）",
                "days_needed": "3〜5営業日",
            },
            {
                "name": "既存施設の検査済証（リノベーションの場合）",
                "required": False,
                "point": "既存建物の改装の場合は建築確認済証等が必要になることがある",
                "ng_example": "無確認で大規模改装後に申請",
                "resolution": "建物所有者・管理会社から検査済証のコピーを入手",
                "source": "建物所有者・管理会社／市区町村建築課",
                "days_needed": "3〜7日",
            },
        ],
    },
    "就業規則届出": {
        "icon": "📋",
        "description": "常時10人以上の従業員がいる事業場の就業規則届出（労働基準法第89条）",
        "authority": "所轄労働基準監督署",
        "standard_days": "受理即日〜1週間（届出のみ）",
        "estimated_cost": "10〜30万円（社労士報酬含む）",
        "prep_days": "2〜4週間",
        "window_info": "所轄労働基準監督署 監督課",
        "items": [
            {
                "name": "就業規則届（様式第9号）",
                "required": True,
                "point": "事業場単位で提出。本社・支店別に届出が必要。2部提出（控え受領）",
                "ng_example": "本社のみ提出で支店分が漏れる",
                "resolution": "厚生労働省HPから様式第9号をダウンロードし記入",
                "source": "厚生労働省HP",
                "days_needed": "1日",
            },
            {
                "name": "就業規則本文",
                "required": True,
                "point": "絶対的必要記載事項（始業・終業時刻、休日、賃金等）の欠落がないか確認",
                "ng_example": "育児・介護休業、ハラスメント防止規程の未整備",
                "resolution": "社労士に作成・レビューを依頼。厚労省のモデル就業規則を参考に作成",
                "source": "社労士／厚生労働省モデル就業規則",
                "days_needed": "1〜3週間",
            },
            {
                "name": "意見書（労働者代表の署名・押印付き）",
                "required": True,
                "point": "過半数労働組合または過半数代表者の意見書。同意でなく意見書でOK",
                "ng_example": "代表者の選出方法が適切でない（挙手・互選でなく使用者指名）",
                "resolution": "労働者代表を適正に選出し、就業規則案を提示のうえ意見書に署名押印を取得",
                "source": "労働者代表（社内選出）",
                "days_needed": "3〜7日",
            },
            {
                "name": "労働者代表者の選出根拠書類",
                "required": True,
                "point": "代表者の選出方法・日時・氏名を記録。メール・投票の記録が望ましい",
                "ng_example": "「管理職が代表者」は不可（法定違反）",
                "resolution": "挙手・投票・メール回覧等で代表者を選出し、選出記録を書面化",
                "source": "社内手続き（投票・メール記録等）",
                "days_needed": "1〜3日",
            },
            {
                "name": "別規程（育児・介護休業規程）",
                "required": True,
                "point": "育児介護休業法改正対応の内容か確認。2022年・2023年改正への対応",
                "ng_example": "古いバージョンのまま提出（産後パパ育休未対応）",
                "resolution": "最新の育児介護休業法に対応した規程を社労士に作成依頼",
                "source": "社労士／厚生労働省の規程例",
                "days_needed": "1〜2週間",
            },
            {
                "name": "別規程（ハラスメント防止規程）",
                "required": True,
                "point": "パワハラ防止措置（指針対応）、セクハラ・マタハラ規定を含む",
                "ng_example": "パワハラの定義が法律と乖離している",
                "resolution": "厚生労働省指針に準拠したハラスメント防止規程を社労士に作成依頼",
                "source": "社労士／厚生労働省ハラスメント防止指針",
                "days_needed": "1〜2週間",
            },
            {
                "name": "別規程（テレワーク・副業に関する規程）",
                "required": False,
                "point": "テレワーク実施・副業許可の場合は別規程または本規程への記載推奨",
                "ng_example": "テレワーク実施中なのに労働時間管理の規定がない",
                "resolution": "厚生労働省テレワークガイドラインを参考に規程を整備",
                "source": "社労士／厚生労働省ガイドライン",
                "days_needed": "1〜2週間",
            },
            {
                "name": "賃金規程（賃金に関する別規程）",
                "required": False,
                "point": "本規程に賃金の詳細を定めず別規程とする場合は別途届出が必要",
                "ng_example": "賃金規程を別規程にしたが未届出",
                "resolution": "賃金テーブル・手当一覧を整理し、社労士に賃金規程作成を依頼",
                "source": "社労士",
                "days_needed": "1〜2週間",
            },
            {
                "name": "36協定（時間外・休日労働協定）",
                "required": False,
                "point": "時間外労働がある場合は36協定も届出が必要（就業規則とセットで確認）",
                "ng_example": "就業規則の時間外規定と36協定の上限が矛盾",
                "resolution": "労働基準監督署へ36協定届を届出（費用無料）",
                "source": "労働基準監督署",
                "days_needed": "1〜2週間",
            },
            {
                "name": "旧就業規則（変更届の場合）",
                "required": False,
                "point": "変更届の場合は変更前の就業規則の写しを添付（署の指示による）",
                "ng_example": "変更届なのに旧版を添付しない",
                "resolution": "現行の就業規則の写しを準備（社内保管分をコピー）",
                "source": "自社保管書類",
                "days_needed": "即日",
            },
        ],
    },
    "社会保険新規適用届": {
        "icon": "🏥",
        "description": "法人設立・従業員雇用時の社会保険（健康保険・厚生年金）新規適用手続き",
        "authority": "所轄年金事務所",
        "standard_days": "受理後5〜10日（保険証交付）",
        "estimated_cost": "3〜5万円（社労士報酬含む）",
        "prep_days": "3〜5日",
        "window_info": "所轄年金事務所（日本年金機構）/ e-Gov電子申請可",
        "items": [
            {
                "name": "健康保険・厚生年金保険新規適用届",
                "required": True,
                "point": "事業所の所在地・名称・事業主氏名を正確に記載。法人番号の記入を忘れずに",
                "ng_example": "法人番号の誤り、事業所名が登記と不一致",
                "how_to_get": "日本年金機構HPからダウンロード。e-Gov電子申請でも提出可",
                "resolution": "日本年金機構HPから様式をダウンロードし記入。e-Gov電子申請でも提出可",
                "source": "日本年金機構HP／e-Gov",
                "days_needed": "1日",
            },
            {
                "name": "法人の登記事項証明書（原本）",
                "required": True,
                "point": "発行後3ヶ月以内のもの。事業内容・所在地が申請書と一致しているか確認",
                "ng_example": "本店移転後の旧住所で申請",
                "how_to_get": "法務局（オンライン申請可: 登記・供託オンラインシステム）",
                "resolution": "法務局で登記事項証明書を取得（オンライン申請可）、手数料¥600",
                "source": "法務局（登記・供託オンラインシステム）",
                "days_needed": "3〜5営業日",
            },
            {
                "name": "被保険者資格取得届（従業員全員分）",
                "required": True,
                "point": "採用日・生年月日・基本給・報酬月額を正確に記入。マイナンバー記載",
                "ng_example": "試用期間中の従業員を漏らす、報酬月額の計算誤り",
                "resolution": "日本年金機構HPから様式をダウンロードし、従業員ごとに記入",
                "source": "日本年金機構HP",
                "days_needed": "1〜2日",
            },
            {
                "name": "事業所の賃貸借契約書または登記事項証明書",
                "required": True,
                "point": "実態のある事業所があることを証明。自宅兼事務所の場合も必要",
                "ng_example": "バーチャルオフィスのみで実態なしと判断される",
                "resolution": "賃貸の場合は管理会社から契約書コピーを取得。自己所有は法務局で登記事項証明書を取得",
                "source": "不動産管理会社／法務局",
                "days_needed": "1〜5日",
            },
            {
                "name": "労働保険関係成立届の控え（雇用保険適用事業所の場合）",
                "required": False,
                "point": "雇用保険の適用事業所である場合は、労働保険の成立届控えを添付",
                "ng_example": "雇用保険を未手続きのまま社保のみ申請",
                "resolution": "ハローワークで労働保険関係成立届を提出し、控えを取得",
                "source": "ハローワーク（公共職業安定所）",
                "days_needed": "1〜3日",
            },
            {
                "name": "役員報酬を決めた議事録（役員の場合）",
                "required": False,
                "point": "役員の報酬月額の根拠として株主総会議事録・取締役会議事録が必要",
                "ng_example": "議事録がなく役員報酬の根拠を証明できない",
                "resolution": "株主総会または取締役会を開催し、役員報酬決議の議事録を作成",
                "source": "自社作成（必要に応じ司法書士に依頼）",
                "days_needed": "1〜3日",
            },
            {
                "name": "賃金台帳・タイムカード等の写し",
                "required": False,
                "point": "求められる場合あり。報酬月額の根拠として使用。直近3ヶ月分が目安",
                "ng_example": "給与明細だけでタイムカードがない",
                "resolution": "直近3ヶ月分の賃金台帳・タイムカードを社内で整理しコピーを準備",
                "source": "自社保管書類（給与計算システム等）",
                "days_needed": "1〜2日",
            },
            {
                "name": "マイナンバー収集同意書・本人確認書類",
                "required": True,
                "point": "従業員のマイナンバーを収集する際の同意書と本人確認（コピー）が必要",
                "ng_example": "マイナンバーのみ提供でID確認書類がない",
                "resolution": "従業員にマイナンバー通知カード+身分証のコピー提出を依頼。同意書を配布・回収",
                "source": "従業員本人（社内回収）",
                "days_needed": "3〜7日",
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
    initial_sidebar_state="expanded"
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
# Sidebar — 使い方ガイド
# ============================================================
with st.sidebar:
    st.markdown("## 📖 使い方ガイド")
    st.markdown(
        "**3ステップで書類チェック完了!**\n\n"
        "1. **書類種別を選択** — チェックしたい申請種別を選びます\n"
        "2. **各書類をチェック** — 準備状況を「済 / 未済 / 該当なし」で入力\n"
        "3. **結果を確認** — 不備一覧・完了率・アクションプランを確認\n"
    )
    st.markdown("---")
    st.markdown("### 対応書類種別")
    for doc_key, cl_data in CHECKLISTS.items():
        st.markdown(f"{cl_data['icon']} **{doc_key}**")
    st.markdown("---")
    st.caption("**AI経営パートナー × データサイエンス**")
    st.caption("申請書類チェッカー v1.0")

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
    col_info3, col_info4 = st.columns(2)
    col_info3.markdown(f"- **費用目安**: {cl['estimated_cost']}")
    col_info4.markdown(f"- **準備期間**: {cl['prep_days']}")
    st.markdown(f"- **申請窓口**: {cl['window_info']}")
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

        # 審査リスク判定
        if completion_rate == 100:
            risk_label = "🟢 低リスク"
            risk_level = "low"
        elif completion_rate >= 80:
            risk_label = "🟡 中リスク"
            risk_level = "medium"
        else:
            risk_label = "🔴 高リスク"
            risk_level = "high"

        # KPIカード
        kc1, kc2, kc3, kc4, kc5 = st.columns(5)
        kc1.metric("必須項目 完了率", f"{completion_rate:.0f}%", f"{required_ok}/{required_total}件")
        kc2.metric("✅ 準備完了", f"{len(ok_items)}件")
        kc3.metric("❌ 未済（必須）", f"{len(ng_items)}件",
                   delta=f"-{len(ng_items)}" if ng_items else None,
                   delta_color="inverse")
        kc4.metric("➖ 該当なし", f"{len(na_items)}件")
        kc5.metric("審査リスク", risk_label)

        # プログレスバー
        st.markdown(f'<div class="progress-label">必須書類 完了率: {completion_rate:.0f}%</div>', unsafe_allow_html=True)
        st.progress(completion_rate / 100)

        if completion_rate == 100:
            st.success("🎉 必須書類はすべて準備完了です！申請可能な状態です。")
        elif completion_rate >= 80:
            st.warning(f"📋 あと少し！必須書類 {len(ng_items)}件 の準備を完了させてから申請してください。")
        else:
            st.error(f"⚠️ 必須書類 {len(ng_items)}件 が未済です。申請前に必ずご対応ください。")

        # 審査リスク補足
        if risk_level == "low":
            st.info("🟢 **審査リスク: 低** — 必須書類がすべて揃っています。高確率で審査を通過できる見込みです。")
        elif risk_level == "medium":
            st.warning("🟡 **審査リスク: 中** — 必須書類の大部分は揃っていますが、不備指摘を受ける可能性があります。未済書類を早急に準備してください。")
        else:
            st.error("🔴 **審査リスク: 高** — 必須書類の準備が不十分です。このまま申請すると審査不通過の可能性が高いため、未済書類の準備を優先してください。")

        # 不備リスト（必須）
        if ng_items:
            st.markdown("### ❌ 未済の必須書類（要対応）")
            for r in ng_items:
                resolution = r["item"].get("resolution", "")
                source = r["item"].get("source", "")
                days = r["item"].get("days_needed", "")
                resolution_html = f'<small>🛠️ 解決方法: {resolution}</small><br>' if resolution else ""
                source_html = f'<small>📍 入手先: {source}</small><br>' if source else ""
                days_html = f'<small>⏱️ 所要日数: {days}</small>' if days else ""
                st.markdown(
                    f'<div class="check-item-ng">❌ <b>{r["item"]["name"]}</b><br>'
                    f'<small>📌 {r["item"]["point"]}</small><br>'
                    f'<small>⚠️ よくある不備: {r["item"]["ng_example"]}</small><br>'
                    f'{resolution_html}{source_html}{days_html}</div>',
                    unsafe_allow_html=True
                )

        # 任意・未済
        if ng_optional:
            st.markdown("### ⚠️ 未済の任意書類（状況により必要）")
            for r in ng_optional:
                resolution = r["item"].get("resolution", "")
                source = r["item"].get("source", "")
                days = r["item"].get("days_needed", "")
                resolution_html = f'<small>🛠️ 解決方法: {resolution}</small><br>' if resolution else ""
                source_html = f'<small>📍 入手先: {source}</small><br>' if source else ""
                days_html = f'<small>⏱️ 所要日数: {days}</small>' if days else ""
                st.markdown(
                    f'<div class="check-item-ng">❌ <b>{r["item"]["name"]}</b>【任意】<br>'
                    f'<small>📌 {r["item"]["point"]}</small><br>'
                    f'{resolution_html}{source_html}{days_html}</div>',
                    unsafe_allow_html=True
                )

        # 完了済みリスト
        if ok_items:
            with st.expander(f"✅ 準備完了の書類 ({len(ok_items)}件)"):
                for r in ok_items:
                    req = "【必須】" if r["item"]["required"] else "【任意】"
                    st.markdown(f'<div class="check-item-ok">✅ {req} {r["item"]["name"]}</div>', unsafe_allow_html=True)

        # アクションプラン
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("### 🚀 次のアクション")
        if ng_items:
            st.markdown("未済の必須書類を準備しましょう。以下に入手先・準備方法のヒントをまとめます。")
            for r in ng_items:
                how = r["item"].get("how_to_get", "")
                if how:
                    st.markdown(f"- **{r['item']['name']}** → {how}")
                else:
                    st.markdown(f"- **{r['item']['name']}** → 申請先窓口にお問い合わせください")
        else:
            st.success("全ての必須書類が準備完了です! 申請先に事前相談の予約を取りましょう。")
            st.markdown(f"**申請窓口**: {cl['window_info']}")

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
            st.markdown(f"**費用目安**: {cl_data['estimated_cost']}　|　**準備期間**: {cl_data['prep_days']}　|　**窓口**: {cl_data['window_info']}")
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
_card=lambda icon,title,url,desc,action: f'<div style="border:1px solid #E2E8F0;border-radius:12px;padding:20px;text-align:center;height:100%;"><div style="font-size:2rem;">{icon}</div><h4 style="margin:8px 0 4px;"><a href="{url}" target="_blank" style="text-decoration:none;color:#0891B2;">{title}</a></h4><p style="font-size:.85rem;color:#475569;margin:0 0 8px;">{desc}</p><small style="color:#059669;">▶ {action}</small></div>'
fc1, fc2, fc3 = st.columns(3)
fc1.markdown(_card("🛡️","安心パッケージ","https://shigyou-compliance.streamlit.app","AI導入コンプライアンス対応","AI導入のコンプライアンス準備"),unsafe_allow_html=True)
fc2.markdown(_card("📝","契約書ドラフトAI","https://shigyou-contract.streamlit.app","顧問契約書を自動生成","顧問契約書の自動生成"),unsafe_allow_html=True)
fc3.markdown(_card("🏠","士業ポータル","https://shigyou-ai-tools.streamlit.app","全ツール一覧","全ツール一覧"),unsafe_allow_html=True)
st.caption("AI経営パートナー × データサイエンス | 申請書類チェッカー v1.0")
