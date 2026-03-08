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

from modules.data_loader import load_file, display_data_info, display_preview, display_data_quality_report
from modules.model import preprocess_data, split_data, train_model, predict, check_feature_compatibility, handle_missing_values
from modules.evaluation import calculate_metrics, display_metrics, display_prediction_scatter, generate_model_interpretation
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
if 'y_pred' not in st.session_state:
    st.session_state.y_pred = None
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
                st.session_state.y_pred = y_pred

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

    # 数値列のみを回帰対象として推奨表示（批判的思考: 型バリデーション）
    numeric_cols = st.session_state.train_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    all_cols = st.session_state.train_df.columns.tolist()

    target_col = st.sidebar.selectbox(
        "予測する変数を選択",
        options=all_cols,
        index=default_index
    )

    # 目的変数のバリデーション（批判的思考）
    if target_col not in numeric_cols:
        st.sidebar.warning(f"⚠️ 「{target_col}」はカテゴリ変数です。回帰予測には数値変数を選択してください。")

    # 目的変数の基本統計を表示（論理的思考: 選択の妥当性確認）
    if target_col in numeric_cols:
        target_series = st.session_state.train_df[target_col]
        with st.sidebar.expander(f"📈 {target_col} の分布情報"):
            st.write(f"**平均**: {target_series.mean():.2f}")
            st.write(f"**中央値**: {target_series.median():.2f}")
            st.write(f"**標準偏差**: {target_series.std():.2f}")
            st.write(f"**最小値**: {target_series.min():.2f}")
            st.write(f"**最大値**: {target_series.max():.2f}")
            # 外れ値チェック
            q1 = target_series.quantile(0.25)
            q3 = target_series.quantile(0.75)
            iqr = q3 - q1
            outlier_count = ((target_series < q1 - 1.5 * iqr) | (target_series > q3 + 1.5 * iqr)).sum()
            if outlier_count > 0:
                st.write(f"**外れ値候補**: {outlier_count}件")

    # 特徴量の自動設定
    feature_cols = [col for col in st.session_state.train_df.columns if col != target_col]

    st.sidebar.info(f"✅ 特徴量: {len(feature_cols)}個")
    with st.sidebar.expander("特徴量一覧"):
        for i, col in enumerate(feature_cols, 1):
            dtype_label = "数値" if col in numeric_cols else "カテゴリ"
            st.write(f"{i}. {col} ({dtype_label})")

    # セッションに保存
    st.session_state.target_col = target_col
    st.session_state.feature_cols = feature_cols

st.sidebar.markdown("---")

# 学習実行ボタン（デフォルトデータまたはアップロードされたデータがある場合）
if (train_file is not None or st.session_state.using_default_data) and target_col is not None:
    # ステップ3強化: ハイパーパラメータ設定UI（グロース思考: ユーザーのML理解を促進）
    with st.sidebar.expander("⚙️ 学習パラメータ設定"):
        st.caption("パラメータを調整してモデルの精度を改善できます")
        n_estimators = st.slider(
            "木の数 (n_estimators)",
            min_value=10, max_value=500, value=100, step=10,
            help="大きいほど精度が上がりやすいが、学習に時間がかかります"
        )
        learning_rate = st.select_slider(
            "学習率 (learning_rate)",
            options=[0.01, 0.05, 0.1, 0.2, 0.3],
            value=0.1,
            help="小さいほど慎重に学習しますが、木の数を増やす必要があります"
        )
        max_depth = st.slider(
            "木の深さ (max_depth)",
            min_value=2, max_value=15, value=6,
            help="大きいほど複雑なパターンを学習できますが、過学習のリスクが増します"
        )
        test_size = st.slider(
            "テストデータ割合",
            min_value=0.1, max_value=0.4, value=0.2, step=0.05,
            help="モデル評価に使用するデータの割合"
        )

    # デフォルトデータで既に学習済みの場合は「再学習」ボタン表示
    button_label = "🔄 再学習" if st.session_state.trained else "▶️ モデル学習"

    if st.sidebar.button(button_label, type="primary", use_container_width=True):
        with st.spinner("🔄 モデルを学習中..."):
            # 警告を完全に抑制
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                try:
                    # ステップ3強化: 欠損値の自動処理（批判的思考: データの問題を自動解決）
                    df_clean, missing_report = handle_missing_values(
                        st.session_state.train_df.copy(), target_col
                    )

                    # 欠損値処理の結果を表示
                    if missing_report['dropped_rows'] > 0:
                        st.sidebar.info(f"💡 目的変数の欠損 {missing_report['dropped_rows']}行を除外しました")
                    if missing_report['filled_cols']:
                        st.sidebar.info(f"💡 {len(missing_report['filled_cols'])}列の欠損値を自動補完しました")

                    # データの前処理
                    df_processed, label_encoders = preprocess_data(
                        df_clean,
                        target_col,
                        is_training=True
                    )

                    # Train/Test分割
                    X_train, X_test, y_train, y_test = split_data(
                        df_processed.copy(),
                        target_col,
                        test_size=test_size,
                        random_state=42
                    )

                    # モデル学習（ユーザー指定パラメータ）
                    model = train_model(
                        X_train, y_train,
                        n_estimators=n_estimators,
                        learning_rate=learning_rate,
                        max_depth=max_depth
                    )

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
                    st.session_state.y_pred = y_pred

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
with st.expander("📖 使い方ガイド", expanded=False):
    st.markdown("""
    ### ステップ1: 教師データのアップロード
    サイドバーから訓練用データ（CSV/Excel）をアップロードします。
    - **データ品質診断**が自動実行され、欠損値・重複・外れ値候補を検出します
    - 品質スコア（100点満点）でデータの準備状況を確認できます
    - 問題がある場合、具体的な対処方法が表示されます

    ### ステップ2: 目的変数の選択
    予測したい数値変数をドロップダウンから選択します。
    - 数値型以外を選ぶと警告が表示されます（回帰分析のため）
    - 選択した変数の**分布情報**（平均・中央値・外れ値候補数）を確認できます
    - 特徴量一覧にデータ型が表示され、カテゴリ/数値の構成が把握できます

    ### ステップ3: モデル学習
    パラメータを調整し、「モデル学習」ボタンで学習を実行します。
    - **パラメータ設定**: 木の数・学習率・深さ・テストデータ割合を調整可能
    - **欠損値の自動処理**: 数値列は中央値、カテゴリ列は専用ラベルで自動補完
    - パラメータを変えて再学習し、精度の変化を比較できます

    ### ステップ4: 結果の確認
    モデルの性能を多角的に評価します。
    - **評価指標**: MAE・RMSE・R²の数値とその解釈テキスト
    - **散布図**: 実測値 vs 予測値の比較と残差プロット
    - **SHAP解析**: どの特徴量が予測に影響しているかを可視化
    - 「このモデルはビジネスに使えるか」の判断材料が揃います

    ### ステップ5: 予測の実行
    ターゲットデータをアップロードして予測を実行します。
    - 教師データとのカラム整合性を自動チェック
    - **予測値の分布**をヒストグラムで確認できます
    - 統計サマリー（平均・中央値・最小・最大）で全体傾向を把握
    - 予測結果をCSVでダウンロード可能
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

            # データ品質診断（ステップ1強化: 批判的思考 - データの問題点を事前に可視化）
            display_data_quality_report(train_df, "教師データ")

            st.markdown("##### 先頭10行のプレビュー")
            display_preview(train_df, n_rows=10)

            # セッションに保存
            st.session_state.train_df = train_df
    elif st.session_state.using_default_data and st.session_state.train_df is not None:
        # デフォルトデータの表示
        st.subheader("📊 教師データ（デモデータ）")
        display_data_info(st.session_state.train_df, "教師データ")

        # データ品質診断
        display_data_quality_report(st.session_state.train_df, "教師データ")

        st.markdown("##### 先頭10行のプレビュー")
        display_preview(st.session_state.train_df, n_rows=10)
    else:
        st.info("👈 サイドバーから教師データをアップロードしてください")
        # グロース思考: ユーザーに良いデータの要件を伝える
        with st.expander("💡 教師データの準備ガイド"):
            st.markdown("""
            **良い教師データのポイント:**
            - **行数**: 最低30件以上（100件以上推奨）
            - **欠損値**: できるだけ少なく（30%未満を推奨）
            - **目的変数**: 予測したい数値の列を含める
            - **対応形式**: CSV (.csv) または Excel (.xlsx, .xls)

            **よくある問題:**
            - ヘッダー行がない → 1行目がカラム名として読み込まれます
            - 全角数字 → 自動変換されません。事前に半角に統一してください
            - 日付列 → カテゴリとして扱われます
            """)

    st.markdown("---")

    # ターゲットデータの読み込みと表示
    if target_file is not None:
        target_df = load_file(target_file)
        if target_df is not None:
            st.subheader("🎯 ターゲットデータ")
            display_data_info(target_df, "ターゲットデータ")

            # ターゲットデータの品質診断
            display_data_quality_report(target_df, "ターゲットデータ")

            st.markdown("##### 先頭10行のプレビュー")
            display_preview(target_df, n_rows=10)

            # セッションに保存
            st.session_state.target_df = target_df
    elif st.session_state.using_default_data and st.session_state.target_df is not None:
        # デフォルトターゲットデータの表示
        st.subheader("🎯 ターゲットデータ（デモデータ）")
        display_data_info(st.session_state.target_df, "ターゲットデータ")
        display_data_quality_report(st.session_state.target_df, "ターゲットデータ")
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

        # ステップ4強化: モデル性能の自動解釈（新規事業思考: 非エンジニアでも判断可能に）
        if st.session_state.y_test is not None and st.session_state.y_pred is not None:
            st.markdown("---")
            st.markdown("### 💬 モデル性能の解釈")
            interpretation = generate_model_interpretation(
                st.session_state.metrics,
                np.array(st.session_state.y_test),
                np.array(st.session_state.y_pred)
            )
            st.markdown(interpretation)

            # ステップ4強化: 散布図・残差プロット（論理的思考: 視覚的な検証）
            st.markdown("---")
            st.markdown("### 📈 予測精度の可視化")
            st.caption("左: 実測値と予測値の比較（対角線に近いほど高精度）  右: 残差の分布（0付近に集中しているほど良い）")
            display_prediction_scatter(
                np.array(st.session_state.y_test),
                np.array(st.session_state.y_pred)
            )

        st.markdown("---")
        # 評価指標の説明（折りたたみに変更 - グロース思考: 必要な人が学べる）
        with st.expander("📖 評価指標の説明"):
            st.markdown("""
            | 指標 | 意味 | 良い値の目安 |
            |------|------|-------------|
            | **MAE** | 予測誤差の平均（単位は目的変数と同じ） | 小さいほど良い |
            | **RMSE** | 大きな誤差をより重視した指標 | MAEに近いほど外れ値の影響が少ない |
            | **R²** | モデルの説明力（0〜1） | 0.7以上で良好、0.9以上で優秀 |
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
            # 特徴量の整合性チェック（論理的思考: 詳細な差異表示）
            is_compatible, missing_cols = check_feature_compatibility(
                feature_cols,
                target_df.columns.tolist()
            )

            if not is_compatible:
                st.error(f"❌ ターゲットデータに以下のカラムがありません: {missing_cols}")
                st.markdown("**対処方法**: 教師データと同じ列名を持つデータをアップロードしてください。")
            else:
                # ターゲットデータの欠損値処理（ステップ5強化: 批判的思考）
                target_for_pred = target_df[feature_cols].copy()
                missing_in_target = target_for_pred.isnull().sum().sum()
                if missing_in_target > 0:
                    target_for_pred, _ = handle_missing_values(target_for_pred)
                    st.info(f"💡 ターゲットデータの欠損値 {missing_in_target}件を自動補完しました")

                # ターゲットデータの前処理
                target_processed, _ = preprocess_data(
                    target_for_pred,
                    target_col=None,
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

                # ステップ5強化: サマリー統計（新規事業思考: 意思決定支援）
                st.subheader("📊 予測結果サマリー")
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                with stat_col1:
                    st.metric("平均値", f"{predictions.mean():.2f}")
                with stat_col2:
                    st.metric("中央値", f"{np.median(predictions):.2f}")
                with stat_col3:
                    st.metric("最小値", f"{predictions.min():.2f}")
                with stat_col4:
                    st.metric("最大値", f"{predictions.max():.2f}")

                # ステップ5強化: 予測値の分布ヒストグラム（水平思考: 全体像の可視化）
                st.markdown("---")
                st.subheader("📈 予測値の分布")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.hist(predictions, bins=30, color='#2196F3', alpha=0.7, edgecolor='white')
                ax.axvline(predictions.mean(), color='red', linestyle='--', label=f'Mean: {predictions.mean():.2f}')
                ax.axvline(np.median(predictions), color='green', linestyle='--', label=f'Median: {np.median(predictions):.2f}')
                ax.set_xlabel('Predicted Value')
                ax.set_ylabel('Count')
                ax.set_title('Distribution of Predictions')
                ax.legend()
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

                # 上位10件を表示（特徴量は左から最大5列）
                st.markdown("---")
                st.subheader("📋 予測結果（上位10件）")
                display_cols = feature_cols[:5] + ['予測値']
                display_df = result_df[display_cols].head(10)
                st.dataframe(display_df, use_container_width=True)

                # ステップ5強化: 予測結果の読み方ガイド（グロース思考）
                with st.expander("💡 予測結果の読み方"):
                    st.markdown(f"""
                    - **予測値の範囲**: {predictions.min():.2f} 〜 {predictions.max():.2f}
                    - **標準偏差**: {predictions.std():.2f}（値のばらつきの大きさ）
                    - 平均値と中央値が大きく異なる場合、データに偏りがある可能性があります
                    - 極端に高い/低い予測値は、外れ値の可能性があるため確認してください
                    """)

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
