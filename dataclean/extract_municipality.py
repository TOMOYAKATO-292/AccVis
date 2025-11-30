import pandas as pd
import re

# CSVファイルを読み込み
df = pd.read_csv('output_with_latlon.csv')

# 地域カラムから市町村を抜き出す関数
def extract_municipality(region_text):
    """
    地域カラムから市町村を抜き出す
    例: '北海道 札幌市' -> '札幌市'
        '北海道 札幌市 中央区' -> '札幌市 中央区'
    """
    if pd.isna(region_text):
        return None

    # 最初のスペースで分割して、都道府県以降を取得
    parts = region_text.split(' ', 1)
    if len(parts) > 1:
        return parts[1]
    else:
        return None

# 市町村カラムを新規作成
df['市町村'] = df['地域'].apply(extract_municipality)

# 結果を表示（最初の20行）
print("抽出結果のサンプル:")
print(df[['地域', '市町村']].head(20))

# 結果をCSVファイルに保存
output_file = 'output_with_municipality.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n結果を {output_file} に保存しました。")

# 統計情報を表示
print(f"\n総データ数: {len(df)}")
print(f"市町村抽出成功: {df['市町村'].notna().sum()}")
print(f"市町村抽出失敗: {df['市町村'].isna().sum()}")
