"""
クロスセル分析サンプルデータ生成
150顧問先 × サービス利用マトリクス
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

INDUSTRIES = ["製造業", "小売業", "サービス業", "建設業", "飲食業", "IT業", "医療・介護", "不動産業"]
SIZES = ["1-5名", "6-20名", "21-50名", "51-100名"]
NAME_PARTS1 = ["東", "西", "南", "北", "中", "山", "川", "田", "村", "木", "金", "石", "大", "小", "新"]
NAME_PARTS2 = ["商事", "工業", "建設", "サービス", "技研", "工務店", "システム", "クリニック", "フーズ", "ホーム"]
COMPANY_TYPES = ["株式会社", "有限会社", "合同会社"]

# サービスカタログ: {名称: 月額単価}
SERVICES = {
    "記帳代行":    30000,
    "給与計算":    20000,
    "年末調整":    15000,
    "社保手続き":  20000,
    "助成金申請":  50000,
    "経営計画策定": 30000,
    "M&A支援":   100000,
    "IT導入支援":  30000,
}
SERVICE_NAMES = list(SERVICES.keys())

N_CLIENTS = 150


def generate_unique_names(n, rng):
    """重複のないユニークな顧問先名をn件生成する"""
    names = set()
    while len(names) < n:
        name = (rng.choice(NAME_PARTS1) + rng.choice(NAME_PARTS2)
                + rng.choice(COMPANY_TYPES))
        names.add(name)
    return list(names)


# 業種・規模に応じたサービス利用確率テーブル
# 行: 業種, 列: サービス
PROB_INDUSTRY = {
    "製造業":    [0.7, 0.8, 0.8, 0.7, 0.4, 0.3, 0.2, 0.4],
    "小売業":    [0.8, 0.7, 0.7, 0.6, 0.3, 0.2, 0.1, 0.3],
    "サービス業": [0.6, 0.6, 0.6, 0.5, 0.4, 0.3, 0.1, 0.5],
    "建設業":    [0.7, 0.7, 0.7, 0.8, 0.5, 0.2, 0.1, 0.2],
    "飲食業":    [0.8, 0.6, 0.6, 0.5, 0.3, 0.1, 0.0, 0.2],
    "IT業":      [0.5, 0.6, 0.6, 0.4, 0.3, 0.5, 0.2, 0.7],
    "医療・介護": [0.7, 0.8, 0.8, 0.9, 0.5, 0.2, 0.1, 0.3],
    "不動産業":  [0.7, 0.5, 0.5, 0.5, 0.3, 0.4, 0.3, 0.3],
}
# 規模による補正係数（大きいほど利用率↑）
SIZE_MULT = {"1-5名": 0.7, "6-20名": 1.0, "21-50名": 1.2, "51-100名": 1.4}

rng = np.random.RandomState(42)
unique_names = generate_unique_names(N_CLIENTS, rng)

records = []
for i in range(N_CLIENTS):
    industry = rng.choice(INDUSTRIES)
    size = rng.choice(SIZES)
    name = unique_names[i]
    base_fee = rng.choice([30000, 50000, 80000, 100000, 150000, 200000])
    years = rng.randint(1, 11)  # 契約年数1-10年

    probs = np.array(PROB_INDUSTRY[industry]) * SIZE_MULT[size]
    probs = np.clip(probs, 0.0, 0.95)

    usage = (rng.random(len(SERVICE_NAMES)) < probs).astype(int)

    row = {
        "顧問先ID": f"C{str(i+1).zfill(3)}",
        "顧問先名": name,
        "月額顧問料": base_fee,
        "業種": industry,
        "従業員規模": size,
        "契約年数": years,
    }
    for svc, u in zip(SERVICE_NAMES, usage):
        row[svc] = u
    records.append(row)

df = pd.DataFrame(records)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "crosssell_data.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"✅ サンプルデータ生成完了: {len(df)}行 → {out_path}")
print(df[["顧問先名", "業種", "従業員規模"] + SERVICE_NAMES].head(5))
print("\nサービス利用率:")
for svc in SERVICE_NAMES:
    print(f"  {svc}: {df[svc].mean()*100:.1f}%")
