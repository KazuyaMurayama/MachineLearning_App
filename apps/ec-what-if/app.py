"""
EC What-If シミュレーター
==========================
逆SHAP What-Ifシミュレーター: LightGBM予測 + SHAP解釈 + インタラクティブ入力
L3プレミアムのキラー機能
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import lightgbm as lgb
import shap


# ──────────────────────────────────────────────
# 日本語フォント設定
# ──────────────────────────────────────────────
def setup_japanese_font():
    """利用可能な日本語フォントを探して設定する。"""
    japanese_fonts = ["Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic", "MS Gothic", "Meiryo", "DejaVu Sans"]
    available = [f.name for f in fm.fontManager.ttflist]
    for font in japanese_fonts:
        if font in available:
            plt.rcParams["font.family"] = font
            plt.rcParams["font.sans-serif"] = [font]
            plt.rcParams["axes.unicode_minus"] = False
            return font
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    return None


_font = setup_japanese_font()


# ──────────────────────────────────────────────
# ページ設定
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="EC What-If シミュレーター",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ──────────────────────────────────────────────
# CSS注入
# ──────────────────────────────────────────────
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #059669 0%, #0369A1 100%);
    color: white; padding: 2rem; border-radius: 16px;
    text-align: center; margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.2rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0; }
.kpi-card {
    text-align: center; padding: 18px 12px;
    background: linear-gradient(180deg, #ECFDF5, #FFFFFF);
    border-radius: 12px; border: 1px solid #A7F3D0;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #065F46; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.scenario-card {
    background: #F0F9FF; border: 1px solid #BAE6FD;
    border-radius: 10px; padding: 16px; margin: 8px 0;
}
.diff-positive { color: #059669; font-weight: 700; }
.diff-negative { color: #DC2626; font-weight: 700; }
.section-divider { border: none; height: 2px; background: linear-gradient(to right, #0369A1, #e2e8f0); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# データ読み込み + LightGBM学習 (cache_resource)
# ──────────────────────────────────────────────
FEATURE_COLS = [
    "チャネル_enc", "カテゴリ_enc", "広告費", "インプレッション", "クリック",
    "価格指数", "在庫水準", "月", "季節係数", "Champions比率"
]
FEATURE_DISPLAY = [
    "チャネル", "カテゴリ", "広告費", "インプレッション", "クリック",
    "価格指数", "在庫水準", "月", "季節係数", "Champions比率"
]
TARGET_COLS = ["売上", "ROAS", "離脱率"]


@st.cache_resource
def train_models():
    """LightGBMモデルを3つ学習し、SHAP値を含む辞書を返す。"""
    import create_sample_data
    data_path = os.path.join(os.path.dirname(__file__), "sample_data", "training_data.csv")
    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # LabelEncoder
    le_ch = LabelEncoder()
    le_cat = LabelEncoder()
    df["チャネル_enc"] = le_ch.fit_transform(df["チャネル"])
    df["カテゴリ_enc"] = le_cat.fit_transform(df["カテゴリ"])

    X = df[FEATURE_COLS]
    results = {}
    shap_values_dict = {}
    X_shap_dict = {}

    for target in TARGET_COLS:
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, pred)
        rmse = float(np.sqrt(np.mean((y_test - pred) ** 2)))
        r2 = r2_score(y_test, pred)

        # SHAP
        explainer = shap.TreeExplainer(model)
        sample_size = min(200, len(X_test))
        X_shap = X_test.iloc[:sample_size].copy()
        sv = explainer.shap_values(X_shap)

        results[target] = {
            "model": model,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "X_test": X_test,
            "y_test": y_test,
            "pred": pred,
        }
        shap_values_dict[target] = sv
        X_shap_dict[target] = X_shap

    # ベースライン（全データ平均）
    baselines = {col: float(df[col].mean()) for col in TARGET_COLS}
    # チャネル・カテゴリのリスト
    channels = sorted(df["チャネル"].unique().tolist())
    cat_list = sorted(df["カテゴリ"].unique().tolist())

    return {
        "models": {t: results[t]["model"] for t in TARGET_COLS},
        "encoders": {"チャネル": le_ch, "カテゴリ": le_cat},
        "metrics": {t: {"MAE": results[t]["mae"], "RMSE": results[t]["rmse"], "R²": results[t]["r2"]} for t in TARGET_COLS},
        "shap_values": shap_values_dict,
        "X_shap": X_shap_dict,
        "features": FEATURE_COLS,
        "features_display": FEATURE_DISPLAY,
        "X_train_sample": {t: results[t]["X_test"] for t in TARGET_COLS},
        "df": df,
        "baselines": baselines,
        "channels": channels,
        "cat_list": cat_list,
    }


def predict_scenario(cache, channel, category, ad_budget, price_index, inventory, season_factor, month_num=6, champions_ratio=0.20):
    """単一シナリオの予測値を返す。"""
    le_ch = cache["encoders"]["チャネル"]
    le_cat = cache["encoders"]["カテゴリ"]

    # クリック・インプレッションは平均的な値で計算
    impressions = int(ad_budget * 20)
    clicks = int(impressions * 0.02)

    ch_enc = le_ch.transform([channel])[0]
    cat_enc = le_cat.transform([category])[0]

    row = pd.DataFrame([{
        "チャネル_enc": ch_enc,
        "カテゴリ_enc": cat_enc,
        "広告費": ad_budget,
        "インプレッション": impressions,
        "クリック": clicks,
        "価格指数": price_index,
        "在庫水準": inventory,
        "月": month_num,
        "季節係数": season_factor,
        "Champions比率": champions_ratio,
    }])

    preds = {}
    for target in TARGET_COLS:
        preds[target] = float(cache["models"][target].predict(row)[0])

    # SHAP for single row
    explainer = shap.TreeExplainer(cache["models"]["売上"])
    sv = explainer.shap_values(row)
    return preds, sv, row


def fmt_man(value):
    """金額を万円形式で整形する。"""
    return f"¥{value/10000:,.1f}万"


# ──────────────────────────────────────────────
# データ読み込み (初期チェック)
# ──────────────────────────────────────────────
data_path = os.path.join(os.path.dirname(__file__), "sample_data", "training_data.csv")
if not os.path.exists(data_path):
    st.error("⚠️ サンプルデータが見つかりません。`python create_sample_data.py` を実行してください。")
    st.stop()


# ──────────────────────────────────────────────
# モデルキャッシュ読み込み
# ──────────────────────────────────────────────
if "models_loaded" not in st.session_state:
    with st.status("🤖 初回モデル学習中（30秒〜1分かかります）...", expanded=True) as status:
        st.write("📥 サンプルデータを読込中...")
        st.write("🌲 LightGBM 3モデル（売上/ROAS/離脱率）を学習中...")
        st.write("📊 SHAP値を計算中...")
        cache = train_models()
        st.session_state.models_loaded = True
        status.update(label="✅ モデル学習完了", state="complete", expanded=False)
else:
    cache = train_models()  # キャッシュから即時取得


# ──────────────────────────────────────────────
# サイドバー
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 EC What-If シミュレーター")
    st.markdown("---")

    selected_channels = st.multiselect(
        "学習対象チャネル",
        options=cache["channels"],
        default=cache["channels"],
        help="表示するチャネルを選択"
    )

    selected_cats = st.multiselect(
        "学習対象カテゴリ",
        options=cache["cat_list"],
        default=cache["cat_list"],
        help="表示するカテゴリを選択"
    )

    if st.button("🔄 データ再生成"):
        st.cache_resource.clear()
        st.success("キャッシュをクリアしました。ページを再読み込みしてください。")
        st.rerun()

    st.markdown("---")
    st.markdown("**使い方**")
    st.markdown("1. 「モデル学習」タブでモデル性能を確認")
    st.markdown("2. 「SHAP重要度」タブで各特徴量の影響を把握")
    st.markdown("3. 「What-Ifシミュレーター」でスライダー操作")
    st.markdown("4. 「シナリオ比較」で複数案を比較・CSVダウンロード")
    st.markdown("---")
    st.markdown("""
💡 **L3 プレミアムパック 月額25万円の価値**

GA4・Lookerでは不可能な仮説検証:
- 広告費±30%で売上はどう変わる？
- 価格を5%上げたら離脱率は？
- 在庫切れが続いたときのROASへの影響は？

LightGBM（3モデル）+ SHAPで定量的に回答。
経営会議の「たぶん」を「予測値」に変える。
""")


# ──────────────────────────────────────────────
# Hero セクション
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
<h1>🎯 EC What-If シミュレーター</h1>
<p>広告費・価格・在庫を変えたら売上はどう変わる？LightGBM + SHAP で "次の一手" を科学的に可視化<br>
<span style="font-size:0.95rem;opacity:0.9;"><strong>L3 プレミアムパック 月額25万円</strong> — GA4・Lookerでは見えない「仮説検証」をリアルタイム予測で即座に実行</span></p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# KPIカード用: デフォルト予測（平均値で計算）
# ──────────────────────────────────────────────
_default_ch = cache["channels"][0]
_default_cat = cache["cat_list"][0]
_default_budget = 1500000
_default_price = 1.0
_default_inv = 250
_default_season = 1.0

_default_preds, _, _ = predict_scenario(
    cache, _default_ch, _default_cat,
    _default_budget, _default_price, _default_inv, _default_season
)
_baseline = cache["baselines"]
_gross_impact = (_default_preds["売上"] - _baseline["売上"]) * 0.4

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{fmt_man(_default_preds['売上'])}</div>
        <div class="kpi-label">予測売上（デフォルト条件）</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{_default_preds['ROAS']:.2f}</div>
        <div class="kpi-label">予測ROAS</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{_default_preds['離脱率']*100:.1f}%</div>
        <div class="kpi-label">予測離脱率</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    diff_cls = "diff-positive" if _gross_impact >= 0 else "diff-negative"
    sign = "+" if _gross_impact >= 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value"><span class="{diff_cls}">{sign}{fmt_man(_gross_impact)}</span></div>
        <div class="kpi-label">粗利インパクト（ベースライン比）</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# タブ
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🤖 モデル学習", "📊 SHAP重要度", "🎯 What-Ifシミュレーター", "📋 シナリオ比較"]
)


# ============================================================
# タブ1: モデル学習
# ============================================================
with tab1:
    st.subheader("🤖 LightGBM モデル学習結果")
    st.success("✅ モデル学習完了（3モデル: 売上 / ROAS / 離脱率）")

    # 評価指標テーブル
    st.markdown("#### 評価指標")
    metrics_data = []
    for target in TARGET_COLS:
        m = cache["metrics"][target]
        metrics_data.append({
            "モデル": target,
            "MAE": f"{m['MAE']:,.4f}",
            "RMSE": f"{m['RMSE']:,.4f}",
            "R²": f"{m['R²']:.4f}",
        })
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    # 離脱率モデル品質警告バナー
    churn_r2 = cache["metrics"]["離脱率"]["R²"]
    if churn_r2 < 0.3:
        st.warning(f"⚠️ 離脱率モデルのR²={churn_r2:.3f}は基準値0.3を下回っています。デモ前にデータ生成スクリプトを再実行してください。")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 特徴量重要度
    st.markdown("#### 特徴量重要度")
    cols_fi = st.columns(3)
    colors = ["#059669", "#0369A1", "#DC2626"]

    for i, target in enumerate(TARGET_COLS):
        model = cache["models"][target]
        importance = model.feature_importances_
        feat_imp_df = pd.DataFrame({
            "特徴量": FEATURE_DISPLAY,
            "重要度": importance
        }).sort_values("重要度", ascending=True)

        with cols_fi[i]:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.barh(feat_imp_df["特徴量"], feat_imp_df["重要度"], color=colors[i])
            ax.set_xlabel("重要度")
            ax.set_title(f"{target}モデル 特徴量重要度")
            ax.tick_params(axis="y", labelsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)


# ============================================================
# タブ2: SHAP重要度
# ============================================================
with tab2:
    st.subheader("📊 SHAP Summary Plot")

    selected_shap_model = st.radio(
        "表示モデル選択",
        options=TARGET_COLS,
        horizontal=True,
        key="shap_model_radio"
    )

    sv = cache["shap_values"][selected_shap_model]
    X_shap = cache["X_shap"][selected_shap_model].copy()
    X_shap.columns = FEATURE_DISPLAY

    fig_shap, ax_shap = plt.subplots(figsize=(10, 5))
    shap.summary_plot(
        sv, X_shap,
        plot_type="dot",
        show=False,
        plot_size=None
    )
    plt.title(f"{selected_shap_model}モデル SHAP Summary Plot (Beeswarm)", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig_shap)
    plt.close(fig_shap)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 説明テキスト
    st.markdown("#### 主要特徴量の影響方向")
    if selected_shap_model == "売上":
        st.info("""
- **広告費**: 値が大きいほど売上への正の影響が大きい（最重要特徴量）
- **季節係数**: 高い季節係数は売上増加に寄与
- **価格指数**: 価格が高めの場合、売上への影響は複合的
- **Champions比率**: 優良顧客比率が高いほど売上安定化に貢献
        """)
    elif selected_shap_model == "ROAS":
        st.info("""
- **広告費**: 投資規模がROASに直接影響
- **Champions比率**: 優良顧客が多いとROAS改善
- **価格指数**: 価格設定がROAS効率に影響
- **季節係数**: 季節性の高い時期はROASが変動しやすい
        """)
    else:
        st.info("""
- **Champions比率**: 優良顧客比率が高いほど離脱率が低下（最重要）
- **広告費**: 適切な広告投資で顧客維持に寄与
- **価格指数**: 過度な値上げは離脱率上昇リスクあり
- **在庫水準**: 在庫切れは離脱率上昇の原因に
        """)

    # Bar plot (特徴量重要度をSHAPで表示)
    st.markdown("#### SHAP Bar Plot（平均|SHAP値|）")
    fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
    mean_shap = np.abs(sv).mean(axis=0)
    feat_shap_df = pd.DataFrame({
        "特徴量": FEATURE_DISPLAY,
        "平均|SHAP値|": mean_shap
    }).sort_values("平均|SHAP値|", ascending=True)
    ax_bar.barh(feat_shap_df["特徴量"], feat_shap_df["平均|SHAP値|"], color="#059669")
    ax_bar.set_xlabel("平均|SHAP値|")
    ax_bar.set_title(f"{selected_shap_model}モデル 特徴量の影響度（SHAP）")
    ax_bar.tick_params(axis="y", labelsize=9)
    plt.tight_layout()
    st.pyplot(fig_bar)
    plt.close(fig_bar)


# ============================================================
# タブ3: What-If シミュレーター
# ============================================================
with tab3:
    st.subheader("🎯 What-If シミュレーター")
    st.markdown("スライダーを操作して「次の一手」を予測します。")

    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown("#### 入力条件")

        sim_channel = st.selectbox(
            "チャネル選択",
            options=cache["channels"],
            key="sim_channel"
        )
        sim_cat = st.selectbox(
            "カテゴリ選択",
            options=cache["cat_list"],
            key="sim_cat"
        )
        sim_budget = st.slider(
            "広告費 (円)",
            min_value=500_000,
            max_value=3_000_000,
            value=1_500_000,
            step=100_000,
            format="%d円",
            key="sim_budget"
        )
        sim_price = st.slider(
            "価格指数",
            min_value=0.80,
            max_value=1.20,
            value=1.00,
            step=0.05,
            format="%.2f",
            key="sim_price"
        )
        sim_inv = st.slider(
            "在庫水準",
            min_value=50,
            max_value=500,
            value=250,
            step=10,
            key="sim_inv"
        )
        sim_season = st.slider(
            "季節係数",
            min_value=0.80,
            max_value=1.20,
            value=1.00,
            step=0.05,
            format="%.2f",
            key="sim_season"
        )

    # 予測実行
    sim_preds, sim_sv, sim_row = predict_scenario(
        cache,
        sim_channel, sim_cat,
        sim_budget, sim_price, sim_inv, sim_season
    )

    gross_impact = (sim_preds["売上"] - _baseline["売上"]) * 0.4

    with col_output:
        st.markdown("#### 予測結果")

        # 売上
        rev_diff = sim_preds["売上"] - _baseline["売上"]
        rev_sign = "+" if rev_diff >= 0 else ""
        rev_cls = "diff-positive" if rev_diff >= 0 else "diff-negative"
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom:10px">
            <div class="kpi-value">{fmt_man(sim_preds['売上'])}</div>
            <div class="kpi-label">予測売上 / ベースライン比: <span class="{rev_cls}">{rev_sign}{fmt_man(rev_diff)}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # ROAS
        roas_diff = sim_preds["ROAS"] - _baseline["ROAS"]
        roas_sign = "+" if roas_diff >= 0 else ""
        roas_cls = "diff-positive" if roas_diff >= 0 else "diff-negative"
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom:10px">
            <div class="kpi-value">{sim_preds['ROAS']:.2f}</div>
            <div class="kpi-label">予測ROAS / ベースライン比: <span class="{roas_cls}">{roas_sign}{roas_diff:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # 離脱率
        churn_diff = sim_preds["離脱率"] - _baseline["離脱率"]
        churn_sign = "+" if churn_diff >= 0 else ""
        # 離脱率は下がるほど良い
        churn_cls = "diff-negative" if churn_diff >= 0 else "diff-positive"
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom:10px">
            <div class="kpi-value">{sim_preds['離脱率']*100:.1f}%</div>
            <div class="kpi-label">予測離脱率 / ベースライン比: <span class="{churn_cls}">{churn_sign}{churn_diff*100:.1f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

        # 粗利インパクト
        gi_sign = "+" if gross_impact >= 0 else ""
        gi_cls = "diff-positive" if gross_impact >= 0 else "diff-negative"
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom:10px">
            <div class="kpi-value"><span class="{gi_cls}">{gi_sign}{fmt_man(gross_impact)}</span></div>
            <div class="kpi-label">粗利インパクト（売上差分×40%）</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 経営インパクトサマリーカード
    st.markdown("#### 💼 経営インパクト概算")
    churn_rate_diff = sim_preds["離脱率"] - _baseline["離脱率"]
    # 仮定: 顧客数500人、平均累計購入額120,000円、年間購入頻度2.5回
    est_customers = 500
    est_avg_ltv = 120_000
    est_annual_freq = 2.5
    churn_impact_annual = int(est_customers * churn_rate_diff * est_avg_ltv * est_annual_freq)
    gi_annual = int(gross_impact * 12)
    net_impact = gi_annual - max(0, churn_impact_annual)
    net_sign = "+" if net_impact >= 0 else ""
    net_cls = "diff-positive" if net_impact >= 0 else "diff-negative"
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        gi_sign = "+" if gi_annual >= 0 else ""
        gi_cls2 = "diff-positive" if gi_annual >= 0 else "diff-negative"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value"><span class="{gi_cls2}">{gi_sign}{fmt_man(gi_annual)}</span></div>
            <div class="kpi-label">粗利インパクト年換算（×12ヶ月）</div>
        </div>
        """, unsafe_allow_html=True)
    with ci2:
        ca_sign = "+" if churn_impact_annual >= 0 else "-"
        ca_cls = "diff-negative" if churn_impact_annual > 0 else "diff-positive"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value"><span class="{ca_cls}">{ca_sign}{fmt_man(abs(churn_impact_annual))}</span></div>
            <div class="kpi-label">離脱率変化による年間損失/益 試算</div>
        </div>
        """, unsafe_allow_html=True)
    with ci3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value"><span class="{net_cls}">{net_sign}{fmt_man(net_impact)}</span></div>
            <div class="kpi-label">ネット年間インパクト（粗利－離脱損失）</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # SHAP TOP5 横棒グラフ
    st.markdown("#### この予測の主要要因（売上モデル SHAP TOP5）")
    sv_flat = sim_sv[0] if sim_sv.ndim > 1 else sim_sv
    shap_df = pd.DataFrame({
        "特徴量": FEATURE_DISPLAY,
        "SHAP値": sv_flat
    }).sort_values("SHAP値", key=abs, ascending=False).head(5)

    colors_shap = ["#059669" if v >= 0 else "#DC2626" for v in shap_df["SHAP値"]]
    colors_wi = colors_shap[::-1]
    fig_wi, ax_wi = plt.subplots(figsize=(8, 3))
    ax_wi.barh(shap_df["特徴量"][::-1], shap_df["SHAP値"][::-1], color=colors_wi)
    ax_wi.axvline(0, color="black", linewidth=0.8)
    ax_wi.set_xlabel("SHAP値（正=売上増加方向、負=売上減少方向）")
    ax_wi.set_title("現在のシナリオにおける特徴量の寄与（SHAP TOP5）")
    plt.tight_layout()
    st.pyplot(fig_wi)
    plt.close(fig_wi)


# ============================================================
# タブ4: シナリオ比較
# ============================================================
with tab4:
    st.subheader("📋 シナリオ比較")

    # タブ3のスライダー値をベースにシナリオ生成
    base_budget = st.session_state.get("sim_budget", 1_500_000)
    base_price = st.session_state.get("sim_price", 1.00)
    base_season = st.session_state.get("sim_season", 1.00)
    base_inv = st.session_state.get("sim_inv", 250)
    base_channel = st.session_state.get("sim_channel", cache["channels"][0])
    base_cat = st.session_state.get("sim_cat", cache["cat_list"][0])

    # シナリオ定義
    scenarios = {
        "現状": {"広告費": base_budget, "価格指数": base_price, "在庫水準": base_inv, "季節係数": base_season},
        "案A: 広告+30%": {"広告費": int(base_budget * 1.3), "価格指数": base_price, "在庫水準": base_inv, "季節係数": base_season},
        "案B: 広告-20%+価格+5%": {"広告費": int(base_budget * 0.8), "価格指数": round(base_price * 1.05, 2), "在庫水準": base_inv, "季節係数": base_season},
    }

    scenario_results = {}
    for name, params in scenarios.items():
        preds, _, _ = predict_scenario(
            cache,
            base_channel, base_cat,
            params["広告費"], params["価格指数"], params["在庫水準"], params["季節係数"]
        )
        gross = (preds["売上"] - _baseline["売上"]) * 0.4
        scenario_results[name] = {
            "広告費": params["広告費"],
            "価格指数": params["価格指数"],
            "予測売上": preds["売上"],
            "予測ROAS": preds["ROAS"],
            "予測離脱率": preds["離脱率"],
            "粗利インパクト": gross,
        }

    # 3列比較テーブル
    st.markdown("#### シナリオ別予測比較")
    compare_rows = []
    for name, res in scenario_results.items():
        compare_rows.append({
            "シナリオ": name,
            "広告費": f"¥{res['広告費']:,}",
            "価格指数": f"{res['価格指数']:.2f}",
            "予測売上": fmt_man(res["予測売上"]),
            "予測ROAS": f"{res['予測ROAS']:.2f}",
            "予測離脱率": f"{res['予測離脱率']*100:.1f}%",
            "粗利インパクト": fmt_man(res["粗利インパクト"]),
        })
    compare_df = pd.DataFrame(compare_rows)
    st.dataframe(compare_df, use_container_width=True, hide_index=True)

    # 推奨シナリオ
    best_name = max(scenario_results, key=lambda k: scenario_results[k]["粗利インパクト"])
    best_res = scenario_results[best_name]
    st.success(
        f"推奨シナリオ: **{best_name}** — "
        f"予測売上 {fmt_man(best_res['予測売上'])} / "
        f"ROAS {best_res['予測ROAS']:.2f} / "
        f"粗利インパクト {fmt_man(best_res['粗利インパクト'])}"
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # シナリオ比較グラフ
    st.markdown("#### シナリオ別予測売上・粗利インパクト")
    sc_names = list(scenario_results.keys())
    sc_revenues = [scenario_results[n]["予測売上"] / 10000 for n in sc_names]
    sc_gross = [scenario_results[n]["粗利インパクト"] / 10000 for n in sc_names]

    fig_sc, axes = plt.subplots(1, 2, figsize=(10, 4))
    bar_colors = ["#0369A1", "#059669", "#DC2626"]
    axes[0].bar(sc_names, sc_revenues, color=bar_colors)
    axes[0].set_title("予測売上（万円）")
    axes[0].set_ylabel("売上（万円）")
    for i, v in enumerate(sc_revenues):
        axes[0].text(i, v + max(sc_revenues)*0.01, f"{v:,.0f}", ha="center", fontsize=9)

    gross_colors = ["#059669" if v >= 0 else "#DC2626" for v in sc_gross]
    axes[1].bar(sc_names, sc_gross, color=gross_colors)
    axes[1].set_title("粗利インパクト（万円）")
    axes[1].set_ylabel("粗利インパクト（万円）")
    axes[1].axhline(0, color="black", linewidth=0.8)
    for i, v in enumerate(sc_gross):
        offset = max(abs(x) for x in sc_gross) * 0.02 if sc_gross else 1
        axes[1].text(i, v + (offset if v >= 0 else -offset*3), f"{v:+,.0f}", ha="center", fontsize=9)

    plt.tight_layout()
    st.pyplot(fig_sc)
    plt.close(fig_sc)

    # 経営判断インサイト
    st.markdown("#### 💼 経営判断インサイト")
    best_res = scenario_results[best_name]
    worst_name = min(scenario_results, key=lambda k: scenario_results[k]["粗利インパクト"])
    worst_res = scenario_results[worst_name]
    impact_diff = best_res["粗利インパクト"] - worst_res["粗利インパクト"]
    st.info(f"""
**推奨シナリオ「{best_name}」を選択した場合の経営判断ポイント:**
- 最良案 vs 最悪案の粗利差分: **{fmt_man(impact_diff)}**
- 予測ROAS: **{best_res['予測ROAS']:.2f}**（損益分岐点1.0を{'上回っています ✅' if best_res['予測ROAS'] > 1.0 else '下回っています ⚠️'}）
- 予測離脱率: **{best_res['予測離脱率']*100:.1f}%**

GA4・Lookerでは不可能なシナリオ定量比較を、月額25万円のL3プレミアムパックがリアルタイムで提供します。
""")

    # CSVダウンロード
    st.markdown("#### データエクスポート")
    csv_data = compare_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 シナリオ比較CSVダウンロード",
        data=csv_data,
        file_name="whatif_scenario_comparison.csv",
        mime="text/csv"
    )


# ──────────────────────────────────────────────
# フッター
# ──────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem; padding:1rem 0;">
    🎯 EC What-If シミュレーター | LightGBM + SHAP | <strong>L3 プレミアムパック 月額25万円</strong><br>
    <span style="color:#059669">広告費・価格・在庫・季節係数</span>を変えて、次の一手を科学的に判断 —
    GA4・Lookerでは見えない仮説検証をリアルタイム予測で即座に実行
</div>
""", unsafe_allow_html=True)
