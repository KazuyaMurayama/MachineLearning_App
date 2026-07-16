# MachineLearning_App — 士業・EC事業者向けAIツール群（18アプリ）

Streamlitで構築した18本のAI/機械学習アプリのポートフォリオです。士業（税理士・社労士・行政書士）向け11本、EC事業者向け7本を、それぞれ専用ポータルから提供します。

> ⚠️ 本README は実装の現状を記載したものです。事業進捗（パイロット実績・GTM状況等）は `tasks.md` を単一の真実（SSOT）として参照してください。

## 全体構成

本リポジトリは以下の3層で構成されています。

1. **ポータル**（`streamlit_app.py` / `ec_app.py`）— 士業向け・EC向けそれぞれの入口。ユーザーは各業界ポータルからアプリを選択して利用します。
2. **業務アプリ**（`apps/` 配下18ディレクトリ）— 個別のStreamlitアプリ本体。
3. **単独MLアプリ**（`app.py`）— 本プロジェクト初期スコープの汎用LightGBM回帰予測アプリ（ポータルには含まれない独立アプリ）。

```
.
├── app.py                  # 単独MLアプリ（初期スコープ・汎用LightGBM回帰予測）
├── ec_app.py                # ECポータル（apps/ec-* 配下アプリのランチャー）
├── streamlit_app.py         # 士業ポータル（apps/shigyou-* 等配下アプリのランチャー）
├── apps/                    # 18業務アプリ本体
│   └── common/              # 士業・EC共通ライブラリ（逆SHAPエンジン等）
├── modules/                  # app.py（単独MLアプリ）専用モジュール
├── sample_data/              # app.py用サンプルデータ
├── docs/                     # 設計ドキュメント・ルール・分析資料
├── scripts/smoke_test.py     # 全アプリ一括スモークテスト
├── create_sample_data.py     # app.py用サンプルデータ生成
├── create_sample_data_all.py # 複数ユースケース分のサンプルデータ生成
├── generate_docs_html.py     # docs/配下MDをHTML化（ブラウザ閲覧用）
├── setup_fonts.py            # Streamlit Cloud環境の日本語フォントセットアップ
└── requirements.txt
```

## apps/ 配下 18アプリ一覧

### 士業向け（税理士・社労士・行政書士）

| ディレクトリ | アプリ名 | 概要 |
|---|---|---|
| `shigyou-demo` | 顧問先離反予測デモ | LightGBM＋SHAP＋逆SHAPで顧問先の離反リスクをスコアリングし、改善提案を提示 |
| `shigyou-ltv` | 顧問先LTV予測＋不採算フラグ | crosssell × shigyou-demo を結合し、5年間のLTV予測とクラスタ分類で収益性を可視化 |
| `shigyou-office-dashboard` | 事務所経営ダッシュボード（L3コア） | 8アプリのデータを1画面に集約した事務所経営者向け統合ビュー |
| `shigyou-briefing` | 月次AIブリーフィングレポート（L3コア） | 月次経営会議用レポートを自動生成 |
| `crosssell` | 顧問先クロスセル分析 | 顧問先のサービス利用状況から未利用サービスを推奨し、推定増収額を算出 |
| `payment-alert` | 請求・入金遅延アラート | 顧問先の入金遅延を可視化し、催促テンプレートを生成 |
| `report-gen` | 月次レポート自動生成 | freee/MFのCSV試算表から前月比・前年同月比・異常値を検知し月次レポートを自動生成 |
| `contract-draft` | 契約書ドラフトAI | 事務所情報の入力だけで業種別の契約書ドラフトを自動生成 |
| `compliance-pack` | 士業向け安心パッケージ | 守秘義務契約・データ取扱い規程・AI処理同意書の3点セットをプレビュー＋ダウンロード |
| `doc-checker` | 申請書類チェッカー | 建設業許可・飲食店営業許可・就業規則届出・社保新規適用届の書類不備を即座に特定 |
| `service-lp` | 統合サービスLP＋AI経営診断 | サービス紹介LPと10問診断でAI活用成熟度を評価し推奨サービス層を提案 |

### EC事業者向け

| ディレクトリ | アプリ名 | 概要 |
|---|---|---|
| `ec-demo` | 顧客離脱予測＋需要予測デモ | LightGBM分類（離脱）＋回帰（需要）＋SHAP＋逆SHAP |
| `ec-executive-dashboard` | EC経営ダッシュボード（L3コア） | 売上・広告・顧客・在庫を1画面に集約したEC経営者向け統合ビュー |
| `ec-monthly-briefing` | EC月次AIブリーフィングレポート（L3コア） | 月次経営会議用レポートを自動生成 |
| `ec-what-if` | What-Ifシミュレーター（L3コア） | 逆SHAP What-If：LightGBM予測＋SHAP解釈＋インタラクティブ入力シミュレーション |
| `ec-ad-roi` | 広告ROI分析 | チャネル別ROAS分析・予算配分シミュレーション・トレンド分析（LightGBM+SHAP） |
| `ec-dashboard` | EC売上ダッシュボード | 売上関連指標の可視化ダッシュボード |
| `ec-rfm` | 顧客RFM分析 | 購買履歴に基づくRFM分析による顧客セグメンテーション |

### 共通

| ディレクトリ | 概要 |
|---|---|
| `common` | 士業・EC共通の逆SHAPエンジン（`reverse_shap.py`）。通常のSHAPが「なぜこの予測か」を説明するのに対し、逆SHAPは「何を変えれば改善できるか」を提案する |

> 各アプリの詳細な設計判断・重要度分類・統合方針は `docs/app-portfolio-analysis.md` を参照してください。

## セットアップ・起動方法

### 前提

- Python 3.11（`.python-version` 指定）

### 依存関係のインストール

```bash
# ルート（app.py用）
pip install -r requirements.txt

# 各業務アプリ（apps/<アプリ名>/requirements.txt が存在する場合）
pip install -r apps/<アプリ名>/requirements.txt
```

### ポータルの起動

```bash
# 士業ポータル（apps/shigyou-* 系アプリのランチャー）
streamlit run streamlit_app.py

# ECポータル（apps/ec-* 系アプリのランチャー）
streamlit run ec_app.py
```

### 個別業務アプリの起動

```bash
streamlit run apps/<アプリ名>/app.py
# 例:
streamlit run apps/shigyou-demo/app.py
streamlit run apps/ec-what-if/app.py
```

### 単独MLアプリの起動（初期スコープの汎用回帰予測アプリ）

```bash
streamlit run app.py
```

`http://localhost:8501` がブラウザで自動的に開きます。LightGBMベースの回帰予測（データアップロード→モデル学習→SHAP解析→予測出力）を単体で試せます。対応データ形式はCSV/Excel。サンプルデータは以下で生成できます。

```bash
python create_sample_data_all.py
```

### スモークテスト（全アプリ一括健全性チェック）

```bash
python scripts/smoke_test.py
# JSON出力
python scripts/smoke_test.py --json
```

構文チェック（`ast.parse`）・サンプルデータ生成可否・必須ファイル存在・import健全性を一括検証します。

### ドキュメントHTML化

```bash
python generate_docs_html.py
```

`docs/index.html` が生成され、ブラウザで `docs/` 配下の全Markdownドキュメントを閲覧できます。

## 本番デプロイ

士業・EC双方の主要アプリはStreamlit Cloud上で個別URLで稼働中です。稼働URL一覧は `tasks.md` の「デプロイ済みアプリURL」を参照してください（本READMEでは重複記載しません。URLは運用状況により変わるため `tasks.md` を正とします）。

## 技術スタック

- **Frontend**: Streamlit
- **ML**: LightGBM, scikit-learn
- **Explainability**: SHAP（＋独自の逆SHAPエンジン `apps/common/reverse_shap.py`）
- **Data**: pandas, numpy
- **可視化**: matplotlib（日本語フォント対応）

## ドキュメント案内

| ファイル | 役割 |
|---|---|
| `tasks.md` | 進捗管理のSSOT（事業進捗・デプロイURL・既知のリスク・撤退基準） |
| `CLAUDE.md` | 開発ルール・Claude Code設定 |
| `FILE_INDEX.md` | 全ファイルインデックス |
| `ISSUES.md` | 初期スコープ（単独MLアプリ `app.py`）開発時のIssue記録（アーカイブ済み、履歴として保持） |
| `progress.md` | 長時間タスクの中断・再開用チェックポイント（アーカイブ済み、履歴として保持） |
| `docs/app-portfolio-analysis.md` | 18アプリの重要度分類・統合方針の分析 |
| `Timeout_Prevention.md` | Claude Code実行時のタイムアウト対策ガイド |

## ライセンス

MIT License
