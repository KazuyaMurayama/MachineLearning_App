"""
士業向け AI経営パートナー
========================
税理士・社労士・行政書士向けAIツール9アプリの専用ポータル
"""
import streamlit as st

st.set_page_config(
    page_title="士業AI経営パートナー",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === CSS ===
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563EB 100%);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.4rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.15rem; margin: 0; }
.hero-section .hero-sub { color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-top: 0.8rem; }
.kpi-card {
    text-align: center;
    padding: 20px 12px;
    background: linear-gradient(180deg, #EFF6FF, #FFFFFF);
    border-radius: 12px;
    border: 1px solid #BFDBFE;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.app-card {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 18px;
    min-height: 180px;
    transition: box-shadow 0.2s, transform 0.2s;
    background: #ffffff;
}
.app-card:hover { box-shadow: 0 6px 16px rgba(37,99,235,0.12); transform: translateY(-2px); cursor: pointer; }
.app-card .card-icon { font-size: 2rem; margin-bottom: 8px; }
.app-card .card-title { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-bottom: 6px; }
.app-card .card-desc { font-size: 0.85rem; color: #64748b; line-height: 1.6; }
.app-card .card-effect { font-size: 0.8rem; color: #2563EB; font-weight: 600; margin-top: 10px; }
.app-card .card-tag {
    display: inline-block; font-size: 0.7rem; padding: 2px 8px;
    border-radius: 999px; margin-top: 8px; font-weight: 600;
}
.tag-recommend { background: #FEF3C7; color: #92400E; }
.tag-efficiency { background: #DBEAFE; color: #1E40AF; }
.tag-compliance { background: #F3E8FF; color: #6B21A8; }
.tag-l3 { background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
.l3-section-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #7C3AED 100%);
    color: white; padding: 1rem 1.5rem; border-radius: 12px;
    margin-bottom: 1rem; font-size: 0.9rem;
}
.l3-section-banner strong { font-size: 1rem; }
.section-divider { border: none; height: 2px; background: linear-gradient(to right, #2563EB, #e2e8f0); margin: 2rem 0; }
.benefit-box {
    background: #F0F9FF;
    border: 1px solid #BAE6FD;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    min-height: 140px;
}
.benefit-box .benefit-title { font-weight: 700; color: #0C4A6E; font-size: 1rem; margin-bottom: 4px; }
.benefit-box .benefit-desc { font-size: 0.85rem; color: #475569; }
</style>
""", unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.markdown("## 🏛️ 士業AI経営パートナー")
    st.markdown("税理士・社労士・行政書士 専用")
    st.markdown("---")
    st.markdown("### 📋 ツール一覧（11アプリ）")
    st.markdown("""
**🚀 L3 AI経営パートナー（月額30万円）**
1. 🏛️ 事務所経営ダッシュボード
2. 💎 顧問先LTV予測+不採算フラグ
3. 📋 月次AIブリーフィング

**経営分析・予測（L1/L2）**
4. 🏢 顧問先離反予測
5. 🌐 サービスLP+AI経営診断
6. 🔄 クロスセル分析

**業務効率化**
7. 📊 月次レポート自動生成
8. 📝 契約書ドラフトAI
9. 💰 入金遅延アラート

**コンプライアンス**
10. 🛡️ 安心パッケージ
11. 📋 申請書類チェッカー
""")
    st.markdown("---")
    st.markdown("### 💡 このツールの対象者")
    st.markdown("""
- AI導入を検討中の士業事務所
- 顧問先の離反に悩んでいる方
- 月次業務を効率化したい方
- コンプライアンス整備が必要な方
""")
    st.markdown("---")
    st.caption("士業AI経営パートナー v2.0")

# === Hero ===
st.markdown("""
<div class="hero-section">
<h1>🏛️ 士業AI経営パートナー</h1>
<p>税理士・社労士・行政書士の業務を<br>AIで変革する 11の専用ツール</p>
<div class="hero-sub">顧問先の離反予測から契約書作成、月次レポートまでワンストップ</div>
</div>
""", unsafe_allow_html=True)

# === 導入効果 KPI ===
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="kpi-card"><div class="kpi-value">11</div><div class="kpi-label">専用AIツール</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="kpi-card"><div class="kpi-value">80%</div><div class="kpi-label">業務時間削減</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="kpi-card"><div class="kpi-value">年150h+</div><div class="kpi-label">工数削減効果</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="kpi-card"><div class="kpi-value">3士業</div><div class="kpi-label">完全対応</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === 導入メリット ===
st.markdown("### 💼 士業事務所が抱える課題を解決")
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown("""<div class="benefit-box">
<div class="benefit-title">📉 顧問先の離反が止まらない</div>
<div class="benefit-desc">→ AI離反予測で「辞めそうな顧問先」を<br>3ヶ月前に検知し、先手を打てます</div>
</div>""", unsafe_allow_html=True)
with b2:
    st.markdown("""<div class="benefit-box">
<div class="benefit-title">⏰ 月次業務に時間を取られすぎ</div>
<div class="benefit-desc">→ レポート3時間→15分、契約書2時間→10分。<br>AIが定型業務を自動化します</div>
</div>""", unsafe_allow_html=True)
with b3:
    st.markdown("""<div class="benefit-box">
<div class="benefit-title">🔒 AI導入の守秘義務が不安</div>
<div class="benefit-desc">→ 安心パッケージで守秘義務契約・<br>データ規程・AI同意書を即日整備</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === アプリURL定義 ===
APP_URLS = {
    "shigyou-office-dashboard": "https://shigyou-office-dashboard.streamlit.app",
    "shigyou-ltv": "https://shigyou-ltv.streamlit.app",
    "shigyou-briefing": "https://shigyou-briefing.streamlit.app",
    "shigyou-demo": "https://shigyou-churn.streamlit.app",
    "service-lp": "https://shigyou-service-lp.streamlit.app",
    "crosssell": "https://shigyou-crosssell.streamlit.app",
    "report-gen": "https://shigyou-report.streamlit.app",
    "contract-draft": "https://shigyou-contract.streamlit.app",
    "payment-alert": "https://shigyou-payment.streamlit.app",
    "compliance-pack": "https://shigyou-compliance.streamlit.app",
    "doc-checker": "https://shigyou-doc-check.streamlit.app",
}

# === アプリカード定義 ===
APPS = {
    "🚀 L3 AI経営パートナー（月額30万円）": [
        {"icon": "🏛️", "name": "事務所経営ダッシュボード", "desc": "8アプリのデータを1画面に集約。全顧問先の離反リスク・入金状況・クロスセル機会を俯瞰し、月次コンサル資料を5分で出力。", "dir": "shigyou-office-dashboard", "effect": "月次経営会議の資料が5分で完成", "tag": "L3新機能", "tag_class": "tag-recommend"},
        {"icon": "💎", "name": "顧問先LTV予測+不採算フラグ", "desc": "LightGBM+SHAPで顧問先1社ごとの5年間LTVを予測。VIP/成長/不採算クラスタに自動分類し、改善アクションを提示。", "dir": "shigyou-ltv", "effect": "不採算先特定→利益率5%改善", "tag": "L3新機能", "tag_class": "tag-recommend"},
        {"icon": "📋", "name": "月次AIブリーフィング", "desc": "離反リスクTOP5・入金遅延対応・クロスセル機会・翌月アクションを自動生成。月額30万円のコンサル価値を可視化。", "dir": "shigyou-briefing", "effect": "30分→5分で月次経営レポート完成", "tag": "L3新機能", "tag_class": "tag-recommend"},
    ],
    "📊 経営分析・予測": [
        {"icon": "🏢", "name": "顧問先離反予測", "desc": "LightGBM+SHAPで離反リスクを予測。逆SHAP提案で具体的な改善アクションを提示。", "dir": "shigyou-demo", "effect": "離反率15%→5%に改善", "tag": "おすすめ", "tag_class": "tag-recommend"},
        {"icon": "🌐", "name": "サービスLP+AI経営診断", "desc": "サービス紹介LPとAI経営診断ツールを統合。初回商談のインパクトを最大化。", "dir": "service-lp", "effect": "成約率30%向上", "tag": "おすすめ", "tag_class": "tag-recommend"},
        {"icon": "🔄", "name": "クロスセル分析", "desc": "顧問先カルテ・優先度ランク・トークスクリプトで追加提案を支援。", "dir": "crosssell", "effect": "顧問単価20%UP", "tag": "分析", "tag_class": "tag-efficiency"},
    ],
    "⚡ 業務効率化": [
        {"icon": "📊", "name": "月次レポート自動生成", "desc": "freee/MF試算表CSVから前月比・前年同月比・異常値検知を自動実行。", "dir": "report-gen", "effect": "利益率分析+異常値原因を自動表示", "tag": "効率化", "tag_class": "tag-efficiency"},
        {"icon": "📝", "name": "契約書ドラフトAI", "desc": "税理士・社労士・行政書士向け契約書テンプレートを自動生成。", "dir": "contract-draft", "effect": "条項解説+契約総額を自動試算", "tag": "効率化", "tag_class": "tag-efficiency"},
        {"icon": "💰", "name": "入金遅延アラート", "desc": "遅延検知・悪化傾向分析・督促テンプレート生成で未入金リスクを管理。", "dir": "payment-alert", "effect": "優先度スコアで催促を最適化", "tag": "効率化", "tag_class": "tag-efficiency"},
    ],
    "🛡️ コンプライアンス": [
        {"icon": "🛡️", "name": "安心パッケージ", "desc": "守秘義務契約・データ取扱い規程・AI処理同意書の3点セットを自動生成。", "dir": "compliance-pack", "effect": "AI導入リスク診断付き", "tag": "安心", "tag_class": "tag-compliance"},
        {"icon": "📋", "name": "申請書類チェッカー", "desc": "必要書類チェックリスト・費用/期間表示・アクションプラン提示。", "dir": "doc-checker", "effect": "審査リスク予測+解決方法を提示", "tag": "安心", "tag_class": "tag-compliance"},
    ],
}

def render_cards(apps, cols=3):
    rows = [apps[i:i+cols] for i in range(0, len(apps), cols)]
    for row in rows:
        columns = st.columns(cols)
        for col, app in zip(columns, row):
            with col:
                url = APP_URLS.get(app["dir"], "#")
                st.markdown(f"""<a href="{url}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<div class="card-icon">{app['icon']}</div>
<div class="card-title">{app['name']}</div>
<div class="card-desc">{app['desc']}</div>
<div class="card-effect">✨ {app['effect']}</div>
<span class="card-tag {app['tag_class']}">{app['tag']}</span>
</div>
</a>""", unsafe_allow_html=True)

# === カテゴリ別表示 ===
for category, apps in APPS.items():
    st.markdown(f"### {category}")
    if "L3" in category:
        st.markdown("""<div class="l3-section-banner">
<strong>🚀 L3 AI経営パートナー</strong> — データサイエンティスト採用（月50〜100万円）より安く、船井総研コンサル（月20〜50万円）と同等の経営改善価値を提供します。
</div>""", unsafe_allow_html=True)
    cols = min(len(apps), 3)
    render_cards(apps, cols=cols)
    st.markdown("")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === 導入ステップ ===
st.markdown("### 🚀 導入の流れ")
st.markdown("すべてのツールはブラウザだけで利用可能。インストール不要です。")
s1, s2, s3 = st.columns(3)
with s1:
    st.info("**Step 1: 無料体験**\n\nデモデータで全機能をお試し。サンプルデータが自動読込されるのですぐに体験できます。")
with s2:
    st.info("**Step 2: データ連携**\n\nfreee/MFのCSVエクスポートをアップロードするだけ。既存の業務フローを変える必要はありません。")
with s3:
    st.info("**Step 3: 業務に組込み**\n\n月次レポート・離反予測・入金管理をルーティンに。AIが継続的に業務をサポートします。")

# Footer
st.markdown("---")
st.caption("士業AI経営パートナー × データサイエンス | v3.0 — L3（月額30万円）プラン対応")
