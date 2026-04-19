# タスク（セッション間引継ぎ用ランニングリスト）

> 最終更新: 2026-04-19
> ブランチ: `main`（ブランチ作成は禁止、`docs/rules/04-git-rules.md` 参照）
> 関連リポ: `kazuyamurayama/freelance-compass`（上流＝事業戦略）
> 最新戦略: [freelance-compass/outputs/integrated-business-plan-v2.md](https://github.com/KazuyaMurayama/freelance-compass/blob/claude/review-repo-docs-2nBuQ/outputs/integrated-business-plan-v2.md)（2026-03-25）

## 起動時チェックリスト

1. `CLAUDE.md` を読む（ルール参照テーブル）
2. `docs/file-index.md` を読む（全ファイル索引）
3. `docs/context-handoff.md` を読む（不変条件・戦略整合）
4. `docs/rules/` を全て読む（行動ルール 7 本）
5. 本ファイルの「次にやる」を確認
6. `docs/sessions/` の最新要約を確認
7. `freelance-compass/tasks.md` と突き合わせ（戦略ドリフト検出）

---

## 戦略整合性ステータス（v2 = 2026-03-25）

| 項目 | v2 | 本リポ実装 | 整合 |
|---|---|---|---|
| 初期ターゲット | 士業 + 小売/EC | 士業 11本 + EC 7本 | ✅ |
| L3 価格 士業 | ¥20万 | ¥20万（v0.3） | ✅ |
| L3 価格 EC | ¥25万 | ¥25万（v0.3） | ✅ |
| パイロット 士業 | — | ¥10万/6週間（v0.3） | ✅ |
| パイロット EC | — | ¥12.5万/6週間（v0.3） | ✅ |

> 戦略バージョン: v9.0（旧）→ v29.0（中間）→ **v2 = 最新**

---

## 次にやる（優先度順）

### 🔴 P0: 価格変更の全ファイル波及監査（v0.3 反映必須）

`pricing-and-scope.md` v0.3 で L3 価格を変更。他ファイルに旧価格が残存の可能性:

- [ ] `docs/sales-assets/pilot-proposal-template.md`
- [ ] `docs/sales-assets/demo-script-15min.md`
- [ ] `docs/sales-assets/roi-calculator.md`
- [ ] `docs/sales-assets/ringi-summary-template.md`
- [ ] `docs/sales-assets/outreach-email-templates.md`
- [ ] `docs/sales-assets/objection-handling.md`
- [ ] `docs/shigyou-business-alignment.md` — v2 ベースに更新
- [ ] `docs/ec-business-alignment.md` — v2 ベースに更新

### 🟠 P1: Go-to-Market 実行（v2 Phase 0 = M1=2026年5月）

- [ ] **最初の 5社ヒアリング**（士業 3 + EC 2）
- [ ] **初回有料契約 1社**（v2 Phase 0 完了条件 M3末）
- [ ] **ゼロ接点アウトリーチ チャネル立ち上げ**
  - [ ] ビザスクエキスパート登録
  - [ ] ココナラ出品（¥5,000 診断レポート）
  - [ ] Shopify Partner 申請
  - [ ] note / X 記事 3本公開
  - [ ] 士業向けウェビナー開催（M3, 参加目標 15名）
  - 成果物: `docs/sales-assets/zero-to-one-outreach-playbook.md`

### 🟡 P2: プロトタイプの商業化準備

- [ ] Streamlit Cloud デプロイ状況確認（L3 6本）
- [ ] ec-what-if R²=-0.16 の本質的精度改善
- [ ] `pilot-contract-template.md` 法務レビュー
- [ ] 稼働時間記録運用開始（v2 時給 KPI 用）

### 🟢 P3: 技術負債（パイロット獲得後）

- [ ] 改善バックログ消化（`docs/improvement-backlog.md`）
- [ ] CI/CD 構築（GitHub Actions + pytest）
- [ ] 共通ライブラリ化
- [ ] テンプレート化（v2 Part 3: 1社 3h→0.7h）

---

## 進行中

- なし

---

## 完了（直近）

- 2026-04-19: **リポジトリルール整備** — `docs/rules/` 7本作成、CLAUDE.md をルール参照構造に再構築、tasks.md / file-index.md を新ルール反映版に更新。全ブランチ→main 集約確認済み
- 2026-04-16: `pricing-and-scope.md` v0.3 更新、戦略整合性確認完了、main への 2段階マージ完了
- 2026-04-09: 営業アセット改善ラウンド（新規 7 + 改善 2 + 5 批評者レビュー）
- 2026-04-08: L3 キラー機能実装（士業 3 + EC 3）

---

## 既知のリスク

- 🔴 `ec-what-if` R²=-0.16（応急処置のみ、本質未解決）
- 🔴 パイロット実績 0 社 — v2 Phase 0 完了条件（M3末有料契約1社）未達成
- 🟠 価格変更の他ファイル波及未監査（P0）
- 🟠 `pilot-contract-template.md` 法務レビュー未完了
- 🟠 既存人脈 0 段階のリード獲得戦略が未確立

---

## 撤退基準（v2 Part 6）

| 条件 | 判定時期 |
|---|---|
| 有料顧客 0社 | M6末 |
| MRR ¥10万未満 | M12末 |
| 実測時給 ¥15,000/h未満 | M12末 |
| 累計利益マイナス | M18末 |
