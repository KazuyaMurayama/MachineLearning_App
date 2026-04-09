# Phase 3: 優先順位付きアクションプラン

> 作成者: Action Planner Agent (Opus)
> 日付: 2026-04-08
> 入力: 06-synthesis.md

## エグゼクティブサマリー

6テーマの統合synthesisに対し、Phase 4で最も投資対効果が高いのは「**信頼性の訂正**」に的を絞った局所修正である。5エージェントが一致して指摘した「楽観バイアス」の具体物（R² = -0.16 の欠陥モデル、誇大な完了宣言、アプリ数の表示不整合）は、いずれも数十行以内の修正で完了でき、効果は即時に顧客提示品質に反映される。

**3つの方針**:
1. **訂正 > 追加**: 新機能より先に「間違った宣言」を訂正する（P0）。信頼性の地盤が無ければ営業アセットは意味を持たない。
2. **self-contained制約を厳守**: 共通ライブラリ化（`apps/common/`）は保留。各アプリ内で完結する修正のみPhase 4対象。
3. **Go-to-Marketアセットは最小2点のみ**: パイロット提案書テンプレートと15分デモスクリプトのみPhase 4に含める。ROI試算・料金表は次フェーズへ繰越。

**Phase 4 の目標成果**: P0を3件・P1を5件・営業アセット2件、計10タスクを2セッション以内に完了する。

---

## Phase 4 で即実行するタスク（P0 + P1 高優先）

### 🔴 P0-A: ec-what-if 離脱率データ欠陥の修正
- **問題**: synthesis P0-2（R² = -0.16、churn_rate > 1.0 が 27件）
- **根本原因**: `apps/ec-what-if/create_sample_data.py` 87行目 `churn_rate = round(np.random.uniform(0.05, 0.30) / (champions_ratio + 0.1), 3)` に `clip` が無い。`champions_ratio ∈ [0.10, 0.30]` のため分母最小0.20 → 最大1.5が発生。
- **対応内容**:
  1. 87行目を `churn_rate = round(np.clip(np.random.uniform(0.05, 0.30) / (champions_ratio + 0.1), 0.0, 0.95), 3)` に修正
  2. `python apps/ec-what-if/create_sample_data.py` 再実行して `training_data.csv` 再生成
  3. `app.py` 内のLightGBM再学習ルートで R² を再計測し、`R² < 0.3` の場合は `st.warning()` で警告バナー表示（2-3行追加）
  4. 再学習後のR²を `docs/task-improvement/08-execution-log.md` に記録
- **工数**: A (15-45分)
- **期待効果**: 離脱率モデルR²を -0.16 → 0.3以上に改善。デモ中核機能の信頼性確保。
- **依存**: なし（最優先）
- **担当エージェント**: general-purpose (sonnet)

### 🔴 P0-B: 「L3実装完了」誇大表現の訂正
- **問題**: synthesis P0-3（パイロット顧客0社での完了宣言）
- **対応内容**: 以下6箇所を「L3プロトタイプ完成・パイロット検証前」に統一修正:
  - `docs/ec-business-alignment.md` 132行目「L3水準に到達」/ 194行目「### L3実装完了」/ 228行目「L3実装完了を反映」
  - `docs/shigyou-business-alignment.md` 54行目「新規実装完了」/ 191行目「✅実装完了」「L3水準に到達」/ 219行目「L3実装完了を反映」
  - 各ファイル末尾に1文追記: 「※L3水準の最終充足はパイロット顧客1社による6週間の実運用検証をもって確定する」
- **工数**: S (5-15分)
- **期待効果**: 誇大表現を撤回し、パイロット獲得への危機感維持。Businessリスク低減。
- **依存**: なし
- **担当エージェント**: general-purpose (sonnet)

### 🔴 P0-C: `ec_app.py` アプリ数カウント・docstring訂正
- **問題**: synthesis P1-3（アプリ追加時の登録フロー不在）由来の表示不整合
- **対応内容**:
  - `ec_app.py` 4行目「EC事業者向けAIツール3アプリ」→「EC事業者向けAIツール7アプリ」
  - 同ファイル 84行目「ツール一覧（6アプリ）」→「ツール一覧（7アプリ）」
- **工数**: S (5-15分)
- **期待効果**: ポータル表示の整合性回復。初見UXの信頼感低下を防止。
- **依存**: なし
- **担当エージェント**: general-purpose (sonnet)

### 🟠 P1-A: `shigyou-ltv` キャッシュ設計の修正
- **問題**: synthesis Tech-1（`st.session_state` にモデル格納 → セッション跨ぎで再学習）
- **対応内容**: `apps/shigyou-ltv/app.py` 219-230行目のセッション初期化ブロックを改修:
  - モデル学習関数を切り出して `@st.cache_resource` でキャッシュ
  - SHAP値計算も `@st.cache_data` でキャッシュ
  - 既存の `st.session_state.model` 参照を `get_trained_model()` 呼び出しに置換
- **工数**: A (15-45分)
- **期待効果**: 2回目以降のアクセス時間を90%以上削減。デモ中の待ち時間低減。
- **依存**: なし
- **担当エージェント**: general-purpose (sonnet)

### 🟠 P1-B: `ec-monthly-briefing` subprocess エラーハンドリング修正
- **問題**: synthesis Tech-2（`check=True` 省略で生トレースバック露出）
- **対応内容**: `apps/ec-monthly-briefing/app.py` 83/107行目の `subprocess.run(...)` に以下を適用:
  ```python
  try:
      subprocess.run([...], check=True, capture_output=True, text=True)
  except subprocess.CalledProcessError as e:
      st.error(f"サンプルデータ生成に失敗しました: {e.stderr}")
      st.stop()
  ```
  同パターンを `shigyou-briefing/app.py` にも横展開
- **工数**: S (5-15分)
- **期待効果**: 顧客環境でのエラー露出リスク削減。
- **依存**: なし
- **担当エージェント**: general-purpose (sonnet)

### 🟠 P1-C: ec-what-if コールドスタートプログレス表示追加
- **問題**: synthesis UX-1（デモ最大山場のコールドスタート沈黙リスク）
- **対応内容**: `apps/ec-what-if/app.py` のモデル学習セクションを `with st.status("モデル学習中...", expanded=True) as status:` で包み、4段階のサブメッセージ（データ読込 → 前処理 → 3モデル学習 → SHAP計算）を逐次表示。
- **工数**: A (15-45分)
- **期待効果**: デモ中の体感待ち時間を主観的に50%削減。
- **依存**: P0-A 完了後（同ファイル群を触るため競合回避）

### 🟠 P1-D: スモークテストスクリプト追加
- **問題**: synthesis P0-1（ast.parse を動作確認と呼ぶ誤称）
- **対応内容**: `scripts/smoke_test.py` を新規作成:
  - 全18アプリの `app.py` を import チェック（ランタイムエラー検出）
  - create_sample_data.py の実行確認
  - 結果を `docs/task-improvement/smoke-test-result.json` に出力
  - 注: Streamlit本体の起動はサンドボックス制約により省略、import健全性で代替
- **工数**: A (15-45分)
- **期待効果**: 「構文OK → 動作OK」ギャップの初解消。
- **依存**: なし

### 🟠 P1-E: 品質スコア採点基準ドキュメント化
- **問題**: synthesis P1-2（91-95点の根拠欠如）
- **対応内容**: `docs/quality-scoring-rubric.md` を新規作成:
  - 採点観点6カテゴリ（実装充足率・データ健全性・UX完成度・ドキュメント整合性・テスト有無・デプロイ実績）各20点満点
  - 各カテゴリの採点例を1-2件記載
  - L3アプリ6本の再採点結果を表形式で再掲（透明性確保）
- **工数**: A (15-45分)
- **期待効果**: 第三者再現性の確保。
- **依存**: P0-A, P0-B 完了後

### 🟠 P1-F: パイロット提案書テンプレート作成
- **問題**: synthesis P1-4（Go-to-Marketアセット完全不在）
- **対応内容**: `docs/sales-assets/pilot-proposal-template.md` を新規作成:
  - セクション構成: 課題定義 / 提供機能 / パイロット期間（6週間） / 成功指標 / パイロット価格（月額10万円） / 契約終了後の選択肢
  - 士業版・EC版の2バリアント
  - プレースホルダー `{{顧客名}}` `{{業種}}` を明示
- **工数**: A (15-45分)
- **期待効果**: 営業活動着手の最小ブロッカー解消。
- **依存**: P0-B 完了後

### 🟠 P1-G: 15分デモスクリプト作成
- **問題**: synthesis P1-4・UX-2
- **対応内容**: `docs/sales-assets/demo-script-15min.md` を新規作成:
  - 時間配分: 0-2分 ポータル概観 → 2-7分 ec-what-if → 7-11分 shigyou-ltv → 11-14分 月次briefing → 14-15分 パイロット提案
  - 各シーンで「見せる画面」「語るセリフ」「想定質問」を3列表で記載
- **工数**: A (15-45分)
- **期待効果**: デモ実施体制の即時構築。
- **依存**: P0-A, P1-C, P1-F 完了後

---

## Phase 4 で実行しないが記録するタスク（P2）

| # | タスク | 除外理由 |
|---|-------|---------|
| R-1 | `setup_japanese_font()` 共通ライブラリ化 | self-contained制約違反。次スプリント |
| R-2 | requirements.txt 上限バインド追加 | 18アプリ分で30分超 |
| R-3 | URL定義のYAML集約 | 次スプリント |
| R-4 | GitHub Actions CI 導入 | 1-2セッション内には収まらない |
| R-5 | ROI試算シート | P1-F提案書テンプレに最小ROI記述を含めて代替 |
| R-6 | 顧客向け料金表 | 価格論理の脆弱性未解決のまま公開版を作ると誤誘導 |
| R-7 | EC3アプリ共通マスター seed統合 | 次スプリントで根治 |
| R-8 | 全18URL実デプロイ疎通確認 | 未デプロイURL発見時の対応で工数拡大リスク |

---

## 将来対応（P3）

- CI/CD 構築 (pytest + GitHub Actions)
- Streamlit Cloud 実デプロイ検証（メモリ・コールドスタート実測）
- 契約書・個人情報保護・SLA定義
- 共通ライブラリ化（`apps/common/utils.py`）
- WTP（支払意欲）インタビュー実施
- CRM・コンタクトリスト整備

---

## Phase 4 実行手順

### Step 1: 独立タスク並列実行（60-90分）
以下は相互依存なし、並列起動可能:
- **P0-A**: ec-what-if 離脱率データ修正・再学習
- **P0-B**: 「L3実装完了」表現訂正（6箇所）
- **P0-C**: ec_app.py アプリ数訂正
- **P1-B**: subprocess.run check=True 追加（2アプリ4箇所）
- **P1-D**: smoke_test.py 新規作成
- **P1-A**: shigyou-ltv @st.cache_resource 移行

### Step 2: Step1依存タスク実行（60-90分）
- **P1-C**: ec-what-if プログレス表示追加（P0-A依存）
- **P1-E**: 品質スコア採点基準ドキュメント化（P0-A, P0-B依存）
- **P1-F**: パイロット提案書テンプレート（P0-B依存）

### Step 3: Step2依存タスク実行（30分）
- **P1-G**: 15分デモスクリプト（P1-C, P1-F依存）

### Step 4: 検証・ログ化（15分）
- `scripts/smoke_test.py` 実行 → 結果を `docs/task-improvement/08-execution-log.md` に記録
- P0-A の再学習R²値を記録
- 全変更ファイルの git diff 要約

---

## 成功指標（Phase 4 完了時点）

- [ ] ec-what-if 離脱率モデル R² ≥ 0.3 を達成（P0-A）
- [ ] `churn_rate > 1.0` のレコード数 = 0 件（P0-A の clip効果）
- [ ] `docs/` 配下で「L3実装完了」「L3水準に到達」の文字列が残存0件（P0-B）
- [ ] `ec_app.py` が「7アプリ」と表示（P0-C）
- [ ] `scripts/smoke_test.py` で18アプリ中17以上が import成功（P1-D）
- [ ] `shigyou-ltv` の2回目ロード時間が1回目の30%以下（P1-A）
- [ ] `docs/sales-assets/` に pilot-proposal-template.md と demo-script-15min.md の2ファイル（P1-F, P1-G）
- [ ] `docs/quality-scoring-rubric.md` に6カテゴリ×20点の採点基準と再採点結果（P1-E）
- [ ] Phase 4 で触ったファイル数 ≤ 15（局所修正原則）
- [ ] 新規ディレクトリは `scripts/` と `docs/sales-assets/` の2つのみ
