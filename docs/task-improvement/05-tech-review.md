# 技術レビューエージェントによる評価

> 評価者: Tech Reviewer Agent
> 日付: 2026-04-08

---

## エグゼクティブサマリー

3タスクをエンジニアリング品質・保守性・パフォーマンスの観点で精査した結果、**「実装した」と「本番品質で動く」の間には複数の未解決課題が存在する**。特に深刻なのは3点だ。(1) `ast.parse()` 止まりの動作確認はスモークテスト不在と同義であり「デプロイ準備完了」の根拠にならない。(2) 4057行の self-contained コードベースには `setup_japanese_font()` 6箇所コピーを筆頭とするDRY原則違反が広範に存在し、バグ修正コストが6倍になる。(3) `subprocess.run()` の `check=True` 省略・失敗後の即座な `pd.read_csv()` 実行など、エラーハンドリングが本番環境で致命的な障害を引き起こす構造になっている。「動けばOK」でマージしたコードが月額26〜30万円のプレミアムサービスを支えるには技術的負債が重すぎる。

---

## TASK 1 の技術的評価

### 動作確認スコープの問題

**`ast.parse()` による「動作確認」は構文レベルの検証にすぎない。** 実際に `ec-what-if/app.py` は起動時に `training_data.csv` の存在チェックを行い、ファイルが無ければ `st.stop()` で停止する（217〜220行）。この制御フローは構文解析では到達できない。

`shigyou-ltv/app.py` の LightGBM 学習は `st.session_state.model is None` のブランチで起動直後に実行される（408〜423行）。150行のデータに対しても `shap.TreeExplainer` + `explainer.shap_values()` の初回計算は数十秒オーダーを要する。Streamlit Cloud の無料枠では CPU が遅く、タイムアウトのリスクは実測なしに「問題なし」とは断言できない。

`requirements.txt` はすべてのパッケージに `>=` バージョン指定のみを使用しており（例: `lightgbm>=4.5.0`）、上限バインドがない。LightGBM 5.x がリリースされた際に API 破壊変更が含まれる可能性を排除していない。

### 欠落している検証

以下の検証が一切実施されていない。

| 検証項目 | リスク |
|---------|--------|
| `streamlit run app.py --server.headless true` によるスモークテスト | 起動時クラッシュの検出不能 |
| LightGBM fit の実行時間計測 | タイムアウトリスク未評価 |
| SHAP 計算のメモリプロファイリング | OOM による無音クラッシュ |
| Streamlit Cloud 環境での日本語フォント確認 | グラフタイトル文字化け |
| `requirements.txt` の `pip install` 成功確認 | バージョン競合によるデプロイ失敗 |
| `create_sample_data.py` 実行後の生成ファイル統計チェック | 異常値（例: 離脱率 > 1.0）の見落とし |

### Smoke test の必要性

最低限のスモークテストとして、以下を CI に組み込む必要がある。

```bash
# 各アプリディレクトリで実行
python create_sample_data.py
python -c "import app"  # モジュールレベル副作用の確認
streamlit run app.py --server.headless true &
sleep 10 && curl -f http://localhost:8501/healthz || exit 1
```

これすら存在しない状態で「デプロイ準備完了」と評価することはエンジニアリング観点では受け入れられない。

---

## TASK 2 の技術的評価

### URL整合性チェックの網羅性

`ec-demo` の欠落を「発見して修正した」という事実そのものが、チェックプロセスの信頼性問題を露呈している。手動の目視確認は再現性がなく、次の追加時に同じ漏れが発生することを防ぐ仕組みがない。

`streamlit_app.py` の `APP_URLS` は11エントリ、`ec_app.py` の `EC_URLS` は7エントリ（ec-demo を含む）。これらの URL (`https://*.streamlit.app`) がデプロイ済みかの疎通確認は実施されていない。ポータルのカードをクリックしても「Not Found」になるリスクが残っている。

### 自動化の可能性

URL整合性チェックは以下のスクリプトで完全自動化できる。

```python
# url_consistency_check.py の案
import ast, re

def extract_urls(filepath):
    with open(filepath) as f:
        src = f.read()
    # APP_URLS / EC_URLS の辞書リテラルを抽出
    ...

def check_url_reachability(url_dict):
    import requests
    for key, url in url_dict.items():
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code != 200:
            print(f"WARN: {key} → {url} ({r.status_code})")
```

このスクリプトをデプロイ前チェックリストに組み込めば、手動確認漏れを排除できる。

### 再発防止策

1. `APP_URLS` / `EC_URLS` を YAML 等の単一設定ファイルに集約し、ポータルコードはそこから読み込む
2. CI パイプラインで `apps/` ディレクトリのサブフォルダ一覧と URL 辞書の差分を自動検出する
3. PR テンプレートに「新規アプリ追加時のURL登録チェックリスト」を追加する

---

## TASK 3 の技術的評価

### ドキュメントのバージョン管理

`shigyou-business-alignment.md` および `ec-business-alignment.md` の更新は commit `eddbe9e` で実施されているが、バージョン番号や更新日が本文内に埋め込まれていない。後から「いつの時点の評価か」を追跡するには git log を参照するしかなく、非エンジニアの関係者には不透明である。

### 機械読み取り可能性

ドキュメント内の「L3実装完了」「充足率 95/100点」といった数値は自由記述のMarkdownテキストに埋め込まれており、機械的に抽出・検証できない。品質スコアは主観的な文字列であり、採点基準・採点者・評価日が紐付いていない。これは TASK 1 が採用した「スコア掲示 ≒ 品質保証」という誤った認識を助長する。

具体的なリスクとして、将来のアプリ改修時に「充足率 95/100」という数値を更新し忘れるケースが想定できる。テキストとコードが乖離しても自動的に検出する手段がない。

### 数値の更新漏れリスク

`streamlit_app.py` の Hero セクションには「11の専用ツール」という文言がハードコードされている（121行）。アプリ数が変わったとき、サイドバー (`### 📋 ツール一覧（11アプリ）`)・Hero テキスト・KPI カード (`11`) の3箇所を手動で更新しなければならない。現時点で ec_app.py のサイドバーは「6アプリ」と表示しているが、ポータル自体は ec-demo を含む7アプリの URL を定義しており、既に不一致が発生している。

---

## コードベース全体の技術負債

### DRY原則違反（重複コード）

**`setup_japanese_font()` 関数は6アプリ × 14行 = 84行が完全コピペされている。**

```
/apps/shigyou-office-dashboard/app.py:29-43
/apps/shigyou-ltv/app.py:26-37
/apps/shigyou-briefing/app.py:21-33
/apps/ec-executive-dashboard/app.py:29-43
/apps/ec-what-if/app.py:26-38
/apps/ec-monthly-briefing/app.py:21-33
```

フォントの優先順位を変更したい場合、6ファイルすべてを編集する必要がある。1箇所でも更新漏れがあると、アプリ間でフォント挙動が分岐する。

共通マスター生成コードも同様だ。EC系3アプリ（ec-executive-dashboard, ec-what-if, ec-monthly-briefing）の `create_sample_data.py` は「商品マスター → 顧客マスター → 注文履歴 → 広告実績」の生成ブロックがほぼ同一で複製されている。seed=42 で生成される乱数列はプロセス内の呼び出し順序に依存するため、3ファイルのコードが完全に一致していない限り生成データが食い違う。`ec-monthly-briefing/create_sample_data.py` は注文履歴の後に `cross_segment` を生成しないが、`ec-executive-dashboard/create_sample_data.py` は生成する。この差異により、乱数シーケンスがずれ、両アプリで「同じ顧客ID・同じ商品ID」と主張していても実際の値が異なる可能性がある（diff 検証未実施）。

LabelEncoder の直接使用も2箇所（`shigyou-ltv` と `ec-what-if`）で独立実装されている。カテゴリ変数のエンコーディング順序は `fit()` 時のデータ分布に依存するため、アプリを再起動するたびにエンコーディングが変わりうる。`st.session_state` にモデルと Encoder を格納しているが、セッションが切れると再学習・再フィットが走り、予測値の連続性が保証されない。

### テスト不在

6アプリ計4057行に対してユニットテストが1件も存在しない。テストが書かれていないコードは保守コストが指数的に増大する。

具体的に欠落しているテスト：
- `generate_sample_data()` の出力スキーマ検証（カラム名・型・値域）
- `classify_cluster()` の境界値テスト（LTV=0、ROI=0.1、crosssell_prob=0.5）
- `train_model()` の戻り値型チェック
- URL定義辞書とアプリディレクトリの整合性チェック

CI/CD 設定ファイル（`.github/workflows/`）は存在しない。デプロイは手動操作に依存しており、誰がいつデプロイしたかのトレーサビリティがない。

### パフォーマンス懸念

**起動時の LightGBM 自動学習（shigyou-ltv）はキャッシュ設計として問題がある。** `st.session_state` にモデルを格納しているため、**セッション間でモデルが共有されない**。ユーザーAとユーザーBが同時にアプリを開いた場合、両者で独立してモデル学習が走る。`@st.cache_resource` を使えばサーバプロセス全体でモデルを共有できるが、現実装はその恩恵を受けていない。

`ec-what-if` は `@st.cache_resource` でモデルを正しく共有しているが、`train_models()` 内でSHAP値を全テストデータに対して事前計算・キャッシュしているため、初回起動時のメモリ使用量が大きい（3モデル × 200サンプル × 10特徴量分のSHAP行列）。

Streamlit Cloud の無料枠は RAM 1GB 制限がある。17アプリが同時稼働した場合、各アプリインスタンスが独立して LightGBM モデル + SHAP 値をメモリに保持するため、合計メモリ使用量は予測困難だ。

### メモリリーク

`ec-what-if/app.py` の `predict_scenario()` 関数は呼び出されるたびに `shap.TreeExplainer(model)` を**新規に作成**している（204行）。

```python
def predict_scenario(cache, ...):
    ...
    explainer = shap.TreeExplainer(cache["models"]["売上"])  # ←毎回生成
    sv = explainer.shap_values(row)
    return preds, sv, row
```

What-If シミュレーターのスライダーを動かすたびにこの関数が実行され、`TreeExplainer` オブジェクトが GC に渡るまでメモリに留まる。Streamlit の再実行モデルとの相互作用により、実質的なメモリリークになりうる。

`shigyou-ltv/app.py` のタブ1で SHAP Summary Plot を描画する際、`plt.gcf()` で現在のフィギュアを取得している（511行）。これは `fig_shap, ax_shap = plt.subplots(...)` で作成したフィギュアと**異なるフィギュアを参照する可能性**があり、メモリ上にゴミフィギュアが残る。`plt.close("all")` で全フィギュアをクローズしているが、このアンチパターンは保守時に混乱を招く。

### セキュリティリスク

**`subprocess.run()` のエラーハンドリング不整合：**

`ec-monthly-briefing/app.py` 83行は `check=True` なしで実行している。

```python
subprocess.run([sys.executable, os.path.join(base_dir, "create_sample_data.py")])
```

スクリプトが失敗しても例外が発生せず、直後の `pd.read_csv()` でファイルが存在しなければ `FileNotFoundError` がユーザーに生の Python トレースバックとして表示される。対照的に `shigyou-office-dashboard/app.py` は `check=True` + `try/except` で適切にハンドリングしている（100〜108行）。同じパターンの4箇所での実装に一貫性がない。

`subprocess.run([sys.executable, path])` は `path` が外部入力でないため現状では RCE リスクは限定的だが、将来的に `path` の構成にユーザー入力が混入した場合に RCE となる。サブプロセス呼び出しではなく Python 関数を直接呼び出す設計（`import create_sample_data; create_sample_data.main()`）が望ましい。

`unsafe_allow_html=True` は `shigyou-ltv` に19箇所、`ec-what-if` に21箇所存在する。HTML を直接組み込む設計は XSS 耐性がゼロであり、将来的にユーザー入力を HTML テンプレートに埋め込む実装が追加された場合に直接 XSS になる。現在はサンプルデータのみを表示しているため即時のリスクは低いが、設計上の火種として残っている。

---

## 技術的に最も深刻な問題 TOP5

1. 🔴 **モデルキャッシング設計の根本的誤り（shigyou-ltv）**
   - `st.session_state` にモデルを格納する設計では、セッション間でモデルが共有されず、ユーザーごとに毎回学習が走る。初回アクセス時に30〜60秒のスピナーが発生し、Streamlit Cloud の無料枠 CPU でタイムアウトするリスクがある。`@st.cache_resource` への移行が必要。

2. 🔴 **スモークテスト完全不在・CI/CD なし**
   - 4057行のプロダクションコードに対してテストゼロ、CI ゼロ。`streamlit run app.py` すら自動実行されない。次のデプロイで無音の回帰が発生しても検出手段がない。月額30万円のサービスをこのまま提供することはエンジニアリングリスクとして容認できない。

3. 🔴 **エラーハンドリング不整合によるユーザー向け生エラー露出**
   - `ec-monthly-briefing/app.py` の `subprocess.run()` は `check=True` なしで、失敗時に `FileNotFoundError` の生トレースバックをユーザーに表示する。同一コードパターンが4アプリで異なる実装になっており、品質基準が統一されていない。

4. 🟡 **6アプリ × 共通関数コピペによるDRY原則違反**
   - `setup_japanese_font()`（84行相当）、共通マスター生成ブロック（各50〜80行）が6箇所に複製。seed=42 のランダム呼び出し順序がファイル間でずれているため、「同一データ」と主張しても実際の値が異なる可能性がある。共通ライブラリ（`apps/common/utils.py` 等）への抽出が必要。

5. 🟡 **requirements.txt の上限バインドなしバージョン指定**
   - `lightgbm>=4.5.0`, `shap>=0.42.0` 等の上限なし指定は、メジャーバージョンアップ時に API 破壊変更でデプロイが失敗するリスクを抱える。本番デプロイには `lightgbm>=4.5.0,<5.0.0` 形式の上限バインドが必要。

---

## 推奨する技術的改善策

### 即時対応（デプロイ前に必須）

- **スモークテスト実行**: 各アプリで `streamlit run app.py --server.headless true` を実行し、起動エラーがないことを手動確認する
- **`ec-monthly-briefing` のエラーハンドリング修正**: `subprocess.run()` に `check=True` を追加し、失敗時の `st.error()` 表示と `st.stop()` を実装する（`shigyou-office-dashboard` の100〜109行を参照）
- **`requirements.txt` に上限バインド追加**: 少なくとも LightGBM, SHAP, Streamlit の3パッケージに `<次メジャーバージョン` を追加する
- **`ec_app.py` のアプリ数カウント修正**: サイドバーの「6アプリ」を「7アプリ」に修正する（ec-demo を含む）

### 短期対応（1〜2スプリント）

- **`setup_japanese_font()` を共通ライブラリに抽出**: `apps/common/utils.py` を作成し、全アプリからインポートする。`sys.path.append` の代わりに `PYTHONPATH` 設定、または Streamlit の `pages/` 構造の採用を検討する
- **`shigyou-ltv` のキャッシュを `@st.cache_resource` に移行**: モデル・Encoder・SHAP値を `train_and_cache()` 関数に集約し `@st.cache_resource` デコレータを付与する
- **`predict_scenario()` の `TreeExplainer` をキャッシュ**: `ec-what-if` において `explainer` オブジェクトを `train_models()` の戻り値辞書に含める
- **EC 3アプリの共通マスター生成を単一スクリプトに統合**: `apps/ec-common/create_master_data.py` を作成し、3アプリが同一スクリプトを参照する。差分検証（diff）を生成スクリプト内に実装する
- **URL定義を設定ファイルに集約**: `portal_config.yaml` に全 URL を定義し、`streamlit_app.py` と `ec_app.py` がそこから読み込む

### 中期対応（1〜2ヶ月）

- **pytest による最低限のユニットテスト整備**: `test_create_sample_data.py`（スキーマ・値域検証）と `test_app_startup.py`（import + 起動確認）を各アプリに追加する
- **GitHub Actions CI パイプラインの導入**: `push` トリガーで `pip install`, `python create_sample_data.py`, スモークテストを自動実行する
- **URL疎通確認スクリプトの CI 組み込み**: デプロイ後に全 URL への HTTP HEAD リクエストを実行し、200 以外を Slack 通知する
- **LightGBM モデルの品質ゲート実装**: R² < 0 の場合に `st.warning()` で警告バナーを表示する。離脱率モデルの R² = -0.16 は現在無警告で表示されており、顧客への誤解を招く
- **Streamlit Cloud ブランチ整理**: `claude/integrate-business-plan-IBKFu` ブランチが長期間残存している。`main` ブランチへのマージまたはクローズを行い、ブランチ戦略（`main`: 本番、`develop`: 開発）を明文化する
- **`requirements.txt` の固定バージョン化**: CI で `pip-compile` を実行し `requirements.lock` を生成・コミットして再現可能なビルドを保証する
