"""
モデル処理モジュール
====================
LightGBMモデルの学習・予測を担当
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, Dict, Optional, List
import warnings

# 警告を抑制（NumPy 2.x互換性警告を含む）
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

# NumPy 2.x互換性: copyエラーを無視
import numpy as np
np.set_printoptions(legacy='1.25')


def preprocess_data(
    df: pd.DataFrame,
    target_col: Optional[str] = None,
    label_encoders: Optional[Dict[str, LabelEncoder]] = None,
    is_training: bool = True
) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """
    データの前処理（カテゴリ変数のエンコーディング）

    Parameters
    ----------
    df : pd.DataFrame
        入力データ
    target_col : str, optional
        目的変数のカラム名（予測時はNone）
    label_encoders : dict, optional
        既存のLabelEncoderの辞書（予測時に使用）
    is_training : bool
        学習時かどうか

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, LabelEncoder]]
        前処理済みDataFrameとLabelEncoderの辞書
    """
    df_processed = df.copy()

    if label_encoders is None:
        label_encoders = {}

    # カテゴリ変数をLabel Encoding
    for col in df_processed.columns:
        if target_col is not None and col == target_col:
            continue
            
        if df_processed[col].dtype == 'object' or df_processed[col].dtype.name == 'category':
            if is_training:
                if col not in label_encoders:
                    label_encoders[col] = LabelEncoder()
                    # 未知のカテゴリに対応するため、文字列に変換
                    str_values = df_processed[col].astype(str).fillna('__NA__')
                    transformed = label_encoders[col].fit_transform(str_values)
                    # pandasのSeriesとして代入（NumPyのarrayを避ける）
                    df_processed[col] = pd.Series(transformed, index=df_processed.index, dtype='int64')
            else:
                if col in label_encoders:
                    # 未知のカテゴリは-1にマッピング
                    df_processed[col] = df_processed[col].astype(str).fillna('__NA__')
                    known_classes = set(label_encoders[col].classes_)
                    df_processed[col] = df_processed[col].apply(
                        lambda x: label_encoders[col].transform([x])[0] 
                        if x in known_classes else -1
                    )
    
    return df_processed, label_encoders


def split_data(
    df: pd.DataFrame,
    target_col: str,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    データをtrain/testに分割

    Parameters
    ----------
    df : pd.DataFrame
        入力データ
    target_col : str
        目的変数のカラム名
    test_size : float
        テストデータの割合
    random_state : int
        乱数シード

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]
        X_train, X_test, y_train, y_test
    """
    # NumPy 2.x対応: DataFrameの値を明示的にコピー
    X = df.drop(columns=[target_col]).reset_index(drop=True)
    y = df[target_col].reset_index(drop=True)

    # NumPy配列に変換してからsplit（copy問題を回避）
    X_values = X.values.copy()
    y_values = y.values.copy()

    # 分割実行
    X_train_arr, X_test_arr, y_train_arr, y_test_arr = train_test_split(
        X_values, y_values, test_size=test_size, random_state=random_state
    )

    # DataFrameとSeriesに戻す
    X_train = pd.DataFrame(X_train_arr, columns=X.columns)
    X_test = pd.DataFrame(X_test_arr, columns=X.columns)
    y_train = pd.Series(y_train_arr, name=y.name)
    y_test = pd.Series(y_test_arr, name=y.name)

    return X_train, X_test, y_train, y_test


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 100,
    learning_rate: float = 0.1,
    max_depth: int = 6,
    random_state: int = 42
) -> lgb.LGBMRegressor:
    """
    LightGBMモデルの学習
    
    Parameters
    ----------
    X_train : pd.DataFrame
        訓練用特徴量
    y_train : pd.Series
        訓練用目的変数
    n_estimators : int
        木の数
    learning_rate : float
        学習率
    max_depth : int
        木の深さ
    random_state : int
        乱数シード
        
    Returns
    -------
    lgb.LGBMRegressor
        学習済みモデル
    """
    model = lgb.LGBMRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        random_state=random_state,
        verbose=-1,
        force_col_wise=True
    )
    
    model.fit(X_train, y_train)
    
    return model


def predict(
    model: lgb.LGBMRegressor,
    X: pd.DataFrame
) -> np.ndarray:
    """
    予測の実行
    
    Parameters
    ----------
    model : lgb.LGBMRegressor
        学習済みモデル
    X : pd.DataFrame
        予測用特徴量
        
    Returns
    -------
    np.ndarray
        予測値
    """
    return model.predict(X)


def check_feature_compatibility(
    train_features: List[str],
    target_features: List[str]
) -> Tuple[bool, List[str]]:
    """
    特徴量の整合性チェック
    
    Parameters
    ----------
    train_features : List[str]
        学習時の特徴量リスト
    target_features : List[str]
        予測対象の特徴量リスト
        
    Returns
    -------
    Tuple[bool, List[str]]
        整合性チェック結果と不足している特徴量のリスト
    """
    missing = set(train_features) - set(target_features)
    return len(missing) == 0, list(missing)
