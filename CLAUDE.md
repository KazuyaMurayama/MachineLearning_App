# CLAUDE.md

> 本ファイルは軽量・最小限に保つ。詳細ルールは `docs/rules/` に分散。

## セッション開始時に必ず読むファイル

1. **`docs/file-index.md`** — リポジトリ全ファイルの索引
2. **`docs/context-handoff.md`** — 現行状況・不変条件・戦略整合・撤退基準
3. **`tasks.md`** — セッション間引継ぎタスク（次にやること）
4. **`docs/sessions/`** — 日付別セッション要約（最新を先に読む）

## ルール（`docs/rules/` を必ず遵守）

| # | ファイル | 内容 |
|:-:|---------|------|
| 01 | `docs/rules/01-response-rules.md` | 回答の基本ルール（要約先行・客観的・選択肢+推奨） |
| 02 | `docs/rules/02-task-management.md` | tasks.md 一元管理・細分化・即時保存 |
| 03 | `docs/rules/03-file-index-rules.md` | file-index.md 網羅性・優先度明示 |
| 04 | `docs/rules/04-git-rules.md` | **ブランチ作成禁止**・main 直接コミット |
| 05 | `docs/rules/05-model-usage.md` | Opus=計画/分析、Sonnet=実行/サブタスク |
| 06 | `docs/rules/06-deliverable-rules.md` | 成果物は GitHub ハイパーリンクで報告 |
| 07 | `docs/rules/07-execution-timeout.md` | タイムアウト対策・チェックポイント設計 |

## プロジェクト概要

Streamlit + LightGBM + SHAP による、士業 / EC 向け AI 経営パートナー。L3 パイロット顧客獲得フェーズ。

- 士業ポータル: `streamlit_app.py` / EC ポータル: `ec_app.py` / ML コア: `app.py`

## 開発コマンド

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py  # 士業
streamlit run ec_app.py         # EC
```

## 不変条件（詳細は `docs/context-handoff.md`）

- `pricing-and-scope.md` が料金 SSOT（⚠️ L3 ¥30万は v2 上限 ¥25万 を超過、要確定）
- ec-what-if R²=-0.16（精度再検証中）
- パイロット実績 0 社
