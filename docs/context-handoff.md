# コンテキスト引継ぎガイド

> 新しいセッション開始時は、本ファイル → `docs/file-index.md` → `tasks.md` の順で読むこと。
> `CLAUDE.md` は最小ポインタのみ。詳細は本ファイル。
> 最終更新: 2026-04-30

## 関連リポジトリ（必ず一緒に読む）

本リポは `kazuyamurayama/freelance-compass` で決定された事業戦略の**実装側**。

| リポ | 役割 | 主要ファイル |
|------|------|------------|
| `freelance-compass` | 上流：事業戦略・意思決定（6エージェント） | **`outputs/integrated-business-plan-v2.md` (v2、2026-03-25 改訂、最新)** on `claude/integrated-business-plan` ブランチ、`tasks.md` |
| 本リポ | 下流：18 Streamlit アプリの実装と顧客獲得 | 本ファイル、`tasks.md` |

セッション開始時は **両リポの `tasks.md` を必ず突き合わせる**。戦略ドリフトの早期発見が目的。

> ⚠️ `freelance-compass/outputs/recommendation.md` は v9.0（士業+クリニック、旧版）または v29.0（EC+クリニック、中間版）。**最新は integrated v2（士業+小売/EC）で本リポ実装と整合済み**。

## プロジェクトの本質

Streamlit + LightGBM + SHAP による、士業（税理士・社労士・行政書士）と EC 事業者向け AI 経営パートナー。**L3 プレミアム機能**（月額 士業 ¥300k / EC ¥260k）のパイロット顧客獲得フェーズ。

- 目標: v2 Phase 0 完了条件 = M1=2026年5月開始 → M3末 有料契約 1社
- 現状: パイロット実績 0 社、営業資料一式は整備完了
- v2 の 24ヶ月期待値: M24 MRR ¥97万 / 累計利益 ¥1,210万 / 時給 ¥46,700/h

## ブランチ戦略

| ブランチ | 役割 |
|---------|------|
| `main` | 公開用。基盤コードと公開用ドキュメントのみ。PR #2/#3 マージ済み |
| `claude/integrate-business-plan-IBKFu` | L3 アプリ本体 + 事業整合ドキュメントの統合ブランチ |
| `claude/organize-repo-by-date-VNw9E` | 営業アセット改善ラウンド |
| `claude/review-repo-docs-2nBuQ` | 戦略整合性レビュー・tasks.md/context-handoff.md 再構成 |

## 重要な不変条件（全員必読）

0. ✅ **戦略 vs 実装の整合**: freelance-compass v2 (2026-03-25) で「士業 + 小売/EC」が確定、本リポ実装と整合済み。古い v9.0 (士業+クリニック) や v29.0 (EC+クリニック) を引用しないこと。
1. **`docs/sales-assets/pricing-and-scope.md` が料金の SSOT**: 他ファイルに料金を書く場合は必ず整合を取る。⚠️ ただし本リポの L3 ¥30万 は v2 の L3 上限 ¥25万 を超過。要確定（`tasks.md` P0）。
2. **ec-what-if の R²=0.74**: 2026-04-19 改善済み（サンプルデータ再設計）。予測値を確定値として顧客提示禁止。
3. **パイロット実績 0 社**: 「導入事例あり」「導入済企業あり」を示唆する表現は全資料で禁止。v2 Phase 0 完了条件は「M3末 有料契約 1社」。
4. **`customer-pain-research.md` の数値は全て仮説**: 営業資料に引用時は「仮説」マーカー必須。
5. **`lead-list-framework.md` の既存人脈 60% 前提は接点 0 段階では無効**: ゼロ接点アウトリーチ戦略の策定が必要（`tasks.md` P1）。
6. **データ処理は ホステッド環境で実施**: 「ローカル処理のためクラウド送信されない」系の表現は虚偽になるので禁止。

## v2 で定義された撤退基準（Kill Criteria）

| 条件 | 判定時期 |
|---|---|
| 有料顧客 0社 | M6末 |
| MRR ¥10万未満 | M12末 |
| 実測時給 ¥15,000/h未満 | M12末 |
| 累計利益マイナス | M18末 |
| 紹介 0件 | M24末 |

## マルチエージェント改善パターン

品質改善ラウンド時のロール構成:

| ロール | 役割 |
|-------|------|
| Orchestrator（= セッション担当 AI） | 全体調整、コミット、state.json 更新 |
| Diagnostician | 既存資料の問題点洗い出し |
| FactChecker | 事実誤認・法令違反チェック |
| Writer A/B | 新規・改訂の執筆（並列可） |
| Critic ×5 | Sales Effectiveness / Legal & Risk / Customer Devil's Advocate / Cross-Doc Consistency / GTM Strategy |
| Integrator | Critics 指摘の統合・優先順位付け |

進行状態は `docs/sales-assets/_workspace/state.json` に checkpoint 形式で記録。

## API Stream idle timeout 対策（必須）

詳細は `docs/rules/07-execution-timeout.md` を参照。

| 原因 | 対策 |
|------|------|
| MCP 切断の突発性 | プロービング: 書き込み前に軽量 read で接続確認 |
| 大ファイル push | 分割: **1 ファイル ≤ 250行 / ≤ 2,500トークン**（helpers.py+app.py パターン） |
| 複数ファイル並列送信の詰まり | 完全直列: `create_or_update_file` で 1 ファイルずつ |
| 書き込み成功の不確実性 | read verify: push 後にファイルを read して SHA 変化を確認 |
| 失敗時の即再送 | 段階的: 失敗 → 待機 → 再 probe → 再送 |

> ⚠️ サブエージェント委譲では解決しない（同じ LLM 生成速度のため）。ファイル分割が唯一の根本解決策。

## セッション終了時の手順

1. `tasks.md` の「次にやる」「完了」を更新
2. **freelance-compass 側に影響する戦略変化があれば同リポの `tasks.md` も更新**
3. 重大変更時は `docs/sessions/YYYY-MM-DD-session-summary.md` を追加
4. 新規ファイル作成・大幅変更時は `docs/file-index.md` を更新
5. コミット → push → 必要なら PR 更新 → 本ファイル「最終更新」日付を更新

## 参照すべき外部ドキュメント

- 営業アセット全体: `docs/sales-assets/README.md`
- 事業整合: `docs/shigyou-business-alignment.md` / `docs/ec-business-alignment.md`（**v2 ベースに更新が必要**、`tasks.md` P0）
- 改善プロセス履歴: `docs/task-improvement/00-master-plan.md` 〜 `09-final-report.md`
- 品質採点基準: `docs/quality-scoring-rubric.md`
- 改善バックログ: `docs/improvement-backlog.md`
- 最新セッション要約: `docs/sessions/2026-04-30-session-summary.md`
- L3 アプリ群: `apps/shigyou-*/`, `apps/ec-*/`, 共通モジュール `apps/common/reverse_shap.py`
- **上流リポ最新戦略**: `freelance-compass/outputs/integrated-business-plan-v2.md` (v2、2026-03-25)、`freelance-compass/tasks.md`

## よくある質問

**Q. 新しいアプリを追加したい**
→ `.claude/commands/mvp-plan.md` → `mvp-build.md` のフローに従う。サンプルデータ生成スクリプト + `apps/<name>/app.py` + `requirements.txt` + `packages.txt` の 4 点セット。**ターゲットは v2 で士業 or 小売/EC に確定済み**（クリニックは追加不要）。

**Q. 営業資料の料金を変更したい**
→ `pricing-and-scope.md` を先に更新 → 他ファイルを整合させる。「Standard 月額」「パイロット期間合計」を混同しない。**v2 の L1 ¥5万 / L2 ¥10-12万 / L3 ¥20-25万 とも要整合**。本リポ L3 ¥30万 が v2 上限超過のため要決定。

**Q. セッションがタイムアウトした**
→ `docs/rules/07-execution-timeout.md` の「ファイル分割パターン」を参照。1 ファイル ≤ 250行に分割し `create_or_update_file` で直列 push する。

**Q. 戦略文書を引用したいが、どれが最新か分からない**
→ **v2 (`freelance-compass/outputs/integrated-business-plan-v2.md`、2026-03-25)** が最新。v9.0 / v29.0 は古い。混乱したら `freelance-compass/tasks.md` の「戦略バージョン履歴」表を参照。
