"""統計計算モジュール

フィルター後の事故データから統計を計算し、TOP5ランキングを提供します。
"""

from typing import Dict
import pandas as pd
import numpy as np
import streamlit as st


def count_unique_accidents(df: pd.DataFrame) -> int:
    """主キーでユニークな事故数をカウント

    Args:
        df: 事故データ

    Returns:
        int: ユニークな事故数
    """
    if len(df) == 0:
        return 0

    unique_df = df.drop_duplicates(
        subset=['OCCURRENCE_DATE_AND_TIME', 'LATITUDE', 'LONGITUDE'],
        keep='first'
    )

    return len(unique_df)


def add_time_period_column(df: pd.DataFrame) -> pd.DataFrame:
    """時間帯カラムを追加

    Args:
        df: 事故データ

    Returns:
        pd.DataFrame: 時間帯カラムが追加されたデータ
    """
    df = df.copy()

    if 'OCCURRENCE_DATE_AND_TIME' not in df.columns:
        return df

    hour = df['OCCURRENCE_DATE_AND_TIME'].dt.hour

    conditions = [
        (hour >= 0) & (hour < 6),
        (hour >= 6) & (hour < 12),
        (hour >= 12) & (hour < 18),
        (hour >= 18) & (hour < 24)
    ]
    choices = ['深夜 (0-6時)', '朝 (6-12時)', '昼 (12-18時)', '夜 (18-24時)']

    df['time_period'] = np.select(conditions, choices, default='不明')

    return df


def get_top_municipalities(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """市町村別TOP Nを取得

    Args:
        df: 事故データ（ユニーク処理済み）
        top_n: 取得する上位件数

    Returns:
        pd.DataFrame: TOP N市町村
    """
    if len(df) == 0 or 'Area' not in df.columns:
        return pd.DataFrame(columns=['市区町村', '事故件数'])

    # Areaカラムの欠損値を除外
    valid_df = df[df['Area'].notna()]

    if len(valid_df) == 0:
        return pd.DataFrame(columns=['市区町村', '事故件数'])

    result = (valid_df.groupby('Area')
              .size()
              .reset_index(name='事故件数')
              .rename(columns={'Area': '市区町村'})
              .sort_values('事故件数', ascending=False)
              .head(top_n))

    return result


def get_top_accident_types(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """事故種類別TOP Nを取得

    Args:
        df: 事故データ（ユニーク処理済み）
        top_n: 取得する上位件数

    Returns:
        pd.DataFrame: TOP N事故種類
    """
    if len(df) == 0 or 'ACCIDENT_TYPE_(CATEGORY)' not in df.columns:
        return pd.DataFrame(columns=['事故種類', '事故件数'])

    # 事故種類の欠損値を除外
    valid_df = df[df['ACCIDENT_TYPE_(CATEGORY)'].notna()]

    if len(valid_df) == 0:
        return pd.DataFrame(columns=['事故種類', '事故件数'])

    result = (valid_df.groupby('ACCIDENT_TYPE_(CATEGORY)')
              .size()
              .reset_index(name='事故件数')
              .rename(columns={'ACCIDENT_TYPE_(CATEGORY)': '事故種類'})
              .sort_values('事故件数', ascending=False)
              .head(top_n))

    return result


def get_top_time_periods(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """時間帯別TOP Nを取得

    Args:
        df: 事故データ（time_periodカラム付き、ユニーク処理済み）
        top_n: 取得する上位件数

    Returns:
        pd.DataFrame: TOP N時間帯
    """
    if len(df) == 0 or 'time_period' not in df.columns:
        return pd.DataFrame(columns=['時間帯', '事故件数'])

    # 「不明」を除外
    valid_df = df[df['time_period'] != '不明']

    if len(valid_df) == 0:
        return pd.DataFrame(columns=['時間帯', '事故件数'])

    result = (valid_df.groupby('time_period')
              .size()
              .reset_index(name='事故件数')
              .rename(columns={'time_period': '時間帯'})
              .sort_values('事故件数', ascending=False)
              .head(top_n))

    return result


@st.cache_data
def calculate_filtered_statistics(
    df: pd.DataFrame,
    year: int = None,
    month: int = None,
    hour_range: tuple = None,
    accident_types: list = None,
    weather_conditions: list = None,
    areas: list = None
) -> Dict[str, pd.DataFrame]:
    """フィルター後データから統計を動的計算してTOP5を返す

    Args:
        df: 事故データ
        year: フィルタする年（Noneの場合は全年）
        month: フィルタする月（1-12、Noneの場合は全月）
        hour_range: 時間帯範囲 (start_hour, end_hour)
        accident_types: フィルタする事故種類のリスト
        weather_conditions: フィルタする天候のリスト
        areas: フィルタする市区町村のリスト

    Returns:
        Dict[str, pd.DataFrame]: 統計結果の辞書
            - 'municipalities': TOP5市町村DataFrame
            - 'accident_types': TOP5事故種類DataFrame
            - 'time_periods': TOP5時間帯DataFrame
    """
    # 空のDataFrameの場合は空の結果を返す
    if len(df) == 0:
        return {
            'municipalities': pd.DataFrame(columns=['市区町村', '事故件数']),
            'accident_types': pd.DataFrame(columns=['事故種類', '事故件数']),
            'time_periods': pd.DataFrame(columns=['時間帯', '事故件数'])
        }

    filtered_df = df.copy()

    # 統計用のフィルタを適用
    if year is not None:
        filtered_df = filtered_df[filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.year == year]

    if month is not None:
        filtered_df = filtered_df[filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.month == month]

    if hour_range is not None:
        start_hour, end_hour = hour_range
        filtered_df = filtered_df[
            (filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.hour >= start_hour) &
            (filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.hour < end_hour)
        ]

    if accident_types and len(accident_types) > 0:
        filtered_df = filtered_df[filtered_df['ACCIDENT_TYPE_(CATEGORY)'].isin(accident_types)]

    if weather_conditions and len(weather_conditions) > 0:
        filtered_df = filtered_df[filtered_df['WEATHER'].isin(weather_conditions)]

    if areas and len(areas) > 0:
        filtered_df = filtered_df[filtered_df['Area'].isin(areas)]

    # 空のDataFrameチェック
    if len(filtered_df) == 0:
        return {
            'municipalities': pd.DataFrame(columns=['市区町村', '事故件数']),
            'accident_types': pd.DataFrame(columns=['事故種類', '事故件数']),
            'time_periods': pd.DataFrame(columns=['時間帯', '事故件数'])
        }

    # ユニークな事故データを抽出
    unique_df = filtered_df.drop_duplicates(
        subset=['OCCURRENCE_DATE_AND_TIME', 'LATITUDE', 'LONGITUDE'],
        keep='first'
    )

    # 時間帯カラムを追加
    unique_df = add_time_period_column(unique_df)

    # 各種TOP5を計算
    municipalities = get_top_municipalities(unique_df, top_n=5)
    accident_types = get_top_accident_types(unique_df, top_n=5)
    time_periods = get_top_time_periods(unique_df, top_n=5)

    return {
        'municipalities': municipalities,
        'accident_types': accident_types,
        'time_periods': time_periods
    }


def validate_data_for_statistics(df: pd.DataFrame) -> tuple[bool, str]:
    """統計計算に必要なカラムが存在するか検証

    Args:
        df: 検証対象のデータフレーム

    Returns:
        tuple[bool, str]: (検証結果, エラーメッセージ)
    """
    required_columns = [
        'OCCURRENCE_DATE_AND_TIME',
        'LATITUDE',
        'LONGITUDE',
        'Area',
        'ACCIDENT_TYPE_(CATEGORY)'
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f"必須カラムが不足しています: {', '.join(missing_columns)}"

    return True, ""
