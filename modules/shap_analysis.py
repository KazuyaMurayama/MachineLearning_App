"""
SHAP解析モジュール
==================
SHAPによるモデル解釈・可視化を担当
"""

import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from typing import Tuple, Optional
import lightgbm as lgb
import matplotlib.font_manager as fm
import sys
import os

# matplotlibのフォントキャッシュをリセット（初回のみ）
try:
    cache_dir = fm.get_cachedir()
    if cache_dir and os.path.exists(cache_dir):
        fm._rebuild()
except Exception:
    pass

# 日本語フォントの設定
def setup_japanese_font():
    """
    matplotlibで日本語を表示するためのフォント設定
    Windows/Linux（Streamlit Cloud）両対応
    """
    # 日本語フォント候補（優先順位順）
    japanese_fonts = [
        'Noto Sans CJK JP',    # Linux（Streamlit Cloud用）
        'Noto Sans JP',        # Linux代替
        'Yu Gothic',           # 游ゴシック（Windows 10+）
        'MS Gothic',           # MSゴシック（Windows）
        'Meiryo',              # メイリオ（Windows）
        'Yu Mincho',           # 游明朝（Windows）
        'MS Mincho',           # MS明朝（Windows）
        'DejaVu Sans',         # フォールバック（英語）
    ]

    # 利用可能なフォントを確認
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # 最初に見つかった日本語フォントを使用
    for font in japanese_fonts:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            plt.rcParams['font.sans-serif'] = [font]
            plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け対策
            return font

    # フォントが見つからない場合でもエラーにしない
    # Noto Sans CJKの代替パス（Streamlit Cloud）
    try:
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        pass

    return None

# モジュール読み込み時にフォント設定を実行
_font_name = setup_japanese_font()


def calculate_shap_values(
    model: lgb.LGBMRegressor,
    X: pd.DataFrame,
    max_samples: int = 1000
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    SHAP値を計算
    
    Parameters
    ----------
    model : lgb.LGBMRegressor
        学習済みモデル
    X : pd.DataFrame
        特徴量データ
    max_samples : int
        SHAP計算に使用する最大サンプル数
        
    Returns
    -------
    Tuple[np.ndarray, pd.DataFrame]
        SHAP値とサンプリングしたデータ
    """
    # サンプリング（大規模データ対応）
    if len(X) > max_samples:
        X_sample = X.sample(n=max_samples, random_state=42)
    else:
        X_sample = X.copy()
    
    # SHAP値の計算
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    return shap_values, X_sample


def create_summary_plot(
    shap_values: np.ndarray,
    X: pd.DataFrame,
    max_display: int = 20
) -> plt.Figure:
    """
    SHAP Summary Plot（beeswarm）を生成

    Parameters
    ----------
    shap_values : np.ndarray
        SHAP値
    X : pd.DataFrame
        特徴量データ
    max_display : int
        表示する特徴量の最大数

    Returns
    -------
    plt.Figure
        生成したFigure
    """
    # フォント設定を確実に適用
    setup_japanese_font()

    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(
        shap_values,
        X,
        max_display=max_display,
        show=False,
        plot_size=None
    )
    plt.tight_layout()
    return fig


def create_bar_plot(
    shap_values: np.ndarray,
    X: pd.DataFrame,
    max_display: int = 20
) -> plt.Figure:
    """
    SHAP Bar Plot（特徴量重要度）を生成

    Parameters
    ----------
    shap_values : np.ndarray
        SHAP値
    X : pd.DataFrame
        特徴量データ
    max_display : int
        表示する特徴量の最大数

    Returns
    -------
    plt.Figure
        生成したFigure
    """
    # フォント設定を確実に適用
    setup_japanese_font()

    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(
        shap_values,
        X,
        plot_type="bar",
        max_display=max_display,
        show=False,
        plot_size=None
    )
    plt.tight_layout()
    return fig


def check_japanese_font_available() -> bool:
    """
    日本語フォントが利用可能かチェック

    Returns
    -------
    bool
        日本語フォントが利用可能ならTrue
    """
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    japanese_fonts = ['Noto Sans CJK JP', 'Noto Sans JP', 'Yu Gothic', 'MS Gothic', 'Meiryo']

    for font in japanese_fonts:
        if font in available_fonts:
            return True
    return False


def convert_columns_to_romaji(df: pd.DataFrame) -> pd.DataFrame:
    """
    日本語カラム名をローマ字に変換（フォールバック用）

    Parameters
    ----------
    df : pd.DataFrame
        変換対象のDataFrame

    Returns
    -------
    pd.DataFrame
        カラム名を変換したDataFrame
    """
    # 簡易的な日本語→ローマ字マッピング
    translation_map = {
        # 年収予測
        '年齢': 'Age',
        '経験年数': 'Experience_Years',
        '学歴': 'Education',
        '部署': 'Department',
        '役職': 'Position',
        '残業時間': 'Overtime_Hours',
        'プロジェクト数': 'Projects',
        '資格数': 'Certifications',
        '年収': 'Annual_Salary',

        # 不動産
        '専有面積': 'Floor_Area',
        '築年数': 'Building_Age',
        '階数': 'Floor_Number',
        '駅徒歩分': 'Station_Minutes',
        '部屋数': 'Rooms',
        '向き': 'Direction',
        'エリア': 'Area',
        '最寄り駅種別': 'Station_Type',
        'リフォーム済': 'Renovated',
        '価格': 'Price',

        # 売上
        '来店客数': 'Customer_Count',
        '平均客単価': 'Avg_Spending',
        '従業員数': 'Staff_Count',
        '店舗面積': 'Store_Area',
        'キャンペーン実施': 'Campaign',
        '曜日': 'Day_of_Week',
        '天気': 'Weather',
        '立地': 'Location',
        '駐車場': 'Parking',
        '日次売上': 'Daily_Sales',

        # LTV
        '初回購入額': 'First_Purchase',
        '購入回数': 'Purchase_Count',
        '平均購入単価': 'Avg_Purchase',
        '会員歴月数': 'Membership_Months',
        'メール開封率': 'Email_Open_Rate',
        'レビュー投稿数': 'Review_Count',
        '会員ランク': 'Member_Rank',
        '利用チャネル': 'Channel',
        'LTV': 'LTV',

        # 離職
        '勤続年数': 'Tenure_Years',
        '月給': 'Monthly_Salary',
        '有給消化率': 'PTO_Usage_Rate',
        '評価スコア': 'Rating_Score',
        '異動回数': 'Transfer_Count',
        '直近昇給': 'Recent_Raise',
        '離職リスクスコア': 'Turnover_Risk_Score',
    }

    # カラム名を変換
    df_renamed = df.copy()
    new_columns = []
    for col in df.columns:
        if col in translation_map:
            new_columns.append(translation_map[col])
        else:
            # マッピングにない場合はそのまま
            new_columns.append(col)

    df_renamed.columns = new_columns
    return df_renamed


def display_shap_plots(
    model: lgb.LGBMRegressor,
    X: pd.DataFrame,
    max_samples: int = 1000
) -> None:
    """
    SHAP可視化をStreamlitに表示

    Parameters
    ----------
    model : lgb.LGBMRegressor
        学習済みモデル
    X : pd.DataFrame
        特徴量データ
    max_samples : int
        SHAP計算に使用する最大サンプル数
    """
    # 日本語フォントが利用できない場合は英語にフォールバック
    use_english = not check_japanese_font_available()

    if use_english:
        st.warning("⚠️ 日本語フォントが利用できないため、特徴量名を英語で表示します")
        X_display = convert_columns_to_romaji(X)
    else:
        X_display = X

    with st.spinner("SHAP値を計算中..."):
        shap_values, X_sample = calculate_shap_values(model, X_display, max_samples)
    
    # Summary Plot
    st.subheader("📊 SHAP Summary Plot")
    st.caption("各特徴量がモデル予測に与える影響を表示。赤は高い値、青は低い値を示します。")
    fig_summary = create_summary_plot(shap_values, X_sample)
    st.pyplot(fig_summary)
    plt.close(fig_summary)
    
    st.markdown("---")
    
    # Bar Plot
    st.subheader("📊 特徴量重要度（SHAP）")
    st.caption("各特徴量の平均的な影響度をランキング表示。")
    fig_bar = create_bar_plot(shap_values, X_sample)
    st.pyplot(fig_bar)
    plt.close(fig_bar)


def get_feature_importance(
    shap_values: np.ndarray,
    feature_names: list
) -> pd.DataFrame:
    """
    特徴量重要度をDataFrameとして取得
    
    Parameters
    ----------
    shap_values : np.ndarray
        SHAP値
    feature_names : list
        特徴量名のリスト
        
    Returns
    -------
    pd.DataFrame
        特徴量重要度のDataFrame
    """
    importance = np.abs(shap_values).mean(axis=0)
    df_importance = pd.DataFrame({
        '特徴量': feature_names,
        '重要度': importance
    }).sort_values('重要度', ascending=False).reset_index(drop=True)
    
    return df_importance
