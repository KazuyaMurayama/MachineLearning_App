"""
評価指標モジュール
==================
モデルの評価指標を算出
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    評価指標を算出
    
    Parameters
    ----------
    y_true : np.ndarray
        実測値
    y_pred : np.ndarray
        予測値
        
    Returns
    -------
    Dict[str, float]
        MAE, RMSE, R2を含む辞書
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2
    }


def display_metrics(metrics: Dict[str, float]) -> None:
    """
    評価指標をStreamlitで表示
    
    Parameters
    ----------
    metrics : Dict[str, float]
        評価指標の辞書
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="MAE（平均絶対誤差）",
            value=f"{metrics['MAE']:.4f}",
            help="予測誤差の平均。小さいほど良い。"
        )
    
    with col2:
        st.metric(
            label="RMSE（二乗平均平方根誤差）",
            value=f"{metrics['RMSE']:.4f}",
            help="予測誤差の二乗平均の平方根。外れ値に敏感。小さいほど良い。"
        )
    
    with col3:
        st.metric(
            label="R²（決定係数）",
            value=f"{metrics['R2']:.4f}",
            help="モデルの説明力。1に近いほど良い。"
        )


def create_metrics_dataframe(metrics: Dict[str, float]) -> pd.DataFrame:
    """
    評価指標をDataFrameとして返す
    
    Parameters
    ----------
    metrics : Dict[str, float]
        評価指標の辞書
        
    Returns
    -------
    pd.DataFrame
        評価指標のDataFrame
    """
    return pd.DataFrame([
        {'指標': 'MAE', '値': metrics['MAE'], '説明': '平均絶対誤差'},
        {'指標': 'RMSE', '値': metrics['RMSE'], '説明': '二乗平均平方根誤差'},
        {'指標': 'R²', '値': metrics['R2'], '説明': '決定係数'},
    ])
