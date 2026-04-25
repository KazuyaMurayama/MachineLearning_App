# タスク（セッション間引継ぎ用ランニングリスト）

> 最終更新: 2026-04-24
> ブランチ: `main`（ブランチ作成は禁止、`docs/rules/04-git-rules.md` 参照）
> 関連リポ: `kazuyamurayama/freelance-compass`（上流＝事業戦略）
> 最新戦略: [freelance-compass/outputs/integrated-business-plan-v2.md](https://github.com/KazuyaMurayama/freelance-compass/blob/claude/review-repo-docs-2nBuQ/outputs/integrated-business-plan-v2.md)（2026-03-25）

## 起動時チェックリスト

0. `progress.md` を読む（中断タスクの有無を確認）
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

## デプロイ済みアプリ URL（2026-04-20 確定）

| # | アプリ名 | URL |
|---|---|---|
| 1 | 士業ポータル | https://km-shigyou-apps.streamlit.app |
| 2 | 事務所経営ダッシュボード (L3) | https://km-shigyou-dashboard.streamlit.app |
| 3 | LTV予測＋不採算フラグ (L3) | https://km-shigyou-ltv.streamlit.app |
| 4 | 月次AIブリーフィング・士業 (L3) | https://km-shigyou-briefing.streamlit.app |
| 5 | ECポータル | https://km-ec-apps.streamlit.app |
| 6 | EC経営ダッシュボード (L3) | https://km-ec-dashboard.streamlit.app |
| 7 | What-Ifシミュレーター (L3) | https://km-ec-what-if.streamlit.app |
| 8 | EC月次AIブリーフィング (L3) | https://km-ec-briefing.streamlit.app |

---

## 次にやる（優先度順）

### 🔴 P0: ポートフォリオ整備 → GTM準備（GTMの前提条件）

> 根拠: [app-portfolio-analysis.md v2](https://github.com/KazuyaMurayama/MachineLearning_App/blob/claude/review-repo-docs-2nBuQ/docs/app-portfolio-analysis.md)

**Step 1: ポータル修正**（壊れたリンク修正 + L3コア表示）
- [ ] 士業ポータル（`streamlit_app.py`）: L3コア3本のURL→km-*修正 + T4(デモ版) + T5(無料) のみ表示。他8本のリンク削除
- [ ] ECポータル（`ec_app.py`）: L3コア3本のURL→km-*修正 + E6(デモ版) のみ表示。他3本のリンク削除

**Step 2: E6（広告ROI分析）にML+SHAP追加**
- [ ] E2(ec-what-if)のLightGBM+SHAPパイプラインをE6に流用実装
- [ ] 広告チャネル別ROAS予測 + SHAP要因分析を追加

**Step 3: T4・E6をStreamlit Cloudにデプロイ**
- [ ] T4（離反予測）デプロイ — URL: km-shigyou-churn.streamlit.app（仮）
- [ ] E6（広告ROI）デプロイ — URL: km-ec-ad-roi.streamlit.app（仮）
- [ ] ポータルのURL更新

**Step 4: GTM実行開始**（→ P1に合流）
- [ ] ゼロイチアウトリーチ戦術書作成
- [ ] ビザスク・ココナラ登録
- [ ] コールド開始

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

- [x] Streamlit Cloud デプロイ 8本完了（2026-04-20）
- [x] ec-what-if R² 改善済み（-0.16 → 0.74、2026-04-19）
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

- 2026-04-24: **アプリポートフォリオ分析 v2完了** — 全18アプリ棚卸し、3批評者レビュー40件対応、バンドルWTP再計算
- 2026-04-20: **P0 価格変更の全ファイル波及監査完了** — 全8ファイルがv0.3価格に整合済みを確認
- 2026-04-20: **Streamlit Cloud デプロイ完了** — L3 6本 + ポータル 2本、URL 確定
- 2026-04-20: **リカバリプロトコル導入** — progress.md + CLAUDE.md + 07-execution-timeout.md
- 2026-04-19: **ec-what-if R² 改善** — サンプルデータ再設計 R²=-0.16→0.74
- 2026-04-19: **リポジトリルール整備** — `docs/rules/` 7本作成、CLAUDE.md をルール参照構造に再構築
- 2026-04-16: `pricing-and-scope.md` v0.3 更新、戦略整合性確認完了、main への 2段階マージ完了
- 2026-04-09: 営業アセット改善ラウンド（新規 7 + 改善 2 + 5 批評者レビュー）
- 2026-04-08: L3 キラー機能実装（士業 3 + EC 3）

---

## 既知のリスク

- 🔴 パイロット実績 0 社 — v2 Phase 0 完了条件（M3末有料契約 1社）未達成
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
