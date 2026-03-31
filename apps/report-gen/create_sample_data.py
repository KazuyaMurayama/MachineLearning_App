"""
月次レポート自動生成用 サンプルCSV生成
======================================
freee/MF試算表エクスポートを模した月次財務データ
データソース: freee会計 → 試算表 → CSVエクスポート

2つのファイルを生成:
  1. 当期データ（12ヶ月: 2025年4月〜2026年3月）
  2. 前期データ（12ヶ月: 2024年4月〜2025年3月）
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)

# === 顧問先情報 ===
CLIENT_NAME = "株式会社サンプル商事"
FISCAL_YEAR_CURRENT = "2025年度"  # 2025/4〜2026/3
FISCAL_YEAR_PREV = "2024年度"     # 2024/4〜2025/3

# === 勘定科目の基準値（月次平均、万円） ===
ACCOUNTS = {
    "売上高": {"base": 1200, "seasonality": [0.85, 0.90, 1.0, 1.05, 0.95, 0.90, 0.80, 0.85, 1.10, 1.15, 1.20, 1.25], "noise": 0.08, "growth": 0.05},
    "売上原価": {"base": 720, "seasonality": [0.85, 0.90, 1.0, 1.05, 0.95, 0.90, 0.80, 0.85, 1.10, 1.15, 1.20, 1.25], "noise": 0.06, "growth": 0.04},
    "人件費": {"base": 200, "seasonality": [1.0]*11 + [1.3], "noise": 0.02, "growth": 0.03},  # 12月賞与
    "地代家賃": {"base": 50, "seasonality": [1.0]*12, "noise": 0.0, "growth": 0.0},  # 固定費
    "通信費": {"base": 8, "seasonality": [1.0]*12, "noise": 0.05, "growth": 0.02},
    "広告宣伝費": {"base": 30, "seasonality": [1.2, 1.0, 0.8, 0.8, 0.9, 1.0, 1.5, 1.0, 1.0, 1.2, 1.3, 1.0], "noise": 0.15, "growth": 0.10},
    "消耗品費": {"base": 5, "seasonality": [1.0]*12, "noise": 0.10, "growth": 0.02},
    "交際費": {"base": 10, "seasonality": [1.0, 0.8, 1.2, 1.0, 1.0, 0.8, 0.5, 0.5, 1.0, 1.0, 1.2, 1.5], "noise": 0.20, "growth": 0.0},
    "旅費交通費": {"base": 12, "seasonality": [0.8, 0.9, 1.0, 1.0, 1.0, 1.1, 0.6, 0.6, 1.0, 1.1, 1.2, 1.0], "noise": 0.15, "growth": 0.03},
    "水道光熱費": {"base": 6, "seasonality": [1.3, 1.2, 1.0, 0.8, 0.7, 0.8, 1.0, 1.2, 1.0, 0.8, 0.9, 1.2], "noise": 0.05, "growth": 0.05},
    "支払利息": {"base": 3, "seasonality": [1.0]*12, "noise": 0.0, "growth": -0.05},  # 借入金返済で減少
    "雑費": {"base": 4, "seasonality": [1.0]*12, "noise": 0.20, "growth": 0.0},
}

def generate_monthly_data(base_year_start, is_current=True):
    """12ヶ月分の月次試算表データを生成"""
    months = pd.date_range(base_year_start, periods=12, freq="MS")
    rows = []
    for i, month in enumerate(months):
        row = {"年月": month.strftime("%Y年%m月")}
        for acct, params in ACCOUNTS.items():
            base = params["base"]
            season = params["seasonality"][i]
            noise = 1 + np.random.normal(0, params["noise"])
            growth = 1 + params["growth"] if is_current else 1.0
            # 当期は異常値を1箇所仕込む（デモ用）
            anomaly = 1.0
            if is_current and acct == "広告宣伝費" and i == 6:  # 10月に異常増
                anomaly = 2.5
            if is_current and acct == "交際費" and i == 11:  # 3月に異常増
                anomaly = 3.0
            val = int(base * season * noise * growth * anomaly)
            row[acct] = val
        # 計算科目
        row["売上総利益"] = row["売上高"] - row["売上原価"]
        販管費 = sum(row[k] for k in ACCOUNTS if k not in ["売上高", "売上原価", "支払利息"])
        row["販売管理費計"] = 販管費
        row["営業利益"] = row["売上総利益"] - 販管費
        row["経常利益"] = row["営業利益"] - row["支払利息"]
        rows.append(row)
    return pd.DataFrame(rows)

# 生成
df_current = generate_monthly_data("2025-04-01", is_current=True)
df_prev = generate_monthly_data("2024-04-01", is_current=False)

# 保存
out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(out_dir, exist_ok=True)
df_current.to_csv(os.path.join(out_dir, "trial_balance_current.csv"), index=False, encoding="utf-8-sig")
df_prev.to_csv(os.path.join(out_dir, "trial_balance_prev.csv"), index=False, encoding="utf-8-sig")

print(f"[当期] {FISCAL_YEAR_CURRENT}: {len(df_current)}行, 科目数={len(df_current.columns)-1}")
print(f"[前期] {FISCAL_YEAR_PREV}: {len(df_prev)}行, 科目数={len(df_prev.columns)-1}")
print(f"Saved to {out_dir}")
