# FILE_INDEX.md — MachineLearning_App

> **新セッション開始時に必ずこのファイルを読む。**
> ファイル追加・削除・移動時は必ずこのファイルを更新すること。
> 最終更新: 2026-04-30

## 概要
Streamlit + LightGBMベースの機械学習予測アプリ群。EC・不動産・給与・LTV・離職などの回帰予測をデモ提供する多機能プラットフォーム。

**スタック:** Python, Streamlit, LightGBM, SHAP, Pandas, GitHub Actions

---

## 📋 最初に読むべきファイル

| 優先度 | ファイル | 内容 |
|---|---|---|
| ★★★ | `CLAUDE.md` | 運用ルール・Claude Code向け指針 |
| ★★★ | `README.md` | プロジェクト概要 |
| ★★★ | `tasks.md` | 現在のタスク一覧 |
| ★★ | `progress.md` | 開発進捗記録 |
| ★★ | `app.py` | メインStreamlitアプリ |

---

## 🗂️ ディレクトリ構造

```
MachineLearning_App/
├── CLAUDE.md                    ← 最重要ルール
├── README.md
├── tasks.md
├── progress.md
├── ISSUES.md
├── app.py
├── streamlit_app.py
├── ec_app.py
├── requirements.txt
├── packages.txt
├── .python-version
├── .streamlit/config.toml
├── .github/workflows/patch-ec-what-if.yml
├── .claude/commands/           ← カスタムコマンド群
├── modules/                    ← 共通モジュール
│   ├── data_loader.py
│   ├── evaluation.py
│   ├── model.py
│   └── shap_analysis.py
├── apps/                       ← 各デモアプリ
│   ├── common/reverse_shap.py
│   ├── ec-demo/ ec-dashboard/ ec-rfm/ ec-what-if/
│   ├── ec-ad-roi/ ec-executive-dashboard/ ec-monthly-briefing/
│   ├── crosssell/ payment-alert/ report-gen/
│   ├── shigyou-demo/ shigyou-ltv/ shigyou-office-dashboard/
│   ├── compliance-pack/ contract-draft/ doc-checker/ service-lp/
│   └── shigyou-briefing/
├── sample_data/                ← 学習・評価用CSV
├── scripts/smoke_test.py
├── create_sample_data.py
└── docs/sales-assets/          ← 営業資料
```

---

## 📑 全ファイル一覧

| パス | 種別 | 説明 |
|---|---|---|
| `CLAUDE.md` | ドキュメント | 運用ルール・Claude Code向け指針 |
| `README.md` | ドキュメント | プロジェクト概要 |
| `tasks.md` | ドキュメント | タスク管理 |
| `progress.md` | ドキュメント | 開発進捗記録 |
| `ISSUES.md` | ドキュメント | 既知の問題一覧 |
| `app.py` | Python | メインStreamlitアプリ |
| `streamlit_app.py` | Python | Streamlitエントリポイント |
| `ec_app.py` | Python | EC特化アプリ |
| `requirements.txt` | 設定 | Python依存関係 |
| `packages.txt` | 設定 | システムパッケージ |
| `.python-version` | 設定 | Pythonバージョン指定 |
| `.streamlit/config.toml` | 設定 | Streamlit設定 |
| `.github/workflows/patch-ec-what-if.yml` | CI/CD | EC What-ifアプリのパッチワークフロー |
| `modules/data_loader.py` | Python | データ読み込みモジュール |
| `modules/evaluation.py` | Python | 評価指標モジュール |
| `modules/model.py` | Python | LightGBMモデルモジュール |
| `modules/shap_analysis.py` | Python | SHAP分析モジュール |
| `apps/common/reverse_shap.py` | Python | 逆SHAP分析（共通ユーティリティ） |
| `apps/ec-demo/app.py` | Python | ECデモアプリ |
| `apps/ec-dashboard/app.py` | Python | EC分析ダッシュボード |
| `apps/ec-rfm/app.py` | Python | EC RFM分析アプリ |
| `apps/ec-what-if/app.py` | Python | EC What-if分析アプリ |
| `apps/ec-ad-roi/app.py` | Python | EC広告ROI計算アプリ |
| `apps/ec-executive-dashboard/app.py` | Python | EC経営者向けダッシュボード |
| `apps/crosssell/app.py` | Python | クロスセル予測アプリ |
| `apps/payment-alert/app.py` | Python | 支払アラートアプリ |
| `apps/shigyou-demo/app.py` | Python | 士業デモアプリ |
| `apps/compliance-pack/app.py` | Python | コンプライアンスパックアプリ |
| `sample_data/` | データ | 学習・評価用CSVデータセット |
| `scripts/smoke_test.py` | Python | スモークテストスクリプト |
| `create_sample_data.py` | Python | サンプルデータ生成スクリプト |
| `docs/sales-assets/` | ドキュメント | 営業資料・メールテンプレート |

---

## 🔖 ファイル更新ルール

1. 新ファイル追加時: 該当セクションに1行追加
2. ファイル削除・移動時: 該当行を削除または更新
3. 更新後: `git add FILE_INDEX.md && git commit -m "docs: FILE_INDEX.md更新"`
