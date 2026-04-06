"""
顧問先LTV予測＋不採算フラグ
============================
crosssell × shigyou-demo 結合分析
5年間のLTV予測とクラスタ分類で収益性を最大化
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
    page_title="顧問先LTV予測",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CSS注入
# ──────────────────────────────────────────────
st.markdown("""
<style>
.hero-section {
    background: linear-gradient(135deg, #1e3a5f 0%, #7C3AED 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
}
.hero-section h1 { color: white; font-size: 2.2rem; margin-bottom: 0.5rem; }
.hero-section p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0; }
.kpi-card {
    text-align: center;
    padding: 18px 12px;
    background: linear-gradient(180deg, #F5F3FF, #FFFFFF);
    border-radius: 12px;
    border: 1px solid #DDD6FE;
}
.kpi-card .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; }
.kpi-card .kpi-label { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
.cluster-vip {
    background: #FEF3C7; border: 1px solid #FCD34D;
    border-radius: 6px; padding: 4px 10px; font-weight: 700; color: #92400E;
}
.cluster-growth {
    background: #D1FAE5; border: 1px solid #6EE7B7;
    border-radius: 6px; padding: 4px 10px; font-weight: 700; color: #065F46;
}
.cluster-unprofitable {
    background: #FEE2E2; border: 1px solid #FCA5A5;
    border-radius: 6px; padding: 4px 10px; font-weight: 700; color: #991B1B;
}
.cluster-stable {
    background: #E0E7FF; border: 1px solid #A5B4FC;
    border-radius: 6px; padding: 4px 10px; font-weight: 700; color: #3730A3;
}
.section-divider {
    border: none; height: 2px;
    background: linear-gradient(to right, #7C3AED, #e2e8f0);
    margin: 1.5rem 0;
}
.action-card {
    background: #F5F3FF;
    border: 1px solid #DDD6FE;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# ユーティリティ: サンプルデータ生成
# ──────────────────────────────────────────────
def generate_sample_data(seed: int = 42) -> pd.DataFrame:
    """サンプルデータを生成して返す。"""
    np.random.seed(seed)
    N = 150

    顧問先ID = [f"C{i:03d}" for i in range(1, N + 1)]
    業種 = np.random.choice(
        ["建設業", "飲食業", "不動産", "小売業", "製造業", "サービス業", "IT", "医療"],
        N, p=[0.18, 0.15, 0.14, 0.13, 0.12, 0.12, 0.08, 0.08]
    )
    月額顧問料 = np.random.choice(
        [10000, 20000, 30000, 50000, 80000, 100000, 150000, 200000, 300000],
        N, p=[0.05, 0.10, 0.20, 0.25, 0.15, 0.12, 0.07, 0.04, 0.02]
    )
    離反リスクスコア = (np.random.beta(2, 5, N) * 100).round(1)
    クロスセル推定増収額 = np.random.randint(0, 5, N) * np.random.choice(
        [50000, 80000, 100000, 150000, 200000], N
    )
    契約継続予測年数 = np.random.exponential(4, N).clip(0.5, 10).round(1)
    クロスセル成約確率 = np.random.beta(3, 3, N).round(3)
    月次提供工数時間 = np.random.uniform(1, 15, N).round(1)
    時給換算原価 = np.random.choice(
        [2000, 3000, 5000, 7000, 10000], N, p=[0.10, 0.25, 0.35, 0.20, 0.10]
    )
    過去12ヶ月クレーム数 = np.random.poisson(0.5, N).clip(0, 5)

    継続月数 = (契約継続予測年数 * 12).clip(1, 60)
    顧問料収入 = 月額顧問料 * 継続月数
    クロスセル収入 = クロスセル推定増収額 * クロスセル成約確率 * 契約継続予測年数
    原価 = 月次提供工数時間 * 時給換算原価 * 継続月数
    LTV_5年 = (顧問料収入 + クロスセル収入 - 原価).round(0).astype(int)

    年率ROI = LTV_5年 / np.maximum(継続月数, 1) / np.maximum(月額顧問料, 1)

    ltv_80pct = np.percentile(LTV_5年, 80)
    VIPフラグ = LTV_5年 >= ltv_80pct
    不採算フラグ = (LTV_5年 < 0) | (年率ROI < 0.1)
    成長フラグ = (クロスセル成約確率 >= 0.5) & ~VIPフラグ & ~不採算フラグ

    クラスタ = np.where(
        VIPフラグ, "VIP",
        np.where(
            不採算フラグ, "不採算",
            np.where(成長フラグ, "成長", "安定")
        )
    )

    df = pd.DataFrame({
        "顧問先ID": 顧問先ID,
        "業種": 業種,
        "月額顧問料": 月額顧問料,
        "離反リスクスコア": 離反リスクスコア,
        "クロスセル推定増収額": クロスセル推定増収額,
        "契約継続予測年数": 契約継続予測年数,
        "クロスセル成約確率": クロスセル成約確率,
        "月次提供工数時間": 月次提供工数時間,
        "時給換算原価": 時給換算原価,
        "過去12ヶ月クレーム数": 過去12ヶ月クレーム数,
        "継続月数": 継続月数,
        "顧問料収入": 顧問料収入.round(0).astype(int),
        "クロスセル収入": クロスセル収入.round(0).astype(int),
        "原価": 原価.round(0).astype(int),
        "LTV_5年": LTV_5年,
        "年率ROI": 年率ROI.round(4),
        "クラスタ": クラスタ,
    })
    return df


def load_data() -> pd.DataFrame:
    """CSVファイルが存在すればそれを読み込み、なければ生成して返す。"""
    data_path = os.path.join(os.path.dirname(__file__), "sample_data", "ltv_train.csv")
    if os.path.exists(data_path):
        return pd.read_csv(data_path, encoding="utf-8-sig")
    return generate_sample_data()


def classify_cluster(ltv: float, roi: float, crosssell_prob: float, ltv_80pct: float) -> str:
    """クラスタを判定する。"""
    if ltv >= ltv_80pct:
        return "VIP"
    if ltv < 0 or roi < 0.1:
        return "不採算"
    if crosssell_prob >= 0.5:
        return "成長"
    return "安定"


def cluster_badge(cluster: str) -> str:
    """クラスタに対応するHTMLバッジを返す。"""
    mapping = {
        "VIP": ("💎VIP", "cluster-vip"),
        "成長": ("🌱成長", "cluster-growth"),
        "不採算": ("⚠️不採算", "cluster-unprofitable"),
        "安定": ("📋安定", "cluster-stable"),
    }
    label, css_class = mapping.get(cluster, (cluster, "cluster-stable"))
    return f'<span class="{css_class}">{label}</span>'


def fmt_yen(value: float) -> str:
    """金額を円形式に整形する。"""
    return f"¥{int(value):,}"


# ──────────────────────────────────────────────
# セッション状態の初期化
# ──────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_data()
if "model" not in st.session_state:
    st.session_state.model = None
if "shap_values" not in st.session_state:
    st.session_state.shap_values = None
if "X_test" not in st.session_state:
    st.session_state.X_test = None
if "pred_ltv" not in st.session_state:
    st.session_state.pred_ltv = None
if "le" not in st.session_state:
    st.session_state.le = None
if "feature_cols" not in st.session_state:
    st.session_state.feature_cols = None


# ──────────────────────────────────────────────
# サイドバー
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💎 顧問先LTV予測")
    st.markdown("---")

    df_all = st.session_state.df

    # 業種フィルタ
    all_業種 = sorted(df_all["業種"].unique().tolist())
    selected_業種 = st.multiselect(
        "業種フィルタ",
        options=all_業種,
        default=all_業種,
        help="表示する業種を選択してください"
    )

    # LTVしきい値スライダー
    ltv_threshold = st.slider(
        "LTVしきい値（不採算判定）",
        min_value=-5_000_000,
        max_value=0,
        value=0,
        step=100_000,
        format="%d円",
        help="このしきい値以下のLTVを不採算と判定します"
    )

    # サンプルデータ再生成ボタン
    if st.button("🔄 サンプルデータ再生成"):
        import random
        new_seed = random.randint(0, 9999)
        st.session_state.df = generate_sample_data(seed=new_seed)
        st.session_state.model = None
        st.session_state.shap_values = None
        st.session_state.pred_ltv = None
        st.success(f"データを再生成しました（seed={new_seed}）")
        st.rerun()

    st.markdown("---")
    st.markdown("**使い方**")
    st.markdown("1. 業種フィルタで対象を絞り込む")
    st.markdown("2. 「モデル学習」タブでLightGBMを学習")
    st.markdown("3. 「不採算先分析」で改善施策を確認")


# ──────────────────────────────────────────────
# データフィルタリング
# ──────────────────────────────────────────────
df = st.session_state.df.copy()
if selected_業種:
    df = df[df["業種"].isin(selected_業種)]
else:
    df = df.copy()

# LTVしきい値による不採算再判定
df["不採算フラグ"] = (df["LTV_5年"] < ltv_threshold) | (df["年率ROI"] < 0.5)
ltv_80pct_filtered = np.percentile(df["LTV_5年"], 80) if len(df) > 0 else 0


# ──────────────────────────────────────────────
# Hero セクション
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
<h1>💎 顧問先LTV予測＋不採算フラグ</h1>
<p>5年後、その顧問先はいくら儲かるか。不採算先を特定し、利益率を改善。</p>
<p style="margin-top:0.6rem;font-size:0.95rem;color:rgba(255,255,255,0.75);">
💡 L3 月額30万円の価値 ― AIが不採算先を自動検出し、工数削減・値上げ・クロスセルの3施策で年間数百万円の利益改善を実現
</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# KPIカード（4個）
# ──────────────────────────────────────────────
df_vip = df[df["クラスタ"] == "VIP"]
df_unprofitable = df[df["不採算フラグ"]]
df_crosssell_rescue = df[df["不採算フラグ"] & (df["クロスセル成約確率"] >= 0.5)]

avg_ltv = df["LTV_5年"].mean() if len(df) > 0 else 0
vip_count = len(df_vip)
vip_total_ltv = df_vip["LTV_5年"].sum()
unprofitable_count = len(df_unprofitable)
unprofitable_loss = df_unprofitable["LTV_5年"].sum()
crosssell_rescue_count = len(df_crosssell_rescue)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{fmt_yen(avg_ltv)}</div>
        <div class="kpi-label">平均LTV（5年）</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    vip_total_str = f"¥{vip_total_ltv/1e8:.1f}億" if vip_total_ltv >= 1e8 else fmt_yen(vip_total_ltv)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{vip_count}社</div>
        <div class="kpi-label">VIP顧問先 / 総LTV: {vip_total_str}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    loss_str = f"¥{abs(unprofitable_loss)/10000:.0f}万" if abs(unprofitable_loss) < 1e8 else f"¥{abs(unprofitable_loss)/1e8:.1f}億"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{unprofitable_count}社</div>
        <div class="kpi-label">不採算先 / 年間損失: {loss_str}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{crosssell_rescue_count}社</div>
        <div class="kpi-label">クロスセル救済可能</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# モデル学習（起動時に自動実行）
# ──────────────────────────────────────────────
FEATURE_COLS = [
    "月額顧問料", "契約継続予測年数", "クロスセル推定増収額",
    "クロスセル成約確率", "月次提供工数時間", "時給換算原価",
    "過去12ヶ月クレーム数", "離反リスクスコア", "業種_encoded"
]
TARGET_COL = "LTV_5年"


def train_model(df_full: pd.DataFrame):
    """LightGBMモデルを学習し、(model, le, X_test, y_test, pred, shap_values) を返す。"""
    df_m = df_full.copy()
    le = LabelEncoder()
    df_m["業種_encoded"] = le.fit_transform(df_m["業種"])

    X = df_m[FEATURE_COLS]
    y = df_m[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        verbose=-1
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    # SHAP
    explainer = shap.TreeExplainer(model)
    sample_size = min(100, len(X_test))
    X_shap = X_test.iloc[:sample_size]
    shap_vals = explainer.shap_values(X_shap)

    return model, le, X_test, y_test, pred, shap_vals, X_shap


# 未学習なら自動学習
if st.session_state.model is None:
    with st.spinner("モデルを学習中..."):
        df_full = st.session_state.df.copy()
        (
            st.session_state.model,
            st.session_state.le,
            st.session_state.X_test,
            st.session_state.y_test,
            st.session_state.pred_test,
            st.session_state.shap_values,
            st.session_state.X_shap,
        ) = train_model(df_full)
        # 全件予測
        df_full["業種_encoded"] = st.session_state.le.transform(df_full["業種"])
        st.session_state.pred_ltv = st.session_state.model.predict(df_full[FEATURE_COLS])
        st.session_state.feature_cols = FEATURE_COLS


# 全件予測値をdfに付与
df_full_with_pred = st.session_state.df.copy()
df_full_with_pred["業種_encoded"] = st.session_state.le.transform(df_full_with_pred["業種"])
df_full_with_pred["予測LTV_5年"] = st.session_state.model.predict(
    df_full_with_pred[FEATURE_COLS]
).round(0).astype(int)

# フィルタ後のデータにも予測LTVを付与
df["業種_encoded"] = st.session_state.le.transform(df["業種"])
df["予測LTV_5年"] = st.session_state.model.predict(df[FEATURE_COLS]).round(0).astype(int)

# 年率ROI（予測LTVベース）
df["予測年率ROI"] = df["予測LTV_5年"] / np.maximum(df["継続月数"], 1) / np.maximum(df["月額顧問料"], 1)

# クラスタ再判定（予測LTVベース）
pred_ltv_80pct = np.percentile(df_full_with_pred["予測LTV_5年"], 80)


def classify_row(row):
    """行単位のクラスタ判定。"""
    return classify_cluster(
        row["予測LTV_5年"], row["予測年率ROI"],
        row["クロスセル成約確率"], pred_ltv_80pct
    )


df["予測クラスタ"] = df.apply(classify_row, axis=1)


# ──────────────────────────────────────────────
# タブ
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🤖 モデル学習", "📊 LTVランキング", "⚠️ 不採算先分析", "💡 改善アクション"]
)

# ============================================================
# タブ1: モデル学習
# ============================================================
with tab1:
    st.subheader("🤖 LightGBM モデル学習結果")
    st.success("✅ モデル学習完了")

    y_test = st.session_state.y_test
    pred_test = st.session_state.pred_test

    mae = mean_absolute_error(y_test, pred_test)
    rmse = np.sqrt(np.mean((y_test - pred_test) ** 2))
    r2 = r2_score(y_test, pred_test)

    m1, m2, m3 = st.columns(3)
    m1.metric("MAE", f"¥{mae:,.0f}")
    m2.metric("RMSE", f"¥{rmse:,.0f}")
    m3.metric("R²", f"{r2:.4f}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 特徴量重要度
    st.subheader("特徴量重要度")
    model = st.session_state.model
    importance = model.feature_importances_
    feat_imp_df = pd.DataFrame({
        "特徴量": FEATURE_COLS,
        "重要度": importance
    }).sort_values("重要度", ascending=True)

    fig_imp, ax_imp = plt.subplots(figsize=(8, 4))
    ax_imp.barh(feat_imp_df["特徴量"], feat_imp_df["重要度"], color="#7C3AED")
    ax_imp.set_xlabel("重要度")
    ax_imp.set_title("特徴量重要度（LightGBM）")
    ax_imp.tick_params(axis="y", labelsize=9)
    plt.tight_layout()
    st.pyplot(fig_imp)
    plt.close(fig_imp)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # SHAP Summary Plot
    st.subheader("SHAP Summary Plot（beeswarm）")
    shap_values = st.session_state.shap_values
    X_shap = st.session_state.X_shap

    fig_shap, ax_shap = plt.subplots(figsize=(8, 5))
    shap.summary_plot(shap_values, X_shap, plot_type="dot", show=False)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.close("all")


# ============================================================
# タブ2: LTVランキング
# ============================================================
with tab2:
    st.subheader("📊 顧問先LTVランキング（予測値）")

    # テーブル表示用
    df_rank = df[["顧問先ID", "業種", "月額顧問料", "予測LTV_5年", "予測クラスタ", "予測年率ROI"]].copy()
    df_rank = df_rank.sort_values("予測LTV_5年", ascending=False).reset_index(drop=True)
    df_rank.index = df_rank.index + 1
    df_rank.columns = ["顧問先ID", "業種", "月額顧問料", "予測LTV(5年)", "クラスタ", "年率ROI"]
    df_rank["月額顧問料"] = df_rank["月額顧問料"].apply(lambda x: f"¥{x:,}")
    df_rank["予測LTV(5年)"] = df_rank["予測LTV(5年)"].apply(lambda x: f"¥{x:,}")
    df_rank["年率ROI"] = df_rank["年率ROI"].apply(lambda x: f"{x:.2f}")

    st.dataframe(df_rank, use_container_width=True, height=400)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_hist, col_scatter = st.columns(2)

    cluster_colors = {"VIP": "#F59E0B", "成長": "#10B981", "不採算": "#EF4444", "安定": "#6366F1"}

    with col_hist:
        st.subheader("LTV分布（クラスタ別）")
        fig_hist, ax_hist = plt.subplots(figsize=(6, 4))
        for cluster, color in cluster_colors.items():
            subset = df[df["予測クラスタ"] == cluster]["予測LTV_5年"]
            if len(subset) > 0:
                ax_hist.hist(subset, bins=20, alpha=0.6, color=color, label=cluster)
        ax_hist.set_xlabel("予測LTV（円）")
        ax_hist.set_ylabel("件数")
        ax_hist.set_title("LTV分布（クラスタ色分け）")
        ax_hist.legend()
        plt.tight_layout()
        st.pyplot(fig_hist)
        plt.close(fig_hist)

    with col_scatter:
        st.subheader("LTV vs 月額顧問料")
        fig_sc, ax_sc = plt.subplots(figsize=(6, 4))
        for cluster, color in cluster_colors.items():
            subset = df[df["予測クラスタ"] == cluster]
            if len(subset) > 0:
                ax_sc.scatter(
                    subset["月額顧問料"], subset["予測LTV_5年"],
                    c=color, label=cluster, alpha=0.7, s=40
                )
        ax_sc.set_xlabel("月額顧問料（円）")
        ax_sc.set_ylabel("予測LTV（円）")
        ax_sc.set_title("LTV vs 月額顧問料")
        ax_sc.legend()
        plt.tight_layout()
        st.pyplot(fig_sc)
        plt.close(fig_sc)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("クラスタ別集計")
    cluster_summary = df.groupby("予測クラスタ").agg(
        件数=("顧問先ID", "count"),
        平均予測LTV=("予測LTV_5年", "mean"),
        合計予測LTV=("予測LTV_5年", "sum"),
    ).reset_index()
    cluster_summary.columns = ["クラスタ", "件数", "平均LTV（円）", "合計LTV（円）"]
    cluster_summary["平均LTV（円）"] = cluster_summary["平均LTV（円）"].apply(lambda x: f"¥{x:,.0f}")
    cluster_summary["合計LTV（円）"] = cluster_summary["合計LTV（円）"].apply(lambda x: f"¥{x:,.0f}")
    st.dataframe(cluster_summary, use_container_width=True)


# ============================================================
# タブ3: 不採算先分析
# ============================================================
with tab3:
    st.subheader("⚠️ 不採算先一覧（LTV昇順）")

    df_bad = df[df["不採算フラグ"]].copy()
    df_bad = df_bad.sort_values("予測LTV_5年", ascending=True)

    # 損失要因判定
    def get_loss_reason(row):
        reasons = []
        # 工数過剰: 月次提供工数が全体の75パーセンタイル超
        if row["月次提供工数時間"] > df["月次提供工数時間"].quantile(0.75):
            reasons.append("工数過剰")
        if row["過去12ヶ月クレーム数"] >= 2:
            reasons.append("クレーム")
        if row["離反リスクスコア"] > 50:
            reasons.append("早期離脱リスク")
        if row["クロスセル成約確率"] < 0.2:
            reasons.append("クロスセル低確率")
        return " / ".join(reasons) if reasons else "原価超過"

    df_bad["損失要因"] = df_bad.apply(get_loss_reason, axis=1)
    df_bad["損失額"] = df_bad["予測LTV_5年"].apply(lambda x: f"¥{x:,}" if x >= 0 else f"▲¥{abs(x):,}")

    df_bad_disp = df_bad[[
        "顧問先ID", "業種", "月額顧問料", "予測LTV_5年", "損失額", "損失要因"
    ]].copy()
    df_bad_disp.columns = ["顧問先ID", "業種", "月額顧問料", "予測LTV(5年)", "損失額", "主な損失要因"]
    df_bad_disp["月額顧問料"] = df_bad_disp["月額顧問料"].apply(lambda x: f"¥{x:,}")
    df_bad_disp["予測LTV(5年)"] = df_bad_disp["予測LTV(5年)"].apply(lambda x: f"¥{x:,}")
    st.dataframe(df_bad_disp, use_container_width=True, height=350)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("不採算解消のための試算")

    if len(df_bad) > 0:
        col_sim1, col_sim2 = st.columns(2)

        with col_sim1:
            st.markdown("**月次工数削減シミュレーション**")
            reduce_hours = st.slider(
                "月次工数削減時間（時間）",
                min_value=0.0, max_value=20.0, value=5.0, step=0.5,
                key="reduce_hours"
            )
            avg_cost_rate = df_bad["時給換算原価"].mean()
            avg_months = df_bad["継続月数"].mean()
            ltv_improvement_hours = reduce_hours * avg_cost_rate * avg_months
            st.metric(
                "平均LTV改善額（不採算先平均）",
                f"¥{ltv_improvement_hours:,.0f}",
                help="工数削減による原価低減効果の平均値"
            )

        with col_sim2:
            st.markdown("**顧問料改定シミュレーション**")
            fee_increase = st.slider(
                "月額顧問料値上げ額（万円）",
                min_value=0, max_value=10, value=2, step=1,
                key="fee_increase"
            )
            fee_increase_yen = fee_increase * 10000
            ltv_improvement_fee = fee_increase_yen * avg_months
            st.metric(
                "平均LTV改善額（不採算先平均）",
                f"¥{ltv_improvement_fee:,.0f}",
                help="顧問料値上げによる収入増加効果の平均値"
            )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.subheader("業種別不採算率")
    industry_stats = df.groupby("業種").agg(
        total=("顧問先ID", "count"),
        unprofitable=("不採算フラグ", "sum")
    ).reset_index()
    industry_stats["不採算率"] = (industry_stats["unprofitable"] / industry_stats["total"] * 100).round(1)
    industry_stats = industry_stats.sort_values("不採算率", ascending=True)

    fig_bar, ax_bar = plt.subplots(figsize=(7, 4))
    colors_bar = ["#EF4444" if r >= 30 else "#F59E0B" if r >= 15 else "#10B981"
                  for r in industry_stats["不採算率"]]
    ax_bar.barh(industry_stats["業種"], industry_stats["不採算率"], color=colors_bar)
    ax_bar.set_xlabel("不採算率（%）")
    ax_bar.set_title("業種別不採算率")
    ax_bar.axvline(x=20, color="#EF4444", linestyle="--", alpha=0.5, label="警戒ライン(20%)")
    ax_bar.legend()
    plt.tight_layout()
    st.pyplot(fig_bar)
    plt.close(fig_bar)


# ============================================================
# タブ4: 改善アクション
# ============================================================
with tab4:
    st.subheader("💡 顧問先別 改善アクション提案")

    # 顧問先IDセレクトボックス（全150社）
    all_clients = st.session_state.df["顧問先ID"].tolist()
    selected_client_id = st.selectbox("顧問先IDを選択", options=all_clients, key="client_select")

    # 選択した顧問先の詳細
    df_all_with_pred = df_full_with_pred.copy()
    df_all_with_pred["業種_encoded_tmp"] = st.session_state.le.transform(df_all_with_pred["業種"])
    df_all_with_pred["予測LTV_5年"] = st.session_state.model.predict(
        df_all_with_pred[FEATURE_COLS]
    ).round(0).astype(int)
    df_all_with_pred["予測年率ROI"] = (
        df_all_with_pred["予測LTV_5年"] /
        np.maximum(df_all_with_pred["継続月数"], 1) /
        np.maximum(df_all_with_pred["月額顧問料"], 1)
    )
    df_all_with_pred["予測クラスタ"] = df_all_with_pred.apply(
        lambda r: classify_cluster(
            r["予測LTV_5年"], r["予測年率ROI"],
            r["クロスセル成約確率"], pred_ltv_80pct
        ), axis=1
    )

    client_row = df_all_with_pred[df_all_with_pred["顧問先ID"] == selected_client_id].iloc[0]

    col_detail1, col_detail2 = st.columns([1, 2])

    with col_detail1:
        st.markdown("**現在のステータス**")
        st.markdown(f"- 業種: **{client_row['業種']}**")
        st.markdown(f"- 月額顧問料: **{fmt_yen(client_row['月額顧問料'])}**")
        st.markdown(f"- 予測LTV（5年）: **{fmt_yen(client_row['予測LTV_5年'])}**")
        st.markdown(f"- 契約継続予測年数: **{client_row['契約継続予測年数']}年**")
        st.markdown(f"- 月次提供工数: **{client_row['月次提供工数時間']}時間**")
        st.markdown(f"- クロスセル成約確率: **{client_row['クロスセル成約確率']:.1%}**")
        st.markdown(f"- 離反リスクスコア: **{client_row['離反リスクスコア']}点**")
        cluster_label = client_row["予測クラスタ"]
        st.markdown(f"- クラスタ: {cluster_badge(cluster_label)}", unsafe_allow_html=True)

    with col_detail2:
        st.markdown("**この顧問先のLTVを改善する3つの方法**")

        # 方法1: クロスセル成約
        crosssell_prob = client_row["クロスセル成約確率"]
        crosssell_amount = client_row["クロスセル推定増収額"]
        crosssell_years = client_row["契約継続予測年数"]
        crosssell_expected = crosssell_amount * crosssell_prob * crosssell_years
        crosssell_max = crosssell_amount * crosssell_years
        st.markdown(f"""
        <div class="action-card">
        <strong>① クロスセル成約による収入増加</strong><br>
        クロスセル推定増収額: <strong>{fmt_yen(crosssell_amount)}</strong><br>
        現在の成約確率: <strong>{crosssell_prob:.1%}</strong> →
        期待追加収入: <strong>{fmt_yen(crosssell_expected)}</strong><br>
        成約確率を100%にした場合の最大追加LTV: <strong>{fmt_yen(crosssell_max)}</strong>
        </div>
        """, unsafe_allow_html=True)

        # 方法2: 工数削減
        current_hours = client_row["月次提供工数時間"]
        cost_rate = client_row["時給換算原価"]
        months = client_row["継続月数"]
        reduce_suggestion = min(current_hours * 0.3, 10.0)
        hours_saving = reduce_suggestion * cost_rate * months
        st.markdown(f"""
        <div class="action-card">
        <strong>② 工数削減による原価改善</strong><br>
        現在の月次工数: <strong>{current_hours}時間</strong> /
        時給換算原価: <strong>{fmt_yen(cost_rate)}</strong><br>
        月次工数を<strong>{reduce_suggestion:.1f}時間</strong>削減した場合の
        LTV改善額: <strong>{fmt_yen(hours_saving)}</strong>
        </div>
        """, unsafe_allow_html=True)

        # 方法3: 長期継続
        current_years = client_row["契約継続予測年数"]
        monthly_fee = client_row["月額顧問料"]
        monthly_cost = current_hours * cost_rate
        monthly_profit = monthly_fee - monthly_cost
        additional_ltv = monthly_profit * 2 * 12  # +2年分
        st.markdown(f"""
        <div class="action-card">
        <strong>③ 長期継続による追加LTV</strong><br>
        現在の予測継続年数: <strong>{current_years}年</strong><br>
        契約継続を<strong>+2年</strong>延長した場合の追加LTV:
        <strong>{fmt_yen(additional_ltv)}</strong>
        （月次利益 {fmt_yen(monthly_profit)} × 24ヶ月）
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # スライダー試算
    st.subheader("🔢 改善施策シミュレーター")
    st.markdown("施策をスライダーで調整して、この顧問先のLTV改善効果をリアルタイム試算します。")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        sim_crosssell_rate = st.slider(
            "クロスセル成約確率改善",
            min_value=0.0, max_value=1.0,
            value=float(min(client_row["クロスセル成約確率"] + 0.2, 1.0)),
            step=0.05, format="%.0f%%",
            key="sim_crosssell_rate",
            help="営業強化でクロスセル成約確率を引き上げた場合"
        )
    with sim_col2:
        sim_fee_increase = st.slider(
            "月額顧問料値上げ（万円）",
            min_value=0, max_value=10, value=2, step=1,
            key="sim_fee_increase",
            help="顧問料改定による月次収入の増加額"
        )
    with sim_col3:
        sim_hours_reduce = st.slider(
            "月次工数削減（時間）",
            min_value=0.0, max_value=float(min(client_row["月次提供工数時間"], 15.0)),
            value=min(2.0, float(client_row["月次提供工数時間"])),
            step=0.5,
            key="sim_hours_reduce",
            help="業務効率化による工数削減効果"
        )

    # 試算計算
    months = float(client_row["継続月数"])
    orig_crosssell = crosssell_amount * float(client_row["クロスセル成約確率"]) * crosssell_years
    new_crosssell = crosssell_amount * sim_crosssell_rate * crosssell_years
    delta_crosssell = new_crosssell - orig_crosssell

    delta_fee = sim_fee_increase * 10000 * months
    delta_hours = sim_hours_reduce * float(client_row["時給換算原価"]) * months
    total_improvement = delta_crosssell + delta_fee + delta_hours
    new_ltv = float(client_row["予測LTV_5年"]) + total_improvement

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("クロスセル改善", f"¥{delta_crosssell:+,.0f}")
    res_col2.metric("顧問料改定効果", f"¥{delta_fee:+,.0f}")
    res_col3.metric("工数削減効果", f"¥{delta_hours:+,.0f}")
    res_col4.metric("改善後 予測LTV（5年）", f"¥{new_ltv:,.0f}",
                    delta=f"¥{total_improvement:+,.0f}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # CSV出力: LTVランキング全件 + クラスタラベル
    st.subheader("📥 LTVランキング全件ダウンロード")
    export_df = df_all_with_pred[[
        "顧問先ID", "業種", "月額顧問料", "契約継続予測年数",
        "クロスセル成約確率", "月次提供工数時間", "時給換算原価",
        "過去12ヶ月クレーム数", "離反リスクスコア",
        "LTV_5年", "予測LTV_5年", "年率ROI", "クラスタ", "予測クラスタ"
    ]].sort_values("予測LTV_5年", ascending=False)

    csv_data = export_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 LTVランキングCSVダウンロード",
        data=csv_data,
        file_name="ltv_ranking.csv",
        mime="text/csv"
    )
