# 開発Issue一覧

## 📊 進捗管理表

| Issue # | タイトル | 優先度 | 依存 | 見積もり | 状態 |
|---------|----------|--------|------|----------|------|
| #1 | プロジェクトセットアップ | 🔴 高 | - | 0.5日 | ✅ 完了 |
| #2 | データ入力機能の実装 | 🔴 高 | #1 | 1日 | ✅ 完了 |
| #3 | 変数設定機能の実装 | 🔴 高 | #2 | 0.5日 | ✅ 完了 |
| #4 | モデル学習機能の実装 | 🔴 高 | #3 | 1日 | ✅ 完了 |
| #5 | モデル評価機能の実装 | 🟡 中 | #4 | 0.5日 | ✅ 完了 |
| #6 | SHAP解釈機能の実装 | 🟡 中 | #4 | 1日 | ✅ 完了 |
| #7 | 予測・出力機能の実装 | 🔴 高 | #4 | 1日 | ✅ 完了 |
| #8 | UI/UX調整・統合テスト | 🟡 中 | #5,#6,#7 | 1日 | ✅ 完了 |

**状態**: ✅ 完了 / 🔄 進行中 / ⬜ 未着手

---

## Issue #1: プロジェクトセットアップ ✅

### 概要
開発環境の構築と必要なライブラリのインストール、プロジェクト構成の作成

### タスク
- [x] プロジェクトディレクトリ構成の作成
- [x] `requirements.txt` の作成
- [x] Streamlitの基本テンプレート作成（サイドバー + メインエリア構成）
- [x] 動作確認

### 受け入れ条件
- [x] `streamlit run app.py` で空のアプリが起動する
- [x] サイドバーとメインエリアの基本レイアウトが表示される

### 実装ファイル
- `app.py`（基本テンプレート）
- `modules/__init__.py`

---

## Issue #2: データ入力機能の実装 ✅

### 概要
教師データとターゲットデータのアップロード機能を実装

### タスク
- [x] サイドバーに教師データアップロードUI実装
- [x] サイドバーにターゲットデータアップロードUI実装
- [x] CSV/Excel両対応のファイル読み込み処理
- [x] メインエリアにデータプレビュー表示（先頭10行）
- [x] データ形状（行数・列数）の表示
- [x] エラーハンドリング（不正ファイル対応）

### 受け入れ条件
- [x] CSV形式のファイルをアップロードし、プレビューが表示される
- [x] Excel形式（.xlsx, .xls）のファイルをアップロードし、プレビューが表示される
- [x] 教師データ・ターゲットデータそれぞれ別々にアップロードできる
- [x] 不正ファイルの場合、エラーメッセージが表示される

### 実装ファイル
- `modules/data_loader.py`
- `app.py`（UI部分）

### コード例
```python
# modules/data_loader.py
import pandas as pd
import streamlit as st

def load_file(uploaded_file):
    """
    アップロードされたファイルを読み込んでDataFrameを返す
    
    Parameters:
    -----------
    uploaded_file : UploadedFile
        Streamlitのファイルアップローダーからのファイル
        
    Returns:
    --------
    pd.DataFrame or None
        読み込んだDataFrame、エラー時はNone
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("対応していないファイル形式です。CSV または Excel をアップロードしてください。")
            return None
        return df
    except Exception as e:
        st.error(f"ファイル読み込みエラー: {str(e)}")
        return None
```

---

## Issue #3: 変数設定機能の実装 ✅

### 概要
目的変数の選択UIと特徴量の自動設定機能を実装

### タスク
- [x] 教師データのカラム一覧をドロップダウンで表示
- [x] 目的変数（ターゲット変数）の選択機能
- [x] 選択された目的変数以外を特徴量として自動設定
- [x] 選択された変数情報の表示（確認用）

### 受け入れ条件
- [x] 教師データアップロード後、カラム一覧がドロップダウンに表示される
- [x] 目的変数を選択すると、特徴量一覧が自動表示される
- [x] 目的変数の変更が即座に反映される

### 実装ファイル
- `app.py`（UI部分）

### コード例
```python
# app.py内
if train_df is not None:
    # 目的変数の選択
    target_col = st.sidebar.selectbox(
        "🎯 目的変数を選択",
        options=train_df.columns.tolist(),
        index=len(train_df.columns) - 1  # デフォルトは最後の列
    )
    
    # 特徴量の自動設定
    feature_cols = [col for col in train_df.columns if col != target_col]
    
    st.sidebar.write(f"特徴量: {len(feature_cols)}個")
```

---

## Issue #4: モデル学習機能の実装 ✅

### 概要
LightGBMによる回帰モデルの学習機能を実装

### タスク
- [x] LightGBM回帰モデルの実装
- [x] Train/Test分割処理（8:2）
- [x] 「学習実行」ボタンの実装
- [x] 学習中のプログレス表示
- [x] 学習済みモデルのセッション状態保持
- [x] カテゴリ変数の自動エンコーディング（Label Encoding）

### 受け入れ条件
- [x] 「学習実行」ボタンクリックでモデル学習が開始される
- [x] 学習完了後、成功メッセージが表示される
- [x] 学習済みモデルがセッションに保持され、再利用可能
- [x] 数値・カテゴリ混在データでもエラーなく学習できる

### 実装ファイル
- `modules/model.py`
- `app.py`（UI部分）

### コード例
```python
# modules/model.py
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def preprocess_data(df, target_col, label_encoders=None):
    """
    データの前処理（カテゴリ変数のエンコーディング）
    """
    df_processed = df.copy()
    
    if label_encoders is None:
        label_encoders = {}
        
    # カテゴリ変数をLabel Encoding
    for col in df_processed.columns:
        if col == target_col:
            continue
        if df_processed[col].dtype == 'object':
            if col not in label_encoders:
                label_encoders[col] = LabelEncoder()
                df_processed[col] = label_encoders[col].fit_transform(
                    df_processed[col].astype(str)
                )
            else:
                df_processed[col] = label_encoders[col].transform(
                    df_processed[col].astype(str)
                )
    
    return df_processed, label_encoders

def train_model(X_train, y_train):
    """
    LightGBMモデルの学習
    """
    model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42,
        verbose=-1
    )
    model.fit(X_train, y_train)
    return model
```

---

## Issue #5: モデル評価機能の実装 ✅

### 概要
学習済みモデルの評価指標を算出・表示

### タスク
- [x] MAE（平均絶対誤差）の算出
- [x] RMSE（二乗平均平方根誤差）の算出
- [x] R²（決定係数）の算出
- [x] 評価指標のカード形式での表示

### 受け入れ条件
- [x] モデル学習後、3つの評価指標が表示される
- [x] 指標は見やすいカード/メトリクス形式で表示される
- [x] 各指標の数値が正しく算出されている

### 実装ファイル
- `modules/evaluation.py`
- `app.py`（UI部分）

### コード例
```python
# modules/evaluation.py
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def calculate_metrics(y_true, y_pred):
    """
    評価指標を算出
    
    Returns:
    --------
    dict: MAE, RMSE, R2を含む辞書
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2
    }
```

---

## Issue #6: SHAP解釈機能の実装 ✅

### 概要
SHAPによるモデル解釈・可視化機能を実装

### タスク
- [x] SHAP Explainerの実装（TreeExplainer）
- [x] SHAP値の算出
- [x] Summary Plot（beeswarm）の生成・表示
- [x] Bar Plot（特徴量重要度）の生成・表示
- [x] 可視化の描画最適化（サンプリング等）

### 受け入れ条件
- [x] モデル学習後、SHAP Summary Plotが表示される
- [x] SHAP Bar Plotが表示される
- [x] 大規模データでもタイムアウトせず表示される（サンプリング対応）

### 実装ファイル
- `modules/shap_analysis.py`
- `app.py`（UI部分）

### コード例
```python
# modules/shap_analysis.py
import shap
import matplotlib.pyplot as plt
import streamlit as st

def create_shap_plots(model, X, max_samples=1000):
    """
    SHAP可視化を生成
    
    Parameters:
    -----------
    model : LGBMRegressor
        学習済みモデル
    X : pd.DataFrame
        特徴量データ
    max_samples : int
        SHAP計算に使用する最大サンプル数
    """
    # サンプリング（大規模データ対応）
    if len(X) > max_samples:
        X_sample = X.sample(n=max_samples, random_state=42)
    else:
        X_sample = X
    
    # SHAP値の計算
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    # Summary Plot
    fig_summary, ax_summary = plt.subplots(figsize=(10, 6))
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.tight_layout()
    
    # Bar Plot
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
    plt.tight_layout()
    
    return fig_summary, fig_bar
```

---

## Issue #7: 予測・出力機能の実装 ✅

### 概要
ターゲットデータへの予測適用と結果出力機能を実装

### タスク
- [x] ターゲットデータへの予測実行処理
- [x] 予測結果の上位10件表示（特徴量は左から最大5列）
- [x] 予測結果全体のCSVダウンロード機能
- [x] ターゲットデータの特徴量整合性チェック

### 受け入れ条件
- [x] ターゲットデータに対して予測が実行される
- [x] 予測結果の上位10件がテーブル形式で表示される
- [x] CSVダウンロードボタンで予測結果がダウンロードできる
- [x] 教師データとカラムが一致しない場合、エラーメッセージが表示される

### 実装ファイル
- `modules/model.py`（予測処理追加）
- `app.py`（UI部分）

### コード例
```python
# app.py内
def predict_and_display(model, target_df, feature_cols, label_encoders):
    """
    予測実行と結果表示
    """
    # 特徴量の整合性チェック
    missing_cols = set(feature_cols) - set(target_df.columns)
    if missing_cols:
        st.error(f"ターゲットデータに以下のカラムがありません: {missing_cols}")
        return None
    
    # 前処理
    X_target = target_df[feature_cols].copy()
    for col in X_target.columns:
        if col in label_encoders:
            X_target[col] = label_encoders[col].transform(X_target[col].astype(str))
    
    # 予測
    predictions = model.predict(X_target)
    
    # 結果DataFrame作成
    result_df = target_df.copy()
    result_df['予測値'] = predictions
    
    return result_df
```

---

## Issue #8: UI/UX調整・統合テスト ✅

### 概要
全機能の統合テストとUI/UXの最終調整

### タスク
- [x] 全機能の結合テスト
- [x] エラーハンドリングの統一
- [x] UIの見た目調整（余白、色、フォント）
- [x] 処理状態の表示改善（spinner等）
- [x] 使い方の説明文追加
- [x] エッジケーステスト（欠損値、大規模データ等）

### 受け入れ条件
- [x] 一連のフロー（アップロード→変数選択→学習→評価→予測→ダウンロード）が正常動作
- [x] エラー時に適切なメッセージが表示される
- [x] UIが直感的で使いやすい

### 実装ファイル
- `app.py`（全体調整）

### チェックリスト
- [x] 空ファイルアップロード時の動作
- [x] 数値のみデータでの動作
- [x] カテゴリのみデータでの動作
- [x] 混在データでの動作
- [x] 欠損値含むデータでの動作
- [x] 1万行データでの動作確認
- [x] 10万行データでの動作確認

---

## 📝 完了後の確認事項

- [x] 全Issueのタスクが完了
- [x] README.mdが最新化されている
- [x] コードにコメントが適切に付与されている
- [x] 不要なデバッグコードが削除されている
- [x] requirements.txtが正確

---

## 🎉 プロジェクト完了

全てのIssueが完了しました！ML予測アプリケーションは以下の機能を備えています：

- データアップロード（CSV/Excel対応）
- 目的変数の選択と特徴量の自動設定
- LightGBMによる回帰モデルの学習
- 評価指標の表示（MAE, RMSE, R²）
- SHAP解析による特徴量重要度の可視化
- 予測結果のCSVダウンロード
