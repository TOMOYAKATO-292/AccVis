"""物流事故ヒートマップ可視化システム - メインアプリケーション"""
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt
from config import DEFAULT_CENTER_LAT, DEFAULT_CENTER_LON, DEFAULT_ZOOM
from src.data_loader import load_accident_data
from src.map_components import render_map
from src.filters import apply_filters, extract_filter_options
from src.utils import validate_coordinates
from src.request_handler import submit_request
from src.statistics import calculate_filtered_statistics
from src.styles import get_google_cloud_css


# ページ設定
st.set_page_config(
    page_title="物流事故ヒートマップ可視化システム",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """セッション状態の初期化"""
    if 'center_lat' not in st.session_state:
        st.session_state.center_lat = DEFAULT_CENTER_LAT
    if 'center_lon' not in st.session_state:
        st.session_state.center_lon = DEFAULT_CENTER_LON
    if 'zoom' not in st.session_state:
        st.session_state.zoom = DEFAULT_ZOOM
    if 'show_request_form' not in st.session_state:
        st.session_state.show_request_form = False


def render_sidebar(accident_data):
    """サイドバーのフィルタUIを描画"""
    # タイトル削除: st.sidebar.title("コントロールパネル") は削除

    # --- 位置指定セクション ---
    st.sidebar.markdown('<p class="sidebar-header">📍 地図中心位置</p>', unsafe_allow_html=True)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        input_lat = st.number_input(
            "緯度",
            min_value=-90.0,
            max_value=90.0,
            value=st.session_state.center_lat,
            format="%.6f"
        )
    with col2:
        input_lon = st.number_input(
            "経度",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.center_lon,
            format="%.6f"
        )

    if st.sidebar.button("🎯 移動", use_container_width=True):
        is_valid, error_msg = validate_coordinates(input_lat, input_lon)
        if is_valid:
            st.session_state.center_lat = input_lat
            st.session_state.center_lon = input_lon
            st.sidebar.success("移動しました")
            st.rerun()
        else:
            st.sidebar.error(error_msg)

    st.sidebar.divider()

    # フィルタオプション抽出
    filter_options = extract_filter_options(accident_data)

    # --- フィルタセクション ---
    st.sidebar.markdown('<p class="sidebar-header">🔍 データフィルタ</p>', unsafe_allow_html=True)

    # 年フィルタ
    year_filter = st.sidebar.selectbox(
        "年",
        options=[None] + filter_options['years'],
        format_func=lambda x: "全年" if x is None else str(x)
    )

    # 月フィルタ
    month_filter = st.sidebar.selectbox(
        "月",
        options=[None] + filter_options['months'],
        format_func=lambda x: "全月" if x is None else f"{x}月"
    )

    # 時間帯フィルタ
    hour_range_options = {
        "全時間帯": None,
        "深夜 (0-6時)": (0, 6),
        "朝 (6-12時)": (6, 12),
        "昼 (12-18時)": (12, 18),
        "夜 (18-24時)": (18, 24)
    }
    hour_range_label = st.sidebar.selectbox(
        "時間帯",
        options=list(hour_range_options.keys())
    )
    hour_range = hour_range_options[hour_range_label]

    # 事故種類フィルタ
    accident_types_filter = st.sidebar.multiselect(
        "事故種類",
        options=filter_options['accident_types'],
        default=[]
    )

    # 天候フィルタ
    weather_filter = st.sidebar.multiselect(
        "天候",
        options=filter_options['weather'],
        default=[]
    )

    # 市区町村フィルタ
    area_filter = st.sidebar.multiselect(
        "市区町村",
        options=filter_options['areas'],
        default=[]
    )

    # フィルタ適用
    filtered_data = apply_filters(
        accident_data,
        year=year_filter,
        month=month_filter,
        hour_range=hour_range,
        accident_types=accident_types_filter if accident_types_filter else None,
        weather_conditions=weather_filter if weather_filter else None,
        areas=area_filter if area_filter else None
    )

    # フィルタリセット
    if st.sidebar.button("🔄 リセット", use_container_width=True):
        st.rerun()

    # 統計情報
    st.sidebar.markdown(f"""
    <div style="margin-top: 20px; padding: 10px; background-color: #E8F0FE; border-radius: 8px; color: #1967D2; font-size: 0.9rem; text-align: center;">
        <b>表示中: {len(filtered_data):,} 件</b> <br>
        <span style="font-size: 0.8rem; color: #5F6368;">(全体: {len(accident_data):,} 件)</span>
    </div>
    """, unsafe_allow_html=True)

    return filtered_data


def render_request_form():
    """要望投稿フォーム"""
    st.markdown('<h2 class="main-title">📝 危険地点の報告</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">事故が多い、または危険だと感じる地点を報告してください。</p>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        with st.form("request_form"):
            # 位置指定
            col1, col2 = st.columns(2)
            with col1:
                req_lat = st.number_input(
                    "緯度 *",
                    min_value=-90.0,
                    max_value=90.0,
                    value=st.session_state.center_lat,
                    format="%.6f"
                )
            with col2:
                req_lon = st.number_input(
                    "経度 *",
                    min_value=-180.0,
                    max_value=180.0,
                    value=st.session_state.center_lon,
                    format="%.6f"
                )

            # 住所（任意）
            address = st.text_input(
                "住所・場所の説明（任意）",
                placeholder="例: 〇〇交差点、△△商店前"
            )

            # 要望内容
            description = st.text_area(
                "要望内容 *",
                placeholder="危険だと感じる理由、改善してほしいことなどを記入してください",
                height=150
            )

            # 画像アップロード
            image_file = st.file_uploader(
                "画像（任意）",
                type=['jpg', 'jpeg', 'png']
            )

            st.markdown("<br>", unsafe_allow_html=True)
            
            # 送信ボタン
            submitted = st.form_submit_button("送信する", type="primary", use_container_width=True)

            if submitted:
                success, message = submit_request(
                    req_lat,
                    req_lon,
                    description,
                    address,
                    image_file
                )

                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)


def render_statistics(accident_data, filtered_data):
    """統計情報セクションを描画"""
    st.markdown('<h2 class="main-title">📊 事故統計ダッシュボード</h2>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("表示件数", f"{len(filtered_data):,}")
    with col2:
        ratio = (len(filtered_data) / len(accident_data)) * 100
        st.metric("表示率", f"{ratio:.1f}%")
    with col3:
        if 'Area' in filtered_data.columns and not filtered_data.empty:
            top_area = filtered_data['Area'].mode().iloc[0]
            st.metric("最多事故エリア", top_area)
        else:
            st.metric("最多事故エリア", "-")
    with col4:
        if 'ACCIDENT_TYPE_(CATEGORY)' in filtered_data.columns and not filtered_data.empty:
            top_type = filtered_data['ACCIDENT_TYPE_(CATEGORY)'].mode().iloc[0]
            st.metric("最多事故種別", top_type)
        else:
            st.metric("最多事故種別", "-")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<p class="dashboard-card-title">事故の多い市区町村 (TOP 10)</p>', unsafe_allow_html=True)
        if 'Area' in filtered_data.columns:
            city_counts = filtered_data['Area'].value_counts().head(10).reset_index()
            city_counts.columns = ['市区町村', '件数']
            
            tab_chart, tab_data = st.tabs(["📊 グラフ", "📄 データ"])
            with tab_chart:
                chart = alt.Chart(city_counts).mark_bar().encode(
                    x=alt.X('件数', title=None),
                    y=alt.Y('市区町村', sort='-x', title=None),
                    color=alt.value('#4285F4'),
                    tooltip=['市区町村', '件数']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            with tab_data:
                st.dataframe(city_counts, use_container_width=True, hide_index=True)
        else:
            st.info("データがありません")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<p class="dashboard-card-title">事故種類別内訳</p>', unsafe_allow_html=True)
        if 'ACCIDENT_TYPE_(CATEGORY)' in filtered_data.columns:
            type_counts = filtered_data['ACCIDENT_TYPE_(CATEGORY)'].value_counts().reset_index()
            type_counts.columns = ['事故類型', '件数']
            
            tab_chart, tab_data = st.tabs(["📊 グラフ", "📄 データ"])
            with tab_chart:
                chart = alt.Chart(type_counts).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="件数", type="quantitative"),
                    color=alt.Color(field="事故類型", type="nominal", legend=alt.Legend(title=None)),
                    tooltip=['事故類型', '件数']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            with tab_data:
                st.dataframe(type_counts, use_container_width=True, hide_index=True)
        else:
            st.info("データがありません")
        st.markdown('</div>', unsafe_allow_html=True)

    # Charts Row 2
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-card-title">時間帯別発生件数</p>', unsafe_allow_html=True)
    if 'OCCURRENCE_DATE_AND_TIME' in filtered_data.columns:
        # 時間帯集計
        hours = filtered_data['OCCURRENCE_DATE_AND_TIME'].dt.hour
        hour_counts = hours.value_counts().sort_index().reset_index()
        hour_counts.columns = ['時間', '件数']
        
        tab_chart, tab_data = st.tabs(["📊 グラフ", "📄 データ"])
        with tab_chart:
            chart = alt.Chart(hour_counts).mark_area(
                line={'color':'#1A73E8'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1A73E8', offset=0),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('時間', title='時間 (0-23時)'),
                y=alt.Y('件数', title=None),
                tooltip=['時間', '件数']
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        with tab_data:
            st.dataframe(hour_counts, use_container_width=True, hide_index=True)
    else:
        st.info("データがありません")
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """メイン処理"""
    initialize_session_state()
    st.markdown(get_google_cloud_css(), unsafe_allow_html=True)

    # データ読み込み
    try:
        accident_data = load_accident_data()
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        return

    # トップナビゲーション
    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["マップ & フィルタ", "ダッシュボード", "危険地点の報告"],
            icons=["map", "bar-chart", "exclamation-triangle"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent", "margin-bottom": "1rem"},
                "icon": {"color": "#5f6368", "font-size": "14px"}, 
                "nav-link": {
                    "font-size": "14px", 
                    "text-align": "center", 
                    "margin": "0px 10px", 
                    "--hover-color": "#F1F3F4", 
                    "color": "#5f6368",
                    "background-color": "#FFFFFF",
                    "border-radius": "20px",
                    "border": "1px solid #DADCE0",
                    "padding": "0.5rem 1rem"
                },
                "nav-link-selected": {
                    "background-color": "#E8F0FE", 
                    "color": "#1967D2", 
                    "font-weight": "600", 
                    "border": "1px solid #E8F0FE"
                },
            }
        )

    # サイドバー（共通）
    filtered_data = accident_data
    if selected in ["マップ & フィルタ", "ダッシュボード"]:
        filtered_data = render_sidebar(accident_data)
    else:
        with st.sidebar:
            st.info("危険地点の報告ページです。地図上の位置を指定して報告してください。")

    # コンテンツ表示
    if selected == "マップ & フィルタ":
        st.markdown('<h2 class="main-title">📍 事故ヒートマップ</h2>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">地図を操作して事故多発地点を確認できます。</p>', unsafe_allow_html=True)
        
        try:
            deck = render_map(
                filtered_data,
                st.session_state.center_lat,
                st.session_state.center_lon,
                st.session_state.zoom
            )
            st.pydeck_chart(deck)
        except Exception as e:
            st.error(f"地図の表示に失敗しました: {str(e)}")

    elif selected == "ダッシュボード":
        render_statistics(accident_data, filtered_data)

    elif selected == "危険地点の報告":
        render_request_form()


if __name__ == "__main__":
    main()
