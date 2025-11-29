"""物流事故ヒートマップ可視化システム - メインアプリケーション"""
import streamlit as st
from config import DEFAULT_CENTER_LAT, DEFAULT_CENTER_LON, DEFAULT_ZOOM
from src.data_loader import load_accident_data
from src.map_components import render_map
from src.filters import apply_filters, extract_filter_options
from src.utils import validate_coordinates
from src.request_handler import submit_request
from src.statistics import calculate_filtered_statistics


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
    """サイドバーのフィルタUIを描画

    Args:
        accident_data: 全事故データ

    Returns:
        pd.DataFrame: フィルタ後の事故データ
    """
    st.sidebar.title("コントロールパネル")

    # --- 位置指定セクション ---
    st.sidebar.header("📍 地図中心位置")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        input_lat = st.number_input(
            "緯度",
            min_value=-90.0,
            max_value=90.0,
            value=st.session_state.center_lat,
            format="%.6f",
            help="地図の中心にしたい緯度を入力"
        )
    with col2:
        input_lon = st.number_input(
            "経度",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.center_lon,
            format="%.6f",
            help="地図の中心にしたい経度を入力"
        )

    if st.sidebar.button("🎯 地図中心を移動"):
        is_valid, error_msg = validate_coordinates(input_lat, input_lon)
        if is_valid:
            st.session_state.center_lat = input_lat
            st.session_state.center_lon = input_lon
            st.sidebar.success("地図中心を移動しました")
            st.rerun()
        else:
            st.sidebar.error(error_msg)

    st.sidebar.divider()

    # フィルタオプション抽出
    filter_options = extract_filter_options(accident_data)

    # --- フィルタセクション ---
    st.sidebar.header("🔍 データフィルタ")

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
    if st.sidebar.button("🔄 フィルタをリセット"):
        st.rerun()

    # 統計情報
    st.sidebar.info(f"📊 表示中: {len(filtered_data):,}件 / 全体: {len(accident_data):,}件")

    st.sidebar.divider()

    # --- 要望投稿ボタン ---
    st.sidebar.header("📝 危険地点の報告")
    if st.sidebar.button("📢 危険地点を報告する", type="primary", use_container_width=True):
        st.session_state.show_request_form = True

    return filtered_data


def render_request_form():
    """要望投稿フォーム"""
    st.divider()
    st.header("📝 危険地点の要望投稿")

    with st.form("request_form"):
        st.write("事故が多い、または危険だと感じる地点を報告してください。")

        # 位置指定
        col1, col2 = st.columns(2)
        with col1:
            req_lat = st.number_input(
                "緯度 *",
                min_value=-90.0,
                max_value=90.0,
                value=st.session_state.center_lat,
                format="%.6f",
                help="報告したい地点の緯度"
            )
        with col2:
            req_lon = st.number_input(
                "経度 *",
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.center_lon,
                format="%.6f",
                help="報告したい地点の経度"
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
            height=150,
            help="必須項目です"
        )

        # 画像アップロード
        image_file = st.file_uploader(
            "画像（任意）",
            type=['jpg', 'jpeg', 'png'],
            help="現場の写真などをアップロードできます（最大5MB）"
        )

        # 送信・キャンセルボタン
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("送信する", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("キャンセル", use_container_width=True)

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
                st.session_state.show_request_form = False
                st.balloons()
                st.rerun()
            else:
                st.error(message)

        if cancelled:
            st.session_state.show_request_form = False
            st.rerun()


def render_statistics(accident_data):
    """統計情報セクションを描画

    Args:
        accident_data: 全事故データ
    """
    st.header("TOP5 統計情報")

    # フィルタオプション抽出
    filter_options = extract_filter_options(accident_data)

    # 統計用フィルターUI（エキスパンダーで折りたたみ可能）
    with st.expander("🔍 統計フィルター", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            # 年フィルタ
            stats_year_filter = st.selectbox(
                "年",
                options=[None] + filter_options['years'],
                format_func=lambda x: "全年" if x is None else str(x),
                key="stats_year"
            )

            # 月フィルタ
            stats_month_filter = st.selectbox(
                "月",
                options=[None] + filter_options['months'],
                format_func=lambda x: "全月" if x is None else f"{x}月",
                key="stats_month"
            )

        with col2:
            # 時間帯フィルタ
            hour_range_options = {
                "全時間帯": None,
                "深夜 (0-6時)": (0, 6),
                "朝 (6-12時)": (6, 12),
                "昼 (12-18時)": (12, 18),
                "夜 (18-24時)": (18, 24)
            }
            stats_hour_range_label = st.selectbox(
                "時間帯",
                options=list(hour_range_options.keys()),
                key="stats_hour_range"
            )
            stats_hour_range = hour_range_options[stats_hour_range_label]

            # 事故種類フィルタ
            stats_accident_types_filter = st.multiselect(
                "事故種類",
                options=filter_options['accident_types'],
                default=[],
                key="stats_accident_types"
            )

        with col3:
            # 天候フィルタ
            stats_weather_filter = st.multiselect(
                "天候",
                options=filter_options['weather'],
                default=[],
                key="stats_weather"
            )

            # 市区町村フィルタ
            stats_area_filter = st.multiselect(
                "市区町村",
                options=filter_options['areas'],
                default=[],
                key="stats_area"
            )

    # 統計計算
    try:
        stats = calculate_filtered_statistics(
            accident_data,
            year=stats_year_filter,
            month=stats_month_filter,
            hour_range=stats_hour_range,
            accident_types=stats_accident_types_filter if stats_accident_types_filter else None,
            weather_conditions=stats_weather_filter if stats_weather_filter else None,
            areas=stats_area_filter if stats_area_filter else None
        )
    except Exception as e:
        st.error(f"統計情報の計算に失敗しました: {str(e)}")
        return

    # 3カラムレイアウトで表示
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("事故の多い市区町村")
        if len(stats['municipalities']) > 0:
            st.dataframe(
                stats['municipalities'],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("データがありません")

    with col2:
        st.subheader("事故種類")
        if len(stats['accident_types']) > 0:
            st.dataframe(
                stats['accident_types'],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("データがありません")

    with col3:
        st.subheader("時間帯")
        if len(stats['time_periods']) > 0:
            st.dataframe(
                stats['time_periods'],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("データがありません")


def main():
    """メイン処理"""
    # セッション状態初期化
    initialize_session_state()

    # タイトル
    st.title("交通事故ヒートマップ可視化システム")
    st.markdown("""
    このシステムは、地方住民が事故多発箇所を把握し、危険な道路を避けるための判断材料を提供します。
    """)

    # データ読み込み
    try:
        accident_data = load_accident_data()
        st.sidebar.success(f"✅ 事故データ読み込み完了: {len(accident_data):,}件")
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        return

    # サイドバー（フィルタ）
    filtered_data = render_sidebar(accident_data)

    # 地図表示
    st.header("📍 事故ヒートマップ")

    try:
        # ヒートマップ描画
        deck = render_map(
            filtered_data,
            st.session_state.center_lat,
            st.session_state.center_lon,
            st.session_state.zoom
        )
        st.pydeck_chart(deck)
    except Exception as e:
        st.error(f"地図の表示に失敗しました: {str(e)}")

    # 統計情報表示
    st.divider()
    render_statistics(accident_data)

    # 要望投稿フォーム（条件付き表示）
    if st.session_state.show_request_form:
        render_request_form()


if __name__ == "__main__":
    main()
