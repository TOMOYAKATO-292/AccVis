"""地図・ヒートマップ描画"""
import pydeck as pdk
import pandas as pd
from config import HEATMAP_RADIUS_PIXELS, HEATMAP_INTENSITY, HEATMAP_THRESHOLD


def create_heatmap_layer(df: pd.DataFrame) -> pdk.Layer:
    """HeatmapLayerを作成

    Args:
        df: 事故データ（LONGITUDE, LATITUDEカラムを含む）

    Returns:
        pdk.Layer: Pydeck HeatmapLayer
    """
    # DataFrameから座標データを準備
    # Pydeckは[lon, lat]の順序を要求
    data = df[['LONGITUDE', 'LATITUDE']].copy()
    data.columns = ['lon', 'lat']

    return pdk.Layer(
        'HeatmapLayer',
        data=data,
        get_position=['lon', 'lat'],
        radiusPixels=HEATMAP_RADIUS_PIXELS,
        intensity=HEATMAP_INTENSITY,
        threshold=HEATMAP_THRESHOLD,
        opacity=0.8,
        # カラーグラデーション: 黄色（低密度）→ 赤（高密度）
        colorRange=[
            [255, 255, 178, 25],   # 黄色（低密度）
            [254, 217, 118, 85],
            [254, 178, 76, 127],
            [253, 141, 60, 170],
            [252, 78, 42, 212],
            [227, 26, 28, 255]     # 赤（高密度）
        ]
    )


def create_initial_view_state(center_lat: float, center_lon: float, zoom: int) -> pdk.ViewState:
    """ViewStateを作成

    Args:
        center_lat: 中心緯度
        center_lon: 中心経度
        zoom: ズームレベル

    Returns:
        pdk.ViewState: Pydeck ViewState
    """
    return pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0,
        bearing=0
    )


def render_map(df: pd.DataFrame, center_lat: float, center_lon: float, zoom: int) -> pdk.Deck:
    """Pydeckマップを作成

    Args:
        df: 事故データ
        center_lat: 中心緯度
        center_lon: 中心経度
        zoom: ズームレベル

    Returns:
        pdk.Deck: Pydeckマップ
    """
    heatmap_layer = create_heatmap_layer(df)
    view_state = create_initial_view_state(center_lat, center_lon, zoom)

    return pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/light-v10',
        tooltip={
            'text': '事故多発地点'
        }
    )
