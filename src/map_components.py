"""地図・ヒートマップ描画"""
import pydeck as pdk
import pandas as pd
from config import HEATMAP_RADIUS_PIXELS, HEATMAP_INTENSITY, HEATMAP_THRESHOLD


RED_RANGE = [
    [255, 255, 178, 25],
    [254, 217, 118, 85],
    [254, 178, 76, 127],
    [253, 141, 60, 170],
    [252, 78, 42, 212],
    [227, 26, 28, 255]
]

BLUE_RANGE = [
    [222, 235, 247, 25],
    [189, 215, 231, 85],
    [158, 202, 225, 127],
    [107, 174, 214, 170],
    [66, 146, 198, 212],
    [33, 113, 181, 255]
]


def create_heatmap_layer(df: pd.DataFrame, weight_col: str | None, color_range, opacity: float = 0.8) -> pdk.Layer:
    """HeatmapLayerを作成"""
    data = df[['LONGITUDE', 'LATITUDE']].copy()
    data.columns = ['lon', 'lat']
    if weight_col and weight_col in df.columns:
        data['weight'] = df[weight_col]
    else:
        data['weight'] = 1

    return pdk.Layer(
        'HeatmapLayer',
        data=data,
        get_position=['lon', 'lat'],
        get_weight='weight',
        radiusPixels=HEATMAP_RADIUS_PIXELS,
        intensity=HEATMAP_INTENSITY,
        threshold=HEATMAP_THRESHOLD,
        opacity=opacity,
        colorRange=color_range
    )


def _build_actual_tooltip(row: pd.Series) -> str:
    """実績データのツールチップHTMLを構築"""
    accident = row.get('ACCIDENT_TYPE_(CATEGORY)', '-')
    weather = row.get('WEATHER', '-')
    datetime_str = row.get('datetime_str', '-')
    location = row.get('LOCATION', '-')
    road = row.get('ROAD_TYPE', '-')
    return (
        f"<b>種別:</b> {accident}<br/>"
        f"<b>天候:</b> {weather}<br/>"
        f"<b>発生日時:</b> {datetime_str}<br/>"
        f"<b>場所:</b> {location}<br/>"
        f"<b>道路種別:</b> {road}<br/>"
        f"<b>ソース:</b> 実績"
    )


def _build_predicted_tooltip(row: pd.Series, impact_column: str) -> str:
    """予測データのツールチップHTMLを構築（影響度のみ）"""
    impact_val = row.get(impact_column, None)
    impact_text = f"{impact_val:.1f}/10" if pd.notna(impact_val) else "-"
    return f"<b>影響度:</b> {impact_text}<br/><b>ソース:</b> 予測"


def create_scatterplot_layer(df: pd.DataFrame, color, tooltip_label: str, impact_column: str | None = None, show_impact: bool = False) -> pdk.Layer:
    """ScatterplotLayerを作成（クリック可能な個別ポイント）"""
    data = df.copy()

    if 'OCCURRENCE_DATE_AND_TIME' in data.columns and pd.api.types.is_datetime64_any_dtype(data['OCCURRENCE_DATE_AND_TIME']):
        data['datetime_str'] = data['OCCURRENCE_DATE_AND_TIME'].dt.strftime('%Y年%m月%d日 %H:%M')
    else:
        data['datetime_str'] = data.get('datetime_str', '予測データ')

    data['source_label'] = tooltip_label
    if show_impact and impact_column and impact_column in data.columns:
        data['tooltip_html'] = data.apply(lambda r: _build_predicted_tooltip(r, impact_column), axis=1)
    else:
        data['tooltip_html'] = data.apply(_build_actual_tooltip, axis=1)

    return pdk.Layer(
        'ScatterplotLayer',
        data=data,
        get_position=['LONGITUDE', 'LATITUDE'],
        get_radius=100,
        get_fill_color=color,
        pickable=True,
        auto_highlight=True
    )


def create_initial_view_state(center_lat: float, center_lon: float, zoom: int) -> pdk.ViewState:
    """ViewStateを作成"""
    return pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0,
        bearing=0
    )


def render_map(actual_df: pd.DataFrame, predicted_df: pd.DataFrame, center_lat: float, center_lon: float, zoom: int, mode: str) -> pdk.Deck:
    """Pydeckマップを作成"""
    layers = []

    if mode in ("all", "actual") and not actual_df.empty:
        layers.append(create_heatmap_layer(actual_df, None, RED_RANGE, opacity=0.8))
        layers.append(create_scatterplot_layer(actual_df, [223, 59, 48, 140], "実績", show_impact=False))

    if mode in ("all", "predicted") and predicted_df is not None and not predicted_df.empty:
        layers.append(create_heatmap_layer(predicted_df, 'PREDICTED_IMPACT', BLUE_RANGE, opacity=0.6))
        layers.append(create_scatterplot_layer(predicted_df, [66, 133, 244, 170], "予測", impact_column='PREDICTED_IMPACT', show_impact=True))

    view_state = create_initial_view_state(center_lat, center_lon, zoom)

    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style='https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
        tooltip={
            'html': '{tooltip_html}',
            'style': {
                'backgroundColor': 'rgba(33, 33, 33, 0.85)',
                'color': 'white',
                'padding': '10px',
                'borderRadius': '6px'
            }
        }
    )
