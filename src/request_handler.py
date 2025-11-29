"""要望投稿処理"""
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from PIL import Image
import streamlit as st

from config import (
    REQUESTS_CSV_FILE,
    REQUESTS_IMAGES_DIR,
    MAX_IMAGE_SIZE_MB,
    ALLOWED_IMAGE_TYPES,
    REQUESTS_DATA_DIR
)


def generate_request_id() -> str:
    """一意の要望IDを生成

    Returns:
        str: 要望ID（例: req_20241129_143025_a1b2c3d4）
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"req_{timestamp}_{unique_id}"


def validate_image(uploaded_file) -> Tuple[bool, str]:
    """画像ファイルのバリデーション

    Args:
        uploaded_file: Streamlitのアップロードファイル

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if uploaded_file is None:
        return True, ""  # 画像は任意

    # ファイルサイズチェック
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"画像サイズが{MAX_IMAGE_SIZE_MB}MBを超えています（{file_size_mb:.2f}MB）"

    # ファイル形式チェック
    if uploaded_file.type not in ALLOWED_IMAGE_TYPES:
        return False, f"JPEG または PNG 形式の画像をアップロードしてください（現在: {uploaded_file.type}）"

    return True, ""


def save_image(uploaded_file, request_id: str) -> Optional[str]:
    """画像を保存

    Args:
        uploaded_file: Streamlitのアップロードファイル
        request_id: 要望ID

    Returns:
        Optional[str]: 保存したファイルパス（相対パス）、失敗時はNone
    """
    if uploaded_file is None:
        return None

    try:
        # 拡張子を取得
        ext = 'jpg' if uploaded_file.type == 'image/jpeg' else 'png'
        filename = f"{request_id}.{ext}"
        filepath = REQUESTS_IMAGES_DIR / filename

        # ディレクトリ作成
        REQUESTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        # 画像を保存
        image = Image.open(uploaded_file)
        image.save(filepath)

        # 相対パスを返す
        return f"data/requests/images/{filename}"
    except Exception as e:
        st.error(f"画像の保存に失敗しました: {str(e)}")
        return None


def save_request_metadata(
    request_id: str,
    latitude: float,
    longitude: float,
    description: str,
    address: Optional[str],
    image_path: Optional[str]
) -> bool:
    """要望メタデータをCSVファイルに追記保存

    Args:
        request_id: 要望ID
        latitude: 緯度
        longitude: 経度
        description: 要望内容
        address: 住所（任意）
        image_path: 画像パス（任意）

    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # ディレクトリ作成
        REQUESTS_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 新規要望データ
        new_request = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'address': address if address else '',
            'image_path': image_path if image_path else ''
        }

        # ファイルが存在する場合は追記、存在しない場合は新規作成
        if REQUESTS_CSV_FILE.exists():
            df = pd.read_csv(REQUESTS_CSV_FILE)
            df = pd.concat([df, pd.DataFrame([new_request])], ignore_index=True)
        else:
            df = pd.DataFrame([new_request])

        df.to_csv(REQUESTS_CSV_FILE, index=False, encoding='utf-8')
        return True

    except Exception as e:
        st.error(f"要望の保存に失敗しました: {str(e)}")
        return False


def submit_request(
    latitude: float,
    longitude: float,
    description: str,
    address: Optional[str],
    image_file
) -> Tuple[bool, str]:
    """要望を投稿

    Args:
        latitude: 緯度
        longitude: 経度
        description: 要望内容
        address: 住所（任意）
        image_file: 画像ファイル（任意）

    Returns:
        Tuple[bool, str]: (success, message)
    """
    # バリデーション
    if not description or len(description.strip()) == 0:
        return False, "要望内容を入力してください"

    # 画像バリデーション
    is_valid, error_msg = validate_image(image_file)
    if not is_valid:
        return False, error_msg

    # 要望ID生成
    request_id = generate_request_id()

    # 画像保存
    image_path = save_image(image_file, request_id)

    # メタデータ保存
    success = save_request_metadata(
        request_id,
        latitude,
        longitude,
        description,
        address,
        image_path
    )

    if success:
        return True, "要望を受け付けました。ご協力ありがとうございます。"
    else:
        return False, "送信に失敗しました。時間をおいて再度お試しください。"
