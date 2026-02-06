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
st.sidebar.caption("AIに学習させるための「お手本データ」です。正解（予測したい値）を含むデータをアップロードしてください。")
train_file = st.sidebar.file_uploader(
    "訓練用データをアップロード",
    type=['csv', 'xlsx', 'xls'],
    key='train_file'
)

st.sidebar.subheader("📁 ターゲットデータ")
st.sidebar.caption("予測したい対象のデータです。正解の値がなくてもOKです。教師データと同じ項目（列）を含む必要があります。")
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
    st.sidebar.caption("AIに予測させたい項目を選んでください。例：「売上」「価格」「年収」など、数値で表される列を選びます。")

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

st.info(
    "**このアプリでできること：** 過去のデータ（例：売上実績や顧客情報）をもとに、"
    "AIが自動でパターンを学習し、まだ結果が分かっていないデータに対して数値を予測します。"
    "たとえば「この顧客の購入額はいくらになりそうか？」といった予測が、プログラミング不要で行えます。"
)

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
with st.expander("📖 使い方（はじめての方はこちら）", expanded=False):
    st.markdown("""
    ### このアプリの流れ
    過去のデータからAIが法則を学び、新しいデータに対して数値を予測します。

    ---

    ### ステップ1: 教師データのアップロード
    まず、AIに学習させるための**お手本データ**（教師データ）を用意します。
    - サイドバーの「教師データ」からCSVまたはExcelファイルをアップロード
    - 教師データには、**予測したい値（正解）が含まれている**必要があります
    - 例：社員の年齢・経験年数・年収の一覧表（年収を予測したい場合）

    ### ステップ2: 目的変数の選択
    「目的変数」とは、**AIに予測させたい項目**のことです。
    - サイドバーのドロップダウンから、予測したい列を選びます
    - それ以外の列は自動的に「特徴量」（予測の手がかりとなる情報）になります
    - 例：「年収」を目的変数にすると、年齢や経験年数などが特徴量になります

    ### ステップ3: モデル学習
    「モデル学習」とは、**AIがデータのパターンを覚える作業**のことです。
    - サイドバーの「▶️ モデル学習」ボタンをクリック
    - 学習が完了するまでお待ちください（通常は数秒で終わります）

    ### ステップ4: 結果の確認
    AIがどれくらい正確に予測できるかを確認します。
    - **評価指標タブ**: 予測の正確さをスコアで確認できます
    - **SHAP解析タブ**: どの項目が予測に大きく影響しているかを視覚的に確認できます

    ### ステップ5: 予測の実行
    学習済みのAIを使って、新しいデータの予測を行います。
    - サイドバーの「ターゲットデータ」から、予測したいデータをアップロード
    - 予測結果タブで結果を確認し、CSVボタンでダウンロードできます
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
    st.markdown(
        "アップロードしたデータの中身を確認できます。"
        "**行数**はデータの件数（例：100人分のデータなら100行）、"
        "**列数**は項目数（例：年齢・年収・部署などの数）、"
        "**欠損値**は値が入っていない箇所の数を表します。欠損値が多いと予測精度に影響することがあります。"
    )

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
    st.markdown(
        "AIの予測がどれくらい正確かを数値で示します。"
        "学習時にデータの一部（20%）をテスト用に取り分けておき、"
        "AIが**まだ見たことのないデータ**に対してどれくらい正しく予測できるかを測定しています。"
    )

    if st.session_state.trained and st.session_state.metrics is not None:
        st.markdown("### 📊 テストデータでの評価")
        display_metrics(st.session_state.metrics)

        st.markdown("---")
        st.markdown("### 📈 評価指標のかんたん解説")
        st.markdown("""
| 指標 | ひとことで言うと | 読み方のポイント |
|:---|:---|:---|
| **MAE** | 予測が平均でどれくらいズレるか | 例：MAE=50なら「平均して50くらいズレる」。**小さいほど正確** |
| **RMSE** | 大きなハズレがないかを見る指標 | MAEと似ていますが、大きく外れた予測があると値が跳ね上がります。**小さいほど良い** |
| **R²** | AIがデータの傾向をどれだけ捉えているか | 1.0 = 完璧、0.5 = まあまあ、0以下 = 予測が当てにならない。**1に近いほど優秀** |
        """)
    else:
        st.info("モデルを学習すると、評価指標が表示されます。サイドバーの「モデル学習」ボタンを押してください。")

# -----------------------------------------------------------------------------
# Tab 3: SHAP解析
# -----------------------------------------------------------------------------
with tab3:
    st.header("SHAP解析")
    st.markdown(
        "SHAP解析は、**AIがなぜその予測をしたのかを説明する技術**です。"
        "「どの項目が予測結果を大きく左右しているか」を可視化することで、"
        "AIの判断根拠を人間が理解できるようにします。"
    )

    if st.session_state.trained and st.session_state.model is not None and st.session_state.X_test is not None:
        st.markdown("""
        ### 🔍 グラフの読み方

        **Summary Plot（上のグラフ）** -- 各項目がAIの予測にどう影響しているかを一目で把握できます。
        - 横軸：予測値を押し上げる（右）／押し下げる（左）影響の大きさ
        - 色：その項目の値が高い（赤）か低い（青）か
        - 例：「年齢」の赤い点が右に多い → 年齢が高いほど予測値が上がる傾向

        **特徴量重要度（下のグラフ）** -- 各項目の影響力の大きさをランキングで表示します。上にある項目ほど予測に大きく影響しています。
        """)

        display_shap_plots(
            st.session_state.model,
            st.session_state.X_test,
            max_samples=1000
        )
    else:
        st.info("モデルを学習すると、SHAP解析が表示されます。サイドバーの「モデル学習」ボタンを押してください。")

# -----------------------------------------------------------------------------
# Tab 4: 予測結果
# -----------------------------------------------------------------------------
with tab4:
    st.header("予測結果")
    st.markdown(
        "学習済みのAIモデルを使って、ターゲットデータ（新しいデータ）に対する予測を行った結果です。"
        "「予測値」の列がAIの出した予測結果になります。"
        "結果はCSVファイルとしてダウンロードできるので、Excelなどで自由に活用できます。"
    )

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
                st.markdown("##### 予測値の統計サマリー")
                st.caption("全件の予測値を集計したものです。平均値は全体の傾向、最小・最大値は予測の幅を示します。")
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
        st.info("👈 サイドバーの「ターゲットデータ」から、予測したいデータ（CSV/Excel）をアップロードしてください。教師データと同じ項目（列）を含むファイルが必要です。")
    else:
        st.info("予測を行うには、まずモデルを学習し、次にターゲットデータをアップロードしてください。左のサイドバーから操作できます。")

# =============================================================================
# フッター
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.caption("ML Prediction App v0.1")
