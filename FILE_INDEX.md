# FILE_INDEX — MachineLearning_App

> ⚠️ このファイルは自動生成です。手動編集は次回更新で上書きされます。

| 項目 | 値 |
|---|---|
| リポジトリ | KazuyaMurayama/MachineLearning_App |
| ブランチ | main |
| 総ファイル数 | 217 |
| 最終更新 | 2026-05-02 |
| 管理者 | 男座員也（Kazuya Oza） |

---

## カテゴリ別サマリー

| カテゴリ | ファイル数 |
|---|---|
| Documentation | 77 |
| Code | 50 |
| Data | 48 |
| Config | 39 |
| Other | 3 |

---

## ディレクトリ構成

```
.
├── .claude/
│   ├── commands/
│   │   ... (4 items)
│   └── settings.local.json
├── .github/
│   └── workflows/
│       ... (1 items)
├── .streamlit/
│   └── config.toml
├── apps/
│   ├── common/
│   │   ... (2 items)
│   ├── compliance-pack/
│   │   ... (4 items)
│   ├── contract-draft/
│   │   ... (4 items)
│   ├── crosssell/
│   │   ... (6 items)
│   ├── doc-checker/
│   │   ... (4 items)
│   ├── ec-ad-roi/
│   │   ... (6 items)
│   ├── ec-dashboard/
│   │   ... (6 items)
│   ├── ec-demo/
│   │   ... (6 items)
│   ├── ec-executive-dashboard/
│   │   ... (7 items)
│   ├── ec-monthly-briefing/
│   │   ... (7 items)
│   ├── ec-rfm/
│   │   ... (6 items)
│   ├── ec-what-if/
│   │   ... (7 items)
│   ├── payment-alert/
│   │   ... (6 items)
│   ├── report-gen/
│   │   ... (6 items)
│   ├── service-lp/
│   │   ... (4 items)
│   ├── shigyou-briefing/
│   │   ... (6 items)
│   ├── shigyou-demo/
│   │   ... (6 items)
│   ├── shigyou-ltv/
│   │   ... (6 items)
│   └── shigyou-office-dashboard/
│       ... (6 items)
├── docs/
│   ├── rules/
│   │   ... (8 items)
│   ├── sales-assets/
│   │   ... (14 items)
│   ├── sessions/
│   │   ... (2 items)
│   ├── task-improvement/
│   │   ... (11 items)
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
├── app.py
├── CLAUDE.md
├── create_sample_data_all.py
├── create_sample_data.py
├── ec_app.py
├── FILE_INDEX.md
├── generate_docs_html.py
├── ISSUES.md
├── packages.txt
├── progress.md
├── README.md
├── requirements.txt
├── setup_fonts.py
├── start_app.bat
├── streamlit_app.py
├── tasks.md
└── Timeout_Prevention.md
```

---

## ファイル詳細

### Documentation (77件)

<details>
<summary>クリックして展開 (77件)</summary>

| ファイル | サイズ | 説明 |
|---|---|---|
| `.claude/commands/mvp-build.md` | 4.0 KB | Claude Code 設定・スキル |
| `.claude/commands/mvp-improve.md` | 3.0 KB | Claude Code 設定・スキル |
| `.claude/commands/mvp-plan.md` | 2.4 KB | Claude Code 設定・スキル |
| `.claude/commands/mvp-quality.md` | 4.1 KB | Claude Code 設定・スキル |
| `apps/compliance-pack/packages.txt` | 15 B | ファイル |
| `apps/contract-draft/packages.txt` | 15 B | ファイル |
| `apps/crosssell/packages.txt` | 15 B | ファイル |
| `apps/doc-checker/packages.txt` | 15 B | ファイル |
| `apps/ec-ad-roi/packages.txt` | 15 B | ファイル |
| `apps/ec-dashboard/packages.txt` | 15 B | ファイル |
| `apps/ec-demo/packages.txt` | 15 B | ファイル |
| `apps/ec-executive-dashboard/packages.txt` | 36 B | ファイル |
| `apps/ec-monthly-briefing/packages.txt` | 36 B | ファイル |
| `apps/ec-rfm/packages.txt` | 15 B | ファイル |
| `apps/ec-what-if/packages.txt` | 45 B | ファイル |
| `apps/payment-alert/packages.txt` | 15 B | ファイル |
| `apps/report-gen/packages.txt` | 15 B | ファイル |
| `apps/service-lp/packages.txt` | 15 B | ファイル |
| `apps/shigyou-briefing/packages.txt` | 36 B | ファイル |
| `apps/shigyou-demo/packages.txt` | 15 B | ファイル |
| `apps/shigyou-ltv/packages.txt` | 36 B | ファイル |
| `apps/shigyou-office-dashboard/packages.txt` | 36 B | ファイル |
| `CLAUDE.md` | 2.7 KB | Claude Code プロジェクト設定・命名ルール |
| `docs/app-portfolio-analysis.md` | 34.4 KB | Markdown ドキュメント |
| `docs/context-handoff.md` | 7.6 KB | Markdown ドキュメント |
| `docs/ec-business-alignment.md` | 9.5 KB | Markdown ドキュメント |
| `docs/file-index.md` | 7.7 KB | Markdown ドキュメント |
| `docs/improvement-backlog.md` | 6.9 KB | Markdown ドキュメント |
| `docs/quality-scoring-rubric.md` | 6.2 KB | Markdown ドキュメント |
| `docs/rules/01-response-rules.md` | 799 B | Markdown ドキュメント |
| `docs/rules/02-task-management.md` | 1019 B | Markdown ドキュメント |
| `docs/rules/03-file-index-rules.md` | 1.1 KB | Markdown ドキュメント |
| `docs/rules/04-git-rules.md` | 867 B | Markdown ドキュメント |
| `docs/rules/05-model-usage.md` | 919 B | Markdown ドキュメント |
| `docs/rules/06-deliverable-rules.md` | 947 B | Markdown ドキュメント |
| `docs/rules/07-execution-timeout.md` | 4.4 KB | Markdown ドキュメント |
| `docs/rules/08-ec-app-roles.md` | 4.1 KB | Markdown ドキュメント |
| `docs/sales-assets/customer-pain-research.md` | 6.2 KB | Markdown ドキュメント |
| `docs/sales-assets/demo-script-15min.md` | 10.2 KB | Markdown ドキュメント |
| `docs/sales-assets/demo-tech-checklist.md` | 8.0 KB | Markdown ドキュメント |
| `docs/sales-assets/lead-list-framework.md` | 4.9 KB | Markdown ドキュメント |
| `docs/sales-assets/objection-handling.md` | 14.7 KB | Markdown ドキュメント |
| `docs/sales-assets/outreach-email-templates.md` | 4.2 KB | Markdown ドキュメント |
| `docs/sales-assets/pilot-contract-template.md` | 8.4 KB | Markdown ドキュメント |
| `docs/sales-assets/pilot-proposal-template.md` | 10.5 KB | Markdown ドキュメント |
| `docs/sales-assets/pricing-and-scope.md` | 10.8 KB | Markdown ドキュメント |
| `docs/sales-assets/prospect-research-template.md` | 2.9 KB | Markdown ドキュメント |
| `docs/sales-assets/README.md` | 4.9 KB | リポジトリ概要・セットアップ手順 |
| `docs/sales-assets/ringi-summary-template.md` | 3.0 KB | Markdown ドキュメント |
| `docs/sales-assets/roi-calculator.md` | 6.9 KB | Markdown ドキュメント |
| `docs/sessions/2026-04-08-session-summary.md` | 15.5 KB | Markdown ドキュメント |
| `docs/sessions/2026-04-30-session-summary.md` | 2.6 KB | Markdown ドキュメント |
| `docs/shigyou-business-alignment.md` | 14.0 KB | Markdown ドキュメント |
| `docs/step1_usecase_catalog.md` | 31.0 KB | Markdown ドキュメント |
| `docs/step2_monetization_scoring.md` | 26.8 KB | Markdown ドキュメント |
| `docs/step3_prioritization.md` | 18.1 KB | Markdown ドキュメント |
| `docs/step4_marketing_strategy.md` | 28.8 KB | Markdown ドキュメント |
| `docs/step5_strategy_review.md` | 24.9 KB | Markdown ドキュメント |
| `docs/step6_revised_strategy.md` | 29.0 KB | Markdown ドキュメント |
| `docs/step7_second_review.md` | 39.8 KB | Markdown ドキュメント |
| `docs/task-improvement/00-master-plan.md` | 3.8 KB | Markdown ドキュメント |
| `docs/task-improvement/01-critical-thinking.md` | 16.7 KB | Markdown ドキュメント |
| `docs/task-improvement/02-logical-analysis.md` | 17.7 KB | Markdown ドキュメント |
| `docs/task-improvement/03-business-strategy.md` | 9.7 KB | Markdown ドキュメント |
| `docs/task-improvement/04-ux-quality.md` | 9.1 KB | Markdown ドキュメント |
| `docs/task-improvement/05-tech-review.md` | 18.3 KB | Markdown ドキュメント |
| `docs/task-improvement/06-synthesis.md` | 16.5 KB | Markdown ドキュメント |
| `docs/task-improvement/07-action-plan.md` | 11.5 KB | Markdown ドキュメント |
| `docs/task-improvement/08-execution-log.md` | 3.7 KB | Markdown ドキュメント |
| `docs/task-improvement/09-final-report.md` | 10.6 KB | Markdown ドキュメント |
| `FILE_INDEX.md` | 4.7 KB | （このファイル）全ファイルインデックス |
| `ISSUES.md` | 12.9 KB | Markdown ドキュメント |
| `packages.txt` | 36 B | ファイル |
| `progress.md` | 930 B | Markdown ドキュメント |
| `README.md` | 4.3 KB | リポジトリ概要・セットアップ手順 |
| `tasks.md` | 6.5 KB | タスク管理・セッション履歴 |
| `Timeout_Prevention.md` | 4.9 KB | タイムアウト対策ガイド |

</details>

### Code (50件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `app.py` | 23.2 KB | Python スクリプト |
| `apps/common/__init__.py` | - | Python スクリプト |
| `apps/common/reverse_shap.py` | 8.4 KB | Python スクリプト |
| `apps/compliance-pack/app.py` | 21.5 KB | Python スクリプト |
| `apps/contract-draft/app.py` | 23.3 KB | Python スクリプト |
| `apps/crosssell/app.py` | 28.5 KB | Python スクリプト |
| `apps/crosssell/create_sample_data.py` | 3.3 KB | Python スクリプト |
| `apps/doc-checker/app.py` | 40.3 KB | Python スクリプト |
| `apps/ec-ad-roi/app.py` | 36.1 KB | Python スクリプト |
| `apps/ec-ad-roi/create_sample_data.py` | 2.6 KB | Python スクリプト |
| `apps/ec-dashboard/app.py` | 37.5 KB | Python スクリプト |
| `apps/ec-dashboard/create_sample_data.py` | 2.0 KB | Python スクリプト |
| `apps/ec-demo/app.py` | 31.8 KB | Python スクリプト |
| `apps/ec-demo/create_sample_data.py` | 9.4 KB | Python スクリプト |
| `apps/ec-executive-dashboard/app.py` | 8.6 KB | Python スクリプト |
| `apps/ec-executive-dashboard/create_sample_data.py` | 4.1 KB | Python スクリプト |
| `apps/ec-executive-dashboard/helpers.py` | 11.7 KB | Python スクリプト |
| `apps/ec-monthly-briefing/app.py` | 8.9 KB | Python スクリプト |
| `apps/ec-monthly-briefing/create_sample_data.py` | 3.1 KB | Python スクリプト |
| `apps/ec-monthly-briefing/helpers.py` | 16.4 KB | Python スクリプト |
| `apps/ec-rfm/app.py` | 33.5 KB | Python スクリプト |
| `apps/ec-rfm/create_sample_data.py` | 5.0 KB | Python スクリプト |
| `apps/ec-what-if/app.py` | 32.0 KB | Python スクリプト |
| `apps/ec-what-if/create_sample_data.py` | 7.6 KB | Python スクリプト |
| `apps/ec-what-if/data_setup.py` | 1.1 KB | Python スクリプト |
| `apps/payment-alert/app.py` | 24.5 KB | Python スクリプト |
| `apps/payment-alert/create_sample_data.py` | 4.0 KB | Python スクリプト |
| `apps/report-gen/app.py` | 33.0 KB | Python スクリプト |
| `apps/report-gen/create_sample_data.py` | 4.2 KB | Python スクリプト |
| `apps/service-lp/app.py` | 29.4 KB | Python スクリプト |
| `apps/shigyou-briefing/app.py` | 27.1 KB | Python スクリプト |
| `apps/shigyou-briefing/create_sample_data.py` | 3.2 KB | Python スクリプト |
| `apps/shigyou-demo/app.py` | 37.1 KB | Python スクリプト |
| `apps/shigyou-demo/create_sample_data.py` | 8.3 KB | Python スクリプト |
| `apps/shigyou-ltv/app.py` | 34.5 KB | Python スクリプト |
| `apps/shigyou-ltv/create_sample_data.py` | 3.9 KB | Python スクリプト |
| `apps/shigyou-office-dashboard/app.py` | 21.7 KB | Python スクリプト |
| `apps/shigyou-office-dashboard/create_sample_data.py` | 5.5 KB | Python スクリプト |
| `create_sample_data_all.py` | 16.6 KB | Python スクリプト |
| `create_sample_data.py` | 3.6 KB | Python スクリプト |
| `ec_app.py` | 10.1 KB | Python スクリプト |
| `generate_docs_html.py` | 13.2 KB | Python スクリプト |
| `modules/__init__.py` | 260 B | Python スクリプト |
| `modules/data_loader.py` | 2.6 KB | Python スクリプト |
| `modules/evaluation.py` | 2.3 KB | Python スクリプト |
| `modules/model.py` | 6.0 KB | Python スクリプト |
| `modules/shap_analysis.py` | 9.6 KB | Python スクリプト |
| `scripts/smoke_test.py` | 6.9 KB | Python スクリプト |
| `setup_fonts.py` | 1.2 KB | Python スクリプト |
| `streamlit_app.py` | 10.2 KB | Python スクリプト |

### Data (48件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.claude/settings.local.json` | 554 B | JSON データ |
| `.github/workflows/patch-ec-what-if.yml` | 2.0 KB | GitHub Actions ワークフロー |
| `apps/crosssell/sample_data/crosssell_data.csv` | 11.1 KB | CSV データ |
| `apps/ec-ad-roi/sample_data/ad_performance.csv` | 4.1 KB | CSV データ |
| `apps/ec-dashboard/sample_data/daily_sales.csv` | 133.7 KB | CSV データ |
| `apps/ec-demo/sample_data/ec_customers_target.csv` | 11.2 KB | CSV データ |
| `apps/ec-demo/sample_data/ec_customers_train.csv` | 56.4 KB | CSV データ |
| `apps/ec-demo/sample_data/ec_sales_target.csv` | 90.0 KB | CSV データ |
| `apps/ec-demo/sample_data/ec_sales_train.csv` | 1.2 MB | CSV データ |
| `apps/ec-executive-dashboard/sample_data/ads.csv` | 4.3 KB | CSV データ |
| `apps/ec-executive-dashboard/sample_data/cross_segment.csv` | 1.0 KB | CSV データ |
| `apps/ec-executive-dashboard/sample_data/customers.csv` | 17.3 KB | CSV データ |
| `apps/ec-executive-dashboard/sample_data/orders.csv` | 14.1 KB | CSV データ |
| `apps/ec-executive-dashboard/sample_data/products.csv` | 2.8 KB | CSV データ |
| `apps/ec-monthly-briefing/sample_data/ads.csv` | 4.3 KB | CSV データ |
| `apps/ec-monthly-briefing/sample_data/customers.csv` | 17.3 KB | CSV データ |
| `apps/ec-monthly-briefing/sample_data/orders.csv` | 14.1 KB | CSV データ |
| `apps/ec-monthly-briefing/sample_data/products.csv` | 2.8 KB | CSV データ |
| `apps/ec-rfm/sample_data/purchase_history.csv` | 217.5 KB | CSV データ |
| `apps/ec-what-if/sample_data/ads.csv` | 4.3 KB | CSV データ |
| `apps/ec-what-if/sample_data/customers.csv` | 17.3 KB | CSV データ |
| `apps/ec-what-if/sample_data/orders.csv` | 14.1 KB | CSV データ |
| `apps/ec-what-if/sample_data/products.csv` | 2.8 KB | CSV データ |
| `apps/ec-what-if/sample_data/training_data.csv` | 27.7 KB | CSV データ |
| `apps/payment-alert/sample_data/payment_data.csv` | 164.3 KB | CSV データ |
| `apps/report-gen/sample_data/trial_balance_current.csv` | 971 B | CSV データ |
| `apps/report-gen/sample_data/trial_balance_prev.csv` | 962 B | CSV データ |
| `apps/shigyou-briefing/sample_data/briefing_master.csv` | 10.8 KB | CSV データ |
| `apps/shigyou-briefing/sample_data/monthly_history.csv` | 440 B | CSV データ |
| `apps/shigyou-demo/sample_data/shigyou_target.csv` | 2.3 KB | CSV データ |
| `apps/shigyou-demo/sample_data/shigyou_train.csv` | 10.9 KB | CSV データ |
| `apps/shigyou-ltv/sample_data/ltv_train.csv` | 15.8 KB | CSV データ |
| `apps/shigyou-office-dashboard/sample_data/monthly_kpi.csv` | 377 B | CSV データ |
| `apps/shigyou-office-dashboard/sample_data/office_master.csv` | 12.9 KB | CSV データ |
| `docs/sales-assets/_workspace/state.json` | 4.6 KB | JSON データ |
| `docs/task-improvement/smoke-test-result.json` | 6.7 KB | JSON データ |
| `sample_data/1_salary_target.csv` | 3.4 KB | CSV データ |
| `sample_data/1_salary_train.csv` | 37.8 KB | CSV データ |
| `sample_data/2_realestate_target.csv` | 3.7 KB | CSV データ |
| `sample_data/2_realestate_train.csv` | 40.3 KB | CSV データ |
| `sample_data/3_sales_target.csv` | 3.4 KB | CSV データ |
| `sample_data/3_sales_train.csv` | 36.3 KB | CSV データ |
| `sample_data/4_ltv_target.csv` | 3.4 KB | CSV データ |
| `sample_data/4_ltv_train.csv` | 36.9 KB | CSV データ |
| `sample_data/5_turnover_target.csv` | 1.8 KB | CSV データ |
| `sample_data/5_turnover_train.csv` | 19.8 KB | CSV データ |
| `sample_data/target.csv` | 2.5 KB | CSV データ |
| `sample_data/train.csv` | 28.2 KB | CSV データ |

### Config (39件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.gitignore` | 630 B | Git 除外設定 |
| `.streamlit/config.toml` | 261 B | TOML 設定 |
| `apps/compliance-pack/.streamlit/config.toml` | 158 B | TOML 設定 |
| `apps/compliance-pack/requirements.txt` | 18 B | Python 依存パッケージリスト |
| `apps/contract-draft/.streamlit/config.toml` | 158 B | TOML 設定 |
| `apps/contract-draft/requirements.txt` | 18 B | Python 依存パッケージリスト |
| `apps/crosssell/.streamlit/config.toml` | 185 B | TOML 設定 |
| `apps/crosssell/requirements.txt` | 92 B | Python 依存パッケージリスト |
| `apps/doc-checker/.streamlit/config.toml` | 185 B | TOML 設定 |
| `apps/doc-checker/requirements.txt` | 18 B | Python 依存パッケージリスト |
| `apps/ec-ad-roi/.streamlit/config.toml` | 185 B | TOML 設定 |
| `apps/ec-ad-roi/requirements.txt` | 141 B | Python 依存パッケージリスト |
| `apps/ec-dashboard/.streamlit/config.toml` | 185 B | TOML 設定 |
| `apps/ec-dashboard/requirements.txt` | 92 B | Python 依存パッケージリスト |
| `apps/ec-demo/.streamlit/config.toml` | 158 B | TOML 設定 |
| `apps/ec-demo/requirements.txt` | 141 B | Python 依存パッケージリスト |
| `apps/ec-executive-dashboard/.streamlit/config.toml` | 140 B | TOML 設定 |
| `apps/ec-executive-dashboard/requirements.txt` | 64 B | Python 依存パッケージリスト |
| `apps/ec-monthly-briefing/.streamlit/config.toml` | 140 B | TOML 設定 |
| `apps/ec-monthly-briefing/requirements.txt` | 64 B | Python 依存パッケージリスト |
| `apps/ec-rfm/.streamlit/config.toml` | 185 B | TOML 設定 |
| `apps/ec-rfm/requirements.txt` | 92 B | Python 依存パッケージリスト |
| `apps/ec-what-if/.streamlit/config.toml` | 140 B | TOML 設定 |
| `apps/ec-what-if/requirements.txt` | 113 B | Python 依存パッケージリスト |
| `apps/payment-alert/.streamlit/config.toml` | 185 B | TOML 設定 |
| `apps/payment-alert/requirements.txt` | 92 B | Python 依存パッケージリスト |
| `apps/report-gen/.streamlit/config.toml` | 158 B | TOML 設定 |
| `apps/report-gen/requirements.txt` | 92 B | Python 依存パッケージリスト |
| `apps/service-lp/.streamlit/config.toml` | 158 B | TOML 設定 |
| `apps/service-lp/requirements.txt` | 50 B | Python 依存パッケージリスト |
| `apps/shigyou-briefing/.streamlit/config.toml` | 140 B | TOML 設定 |
| `apps/shigyou-briefing/requirements.txt` | 64 B | Python 依存パッケージリスト |
| `apps/shigyou-demo/.streamlit/config.toml` | 158 B | TOML 設定 |
| `apps/shigyou-demo/requirements.txt` | 141 B | Python 依存パッケージリスト |
| `apps/shigyou-ltv/.streamlit/config.toml` | 140 B | TOML 設定 |
| `apps/shigyou-ltv/requirements.txt` | 113 B | Python 依存パッケージリスト |
| `apps/shigyou-office-dashboard/.streamlit/config.toml` | 140 B | TOML 設定 |
| `apps/shigyou-office-dashboard/requirements.txt` | 64 B | Python 依存パッケージリスト |
| `requirements.txt` | 141 B | Python 依存パッケージリスト |

### Other (3件)

| ファイル | サイズ | 説明 |
|---|---|---|
| `.python-version` | 5 B | ファイル |
| `docs/index.html` | 287.5 KB | ファイル |
| `start_app.bat` | 203 B | ファイル |

---

_自動生成: 2026-05-02 | 管理者: 男座員也（Kazuya Oza）_
