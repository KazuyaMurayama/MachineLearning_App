# 営業アセット (Sales Assets)

L3パイロット顧客獲得（士業・EC 各業種）のための営業資料を格納するディレクトリ。

本ディレクトリの改善は、2026-04-09 のマルチエージェント改善ラウンド（Orchestrator + Diagnostician + FactChecker + Writer×2 + Reviewer + Integrator）で実施しました。進行状態は `_workspace/state.json` を参照してください。

## 含まれるファイル

### 既存アセット（修正済み）

| ファイル | 用途 | 状態 |
|---------|------|------|
| [`pilot-proposal-template.md`](./pilot-proposal-template.md) | パイロット運用提案書（士業版・EC版） | v0.1 / プレースホルダー要置換 |
| [`demo-script-15min.md`](./demo-script-15min.md) | 15分デモスクリプト | v0.2 / ec-what-if R²=-0.16 への誠実対応版 |

### 新規アセット（2026-04-09 追加）

| ファイル | 用途 | 文書ID |
|---------|------|--------|
| [`pricing-and-scope.md`](./pricing-and-scope.md) | 料金・プラン・スコープ・SLAの単一情報源 | SA-PRC-001 |
| [`roi-calculator.md`](./roi-calculator.md) | 商談クロージング用ROI試算ワークシート（業種別） | SA-ROI-001 |
| [`pilot-contract-template.md`](./pilot-contract-template.md) | パイロット契約雛形（正式契約前に法務レビュー必須） | SA-CNT-001 |
| [`demo-tech-checklist.md`](./demo-tech-checklist.md) | デモ技術チェックリスト・遅延改善ロードマップ | SA-DEMO-001 |
| [`objection-handling.md`](./objection-handling.md) | 反論対応ハンドブック（5カテゴリ15件、4段階フレームワーク） | SA-OBJ-001 |
| [`customer-pain-research.md`](./customer-pain-research.md) | 顧客ペイン仮説マップとヒアリング設計（全項目未検証） | SA-PAIN-001 |
| [`lead-list-framework.md`](./lead-list-framework.md) | リード獲得4チャネル戦略・ICP・BANT・30日ロードマップ | SA-LEAD-001 |

### 内部管理

| ファイル | 用途 |
|---------|------|
| [`_workspace/state.json`](./_workspace/state.json) | 改善プロセス進捗台帳（マルチエージェントプロセス） |

## 文書間の参照関係

```
pricing-and-scope.md ────┐
                         ├──→ pilot-proposal-template.md
pilot-contract-template.md ─┘
                         │
customer-pain-research.md ──→ objection-handling.md ──→ demo-script-15min.md
                         │                                     │
                         └──→ lead-list-framework.md            │
                                                                │
                              demo-tech-checklist.md ◀──────────┘

roi-calculator.md ──→ pilot-proposal-template.md
```

## 使い方（改訂版）

### 1. リード発掘フェーズ
- `lead-list-framework.md` でICPとチャネル戦略を確認
- `customer-pain-research.md` の仮説マップで想定ペインを事前学習（仮説段階であることに留意）

### 2. ヒアリングフェーズ
- `customer-pain-research.md` の15問ヒアリングテンプレートを使用
- 結果は同書の記録フォーマットに蓄積

### 3. デモフェーズ
- **必ず先に** `demo-tech-checklist.md` の24時間前・1時間前チェックを実施
- `demo-script-15min.md` を使用（ec-what-if R²=-0.16 の扱いに注意）
- 反論が出た場合は `objection-handling.md` を即参照

### 4. 提案フェーズ
- `pilot-proposal-template.md` の該当業種セクションを使用
- ROI試算は `roi-calculator.md` を顧客と一緒に埋める
- 料金根拠は `pricing-and-scope.md` と必ず整合

### 5. クロージングフェーズ
- 契約条件の素案提示には `pilot-contract-template.md` を参照
- **正式契約前に必ず法務レビュー**

## 既知の重要事項（全担当者共有）

1. **ec-what-if モデルは R²=-0.16 と精度再検証中**です。数値予測を確定値として提示しないでください。詳細対応は `objection-handling.md` D-2/D-3 を参照。
2. **パイロット実績は現時点0社**です。「導入事例あり」を示唆する表現は禁止。「最初の5社」優位性として誠実に語ってください。
3. **`customer-pain-research.md` の数値は全て仮説**です。出典なしに営業資料で引用しないでください。
4. 料金・スコープの変更は必ず `pricing-and-scope.md` を更新し、関連ドキュメントと整合を取ってください。

## 変更履歴

| 日付 | 変更内容 | 担当 |
|------|---------|------|
| 2026-04-09 | 営業アセット改善ラウンド実施。新規7ファイル追加、`demo-script-15min.md` を R²=-0.16 誠実対応版へ更新、本READMEを全面改訂 | Orchestrator + Writer A/B |
| 2026-04-08以前 | 初期版（`pilot-proposal-template.md` + `demo-script-15min.md` のみ） | Sales Ops |
