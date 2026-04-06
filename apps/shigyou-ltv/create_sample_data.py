"""
顧問先LTV予測 サンプルデータ生成スクリプト
==========================================
実行: python apps/shigyou-ltv/create_sample_data.py
"""
import os
import numpy as np
import pandas as pd

np.random.seed(42)  # 他の2アプリと同一seed
N = 150

# 共通マスター（他アプリと同一）
顧問先ID = [f"C{i:03d}" for i in range(1, N + 1)]
業種 = np.random.choice(
    ["建設業", "飲食業", "不動産", "小売業", "製造業", "サービス業", "IT", "医療"],
    N, p=[0.18, 0.15, 0.14, 0.13, 0.12, 0.12, 0.08, 0.08]
)
月額顧問料 = np.random.choice(
    [10000, 20000, 30000, 50000, 80000, 100000, 150000, 200000, 300000],
    N, p=[0.05, 0.10, 0.20, 0.25, 0.15, 0.12, 0.07, 0.04, 0.02]
)
離反リスクスコア = (np.random.beta(2, 5, N) * 100).round(1)
クロスセル推定増収額 = np.random.randint(0, 5, N) * np.random.choice(
    [50000, 80000, 100000, 150000, 200000], N
)

# LTV固有列
契約継続予測年数 = np.random.exponential(4, N).clip(0.5, 10).round(1)
クロスセル成約確率 = np.random.beta(3, 3, N).round(3)  # 0〜1 （beta(3,3)で成長クラスタ比率を改善）
月次提供工数時間 = np.random.uniform(1, 15, N).round(1)
時給換算原価 = np.random.choice(
    [2000, 3000, 5000, 7000, 10000], N, p=[0.10, 0.25, 0.35, 0.20, 0.10]
)
過去12ヶ月クレーム数 = np.random.poisson(0.5, N).clip(0, 5)

# LTV計算（5年間）
継続月数 = (契約継続予測年数 * 12).clip(1, 60)
顧問料収入 = 月額顧問料 * 継続月数
クロスセル収入 = クロスセル推定増収額 * クロスセル成約確率 * 契約継続予測年数
原価 = 月次提供工数時間 * 時給換算原価 * 継続月数
LTV_5年 = (顧問料収入 + クロスセル収入 - 原価).round(0).astype(int)

# 年率ROI計算
年率ROI = LTV_5年 / np.maximum(継続月数, 1) / np.maximum(月額顧問料, 1)

# クラスタ分類
# VIP: LTV上位20%
# 不採算: LTV<0 or 年率ROI<0.5
# 成長: クロスセル成約確率>=0.5 and not VIP and not 不採算
# 安定: それ以外
ltv_80pct = np.percentile(LTV_5年, 80)
VIPフラグ = LTV_5年 >= ltv_80pct
不採算フラグ = (LTV_5年 < 0) | (年率ROI < 0.1)  # ROIしきい値を0.1に緩和して不採算比率を適正化
成長フラグ = (クロスセル成約確率 >= 0.5) & ~VIPフラグ & ~不採算フラグ

クラスタ = np.where(
    VIPフラグ, "VIP",
    np.where(
        不採算フラグ, "不採算",
        np.where(成長フラグ, "成長", "安定")
    )
)

# DataFrame作成
df = pd.DataFrame({
    "顧問先ID": 顧問先ID,
    "業種": 業種,
    "月額顧問料": 月額顧問料,
    "離反リスクスコア": 離反リスクスコア,
    "クロスセル推定増収額": クロスセル推定増収額,
    "契約継続予測年数": 契約継続予測年数,
    "クロスセル成約確率": クロスセル成約確率,
    "月次提供工数時間": 月次提供工数時間,
    "時給換算原価": 時給換算原価,
    "過去12ヶ月クレーム数": 過去12ヶ月クレーム数,
    "継続月数": 継続月数,
    "顧問料収入": 顧問料収入.round(0).astype(int),
    "クロスセル収入": クロスセル収入.round(0).astype(int),
    "原価": 原価.round(0).astype(int),
    "LTV_5年": LTV_5年,
    "年率ROI": 年率ROI.round(4),
    "クラスタ": クラスタ,
})

# 保存先
output_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "ltv_train.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ サンプルデータを生成しました: {output_path}")
print(f"   行数: {len(df)}, 列数: {len(df.columns)}")
print(f"   LTV_5年 範囲: {LTV_5年.min():,} 〜 {LTV_5年.max():,}")
print(f"   クラスタ分布:")
print(df["クラスタ"].value_counts().to_string())
print(f"\n   先頭5行:")
print(df.head().to_string())
