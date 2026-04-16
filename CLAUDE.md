# CLAUDE.md

> このファイルは最小限に保つ。詳細は外部ファイルに分離している（下記参照）。

## セッション開始時に必ず読むファイル

1. **`docs/file-index.md`** — リポジトリ全ファイルの索引。どこに何があるかはまずここで特定する。
2. **`docs/context-handoff.md`** — 現行状況・重要な不変条件・マルチエージェントパターン・API タイムアウト対策・セッション終了手順。
3. **`tasks.md`** — セッション間引継ぎタスクリスト（次にやること）。
4. **`docs/sessions/`** — 日付別セッション要約。最新日付を先に参照。

## プロジェクト概要

Streamlit + LightGBM + SHAP による、士業 / EC 事業者向け AI 経営パートナー。L3 プレミアム機能（月額 士業 ¥300k / EC ¥260k）のパイロット顧客獲得フェーズ。

- 士業ポータル: `streamlit_app.py`
- EC ポータル: `ec_app.py`
- ML 予測コア: `app.py`
- 共通モジュール: `modules/`, `apps/common/`

## 開発コマンド

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py  # 士業ポータル
streamlit run ec_app.py         # EC ポータル
streamlit run app.py            # ML 予測コア
```

## 開発規約（最低限）

- 新規ファイル作成・大幅変更時は `docs/file-index.md` を更新する
- 重要セッション終了時は `docs/sessions/YYYY-MM-DD-session-summary.md` を追加する
- 進行中/完了タスクは `tasks.md` に反映する
- 詳細規約・ML 実装パターン・品質採点は `docs/context-handoff.md` 経由でリンク先を参照
- 本ファイル（CLAUDE.md）は最小限に保つ。詳細は `docs/context-handoff.md` に追記する

## カスタムスキルコマンド

`.claude/commands/` 配下: `/mvp-plan`, `/mvp-build`, `/mvp-quality`, `/mvp-improve`
（MVP 企画 → 実装 → 品質採点 → 4 エージェント並列改善）

## 重要な不変条件（詳細は `docs/context-handoff.md`）

- `docs/sales-assets/pricing-and-scope.md` が料金の SSOT
- ec-what-if モデルは R²=-0.16（精度再検証中）。顧客提示は `docs/sales-assets/objection-handling.md` D-2/D-3 を参照
- パイロット実績 0 社。「導入事例あり」を示唆する表現は禁止
