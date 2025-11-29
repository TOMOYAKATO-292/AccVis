"""ユーティリティ関数"""
from typing import Tuple
from datetime import datetime


def validate_coordinates(lat: float, lon: float) -> Tuple[bool, str]:
    """緯度経度のバリデーション

    Args:
        lat: 緯度
        lon: 経度

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not (-90 <= lat <= 90):
        return False, "緯度は-90から90の範囲で入力してください"

    if not (-180 <= lon <= 180):
        return False, "経度は-180から180の範囲で入力してください"

    return True, ""


def format_timestamp(iso_timestamp: str) -> str:
    """ISO形式のタイムスタンプを読みやすい形式に変換

    Args:
        iso_timestamp: ISO形式のタイムスタンプ

    Returns:
        str: 読みやすい形式のタイムスタンプ（例: 2024年01月15日 08:32）
    """
    dt = datetime.fromisoformat(iso_timestamp)
    return dt.strftime("%Y年%m月%d日 %H:%M")
