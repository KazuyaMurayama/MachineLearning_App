# MachineLearning_App — Claude Code 運用ルール

Streamlit + LightGBM ベースの回帰予測アプリケーション。CSV/Excel をアップロードし、機械学習モデルを構築・予測を行う Web アプリ。

> **本ファイルは VSCode版 / Web版 Claude Code（claude.ai）の両方で本リポジトリの単独完結ガイド**。
> Web版はグローバル `~/.claude/CLAUDE.md` を参照しない前提で、本リポの運用に必要な全ルールをここに集約。

> 本ファイルは軽量・最小限に保つ。詳細ルールは `docs/rules/` に分散。

---

## 0. セッション開始時の参照順序
1. `tasks.md` — 未完了タスク（存在する場合）
2. `FILE_INDEX.md` — ファイル一覧（存在する場合）
3. `docs/rules/` — 詳細ルール一覧
4. このCLAUDE.md — ルール入口

---

## 1. 機能（README より）
- **データ入力**: CSV/Excel ファイルのアップロード
- **モデル**: LightGBM（回帰）
- **UI**: Streamlit によるインタラクティブ可視化
- **下流**: 18 Streamlit アプリ実装と顧客獲得（freelance-compass 上流戦略と整合）

---

## 2. 関連リポジトリ
| リポ | 役割 |
|---|---|
| [KazuyaMurayama/freelance-compass](https://github.com/KazuyaMurayama/freelance-compass) | 上流：事業戦略・意思決定 |
| [KazuyaMurayama/customer_segment_analysis](https://github.com/KazuyaMurayama/customer_segment_analysis) | 顧客セグメント特定 |
| [KazuyaMurayama/streamlit-sales-dashboard](https://github.com/KazuyaMurayama/streamlit-sales-dashboard) | 売上KPIダッシュボード（姉妹アプリ） |

---

## 3. 開発者情報・命名ルール

| 種別 | 表記 | 用途 |
|---|---|---|
| **システム識別子（変更不可）** | `KazuyaMurayama` | GitHub ユーザー名 / URL / `@KazuyaMurayama` |
| **システム識別子（変更不可）** | `kazuya.murayama.21@gmail.com` | git `user.email` / 連絡先 |
| **表記名（人間として記載する場合）** | **男座員也（Kazuya Oza / おざ かずや）** | ドキュメント本文の著者名 / コミット message 中の自己言及 |

- ドキュメント本文等で開発者名を**人間として**記載する際は **男座員也 / Kazuya Oza** を使用
- 「Murayama」「村山」「Otokoza」「おとこざ」を**表記名**として誤用しない（システム識別子としての `KazuyaMurayama` は許容）

---

## 4. ツール実行・Git・ファイル保存
- 確認不要・即実行（事前確認文を出力しない）
- 例外（事前確認必須）: main への `git push --force`、`gh repo delete`
- **ブランチ管理**: デフォルトはmainへ直接コミット。ブランチ作成は明示指示時のみ。万一作成した場合はmainマージ→削除→push完了で「完了」
- **ファイル保存**: 本リポ内のみ。`C:\Users\user\Desktop` への出力禁止

---

## 5. 成果物報告ルール

| 成果物 | 説明 | リンク |
|---|---|---|
| file.py | 1行説明 | [開く](https://github.com/KazuyaMurayama/MachineLearning_App/blob/main/path/to/file.py) |

- Markdownリンク `[表示名](URL)` 形式必須 / `/blob/<実ブランチ>/<実パス>` 形式
- **報告前にURL存在確認**：`Invoke-WebRequest -Uri https://api.github.com/repos/KazuyaMurayama/MachineLearning_App/contents/PATH?ref=main -UseBasicParsing` でステータス200確認
- push完了後のみURL生成

---

## ドキュメント命名・日付ルール（v2.0 / 2026-06-03 改訂）

### ファイル名
- `<TOPIC>_YYYYMMDD.md` 形式（**サフィックス・ハイフンなし**）
  - 例: `STRATEGY_REPORT_20260603.md`
- **同日中の追加更新**: `-v2`、`-v3` を追加（例: `STRATEGY_REPORT_20260603-v2.md`）
- **翌日1回目**: v サフィックスをリセット（例: `STRATEGY_REPORT_20260604.md`）

### 表記の区別
- **ファイル名**: ハイフン**なし** `YYYYMMDD`（例: `20260603`）
- **本文中の日付表記**: ハイフン**あり** `YYYY-MM-DD`（例: `2026-06-03`）

### H1直下の日付メタデータ
レポート系 .md 新規作成時は H1直下に必ず記載:
```
作成日: YYYY-MM-DD
最終更新日: YYYY-MM-DD
```
更新時は **最終更新日のみ** 当日付に書き換え（作成日は固定）。

### 対象外（日付サフィックスを入れない）
- README / CLAUDE.md / FILE_INDEX / tasks.md / CHANGELOG / LICENSE / SPEC.md
- `CURRENT_*.md`（常に最新で参照される単一ファイル）
- パイプライン自動生成ファイル（例: `REPORT.md`、`outputs/*.md`）

### 旧形式（廃止・新規禁止）
- ❌ `<TOPIC>_2026-06-03.md`（ハイフン区切り）
- ✅ `<TOPIC>_20260603.md`（**現行ルール**）

---

## 7. Skill 起動ルール

| トリガー | スキル |
|---|---|
| EDA（探索的データ分析） | `.claude/skills/programmatic-eda/SKILL.md` |
| データ品質監査 | `.claude/skills/data-quality-audit/SKILL.md` |
| ビジネス指標計算 | `.claude/skills/business-metrics-calculator/SKILL.md` |
| 時系列・トレンド分析 | `.claude/skills/time-series-analysis/SKILL.md` |
| セグメンテーション・顧客分析 | `.claude/skills/segmentation-analysis/SKILL.md` |
| 可視化設計 | `.claude/skills/visualization-builder/SKILL.md` |
| ダッシュボード仕様定義 | `.claude/skills/dashboard-specification/SKILL.md` |
| TDD で機能実装 | `.claude/skills/sp-test-driven-development/SKILL.md` |
| バグ・エラー調査 | `.claude/skills/sp-systematic-debugging/SKILL.md` |
| QC・レビュー前 | `.claude/skills/analysis-qa-checklist/SKILL.md` |
| 成果物の納品・コミット前 | `.claude/skills/sp-verification-before-completion/SKILL.md` |
