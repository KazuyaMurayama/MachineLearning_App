"""
サンプルデータ生成スクリプト
150顧問先 × 12ヶ月の請求・入金データを生成
遅延パターン: 正常(70%)=0-5日 / 一時遅延(20%)=6-15日 / 常習遅延(10%)=16-60日
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
N_CLIENTS = 150
N_MONTHS = 12
BASE_YEAR = 2024


def generate_unique_names(n, rng):
    """重複のないユニークな顧問先名をn件生成する"""
    names = set()
    while len(names) < n:
        name = (rng.choice(NAME_PARTS1) + rng.choice(NAME_PARTS2)
                + rng.choice(COMPANY_TYPES))
        names.add(name)
    return list(names)


rng = np.random.RandomState(42)
unique_names = generate_unique_names(N_CLIENTS, rng)

# 顧問先ごとの特性を決める（遅延タイプを明示的に割り当てて設計比率を保証）
delay_types = (["正常"] * int(N_CLIENTS * 0.70)
               + ["一時遅延"] * int(N_CLIENTS * 0.20)
               + ["常習遅延"] * int(N_CLIENTS * 0.10))
rng.shuffle(delay_types)

profiles = []
for i in range(N_CLIENTS):
    delay_type = delay_types[i]
    worsening = (delay_type != "正常") and (rng.random() < 0.30)

    profiles.append({
        "顧問先ID": f"C{str(i+1).zfill(3)}",
        "顧問先名": unique_names[i],
        "月額顧問料": rng.choice([30000, 50000, 80000, 100000, 150000, 200000]),
        "業種": rng.choice(INDUSTRIES),
        "従業員規模": rng.choice(SIZES),
        "delay_type": delay_type,
        "worsening": worsening,
    })

# 月ラベル: 2024年01月 〜 2024年12月
month_labels = [f"{BASE_YEAR}年{m:02d}月" for m in range(1, N_MONTHS + 1)]

records = []
for profile in profiles:
    delay_type = profile["delay_type"]
    worsening = profile["worsening"]
    for m_idx, month_label in enumerate(month_labels):
        # 遅延日数を決定
        if delay_type == "正常":
            base_delay = int(rng.randint(0, 6))
        elif delay_type == "一時遅延":
            if rng.random() < 0.35:
                base_delay = int(rng.randint(6, 16))
            else:
                base_delay = int(rng.randint(0, 6))
        else:  # 常習遅延
            base_delay = int(rng.randint(16, 61))

        # 悪化傾向: 直近3ヶ月(m_idx >= 9)で段階的に悪化
        if worsening and m_idx >= 9:
            extra = int((m_idx - 8) * rng.uniform(3.0, 8.0))
            base_delay = min(base_delay + extra, 90)

        # 請求日: 毎月月初
        invoice_dt = pd.Timestamp(year=BASE_YEAR, month=m_idx + 1, day=1)
        payment_dt = invoice_dt + pd.Timedelta(days=30 + base_delay)

        records.append({
            "顧問先ID": profile["顧問先ID"],
            "顧問先名": profile["顧問先名"],
            "月額顧問料": profile["月額顧問料"],
            "請求年月": month_label,
            "請求日": invoice_dt.strftime("%Y-%m-%d"),
            "入金日": payment_dt.strftime("%Y-%m-%d"),
            "入金遅延日数": base_delay,
            "業種": profile["業種"],
            "従業員規模": profile["従業員規模"],
        })

df = pd.DataFrame(records)
df = df[["顧問先ID", "顧問先名", "月額顧問料", "請求年月", "請求日", "入金日", "入金遅延日数", "業種", "従業員規模"]]

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "payment_data.csv")
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"✅ サンプルデータ生成完了: {len(df)}行 → {out_path}")
print(df.head(3))
print("\n遅延日数分布:")
print(df["入金遅延日数"].describe())
