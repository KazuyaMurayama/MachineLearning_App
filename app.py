"""
機械学習予測アプリ (ML Prediction App)
======================================
Streamlit + LightGBM による回帰予測アプリケーション

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
import sys

# NumPy 2.x互換性警告を完全に無視（エラーに昇格させない）
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

# Pythonの警告をエラーとして扱わない
if not sys.warnoptions:
    warnings.simplefilter("ignore")

from modules.data_loader import load_file, display_data_info, display_preview
from modules.model import preprocess_data, split_data, train_model, predict, check_feature_compatibility
from modules.evaluation import calculate_metrics, display_metrics
from modules.shap_analysis import display_shap_plots

# ページ設定
st.set_page_config(
    page_title="ML予測アプリ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# セッション状態の初期化
# =============================================================================
if 'model' not in st.session_state:
    st.session_state.model = None
if 'trained' not in st.session_state:
    st.session_state.trained = False
if 'label_encoders' not in st.session_state:
    st.session_state.label_encoders = None
if 'feature_cols' not in st.session_state:
    st.session_state.feature_cols = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'train_df' not in st.session_state:
    st.session_state.train_df = None
if 'target_df' not in st.session_state:
    st.session_state.target_df = None
if 'X_test' not in st.session_state:
    st.session_state.X_test = None
if 'y_test' not in st.session_state:
    st.session_state.y_test = None
if 'target_col' not in st.session_state:
    st.session_state.target_col = None
if 'using_default_data' not in st.session_state:
    st.session_state.using_default_data = False
if 'default_data_loaded' not in st.session_state:
    st.session_state.default_data_loaded = False

# デフォルトデータの自動読み込み（初回のみ）
import os
if not st.session_state.default_data_loaded:
    default_train_path = "sample_data/4_ltv_train.csv"
    default_target_path = "sample_data/4_ltv_target.csv"

    # デフォルトデータが存在する場合のみ読み込む
    if os.path.exists(default_train_path) and os.path.exists(default_target_path):
        try:
            # デフォルトデータの読み込み
            default_train_df = pd.read_csv(default_train_path)
            default_target_df = pd.read_csv(default_target_path)

            st.session_state.train_df = default_train_df
            st.session_state.target_df = default_target_df
            st.session_state.target_col = 'LTV'
            st.session_state.using_default_data = True
            st.session_state.default_data_loaded = True

            # デフォルトデータでモデルを自動学習
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                feature_cols = [col for col in default_train_df.columns if col != 'LTV']
                st.session_state.feature_cols = feature_cols

                # データの前処理
                df_processed, label_encoders = preprocess_data(
                    default_train_df.copy(),
                    'LTV',
                    is_training=True
                )

                # Train/Test分割
                X_train, X_test, y_train, y_test = split_data(
                    df_processed.copy(),
                    'LTV',
                    test_size=0.2,
                    random_state=42
                )

                # モデル学習
                model = train_model(X_train, y_train)

                # テストデータで予測
                y_pred = predict(model, X_test)

                # 評価指標を計算
                metrics = calculate_metrics(y_test, y_pred)

                # セッション状態に保存
                st.session_state.model = model
                st.session_state.label_encoders = label_encoders
                st.session_state.trained = True
                st.session_state.X_test = X_test
                st.session_state.y_test = y_test
                st.session_state.metrics = metrics

        except Exception as e:
            # エラーが発生してもアプリは続行（デフォルトデータなしでも使える）
            st.session_state.default_data_loaded = True
            pass

# =============================================================================
# サイドバー
# =============================================================================
st.sidebar.title("🤖 ML予測アプリ")
st.sidebar.markdown("---")

# デフォルトデータ使用中の通知
if st.session_state.using_default_data:
    st.sidebar.info("💡 デモデータ（LTV予測）を使用中です。独自データをアップロードすることも可能です。")

st.sidebar.subheader("📁 教師データ")
train_file = st.sidebar.file_uploader(
    "訓練用データをアップロード",
    type=['csv', 'xlsx', 'xls'],
    key='train_file'
)

st.sidebar.subheader("📁 ターゲットデータ")
target_file = st.sidebar.file_uploader(
    "予測用データをアップロード",
    type=['csv', 'xlsx', 'xls'],
    key='target_file'
)

st.sidebar.markdown("---")

# 目的変数選択
target_col = None
feature_cols = []

# ユーザーがファイルをアップロードした場合、デフォルトデータを上書き
if train_file is not None:
    st.session_state.using_default_data = False

# train_dfが存在する場合（デフォルトまたはアップロード）
if (train_file is not None or st.session_state.using_default_data) and 'train_df' in st.session_state and st.session_state.train_df is not None:
    st.sidebar.subheader("🎯 目的変数")

    # デフォルト値の設定
    default_index = len(st.session_state.train_df.columns) - 1
    if st.session_state.target_col is not None and st.session_state.target_col in st.session_state.train_df.columns:
        default_index = st.session_state.train_df.columns.tolist().index(st.session_state.target_col)

    target_col = st.sidebar.selectbox(
        "予測する変数を選択",
        options=st.session_state.train_df.columns.tolist(),
        index=default_index
    )

    # 特徴量の自動設定
    feature_cols = [col for col in st.session_state.train_df.columns if col != target_col]

    st.sidebar.info(f"✅ 特徴量: {len(feature_cols)}個")
    with st.sidebar.expander("特徴量一覧"):
        for i, col in enumerate(feature_cols, 1):
            st.write(f"{i}. {col}")

    # セッションに保存
    st.session_state.target_col = target_col
    st.session_state.feature_cols = feature_cols

st.sidebar.markdown("---")

# 学習実行ボタン（デフォルトデータまたはアップロードされたデータがある場合）
if (train_file is not None or st.session_state.using_default_data) and target_col is not None:
    # デフォルトデータで既に学習済みの場合は「再学習」ボタン表示
    button_label = "🔄 再学習" if st.session_state.trained else "▶️ モデル学習"

    if st.sidebar.button(button_label, type="primary", use_container_width=True):
        with st.spinner("🔄 モデルを学習中..."):
            # 警告を完全に抑制
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                try:
                    # データの前処理
                    df_processed, label_encoders = preprocess_data(
                        st.session_state.train_df.copy(),
                        target_col,
                        is_training=True
                    )

                    # Train/Test分割（NumPy 2.x対応: 明示的にコピーを作成）
                    X_train, X_test, y_train, y_test = split_data(
                        df_processed.copy(),
                        target_col,
                        test_size=0.2,
                        random_state=42
                    )

                    # モデル学習
                    model = train_model(X_train, y_train)

                    # テストデータで予測
                    y_pred = predict(model, X_test)

                    # 評価指標を計算
                    metrics = calculate_metrics(y_test, y_pred)

                    # セッション状態に保存
                    st.session_state.model = model
                    st.session_state.label_encoders = label_encoders
                    st.session_state.trained = True
                    st.session_state.X_test = X_test
                    st.session_state.y_test = y_test
                    st.session_state.metrics = metrics

                    st.sidebar.success("✅ モデル学習が完了しました！")

                except Exception as e:
                    st.sidebar.error(f"❌ 学習エラー: {str(e)}")
                    st.session_state.trained = False

# =============================================================================
# メインエリア
# =============================================================================
st.title("🤖 機械学習予測アプリ")
st.markdown("LightGBMを使用した回帰予測を行います。")

# ステータスバー
status_col1, status_col2, status_col3 = st.columns(3)
with status_col1:
    if st.session_state.train_df is not None:
        st.success("✅ 教師データ読み込み済み")
    else:
        st.info("⏳ 教師データ待機中")

with status_col2:
    if st.session_state.trained:
        st.success("✅ モデル学習済み")
    else:
        st.info("⏳ モデル未学習")

with status_col3:
    if st.session_state.target_df is not None:
        st.success("✅ ターゲットデータ読み込み済み")
    else:
        st.info("⏳ ターゲットデータ待機中")

# 使い方の説明（折りたたみ）
with st.expander("📖 使い方", expanded=False):
    st.markdown("""
    ### ステップ1: 教師データのアップロード
    1. サイドバーから訓練用データ（CSV/Excel）をアップロード
    2. データプレビューで内容を確認

    ### ステップ2: 目的変数の選択
    1. サイドバーのドロップダウンから予測したい変数を選択
    2. 自動的に特徴量が設定されます

    ### ステップ3: モデル学習
    1. サイドバーの「▶️ モデル学習」ボタンをクリック
    2. 学習が完了するまで待機

    ### ステップ4: 結果の確認
    - **評価指標タブ**: モデルの性能を確認
    - **SHAP解析タブ**: 特徴量の重要度を確認

    ### ステップ5: 予測の実行
    1. サイドバーからターゲットデータをアップロード
    2. 予測結果タブで結果を確認
    3. CSVボタンで結果をダウンロード
    """)

st.markdown("---")

# タブ構成
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 データプレビュー",
    "📈 評価指標",
    "🔍 SHAP解析",
    "🎯 予測結果"
])

# -----------------------------------------------------------------------------
# Tab 1: データプレビュー
# -----------------------------------------------------------------------------
with tab1:
    st.header("データプレビュー")

    # 教師データの読み込みと表示
    if train_file is not None:
        train_df = load_file(train_file)
        if train_df is not None:
            st.subheader("📊 教師データ")
            display_data_info(train_df, "教師データ")
            st.markdown("##### 先頭10行のプレビュー")
            display_preview(train_df, n_rows=10)

            # セッションに保存
            st.session_state.train_df = train_df
    elif st.session_state.using_default_data and st.session_state.train_df is not None:
        # デフォルトデータの表示
        st.subheader("📊 教師データ（デモデータ）")
        display_data_info(st.session_state.train_df, "教師データ")
        st.markdown("##### 先頭10行のプレビュー")
        display_preview(st.session_state.train_df, n_rows=10)
    else:
        st.info("👈 サイドバーから教師データをアップロードしてください")

    # ターゲットデータの読み込みと表示
    if target_file is not None:
        target_df = load_file(target_file)
        if target_df is not None:
            st.subheader("🎯 ターゲットデータ")
            display_data_info(target_df, "ターゲットデータ")
            st.markdown("##### 先頭10行のプレビュー")
            display_preview(target_df, n_rows=10)

            # セッションに保存
            st.session_state.target_df = target_df
    elif st.session_state.using_default_data and st.session_state.target_df is not None:
        # デフォルトターゲットデータの表示
        st.subheader("🎯 ターゲットデータ（デモデータ）")
        display_data_info(st.session_state.target_df, "ターゲットデータ")
        st.markdown("##### 先頭10行のプレビュー")
        display_preview(st.session_state.target_df, n_rows=10)

# -----------------------------------------------------------------------------
# Tab 2: 評価指標
# -----------------------------------------------------------------------------
with tab2:
    st.header("モデル評価指標")

    if st.session_state.trained and st.session_state.metrics is not None:
        st.markdown("### 📊 テストデータでの評価")
        display_metrics(st.session_state.metrics)

        st.markdown("---")
        st.markdown("### 📈 評価指標の説明")
        st.markdown("""
        - **MAE (Mean Absolute Error)**: 予測値と実測値の差の絶対値の平均。単位は目的変数と同じ。
        - **RMSE (Root Mean Squared Error)**: 予測値と実測値の差の二乗平均の平方根。外れ値の影響を受けやすい。
        - **R² (R-squared)**: モデルの説明力を示す指標。0~1の範囲で、1に近いほど良い。
        """)
    else:
        st.info("モデルを学習すると、評価指標が表示されます")

# -----------------------------------------------------------------------------
# Tab 3: SHAP解析
# -----------------------------------------------------------------------------
with tab3:
    st.header("SHAP解析")

    if st.session_state.trained and st.session_state.model is not None and st.session_state.X_test is not None:
        st.markdown("""
        ### 🔍 モデル解釈
        SHAPを使用して、各特徴量がモデルの予測にどのように影響しているかを可視化します。
        """)

        display_shap_plots(
            st.session_state.model,
            st.session_state.X_test,
            max_samples=1000
        )
    else:
        st.info("モデルを学習すると、SHAP解析が表示されます")

# -----------------------------------------------------------------------------
# Tab 4: 予測結果
# -----------------------------------------------------------------------------
with tab4:
    st.header("予測結果")

    if st.session_state.trained and (target_file is not None or st.session_state.using_default_data) and 'target_df' in st.session_state and st.session_state.target_df is not None:
        target_df = st.session_state.target_df
        feature_cols = st.session_state.feature_cols
        label_encoders = st.session_state.label_encoders
        model = st.session_state.model

        try:
            # 特徴量の整合性チェック
            is_compatible, missing_cols = check_feature_compatibility(
                feature_cols,
                target_df.columns.tolist()
            )

            if not is_compatible:
                st.error(f"❌ ターゲットデータに以下のカラムがありません: {missing_cols}")
            else:
                # ターゲットデータの前処理
                target_processed, _ = preprocess_data(
                    target_df[feature_cols],
                    target_col=None,  # 予測データなので目的変数はなし
                    label_encoders=label_encoders,
                    is_training=False
                )

                # 予測実行
                with st.spinner("🔮 予測を実行中..."):
                    predictions = predict(model, target_processed)

                # 結果DataFrame作成
                result_df = target_df.copy()
                result_df['予測値'] = predictions

                st.success(f"✅ {len(result_df)}件の予測が完了しました！")

                # 上位10件を表示（特徴量は左から最大5列）
                st.subheader("📋 予測結果（上位10件）")
                display_cols = feature_cols[:5] + ['予測値']
                display_df = result_df[display_cols].head(10)
                st.dataframe(display_df, use_container_width=True)

                # 統計情報
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("予測値の平均", f"{predictions.mean():.4f}")
                with col2:
                    st.metric("予測値の最小値", f"{predictions.min():.4f}")
                with col3:
                    st.metric("予測値の最大値", f"{predictions.max():.4f}")

                # CSVダウンロード
                st.markdown("---")
                st.subheader("⬇️ ダウンロード")

                csv_data = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 予測結果をCSVでダウンロード",
                    data=csv_data,
                    file_name="prediction_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"❌ 予測エラー: {str(e)}")

    elif st.session_state.trained and target_file is None:
        st.info("👈 サイドバーからターゲットデータをアップロードしてください")
    else:
        st.info("モデルを学習し、ターゲットデータをアップロードすると予測結果が表示されます")

# =============================================================================
# フッター
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.caption("ML Prediction App v0.1")
