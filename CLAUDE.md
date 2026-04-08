# ML Prediction App - Claude Code Project Guide

## ファイルインデックス

作業開始前に **`_file_index.md`** を参照してください。全ブランチのファイル概要・目的別クイックリファレンスを記載しています（`claude/check-repo-file-lists-desRY` ブランチ以降に存在）。詳細な全ファイル一覧は **`docs/file-index.md`**（`claude/integrate-business-plan-IBKFu` ブランチ以降）も参照してください。

## プロジェクト概要
Streamlitを使用した機械学習（LightGBM）回帰予測アプリケーション

## 技術スタック
- **フレームワーク**: Streamlit
- **言語**: Python 3.9+
- **ML**: LightGBM, scikit-learn
- **解釈性**: SHAP
- **データ処理**: pandas, numpy

## ディレクトリ構成
```
ml-prediction-app/
├── app.py                 # メインアプリケーション
├── requirements.txt       # 依存ライブラリ
├── modules/
│   ├── __init__.py
│   ├── data_loader.py     # データ読み込み処理
│   ├── model.py           # LightGBMモデル処理
│   ├── evaluation.py      # 評価指標算出
│   └── shap_analysis.py   # SHAP解析処理
├── _file_index.md         # ファイルインデックス（ブランチ横断ナビゲーション）
├── CLAUDE.md              # このファイル
├── ISSUES.md              # 開発Issue一覧
└── README.md              # 使用方法
```

## 開発コマンド
```bash
# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
streamlit run app.py

# ポート指定起動
streamlit run app.py --server.port 8501
```

## Issue一覧（開発順序）

### Issue #1: プロジェクトセットアップ [優先度:高]
- [x] プロジェクトディレクトリ構成の作成
- [x] requirements.txt の作成
- [ ] Streamlitの基本テンプレート作成（サイドバー + メインエリア構成）
- [ ] 動作確認

### Issue #2: データ入力機能の実装 [優先度:高] [依存:#1]
- [ ] サイドバーに教師データアップロードUI実装
- [ ] サイドバーにターゲットデータアップロードUI実装
- [ ] CSV/Excel両対応のファイル読み込み処理
- [ ] メインエリアにデータプレビュー表示（先頭10行）
- [ ] データ形状（行数・列数）の表示
- [ ] エラーハンドリング（不正ファイル対応）

### Issue #3: 変数設定機能の実装 [優先度:高] [依存:#2]
- [ ] 教師データのカラム一覧をドロップダウンで表示
- [ ] 目的変数（ターゲット変数）の選択機能
- [ ] 選択された目的変数以外を特徴量として自動設定
- [ ] 選択された変数情報の表示（確認用）

### Issue #4: モデル学習機能の実装 [優先度:高] [依存:#3]
- [ ] LightGBM回帰モデルの実装
- [ ] Train/Test分割処理（8:2）
- [ ] 「学習実行」ボタンの実装
- [ ] 学習中のプログレス表示
- [ ] 学習済みモデルのセッション状態保持
- [ ] カテゴリ変数の自動エンコーディング（Label Encoding）

### Issue #5: モデル評価機能の実装 [優先度:中] [依存:#4]
- [ ] MAE（平均絶対誤差）の算出
- [ ] RMSE（二乗平均平方根誤差）の算出
- [ ] R²（決定係数）の算出
- [ ] 評価指標のカード形式での表示

### Issue #6: SHAP解釈機能の実装 [優先度:中] [依存:#4]
- [ ] SHAP Explainerの実装（TreeExplainer）
- [ ] SHAP値の算出
- [ ] Summary Plot（beeswarm）の生成・表示
- [ ] Bar Plot（特徴量重要度）の生成・表示
- [ ] 可視化の描画最適化（サンプリング等）

### Issue #7: 予測・出力機能の実装 [優先度:高] [依存:#4]
- [ ] ターゲットデータへの予測実行処理
- [ ] 予測結果の上位10件表示（特徴量は左から最大5列）
- [ ] 予測結果全体のCSVダウンロード機能
- [ ] ターゲットデータの特徴量整合性チェック

### Issue #8: UI/UX調整・統合テスト [優先度:中] [依存:#5,#6,#7]
- [ ] 全機能の結合テスト
- [ ] エラーハンドリングの統一
- [ ] UIの見た目調整（余白、色、フォント）
- [ ] 処理状態の表示改善（spinner等）
- [ ] 使い方の説明文追加
- [ ] エッジケーステスト（欠損値、大規模データ等）

## 画面構成
```
┌─────────────────────────────────────────────────────┐
│  サイドバー           │  メインエリア                │
│ ─────────────────    │                              │
│ 📁 教師データUP       │  ① データプレビュー         │
│ 📁 ターゲットデータUP │  ② 評価指標スコア          │
│ 🎯 目的変数選択       │  ③ SHAP可視化              │
│ ▶️ 実行ボタン         │  ④ 予測結果（上位10件）    │
│                       │  ⬇️ ダウンロードボタン      │
└─────────────────────────────────────────────────────┘
```

## コーディング規約
- 日本語コメントを適宜追加
- 関数にはdocstringを記載
- エラーハンドリングを適切に実装
- Streamlitのセッション状態（st.session_state）を活用

## 主要な実装パターン

### データ読み込み
```python
def load_data(uploaded_file):
    """CSV/Excelファイルを読み込んでDataFrameを返す"""
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)
```

### セッション状態管理
```python
if 'model' not in st.session_state:
    st.session_state.model = None
if 'trained' not in st.session_state:
    st.session_state.trained = False
```

### LightGBMモデル
```python
import lightgbm as lgb
model = lgb.LGBMRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)
model.fit(X_train, y_train)
```

### SHAP解析
```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

## 注意事項
- 大規模データの場合はSHAP計算でサンプリングを行う（最大1000行）
- カテゴリ変数はLabelEncodingで数値化
- ファイルアップロードのサイズ制限に注意（デフォルト200MB）
