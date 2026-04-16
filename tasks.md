# タスク（セッション間引継ぎ用ランニングリスト）

> 最終更新: 2026-04-16
> 現行ブランチ: `claude/organize-repo-by-date-VNw9E`
> 現行 PR: `KazuyaMurayama/MachineLearning_App#2` (→ `claude/integrate-business-plan-IBKFu`)

## 起動時チェックリスト（新しいセッションで最初にやる）

1. `docs/file-index.md` を読む（リポジトリ全ファイルの索引）
2. `docs/context-handoff.md` を読む（現行状況・不変条件・エージェントパターン）
3. `docs/sessions/` の最新要約を読む
4. 本ファイルの「次にやる」を確認

## 次にやる（優先度順）

- [ ] **最初の 5 社ヒアリング実行**: `docs/sales-assets/` 一式を活用し、ユーザー負荷を最小化するため初期連絡メール・事前調査・当日質問票を Claude で自動生成する。
- [ ] **ゼロ接点アウトリーチ戦略策定・実行**: `docs/sales-assets/lead-list-framework.md` は既存人脈 60% 前提のため、接点 0 段階の認知獲得チャネル（freee/MF/Shopify アプリストア、税務通信/ECzine、税理士会連合会、Web 広告、PR TIMES 等）を設計。成果物は `docs/sales-assets/zero-to-one-outreach-playbook.md` として保存予定。
- [ ] **`pilot-contract-template.md` 法務レビュー**: 弁護士レビュー前に社内チェック 1 周。
- [ ] **ec-what-if の R²=-0.16 精度再検証**: 特徴量エンジニアリングまたは問題設定を見直す。
- [ ] **main への反映経路整理**: PR #2 を `claude/integrate-business-plan-IBKFu` にマージ → さらに `main` への PR を作成。重要ファイル（`CLAUDE.md`、`docs/file-index.md`、`tasks.md`、`docs/context-handoff.md`）が main に到達していることを確認する。

## 進行中

- なし

## 完了（直近）

- 2026-04-16: `tasks.md` 新規作成、`docs/context-handoff.md` 新規作成、`CLAUDE.md` 最小化、`docs/file-index.md` を sales-assets 等反映版に更新
- 2026-04-09: 営業アセット改善ラウンド（新規 7 ファイル + 既存 2 ファイル改善 + 5 批評者レビュー）
- 2026-04-08: L3 キラー機能実装（士業 3 app + EC 3 app）、マルチエージェント品質改善プロセス実施

## 既知のリスク（詳細は `docs/context-handoff.md`）

- `ec-what-if` 予測精度 R²=-0.16
- パイロット実績 0 社
- `pilot-contract-template.md` 法務レビュー未完了
- 既存人脈 0 の段階でのリード獲得戦略が未確立
