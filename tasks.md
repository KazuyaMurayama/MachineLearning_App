# タスク（セッション間引継ぎ用ランニングリスト）

> 最終更新: 2026-04-16
> ベースブランチ: `main`（PR #2, #3 マージ完了）
> 作業ブランチ: `claude/review-repo-docs-2nBuQ`
> 関連リポ: `kazuyamurayama/freelance-compass`（上流＝事業戦略）
> **🟢 最新戦略**: [freelance-compass/outputs/integrated-business-plan-v2.md](https://github.com/KazuyaMurayama/freelance-compass/blob/claude/review-repo-docs-2nBuQ/outputs/integrated-business-plan-v2.md)（2026-03-25、分割保存）

## 起動時チェックリスト

1. `docs/file-index.md` を読む
2. `docs/context-handoff.md` を読む
3. 本ファイルの「次にやる」を確認
4. `docs/sessions/2026-04-08-session-summary.md`（前セッション要約）を確認
5. **`freelance-compass/outputs/integrated-business-plan-v2.md`（最新戦略 INDEX）と `freelance-compass/tasks.md` を確認**

---

## 戦略整合性ステータス（v2 = 2026-03-25）

| 項目 | v2 | 本リポ実装 | 整合 |
|---|---|---|---|
| 初期ターゲット | 士業 + 小売/EC | 士業 11本 + EC 7本 | ✅ |
| L3 価格 士業 | ¥20万 | ¥20万（v0.3 で ¥30万→¥20万） | ✅ |
| L3 価格 EC | ¥25万 | ¥25万（v0.3 で ¥26万→¥25万） | ✅ |
| パイロット 士業 | — | ¥10万/6週間（v0.3 で ¥15万→¥10万） | ✅ |
| パイロット EC | — | ¥12.5万/6週間（v0.3 で ¥12万→¥12.5万） | ✅ |
| 年間LTV 士業 | ¥2.4M | ¥2.4M（v0.3） | ✅ |
| 年間LTV EC | ¥3.0M | ¥3.0M（v0.3） | ✅ |

> 戦略バージョン履歴: v9.0（士業+クリニック）→ v29.0（EC+クリニック）→ **v2（士業+小売/EC）= 最新**

---

## 次にやる（優先度順）

### 🔴 P0: 価格変更の全ファイル波及監査（v0.3 反映必須）

`pricing-and-scope.md` v0.3 で L3 価格を変更したため、他ファイルに旧価格が残存している可能性。**以下を順に監査し、v0.3 と整合しない箇所を修正**:

- [ ] `docs/sales-assets/pilot-proposal-template.md`
- [ ] `docs/sales-assets/demo-script-15min.md`
- [ ] `docs/sales-assets/roi-calculator.md`
- [ ] `docs/sales-assets/ringi-summary-template.md`
- [ ] `docs/sales-assets/outreach-email-templates.md`
- [ ] `docs/sales-assets/objection-handling.md`
- [ ] `docs/shigyou-business-alignment.md` — v2 ベースに更新
- [ ] `docs/ec-business-alignment.md` — v2 ベースに更新

### 🟠 P1: Go-to-Market 実行（v2 Phase 0 = M1=2026年5月）

freelance-compass v2 Phase 0 と本リポのパイロット獲得を統合。

- [ ] **最初の 5社ヒアリング**（士業 3 + EC 2、`docs/sales-assets/` 一式を活用）
- [ ] **初回有料契約 1社**（v2 Phase 0 完了条件 M3末、L1 スポット or L2 PoC）
- [ ] **ゼロ接点アウトリーチ チャネル立ち上げ**
  - [ ] ビザスクエキスパート登録
  - [ ] ココナラ出品（¥5,000 診断レポート）
  - [ ] Shopify Partner 申請（審査 1-3ヶ月）
  - [ ] note / X 記事 3本公開
  - [ ] 士業向けウェビナー開催（M3, 参加目標 15名）
  - 成果物: `docs/sales-assets/zero-to-one-outreach-playbook.md`（新規）
- [ ] **A1 診断ツール**（freelance-compass `tools/a1_diagnostic/`）の本リポ統合可否を検討

### 🟡 P2: プロトタイプの商業化準備

- [ ] **Streamlit Cloud デプロイ状況の確認** — 2026-04-08 セッションで P0 だが進捗追跡漏れ。L3 6本がデプロイ済みか確認
- [ ] **ec-what-if モデルの本質的精度改善** — 現状は `np.clip(0.0, 0.95)` 応急処置 + 警告バナーのみ。R²=-0.16 は未解決。特徴量エンジニアリング or 問題設定の見直しが必要
- [ ] **`pilot-contract-template.md` 法務レビュー**（社内 1 周 → 弁護士）
- [ ] **稼働時間記録運用の開始**（v2 時給 ¥30K/h KPI 算出のため）

### 🟢 P3: 技術負債・運用基盤（パイロット獲得後）

2026-04-08 P2 だったが tasks.md から消失していた項目を再登録。

- [ ] **改善バックログ消化**（`docs/improvement-backlog.md` 🔴最優先残）— ec-dashboard へ ML予測+SHAP 追加
- [ ] **CI/CD 構築** — GitHub Actions で `scripts/smoke_test.py` 自動実行 + pytest 導入
- [ ] **共通ライブラリ化検討** — `setup_japanese_font()` 等 18アプリで重複
- [ ] **EC 3アプリの共通マスター seed 統合**
- [ ] **テンプレート化（v2 Part 3）** — 1社あたり対応 3h → 0.7h（M24）への圧縮設計

---

## 進行中

- なし

---

## 完了（直近）

- 2026-04-16: **`pricing-and-scope.md` を v0.3 に更新**（L3 士業 ¥300k→¥200k / EC ¥260k→¥250k、パイロット・LTV も整合）。§1 に v2 L1/L2/L3 層構造、§4 に v2 L1/L2 相当スポットを追加。§10 に他ファイル監査タスクを明示
- 2026-04-16: **戦略整合性確認完了**。freelance-compass の最新戦略 v2 (士業+小売/EC, 2026-03-25) を発見、本リポの実装と価格が整合済み。tasks.md / context-handoff.md から「士業 vs クリニック」アラートを撤回
- 2026-04-16: **main への 2 段階マージ完了**（PR #2, #3）
- 2026-04-16: `tasks.md`・`docs/context-handoff.md` 新規作成、`CLAUDE.md` 最小化、`docs/file-index.md` 更新
- 2026-04-09: 営業アセット改善ラウンド（新規 7 + 改善 2 + 5 批評者レビュー）
- 2026-04-08: L3 キラー機能実装（士業 3 + EC 3）、マルチエージェント品質改善
  - **要注意**: このセッションの P0「Streamlit Cloud デプロイ」「初回ヒアリング」進捗は不明

---

## 既知のリスク

- 🔴 `ec-what-if` 予測精度 R²=-0.16（応急処置のみ、本質未解決）
- 🔴 パイロット実績 0 社 — v2 Phase 0 完了条件（M3末有料契約1社）未達成
- 🟠 価格変更の他ファイル波及未監査（P0 で対応中）
- 🟠 `pilot-contract-template.md` 法務レビュー未完了
- 🟠 既存人脈 0 段階のリード獲得戦略が未確立
- 🟠 2026-04-08 P0 項目（デプロイ・初回ヒアリング）の追跡漏れ

---

## 撤退基準（v2 Part 6）

| 条件 | 判定時期 |
|---|---|
| 有料顧客 0社 | M6末 |
| MRR ¥10万未満 | M12末 |
| 実測時給 ¥15,000/h未満 | M12末 |
| 累計利益マイナス | M18末 |

---

## 次セッションへの申し送り

1. **戦略・価格ともに v2 で確定・整合済み**。古い v9.0/v29.0 を引用しないこと
2. P0 は pricing-and-scope 変更の他ファイル波及監査。v0.3 との整合を1ファイルずつ確認する
3. v2 の M1=2026年5月 開始に向け、P1 GTM チャネルを今月中に準備
4. 「技術 100点 でも 顧客 0社 なら MRR ¥0」— v2 の Phase 0 完了条件「初回有料契約 1社」が KPI
