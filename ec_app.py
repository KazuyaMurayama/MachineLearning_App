"""
EC向け AI経営パートナー
========================
EC事業者向けAIツール3アプリの専用ポータル
"""
import streamlit as st

st.set_page_config(
    page_title="EC AIマーケティングパートナー",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === CSS ===
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #064E3B 0%, #059669 100%);
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
    background: linear-gradient(180deg, #ECFDF5, #FFFFFF);
    border-radius: 12px;
    border: 1px solid #A7F3D0;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #064E3B; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.app-card {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px 20px;
    min-height: 220px;
    transition: box-shadow 0.2s, transform 0.2s;
    background: #ffffff;
}
.app-card:hover { box-shadow: 0 6px 16px rgba(5,150,105,0.12); transform: translateY(-2px); cursor: pointer; }
.app-card .card-icon { font-size: 2.2rem; margin-bottom: 10px; }
.app-card .card-title { font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.app-card .card-desc { font-size: 0.88rem; color: #64748b; line-height: 1.7; }
.app-card .card-effect { font-size: 0.85rem; color: #059669; font-weight: 600; margin-top: 12px; }
.app-card .card-features {
    font-size: 0.8rem; color: #475569; margin-top: 10px;
    padding-top: 10px; border-top: 1px solid #f1f5f9;
}
.section-divider { border: none; height: 2px; background: linear-gradient(to right, #059669, #e2e8f0); margin: 2rem 0; }
.benefit-box {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    min-height: 140px;
}
.benefit-box .benefit-title { font-weight: 700; color: #064E3B; font-size: 1rem; margin-bottom: 4px; }
.benefit-box .benefit-desc { font-size: 0.85rem; color: #475569; }
.step-badge {
    display: inline-block;
    background: #059669;
    color: white;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.markdown("## 🛒 EC AIマーケティング")
    st.markdown("EC事業者 専用")
    st.markdown("---")
    st.markdown("### 📋 ツール一覧（6アプリ）")
    st.markdown("""
**🚀 L3 プレミアムパック（月額26万円）**
1. 📊 EC経営ダッシュボード
2. 🎯 What-Ifシミュレーター
3. 📰 月次AIブリーフィング

**L1/L2 スターター/グロース**
4. 👥 顧客RFM分析
5. 📈 売上ダッシュボード
6. 📣 広告ROI分析
""")
    st.markdown("---")
    st.markdown("### 💡 このツールの対象者")
    st.markdown("""
- ECサイト運営者
- マーケティング担当者
- 広告予算の最適化をしたい方
- 顧客分析を始めたい方
""")
    st.markdown("---")
    st.caption("EC AIマーケティングパートナー v2.0")

# === Hero ===
st.markdown("""
<div class="hero-section">
<h1>🛒 EC AIマーケティングパートナー</h1>
<p>EC事業の売上・顧客・広告を<br>AIで可視化・最適化する 6つの専用ツール</p>
<div class="hero-sub">顧客分析から広告最適化まで、データドリブン経営を実現</div>
</div>
""", unsafe_allow_html=True)

# === 導入効果 KPI ===
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="kpi-card"><div class="kpi-value">6</div><div class="kpi-label">専用AIツール</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="kpi-card"><div class="kpi-value">LTV</div><div class="kpi-label">最大化を支援</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="kpi-card"><div class="kpi-value">ROAS</div><div class="kpi-label">広告効率を最適化</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="kpi-card"><div class="kpi-value">即日</div><div class="kpi-label">導入可能</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === EC事業者の課題 ===
st.markdown("### 📊 EC事業者が直面する3つの課題")
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown("""<div class="benefit-box">
<div class="benefit-title">👥 顧客の顔が見えない</div>
<div class="benefit-desc">→ RFM分析で全顧客を5セグメントに分類。<br>VIP顧客と休眠顧客を即座に特定します</div>
</div>""", unsafe_allow_html=True)
with b2:
    st.markdown("""<div class="benefit-box">
<div class="benefit-title">📉 売上の変動要因が分からない</div>
<div class="benefit-desc">→ 売上ダッシュボードで異常値を自動検知。<br>日次/月次/カテゴリ別で要因を可視化</div>
</div>""", unsafe_allow_html=True)
with b3:
    st.markdown("""<div class="benefit-box">
<div class="benefit-title">💸 広告費の無駄が多い</div>
<div class="benefit-desc">→ ROAS分析で各チャネルの費用対効果を比較。<br>最適な予算配分をAIがシミュレーション</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

EC_URLS = {
    "ec-executive-dashboard": "https://ec-executive-dashboard.streamlit.app",
    "ec-what-if": "https://ec-what-if.streamlit.app",
    "ec-monthly-briefing": "https://ec-monthly-briefing.streamlit.app",
    "ec-rfm": "https://ec-rfm-analysis.streamlit.app",
    "ec-dashboard": "https://ec-sales-dashboard.streamlit.app",
    "ec-ad-roi": "https://ec-ad-roi.streamlit.app",
}

# === L3 プレミアムパック ===
st.markdown("### 🚀 L3 プレミアムパック（月額26万円）")
st.markdown("""<div style="background: linear-gradient(135deg, #064E3B 0%, #0369A1 100%); color: white; padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1rem; font-size: 0.9rem;">
<strong>🎯 GA4・Lookerでは見えない"次の一手"を提示</strong> — DataRobot（月100万円）より安く、横断分析+SHAP+逆SHAPの空白地帯を占める3つのキラー機能。
</div>""", unsafe_allow_html=True)

l1, l2, l3 = st.columns(3)
with l1:
    st.markdown(f"""<a href="{EC_URLS['ec-executive-dashboard']}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<span class="step-badge" style="background:#064E3B;">L3新機能</span>
<div class="card-icon">📊</div>
<div class="card-title">EC経営ダッシュボード</div>
<div class="card-desc">売上・広告・顧客・在庫を1画面で俯瞰。RFMセグメント×チャネルの横断ROI分析で「離脱リスク高セグメントへの広告」を特定。</div>
<div class="card-effect">✨ 月次経営会議の資料が5分で完成</div>
<div class="card-features">横断分析 / 在庫アラート / 離脱リスクTOP10</div>
</div>
</a>""", unsafe_allow_html=True)
with l2:
    st.markdown(f"""<a href="{EC_URLS['ec-what-if']}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<span class="step-badge" style="background:#0369A1;">L3キラー機能</span>
<div class="card-icon">🎯</div>
<div class="card-title">What-Ifシミュレーター</div>
<div class="card-desc">LightGBM+SHAPで「広告費を30%増やすとROASはどうなるか」をリアルタイム予測。現状/案A/案Bの3シナリオ比較で意思決定を加速。</div>
<div class="card-effect">✨ GA4・Lookerにない唯一無二の機能</div>
<div class="card-features">逆SHAP / 3モデル学習 / シナリオ比較</div>
</div>
</a>""", unsafe_allow_html=True)
with l3:
    st.markdown(f"""<a href="{EC_URLS['ec-monthly-briefing']}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<span class="step-badge" style="background:#D97706;">L3新機能</span>
<div class="card-icon">📰</div>
<div class="card-title">月次AIブリーフィング</div>
<div class="card-desc">チャネル別ROI・離脱リスク顧客TOP20・翌月アクション3件を自動生成。月次経営会議の資料をMarkdownで出力。</div>
<div class="card-effect">✨ 月額26万円の伴走支援を可視化</div>
<div class="card-features">自動サマリー / 次月アクション / MDレポート</div>
</div>
</a>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === 3ツールの連携フロー（モバイル対応: 縦並び） ===
st.markdown("### 🔄 L1/L2 コアツール — 3ツール連携でEC経営を最適化")
st.markdown("**RFM → ダッシュボード → 広告ROI** の順に活用し、分析→把握→最適化を実現")
st.markdown("")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<a href="{EC_URLS['ec-rfm']}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<span class="step-badge">Step 1</span>
<div class="card-icon">👥</div>
<div class="card-title">顧客RFM分析</div>
<div class="card-desc">購買データから顧客をVIP/優良/一般/休眠/離脱の5セグメントに自動分類。セグメント別の施策提案まで。</div>
<div class="card-effect">✨ リピート率15%向上</div>
<div class="card-features">R(最終購入日) × F(購入回数) × M(購入金額)</div>
</div>
</a>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<a href="{EC_URLS['ec-dashboard']}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<span class="step-badge">Step 2</span>
<div class="card-icon">📈</div>
<div class="card-title">売上ダッシュボード</div>
<div class="card-desc">日次・月次売上を一画面で把握。±2σの異常値を自動検知し、カテゴリ別・YoY比較で深掘り。</div>
<div class="card-effect">✨ 異常値の即日検知</div>
<div class="card-features">日次推移 / カテゴリ分析 / 前年比較</div>
</div>
</a>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<a href="{EC_URLS['ec-ad-roi']}" target="_blank" style="text-decoration:none;color:inherit;">
<div class="app-card">
<span class="step-badge">Step 3</span>
<div class="card-icon">📣</div>
<div class="card-title">広告ROI分析</div>
<div class="card-desc">Google/Meta/LINE等チャネル別ROAS分析。ROAS加重の最適予算配分をシミュレーション。</div>
<div class="card-effect">✨ 広告効率30%改善</div>
<div class="card-features">ROAS分析 / 予算配分 / 月次トレンド</div>
</div>
</a>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === 導入ステップ ===
st.markdown("### 🚀 導入の流れ")
st.markdown("すべてのツールはブラウザだけで利用可能。インストール不要です。")
s1, s2, s3 = st.columns(3)
with s1:
    st.info("**Step 1: 無料体験**\n\nデモデータで全機能をお試し。500顧客・731日分の売上データが自動読込されます。")
with s2:
    st.info("**Step 2: データ連携**\n\nShopify/BASE/楽天のCSVエクスポートをアップロードするだけ。特別な設定は不要です。")
with s3:
    st.info("**Step 3: 週次ルーティン化**\n\n毎週の売上チェック・月次の顧客分析・四半期の広告見直しをAIがサポートします。")

# Footer
st.markdown("---")
st.caption("EC AIマーケティングパートナー × データサイエンス | v3.0 — L3プレミアムパック（月額26万円）対応")
