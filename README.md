# 機械学習予測アプリ (ML Prediction App)

Streamlitを使用したLightGBMベースの回帰予測アプリケーションです。

## 🎯 機能

- **データ入力**: CSV/Excelファイルのアップロード
- **変数設定**: 目的変数の選択と特徴量の自動設定
- **モデル学習**: LightGBMによる回帰モデルの構築
- **評価指標**: MAE, RMSE, R²の表示
- **SHAP解析**: 特徴量重要度の可視化
- **予測出力**: 予測結果の表示とCSVダウンロード

## 🚀 セットアップ

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd ml-prediction-app
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. アプリの起動
```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 📖 使い方

1. **教師データをアップロード**: サイドバーから訓練用データ（CSV/Excel）をアップロード
2. **目的変数を選択**: ドロップダウンから予測したい変数を選択
3. **学習実行**: 「モデル学習」ボタンをクリック
4. **結果確認**: 評価指標とSHAP可視化を確認
5. **予測実行**: ターゲットデータをアップロードして予測
6. **ダウンロード**: 予測結果をCSVでダウンロード

## 📁 ディレクトリ構成

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
├── CLAUDE.md              # Claude Code設定
├── ISSUES.md              # 開発Issue一覧
└── README.md              # このファイル
```

## 🛠 技術スタック

- **Frontend**: Streamlit
- **ML**: LightGBM, scikit-learn
- **Explainability**: SHAP
- **Data**: pandas, numpy

## 📊 対応データ形式

- CSV (.csv)
- Excel (.xlsx, .xls)

## 📚 サンプルデータ

複数のビジネスユースケースのサンプルデータを用意しています：

### 1. 年収予測（従業員）
- **ファイル**: `sample_data/1_salary_train.csv`, `1_salary_target.csv`
- **目的変数**: 年収（万円）
- **特徴量**: 年齢、経験年数、学歴、部署、役職、残業時間など
- **用途**: 人事評価、給与査定

### 2. 不動産価格予測（マンション）
- **ファイル**: `sample_data/2_realestate_train.csv`, `2_realestate_target.csv`
- **目的変数**: 価格（万円）
- **特徴量**: 専有面積、築年数、階数、駅徒歩分、部屋数、向きなど
- **用途**: 不動産価格査定、物件評価

### 3. 売上予測（店舗）
- **ファイル**: `sample_data/3_sales_train.csv`, `3_sales_target.csv`
- **目的変数**: 日次売上（万円）
- **特徴量**: 来店客数、平均客単価、従業員数、キャンペーン実施、天気など
- **用途**: 売上予測、需要予測

### 4. 顧客生涯価値（LTV）予測
- **ファイル**: `sample_data/4_ltv_train.csv`, `4_ltv_target.csv`
- **目的変数**: LTV（万円）
- **特徴量**: 購入回数、平均購入単価、会員歴、メール開封率、会員ランクなど
- **用途**: 顧客分析、マーケティング最適化

### 5. 離職リスクスコア予測
- **ファイル**: `sample_data/5_turnover_train.csv`, `5_turnover_target.csv`
- **目的変数**: 離職リスクスコア（0-100）
- **特徴量**: 勤続年数、月給、残業時間、有給消化率、評価スコアなど
- **用途**: 人材リテンション、離職防止

### サンプルデータの生成方法
```bash
python create_sample_data_all.py
```

## ⚠️ 注意事項

- 欠損値は自動的に処理されません。事前にデータをクリーニングしてください。
- カテゴリ変数は自動的にLabel Encodingされます。
- 大規模データ（10万行以上）の場合、SHAP計算に時間がかかる場合があります。

## 📝 ライセンス

MIT License
