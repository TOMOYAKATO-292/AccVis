import pandas as pd

# CSVファイルを読み込む
economic_df = pd.read_csv('/Users/tomoyakato/開発/AccVis/data/accidents/economic_impact.csv')
population_df = pd.read_csv('/Users/tomoyakato/開発/AccVis/data/accidents/output_population.csv')

# それぞれのデータフレームでAreaと市町村を重複削除
economic_distinct = economic_df.drop_duplicates(subset=['Area'])
population_distinct = population_df.drop_duplicates(subset=['市町村'])

# 重複削除後のデータで結合
merged_df = pd.merge(
    economic_distinct,
    population_distinct,
    left_on='Area',
    right_on='市町村',
    how='inner'
)

# 結果を確認
print(f"economic_df: {len(economic_df)}行 → distinct後: {len(economic_distinct)}行")
print(f"population_df: {len(population_df)}行 → distinct後: {len(population_distinct)}行")
print(f"merged_df: {len(merged_df)}行")
print("\n結合後のカラム:")
print(merged_df.columns.tolist())
print("\n結合後の最初の5行:")
print(merged_df.head())

# 必要なカラムのみを選択
required_columns = [
    'LATITUDE',
    'LONGITUDE',
    'ACCIDENT_TYPE_(CATEGORY)',
    'ROAD_TYPE',
    'WEATHER',
    'IMPACT',
    'A6103_流出人口（県内他市区町村で従業・通学している人口）【人】'
]
merged_df = merged_df[required_columns]

# 必要に応じて結果を保存
merged_df.to_csv('/Users/tomoyakato/開発/AccVis/data/accidents/merged_data.csv', index=False)