import csv

# 地域カラムから市町村を抜き出す関数
def extract_municipality(region_text):
    """
    地域カラムから市町村を抜き出す
    例: '北海道 札幌市' -> '札幌市'
        '北海道 札幌市 中央区' -> '札幌市 中央区'
    """
    if not region_text or region_text.strip() == '':
        return ''

    # 最初のスペースで分割して、都道府県以降を取得
    parts = region_text.split(' ', 1)
    if len(parts) > 1:
        return parts[1]
    else:
        return ''

# CSVファイルを読み込み、市町村カラムを追加して保存
input_file = 'output_with_latlon.csv'
output_file = 'output_with_municipality.csv'

with open(input_file, 'r', encoding='utf-8-sig') as infile, \
     open(output_file, 'w', encoding='utf-8-sig', newline='') as outfile:

    reader = csv.DictReader(infile)

    # 既存のフィールド名に '市町村' を追加
    fieldnames = reader.fieldnames + ['市町村']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    count_success = 0
    count_fail = 0
    total = 0

    print("抽出結果のサンプル（最初の20行）:")
    print(f"{'地域':<40} -> {'市町村':<30}")
    print("-" * 72)

    for i, row in enumerate(reader):
        total += 1
        region = row.get('地域', '')
        municipality = extract_municipality(region)

        row['市町村'] = municipality
        writer.writerow(row)

        if municipality:
            count_success += 1
        else:
            count_fail += 1

        # 最初の20行を表示
        if i < 20:
            print(f"{region:<40} -> {municipality:<30}")

print("\n" + "=" * 72)
print(f"結果を {output_file} に保存しました。")
print(f"\n統計情報:")
print(f"  総データ数: {total}")
print(f"  市町村抽出成功: {count_success}")
print(f"  市町村抽出失敗: {count_fail}")
