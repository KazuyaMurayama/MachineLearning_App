"""
サンプルデータ作成スクリプト
=============================
テスト用の教師データとターゲットデータを生成します

実行方法:
    python create_sample_data.py
"""

import pandas as pd
import numpy as np
import os

# sample_dataフォルダを作成
os.makedirs('sample_data', exist_ok=True)

# 乱数シード固定（再現性のため）
np.random.seed(42)

# ============================================
# 教師データ（train.csv）の作成
# ============================================
print("教師データを作成中...")

n_samples = 1000

# 特徴量の生成
data_train = {
    '年齢': np.random.randint(20, 70, n_samples),
    '経験年数': np.random.randint(0, 30, n_samples),
    '学歴': np.random.choice(['高卒', '大卒', '院卒'], n_samples),
    '部署': np.random.choice(['営業', '開発', '企画', '総務'], n_samples),
    '残業時間': np.random.randint(0, 80, n_samples),
    'プロジェクト数': np.random.randint(1, 10, n_samples),
}

# 目的変数: 年収（万円）を特徴量から計算
# 年齢 * 10 + 経験年数 * 15 + 学歴ボーナス + 残業 * 2 + ノイズ
education_bonus = {'高卒': 0, '大卒': 50, '院卒': 100}
data_train['年収'] = (
    data_train['年齢'] * 10 +
    data_train['経験年数'] * 15 +
    [education_bonus[e] for e in data_train['学歴']] +
    data_train['残業時間'] * 2 +
    data_train['プロジェクト数'] * 10 +
    np.random.normal(0, 30, n_samples)  # ノイズ
)

df_train = pd.DataFrame(data_train)
df_train['年収'] = df_train['年収'].round(0).astype(int)

# CSVに保存
df_train.to_csv('sample_data/train.csv', index=False, encoding='utf-8-sig')
print(f"✅ 教師データを作成しました: sample_data/train.csv ({len(df_train)}行)")
print(f"   カラム: {list(df_train.columns)}")
print()

# ============================================
# ターゲットデータ（target.csv）の作成
# ============================================
print("ターゲットデータを作成中...")

n_target = 100

data_target = {
    '年齢': np.random.randint(20, 70, n_target),
    '経験年数': np.random.randint(0, 30, n_target),
    '学歴': np.random.choice(['高卒', '大卒', '院卒'], n_target),
    '部署': np.random.choice(['営業', '開発', '企画', '総務'], n_target),
    '残業時間': np.random.randint(0, 80, n_target),
    'プロジェクト数': np.random.randint(1, 10, n_target),
}

df_target = pd.DataFrame(data_target)

# CSVに保存（年収は含まない）
df_target.to_csv('sample_data/target.csv', index=False, encoding='utf-8-sig')
print(f"✅ ターゲットデータを作成しました: sample_data/target.csv ({len(df_target)}行)")
print(f"   カラム: {list(df_target.columns)}")
print()

# ============================================
# プレビュー表示
# ============================================
print("=" * 60)
print("📊 教師データのプレビュー（先頭5行）")
print("=" * 60)
print(df_train.head())
print()

print("=" * 60)
print("📊 ターゲットデータのプレビュー（先頭5行）")
print("=" * 60)
print(df_target.head())
print()

print("=" * 60)
print("🎉 サンプルデータの作成が完了しました！")
print("=" * 60)
print()
print("次のステップ:")
print("1. streamlit run app.py を実行")
print("2. ブラウザでアプリが開きます")
print("3. sample_data/train.csv をアップロード")
print("4. sample_data/target.csv をアップロード")
print("5. 目的変数に「年収」を選択")
print("6. 「モデル学習」ボタンをクリック")
