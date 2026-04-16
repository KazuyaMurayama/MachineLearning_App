# コンテキスト引継ぎガイド

> 新しいセッション開始時は、本ファイル → `docs/file-index.md` → `tasks.md` の順で読むこと。
> `CLAUDE.md` は最小ポインタのみ。詳細は本ファイル。
> 最終更新: 2026-04-16

## プロジェクトの本質

Streamlit + LightGBM + SHAP による、士業（税理士・社労士・行政書士）と EC 事業者向け AI 経営パートナー。現在は **L3 プレミアム機能**（月額 士業 ¥300k / EC ¥260k）のパイロット顧客獲得フェーズ。

- 目標: 最初の 5 社パイロット契約
- 現状: パイロット実績 0 社、営業資料一式を整備完了

## ブランチ戦略

| ブランチ | 役割 |
|---------|------|
| `main` | 公開用。基盤コードと公開用ドキュメントのみ |
| `claude/integrate-business-plan-IBKFu` | L3 アプリ本体 + 事業整合ドキュメントの統合ブランチ |
| `claude/organize-repo-by-date-VNw9E` | 営業アセット改善ラウンド（現行作業ブランチ） |

- 現行 PR: #2 (`claude/organize-repo-by-date-VNw9E` → `claude/integrate-business-plan-IBKFu`)
- 次: #2 マージ後、`claude/integrate-business-plan-IBKFu` → `main` の PR を作成

## 重要な不変条件（全員必読）

1. **`docs/sales-assets/pricing-and-scope.md` が料金の SSOT**: 他ファイルに料金を書く場合は必ず整合を取る。
2. **ec-what-if の R²=-0.16**: 精度再検証中。予測値を確定値として顧客提示禁止。対応は `docs/sales-assets/objection-handling.md` D-2/D-3。
3. **パイロット実績 0 社**: 「導入事例あり」「導入済企業あり」を示唆する表現は全資料で禁止。
4. **`customer-pain-research.md` の数値は全て仮説**: 営業資料に引用時は「仮説」マーカー必須。
5. **`lead-list-framework.md` の既存人脈 60% 前提は接点 0 段階では無効**: ゼロ接点アウトリーチ戦略の策定が必要（`tasks.md` 参照）。
6. **データ処理は ホステッド環境で実施**: 「ローカル処理のためクラウド送信されない」系の表現は虚偽になるので禁止。

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

| 原因 | 対策 |
|------|------|
| MCP 切断の突発性 | プロービング: 書き込み前に軽量 read で接続確認 |
| push_files 応答遅延 | 圧縮: 1 ファイル ≤ 4KB 目標、最大 8KB |
| 複数ファイル並列送信の詰まり | 完全直列: `create_or_update_file` で 1 ファイルずつ |
| 書き込み成功の不確実性 | read verify: push 後にファイルを read して SHA 変化を確認 |
| 失敗時の即再送 | 段階的: 失敗 → 待機 → 再 probe → 再送 |

## セッション終了時の手順

1. `tasks.md` の「次にやる」「完了」を更新
2. 重大変更時は `docs/sessions/YYYY-MM-DD-session-summary.md` を追加
3. 新規ファイル作成・大幅変更時は `docs/file-index.md` を更新
4. コミット → push → 必要なら PR 更新 → 本ファイル「最終更新」日付を更新

## 参照すべき外部ドキュメント

- 営業アセット全体: `docs/sales-assets/README.md`
- 事業整合: `docs/shigyou-business-alignment.md` / `docs/ec-business-alignment.md`
- 改善プロセス履歴: `docs/task-improvement/00-master-plan.md` 〜 `09-final-report.md`
- 品質採点基準: `docs/quality-scoring-rubric.md`
- 改善バックログ: `docs/improvement-backlog.md`
- 前回セッション要約: `docs/sessions/2026-04-08-session-summary.md`
- L3 アプリ群: `apps/shigyou-*/`, `apps/ec-*/`, 共通モジュール `apps/common/reverse_shap.py`

## よくある質問

**Q. 新しいアプリを追加したい**
→ `.claude/commands/mvp-plan.md` → `mvp-build.md` のフローに従う。サンプルデータ生成スクリプト + `apps/<name>/app.py` + `requirements.txt` + `packages.txt` の 4 点セット。

**Q. 営業資料の料金を変更したい**
→ `pricing-and-scope.md` を先に更新 → 他ファイルを整合させる。「Standard 月額」「パイロット期間合計」を混同しない。

**Q. セッションがタイムアウトした**
→ 上記「API Stream idle timeout 対策」を厳格に適用。1 回の送信サイズを半分以下にし、`create_or_update_file` に切り替える。
