# 物流事故ヒートマップ可視化システム (AccVis)

地方住民が事故多発箇所を把握し、危険な道路を避けるための判断材料を提供するWebアプリケーションです。

## 機能

### 1. 事故ヒートマップ表示
- Pydeck HeatmapLayerによる事故データの可視化
- インタラクティブな地図操作（ズーム・パン）
- 緯度・経度入力による地図中心の移動

### 2. 高度なフィルタリング
- **時間フィルタ**: 年、月、時間帯（深夜/朝/昼/夜）
- **事故種類フィルタ**: 複数選択可能
- **天候フィルタ**: 複数選択可能
- リアルタイムでヒートマップが更新

### 3. 危険地点の要望投稿
- 位置指定（緯度・経度）
- テキスト要望入力
- 画像添付（任意、最大5MB、JPEG/PNG対応）
- CSV形式での保存

## セットアップ

### 必要要件
- Python 3.8以上
- pip

### インストール手順

1. リポジトリをクローン
```bash
git clone <repository-url>
cd AccVis
```

2. 仮想環境を作成（推奨）
```bash
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

4. アプリケーションを起動
```bash
streamlit run app.py
```

5. ブラウザで http://localhost:8501 にアクセス

## データ形式

### 事故データ (data/accidents/data.csv)
以下のカラムを含むCSV形式:
- `OCCURRENCE_DATE_AND_TIME`: 発生日時
- `WEATHER`: 天候
- `LOCATION`: 場所名
- `LATITUDE`: 緯度
- `LONGITUDE`: 経度
- `ACCIDENT_TYPE_(CATEGORY)`: 事故種類
- `ROAD_TYPE`: 道路種別

### 要望データ (data/requests/requests.csv)
要望投稿時に自動生成されるCSVファイル:
- `request_id`: 要望ID
- `timestamp`: 投稿日時
- `latitude`: 緯度
- `longitude`: 経度
- `description`: 要望内容
- `address`: 住所（任意）
- `image_path`: 画像パス（任意）

## プロジェクト構造

```
AccVis/
├── app.py                    # メインアプリケーション
├── config.py                 # 設定定数
├── requirements.txt          # 依存パッケージ
├── .gitignore               # Git除外設定
│
├── data/                    # データディレクトリ
│   ├── accidents/           # 事故データ
│   │   └── data.csv
│   └── requests/            # 要望投稿データ
│       ├── requests.csv
│       └── images/          # 投稿画像
│
├── src/                     # ソースコード
│   ├── data_loader.py       # データ読み込み
│   ├── filters.py           # フィルタリング
│   ├── map_components.py    # 地図描画
│   ├── request_handler.py   # 要望投稿処理
│   └── utils.py             # ユーティリティ
│
├── .streamlit/              # Streamlit設定
│   └── config.toml
│
└── docs/                    # ドキュメント
    ├── 要件定義.md
    └── data.csv             # 元データ
```

## 使い方

### 地図の操作
1. サイドバーの「地図中心位置」で緯度・経度を入力
2. 「地図中心を移動」ボタンをクリック
3. 地図上でマウスホイールでズーム、ドラッグでパン操作

### フィルタリング
1. サイドバーの「データフィルタ」セクションで条件を選択
2. ヒートマップが自動的に更新される
3. 「フィルタをリセット」で初期状態に戻る

### 要望投稿
1. サイドバーの「危険地点を報告する」ボタンをクリック
2. 位置情報と要望内容を入力
3. 必要に応じて画像をアップロード
4. 「送信する」ボタンで投稿

## 技術スタック

- **フレームワーク**: Streamlit 1.32.0
- **地図可視化**: Pydeck 0.8.0
- **データ処理**: Pandas 2.2.0
- **画像処理**: Pillow 10.2.0

## ライセンス

MIT License

## 作成者

AccVis Development Team
