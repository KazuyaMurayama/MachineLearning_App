"""
広告ROI分析 サンプルデータ生成
12ヶ月 × 5チャネルの広告データ
"""
import pandas as pd
import numpy as np
import os

rng = np.random.RandomState(42)

CHANNELS = ["Google広告", "Meta広告", "楽天広告", "LINE広告", "TikTok広告"]
MONTHS = [f"2024年{m:02d}月" for m in range(1, 13)]

# チャネル別パラメータ: {費用ベース, ROAS平均, CVR%平均, CPA平均}
CHANNEL_PARAMS = {
    "Google広告":  {"cost_base": 300000, "roas_mean": 4.5, "cvr_mean": 2.5, "trend": 1.02},
    "Meta広告":    {"cost_base": 250000, "roas_mean": 3.8, "cvr_mean": 1.8, "trend": 0.98},
    "楽天広告":    {"cost_base": 200000, "roas_mean": 5.0, "cvr_mean": 3.0, "trend": 1.05},
    "LINE広告":    {"cost_base": 150000, "roas_mean": 2.5, "cvr_mean": 1.2, "trend": 1.08},
    "TikTok広告":  {"cost_base": 100000, "roas_mean": 2.0, "cvr_mean": 0.8, "trend": 1.15},
}

records = []
for m_idx, month in enumerate(MONTHS):
    for ch in CHANNELS:
        p = CHANNEL_PARAMS[ch]
        # 月別変動 + トレンド
        trend_mult = p["trend"] ** m_idx
        seasonal = 1.0
        if m_idx + 1 in [3, 7, 12]:
            seasonal = 1.3
        elif m_idx + 1 in [1, 2, 8]:
            seasonal = 0.8

        cost = int(p["cost_base"] * seasonal * trend_mult * rng.uniform(0.85, 1.15))
        roas = max(0.5, p["roas_mean"] * rng.uniform(0.7, 1.3) * trend_mult)
        revenue = int(cost * roas)
        impressions = int(cost / rng.uniform(5, 20))  # CPM 5-20円
        clicks = int(impressions * rng.uniform(0.01, 0.05))  # CTR 1-5%
        cvr = max(0.3, p["cvr_mean"] * rng.uniform(0.7, 1.3))
        cv = max(1, int(clicks * cvr / 100))
        cpa = int(cost / cv) if cv > 0 else 0

        records.append({
            "月": month,
            "チャネル": ch,
            "広告費": cost,
            "インプレッション数": impressions,
            "クリック数": clicks,
            "CV数": cv,
            "売上": revenue,
            "ROAS": round(roas, 2),
            "CVR(%)": round(cvr, 2),
            "CPA": cpa,
        })

df = pd.DataFrame(records)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "ad_performance.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"✅ サンプルデータ生成完了: {len(df)}行 → {out_path}")
print(df.head(3))
print(f"\nチャネル別年間サマリー:")
summary = df.groupby("チャネル").agg({"広告費": "sum", "売上": "sum", "CV数": "sum"}).reset_index()
summary["ROAS"] = (summary["売上"] / summary["広告費"]).round(2)
print(summary)
