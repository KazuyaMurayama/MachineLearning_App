"""
AI経営パートナー ポータル
========================
士業向け・EC向けAIツール12アプリの統合ポータルページ
"""
import streamlit as st

st.set_page_config(
    page_title="AI経営パートナー | ツールポータル",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === CSS ===
st.markdown("""
<style>
.portal-hero {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
}
.portal-hero h1 { color: white; font-size: 2.4rem; margin-bottom: 0.3rem; }
.portal-hero p { color: rgba(255,255,255,0.85); font-size: 1.15rem; margin: 0; }
.portal-hero .hero-sub { color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-top: 0.8rem; }
.app-card {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 18px;
    height: 100%;
    transition: box-shadow 0.2s;
    background: #ffffff;
}
.app-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.app-card .card-icon { font-size: 2rem; margin-bottom: 8px; }
.app-card .card-title { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.app-card .card-desc { font-size: 0.85rem; color: #64748b; line-height: 1.5; }
.app-card .card-tag {
    display: inline-block;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 999px;
    margin-top: 8px;
    font-weight: 600;
}
.tag-s { background: #fef3c7; color: #92400e; }
.tag-a { background: #dbeafe; color: #1e40af; }
.tag-b { background: #f3e8ff; color: #6b21a8; }
.tag-ec { background: #d1fae5; color: #065f46; }
.section-divider {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #1e293b, #e2e8f0);
    margin: 2rem 0;
}
.stat-box {
    text-align: center;
    padding: 16px;
    background: #f8fafc;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}
.stat-box .stat-value { font-size: 1.8rem; font-weight: 700; color: #1e293b; }
.stat-box .stat-label { font-size: 0.85rem; color: #64748b; }
</style>
""", unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.markdown("## 🚀 AI経営パートナー")
    st.markdown("---")
    st.markdown("### ツール一覧")
    st.markdown("""
**士業向け（9アプリ）**
- Tier S: 離反予測 / 離脱予測 / サービスLP
- Tier A: 安心パッケージ / 月次レポート / 契約書ドラフト
- Tier B: 入金遅延 / 書類チェッカー / クロスセル

**EC向け（3アプリ）**
- RFM分析 / 売上ダッシュボード / 広告ROI
""")
    st.markdown("---")
    st.markdown("### デプロイ状況")
    st.success("全12アプリ 品質チェック済")
    st.markdown("---")
    st.caption("AI経営パートナー × データサイエンス")
    st.caption("ポータル v1.0")

# === Hero ===
st.markdown("""
<div class="portal-hero">
<h1>🚀 AI経営パートナー</h1>
<p>士業 × EC の経営課題を解決する AI ツール群</p>
<div class="hero-sub">税理士・社労士・行政書士 & EC事業者向け｜全12アプリ</div>
</div>
""", unsafe_allow_html=True)

# === 統計 ===
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown('<div class="stat-box"><div class="stat-value">12</div><div class="stat-label">アプリ総数</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="stat-box"><div class="stat-value">2</div><div class="stat-label">対象セグメント</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="stat-box"><div class="stat-value">88+</div><div class="stat-label">品質スコア（点）</div></div>', unsafe_allow_html=True)
with s4:
    st.markdown('<div class="stat-box"><div class="stat-value">5,000+</div><div class="stat-label">コード行数</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === アプリカード定義 ===
APPS_SHIGYOU_S = [
    {"icon": "🏢", "name": "顧問先離反予測", "desc": "LightGBM+SHAPで離反リスクを予測。逆SHAP提案で具体的な改善アクションを提示。", "dir": "shigyou-demo", "score": 95, "tag": "Tier S", "tag_class": "tag-s"},
    {"icon": "📉", "name": "EC顧客離脱予測+需要予測", "desc": "顧客離脱リスクと需要予測を一体化。デモデータ自動生成で即体験可能。", "dir": "ec-demo", "score": 94, "tag": "Tier S", "tag_class": "tag-s"},
    {"icon": "🌐", "name": "統合サービスLP+AI経営診断", "desc": "サービス紹介LPとAI経営診断ツールを統合。初回商談のインパクトを最大化。", "dir": "service-lp", "score": 96, "tag": "Tier S", "tag_class": "tag-s"},
]
APPS_SHIGYOU_A = [
    {"icon": "🛡️", "name": "安心パッケージ", "desc": "守秘義務契約・データ取扱い規程・AI処理同意書の3点セットを自動生成。", "dir": "compliance-pack", "score": 89, "tag": "Tier A", "tag_class": "tag-a"},
    {"icon": "📊", "name": "月次レポート自動生成", "desc": "freee/MF試算表CSVから前月比・前年同月比・異常値検知を自動実行。", "dir": "report-gen", "score": 89, "tag": "Tier A", "tag_class": "tag-a"},
    {"icon": "📝", "name": "契約書ドラフトAI", "desc": "税理士・社労士・行政書士向け契約書テンプレートを自動生成。", "dir": "contract-draft", "score": 88, "tag": "Tier A", "tag_class": "tag-a"},
]
APPS_SHIGYOU_B = [
    {"icon": "💰", "name": "入金遅延アラート", "desc": "遅延検知・悪化傾向分析・督促テンプレート生成で未入金リスクを管理。", "dir": "payment-alert", "score": 88, "tag": "Tier B", "tag_class": "tag-b"},
    {"icon": "📋", "name": "申請書類チェッカー", "desc": "必要書類チェックリスト・費用/期間表示・アクションプラン提示。", "dir": "doc-checker", "score": 89, "tag": "Tier B", "tag_class": "tag-b"},
    {"icon": "🔄", "name": "クロスセル分析", "desc": "顧問先カルテ・優先度ランク・トークスクリプトで追加提案を支援。", "dir": "crosssell", "score": 90, "tag": "Tier B", "tag_class": "tag-b"},
]
APPS_EC = [
    {"icon": "👥", "name": "顧客RFM分析", "desc": "RFMスコアリング・5セグメント分類・施策提案でLTV最大化を支援。", "dir": "ec-rfm", "score": 90, "tag": "EC", "tag_class": "tag-ec"},
    {"icon": "📈", "name": "売上ダッシュボード", "desc": "日次/月次売上・異常検知・カテゴリ分析・YoY比較を一画面で。", "dir": "ec-dashboard", "score": 92, "tag": "EC", "tag_class": "tag-ec"},
    {"icon": "📣", "name": "広告ROI分析", "desc": "ROAS分析・予算配分シミュレーション・月次トレンドで広告効率を最適化。", "dir": "ec-ad-roi", "score": 91, "tag": "EC", "tag_class": "tag-ec"},
]

def render_cards(apps, cols=3):
    """アプリカードを描画"""
    rows = [apps[i:i+cols] for i in range(0, len(apps), cols)]
    for row in rows:
        columns = st.columns(cols)
        for col, app in zip(columns, row):
            with col:
                st.markdown(f"""<div class="app-card">
<div class="card-icon">{app['icon']}</div>
<div class="card-title">{app['name']}</div>
<div class="card-desc">{app['desc']}</div>
<span class="card-tag {app['tag_class']}">{app['tag']} | {app['score']}点</span>
</div>""", unsafe_allow_html=True)

# === 士業向けアプリ ===
st.markdown("## 🏛️ 士業向けAIツール（9アプリ）")
st.markdown("税理士・社労士・行政書士の業務効率化を支援するAIツール群")

st.markdown("#### Tier S — 最重要ツール")
render_cards(APPS_SHIGYOU_S)
st.markdown("")
st.markdown("#### Tier A — コンプライアンス・レポート")
render_cards(APPS_SHIGYOU_A)
st.markdown("")
st.markdown("#### Tier B — 業務分析・管理")
render_cards(APPS_SHIGYOU_B)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === EC向けアプリ ===
st.markdown("## 🛒 EC向けAIツール（3アプリ）")
st.markdown("EC事業者の売上分析・顧客管理・広告最適化を支援")
render_cards(APPS_EC)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === デプロイ情報 ===
st.markdown("## 🚀 各アプリの起動方法")
st.code("streamlit run apps/{アプリ名}/app.py", language="bash")

with st.expander("📂 全アプリのディレクトリ一覧"):
    all_apps = APPS_SHIGYOU_S + APPS_SHIGYOU_A + APPS_SHIGYOU_B + APPS_EC
    for i, app in enumerate(all_apps, 1):
        st.markdown(f"**#{i}** `apps/{app['dir']}/app.py` — {app['icon']} {app['name']}")

# Footer
st.markdown("---")
st.caption("AI経営パートナー × データサイエンス | ポータル v1.0")
