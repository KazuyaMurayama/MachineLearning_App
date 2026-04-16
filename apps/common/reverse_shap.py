"""
逆SHAPエンジン
==============
通常のSHAP: 「なぜこの予測か？」（Why）→ 要因の説明
逆SHAP:     「何を変えれば改善できるか？」（How）→ 具体的アクション提案

士業・EC共通で利用する。
"""

import numpy as np
import pandas as pd
import shap
from typing import Dict, List, Tuple, Optional


def calculate_reverse_shap(
    model,
    X: pd.DataFrame,
    feature_names: List[str],
    target_direction: str = "decrease",
    top_n: int = 5,
    max_samples: int = 500
) -> pd.DataFrame:
    """
    逆SHAP分析: 各サンプルに対して「何を変えれば予測値が改善するか」を提案。

    Parameters
    ----------
    model : LGBMRegressor or LGBMClassifier
        学習済みモデル
    X : pd.DataFrame
        分析対象データ
    feature_names : list
        特徴量名リスト
    target_direction : str
        "decrease" = 予測値を下げたい（例: 離反リスクを下げる）
        "increase" = 予測値を上げたい（例: 売上を上げる）
    top_n : int
        上位N個の改善提案を返す
    max_samples : int
        SHAP計算に使用する最大サンプル数

    Returns
    -------
    pd.DataFrame
        各サンプルの改善提案（feature, current_value, shap_impact,
        suggested_direction, estimated_effect）
    """
    if len(X) > max_samples:
        X_sample = X.sample(n=max_samples, random_state=42)
    else:
        X_sample = X.copy()

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    results = []

    for idx in range(len(X_sample)):
        row_shap = shap_values[idx]
        row_data = X_sample.iloc[idx]

        # target_directionに応じてソート方向を決定
        if target_direction == "decrease":
            # 予測値を下げたい → SHAP値が大きい（予測を上げている）特徴量が改善対象
            sorted_indices = np.argsort(-row_shap)
        else:
            # 予測値を上げたい → SHAP値が小さい（予測を下げている）特徴量が改善対象
            sorted_indices = np.argsort(row_shap)

        for rank, feat_idx in enumerate(sorted_indices[:top_n]):
            feat_name = feature_names[feat_idx]
            current_val = row_data.iloc[feat_idx]
            shap_impact = row_shap[feat_idx]

            # 改善方向の判定
            if target_direction == "decrease":
                if shap_impact > 0:
                    direction = "下げる" if isinstance(current_val, (int, float, np.integer, np.floating)) else "変更"
                else:
                    continue
            else:
                if shap_impact < 0:
                    direction = "上げる" if isinstance(current_val, (int, float, np.integer, np.floating)) else "変更"
                else:
                    continue

            results.append({
                "sample_idx": X_sample.index[idx],
                "rank": rank + 1,
                "feature": feat_name,
                "current_value": current_val,
                "shap_impact": round(float(shap_impact), 4),
                "direction": direction,
                "estimated_effect": round(abs(float(shap_impact)), 4),
            })

    return pd.DataFrame(results)


def generate_action_suggestions(
    model,
    X: pd.DataFrame,
    feature_names: List[str],
    feature_stats: Dict[str, Dict],
    target_direction: str = "decrease",
    top_n: int = 3,
) -> List[Dict]:
    """
    具体的な改善アクション提案を生成する。

    Parameters
    ----------
    model : trained model
    X : pd.DataFrame
        分析対象（1行 or 複数行）
    feature_names : list
    feature_stats : dict
        各特徴量の統計情報 {"feature_name": {"mean": x, "median": x, "q25": x, "q75": x}}
    target_direction : str
    top_n : int

    Returns
    -------
    list of dict
        改善アクション提案のリスト
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if X.ndim == 1 or len(X) == 1:
        shap_row = shap_values[0] if len(X.shape) > 1 else shap_values
        data_row = X.iloc[0] if len(X.shape) > 1 else X
    else:
        # 複数行の場合、平均SHAP値を使用
        shap_row = np.mean(shap_values, axis=0)
        data_row = X.mean(numeric_only=True)

    suggestions = []

    if target_direction == "decrease":
        sorted_indices = np.argsort(-shap_row)
    else:
        sorted_indices = np.argsort(shap_row)

    count = 0
    for feat_idx in sorted_indices:
        if count >= top_n:
            break

        feat_name = feature_names[feat_idx]
        impact = float(shap_row[feat_idx])

        # 改善余地がない場合はスキップ
        if target_direction == "decrease" and impact <= 0:
            continue
        if target_direction == "increase" and impact >= 0:
            continue

        current = float(data_row.iloc[feat_idx]) if isinstance(data_row.iloc[feat_idx], (int, float, np.integer, np.floating)) else data_row.iloc[feat_idx]

        # 統計情報から改善目標を算出
        stats = feature_stats.get(feat_name, {})
        suggestion = _build_suggestion(
            feat_name, current, impact, stats, target_direction
        )
        if suggestion:
            suggestions.append(suggestion)
            count += 1

    return suggestions


def _build_suggestion(
    feat_name: str,
    current_value,
    shap_impact: float,
    stats: Dict,
    target_direction: str
) -> Optional[Dict]:
    """個別特徴量の改善提案を構築"""
    if not isinstance(current_value, (int, float, np.integer, np.floating)):
        return {
            "feature": feat_name,
            "current": str(current_value),
            "action": f"「{feat_name}」を見直すことで予測値を約{abs(shap_impact):.1f}改善可能",
            "impact": abs(shap_impact),
            "target": "要検討",
        }

    median = stats.get("median", current_value)
    q25 = stats.get("q25", current_value)
    q75 = stats.get("q75", current_value)

    if target_direction == "decrease" and shap_impact > 0:
        # 現在の値がリスクを上げている → 値を改善方向に動かす
        if current_value > median:
            target = median
            action = f"「{feat_name}」を {current_value:.1f} → {target:.1f} に改善すると、リスクが約{abs(shap_impact):.1f}低下"
        else:
            target = q25
            action = f"「{feat_name}」を {current_value:.1f} → {target:.1f} に改善すると、リスクが約{abs(shap_impact):.1f}低下"
        if abs(target - current_value) < 0.01:
            return None
    elif target_direction == "increase" and shap_impact < 0:
        # SHAP値が負 = この特徴量が予測値を下げている
        # 改善するには: 特徴量の値を「良い方向」に動かす
        # 良い方向はSHAP値と特徴量値の相関で判断
        if current_value > median:
            # 値が高くて悪影響 → 下げる
            target = q25
            action = f"「{feat_name}」を {current_value:.1f} → {target:.1f} に改善すると、残存月数が約{abs(shap_impact):.1f}ヶ月延長"
        else:
            # 値が低くて悪影響 → 上げる
            target = q75
            action = f"「{feat_name}」を {current_value:.1f} → {target:.1f} に改善すると、残存月数が約{abs(shap_impact):.1f}ヶ月延長"
        # target==currentの場合はスキップ
        if abs(target - current_value) < 0.01:
            return None
    else:
        return None

    return {
        "feature": feat_name,
        "current": round(float(current_value), 2),
        "target": round(float(target), 2),
        "action": action,
        "impact": round(abs(float(shap_impact)), 4),
    }


def compute_feature_stats(df: pd.DataFrame, feature_names: List[str]) -> Dict[str, Dict]:
    """特徴量の統計情報を算出"""
    stats = {}
    for col in feature_names:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            stats[col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "q25": float(df[col].quantile(0.25)),
                "q75": float(df[col].quantile(0.75)),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
            }
    return stats
