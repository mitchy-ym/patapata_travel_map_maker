# 「リスナーと作る！全国観光マップ（フロリの47都道府県パタパタ旅行企画）」生成スクリプト

Excelの観光データから、Web公開用の日本地図HTML（`index.html`）を自動生成するツールです。

## 主な機能
- 47都道府県の「観光地」「食べ物」「お酒」データの可視化
- 地区別（北海道+東北、関東、中部、関西、中国+四国、九州+沖縄）の色分け表示
- EChartsによるインタラクティブな地図操作（地区ズーム、都道府県選択、ホバー詳細表示）
- GitHub Pages等でそのまま公開できる単一HTML（スタンドアロン）出力

## 使い方

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. マップHTMLの生成
```bash
python patamap.py
```
実行すると、Excelデータを読み込んで `index.html` が生成され、ブラウザで自動表示されます。

### 3. Webサイトの更新（GitHub Pages）
```bash
git commit -am "Update map data"
git push origin main
```

## ディレクトリ構成
- `patamap.py`: データ抽出・HTML生成スクリプト
- `index.html`: 生成された地図ページ（公開用）
- `patamap_data.json`: 抽出されたJSONデータ
- `japan.geojson`: 日本地図境界データ
- `requirements.txt`: 依存ライブラリ
