"""設定定数"""
from pathlib import Path

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent

# データディレクトリ
DATA_DIR = PROJECT_ROOT / "data"
ACCIDENT_DATA_DIR = DATA_DIR / "accidents"
REQUESTS_DATA_DIR = DATA_DIR / "requests"
REQUESTS_IMAGES_DIR = REQUESTS_DATA_DIR / "images"

# データファイル
ACCIDENT_DATA_FILE = ACCIDENT_DATA_DIR / "data.csv"
REQUESTS_CSV_FILE = REQUESTS_DATA_DIR / "requests.csv"

# アプリケーション設定
DEFAULT_CENTER_LAT = 35.68  # 東京
DEFAULT_CENTER_LON = 139.76
DEFAULT_ZOOM = 5

# 画像アップロード設定
MAX_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']

# 地図設定
HEATMAP_RADIUS_PIXELS = 60
HEATMAP_INTENSITY = 1
HEATMAP_THRESHOLD = 0.05

# 統計設定
TOP_N_STATISTICS = 5
TIME_PERIODS = {
    "深夜 (0-6時)": (0, 6),
    "朝 (6-12時)": (6, 12),
    "昼 (12-18時)": (12, 18),
    "夜 (18-24時)": (18, 24)
}

# 統計データファイル
STATISTICS_DATA_FILE = ACCIDENT_DATA_DIR / "statistics.csv"
