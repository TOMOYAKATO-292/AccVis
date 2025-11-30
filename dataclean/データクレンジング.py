import time
import requests
import pandas as pd

# ===== 設定 =====
INPUT_CSV = "/Users/tomoyakato/開発/AccVis/data/accidents/人口データ.csv"   # 元のCSVファイル
OUTPUT_CSV = "output_with_latlon.csv"  # 出力ファイル
ADDRESS_COL = "地域"       # 市町村名が入っている列名
SLEEP_SEC = 0.3          # API呼び出し間隔（優しめに）

GSI_API_URL = "https://msearch.gsi.go.jp/address-search/AddressSearch"

# ===== 1. CSV読み込み =====
df = pd.read_csv(INPUT_CSV)

# 確認（任意）
# print(df.head())

# ===== 2. 一意な市町村名を取得 =====
unique_cities = df[ADDRESS_COL].dropna().unique()

# 市町村名 -> (lon, lat) を入れる辞書
city_to_coord = {}

# ===== 3. 国土地理院APIで緯度経度を取得する関数 =====
def fetch_latlon_from_gsi(address: str):
    """国土地理院ジオコーディングAPIから (lat, lon) を返す。見つからなければ (None, None)。"""
    try:
        params = {"q": address}
        resp = requests.get(GSI_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None, None

        # 最初の候補を採用
        feature = data[0]
        lon, lat = feature["geometry"]["coordinates"]  # [lon, lat]
        return lat, lon
    except Exception as e:
        print(f"[WARN] '{address}' でエラー: {e}")
        return None, None

# ===== 4. 一意な市町村ごとにAPIを叩いて辞書に保存 =====
for city in unique_cities:
    print(f"市町村 '{city}' の座標を取得中...")
    lat, lon = fetch_latlon_from_gsi(city)
    city_to_coord[city] = {"lat": lat, "lon": lon}
    time.sleep(SLEEP_SEC)

# ===== 5. 元データに緯度経度を結合 =====
df["lat"] = df[ADDRESS_COL].map(lambda x: city_to_coord.get(x, {}).get("lat"))
df["lon"] = df[ADDRESS_COL].map(lambda x: city_to_coord.get(x, {}).get("lon"))

# ===== 6. CSVとして出力 =====
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print("完了しました ✅ 出力ファイル:", OUTPUT_CSV)
