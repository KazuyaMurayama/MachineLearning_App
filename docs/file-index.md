# リポジトリ ファイルインデックス

> 最終更新: 2026-04-16
> 対象ブランチ: `claude/organize-repo-by-date-VNw9E`（現行作業）、`claude/integrate-business-plan-IBKFu`（統合）、`main`（公開）
> このファイルは新規ファイル作成・大幅変更時に必ず更新する。

## 使い方

ファイル参照が必要な場合、まずこのインデックスで該当ファイルを特定する。カテゴリ別に整理しているため、機能名や種別から検索可能。

---

## 0. セッション引継ぎ・プロジェクト規約

| ファイル | 概要 |
|---------|------|
| `CLAUDE.md` | Claude Code プロジェクトガイド（最小ポインタ）。セッション開始時に最初に読む |
| `docs/context-handoff.md` | 現行状況・不変条件・マルチエージェントパターン・API タイムアウト対策・セッション終了手順 |
| `tasks.md` | セッション間引継ぎタスクリスト（次にやること・進行中・完了） |
| `docs/sessions/` | 日付別セッション要約（`YYYY-MM-DD-session-summary.md`） |
| `ISSUES.md` | 開発 Issue 一覧・進捗管理表 |
| `README.md` | プロジェクト概要・セットアップ・使い方 |

---

## 1. Streamlit アプリ本体

### 1-1. ルートレベル・ポータル

| ファイル | 概要 | 行数 |
|---------|------|:---:|
| `app.py` | ML 予測コア（LightGBM + SHAP 回帰） | 466 |
| `streamlit_app.py` | 士業ポータル（9 アプリ統合） | 216 |
| `ec_app.py` | EC ポータル（6 アプリ統合） | 213 |

### 1-2. 士業向けアプリ（`apps/`）

| ファイル | 概要 | 行数 |
|---------|------|:---:|
| `apps/shigyou-demo/app.py` | 顧問先離反予測デモ（LightGBM + SHAP + 逆 SHAP） | 851 |
| `apps/crosssell/app.py` | クロスセル分析ツール | 610 |
| `apps/payment-alert/app.py` | 請求・入金遅延アラート | 567 |
| `apps/report-gen/app.py` | 月次レポート自動生成（freee/MF CSV） | 671 |
| `apps/compliance-pack/app.py` | コンプライアンス対応テンプレート集 | 427 |
| `apps/contract-draft/app.py` | 契約書ドラフト AI | 510 |
| `apps/doc-checker/app.py` | 申請書類チェッカー | 697 |
| `apps/service-lp/app.py` | サービス LP + AI 経営診断 | 446 |
| `apps/shigyou-office-dashboard/app.py` | 事務所経営ダッシュボード（L3） | — |
| `apps/shigyou-ltv/app.py` | 顧問先 LTV 予測＋不採算フラグ（L3） | — |
| `apps/shigyou-briefing/app.py` | 月次 AI ブリーフィング（L3） | — |

### 1-3. EC 向けアプリ（`apps/`）

| ファイル | 概要 | 行数 |
|---------|------|:---:|
| `apps/ec-demo/app.py` | 顧客離脱予測 + 需要予測デモ | 496 |
| `apps/ec-dashboard/app.py` | 売上ダッシュボード | 811 |
| `apps/ec-rfm/app.py` | RFM 分析＋セグメンテーション | 749 |
| `apps/ec-ad-roi/app.py` | 広告 ROI 分析 | 817 |
| `apps/ec-executive-dashboard/app.py` | EC 経営ダッシュボード（L3） | — |
| `apps/ec-what-if/app.py` | What-If シミュレーター（L3、**R²=-0.16 精度再検証中**） | — |
| `apps/ec-monthly-briefing/app.py` | 月次 AI ブリーフィング（L3） | — |

---

## 2. サンプルデータ生成スクリプト

### 2-1. ルートレベル

| ファイル | 概要 |
|---------|------|
| `create_sample_data.py` | 教師・ターゲット CSV を生成（単一ケース） |
| `create_sample_data_all.py` | 5 ケース一括生成（年収・不動産・日次売上・LTV・離職） |

### 2-2. アプリ別 `apps/*/create_sample_data.py`

各アプリディレクトリに配置。士業系 8 本 + EC 系 7 本 = **15 本**。命名は各 app ディレクトリと一致。

---

## 3. サンプルデータ CSV

### 3-1. ルート `sample_data/`

汎用 2 ファイル + 5 ケース × 2 ファイル = **12 ファイル**（`train.csv` / `target.csv`、`{1-5}_{case}_train.csv` / `{1-5}_{case}_target.csv`）。全ブランチ共通。

### 3-2. アプリ別 `apps/*/sample_data/`

各アプリに専用データ配置。士業系（shigyou, crosssell, payment-alert, report-gen）+ EC 系（ec-demo, ec-dashboard, ec-rfm, ec-ad-roi）の計 13 ファイル以上。

---

## 4. 共通モジュール

### 4-1. `modules/`（ルート、ML コア用）

| ファイル | 概要 | 行数 |
|---------|------|:---:|
| `modules/__init__.py` | パッケージ初期化 | 10 |
| `modules/data_loader.py` | CSV/Excel 読み込み・前処理 | 100 |
| `modules/evaluation.py` | RMSE/MAE/R² 算出 | 92 |
| `modules/model.py` | LightGBM 学習・予測 | 216 |
| `modules/shap_analysis.py` | SHAP 解析・可視化 | 355 |

### 4-2. `apps/common/`

| ファイル | 概要 | 行数 |
|---------|------|:---:|
| `apps/common/__init__.py` | 共通モジュール初期化 | — |
| `apps/common/reverse_shap.py` | 逆 SHAP エンジン（Why→How） | 245 |

---

## 5. 設定ファイル

| パターン | 概要 |
|---------|------|
| `.streamlit/config.toml`（ルート） | Streamlit テーマ・ポート |
| `apps/*/.streamlit/config.toml` | 各アプリ個別 Streamlit 設定 |
| `requirements.txt`（ルート） + `apps/*/requirements.txt` | 依存パッケージ |
| `packages.txt`（ルート） + `apps/*/packages.txt` | システムパッケージ（日本語フォント等） |
| `.python-version` | pyenv 用 Python バージョン |
| `.gitignore` | Git 除外設定 |
| `.claude/settings.local.json` | Claude Code ローカル設定 |

---

## 6. ドキュメント（`docs/`）

### 6-1. 全般

| ファイル | 概要 |
|---------|------|
| `docs/file-index.md` | **本ファイル**。リポジトリ全ファイル索引 |
| `docs/context-handoff.md` | セッション引継ぎ詳細（不変条件・エージェントパターン・タイムアウト対策） |
| `docs/improvement-backlog.md` | 全アプリ改善候補バックログ |
| `docs/quality-scoring-rubric.md` | 5 軸 100 点アプリ品質採点基準 |
| `docs/shigyou-business-alignment.md` | 士業 MVP × 事業計画 整合性チェック |
| `docs/ec-business-alignment.md` | EC MVP × 事業計画 整合性チェック |

### 6-2. セッション記録 (`docs/sessions/`)

| ファイル | 概要 |
|---------|------|
| `docs/sessions/2026-04-08-session-summary.md` | L3 キラー機能実装・マルチエージェント品質改善セッション要約 |

### 6-3. 営業アセット (`docs/sales-assets/`)

詳細は `docs/sales-assets/README.md` を参照。

| ファイル | 文書 ID | 用途 |
|---------|--------|------|
| `docs/sales-assets/README.md` | — | 営業アセット全体ガイド |
| `docs/sales-assets/pricing-and-scope.md` | SA-PRC-001 | 料金・SLA の SSOT |
| `docs/sales-assets/pilot-proposal-template.md` | SA-PRO-001 | パイロット提案書（士業・EC） |
| `docs/sales-assets/demo-script-15min.md` | — | 15 分デモスクリプト |
| `docs/sales-assets/demo-tech-checklist.md` | SA-DEMO-001 | デモ技術チェックリスト |
| `docs/sales-assets/roi-calculator.md` | SA-ROI-001 | ROI 試算ワークシート |
| `docs/sales-assets/pilot-contract-template.md` | SA-CNT-001 | パイロット契約雛形（法務レビュー要） |
| `docs/sales-assets/objection-handling.md` | SA-OBJ-001 | 反論対応 15 件 |
| `docs/sales-assets/ringi-summary-template.md` | SA-RNG-001 | 稟議用 1 枚サマリ |
| `docs/sales-assets/outreach-email-templates.md` | SA-EMAIL-001 | メールテンプレ 5 種 |
| `docs/sales-assets/prospect-research-template.md` | SA-RSCH-001 | 事前調査 1 枚シート |
| `docs/sales-assets/customer-pain-research.md` | SA-PAIN-001 | ペイン仮説マップ（**INTERNAL ONLY**） |
| `docs/sales-assets/lead-list-framework.md` | SA-LEAD-001 | リード獲得戦略（**INTERNAL ONLY**） |
| `docs/sales-assets/_workspace/state.json` | — | 改善プロセス進捗台帳 |

### 6-4. マルチエージェント改善履歴 (`docs/task-improvement/`)

| ファイル | 概要 |
|---------|------|
| `docs/task-improvement/00-master-plan.md` | 改善プロセスマスタープラン |
| `docs/task-improvement/01-critical-thinking.md` | Critic: クリティカルシンカー評価 |
| `docs/task-improvement/02-logical-analysis.md` | Critic: 論理分析 |
| `docs/task-improvement/03-business-strategy.md` | Critic: 事業戦略 |
| `docs/task-improvement/04-ux-quality.md` | Critic: UX 品質 |
| `docs/task-improvement/05-tech-review.md` | Critic: 技術レビュー |
| `docs/task-improvement/06-synthesis.md` | 5 批評統合 |
| `docs/task-improvement/07-action-plan.md` | 優先順位付きアクションプラン |
| `docs/task-improvement/08-execution-log.md` | 実行ログ |
| `docs/task-improvement/09-final-report.md` | 最終報告書 |
| `docs/task-improvement/smoke-test-result.json` | スモークテスト結果 |

---

## 7. カスタムコマンド (`.claude/commands/`)

| ファイル | 概要 |
|---------|------|
| `.claude/commands/mvp-plan.md` | MVP 企画・優先順位付け |
| `.claude/commands/mvp-build.md` | MVP 実装 |
| `.claude/commands/mvp-quality.md` | 5 軸 100 点採点 |
| `.claude/commands/mvp-improve.md` | 4 エージェント並列改善実行 |

---

## 8. その他

| ファイル | 概要 |
|---------|------|
| `start_app.bat` | Windows 用起動バッチ |
| `setup_fonts.py` | Streamlit Cloud 日本語フォントセットアップ（38 行） |

---

## ブランチ別ファイル分布

| 分類 | `main` | `integrate-business-plan-IBKFu` | `organize-repo-by-date-VNw9E` |
|-----|:------:|:--------:|:--------:|
| ML コアアプリ（`app.py`） | ○ | ○ | ○ |
| L1/L2 士業・EC アプリ | — | ○ | ○ |
| L3 キラー機能（士業 3 + EC 3） | — | ○ | ○ |
| 営業アセット（sales-assets） | — | — | ○ |
| セッション記録 / 引継ぎ | — | 一部 | ○ |
| タスク・コンテキスト引継ぎ（tasks.md, context-handoff.md） | — | — | ○ |

> `main` への反映は PR 経由で行う。現行 PR: #2（VNw9E → IBKFu）。次ステップ: IBKFu → main の PR。
