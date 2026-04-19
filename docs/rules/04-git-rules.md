# 04: Git 操作ルール

## ✘ 禁止操作

- **ブランチ作成は一切禁止**（Claude Code がセッションを変えると読み取りにくいため）
  - 禁止コマンド: `git checkout -b` / `git switch -c` / `git branch <name>`
  - GitHub MCP の `create_branch` も禁止
- ユーザーから明示的な指示がない限り、現在のブランチを変更しない

## ✔ 許可操作

- 現在のブランチ（原則 `main`）上での:
  - `git add`, `git commit`, `git push`
  - `git status`, `git log`, `git diff`（読み取り）
  - `git pull`（最新化）
- GitHub MCP の `create_or_update_file`, `push_files`（main ブランチ対象）

## 運用原則

- 全てのファイルは **main ブランチに直接** コミットする
- 他ブランチにファイルが残っていたら main にコピーしてから作業する
