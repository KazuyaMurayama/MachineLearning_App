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


def display_prediction_scatter(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """
    実測値 vs 予測値の散布図を表示
    論理的思考: モデルの予測精度をビジュアルで直感的に確認
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 散布図: 実測 vs 予測
    ax1 = axes[0]
    ax1.scatter(y_true, y_pred, alpha=0.5, s=20, color='#2196F3')
    min_val = min(np.min(y_true), np.min(y_pred))
    max_val = max(np.max(y_true), np.max(y_pred))
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1.5, label='Perfect Prediction')
    ax1.set_xlabel('Actual Values')
    ax1.set_ylabel('Predicted Values')
    ax1.set_title('Actual vs Predicted')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 残差プロット
    ax2 = axes[1]
    residuals = y_true - y_pred
    ax2.scatter(y_pred, residuals, alpha=0.5, s=20, color='#FF9800')
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=1.5)
    ax2.set_xlabel('Predicted Values')
    ax2.set_ylabel('Residuals (Actual - Predicted)')
    ax2.set_title('Residual Plot')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def generate_model_interpretation(metrics: Dict[str, float], y_true: np.ndarray, y_pred: np.ndarray) -> str:
    """
    モデル性能の自動解釈テキストを生成
    新規事業思考: 非エンジニアでも理解できるモデル評価
    """
    r2 = metrics['R2']
    mae = metrics['MAE']
    target_range = np.max(y_true) - np.min(y_true)
    mae_ratio = mae / target_range * 100 if target_range > 0 else 0

    lines = []

    # R2の解釈
    if r2 >= 0.9:
        lines.append("**予測精度**: 非常に高い精度のモデルです（R²≥0.9）。ビジネス活用に十分な精度があります。")
    elif r2 >= 0.7:
        lines.append("**予測精度**: 良好な精度のモデルです（R²≥0.7）。傾向の把握に有効です。")
    elif r2 >= 0.5:
        lines.append("**予測精度**: 中程度の精度です（R²≥0.5）。参考値として活用できますが、個別の精密な予測には注意が必要です。")
    else:
        lines.append("**予測精度**: 精度が低めです（R²<0.5）。特徴量の追加やデータの見直しを検討してください。")

    # MAEの解釈
    lines.append(f"**平均誤差**: 予測値は実際の値から平均 {mae:.2f} 程度ずれます（データ範囲の {mae_ratio:.1f}%）。")

    # 残差の偏り確認
    residuals = y_true - y_pred
    mean_residual = np.mean(residuals)
    if abs(mean_residual) > mae * 0.1:
        if mean_residual > 0:
            lines.append("**傾向**: モデルは全体的にやや低めに予測する傾向があります。")
        else:
            lines.append("**傾向**: モデルは全体的にやや高めに予測する傾向があります。")
    else:
        lines.append("**傾向**: 予測の偏りは小さく、バランスの良いモデルです。")

    return "\n\n".join(lines)


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
