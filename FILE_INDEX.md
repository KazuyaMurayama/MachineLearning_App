# FILE_INDEX — MachineLearning_App

> ⚠️ このファイルは自動生成です。手動編集は次回更新で上書きされます。
> `apps/` 配下18アプリはディレクトリ単位で集約記載しています（各アプリの個別ファイル一覧は下記「apps/ 配下サマリー」参照）。

| 項目 | 値 |
|---|---|
| リポジトリ | KazuyaMurayama/MachineLearning_App |
| ブランチ | main |
| 総ファイル数 | 237 |
| 最終更新 | 2026-07-16 |
| 管理者 | 男座員也（Kazuya Oza） |

---

## カテゴリ別サマリー

| カテゴリ | ファイル数 |
|---|---|
| Documentation | 71件 |
| Code | 18件 |
| Data | 16件 |
| Config | 7件 |
| Other | 2件 |
| apps/ 配下（18アプリ集約） | 123件 |
| **合計** | **237件** |

---

## ディレクトリ構成

```
.
├── .claude/
│   ├── commands/
│   │   ├── mvp-build.md
│   │   ├── mvp-improve.md
│   │   ├── mvp-plan.md
│   │   └── mvp-quality.md
│   ├── hooks/
│   │   ├── md_table_check.py
│   │   ├── post_bash_guard.py
│   │   ├── pre_md_table_guard.py
│   │   ├── pre_write_guard.py
│   │   └── session_guard.py
│   ├── skills/
│   │   ├── branch-cleanup/
│   │   │   └── SKILL.md
│   │   ├── mermaid-agents365/
│   │   │   ├── reference/
│   │   │   │   ├── CLASS-ER.md
│   │   │   │   ├── FLOWCHART.md
│   │   │   │   ├── OTHER-TYPES.md
│   │   │   │   └── SEQUENCE.md
│   │   │   └── SKILL.md
│   │   ├── sp-brainstorming/
│   │   │   └── SKILL.md
│   │   ├── sp-executing-plans/
│   │   │   └── SKILL.md
│   │   ├── sp-verification-before-completion/
│   │   │   └── SKILL.md
│   │   └── sp-writing-plans/
│   │       └── SKILL.md
│   ├── cross-repo.md
│   ├── quality-rules.md
│   ├── settings.json
│   ├── settings.local.json
│   └── visual-rules.md
├── .github/
│   └── workflows/
│       ├── md-table-lint.yml
│       └── patch-ec-what-if.yml
├── .streamlit/
│   └── config.toml
├── apps/
│   ├── common/  ... (2 items)
│   ├── compliance-pack/  ... (4 items)
│   ├── contract-draft/  ... (4 items)
│   ├── crosssell/  ... (6 items)
│   ├── doc-checker/  ... (4 items)
│   ├── ec-ad-roi/  ... (6 items)
│   ├── ec-dashboard/  ... (6 items)
│   ├── ec-demo/  ... (9 items)
│   ├── ec-executive-dashboard/  ... (11 items)
│   ├── ec-monthly-briefing/  ... (10 items)
│   ├── ec-rfm/  ... (6 items)
│   ├── ec-what-if/  ... (11 items)
│   ├── payment-alert/  ... (6 items)
│   ├── report-gen/  ... (7 items)
│   ├── service-lp/  ... (4 items)
│   ├── shigyou-briefing/  ... (7 items)
│   ├── shigyou-demo/  ... (7 items)
│   ├── shigyou-ltv/  ... (6 items)
│   └── shigyou-office-dashboard/  ... (7 items)
├── docs/
│   ├── rules/
│   │   ├── 01-response-rules.md
│   │   ├── 02-task-management.md
│   │   ├── 03-file-index-rules.md
│   │   ├── 04-git-rules.md
│   │   ├── 05-model-usage.md
│   │   ├── 06-deliverable-rules.md
│   │   ├── 07-execution-timeout.md
│   │   └── 08-ec-app-roles.md
│   ├── sales-assets/
│   │   ├── _workspace/
│   │   │   └── state.json
│   │   ├── README.md
│   │   ├── customer-pain-research.md
│   │   ├── demo-script-15min.md
│   │   ├── demo-tech-checklist.md
│   │   ├── lead-list-framework.md
│   │   ├── objection-handling.md
│   │   ├── outreach-email-templates.md
│   │   ├── pilot-contract-template.md
│   │   ├── pilot-proposal-template.md
│   │   ├── pricing-and-scope.md
│   │   ├── prospect-research-template.md
│   │   ├── ringi-summary-template.md
│   │   └── roi-calculator.md
│   ├── sessions/
│   │   ├── 2026-04-08-session-summary.md
│   │   └── 2026-04-30-session-summary.md
│   ├── task-improvement/
│   │   ├── 00-master-plan.md
│   │   ├── 01-critical-thinking.md
│   │   ├── 02-logical-analysis.md
│   │   ├── 03-business-strategy.md
│   │   ├── 04-ux-quality.md
│   │   ├── 05-tech-review.md
│   │   ├── 06-synthesis.md
│   │   ├── 07-action-plan.md
│   │   ├── 08-execution-log.md
│   │   ├── 09-final-report.md
│   │   └── smoke-test-result.json
│   ├── app-portfolio-analysis.md
│   ├── context-handoff.md
│   ├── ec-business-alignment.md
│   ├── file-index.md
│   ├── improvement-backlog.md
│   ├── index.html
│   ├── quality-scoring-rubric.md
│   ├── shigyou-business-alignment.md
│   ├── step1_usecase_catalog.md
│   ├── step2_monetization_scoring.md
│   ├── step3_prioritization.md
│   ├── step4_marketing_strategy.md
│   ├── step5_strategy_review.md
│   ├── step6_revised_strategy.md
│   └── step7_second_review.md
├── modules/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── evaluation.py
│   ├── model.py
│   └── shap_analysis.py
├── sample_data/
│   ├── 1_salary_target.csv
│   ├── 1_salary_train.csv
│   ├── 2_realestate_target.csv
│   ├── 2_realestate_train.csv
│   ├── 3_sales_target.csv
│   ├── 3_sales_train.csv
│   ├── 4_ltv_target.csv
│   ├── 4_ltv_train.csv
│   ├── 5_turnover_target.csv
│   ├── 5_turnover_train.csv
│   ├── target.csv
│   └── train.csv
├── scripts/
│   └── smoke_test.py
├── .gitignore
├── .python-version
├── CLAUDE.md
├── FILE_INDEX.md
├── ISSUES.md
├── README.md
├── Timeout_Prevention.md
├── app.py
├── create_sample_data.py
├── create_sample_data_all.py
├── ec_app.py
├── generate_docs_html.py
├── packages.txt
├── progress.md
├── requirements.txt
├── setup_fonts.py
├── start_app.bat
├── streamlit_app.py
└── tasks.md
```

---

## apps/ 配下サマリー（18アプリ・計123件）

| アプリ | ファイル数 | 概要 |
|---|---|---|
| `apps/common/` | 2件 | 共通ライブラリ（逆SHAPエンジン） |
| `apps/compliance-pack/` | 4件 | 士業向け安心パッケージ |
| `apps/contract-draft/` | 4件 | 契約書ドラフトAI |
| `apps/crosssell/` | 6件 | 顧問先クロスセル分析 |
| `apps/doc-checker/` | 4件 | 申請書類チェッカー |
| `apps/ec-ad-roi/` | 6件 | 広告ROI分析 |
| `apps/ec-dashboard/` | 6件 | EC売上ダッシュボード |
| `apps/ec-demo/` | 9件 | 顧客離脱予測＋需要予測デモ |
| `apps/ec-executive-dashboard/` | 11件 | EC経営ダッシュボード（L3コア） |
| `apps/ec-monthly-briefing/` | 10件 | EC月次AIブリーフィングレポート（L3コア） |
| `apps/ec-rfm/` | 6件 | 顧客RFM分析 |
| `apps/ec-what-if/` | 11件 | What-Ifシミュレーター（L3コア） |
| `apps/payment-alert/` | 6件 | 請求・入金遅延アラート |
| `apps/report-gen/` | 7件 | 月次レポート自動生成 |
| `apps/service-lp/` | 4件 | 統合サービスLP＋AI経営診断 |
| `apps/shigyou-briefing/` | 7件 | 月次AIブリーフィングレポート（L3コア） |
| `apps/shigyou-demo/` | 7件 | 顧問先離反予測デモ |
| `apps/shigyou-ltv/` | 6件 | 顧問先LTV予測＋不採算フラグ |
| `apps/shigyou-office-dashboard/` | 7件 | 事務所経営ダッシュボード（L3コア） |

> 各アプリの内訳ファイル（`app.py` / `create_sample_data.py` / `requirements.txt` / `.streamlit/config.toml` / `sample_data/*.csv` 等）は概ね共通パターンのため個別列挙を省略。詳細はリポジトリを直接参照するか `docs/app-portfolio-analysis.md` を参照。

---

## ファイル詳細（apps/ 以外）

### Documentation (71件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.claude/commands/mvp-build.md` | 4.1 KB | Claude Code カスタムスラッシュコマンド定義 |
| `.claude/commands/mvp-improve.md` | 3.1 KB | Claude Code カスタムスラッシュコマンド定義 |
| `.claude/commands/mvp-plan.md` | 2.5 KB | Claude Code カスタムスラッシュコマンド定義 |
| `.claude/commands/mvp-quality.md` | 4.2 KB | Claude Code カスタムスラッシュコマンド定義 |
| `.claude/cross-repo.md` | 3.5 KB | 他リポジトリ参照ルール（WebFetch/GitHub REST API経由の取得手順） |
| `.claude/quality-rules.md` | 3.0 KB | 品質ガードレール（ファイル生成前・push前・成果物報告前に参照） |
| `.claude/skills/branch-cleanup/SKILL.md` | 6.6 KB | Claude Code スキル定義（branch-cleanup） |
| `.claude/skills/mermaid-agents365/SKILL.md` | 7.6 KB | Claude Code スキル定義（mermaid-agents365） |
| `.claude/skills/mermaid-agents365/reference/CLASS-ER.md` | 2.1 KB | mermaid-agents365スキルの参照資料（CLASS-ER.md） |
| `.claude/skills/mermaid-agents365/reference/FLOWCHART.md` | 1.6 KB | mermaid-agents365スキルの参照資料（FLOWCHART.md） |
| `.claude/skills/mermaid-agents365/reference/OTHER-TYPES.md` | 2.0 KB | mermaid-agents365スキルの参照資料（OTHER-TYPES.md） |
| `.claude/skills/mermaid-agents365/reference/SEQUENCE.md` | 1.7 KB | mermaid-agents365スキルの参照資料（SEQUENCE.md） |
| `.claude/skills/sp-brainstorming/SKILL.md` | 10.5 KB | Claude Code スキル定義（sp-brainstorming） |
| `.claude/skills/sp-executing-plans/SKILL.md` | 2.5 KB | Claude Code スキル定義（sp-executing-plans） |
| `.claude/skills/sp-verification-before-completion/SKILL.md` | 4.2 KB | Claude Code スキル定義（sp-verification-before-completion） |
| `.claude/skills/sp-writing-plans/SKILL.md` | 6.1 KB | Claude Code スキル定義（sp-writing-plans） |
| `.claude/visual-rules.md` | 3.9 KB | レポートMDのビジュアル自動付与ルール |
| `CLAUDE.md` | 15.1 KB | Claude Code プロジェクト設定・命名ルール |
| `FILE_INDEX.md` | 20.3 KB | （このファイル）全ファイルインデックス |
| `ISSUES.md` | 13.7 KB | 初期スコープ（単独MLアプリ）開発時Issue記録（アーカイブ済み・履歴保持） |
| `README.md` | 8.5 KB | リポジトリ概要・セットアップ手順（18アプリポートフォリオ、2026-07-16全面改訂） |
| `Timeout_Prevention.md` | 5.0 KB | Claude Code実行タイムアウト対策ガイド |
| `docs/app-portfolio-analysis.md` | 35.0 KB | 18アプリの重要度分類・統合方針の分析 |
| `docs/context-handoff.md` | 7.7 KB | セッション間の不変条件・戦略整合メモ |
| `docs/ec-business-alignment.md` | 9.9 KB | EC事業の戦略整合ドキュメント |
| `docs/file-index.md` | 8.7 KB | 旧ファイル索引（docs内部用、詳細はFILE_INDEX.md参照） |
| `docs/improvement-backlog.md` | 7.0 KB | 改善バックログ |
| `docs/quality-scoring-rubric.md` | 6.3 KB | 品質スコアリング基準 |
| `docs/rules/01-response-rules.md` | 807 B | 行動ルール（01-response-rules.md） |
| `docs/rules/02-task-management.md` | 1.0 KB | 行動ルール（02-task-management.md） |
| `docs/rules/03-file-index-rules.md` | 1.2 KB | 行動ルール（03-file-index-rules.md） |
| `docs/rules/04-git-rules.md` | 888 B | 行動ルール（04-git-rules.md） |
| `docs/rules/05-model-usage.md` | 947 B | 行動ルール（05-model-usage.md） |
| `docs/rules/06-deliverable-rules.md` | 976 B | 行動ルール（06-deliverable-rules.md） |
| `docs/rules/07-execution-timeout.md` | 4.5 KB | 行動ルール（07-execution-timeout.md） |
| `docs/rules/08-ec-app-roles.md` | 4.2 KB | 行動ルール（08-ec-app-roles.md） |
| `docs/sales-assets/README.md` | 5.0 KB | 営業資産ディレクトリの概要 |
| `docs/sales-assets/customer-pain-research.md` | 6.4 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/demo-script-15min.md` | 10.4 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/demo-tech-checklist.md` | 8.2 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/lead-list-framework.md` | 5.0 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/objection-handling.md` | 14.9 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/outreach-email-templates.md` | 4.3 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/pilot-contract-template.md` | 8.5 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/pilot-proposal-template.md` | 10.7 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/pricing-and-scope.md` | 11.0 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/prospect-research-template.md` | 3.0 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/ringi-summary-template.md` | 3.1 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sales-assets/roi-calculator.md` | 7.1 KB | 営業資産ドキュメント（提案・契約テンプレート等） |
| `docs/sessions/2026-04-08-session-summary.md` | 15.8 KB | セッション要約記録 |
| `docs/sessions/2026-04-30-session-summary.md` | 2.6 KB | セッション要約記録 |
| `docs/shigyou-business-alignment.md` | 14.2 KB | 士業事業の戦略整合ドキュメント |
| `docs/step1_usecase_catalog.md` | 31.5 KB | 事業戦略ステップ資料（step1_usecase_catalog.md） |
| `docs/step2_monetization_scoring.md` | 27.2 KB | 事業戦略ステップ資料（step2_monetization_scoring.md） |
| `docs/step3_prioritization.md` | 18.5 KB | 事業戦略ステップ資料（step3_prioritization.md） |
| `docs/step4_marketing_strategy.md` | 29.4 KB | 事業戦略ステップ資料（step4_marketing_strategy.md） |
| `docs/step5_strategy_review.md` | 25.3 KB | 事業戦略ステップ資料（step5_strategy_review.md） |
| `docs/step6_revised_strategy.md` | 29.5 KB | 事業戦略ステップ資料（step6_revised_strategy.md） |
| `docs/step7_second_review.md` | 40.4 KB | 事業戦略ステップ資料（step7_second_review.md） |
| `docs/task-improvement/00-master-plan.md` | 3.9 KB | タスク改善プロセス記録（00-master-plan.md） |
| `docs/task-improvement/01-critical-thinking.md` | 16.8 KB | タスク改善プロセス記録（01-critical-thinking.md） |
| `docs/task-improvement/02-logical-analysis.md` | 17.8 KB | タスク改善プロセス記録（02-logical-analysis.md） |
| `docs/task-improvement/03-business-strategy.md` | 9.8 KB | タスク改善プロセス記録（03-business-strategy.md） |
| `docs/task-improvement/04-ux-quality.md` | 9.2 KB | タスク改善プロセス記録（04-ux-quality.md） |
| `docs/task-improvement/05-tech-review.md` | 18.5 KB | タスク改善プロセス記録（05-tech-review.md） |
| `docs/task-improvement/06-synthesis.md` | 16.7 KB | タスク改善プロセス記録（06-synthesis.md） |
| `docs/task-improvement/07-action-plan.md` | 11.7 KB | タスク改善プロセス記録（07-action-plan.md） |
| `docs/task-improvement/08-execution-log.md` | 3.7 KB | タスク改善プロセス記録（08-execution-log.md） |
| `docs/task-improvement/09-final-report.md` | 10.8 KB | タスク改善プロセス記録（09-final-report.md） |
| `progress.md` | 1.3 KB | 長時間タスク中断・再開用チェックポイント（アーカイブ済み・履歴保持） |
| `tasks.md` | 7.1 KB | タスク管理・進捗管理のSSOT |

### Code (18件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.claude/hooks/md_table_check.py` | 8.6 KB | GFMパイプテーブルの列数整合性チェックフック |
| `.claude/hooks/post_bash_guard.py` | 1.4 KB | PostToolUseフック（git push後の成果物報告ルール想起） |
| `.claude/hooks/pre_md_table_guard.py` | 4.7 KB | PreToolUseフック（Markdownテーブル列数崩れのWrite/Edit拒否） |
| `.claude/hooks/pre_write_guard.py` | 1.6 KB | PreToolUseフック（Desktop直下等リポ外へのファイル生成拒否） |
| `.claude/hooks/session_guard.py` | 2.4 KB | Stopフック（セッション終了時のブランチ・未pushチェック） |
| `app.py` | 23.7 KB | 単独MLアプリ本体（初期スコープ・汎用LightGBM回帰予測） |
| `create_sample_data.py` | 3.7 KB | app.py用サンプルデータ生成スクリプト |
| `create_sample_data_all.py` | 17.0 KB | 複数ビジネス事例のサンプルデータ生成スクリプト |
| `ec_app.py` | 10.4 KB | ECポータル（apps/ec-* 系アプリのランチャー） |
| `generate_docs_html.py` | 13.7 KB | docs/配下MDをHTML化するスクリプト |
| `modules/__init__.py` | 270 B | modulesパッケージ初期化 |
| `modules/data_loader.py` | 2.7 KB | データ読み込み処理（app.py用） |
| `modules/evaluation.py` | 2.4 KB | 評価指標算出処理（app.py用） |
| `modules/model.py` | 6.2 KB | LightGBMモデル処理（app.py用） |
| `modules/shap_analysis.py` | 9.9 KB | SHAP解析処理（app.py用） |
| `scripts/smoke_test.py` | 7.1 KB | 全アプリ一括スモークテストスクリプト |
| `setup_fonts.py` | 1.2 KB | Streamlit Cloud環境の日本語フォントセットアップスクリプト |
| `streamlit_app.py` | 10.4 KB | 士業ポータル（apps/shigyou-* 系アプリのランチャー） |

### Data (16件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.claude/settings.json` | 856 B | Claude Code 共有設定 |
| `.claude/settings.local.json` | 579 B | Claude Code ローカル設定 |
| `docs/sales-assets/_workspace/state.json` | 4.7 KB | 営業資産ワークスペースの状態データ |
| `docs/task-improvement/smoke-test-result.json` | 7.0 KB | タスク改善プロセスのスモークテスト結果データ |
| `sample_data/1_salary_target.csv` | 3.5 KB | app.py用サンプルデータ（CSV） |
| `sample_data/1_salary_train.csv` | 38.8 KB | app.py用サンプルデータ（CSV） |
| `sample_data/2_realestate_target.csv` | 3.8 KB | app.py用サンプルデータ（CSV） |
| `sample_data/2_realestate_train.csv` | 41.1 KB | app.py用サンプルデータ（CSV） |
| `sample_data/3_sales_target.csv` | 3.5 KB | app.py用サンプルデータ（CSV） |
| `sample_data/3_sales_train.csv` | 36.9 KB | app.py用サンプルデータ（CSV） |
| `sample_data/4_ltv_target.csv` | 3.5 KB | app.py用サンプルデータ（CSV） |
| `sample_data/4_ltv_train.csv` | 37.6 KB | app.py用サンプルデータ（CSV） |
| `sample_data/5_turnover_target.csv` | 1.9 KB | app.py用サンプルデータ（CSV） |
| `sample_data/5_turnover_train.csv` | 20.3 KB | app.py用サンプルデータ（CSV） |
| `sample_data/target.csv` | 2.6 KB | app.py用サンプルデータ（CSV） |
| `sample_data/train.csv` | 29.2 KB | app.py用サンプルデータ（CSV） |

### Config (7件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.github/workflows/md-table-lint.yml` | 374 B | GitHub Actions ワークフロー |
| `.github/workflows/patch-ec-what-if.yml` | 2.1 KB | GitHub Actions ワークフロー |
| `.gitignore` | 697 B | Git除外設定 |
| `.python-version` | 6 B | Pythonバージョン指定（3.11） |
| `.streamlit/config.toml` | 276 B | Streamlit設定（ルートapp.py用） |
| `packages.txt` | 38 B | aptパッケージリスト（Streamlit Cloud用） |
| `requirements.txt` | 150 B | Python依存パッケージリスト（ルート・app.py用） |

### Other (2件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `docs/index.html` | 290.6 KB | generate_docs_html.pyで生成されたドキュメント閲覧用HTML |
| `start_app.bat` | 213 B | app.py起動用Windowsバッチファイル |

---

_自動生成: 2026-07-16 | 管理者: 男座員也（Kazuya Oza）_
