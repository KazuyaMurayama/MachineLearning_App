"""
士業向け 顧問先離反予測デモアプリ
=================================
MVP #1: LightGBM + SHAP + 逆SHAP による離反予測・改善提案

対象: 税理士・社労士・行政書士事務所
核心機能:
  - 顧問先の離反リスクスコアリング
  - SHAP要因分析（なぜ離反リスクが高いか）
  - 逆SHAP改善提案（何を変えれば離反を防げるか）
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
import sys
import os

warnings.filterwarnings("ignore")
if not sys.warnoptions:
    warnings.simplefilter("ignore")

# モジュールパスを追加（親ディレクトリのcommon + 既存modules）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from modules.data_loader import load_file, display_data_info
from modules.model import preprocess_data, split_data, train_model, predict
from modules.evaluation import calculate_metrics, display_metrics
from modules.shap_analysis import (
    calculate_shap_values, create_summary_plot, create_bar_plot,
    setup_japanese_font, check_japanese_font_available,
    get_feature_importance
)
from common.reverse_shap import (
    generate_action_suggestions, compute_feature_stats
)
import shap
import matplotlib.pyplot as plt

# --- ページ設定 ---
st.set_page_config(
    page_title="顧問先離反予測AI | 士業向けデモ",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TARGET_COL = "解約までの予測月数"
RISK_THRESHOLD_HIGH = 12  # 12ヶ月以内 = 高リスク
RISK_THRESHOLD_MED = 24   # 24ヶ月以内 = 中リスク

# =============================================================================
# セッション状態の初期化
# =============================================================================
for key, default in {
    "model": None, "trained": False, "label_encoders": None,
    "feature_cols": None, "metrics": None, "train_df": None,
    "X_test": None, "y_test": None, "shap_values": None,
    "X_shap_sample": None, "feature_stats": None,
    "using_default": False, "default_loaded": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def load_default_data():
    """デフォルトサンプルデータの自動読み込み"""
    train_path = os.path.join(os.path.dirname(__file__), "sample_data", "shigyou_train.csv")
    if not os.path.exists(train_path):
        return
    try:
        df = pd.read_csv(train_path)
        st.session_state.train_df = df
        st.session_state.using_default = True
        st.session_state.default_loaded = True
        _train_model(df)
    except Exception:
        st.session_state.default_loaded = True


def _train_model(df: pd.DataFrame):
    """モデル学習のヘルパー"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        feature_cols = [c for c in df.columns if c not in [TARGET_COL, "顧問先ID"]]
        st.session_state.feature_cols = feature_cols

        df_work = df.drop(columns=["顧問先ID"], errors="ignore")
        df_processed, le = preprocess_data(df_work.copy(), TARGET_COL, is_training=True)
        X_train, X_test, y_train, y_test = split_data(df_processed.copy(), TARGET_COL, test_size=0.2, random_state=42)

        model = train_model(X_train, y_train)
        y_pred = predict(model, X_test)
        metrics = calculate_metrics(y_test, y_pred)

        # SHAP
        shap_vals, X_sample = calculate_shap_values(model, X_test, max_samples=500)

        # 特徴量統計（逆SHAP用）
        stats = compute_feature_stats(df_work, feature_cols)

        st.session_state.update({
            "model": model, "label_encoders": le, "trained": True,
            "feature_cols": feature_cols, "X_test": X_test, "y_test": y_test,
            "metrics": metrics, "shap_values": shap_vals, "X_shap_sample": X_sample,
            "feature_stats": stats,
        })


# 初回読み込み
if not st.session_state.default_loaded:
    load_default_data()

# =============================================================================
# サイドバー
# =============================================================================
st.sidebar.markdown("# 🏛️ 顧問先離反予測AI")
st.sidebar.markdown("**士業事務所向けデモ**")
st.sidebar.markdown("---")

if st.session_state.using_default:
    st.sidebar.info("💡 デモデータ（150社）で自動学習済みです。\n独自データをアップロードして差し替えも可能です。")

st.sidebar.subheader("📁 データアップロード")
uploaded = st.sidebar.file_uploader(
    "顧問先データ（CSV/Excel）", type=["csv", "xlsx", "xls"], key="upload_train"
)

if uploaded is not None:
    new_df = load_file(uploaded)
    if new_df is not None and TARGET_COL in new_df.columns:
        st.session_state.train_df = new_df
        st.session_state.using_default = False
        st.sidebar.success(f"✅ {len(new_df)}件のデータを読み込みました")
    elif new_df is not None:
        st.sidebar.error(f"❌ 「{TARGET_COL}」カラムが必要です")

st.sidebar.markdown("---")

if st.session_state.train_df is not None:
    btn_label = "🔄 再学習" if st.session_state.trained else "▶️ モデル学習"
    if st.sidebar.button(btn_label, type="primary", use_container_width=True):
        with st.spinner("学習中..."):
            _train_model(st.session_state.train_df)
        st.sidebar.success("✅ 学習完了")

st.sidebar.markdown("---")
st.sidebar.caption("AI経営パートナー × データサイエンス")
st.sidebar.caption("MVP #1 — 士業向け離反予測デモ v0.1")

# =============================================================================
# メインエリア
# =============================================================================
st.title("🏛️ 顧問先離反予測AI")
st.markdown(
    "LightGBM + SHAP + **逆SHAP** で、顧問先の離反リスクを予測し、"
    "**「何を変えれば離反を防げるか」**を具体的に提案します。"
)

# --- タブ ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 離反リスク一覧",
    "📈 モデル評価",
    "🔍 SHAP要因分析",
    "💡 逆SHAP改善提案",
    "📋 データプレビュー",
])

# =============================================================================
# Tab 1: 離反リスク一覧
# =============================================================================
with tab1:
    st.header("顧問先 離反リスク一覧")

    if st.session_state.trained and st.session_state.train_df is not None:
        df = st.session_state.train_df.copy()
        model = st.session_state.model
        le = st.session_state.label_encoders
        feat_cols = st.session_state.feature_cols

        # 全データに対して予測
        df_work = df.drop(columns=["顧問先ID", TARGET_COL], errors="ignore")
        df_proc, _ = preprocess_data(df_work.copy(), target_col=None, label_encoders=le, is_training=False)
        preds = predict(model, df_proc)

        df["予測残存月数"] = np.round(preds, 1)

        # リスクレベル
        def risk_level(months):
            if months <= RISK_THRESHOLD_HIGH:
                return "🔴 高リスク"
            elif months <= RISK_THRESHOLD_MED:
                return "🟡 中リスク"
            return "🟢 低リスク"

        df["リスクレベル"] = df["予測残存月数"].apply(risk_level)
        df_sorted = df.sort_values("予測残存月数").reset_index(drop=True)

        # KPI
        n_high = (df_sorted["予測残存月数"] <= RISK_THRESHOLD_HIGH).sum()
        n_med = ((df_sorted["予測残存月数"] > RISK_THRESHOLD_HIGH) & (df_sorted["予測残存月数"] <= RISK_THRESHOLD_MED)).sum()
        n_low = (df_sorted["予測残存月数"] > RISK_THRESHOLD_MED).sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("全顧問先数", f"{len(df)}社")
        c2.metric("🔴 高リスク", f"{n_high}社", help=f"{RISK_THRESHOLD_HIGH}ヶ月以内に離反の恐れ")
        c3.metric("🟡 中リスク", f"{n_med}社")
        c4.metric("🟢 低リスク", f"{n_low}社")

        st.markdown("---")
        st.subheader("🔴 要注意顧問先 TOP10")

        top10 = df_sorted.head(10)
        display_cols = ["顧問先ID", "リスクレベル", "予測残存月数", "契約年数",
                        "月額顧問料", "直近3ヶ月連絡頻度", "直近6ヶ月面談回数",
                        "入金遅延回数", "価格交渉フラグ"]
        display_cols = [c for c in display_cols if c in top10.columns]
        st.dataframe(top10[display_cols], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("全顧問先リスク分布")

        # ヒストグラム
        fig, ax = plt.subplots(figsize=(10, 4))
        setup_japanese_font()
        ax.hist(df["予測残存月数"], bins=20, color="#2563EB", alpha=0.7, edgecolor="white")
        ax.axvline(RISK_THRESHOLD_HIGH, color="red", linestyle="--", label=f"高リスク ({RISK_THRESHOLD_HIGH}ヶ月)")
        ax.axvline(RISK_THRESHOLD_MED, color="orange", linestyle="--", label=f"中リスク ({RISK_THRESHOLD_MED}ヶ月)")
        ax.set_xlabel("予測残存月数")
        ax.set_ylabel("顧問先数")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # CSV DL
        csv = df_sorted.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 リスク一覧をCSVでダウンロード", csv, "risk_list.csv", "text/csv",
                           use_container_width=True)
    else:
        st.info("モデルを学習するとリスク一覧が表示されます")

# =============================================================================
# Tab 2: モデル評価
# =============================================================================
with tab2:
    st.header("モデル評価指標")
    if st.session_state.trained and st.session_state.metrics:
        display_metrics(st.session_state.metrics)
        st.markdown("---")
        st.markdown("""
        **評価指標の読み方**
        - **MAE**: 予測と実際の差（月数）の平均。小さいほど良い。
        - **RMSE**: 外れ値を重視した誤差指標。
        - **R²**: モデルの説明力（1.0が完璧）。0.7以上で実用水準。
        """)
    else:
        st.info("モデルを学習すると評価指標が表示されます")

# =============================================================================
# Tab 3: SHAP要因分析
# =============================================================================
with tab3:
    st.header("SHAP要因分析")
    st.markdown("**「なぜこの顧問先は離反リスクが高いのか？」**を可視化します。")

    if st.session_state.trained and st.session_state.shap_values is not None:
        X_sample = st.session_state.X_shap_sample
        shap_vals = st.session_state.shap_values

        use_english = not check_japanese_font_available()
        X_display = X_sample

        st.subheader("📊 SHAP Summary Plot")
        st.caption("赤=値が高い、青=値が低い。右に寄るほど離反リスクを上げる要因。")
        fig1 = create_summary_plot(shap_vals, X_display)
        st.pyplot(fig1)
        plt.close(fig1)

        st.markdown("---")
        st.subheader("📊 特徴量重要度")
        fig2 = create_bar_plot(shap_vals, X_display)
        st.pyplot(fig2)
        plt.close(fig2)

        st.markdown("---")
        st.subheader("📋 特徴量重要度ランキング")
        importance_df = get_feature_importance(shap_vals, X_sample.columns.tolist())
        st.dataframe(importance_df, use_container_width=True, hide_index=True)
    else:
        st.info("モデルを学習するとSHAP分析が表示されます")

# =============================================================================
# Tab 4: 逆SHAP改善提案（★最大の差別化）
# =============================================================================
with tab4:
    st.header("💡 逆SHAP改善提案")
    st.markdown("""
    通常のSHAP: **「なぜ離反リスクが高いか？」**（Why）
    逆SHAP: **「何を変えれば離反を防げるか？」**（How）
    → 具体的なアクション提案を自動生成します。
    """)

    if st.session_state.trained and st.session_state.train_df is not None:
        df = st.session_state.train_df.copy()
        model = st.session_state.model
        le = st.session_state.label_encoders
        feat_cols = st.session_state.feature_cols
        stats = st.session_state.feature_stats

        # 全データの予測
        df_work = df.drop(columns=["顧問先ID", TARGET_COL], errors="ignore")
        df_proc, _ = preprocess_data(df_work.copy(), target_col=None, label_encoders=le, is_training=False)
        preds = predict(model, df_proc)
        df["予測残存月数"] = np.round(preds, 1)

        # 高リスク顧問先を抽出
        high_risk = df[df["予測残存月数"] <= RISK_THRESHOLD_HIGH].sort_values("予測残存月数")

        if len(high_risk) == 0:
            st.success("🎉 高リスク顧問先は現在ありません！")
        else:
            st.warning(f"🔴 **{len(high_risk)}社** が高リスク（{RISK_THRESHOLD_HIGH}ヶ月以内に離反の恐れ）")

            # 顧問先選択
            client_ids = high_risk["顧問先ID"].tolist()
            selected_id = st.selectbox("改善提案を表示する顧問先を選択", client_ids)

            if selected_id:
                row = df[df["顧問先ID"] == selected_id].iloc[0]
                st.markdown(f"### 顧問先: **{selected_id}**")

                # 基本情報カード
                info_cols = st.columns(4)
                info_cols[0].metric("予測残存月数", f"{row['予測残存月数']:.1f}ヶ月")
                info_cols[1].metric("契約年数", f"{row['契約年数']}年")
                info_cols[2].metric("月額顧問料", f"¥{int(row['月額顧問料']):,}")
                info_cols[3].metric("面談回数(6M)", f"{int(row['直近6ヶ月面談回数'])}回")

                st.markdown("---")
                st.subheader("🎯 改善アクション提案")

                # 逆SHAP実行
                row_features = df_work[df["顧問先ID"] == selected_id].copy()
                row_proc, _ = preprocess_data(row_features.copy(), target_col=None,
                                              label_encoders=le, is_training=False)

                suggestions = generate_action_suggestions(
                    model, row_proc, feat_cols, stats,
                    target_direction="increase",  # 残存月数を上げたい = 離反防止
                    top_n=5,
                )

                if suggestions:
                    for i, s in enumerate(suggestions, 1):
                        impact_pct = s["impact"]
                        st.markdown(f"""
                        **提案 {i}: {s['action']}**
                        > 現在値: `{s['current']}` → 改善目標: `{s['target']}`
                        > 推定改善効果: **+{impact_pct:.1f}ヶ月**
                        """)
                        st.markdown("---")
                else:
                    st.info("この顧問先には数値ベースの改善提案を生成できませんでした。定性的な要因（業種・規模等）の見直しを検討してください。")

                # 個別SHAP Force Plot的な表示
                st.subheader("📊 この顧問先の要因分解")
                explainer = shap.TreeExplainer(model)
                sv = explainer.shap_values(row_proc)
                sv_row = sv[0]

                factor_df = pd.DataFrame({
                    "特徴量": feat_cols,
                    "SHAP値": np.round(sv_row, 3),
                    "影響方向": ["離反リスク↑" if v < 0 else "離反防止↑" for v in sv_row],
                }).sort_values("SHAP値").reset_index(drop=True)
                st.dataframe(factor_df, use_container_width=True, hide_index=True)
    else:
        st.info("モデルを学習すると改善提案が表示されます")

# =============================================================================
# Tab 5: データプレビュー
# =============================================================================
with tab5:
    st.header("データプレビュー")
    if st.session_state.train_df is not None:
        df = st.session_state.train_df
        if st.session_state.using_default:
            st.info("💡 デモデータ（150社の合成顧問先データ）を表示しています")

        display_data_info(df, "顧問先データ")
        st.markdown("##### 先頭20行")
        st.dataframe(df.head(20), use_container_width=True)

        st.markdown("---")
        st.subheader("📊 基本統計量")
        st.dataframe(df.describe(), use_container_width=True)
    else:
        st.info("サイドバーからデータをアップロードしてください")
