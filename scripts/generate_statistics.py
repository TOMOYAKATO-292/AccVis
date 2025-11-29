"""統計用CSV生成スクリプト

このスクリプトは事故データから統計情報を事前計算し、CSVファイルとして保存します。
生成される統計:
- 市町村別事故件数
- 事故種類別事故件数
- 時間帯別事故件数

事故カウントは(OCCURRENCE_DATE_AND_TIME, LATITUDE, LONGITUDE)を主キーとして
ユニークな事故のみをカウントします。
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_accident_data(data_file: str) -> pd.DataFrame:
    """事故データを読み込み

    Args:
        data_file: データファイルのパス

    Returns:
        pd.DataFrame: 読み込んだ事故データ
    """
    print(f"データ読み込み中: {data_file}")

    if not os.path.exists(data_file):
        raise FileNotFoundError(f"データファイルが見つかりません: {data_file}")

    df = pd.read_csv(data_file, on_bad_lines='skip', encoding='utf-8')

    # 日時カラムを変換
    df['OCCURRENCE_DATE_AND_TIME'] = pd.to_datetime(
        df['OCCURRENCE_DATE_AND_TIME'],
        format='mixed',
        errors='coerce'
    )

    # 必要なカラムの欠損値を削除
    df = df.dropna(subset=['OCCURRENCE_DATE_AND_TIME', 'LATITUDE', 'LONGITUDE'])

    print(f"✓ データ読み込み完了: {len(df):,}件")
    return df


def get_unique_accidents(df: pd.DataFrame) -> pd.DataFrame:
    """主キーで重複を削除してユニークな事故データを取得

    Args:
        df: 事故データ

    Returns:
        pd.DataFrame: ユニークな事故データ
    """
    print("ユニークな事故データを抽出中...")

    unique_df = df.drop_duplicates(
        subset=['OCCURRENCE_DATE_AND_TIME', 'LATITUDE', 'LONGITUDE'],
        keep='first'
    )

    print(f"✓ ユニーク事故件数: {len(unique_df):,}件 (元データ: {len(df):,}件)")
    return unique_df


def add_time_period_column(df: pd.DataFrame) -> pd.DataFrame:
    """時間帯カラムを追加

    Args:
        df: 事故データ

    Returns:
        pd.DataFrame: 時間帯カラムが追加されたデータ
    """
    df = df.copy()
    hour = df['OCCURRENCE_DATE_AND_TIME'].dt.hour

    conditions = [
        (hour >= 0) & (hour < 6),
        (hour >= 6) & (hour < 12),
        (hour >= 12) & (hour < 18),
        (hour >= 18) & (hour < 24)
    ]
    choices = ['深夜 (0-6時)', '朝 (6-12時)', '昼 (12-18時)', '夜 (18-24時)']

    df['time_period'] = np.select(conditions, choices, default='不明')

    return df


def calculate_municipality_stats(df: pd.DataFrame) -> pd.DataFrame:
    """市町村別統計を計算

    Args:
        df: ユニークな事故データ

    Returns:
        pd.DataFrame: 市町村別統計
    """
    print("市町村別統計を計算中...")

    stats = (df.groupby('Area')
             .size()
             .reset_index(name='accident_count'))

    stats['stat_type'] = 'municipality'
    stats = stats.rename(columns={'Area': 'key'})
    stats = stats[['stat_type', 'key', 'accident_count']]

    # 欠損値を除外
    stats = stats[stats['key'].notna()]

    print(f"✓ 市町村数: {len(stats)}件")
    return stats


def calculate_accident_type_stats(df: pd.DataFrame) -> pd.DataFrame:
    """事故種類別統計を計算

    Args:
        df: ユニークな事故データ

    Returns:
        pd.DataFrame: 事故種類別統計
    """
    print("事故種類別統計を計算中...")

    stats = (df.groupby('ACCIDENT_TYPE_(CATEGORY)')
             .size()
             .reset_index(name='accident_count'))

    stats['stat_type'] = 'accident_type'
    stats = stats.rename(columns={'ACCIDENT_TYPE_(CATEGORY)': 'key'})
    stats = stats[['stat_type', 'key', 'accident_count']]

    # 欠損値を除外
    stats = stats[stats['key'].notna()]

    print(f"✓ 事故種類数: {len(stats)}件")
    return stats


def calculate_time_period_stats(df: pd.DataFrame) -> pd.DataFrame:
    """時間帯別統計を計算

    Args:
        df: ユニークな事故データ（time_periodカラム付き）

    Returns:
        pd.DataFrame: 時間帯別統計
    """
    print("時間帯別統計を計算中...")

    stats = (df.groupby('time_period')
             .size()
             .reset_index(name='accident_count'))

    stats['stat_type'] = 'time_period'
    stats = stats.rename(columns={'time_period': 'key'})
    stats = stats[['stat_type', 'key', 'accident_count']]

    # 「不明」を除外
    stats = stats[stats['key'] != '不明']

    print(f"✓ 時間帯数: {len(stats)}件")
    return stats


def save_statistics(stats_df: pd.DataFrame, output_file: str):
    """統計データをCSVファイルに保存

    Args:
        stats_df: 統計データ
        output_file: 出力ファイルパス
    """
    print(f"統計データを保存中: {output_file}")

    # ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    stats_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ 保存完了: {len(stats_df):,}件")


def main():
    """メイン処理"""
    print("=" * 60)
    print("統計用CSV生成スクリプト")
    print("=" * 60)

    # ファイルパス設定
    data_file = project_root / "data" / "accidents" / "data.csv"
    output_file = project_root / "data" / "accidents" / "statistics.csv"

    try:
        # 1. データ読み込み
        df = load_accident_data(str(data_file))

        # 2. ユニークな事故データを抽出
        unique_df = get_unique_accidents(df)

        # 3. 時間帯カラムを追加
        unique_df = add_time_period_column(unique_df)

        # 4. 各種統計を計算
        municipality_stats = calculate_municipality_stats(unique_df)
        accident_type_stats = calculate_accident_type_stats(unique_df)
        time_period_stats = calculate_time_period_stats(unique_df)

        # 5. 全統計を結合
        all_stats = pd.concat([
            municipality_stats,
            accident_type_stats,
            time_period_stats
        ], ignore_index=True)

        # 6. 保存
        save_statistics(all_stats, str(output_file))

        # 7. サマリー表示
        print("\n" + "=" * 60)
        print("統計サマリー")
        print("=" * 60)
        print(f"総統計件数: {len(all_stats):,}件")
        print(f"  - 市町村: {len(municipality_stats):,}件")
        print(f"  - 事故種類: {len(accident_type_stats):,}件")
        print(f"  - 時間帯: {len(time_period_stats):,}件")
        print("\nTOP5 市町村:")
        print(municipality_stats.nlargest(5, 'accident_count')[['key', 'accident_count']].to_string(index=False))
        print("\nTOP5 事故種類:")
        print(accident_type_stats.nlargest(5, 'accident_count')[['key', 'accident_count']].to_string(index=False))
        print("\n時間帯別:")
        print(time_period_stats.sort_values('accident_count', ascending=False)[['key', 'accident_count']].to_string(index=False))
        print("=" * 60)
        print("✓ 処理完了")

    except Exception as e:
        print(f"\n✗ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
