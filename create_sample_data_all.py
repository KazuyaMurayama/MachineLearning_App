"""
複数ビジネス事例のサンプルデータ作成スクリプト
================================================
様々なビジネスユースケースのサンプルデータを生成します

実行方法:
    python create_sample_data_all.py

生成されるデータセット:
1. 年収予測（従業員）
2. 不動産価格予測（マンション）
3. 売上予測（店舗）
4. 顧客生涯価値予測（LTV）
5. 離職リスクスコア予測
"""

import pandas as pd
import numpy as np
import os

# sample_dataフォルダを作成
os.makedirs('sample_data', exist_ok=True)

# 乱数シード固定（再現性のため）
np.random.seed(42)

print("="*70)
print("複数ビジネス事例のサンプルデータを生成します")
print("="*70)
print()


# ============================================
# 1. 年収予測データ（従業員）
# ============================================
def create_salary_data():
    print("[1/5] 年収予測データを作成中...")

    n_train = 1000
    n_target = 100

    # 教師データ
    data_train = {
        '年齢': np.random.randint(22, 65, n_train),
        '経験年数': np.random.randint(0, 40, n_train),
        '学歴': np.random.choice(['高卒', '専門卒', '大卒', '院卒'], n_train, p=[0.2, 0.15, 0.5, 0.15]),
        '部署': np.random.choice(['営業', '開発', '企画', '総務', '製造'], n_train),
        '役職': np.random.choice(['なし', '主任', '係長', '課長', '部長'], n_train, p=[0.5, 0.25, 0.15, 0.08, 0.02]),
        '残業時間': np.random.randint(0, 80, n_train),
        'プロジェクト数': np.random.randint(1, 15, n_train),
        '資格数': np.random.randint(0, 8, n_train),
    }

    # 年収計算（万円）
    education_bonus = {'高卒': 0, '専門卒': 30, '大卒': 50, '院卒': 100}
    position_bonus = {'なし': 0, '主任': 50, '係長': 100, '課長': 200, '部長': 400}

    data_train['年収'] = (
        data_train['年齢'] * 8 +
        data_train['経験年数'] * 12 +
        [education_bonus[e] for e in data_train['学歴']] +
        [position_bonus[p] for p in data_train['役職']] +
        data_train['残業時間'] * 1.5 +
        data_train['プロジェクト数'] * 8 +
        data_train['資格数'] * 15 +
        np.random.normal(0, 40, n_train)
    )

    df_train = pd.DataFrame(data_train)
    df_train['年収'] = df_train['年収'].clip(250, 2000).round(0).astype(int)
    df_train.to_csv('sample_data/1_salary_train.csv', index=False, encoding='utf-8-sig')

    # ターゲットデータ
    data_target = {
        '年齢': np.random.randint(22, 65, n_target),
        '経験年数': np.random.randint(0, 40, n_target),
        '学歴': np.random.choice(['高卒', '専門卒', '大卒', '院卒'], n_target, p=[0.2, 0.15, 0.5, 0.15]),
        '部署': np.random.choice(['営業', '開発', '企画', '総務', '製造'], n_target),
        '役職': np.random.choice(['なし', '主任', '係長', '課長', '部長'], n_target, p=[0.5, 0.25, 0.15, 0.08, 0.02]),
        '残業時間': np.random.randint(0, 80, n_target),
        'プロジェクト数': np.random.randint(1, 15, n_target),
        '資格数': np.random.randint(0, 8, n_target),
    }

    df_target = pd.DataFrame(data_target)
    df_target.to_csv('sample_data/1_salary_target.csv', index=False, encoding='utf-8-sig')

    print(f"  教師データ: {len(df_train)}行, 目的変数: 年収")
    print(f"  ターゲットデータ: {len(df_target)}行")
    print()


# ============================================
# 2. 不動産価格予測データ（マンション）
# ============================================
def create_real_estate_data():
    print("[2/5] 不動産価格予測データを作成中...")

    n_train = 800
    n_target = 80

    # 教師データ
    data_train = {
        '専有面積': np.random.randint(40, 150, n_train),
        '築年数': np.random.randint(0, 50, n_train),
        '階数': np.random.randint(1, 30, n_train),
        '駅徒歩分': np.random.randint(1, 30, n_train),
        '部屋数': np.random.choice([1, 2, 3, 4, 5], n_train, p=[0.1, 0.3, 0.35, 0.2, 0.05]),
        '向き': np.random.choice(['北', '東', '南', '西', '南東', '南西'], n_train),
        'エリア': np.random.choice(['都心', '副都心', '郊外', '駅近', '住宅街'], n_train),
        '最寄り駅種別': np.random.choice(['主要駅', '急行停車', '各駅停車'], n_train, p=[0.2, 0.3, 0.5]),
        'リフォーム済': np.random.choice(['あり', 'なし'], n_train, p=[0.3, 0.7]),
    }

    # 価格計算（万円）
    direction_bonus = {'北': -200, '東': 0, '南': 300, '西': -100, '南東': 200, '南西': 150}
    area_bonus = {'都心': 2000, '副都心': 1000, '郊外': 0, '駅近': 800, '住宅街': 300}
    station_bonus = {'主要駅': 500, '急行停車': 200, '各駅停車': 0}

    data_train['価格'] = (
        data_train['専有面積'] * 60 +
        -data_train['築年数'] * 80 +
        data_train['階数'] * 30 +
        -data_train['駅徒歩分'] * 50 +
        data_train['部屋数'] * 300 +
        [direction_bonus[d] for d in data_train['向き']] +
        [area_bonus[a] for a in data_train['エリア']] +
        [station_bonus[s] for s in data_train['最寄り駅種別']] +
        [500 if r == 'あり' else 0 for r in data_train['リフォーム済']] +
        np.random.normal(0, 300, n_train)
    )

    df_train = pd.DataFrame(data_train)
    df_train['価格'] = df_train['価格'].clip(1000, 20000).round(0).astype(int)
    df_train.to_csv('sample_data/2_realestate_train.csv', index=False, encoding='utf-8-sig')

    # ターゲットデータ
    data_target = {
        '専有面積': np.random.randint(40, 150, n_target),
        '築年数': np.random.randint(0, 50, n_target),
        '階数': np.random.randint(1, 30, n_target),
        '駅徒歩分': np.random.randint(1, 30, n_target),
        '部屋数': np.random.choice([1, 2, 3, 4, 5], n_target, p=[0.1, 0.3, 0.35, 0.2, 0.05]),
        '向き': np.random.choice(['北', '東', '南', '西', '南東', '南西'], n_target),
        'エリア': np.random.choice(['都心', '副都心', '郊外', '駅近', '住宅街'], n_target),
        '最寄り駅種別': np.random.choice(['主要駅', '急行停車', '各駅停車'], n_target, p=[0.2, 0.3, 0.5]),
        'リフォーム済': np.random.choice(['あり', 'なし'], n_target, p=[0.3, 0.7]),
    }

    df_target = pd.DataFrame(data_target)
    df_target.to_csv('sample_data/2_realestate_target.csv', index=False, encoding='utf-8-sig')

    print(f"  教師データ: {len(df_train)}行, 目的変数: 価格（万円）")
    print(f"  ターゲットデータ: {len(df_target)}行")
    print()


# ============================================
# 3. 売上予測データ（店舗）
# ============================================
def create_sales_data():
    print("[3/5] 売上予測データを作成中...")

    n_train = 600
    n_target = 60

    # 教師データ
    data_train = {
        '来店客数': np.random.randint(50, 500, n_train),
        '平均客単価': np.random.randint(500, 5000, n_train),
        '従業員数': np.random.randint(2, 20, n_train),
        '店舗面積': np.random.randint(30, 300, n_train),
        'キャンペーン実施': np.random.choice(['あり', 'なし'], n_train, p=[0.4, 0.6]),
        '曜日': np.random.choice(['平日', '土曜', '日曜'], n_train, p=[0.6, 0.2, 0.2]),
        '天気': np.random.choice(['晴', '曇', '雨'], n_train, p=[0.5, 0.3, 0.2]),
        '立地': np.random.choice(['駅前', 'ロードサイド', '住宅街', 'ショッピングモール'], n_train),
        '駐車場': np.random.choice(['あり', 'なし'], n_train, p=[0.7, 0.3]),
    }

    # 売上計算（万円）
    campaign_bonus = {'あり': 1.3, 'なし': 1.0}
    day_bonus = {'平日': 0.8, '土曜': 1.2, '日曜': 1.3}
    weather_bonus = {'晴': 1.1, '曇': 1.0, '雨': 0.8}
    location_bonus = {'駅前': 1.5, 'ロードサイド': 1.2, '住宅街': 0.9, 'ショッピングモール': 1.4}

    data_train['日次売上'] = (
        data_train['来店客数'] * data_train['平均客単価'] / 10000 *
        [campaign_bonus[c] for c in data_train['キャンペーン実施']] *
        [day_bonus[d] for d in data_train['曜日']] *
        [weather_bonus[w] for w in data_train['天気']] *
        [location_bonus[l] for l in data_train['立地']] *
        [1.1 if p == 'あり' else 0.9 for p in data_train['駐車場']] +
        np.random.normal(0, 10, n_train)
    )

    df_train = pd.DataFrame(data_train)
    df_train['日次売上'] = df_train['日次売上'].clip(10, 1000).round(1)
    df_train.to_csv('sample_data/3_sales_train.csv', index=False, encoding='utf-8-sig')

    # ターゲットデータ
    data_target = {
        '来店客数': np.random.randint(50, 500, n_target),
        '平均客単価': np.random.randint(500, 5000, n_target),
        '従業員数': np.random.randint(2, 20, n_target),
        '店舗面積': np.random.randint(30, 300, n_target),
        'キャンペーン実施': np.random.choice(['あり', 'なし'], n_target, p=[0.4, 0.6]),
        '曜日': np.random.choice(['平日', '土曜', '日曜'], n_target, p=[0.6, 0.2, 0.2]),
        '天気': np.random.choice(['晴', '曇', '雨'], n_target, p=[0.5, 0.3, 0.2]),
        '立地': np.random.choice(['駅前', 'ロードサイド', '住宅街', 'ショッピングモール'], n_target),
        '駐車場': np.random.choice(['あり', 'なし'], n_target, p=[0.7, 0.3]),
    }

    df_target = pd.DataFrame(data_target)
    df_target.to_csv('sample_data/3_sales_target.csv', index=False, encoding='utf-8-sig')

    print(f"  教師データ: {len(df_train)}行, 目的変数: 日次売上（万円）")
    print(f"  ターゲットデータ: {len(df_target)}行")
    print()


# ============================================
# 4. 顧客生涯価値（LTV）予測データ
# ============================================
def create_ltv_data():
    print("[4/5] 顧客生涯価値（LTV）予測データを作成中...")

    n_train = 700
    n_target = 70

    # 教師データ
    data_train = {
        '年齢': np.random.randint(18, 70, n_train),
        '初回購入額': np.random.randint(1000, 50000, n_train),
        '購入回数': np.random.randint(1, 50, n_train),
        '平均購入単価': np.random.randint(2000, 30000, n_train),
        '会員歴月数': np.random.randint(1, 120, n_train),
        'メール開封率': np.random.uniform(0, 100, n_train).round(1),
        'レビュー投稿数': np.random.randint(0, 30, n_train),
        '会員ランク': np.random.choice(['ブロンズ', 'シルバー', 'ゴールド', 'プラチナ'], n_train, p=[0.5, 0.3, 0.15, 0.05]),
        '利用チャネル': np.random.choice(['Web', 'アプリ', '店舗', '複数'], n_train, p=[0.3, 0.4, 0.2, 0.1]),
    }

    # LTV計算（万円）
    rank_multiplier = {'ブロンズ': 1.0, 'シルバー': 1.5, 'ゴールド': 2.0, 'プラチナ': 3.0}
    channel_bonus = {'Web': 1.0, 'アプリ': 1.2, '店舗': 0.9, '複数': 1.4}

    data_train['LTV'] = (
        data_train['購入回数'] * data_train['平均購入単価'] / 10000 *
        (1 + data_train['会員歴月数'] / 100) *
        (1 + data_train['メール開封率'] / 200) *
        (1 + data_train['レビュー投稿数'] / 50) *
        [rank_multiplier[r] for r in data_train['会員ランク']] *
        [channel_bonus[c] for c in data_train['利用チャネル']] +
        np.random.normal(0, 20, n_train)
    )

    df_train = pd.DataFrame(data_train)
    df_train['LTV'] = df_train['LTV'].clip(5, 500).round(1)
    df_train.to_csv('sample_data/4_ltv_train.csv', index=False, encoding='utf-8-sig')

    # ターゲットデータ
    data_target = {
        '年齢': np.random.randint(18, 70, n_target),
        '初回購入額': np.random.randint(1000, 50000, n_target),
        '購入回数': np.random.randint(1, 50, n_target),
        '平均購入単価': np.random.randint(2000, 30000, n_target),
        '会員歴月数': np.random.randint(1, 120, n_target),
        'メール開封率': np.random.uniform(0, 100, n_target).round(1),
        'レビュー投稿数': np.random.randint(0, 30, n_target),
        '会員ランク': np.random.choice(['ブロンズ', 'シルバー', 'ゴールド', 'プラチナ'], n_target, p=[0.5, 0.3, 0.15, 0.05]),
        '利用チャネル': np.random.choice(['Web', 'アプリ', '店舗', '複数'], n_target, p=[0.3, 0.4, 0.2, 0.1]),
    }

    df_target = pd.DataFrame(data_target)
    df_target.to_csv('sample_data/4_ltv_target.csv', index=False, encoding='utf-8-sig')

    print(f"  教師データ: {len(df_train)}行, 目的変数: LTV（万円）")
    print(f"  ターゲットデータ: {len(df_target)}行")
    print()


# ============================================
# 5. 離職リスクスコア予測データ
# ============================================
def create_turnover_data():
    print("[5/5] 離職リスクスコア予測データを作成中...")

    n_train = 500
    n_target = 50

    # 教師データ
    data_train = {
        '勤続年数': np.random.randint(0, 30, n_train),
        '年齢': np.random.randint(22, 65, n_train),
        '月給': np.random.randint(20, 100, n_train),
        '残業時間': np.random.randint(0, 100, n_train),
        '有給消化率': np.random.uniform(0, 100, n_train).round(1),
        '評価スコア': np.random.uniform(1, 5, n_train).round(1),
        '異動回数': np.random.randint(0, 10, n_train),
        '部署': np.random.choice(['営業', '開発', '企画', '総務', '製造', 'CS'], n_train),
        '直近昇給': np.random.choice(['あり', 'なし'], n_train, p=[0.3, 0.7]),
    }

    # 離職リスクスコア計算（0-100、高いほど離職リスク高）
    base_risk = 50

    data_train['離職リスクスコア'] = (
        base_risk +
        -data_train['勤続年数'] * 1.5 +
        -data_train['月給'] * 0.3 +
        data_train['残業時間'] * 0.4 +
        -data_train['有給消化率'] * 0.2 +
        -data_train['評価スコア'] * 5 +
        data_train['異動回数'] * 3 +
        [-15 if g == 'あり' else 10 for g in data_train['直近昇給']] +
        np.random.normal(0, 8, n_train)
    )

    df_train = pd.DataFrame(data_train)
    df_train['離職リスクスコア'] = df_train['離職リスクスコア'].clip(0, 100).round(1)
    df_train.to_csv('sample_data/5_turnover_train.csv', index=False, encoding='utf-8-sig')

    # ターゲットデータ
    data_target = {
        '勤続年数': np.random.randint(0, 30, n_target),
        '年齢': np.random.randint(22, 65, n_target),
        '月給': np.random.randint(20, 100, n_target),
        '残業時間': np.random.randint(0, 100, n_target),
        '有給消化率': np.random.uniform(0, 100, n_target).round(1),
        '評価スコア': np.random.uniform(1, 5, n_target).round(1),
        '異動回数': np.random.randint(0, 10, n_target),
        '部署': np.random.choice(['営業', '開発', '企画', '総務', '製造', 'CS'], n_target),
        '直近昇給': np.random.choice(['あり', 'なし'], n_target, p=[0.3, 0.7]),
    }

    df_target = pd.DataFrame(data_target)
    df_target.to_csv('sample_data/5_turnover_target.csv', index=False, encoding='utf-8-sig')

    print(f"  教師データ: {len(df_train)}行, 目的変数: 離職リスクスコア（0-100）")
    print(f"  ターゲットデータ: {len(df_target)}行")
    print()


# ============================================
# メイン実行
# ============================================
if __name__ == "__main__":
    create_salary_data()
    create_real_estate_data()
    create_sales_data()
    create_ltv_data()
    create_turnover_data()

    print("="*70)
    print("すべてのサンプルデータの作成が完了しました！")
    print("="*70)
    print()
    print("[生成されたファイル]")
    print("  1. 年収予測:")
    print("     - sample_data/1_salary_train.csv")
    print("     - sample_data/1_salary_target.csv")
    print()
    print("  2. 不動産価格予測:")
    print("     - sample_data/2_realestate_train.csv")
    print("     - sample_data/2_realestate_target.csv")
    print()
    print("  3. 売上予測:")
    print("     - sample_data/3_sales_train.csv")
    print("     - sample_data/3_sales_target.csv")
    print()
    print("  4. 顧客生涯価値（LTV）予測:")
    print("     - sample_data/4_ltv_train.csv")
    print("     - sample_data/4_ltv_target.csv")
    print()
    print("  5. 離職リスクスコア予測:")
    print("     - sample_data/5_turnover_train.csv")
    print("     - sample_data/5_turnover_target.csv")
    print()
    print()
    print("Streamlitアプリで各データセットを試してみてください！")
