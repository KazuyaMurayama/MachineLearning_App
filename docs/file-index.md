# リポジトリ ファイルインデックス

> 最終更新: 2026-04-30
> 対象: `main` ブランチ（全ファイルを main に集約。ブランチ作成は `docs/rules/04-git-rules.md` で禁止）
> 新規ファイル作成・大幅変更時は本ファイルを必ず更新する（`docs/rules/03-file-index-rules.md` 参照）

---

## 0. セッション引継ぎ・プロジェクト規約

| ファイル | 概要 |
|---------|------|
| `CLAUDE.md` | プロジェクトガイド（最小ポインタ + ルール参照テーブル） |
| `tasks.md` | セッション間引継ぎタスクリスト |
| `docs/context-handoff.md` | 不変条件・戦略整合・撤退基準・マルチエージェントパターン |
| `docs/file-index.md` | **本ファイル**。全ファイル索引 |
| `docs/sessions/` | 日付別セッション要約 |
| `ISSUES.md` | 開発 Issue 一覧 |
| `README.md` | プロジェクト概要・セットアップ |

### 行動ルール（`docs/rules/`）

| ファイル | 内容 |
|---------|------|
| `docs/rules/01-response-rules.md` | 回答の基本ルール |
| `docs/rules/02-task-management.md` | タスク管理（tasks.md 一元管理） |
| `docs/rules/03-file-index-rules.md` | ファイルインデックス管理 |
| `docs/rules/04-git-rules.md` | Git 操作ルール（ブランチ禁止） |
| `docs/rules/05-model-usage.md` | モデル使い分け（Opus/Sonnet） |
| `docs/rules/06-deliverable-rules.md` | 成果物報告ルール |
| `docs/rules/07-execution-timeout.md` | 実行計画・タイムアウト対策・MCP push ファイル分割（≤250行） |
| `docs/rules/08-ec-app-roles.md` | EC L3コア3本（E1/E2/E3）の機能境界・重複禁止ルール |

---

## 1. Streamlit アプリ本体

### 1-1. ポータル

| ファイル | 概要 |
|---------|------|
| `app.py` | ML 予測コア（LightGBM + SHAP 回帰） |
| `streamlit_app.py` | 士業ポータル（11 アプリ統合） |
| `ec_app.py` | EC ポータル（7 アプリ統合） |

### 1-2. 士業向け（`apps/`）

| ファイル | 概要 |
|---------|------|
| `apps/shigyou-demo/app.py` | 顧問先離反予測デモ（LightGBM + SHAP + 逆 SHAP） |
| `apps/crosssell/app.py` | クロスセル分析 |
| `apps/payment-alert/app.py` | 入金遅延アラート |
| `apps/report-gen/app.py` | 月次レポート自動生成 |
| `apps/compliance-pack/app.py` | コンプライアンステンプレート集 |
| `apps/contract-draft/app.py` | 契約書ドラフト AI |
| `apps/doc-checker/app.py` | 申請書類チェッカー |
| `apps/service-lp/app.py` | サービス LP + AI 経営診断 |
| `apps/shigyou-office-dashboard/app.py` | 事務所経営ダッシュボード（L3） |
| `apps/shigyou-ltv/app.py` | LTV 予測＋不採算フラグ（L3） |
| `apps/shigyou-briefing/app.py` | 月次 AI ブリーフィング（L3） |

### 1-3. EC 向け（`apps/`）

| ファイル | 概要 |
|---------|------|
| `apps/ec-demo/app.py` | 顧客離脱予測 + 需要予測デモ |
| `apps/ec-dashboard/app.py` | 売上ダッシュボード |
| `apps/ec-rfm/app.py` | RFM 分析＋セグメンテーション |
| `apps/ec-ad-roi/app.py` | 広告 ROI 分析 |
| `apps/ec-executive-dashboard/app.py` | EC 経営ダッシュボード（L3、E1）|
| `apps/ec-executive-dashboard/helpers.py` | E1 タブ render 関数群（helpers.py+app.py 分割パターン） |
| `apps/ec-what-if/app.py` | What-If シミュレーター（L3、**⚠️ R²=0.74**） |
| `apps/ec-monthly-briefing/app.py` | 月次 AI ブリーフィング（L3、E3） |
| `apps/ec-monthly-briefing/helpers.py` | E3 タブ render 関数群（helpers.py+app.py 分割パターン） |

---

## 2. サンプルデータ

### 生成スクリプト
- `create_sample_data.py` / `create_sample_data_all.py`（ルート）
- `apps/*/create_sample_data.py`（各アプリ、15 本）

### CSV データ
- `sample_data/`（ルート、12 ファイル）
- `apps/*/sample_data/`（各アプリ、13+ ファイル）

---

## 3. 共通モジュール

| ファイル | 概要 |
|---------|------|
| `modules/__init__.py` | パッケージ初期化 |
| `modules/data_loader.py` | CSV/Excel 読み込み |
| `modules/evaluation.py` | RMSE/MAE/R² 算出 |
| `modules/model.py` | LightGBM 学習・予測 |
| `modules/shap_analysis.py` | SHAP 解析・可視化 |
| `apps/common/reverse_shap.py` | 逆 SHAP エンジン（Why→How） |

---

## 4. 設定ファイル

| パターン | 概要 |
|---------|------|
| `.streamlit/config.toml` / `apps/*/.streamlit/config.toml` | Streamlit 設定 |
| `requirements.txt` / `apps/*/requirements.txt` | 依存パッケージ |
| `packages.txt` / `apps/*/packages.txt` | システムパッケージ |
| `.python-version` / `.gitignore` / `.claude/settings.local.json` | 環境設定 |

---

## 5. ドキュメント（`docs/`）

### 5-1. 事業戦略ドキュメント

| ファイル | 概要 |
|---------|------|
| `docs/step1_usecase_catalog.md` | ユースケースカタログ |
| `docs/step2_monetization_scoring.md` | マネタイズスコアリング |
| `docs/step3_prioritization.md` | 優先順位付け |
| `docs/step4_marketing_strategy.md` | マーケティング戦略 |
| `docs/step5_strategy_review.md` | 戦略レビュー |
| `docs/step6_revised_strategy.md` | 改訂戦略 |
| `docs/step7_second_review.md` | 第 2 レビュー |
| `docs/index.html` | 戦略ドキュメント HTML |

### 5-2. 事業整合・品質

| ファイル | 概要 |
|---------|------|
| `docs/shigyou-business-alignment.md` | 士業 MVP × 事業計画整合 |
| `docs/ec-business-alignment.md` | EC MVP × 事業計画整合 |
| `docs/quality-scoring-rubric.md` | 5 軸 100 点品質採点基準 |
| `docs/improvement-backlog.md` | 改善バックログ |

### 5-3. 営業アセット（`docs/sales-assets/`）

詳細は [docs/sales-assets/README.md](https://github.com/KazuyaMurayama/MachineLearning_App/blob/main/docs/sales-assets/README.md) を参照。

| ファイル | ID | 用途 |
|---------|:--:|------|
| `pricing-and-scope.md` | SA-PRC | 料金 SSOT（⚠️ v0.3） |
| `pilot-proposal-template.md` | SA-PRO | パイロット提案書 |
| `demo-script-15min.md` | — | 15 分デモ |
| `demo-tech-checklist.md` | SA-DEMO | デモ技術チェックリスト |
| `roi-calculator.md` | SA-ROI | ROI 試算 |
| `pilot-contract-template.md` | SA-CNT | 契約雛形（法務レビュー要） |
| `objection-handling.md` | SA-OBJ | 反論対応 15 件 |
| `ringi-summary-template.md` | SA-RNG | 稟議サマリ |
| `outreach-email-templates.md` | SA-EMAIL | メールテンプレ 5 種 |
| `prospect-research-template.md` | SA-RSCH | 事前調査シート |
| `customer-pain-research.md` | SA-PAIN | ペイン仮説（**INTERNAL**） |
| `lead-list-framework.md` | SA-LEAD | リード獲得戦略（**INTERNAL**） |
| `_workspace/state.json` | — | 改善プロセス台帳 |

### 5-4. マルチエージェント改善履歴（`docs/task-improvement/`）

`00-master-plan.md` 〜 `09-final-report.md`（10 ファイル）+ `smoke-test-result.json`

### 5-5. セッション記録（`docs/sessions/`）

| ファイル | 概要 |
|---------|------|
| `2026-04-08-session-summary.md` | L3 実装・品質改善セッション |
| `2026-04-30-session-summary.md` | E1/E3 リファクタ・タイムアウト知見文書化 |

---

## 6. カスタムコマンド（`.claude/commands/`）

| ファイル | 概要 |
|---------|------|
| `mvp-plan.md` | MVP 企画 |
| `mvp-build.md` | MVP 実装 |
| `mvp-quality.md` | 5 軸 100 点採点 |
| `mvp-improve.md` | 4 エージェント並列改善 |

---

## 7. その他

| ファイル | 概要 |
|---------|------|
| `start_app.bat` | Windows 用起動バッチ |
| `setup_fonts.py` | 日本語フォントセットアップ |
| `generate_docs_html.py` | 戦略ドキュメント HTML 生成 |
