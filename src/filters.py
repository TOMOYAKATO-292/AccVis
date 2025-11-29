"""フィルタリングロジック"""
from typing import Optional, List, Tuple, Dict
import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    year: Optional[int] = None,
    month: Optional[int] = None,
    hour_range: Optional[Tuple[int, int]] = None,
    accident_types: Optional[List[str]] = None,
    weather_conditions: Optional[List[str]] = None
) -> pd.DataFrame:
    """事故データにフィルタを適用

    Args:
        df: 事故データ
        year: フィルタする年（Noneの場合は全年）
        month: フィルタする月（1-12、Noneの場合は全月）
        hour_range: 時間帯範囲 (start_hour, end_hour)、例: (0, 6)
        accident_types: フィルタする事故種類のリスト（Noneまたは空の場合は全種類）
        weather_conditions: フィルタする天候のリスト（Noneまたは空の場合は全天候）

    Returns:
        pd.DataFrame: フィルタ後の事故データ
    """
    filtered_df = df.copy()

    # 年フィルタ
    if year is not None:
        filtered_df = filtered_df[filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.year == year]

    # 月フィルタ
    if month is not None:
        filtered_df = filtered_df[filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.month == month]

    # 時間帯フィルタ
    if hour_range is not None:
        start_hour, end_hour = hour_range
        filtered_df = filtered_df[
            (filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.hour >= start_hour) &
            (filtered_df['OCCURRENCE_DATE_AND_TIME'].dt.hour < end_hour)
        ]

    # 事故種類フィルタ
    if accident_types and len(accident_types) > 0:
        filtered_df = filtered_df[filtered_df['ACCIDENT_TYPE_(CATEGORY)'].isin(accident_types)]

    # 天候フィルタ
    if weather_conditions and len(weather_conditions) > 0:
        filtered_df = filtered_df[filtered_df['WEATHER'].isin(weather_conditions)]

    return filtered_df


def extract_filter_options(df: pd.DataFrame) -> Dict[str, List]:
    """データから利用可能なフィルタオプションを抽出

    Args:
        df: 事故データ

    Returns:
        Dict[str, List]: フィルタオプション辞書
            - years: 年のリスト
            - months: 月のリスト（1-12）
            - accident_types: 事故種類のリスト
            - weather: 天候のリスト
    """
    return {
        'years': sorted(df['OCCURRENCE_DATE_AND_TIME'].dt.year.unique().tolist()),
        'months': list(range(1, 13)),
        'accident_types': sorted(df['ACCIDENT_TYPE_(CATEGORY)'].dropna().unique().tolist()),
        'weather': sorted(df['WEATHER'].dropna().unique().tolist())
    }
