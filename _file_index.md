# ファイルインデックス — machinelearning_app リポジトリ

**最終更新:** 2026年4月8日  
**用途:** 作業開始時にまず参照し、必要なファイルをブランチをまたいで素早く特定するためのナビゲーション一覧

> **使い方:** 作業前にこのファイルを参照し、目的に合うファイルのブランチ・パスを確認してください。
> 詳細なファイル一覧（全アプリ・全モジュール）は **`docs/file-index.md`** を参照してください（`claude/integrate-business-plan-IBKFu` ブランチ以降に存在）。

---

## ブランチ一覧と役割

| ブランチ名 | 役割・作成目的 |
|---|---|
| `main` | ベースの機械学習予測アプリ（LightGBM + SHAP）。31ファイル |
| `claude/review-feasibility-scoring-OZKMQ` | 実現可能性スコアリング評価・改善 |
| `claude/add-screen-explanations-LSYOf` | 各画面への説明文追加・UX改善 |
| `claude/refine-thinking-steps-v3s8C` | 思考ステップの精緻化（v3） |
| `claude/integrate-business-plan-IBKFu` | **士業・EC向け複数アプリ統合**（109ファイル）★最多コンテンツ |
| `claude/check-repo-file-lists-desRY` | **現在の作業ブランチ**（このインデックスファイルを含む） |

---

## 主要ファイル概要（全ブランチ共通）

| ファイル名 | 種別 | 概要 |
|---|:---:|---|
| `CLAUDE.md` | MD | Claude Code プロジェクトガイド。ディレクトリ構成・開発コマンド・Issue一覧・コーディング規約 |
| `README.md` | MD | プロジェクト概要・セットアップ手順・使い方説明 |
| `ISSUES.md` | MD | 開発Issue一覧と進捗管理表（Issue #1〜#8） |
| `app.py` | Python | **機械学習予測アプリ本体**（LightGBM + SHAP 回帰予測、Streamlit UI） |
| `modules/data_loader.py` | Python | データ読み込みモジュール（CSV/Excel対応） |
| `modules/model.py` | Python | LightGBMモデルの学習・予測 |
| `modules/evaluation.py` | Python | 評価指標（RMSE・MAE・R²）算出 |
| `modules/shap_analysis.py` | Python | SHAP解析・可視化モジュール |
| `create_sample_data.py` | Python | テスト用サンプルデータ生成（単一ケース） |
| `create_sample_data_all.py` | Python | 5種類のビジネスケース一括サンプルデータ生成 |
| `requirements.txt` | Text | 依存パッケージ（LightGBM・SHAP・Streamlit等） |

---

## 拡張ファイル（`claude/integrate-business-plan-IBKFu` ブランチ以降）

### ポータルアプリ

| ファイル名 | 種別 | 概要 |
|---|:---:|---|
| `streamlit_app.py` | Python | 士業向け AI経営パートナー統合ポータル（9アプリ） |
| `ec_app.py` | Python | EC向け AI経営パートナー統合ポータル（3アプリ） |

### 士業向けアプリ（`apps/` 配下）

| ディレクトリ | 概要 |
|---|---|
| `apps/shigyou-demo/` | 顧問先離反予測デモ（LightGBM + 逆SHAP） |
| `apps/crosssell/` | 顧問先クロスセル分析 |
| `apps/payment-alert/` | 請求・入金遅延アラート |
| `apps/report-gen/` | 月次レポート自動生成（freee/MF CSV対応） |
| `apps/compliance-pack/` | コンプライアンス対応テンプレート集 |
| `apps/contract-draft/` | 契約書ドラフトAI |
| `apps/doc-checker/` | 申請書類チェッカー |
| `apps/service-lp/` | サービスLP + AI経営診断ツール |
| `apps/shigyou-briefing/` | 士業向けブリーフィング |
| `apps/shigyou-demo/` | 士業向けデモアプリ |
| `apps/shigyou-ltv/` | 士業向けLTV分析 |
| `apps/shigyou-office-dashboard/` | 士業事務所ダッシュボード |

### EC向けアプリ（`apps/` 配下）

| ディレクトリ | 概要 |
|---|---|
| `apps/ec-demo/` | 顧客離脱予測 + 需要予測デモ |
| `apps/ec-dashboard/` | EC売上ダッシュボード |
| `apps/ec-rfm/` | 顧客RFM分析・セグメンテーション |
| `apps/ec-ad-roi/` | 広告ROI分析ツール |
| `apps/ec-executive-dashboard/` | EC経営者向けダッシュボード |
| `apps/ec-monthly-briefing/` | EC月次ブリーフィング |
| `apps/ec-what-if/` | What-If シミュレーター |

### ドキュメント（`docs/` 配下）

| ファイル名 | 種別 | 概要 |
|---|:---:|---|
| `docs/file-index.md` | MD | **詳細ファイルインデックス**（全109ファイルの行数・概要・ブランチ分類） |
| `docs/improvement-backlog.md` | MD | 全アプリ改善候補バックログ |
| `docs/ec-business-alignment.md` | MD | EC事業者向けビジネスアライメント戦略 |
| `docs/shigyou-business-alignment.md` | MD | 士業向けビジネスアライメント戦略 |

### カスタムコマンド（`.claude/commands/`）

| ファイル名 | 概要 |
|---|---|
| `mvp-plan.md` | MVP企画・優先順位付けスキル |
| `mvp-build.md` | MVP実装スキル（確立パターンに従い実装） |
| `mvp-quality.md` | MVP品質チェック（5軸100点採点） |
| `mvp-improve.md` | MVP改善実行（4エージェント並列） |

---

## 目的別クイックリファレンス

| やりたいこと | 参照ファイル | ブランチ |
|---|---|---|
| プロジェクト概要・起動方法を確認する | `README.md` | 全ブランチ |
| 開発ルール・ディレクトリ構成を確認する | `CLAUDE.md` | 全ブランチ |
| 残りのIssue・開発進捗を確認する | `ISSUES.md` | 全ブランチ |
| 機械学習予測アプリ本体を確認する | `app.py` | 全ブランチ |
| 全ファイルの詳細一覧を確認する | `docs/file-index.md` | `integrate-business-plan-IBKFu` |
| 士業向け統合ポータルを確認する | `streamlit_app.py` | `integrate-business-plan-IBKFu` |
| EC向け統合ポータルを確認する | `ec_app.py` | `integrate-business-plan-IBKFu` |
| 改善バックログを確認する | `docs/improvement-backlog.md` | `integrate-business-plan-IBKFu` |
| MVPの企画〜実装〜品質チェックをする | `.claude/commands/mvp-*.md` | `integrate-business-plan-IBKFu` |
| 逆SHAP（改善提案）ロジックを確認する | `apps/common/reverse_shap.py` | `integrate-business-plan-IBKFu` |
