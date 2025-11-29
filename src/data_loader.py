"""データ読み込み・キャッシング"""
import pandas as pd
import streamlit as st
from config import ACCIDENT_DATA_FILE


@st.cache_data
def load_accident_data() -> pd.DataFrame:
    """CSV形式の事故データを読み込み

    Returns:
        pd.DataFrame: 事故データ（日時はdatetime型に変換済み）
    """
    # CSVファイルを読み込み（エラー行はスキップ）
    df = pd.read_csv(ACCIDENT_DATA_FILE, on_bad_lines='skip', encoding='utf-8')

    # 日時をdatetime型に変換（エラーは強制的に無視）
    df['OCCURRENCE_DATE_AND_TIME'] = pd.to_datetime(
        df['OCCURRENCE_DATE_AND_TIME'],
        format='mixed',
        errors='coerce'
    )

    # 日時の変換に失敗した行を除外
    df = df.dropna(subset=['OCCURRENCE_DATE_AND_TIME'])

    # 緯度経度が欠損している行も除外
    df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])

    return df
