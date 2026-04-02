# MVP実装スキル

企画済みのMVPを、確立されたパターンに従って実装します。

## 入力
$ARGUMENTS
（例: "在庫ABC分析 inventory-abc #10B981 3タブ" や MVP名のみでも可）

入力から以下を解析（不足分はユーザーに確認）:
- **MVP名**（日本語）
- **ディレクトリ名**（英語kebab-case）
- **テーマカラー**（HEX）
- **タブ数と構成**

## 実装パターン（必須遵守）

### ファイル構成
```
apps/{app-name}/
├── .streamlit/config.toml    # テーマカラー設定
├── app.py                     # メインアプリ（self-contained）
├── requirements.txt           # streamlit+pandas+matplotlib+numpy+openpyxl+xlrd
├── packages.txt               # fonts-noto-cjk
├── create_sample_data.py      # サンプルデータ生成スクリプト
└── sample_data/
    └── *.csv                  # 自動生成されたサンプルデータ
```

### app.py 必須パターン

```python
# === 1. Imports ===
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# === 2. 日本語フォント ===
def setup_japanese_font():
    candidates = ["Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic", "MS Gothic", "Meiryo", "DejaVu Sans"]
    available = {f.name for f in fm.fontManager.ttflist}
    for fn in candidates:
        if fn in available:
            plt.rcParams["font.family"] = fn
            plt.rcParams["axes.unicode_minus"] = False
            return fn
    plt.rcParams["font.family"] = "DejaVu Sans"
    return "DejaVu Sans"

# === 3. Page Config ===
st.set_page_config(page_title="...", page_icon="...", layout="wide", initial_sidebar_state="expanded")

# === 4. CSS ===
# .hero, .section-divider, .kpi-card 等のCSS
# hero背景はテーマカラーの薄い色を使用

# === 5. Session State ===
for k, v in {"df": None, "loaded": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === 6. Auto-load sample data ===
if not st.session_state.loaded:
    p = os.path.join(os.path.dirname(__file__), "sample_data", "xxx.csv")
    if os.path.exists(p):
        st.session_state.df = load_csv(p)
    st.session_state.loaded = True

# === 7. Sidebar ===
# ブランド表記 + CSV upload + 必須カラム説明

# === 8. Hero + 導入効果 ===
# st.info("導入効果: ...")

# === 9. KPIカード（3〜4個） ===

# === 10. タブ構成 ===

# === 11. 相互リンクフッター ===
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 関連ツール")
# 3カラムで関連ツールリンク
st.caption("AI経営パートナー x データサイエンス | {ツール名} v1.0")
```

### create_sample_data.py 必須パターン
- `generate_unique_names()` で重複なし顧問先名を生成
- `np.random.RandomState(42)` で再現性確保
- 出力先: `sample_data/xxx.csv`（utf-8-sig）
- 実行後に統計サマリーをprintする

## 実行ステップ

### Step 1: 設定ファイル生成
1. `.streamlit/config.toml` — テーマカラー反映
2. `requirements.txt`
3. `packages.txt`
→ git commit + push

### Step 2: サンプルデータ生成
1. `create_sample_data.py` 作成
2. スクリプト実行してCSV生成
3. 生成結果の統計確認
→ git commit + push

### Step 3: app.py実装
1. 上記パターンに従ってapp.py作成
2. 構文チェック: `python -c "import ast; ast.parse(open('app.py').read())"`
→ git commit + push

## 品質チェックポイント（実装完了時に自己確認）
- [ ] self-contained（外部モジュールimportなし）
- [ ] サンプルデータ自動読み込み動作
- [ ] CSVダウンロード機能あり
- [ ] 日本語フォント対応
- [ ] 相互リンクフッター配置
- [ ] 構文エラーなし

## 注意事項
- 1ステップごとにcommit+push（タイムアウト対策）
- LightGBM/SHAP使用の場合は requirements.txt に追加
- 回答は日本語で行う
