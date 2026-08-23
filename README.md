# patapata_travel_map_maker

47都道府県の観光地・ご当地グルメ・地酒・リスナー口コミを閲覧・共有できるリアルタイムWebマップ。

- 公開URL: https://mitchy-ym.github.io/patapata_travel_map_maker/

## データ管理・更新方法

本システムは **Google スプレッドシート（GAS API）** と直接連携しています。

1. **リスナーからの投稿**:
   - Webマップ上の「➕ 追加」「✏️ 口コミ」ボタンから送信すると、スプレッドシートへ自動追記され、即時マップに反映されます。
2. **管理者による編集・削除**:
   - Google スプレッドシートを直接編集（スポット名の修正や行・セルの削除）するだけで、Webマップを再読み込みすれば即座に最新状態が反映されます（ビルド不要）。

## ローカル実行

```bash
pip install -r requirements.txt
python patamap.py
```

実行後、`index.html` が生成されます。

## ファイル構成

- `patamap.py`: Webマップ生成スクリプト
- `japan.geojson`: 日本地図GeoJSONデータ
- `index.html`: 生成されたWebマップ（公開用）
- `.github/workflows/pages.yml`: GitHub Pages 自動デプロイワークフロー
