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
    with st.spinner("SHAP値を計算中..."):
        shap_values, X_sample = calculate_shap_values(model, X, max_samples)
    
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
