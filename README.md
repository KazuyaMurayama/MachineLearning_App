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

## ⚠️ 注意事項

- 欠損値は自動的に処理されません。事前にデータをクリーニングしてください。
- カテゴリ変数は自動的にLabel Encodingされます。
- 大規模データ（10万行以上）の場合、SHAP計算に時間がかかる場合があります。

## 📝 ライセンス

MIT License
