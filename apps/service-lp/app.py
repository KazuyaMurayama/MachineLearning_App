"""
統合サービスLP＋AI経営診断ツール
================================
MVP #3: サービス紹介LP + 10問診断でAI活用成熟度を評価し推奨サービス層を提案
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# === 日本語フォント設定 ===
def setup_japanese_font():
    candidates=["Noto Sans CJK JP","Noto Sans JP","Yu Gothic","MS Gothic","Meiryo","DejaVu Sans"]
    available={f.name for f in fm.fontManager.ttflist}
    for fn in candidates:
        if fn in available:
            plt.rcParams["font.family"]=fn; plt.rcParams["axes.unicode_minus"]=False; return fn
    plt.rcParams["font.family"]="DejaVu Sans"; return "DejaVu Sans"

# === 定数 ===
DEMO_URL_SHIGYOU="https://shigyou-demo.streamlit.app"  # デプロイ後に更新
DEMO_URL_EC="https://ec-demo.streamlit.app"              # デプロイ後に更新
CONTACT_FORM_URL="https://forms.gle/XXXXXXXXXX"          # デプロイ後にGoogleフォーム等のURLに更新
CONTACT_EMAIL="ai-partner@example.com"                    # デプロイ後に実メールアドレスに更新

SERVICE_TIERS={
    "L1":{"name":"AI業務効率化","price":"¥5万/月","color":"#10B981","icon":"🟢",
        "features":["ChatGPT/Claude活用支援","業務プロンプト設計・テンプレート化","月次レポートのAI自動ドラフト","定型業務の自動化コンサル"]},
    "L2":{"name":"ML予測モデル","price":"¥10-12万/月","color":"#3B82F6","icon":"🔵",
        "features":["顧客離反/離脱予測（LightGBM）","売上・需要予測モデル構築","SHAP要因分析＋逆SHAP改善提案","月次モデルリトレーニング"]},
    "L3":{"name":"AI経営パートナー","price":"¥20-30万/月","color":"#6366F1","icon":"🟣",
        "features":["経営ダッシュボード構築・運用","戦略レベルAI活用コンサルティング","複数予測モデルの統合管理","月次データレビュー＋改善提案"]},
}

# === 診断質問 ===
QUESTIONS_SHIGYOU=[
    {"q":"顧問先データの管理方法は？","opts":["Excel手入力","会計ソフトの一部機能を利用","freee/MFで一元管理","API連携で自動同期"],"cat":"データ基盤"},
    {"q":"顧問先との連絡手段は？","opts":["電話・FAXのみ","メール中心","Chatwork/Slack活用","CRM＋自動リマインド"],"cat":"コミュニケーション"},
    {"q":"月次レポートの作成方法は？","opts":["手作業で毎回作成","テンプレート活用","半自動化","AIで自動生成"],"cat":"業務効率化"},
    {"q":"顧問先の解約リスク把握は？","opts":["感覚に頼っている","担当者が個別判断","KPIで定期モニタリング","予測モデルで早期検知"],"cat":"予測・分析"},
    {"q":"業務のAI活用状況は？","opts":["まったく使っていない","ChatGPTを個人利用","業務フローに一部組込","複数のAIツール連携"],"cat":"AI成熟度"},
    {"q":"請求・入金管理は？","opts":["手動でExcel管理","会計ソフトの請求機能","自動請求＋消込","AI予測で遅延事前アラート"],"cat":"業務効率化"},
    {"q":"新規顧問先の獲得チャネルは？","opts":["紹介のみ","HPあり（問合わせ少）","Web集客施策実施中","データ分析でターゲティング"],"cat":"マーケティング"},
    {"q":"スタッフの稼働・工数管理は？","opts":["把握していない","Excel/紙で記録","ツールで可視化","AI分析で最適配分"],"cat":"データ基盤"},
    {"q":"顧問先へのオプション提案は？","opts":["依頼があれば対応","年1回の定期提案","データに基づく提案","AIレコメンドで自動提案"],"cat":"予測・分析"},
    {"q":"今後のAI導入への関心度は？","opts":["関心なし","興味あるが何から始めるか不明","具体的に検討中","予算確保済みで導入準備中"],"cat":"AI成熟度"},
]

QUESTIONS_EC=[
    {"q":"顧客データの統合状況は？","opts":["バラバラ（各ツール別）","一部統合","CDPで一元管理","リアルタイム統合＋分析"],"cat":"データ基盤"},
    {"q":"顧客の離脱リスク把握は？","opts":["把握していない","購入頻度を手動確認","RFM分析を定期実施","ML予測で自動検知"],"cat":"予測・分析"},
    {"q":"需要予測・在庫管理は？","opts":["経験と勘","Excelで簡易予測","BIツール活用","ML予測モデルで自動発注"],"cat":"予測・分析"},
    {"q":"メールマーケティングは？","opts":["一斉配信のみ","セグメント配信","行動トリガーメール","AIパーソナライゼーション"],"cat":"マーケティング"},
    {"q":"広告運用の最適化は？","opts":["手動で調整","ルールベース自動化","AIツール一部活用","全チャネルAI最適化"],"cat":"マーケティング"},
    {"q":"商品レコメンドは？","opts":["なし","手動おすすめ","ルールベース","AIパーソナライズレコメンド"],"cat":"AI成熟度"},
    {"q":"カート放棄対策は？","opts":["対策なし","リマインドメール","多段階フォローアップ","AI最適タイミング配信"],"cat":"業務効率化"},
    {"q":"価格・割引戦略は？","opts":["一律割引","セール時のみ","セグメント別割引","AIダイナミックプライシング"],"cat":"AI成熟度"},
    {"q":"データ分析の頻度は？","opts":["ほぼしない","月1回レポート確認","週次ダッシュボード","リアルタイムモニタリング"],"cat":"データ基盤"},
    {"q":"AI導入への組織体制は？","opts":["担当者なし","兼務で1名","専任チーム設置","CDO/CTO主導で全社推進"],"cat":"コミュニケーション"},
]

MATURITY_LEVELS=[
    {"lv":1,"name":"AI未活用","range":(10,15),"color":"#EF4444","tier":"L1","desc":"AIの導入はこれから。まずはデータ基盤の整備とAI業務効率化から始めましょう。"},
    {"lv":2,"name":"部分的な活用","range":(16,20),"color":"#F59E0B","tier":"L1","desc":"一部でAIを活用し始めています。業務全体への展開で大きな効率化が見込めます。"},
    {"lv":3,"name":"基盤構築中","range":(21,28),"color":"#3B82F6","tier":"L2","desc":"データ基盤が整いつつあります。ML予測モデルの導入で競争優位を築けるステージです。"},
    {"lv":4,"name":"活用拡大期","range":(29,35),"color":"#10B981","tier":"L2-L3","desc":"AI活用が進んでいます。戦略レベルでの統合と高度な分析で更なる成長が可能です。"},
    {"lv":5,"name":"先進活用","range":(36,40),"color":"#6366F1","tier":"L3","desc":"AI活用の先進企業です。AI経営パートナーとして更なる高みを一緒に目指しましょう。"},
]

CATEGORIES=["データ基盤","コミュニケーション","業務効率化","予測・分析","AI成熟度","マーケティング"]

# === 改善提案マスタ ===
PROPOSALS={
    "士業":{
        1:["freee/MFへのデータ移行で分析基盤を整備","ChatGPT/Claudeで月次レポートのドラフト自動生成","Chatwork/Slackで顧問先とのデジタル連絡基盤構築","紙・FAX業務のデジタル化から着手"],
        2:["会計データのAPI連携で手入力を90%削減","AIチャットボットで顧問先からの定型質問を自動回答","請求・入金管理の自動消込でバックオフィスを効率化","顧問先データのダッシュボード化"],
        3:["顧問先の離反リスクをML予測モデルで月次スコアリング","SHAP分析で離反要因の可視化＋逆SHAPで改善アクション提案","オプションサービスのクロスセル分析","データに基づく顧問料の適正化分析"],
        4:["全顧問先のAIスコアリングダッシュボード構築","予測モデルの月次リトレーニング＋精度改善","AIを活用した新規顧問先獲得チャネル最適化","経営指標のリアルタイムモニタリング"],
        5:["経営戦略レベルでのAI活用（事業ポートフォリオ最適化）","顧問先へのAI導入支援サービスの展開","データドリブン経営の完全実現","業界内でのAI先進事務所としてのブランディング"],
    },
    "EC":{
        1:["Shopify/BASE管理画面からCSVエクスポートでデータ収集開始","顧客セグメント別のメール配信を開始","Googleアナリティクス(GA4)の基本設定を整備","在庫管理のExcelテンプレートを標準化"],
        2:["顧客データをCDPに統合し、一元管理を実現","RFM分析で顧客セグメンテーションを実施","カート放棄リマインドメールの自動化","商品カテゴリ別のABC在庫分析を定期実施"],
        3:["顧客離脱予測モデル（LightGBM）で離脱リスクを自動スコアリング","売上需要予測で在庫最適化（値引き損¥3,000-5,000万/年を削減）","逆SHAP分析で「何を変えれば離脱を防げるか」を具体提案","パーソナライズクーポンの自動配信"],
        4:["全商品のAI需要予測ダッシュボード構築","複数チャネル（SNS/広告/メール）の統合AI最適化","AIレコメンドエンジンの導入","ダイナミックプライシングの試験導入"],
        5:["全社データドリブン経営の実現","AIによる商品開発・仕入れ戦略の最適化","リアルタイム経営ダッシュボード＋自動アラート","AI活用による新規事業開発"],
    },
}

# === Page Config ===
st.set_page_config(page_title="AI経営パートナー",page_icon="🧠",layout="wide",initial_sidebar_state="collapsed")

# === Custom CSS ===
st.markdown("""
<style>
.tier-card{border-radius:12px;padding:24px;text-align:center;height:100%;transition:box-shadow 0.2s,transform 0.2s;}
.tier-card:hover{box-shadow:0 8px 24px rgba(0,0,0,0.08);transform:translateY(-2px);}
.tier-card h3{margin:0 0 8px 0;font-size:1.3rem;}
.tier-card .price{font-size:1.8rem;font-weight:bold;margin:12px 0;}
.tier-card ul{text-align:left;padding-left:20px;margin-top:16px;}
.tier-card li{margin-bottom:8px;font-size:0.95rem;}
.tier-recommended{position:relative;}
.tier-recommended::before{content:"おすすめ";position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#3B82F6;color:white;padding:2px 16px;border-radius:12px;font-size:0.8rem;font-weight:bold;}
.hero-section{text-align:center;padding:48px 0 36px 0;background:linear-gradient(180deg,#F8FAFC 0%,#FFFFFF 100%);border-radius:16px;margin-bottom:8px;}
.hero-section h1{font-size:2.4rem;margin-bottom:12px;background:linear-gradient(135deg,#6366F1,#8B5CF6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-section p{font-size:1.1rem;color:#475569;line-height:1.7;}
.credential-item{padding:16px 20px;border-left:4px solid #6366F1;margin-bottom:12px;background:#F8FAFC;border-radius:0 8px 8px 0;transition:background 0.2s;}
.credential-item:hover{background:#EEF2FF;}
.result-badge{text-align:center;padding:24px;border-radius:16px;color:white;font-size:1.2rem;}
.section-divider{border:none;border-top:2px solid #E2E8F0;margin:40px 0;}
.strength-item{padding:8px 12px;background:#F0FDF4;border-radius:8px;border-left:3px solid #10B981;margin-bottom:8px;}
.weakness-item{padding:8px 12px;background:#FFF7ED;border-radius:8px;border-left:3px solid #F59E0B;margin-bottom:8px;}
</style>
""",unsafe_allow_html=True)

# === LP描画関数 ===
def render_hero():
    st.markdown("""
<div class="hero-section">
<h1>AI経営パートナー × データサイエンス</h1>
<p>士業・小売EC事業者の経営判断を、データとAIで変革する</p>
<p>Amazon Japan広告チーム出身のデータサイエンティストが、<br>
貴社専用のAI予測モデルで「見えなかったリスク」を可視化します。</p>
</div>
""",unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    c1.metric("独自技術","逆SHAPエンジン",help="「なぜリスクが高いか」ではなく「何を変えれば防げるか」を提案")
    c2.metric("実績","新規売上 ¥7億",help="Amazon Japan広告チーム在籍時にROAS+30%改善を実現")
    c3.metric("経営×DS","MBA取得",help="経営戦略とデータサイエンスの二刀流")

def render_service_tiers():
    st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
    st.markdown("## 📋 サービスプラン")
    st.markdown("貴社の課題とAI活用段階に合わせた、3つのサービス層をご用意しています。")
    cols=st.columns(3)
    for i,(key,t) in enumerate(SERVICE_TIERS.items()):
        with cols[i]:
            features_html="".join([f"<li>{f}</li>" for f in t["features"]])
            rec_cls=' tier-recommended' if key=="L2" else ''
            st.markdown(f"""
<div class="tier-card{rec_cls}" style="border:2px solid {t['color']};background:linear-gradient(180deg,{t['color']}08,{t['color']}03);">
<h3>{t['icon']} {key}: {t['name']}</h3>
<div class="price" style="color:{t['color']};">{t['price']}</div>
<ul>{features_html}</ul>
</div>
""",unsafe_allow_html=True)
    st.caption("※ 料金は目安です。IT導入補助金の活用で最大3/4補助の可能性があります。")
    st.markdown("#### 📊 プラン比較")
    st.markdown("""
| | L1: AI業務効率化 | **L2: ML予測モデル** | L3: AI経営パートナー |
|---|---|---|---|
| 月額 | ¥5万 | **¥10-12万** | ¥20-30万 |
| AI自動化 | ○ | ○ | ○ |
| ML予測モデル | - | **○** | ○ |
| 逆SHAP改善提案 | - | **○** | ○ |
| 経営ダッシュボード | - | - | ○ |
| 戦略コンサル | - | - | ○ |
| 初期費用 | 0円 | 0円 | 応相談 |
| 契約 | 月次 | 月次 | 3ヶ月〜 |
""")

def render_demo_links():
    st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
    st.markdown("## 🎯 無料デモを体験する")
    st.markdown("実際のAI予測モデルをブラウザ上でお試しいただけます。データのアップロード不要、ワンクリックで体験可能です。")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 🏢 士業向け：顧問先離反予測AI")
        st.markdown("顧問先の離反リスクをLightGBMで予測し、**逆SHAP**で「何を変えれば離反を防げるか」を具体的に提案します。")
        st.link_button("▶️ 士業デモを試す",DEMO_URL_SHIGYOU,use_container_width=True)
    with c2:
        st.markdown("### 🛒 EC向け：顧客離脱予測AI")
        st.markdown("EC顧客の90日以内離脱リスクを予測し、需要予測・在庫ABC分析まで一気通貫で分析します。")
        st.link_button("▶️ ECデモを試す",DEMO_URL_EC,use_container_width=True)

def render_credentials():
    st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
    st.markdown("## 💼 実績・強み")
    items=[
        ("Amazon Japan 広告チーム","ROAS+30%改善、新規売上¥7億創出。大規模データ分析×広告最適化の実戦経験。"),
        ("エムスリー BIチームリード","医療データ分析基盤を構築。データドリブン意思決定の仕組みづくり。"),
        ("MBA取得","経営戦略×データサイエンスの二刀流。技術だけでなくビジネスインパクトを重視。"),
        ("独自技術「逆SHAP」","通常のSHAPが「なぜリスクが高いか」を説明するのに対し、逆SHAPは「何を変えれば防げるか」を具体的に提案。これにより、分析結果がそのまま実行可能なアクションに変わります。"),
    ]
    for title,desc in items:
        st.markdown(f'<div class="credential-item"><strong>{title}</strong><br>{desc}</div>',unsafe_allow_html=True)

def render_faq():
    st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
    st.markdown("## ❓ よくあるご質問")
    faqs=[
        ("料金体系を教えてください","L1（¥5万/月）からL3（¥20-30万/月）まで、貴社のAI活用段階に合わせてお選びいただけます。IT導入補助金の活用で最大3/4の補助を受けられる可能性があります。まずは無料診断でお見積りいたします。"),
        ("導入までどのくらいかかりますか？","初回無料診断セッション（30分）後、パイロット導入まで約2週間です。パイロット期間は50%オフでご提供し、効果を実感いただいた上で本契約に移行します。"),
        ("データの取り扱いは安全ですか？","守秘義務契約・データ取扱い規程・AI処理同意書の「安心パッケージ」を標準でご用意しています。お客様のデータは暗号化して保管し、分析目的以外には使用しません。"),
        ("どんなデータが必要ですか？","既にお使いの会計ソフト（freee/MF等）やEC管理画面（Shopify/BASE等）からCSVエクスポートするだけで対応可能です。特別な準備は不要です。"),
        ("いつでも解約できますか？","はい、月単位のご契約です。解約条件や違約金は一切ありません。"),
    ]
    for q,a in faqs:
        with st.expander(q):
            st.markdown(a)

def render_cta():
    st.markdown('<hr class="section-divider">',unsafe_allow_html=True)
    st.markdown("## 🚀 まずは無料でAI経営診断を")
    ct1,ct2=st.columns([2,1])
    with ct1:
        st.markdown("""
10問の質問に答えるだけで、貴社の**AI活用成熟度**と**最適なサービスプラン**が分かります。

所要時間はわずか**2分**。診断結果に基づいた具体的な改善提案をお届けします。
""")
        st.info("💡 上部の「🔍 AI経営診断」タブから、今すぐ無料診断をお試しください。")
    with ct2:
        st.markdown("### 📅 直接ご相談も歓迎")
        st.link_button("📅 無料診断セッションを予約する",CONTACT_FORM_URL,type="primary",use_container_width=True)
        st.markdown(f"📩 メール: **{CONTACT_EMAIL}**")

# === 診断ツール関数 ===
def calculate_score(answers):
    return sum(a+1 for a in answers)  # 選択肢index(0-3) → 点数(1-4)

def get_level(score):
    for ml in MATURITY_LEVELS:
        if ml["range"][0]<=score<=ml["range"][1]:
            return ml
    return MATURITY_LEVELS[-1] if score>40 else MATURITY_LEVELS[0]

def get_category_scores(answers,questions):
    cat_scores={c:[] for c in CATEGORIES}
    for a,q in zip(answers,questions):
        cat=q["cat"]
        if cat in cat_scores: cat_scores[cat].append(a+1)
    result={}
    for c in CATEGORIES:
        vals=cat_scores.get(c,[])
        result[c]=np.mean(vals) if vals else 0
    return result

def render_radar_chart(cat_scores):
    setup_japanese_font()
    cats=[c for c in CATEGORIES if cat_scores.get(c,0)>0]
    if len(cats)<3: return  # レーダーチャートには最低3軸必要
    values=[cat_scores[c] for c in cats]
    values.append(values[0])  # 閉じる
    angles=np.linspace(0,2*np.pi,len(cats),endpoint=False).tolist()
    angles.append(angles[0])
    fig,ax=plt.subplots(figsize=(6,6),subplot_kw=dict(polar=True))
    ax.fill(angles,values,color="#6366F1",alpha=0.15)
    ax.plot(angles,values,color="#6366F1",linewidth=2,marker="o",markersize=6)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats,fontsize=11)
    ax.set_ylim(0,4); ax.set_yticks([1,2,3,4]); ax.set_yticklabels(["1","2","3","4"],fontsize=9,color="#94A3B8")
    ax.set_title("カテゴリ別スコア",fontsize=14,fontweight="bold",pad=20)
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)

ROI_ESTIMATES={
    1:{"士業":"月次レポート自動化で**年間約120時間の工数削減**（約¥180万相当）","EC":"データ収集基盤の整備で**分析工数を月10時間削減**"},
    2:{"士業":"業務自動化で**バックオフィスコスト30%削減**（年間¥200-400万）","EC":"RFM分析＋カート放棄対策で**CVR 0.5-1%改善**（年間¥500万〜）"},
    3:{"士業":"離反率3%改善で**年間¥300-600万の売上回復**（逆SHAP活用）","EC":"離脱率1%改善で**年間¥1.2億の売上差**＋在庫最適化で値引き損¥3,000万削減"},
    4:{"士業":"全顧問先のAIスコアリングで**新規獲得コスト40%削減**","EC":"AI最適化で**広告ROAS 30%改善**＋需要予測で欠品率50%削減"},
    5:{"士業":"データドリブン経営で**意思決定スピード5倍**＋顧問先へのAI導入支援で新収益源","EC":"全社AI活用で**売上成長率2倍**＋新規事業のデータ基盤構築"},
}

PRIORITY_BADGES=["🟢 すぐ着手","🟢 すぐ着手","🟡 3ヶ月以内","🔵 半年以内"]

def render_result(score,level,biz_type,cat_scores):
    st.markdown("---")
    st.markdown("## 📊 診断結果")
    # スコア表示
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown(f'<div class="result-badge" style="background:{level["color"]};">Lv{level["lv"]} — {level["name"]}<br><span style="font-size:2.5rem;font-weight:bold;">{score}</span><span style="font-size:1rem;"> / 40点</span></div>',unsafe_allow_html=True)
    st.progress(score/40)
    st.markdown(f"**{level['desc']}**")
    # ROI推定
    roi=ROI_ESTIMATES.get(level["lv"],{}).get(biz_type,"")
    if roi:
        st.info(f"💰 **導入効果の目安**: {roi}")
    # レーダーチャート
    st.markdown("---"); st.subheader("📈 カテゴリ別分析")
    render_radar_chart(cat_scores)
    # 強み/弱み分析
    strengths=[c for c,v in cat_scores.items() if v>=3.0]
    weaknesses=[c for c,v in cat_scores.items() if 0<v<2.5]
    if strengths or weaknesses:
        sw1,sw2=st.columns(2)
        with sw1:
            st.markdown("**✅ 強み（スコア3.0以上）**")
            if strengths:
                for s in strengths: st.markdown(f'<div class="strength-item">{s}: {cat_scores[s]:.1f}/4.0</div>',unsafe_allow_html=True)
            else: st.caption("—")
        with sw2:
            st.markdown("**⚠️ 要改善（スコア2.5未満）**")
            if weaknesses:
                for w in weaknesses: st.markdown(f'<div class="weakness-item">{w}: {cat_scores[w]:.1f}/4.0</div>',unsafe_allow_html=True)
            else: st.caption("— 全カテゴリ良好です")
    # ロードマップ
    if level["lv"]<5:
        next_lv=MATURITY_LEVELS[level["lv"]]  # lv is 1-indexed, list is 0-indexed
        st.markdown("---"); st.subheader("🗺️ 改善ロードマップ")
        st.markdown(f"現在 **Lv{level['lv']}（{level['name']}）** → 目標 **Lv{next_lv['lv']}（{next_lv['name']}）**")
        st.progress(level["lv"]/5)
    # 改善提案（優先度バッジ付き）
    st.markdown("---"); st.subheader("💡 改善提案")
    proposals=PROPOSALS.get(biz_type,{}).get(level["lv"],[])
    for i,p in enumerate(proposals):
        badge=PRIORITY_BADGES[i] if i<len(PRIORITY_BADGES) else "🔵 半年以内"
        st.markdown(f"**{i+1}.** {badge} {p}")
    # 推奨サービス
    st.markdown("---"); st.subheader("🎯 推奨サービスプラン")
    tier_key=level["tier"]
    if "-" in tier_key:
        keys=tier_key.split("-")
        st.markdown(f"貴社の現在のAI活用レベルでは、**{keys[0]}**または**{keys[1]}**が最適です。")
        rcols=st.columns(len(keys))
        for i,k in enumerate(keys):
            t=SERVICE_TIERS[k]
            with rcols[i]:
                st.metric(f"{t['icon']} {k}: {t['name']}",t["price"])
                for f in t["features"]: st.markdown(f"- {f}")
    else:
        t=SERVICE_TIERS.get(tier_key,SERVICE_TIERS["L1"])
        st.markdown(f"貴社の現在のAI活用レベルでは、**{tier_key}: {t['name']}**が最適です。")
        st.metric(f"{t['icon']} {tier_key}: {t['name']}",t["price"])
        for f in t["features"]: st.markdown(f"- {f}")
    # CTA（Agent A修復）
    st.markdown("---")
    st.success("### 🎉 無料診断セッションのご案内\n\n診断結果に基づいて、貴社に最適なAI活用プランを30分の無料セッションで詳しくご説明します。\n\nパイロット導入は**50%オフ**でご提供。まずはお気軽にご相談ください。")
    cta1,cta2=st.columns(2)
    with cta1:
        st.link_button("📅 無料診断セッションを予約する",CONTACT_FORM_URL,type="primary",use_container_width=True)
    with cta2:
        demo_url=DEMO_URL_SHIGYOU if biz_type=="士業" else DEMO_URL_EC
        demo_label="🏢 士業デモを試す" if biz_type=="士業" else "🛒 ECデモを試す"
        st.link_button(demo_label,demo_url,use_container_width=True)
    st.markdown(f"📩 メールでのお問い合わせ: **{CONTACT_EMAIL}**")

def render_diagnostic():
    st.markdown("## 🔍 AI経営診断ツール")
    st.markdown("10問の質問に答えるだけで、貴社の**AI活用成熟度**を5段階で評価し、最適なサービスプランをご提案します。")
    st.markdown("---")
    # 業種選択
    biz_type=st.radio("貴社の業種を選択してください",["士業","EC"],horizontal=True,key="biz_radio")
    # 業種変更時にリセット
    if st.session_state.get("diag_biz")!=biz_type and st.session_state.get("diag_done"):
        st.session_state["diag_done"]=False
    questions=QUESTIONS_SHIGYOU if biz_type=="士業" else QUESTIONS_EC
    st.markdown("---")
    # st.formで10問をまとめて送信（rerun防止）
    with st.form("diagnosis_form"):
        st.markdown("### 以下の10問にお答えください")
        answers=[]
        for i,q in enumerate(questions):
            st.markdown(f"**Q{i+1}/10. {q['q']}** `{q['cat']}`")
            ans=st.radio(f"q{i+1}",q["opts"],key=f"q_{biz_type}_{i}",label_visibility="collapsed",horizontal=False)
            answers.append(q["opts"].index(ans))
            if i<len(questions)-1: st.markdown("")
        submitted=st.form_submit_button("📊 診断結果を見る",type="primary",use_container_width=True)
    if submitted:
        score=calculate_score(answers)
        level=get_level(score)
        cat_scores=get_category_scores(answers,questions)
        st.session_state.update({"diag_done":True,"diag_score":score,"diag_level":level,"diag_biz":biz_type,"diag_cats":cat_scores,"diag_answers":answers})
    if st.session_state.get("diag_done"):
        render_result(st.session_state["diag_score"],st.session_state["diag_level"],st.session_state["diag_biz"],st.session_state["diag_cats"])
        # 回答サマリー
        if st.session_state.get("diag_answers"):
            st.markdown("---"); st.subheader("📋 あなたの回答サマリー")
            qs=QUESTIONS_SHIGYOU if st.session_state["diag_biz"]=="士業" else QUESTIONS_EC
            for i,(a,q) in enumerate(zip(st.session_state["diag_answers"],qs)):
                pts=a+1
                bar="●"*pts+"○"*(4-pts)
                st.caption(f"Q{i+1}. {q['q']} → **{q['opts'][a]}** ({bar} {pts}/4)")
        # やり直しボタン
        st.markdown("---")
        if st.button("🔄 もう一度診断する",use_container_width=True):
            st.session_state["diag_done"]=False; st.session_state["diag_answers"]=[]
            st.rerun()

# === Session State ===
for k,v in {"diag_done":False,"diag_score":0,"diag_level":None,"diag_biz":"士業","diag_cats":{},"diag_answers":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

# === Main ===
st.title("🧠 AI経営パートナー")

tab1,tab2=st.tabs(["🏢 サービス紹介","🔍 AI経営診断"])

with tab1:
    render_hero()
    render_service_tiers()
    render_demo_links()
    render_credentials()
    render_faq()
    render_cta()

with tab2:
    render_diagnostic()
