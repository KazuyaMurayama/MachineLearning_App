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


def display_data_quality_report(df: pd.DataFrame, name: str = "データ") -> dict:
    """
    データ品質診断レポートを表示
    批判的思考: ユーザーが「このデータで学習して大丈夫か」を判断できる情報を提供

    Parameters
    ----------
    df : pd.DataFrame
        対象のDataFrame
    name : str
        データの名前

    Returns
    -------
    dict
        品質診断結果の辞書
    """
    import numpy as np

    report = {
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'missing_total': int(df.isnull().sum().sum()),
        'duplicate_rows': int(df.duplicated().sum()),
        'issues': [],
        'warnings': [],
        'info': []
    }

    col_types = get_column_types(df)
    report['numeric_cols'] = len(col_types['numeric'])
    report['categorical_cols'] = len(col_types['categorical'])

    # 品質スコア算出（100点満点）
    quality_score = 100

    # 欠損値チェック
    missing_ratio = report['missing_total'] / (report['total_rows'] * report['total_cols']) * 100
    if missing_ratio > 30:
        report['issues'].append(f"欠損値が全体の{missing_ratio:.1f}%を占めています（推奨: 30%未満）")
        quality_score -= 30
    elif missing_ratio > 10:
        report['warnings'].append(f"欠損値が全体の{missing_ratio:.1f}%あります")
        quality_score -= 15
    elif missing_ratio > 0:
        report['info'].append(f"欠損値が{report['missing_total']}件あります（全体の{missing_ratio:.1f}%）")
        quality_score -= 5

    # 重複行チェック
    if report['duplicate_rows'] > 0:
        dup_ratio = report['duplicate_rows'] / report['total_rows'] * 100
        if dup_ratio > 10:
            report['warnings'].append(f"重複行が{report['duplicate_rows']}件あります（{dup_ratio:.1f}%）")
            quality_score -= 10
        else:
            report['info'].append(f"重複行が{report['duplicate_rows']}件あります")
            quality_score -= 3

    # サンプル数チェック
    if report['total_rows'] < 30:
        report['issues'].append(f"データ行数が{report['total_rows']}件と少なめです（推奨: 30件以上）")
        quality_score -= 20
    elif report['total_rows'] < 100:
        report['warnings'].append(f"データ行数が{report['total_rows']}件です。より多くのデータで精度が向上する可能性があります")
        quality_score -= 5

    # 特徴量数 vs サンプル数の比率
    if report['total_cols'] > 1 and report['total_rows'] / report['total_cols'] < 5:
        report['warnings'].append("特徴量数に対してサンプル数が少ない可能性があります（推奨: 特徴量の5倍以上）")
        quality_score -= 10

    # 各カラムの欠損値詳細
    missing_per_col = df.isnull().sum()
    cols_with_missing = missing_per_col[missing_per_col > 0]
    report['cols_with_missing'] = cols_with_missing.to_dict()

    # 定数列チェック（値が1種類しかない列）
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    if constant_cols:
        report['warnings'].append(f"値が一定の列があります: {', '.join(constant_cols)}")
        quality_score -= 5

    report['quality_score'] = max(0, quality_score)

    # 表示
    st.markdown(f"#### 📋 {name}の品質診断")

    # スコア表示
    if report['quality_score'] >= 80:
        score_color = "green"
        score_label = "良好"
    elif report['quality_score'] >= 50:
        score_color = "orange"
        score_label = "注意"
    else:
        score_color = "red"
        score_label = "要確認"

    st.markdown(f"**データ品質スコア**: :{score_color}[{report['quality_score']}/100 ({score_label})]")

    # 基本情報
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    with info_col1:
        st.metric("数値列", f"{report['numeric_cols']}列")
    with info_col2:
        st.metric("カテゴリ列", f"{report['categorical_cols']}列")
    with info_col3:
        st.metric("重複行", f"{report['duplicate_rows']}件")
    with info_col4:
        st.metric("欠損率", f"{missing_ratio:.1f}%")

    # 問題・警告・情報の表示
    if report['issues']:
        for issue in report['issues']:
            st.error(f"🚨 {issue}")
    if report['warnings']:
        for warning in report['warnings']:
            st.warning(f"⚠️ {warning}")
    if report['info']:
        for info in report['info']:
            st.info(f"💡 {info}")

    # 欠損値の詳細（折りたたみ）
    if report['cols_with_missing']:
        with st.expander("📊 カラム別欠損値の詳細"):
            missing_df = pd.DataFrame({
                'カラム名': list(report['cols_with_missing'].keys()),
                '欠損数': list(report['cols_with_missing'].values()),
                '欠損率(%)': [v / report['total_rows'] * 100 for v in report['cols_with_missing'].values()]
            }).sort_values('欠損数', ascending=False)
            st.dataframe(missing_df, use_container_width=True, hide_index=True)

    # カラム型の詳細（折りたたみ）
    with st.expander("📊 カラム別データ型と基本統計"):
        type_info = []
        for col in df.columns:
            unique_count = df[col].nunique()
            dtype_label = "数値" if df[col].dtype in ['int64', 'float64'] else "カテゴリ"
            type_info.append({
                'カラム名': col,
                'データ型': dtype_label,
                'ユニーク数': unique_count,
                '欠損数': int(df[col].isnull().sum()),
            })
        type_df = pd.DataFrame(type_info)
        st.dataframe(type_df, use_container_width=True, hide_index=True)

    return report
