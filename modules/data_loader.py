"""
データ読み込みモジュール
========================
CSV/Excelファイルの読み込みと前処理を担当
"""

import pandas as pd
import streamlit as st
from typing import Optional


def load_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    アップロードされたファイルを読み込んでDataFrameを返す
    
    Parameters
    ----------
    uploaded_file : UploadedFile
        Streamlitのファイルアップローダーからのファイル
        
    Returns
    -------
    pd.DataFrame or None
        読み込んだDataFrame、エラー時はNone
    """
    if uploaded_file is None:
        return None
    
    try:
        # ファイル形式に応じた読み込み
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ 対応していないファイル形式です。CSV または Excel をアップロードしてください。")
            return None
        
        return df
        
    except Exception as e:
        st.error(f"❌ ファイル読み込みエラー: {str(e)}")
        return None


def display_data_info(df: pd.DataFrame, name: str = "データ") -> None:
    """
    DataFrameの基本情報を表示
    
    Parameters
    ----------
    df : pd.DataFrame
        表示するDataFrame
    name : str
        データの名前（表示用）
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("行数", f"{len(df):,}")
    with col2:
        st.metric("列数", f"{len(df.columns):,}")
    with col3:
        st.metric("欠損値", f"{df.isnull().sum().sum():,}")


def display_preview(df: pd.DataFrame, n_rows: int = 10) -> None:
    """
    DataFrameのプレビューを表示
    
    Parameters
    ----------
    df : pd.DataFrame
        表示するDataFrame
    n_rows : int
        表示する行数
    """
    st.dataframe(df.head(n_rows), use_container_width=True)


def get_column_types(df: pd.DataFrame) -> dict:
    """
    カラムのデータ型情報を取得
    
    Parameters
    ----------
    df : pd.DataFrame
        対象のDataFrame
        
    Returns
    -------
    dict
        数値列とカテゴリ列のリスト
    """
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    return {
        'numeric': numeric_cols,
        'categorical': categorical_cols
    }
