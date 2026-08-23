# patapata_travel_map_maker

47都道府県の観光地・ご当地グルメ・地酒・口コミを閲覧できるWebマップ生成ツール。

- 公開URL: https://mitchy-ym.github.io/patapata_travel_map_maker/

## データの更新方法

`patamap_data.json` を編集して `main` ブランチにプッシュ（またはWeb上でコミット）すると、GitHub Actions により自動で再ビルドされ GitHub Pages が更新されます。

```json
"茨城県": {
  "地区": "関東",
  "観光地": "国営ひたち海浜公園、偕楽園（梅林）...",
  "食べ物": "水戸納豆、あんこう鍋...",
  "お酒": "来福、森嶋...",
  "メモ": "国営ひたち海浜公園: ネモフィラは4月下旬が見頃！"
}
```

## ローカル実行

```bash
pip install -r requirements.txt
python patamap.py
```

実行後、`index.html` が生成されます。

## ファイル構成

- `patamap.py`: マップ生成スクリプト
- `patamap_data.json`: 都道府県マスターデータ
- `japan.geojson`: 日本地図GeoJSONデータ
- `index.html`: 生成されたWebマップ（公開用）
- `.github/workflows/pages.yml`: 自動ビルド・デプロイワークフロー
