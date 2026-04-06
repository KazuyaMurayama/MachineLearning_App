# リポジトリ ファイルインデックス

> 作成日: 2026-04-06
> ブランチ: claude/integrate-business-plan-IBKFu（109ファイル）、origin/main（31ファイル）

## 使い方

ファイル参照が必要な場合、まずこのインデックスを参照して該当ファイルを特定してください。

---

## 1. Streamlitアプリ本体

### 1-1. ルートレベル・ポータルアプリ

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `app.py` | 機械学習予測アプリ本体。LightGBM + SHAP による回帰予測 | 466 | 両方 |
| `streamlit_app.py` | 士業向け AI経営パートナー。税理士・社労士・行政書士向け9アプリの統合ポータル | 216 | branch |
| `ec_app.py` | EC向け AI経営パートナー。EC事業者向け3アプリの統合ポータル | 213 | branch |

### 1-2. 士業向けアプリ（`apps/` 配下）

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `apps/shigyou-demo/app.py` | 士業向け顧問先離反予測デモ。LightGBM + SHAP + 逆SHAPで離反リスク評価・改善提案 | 851 | branch |
| `apps/crosssell/app.py` | 顧問先クロスセル分析ツール。未利用サービス推奨と推定増収額を算出 | 610 | branch |
| `apps/payment-alert/app.py` | 請求・入金遅延アラートツール。顧問先の入金遅延を可視化し催促テンプレートを生成 | 567 | branch |
| `apps/report-gen/app.py` | 月次レポート自動生成ツール。freee/MF CSV試算表から前月比・前年同月比・異常値を検知しレポート生成 | 671 | branch |
| `apps/compliance-pack/app.py` | 士業向け安心パッケージ（コンプライアンス対応テンプレート集）。守秘義務契約・データ取扱い規程・AI処理同意書のプレビュー＋ダウンロード | 427 | branch |
| `apps/contract-draft/app.py` | 契約書ドラフトAI。税理士・社労士・行政書士向け契約書テンプレート自動生成ツール | 510 | branch |
| `apps/doc-checker/app.py` | 申請書類チェッカー。建設業許可・飲食店営業許可・就業規則・社保届など書類準備状況チェック | 697 | branch |
| `apps/service-lp/app.py` | 統合サービスLP＋AI経営診断ツール。サービス紹介LP + 10問診断でAI活用成熟度評価・推奨サービス提案 | 446 | branch |

### 1-3. EC向けアプリ（`apps/` 配下）

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `apps/ec-demo/app.py` | EC向け顧客離脱予測＋需要予測デモ。LightGBM分類（離脱）+ LightGBM回帰（需要）+ SHAP + 逆SHAP | 496 | branch |
| `apps/ec-dashboard/app.py` | EC売上ダッシュボード。日別売上・カテゴリ別集計・前年比・異常値検知 | 811 | branch |
| `apps/ec-rfm/app.py` | 顧客RFM分析＋セグメンテーション。購買履歴からRFMスコア計算・セグメントマップ・施策提案 | 749 | branch |
| `apps/ec-ad-roi/app.py` | 広告ROI分析ツール。チャネル別ROAS分析・予算配分シミュレーション・トレンド分析 | 817 | branch |

---

## 2. サンプルデータ生成スクリプト

### 2-1. ルートレベル

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `create_sample_data.py` | テスト用の教師データとターゲットデータを生成（単一ビジネスケース用） | 107 | 両方 |
| `create_sample_data_all.py` | 複数ビジネス事例（年収・不動産・日次売上・LTV・離職リスク）のサンプルデータを一括生成 | 380 | 両方 |

### 2-2. アプリ別（`apps/*/create_sample_data.py`）

| ファイル | 概要 | ブランチ |
|---------|------|:--------:|
| `apps/shigyou-demo/create_sample_data.py` | 士業向けサンプルデータ生成。顧問先の契約・連絡・入金状況等データを生成 | branch |
| `apps/crosssell/create_sample_data.py` | クロスセル分析サンプルデータ生成。150顧問先 × サービス利用マトリクス | branch |
| `apps/payment-alert/create_sample_data.py` | サンプルデータ生成。150顧問先 × 12ヶ月の請求・入金データ（遅延パターン付き） | branch |
| `apps/report-gen/create_sample_data.py` | 月次レポート用サンプルCSV生成。freee/MF試算表エクスポートを模した月次財務データ | branch |
| `apps/ec-demo/create_sample_data.py` | EC向けサンプルデータ生成。顧客離脱・需要予測用の特徴量データ | branch |
| `apps/ec-dashboard/create_sample_data.py` | 売上ダッシュボード用サンプルデータ生成。2年分の日別売上データ（2023〜2024） | branch |
| `apps/ec-rfm/create_sample_data.py` | RFM分析サンプルデータ生成。500顧客 × 購買履歴（過去2年分） | branch |
| `apps/ec-ad-roi/create_sample_data.py` | 広告ROI分析サンプルデータ生成。12ヶ月 × 5チャネルの広告データ | branch |

---

## 3. サンプルデータ CSV

### 3-1. ルートレベル `sample_data/`

5種類のビジネスケース各2ファイル（train/target）+ 汎用2ファイルの計12ファイル（main・branch共通）。

| ファイル | 列概要 | ブランチ |
|---------|------|:--------:|
| `sample_data/train.csv` / `target.csv` | 年齢・経験年数・学歴・部署・残業時間・プロジェクト数（targetなし/年収あり） | 両方 |
| `sample_data/1_salary_train.csv` / `1_salary_target.csv` | 年収予測用（年齢・経験年数・学歴・役職・資格数 etc） | 両方 |
| `sample_data/2_realestate_train.csv` / `2_realestate_target.csv` | 不動産価格予測用（専有面積・築年数・階数・駅徒歩分 etc） | 両方 |
| `sample_data/3_sales_train.csv` / `3_sales_target.csv` | 日次売上予測用（来店客数・客単価・立地・天気 etc） | 両方 |
| `sample_data/4_ltv_train.csv` / `4_ltv_target.csv` | LTV予測用（年齢・購入回数・会員歴・メール開封率 etc） | 両方 |
| `sample_data/5_turnover_train.csv` / `5_turnover_target.csv` | 離職リスクスコア予測用（勤続年数・月給・残業時間・評価スコア etc） | 両方 |

### 3-2. アプリ別 `apps/*/sample_data/`

| ファイル | 列概要 | ブランチ |
|---------|------|:--------:|
| `apps/shigyou-demo/sample_data/shigyou_train.csv` / `shigyou_target.csv` | 顧問先離反予測用（契約年数・顧問料・連絡頻度・入金遅延回数・解約予測月数 etc） | branch |
| `apps/crosssell/sample_data/crosssell_data.csv` | 顧問先クロスセル用（顧問先ID・業種・サービス利用マトリクス etc） | branch |
| `apps/payment-alert/sample_data/payment_data.csv` | 入金遅延アラート用（顧問先ID・月額顧問料・請求日・入金日・遅延日数 etc） | branch |
| `apps/report-gen/sample_data/trial_balance_current.csv` / `trial_balance_prev.csv` | 月次試算表（売上高・売上原価・人件費・各経費・営業利益 etc） | branch |
| `apps/ec-demo/sample_data/ec_customers_train.csv` / `ec_customers_target.csv` | EC顧客離脱予測用（購入回数・累計購入金額・ログイン頻度・離脱フラグ etc） | branch |
| `apps/ec-demo/sample_data/ec_sales_train.csv` / `ec_sales_target.csv` | EC需要予測用（SKU・単価・割引率・広告費・販売数量 etc） | branch |
| `apps/ec-dashboard/sample_data/daily_sales.csv` | EC日別売上（日付・カテゴリ・売上金額・注文件数・客単価） | branch |
| `apps/ec-rfm/sample_data/purchase_history.csv` | 購買履歴RFM用（顧客ID・顧客名・注文日・注文金額・商品カテゴリ） | branch |
| `apps/ec-ad-roi/sample_data/ad_performance.csv` | 広告ROI用（月・チャネル・広告費・インプレッション・CV数・ROAS・CPA etc） | branch |

---

## 4. 共通モジュール

### 4-1. `modules/`（ルートレベル、main・branch共通）

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `modules/__init__.py` | 機械学習予測アプリのモジュールパッケージ初期化 | 10 | 両方 |
| `modules/data_loader.py` | データ読み込みモジュール。CSV/Excelファイルの読み込みと前処理 | 100 | 両方 |
| `modules/evaluation.py` | 評価指標モジュール。モデルの評価指標（RMSE, MAE, R²等）を算出 | 92 | 両方 |
| `modules/model.py` | モデル処理モジュール。LightGBMモデルの学習・予測 | 216 | 両方 |
| `modules/shap_analysis.py` | SHAP解析モジュール。SHAPによるモデル解釈・可視化 | 355 | 両方 |

### 4-2. `apps/common/`（branch のみ）

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `apps/common/__init__.py` | appsパッケージ共通モジュール初期化 | — | branch |
| `apps/common/reverse_shap.py` | 逆SHAPエンジン。「Why（要因説明）」ではなく「How（改善提案）」を提示するSHAP応用モジュール | 245 | branch |

---

## 5. 設定ファイル

各アプリには共通で以下の設定ファイルが存在します（branch のみのアプリにはbranch、両方のものは両方）。

| ファイルパターン | 概要 | ブランチ |
|----------------|------|:--------:|
| `.streamlit/config.toml`（ルート） | Streamlit全体設定（テーマ・ポート等） | 両方 |
| `apps/*/.streamlit/config.toml` | 各アプリ個別のStreamlit設定（11アプリ分） | branch |
| `requirements.txt`（ルート） | ルートアプリの依存パッケージ定義 | 両方 |
| `apps/*/requirements.txt` | 各アプリの依存パッケージ定義（11アプリ分） | branch |
| `packages.txt`（ルート） | Streamlit Cloud用システムパッケージ（日本語フォント等） | 両方 |
| `apps/*/packages.txt` | 各アプリ用システムパッケージ（11アプリ分） | branch |
| `.python-version` | Pythonバージョン指定（pyenv用） | 両方 |

---

## 6. ドキュメント

| ファイル | 概要 | 行数 | ブランチ |
|---------|------|:---:|:--------:|
| `README.md` | プロジェクト概要・セットアップ手順・使い方説明 | 125 | 両方 |
| `CLAUDE.md` | Claude Code プロジェクトガイド。開発規約・ディレクトリ構成・MVPパターン説明 | 159 | 両方 |
| `ISSUES.md` | 開発Issue一覧・進捗管理表 | 428 | 両方 |
| `docs/improvement-backlog.md` | 全アプリ改善候補バックログ（品質チェック結果ベース） | 119 | branch |
| `docs/file-index.md` | 本ファイル。リポジトリ全ファイルのインデックス | — | branch |

---

## 7. カスタムコマンド（`.claude/commands/`）

Claude Code 用カスタムスキルコマンド（branch のみ）。

| ファイル | 概要 | ブランチ |
|---------|------|:--------:|
| `.claude/commands/mvp-plan.md` | MVP企画・優先順位付けスキル。士業・EC事業者向けMVPアプリ候補整理と優先順位付け | branch |
| `.claude/commands/mvp-build.md` | MVP実装スキル。確立されたパターンに従ってMVPを実装 | branch |
| `.claude/commands/mvp-quality.md` | MVP品質チェックスキル。5軸100点でアプリ品質採点・改善計画策定 | branch |
| `.claude/commands/mvp-improve.md` | MVP改善実行スキル。品質チェック結果に基づき4エージェント並列起動で改善実行 | branch |

---

## 8. その他

| ファイル | 概要 | ブランチ |
|---------|------|:--------:|
| `.gitignore` | Git管理除外設定 | 両方 |
| `.claude/settings.local.json` | Claude Code ローカル設定ファイル | 両方 |
| `start_app.bat` | Windows用アプリ起動バッチスクリプト | 両方 |
| `setup_fonts.py` | Streamlit Cloud環境で日本語フォントをセットアップするスクリプト（38行） | 両方 |

---

## ブランチ別ファイル分類サマリー

| 分類 | main のみ | 両方 | branch のみ |
|-----|:---------:|:----:|:-----------:|
| Streamlitアプリ本体 | — | 1（`app.py`） | 14 |
| サンプルデータ生成 | — | 2 | 8 |
| サンプルデータ CSV | — | 12 | 13 |
| 共通モジュール | — | 5 | 2 |
| 設定ファイル | — | 複数 | 複数 |
| ドキュメント | — | 4 | 2 |
| カスタムコマンド | — | — | 4 |
| その他 | — | 4 | — |

> main のみに存在するファイルはなし（main の全31ファイルは branch にも含まれる）
