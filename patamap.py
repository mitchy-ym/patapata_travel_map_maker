#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🗺️ PataMap（パタマップ）旅行マップ自動生成スクリプト
================================================================================
- 47都道府県の観光地・ご当地グルメ・お酒データをインタラクティブなWeb地図（index.html）として生成します。
- 主な機能:
  1. 📸 観光地 ＆ 🍽️ グルメ の Google Maps（🗺️） / Google 検索（🔍）デュアル連携
  2. 📝 全漢字ルビ（ふりがな）自動表示 ＆ 送り仮名・カタカナ完全分離
  3. 🎨 Google Fonts「Noto Sans JP」採用による美しいタイポグラフィ
  4. 🎯 都道府県プルダウン選択時の自動ズーム ＆ ポップアップ自動表示
  5. 📜 枠内完結カスタムスクロールバー ＆ レスポンシブ最適化
================================================================================
"""

import os
import json
import webbrowser

# ==============================================================================
# 1. 地図・デザイン設定
# ==============================================================================

MAP_BG_COLOR = "#fcf9f2"          # 地図全体の背景色（和紙のような温かみのあるオフホワイト）
INITIAL_CENTER = [137.5, 37.5]   # 初期の日本地図中心座標 [経度, 緯度]
INITIAL_ZOOM = 1.25              # 全体表示時のズームレベル
AUTO_OPEN_BROWSER = True         # 生成後にデフォルトブラウザで自動オープンするか

# 地区ごとのカラーパレット（WCAG視認性対応）
REGION_COLORS = {
    "北海道+東北": {
        "color": "#93C5FD",        # 淡いスカイブルー
        "hover": "#60A5FA",
        "text": "#1D4ED8",
        "badge_bg": "#EFF6FF"
    },
    "関東": {
        "color": "#FDA4AF",        # 淡いローズピンク
        "hover": "#F43F5E",
        "text": "#BE123C",
        "badge_bg": "#FFF1F2"
    },
    "中部": {
        "color": "#A7F3D0",        # 淡いミントグリーン
        "hover": "#34D399",
        "text": "#047857",
        "badge_bg": "#ECFDF5"
    },
    "関西": {
        "color": "#D8B4FE",        # 淡いパープル
        "hover": "#A855F7",
        "text": "#7E22CE",
        "badge_bg": "#FAF5FF"
    },
    "中国+四国": {
        "color": "#FDBA74",        # 淡いコーラルオレンジ
        "hover": "#FB923C",
        "text": "#C2410C",
        "badge_bg": "#FFF7ED"
    },
    "九州+沖縄": {
        "color": "#99F6E4",        # 淡いターコイズグリーン
        "hover": "#2DD4BF",
        "text": "#0F766E",
        "badge_bg": "#F0FDFA"
    },
    "その他": {
        "color": "#E5E7EB",
        "hover": "#CBD5E1",
        "text": "#475569",
        "badge_bg": "#F8FAFC"
    }
}

ALL_PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

PREFECTURE_CENTERS = {
    "北海道": [142.5, 43.5], "青森県": [140.7, 40.8], "岩手県": [141.2, 39.7],
    "宮城県": [140.9, 38.3], "秋田県": [140.1, 39.7], "山形県": [140.4, 38.2],
    "福島県": [140.5, 37.8], "茨城県": [140.4, 36.3], "栃木県": [139.9, 36.6],
    "群馬県": [139.1, 36.4], "埼玉県": [139.6, 35.9], "千葉県": [140.1, 35.6],
    "東京都": [139.7, 35.7], "神奈川県": [139.6, 35.4], "新潟県": [139.0, 37.9],
    "富山県": [137.2, 36.7], "石川県": [136.6, 36.6], "福井県": [136.2, 36.1],
    "山梨県": [138.6, 35.7], "長野県": [138.2, 36.7], "岐阜県": [136.7, 35.4],
    "静岡県": [138.4, 35.0], "愛知県": [136.9, 35.2], "三重県": [136.5, 34.7],
    "滋賀県": [135.9, 35.0], "京都府": [135.8, 35.0], "大阪府": [135.5, 34.7],
    "兵庫県": [135.2, 34.7], "奈良県": [135.8, 34.7], "和歌山県": [135.2, 34.2],
    "鳥取県": [134.2, 35.5], "島根県": [133.1, 35.5], "岡山県": [133.9, 34.7],
    "広島県": [132.5, 34.4], "山口県": [131.5, 34.2], "徳島県": [134.6, 34.1],
    "香川県": [134.0, 34.3], "愛媛県": [132.8, 33.8], "高知県": [133.5, 33.6],
    "福岡県": [130.4, 33.6], "佐賀県": [130.3, 33.2], "長崎県": [129.9, 32.7],
    "熊本県": [130.7, 32.8], "大分県": [131.6, 33.2], "宮崎県": [131.4, 31.9],
    "鹿児島県": [130.6, 31.6], "沖縄県": [127.7, 26.2]
}

REGION_CENTERS = {
    "北海道+東北": {"center": [141.0, 39.5], "zoom": 3.0},
    "関東": {"center": [139.6, 36.3], "zoom": 4.5},
    "中部": {"center": [137.5, 36.0], "zoom": 3.8},
    "関西": {"center": [135.5, 34.8], "zoom": 4.5},
    "中国+四国": {"center": [133.2, 34.3], "zoom": 4.0},
    "九州+沖縄": {"center": [130.2, 32.2], "zoom": 3.5}
}

# ==============================================================================
# 2. 地図HTML生成関数
# ==============================================================================

def create_interactive_map_html(json_data_path="patamap_data.json", geojson_path="japan.geojson", output_html_path="index.html"):
    """
    GeoJSONと都道府県別データを埋め込み、スタンドアロンで動作するWeb地図HTMLを生成します。
    """
    print(f"[ステップ1] 地図データを読み込み中: {json_data_path}")
    if not os.path.exists(json_data_path):
        raise FileNotFoundError(f"エラー: データファイル '{json_data_path}' が見つかりません。")

    with open(json_data_path, "r", encoding="utf-8") as f:
        prefectures_data = json.load(f)

    with open(geojson_path, "r", encoding="utf-8") as f:
        japan_geojson = json.load(f)

    # GeoJSONの各featureにEChartsが参照する 'name' プロパティ（日本語名）を付与
    for feat in japan_geojson.get("features", []):
        props = feat.get("properties", {})
        if "nam_ja" in props:
            props["name"] = props["nam_ja"]

    # 地区バッジHTMLの生成
    legend_badges = []
    for region, cinfo in REGION_COLORS.items():
        if region == "その他":
            continue
        badge = f"""<button class="region-chip" onclick="jumpToRegion('{region}')" 
            style="background-color: {cinfo['badge_bg']}; color: {cinfo['text']}; border: 1.5px solid {cinfo['color']};"
            title="{region} を拡大表示">
            <span class="dot" style="background-color: {cinfo['hover']};"></span>{region}
        </button>"""
        legend_badges.append(badge)
    legend_badges_html = "".join(legend_badges)

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リスナーと作る！全国観光マップ フロリの47都道府県パタパタ旅行企画</title>
    <!-- Google Fonts: Noto Sans JP -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- EChartsライブラリの読み込み -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans JP', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', Meiryo, sans-serif;
            background-color: {MAP_BG_COLOR};
            color: #333;
            overflow: hidden;
        }}
        #map-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
            background-size: 20px 20px;
            position: relative;
        }}
        #main {{
            width: 100%;
            height: 100%;
        }}

        /* 左上フローティングカード */
        .floating-card {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 100;
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(12px);
            padding: 16px 18px 12px 18px;
            border-radius: 20px;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12);
            border: 2px solid #ffccd5;
            width: 350px;
            max-width: calc(100vw - 40px);
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: all 0.3s ease;
        }}
        .card-header {{
            display: block;
            width: 100%;
        }}
        .card-title-main {{
            display: block;
            font-size: 16.5px;
            font-weight: bold;
            color: #e11d48;
            letter-spacing: 0;
            line-height: 1.25;
            white-space: nowrap;
            width: 100%;
            margin: 0;
        }}
        .card-title-sub {{
            display: block;
            font-size: 11.5px;
            color: #64748b;
            font-weight: 500;
            margin-top: 3px;
            white-space: nowrap;
            width: 100%;
        }}
        .region-legend-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 2px 0;
        }}
        .region-chip {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 9px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            outline: none;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .region-chip:hover {{
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }}
        .region-chip .dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }}
        .search-container {{
            display: flex;
            gap: 6px;
            margin-top: 2px;
        }}
        .pref-select {{
            flex: 1;
            padding: 6px 10px;
            border-radius: 10px;
            border: 1.5px solid #cbd5e1;
            font-size: 12px;
            font-weight: bold;
            color: #334155;
            background: #fff;
            outline: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .pref-select:focus {{
            border-color: #f43f5e;
            box-shadow: 0 0 0 3px rgba(244, 63, 94, 0.2);
        }}
        .btn-all-japan {{
            padding: 6px 12px;
            border-radius: 10px;
            border: none;
            background: #f43f5e;
            color: #fff;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(244, 63, 94, 0.3);
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .btn-all-japan:hover {{
            background: #e11d48;
            transform: translateY(-1px);
        }}
        .card-footer-tip {{
            font-size: 10.5px;
            color: #475569;
            background: #f8fafc;
            border-radius: 10px;
            padding: 7px 10px;
            margin-top: 2px;
            display: grid;
            grid-template-columns: 34px auto 10px 1fr;
            row-gap: 4px;
            column-gap: 0;
            align-items: center;
            border: 1px solid #f1f5f9;
        }}
        .tip-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: flex-start;
            font-size: 11px;
            white-space: nowrap;
        }}
        .tip-label {{
            font-weight: 600;
            color: #334155;
            white-space: nowrap;
        }}
        .tip-sep {{
            color: #94a3b8;
            text-align: center;
        }}
        .tip-desc {{
            color: #64748b;
            white-space: nowrap;
        }}

        /* ツールチップ内のカスタムスタイル（全漢字ルビ＆リッチ対話カード） */
        .tooltip-card {{
            padding: 14px 10px 14px 15px;
            width: 350px;
            max-height: 520px;
            overflow-y: auto;
            white-space: normal;
            line-height: 1.6;
            font-size: 13px;
            box-sizing: border-box;
            border-radius: 14px;
            scrollbar-width: thin;
            scrollbar-color: #cbd5e1 transparent;
        }}
        /* スタイリッシュなカスタムスクロールバー（枠線内に完璧に収める） */
        .tooltip-card::-webkit-scrollbar {{
            width: 5px;
        }}
        .tooltip-card::-webkit-scrollbar-track {{
            background: transparent;
            margin: 10px 0;
        }}
        .tooltip-card::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 10px;
        }}
        .tooltip-card::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}

        .tooltip-header {{
            margin: 0 0 10px 0;
            border-bottom: 2px dashed #f43f5e;
            padding-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .tooltip-pref-title {{
            font-size: 18px;
            font-weight: bold;
            color: #e11d48;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .tooltip-region-badge {{
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
        }}
        .tooltip-section {{
            margin-bottom: 10px;
        }}
        .tooltip-title {{
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .tooltip-title-badge {{
            font-size: 10px;
            font-weight: normal;
            color: #94a3b8;
        }}
        .sightseeing-title {{ color: #15803d; }}
        .food-title {{ color: #c2410c; }}
        .drink-title {{ color: #0369a1; }}
        .tooltip-content {{
            font-size: 12.5px;
            background: #f8fafc;
            padding: 6px 8px;
            border-radius: 8px;
            border-left: 3.5px solid #ccc;
            max-height: none;
            overflow: visible;
        }}
        .sightseeing-box {{ background: #f0fdf4; border-left-color: #4ade80; }}
        .food-box {{ background: #fffbeb; border-left-color: #fbbf24; }}
        .drink-box {{ background: #f0f9ff; border-left-color: #38bdf8; }}

        /* モバイル・レスポンシブ最適化 */
        @media (max-width: 640px) {{
            .floating-card {{
                top: 10px;
                left: 10px;
                right: 10px;
                width: auto;
                max-width: none;
                padding: 12px 14px 10px 14px;
                border-radius: 14px;
            }}
            .card-title-main {{
                font-size: 15px;
            }}
            .card-title-sub {{
                font-size: 10.5px;
            }}
            .region-chip {{
                font-size: 10px;
                padding: 3px 6px;
            }}
            .tooltip-card {{
                width: 290px;
                max-height: 400px;
                padding: 10px 12px;
            }}
        }}

        /* 項目リスト＆インタラクティブラベル */
        .tooltip-items-list {{
            margin: 0;
            padding: 0;
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .tooltip-list-item {{
            margin: 0;
            padding: 0;
        }}
        .item-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 3.5px 6px;
            border-radius: 7px;
            transition: all 0.15s ease;
            background: rgba(255, 255, 255, 0.75);
            gap: 6px;
        }}
        .item-row:hover {{
            background: #ffffff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        }}
        .item-text {{
            flex: 1;
            word-break: break-word;
            line-height: 1.65;
            color: #1e293b;
        }}
        ruby {{
            ruby-position: over;
            ruby-align: center;
        }}
        rt {{
            font-size: 0.62em;
            color: #475569;
            font-weight: 500;
            line-height: 1;
            user-select: none;
        }}
        .item-action-btns {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            flex-shrink: 0;
        }}
        .action-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 23px;
            height: 23px;
            border-radius: 6px;
            background: #f1f5f9;
            text-decoration: none;
            font-size: 11px;
            transition: all 0.15s ease;
            border: 1px solid #e2e8f0;
            cursor: pointer;
            user-select: none;
        }}
        .action-btn:hover {{
            transform: scale(1.18);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .map-btn:hover {{
            background: #ecfdf5;
            border-color: #10b981;
        }}
        .search-btn:hover {{
            background: #eff6ff;
            border-color: #3b82f6;
        }}
    </style>
</head>
<body>
    <div id="map-container">
        <!-- 操作＆凡例カード -->
        <div class="floating-card">
            <div class="card-header">
                <div class="card-title-main">🗾 全国観光マップ（47都道府県）</div>
                <div class="card-title-sub">フロリの47都道府県パタパタ旅行企画</div>
            </div>
            <div class="region-legend-container">
                {legend_badges_html}
            </div>
            <div class="search-container">
                <select id="pref-select" class="pref-select" onchange="jumpToPref(this.value)">
                    <option value="">都道府県を選択してジャンプ...</option>
                    {"".join([f'<option value="{p}">{p}</option>' for p in ALL_PREFECTURES])}
                </select>
                <button class="btn-all-japan" onclick="resetToJapan()" title="日本全体表示に戻す">全体</button>
            </div>
            <div class="card-footer-tip">
                <span class="tip-icon">🗺️/🔍</span>
                <span class="tip-label">項目クリック</span>
                <span class="tip-sep">:</span>
                <span class="tip-desc">Googleマップ/検索を開く</span>
                <span class="tip-icon">👆</span>
                <span class="tip-label">地区ボタン</span>
                <span class="tip-sep">:</span>
                <span class="tip-desc">エリア全体を拡大表示</span>
                <span class="tip-icon">📍</span>
                <span class="tip-label">県ホバー</span>
                <span class="tip-sep">:</span>
                <span class="tip-desc">観光地・グルメを表示</span>
            </div>
        </div>

        <!-- ECharts描画コンテナ -->
        <div id="main"></div>
    </div>

    <script>
        const patamapData = {json.dumps(prefectures_data, ensure_ascii=False)};
        const regionColors = {json.dumps(REGION_COLORS, ensure_ascii=False)};
        const prefCenters = {json.dumps(PREFECTURE_CENTERS, ensure_ascii=False)};
        const regionCenters = {json.dumps(REGION_CENTERS, ensure_ascii=False)};
        const geoJsonData = {json.dumps(japan_geojson, ensure_ascii=False)};
        if (geoJsonData && geoJsonData.features) {{
            geoJsonData.features.forEach(function(f) {{
                if (f.properties) {{
                    f.properties.name = f.properties.nam_ja || f.properties.name;
                }}
            }});
        }}

        echarts.registerMap('Japan', geoJsonData);
        const myChart = echarts.init(document.getElementById('main'));

        const mapData = [];
        Object.keys(patamapData).forEach(prefName => {{
            const item = patamapData[prefName];
            const region = item['地区'] || 'その他';
            const colorInfo = regionColors[region] || regionColors['その他'];

            mapData.push({{
                name: prefName,
                value: 1,
                region: region,
                itemStyle: {{
                    areaColor: colorInfo.color,
                    borderColor: '#ffffff',
                    borderWidth: 1.2
                }},
                emphasis: {{
                    itemStyle: {{
                        areaColor: colorInfo.hover,
                        borderColor: colorInfo.text,
                        borderWidth: 2
                    }}
                }}
            }});
        }});

        // テキストをルビ付き・デュアルアクションボタンHTMLに整形する関数（v1.1）
        function formatList(text, category, prefName) {{
            if (!text || text === 'なし') return '<span style="color:#999; font-style:italic;">なし</span>';
            
            const rawItems = text.replace(/\\n/g, '、').replace(/,/g, '、').split('、').map(s => s.trim()).filter(s => s);
            if (rawItems.length === 0) return '<span style="color:#999; font-style:italic;">なし</span>';

            // 特定の店舗・施設・市場が存在するキーワード群
            const locationKeywords = [
                '食堂', 'レストラン', '市場', '牧場', 'カフェ', '酒場', '店', '堂', '軒', '屋', '舎',
                'センター', 'バーガー', 'ファクトリー', 'ワイナリー', '酒蔵', 'ブルワリー', 'ビール',
                'マルトマ', 'サン・ドミニック', 'ラッキーピエロ', 'あまとう', 'ルタオ', 'インデアン',
                '福田パン', 'ベル', 'びっくりドンキー', 'ハラダ', 'おぎのや', 'サイボク', '怪獣酒場',
                '万代そば', '能作', '近江町', '8番らーめん', 'ヨーロッパ軒', '秋吉', '小作', '不動',
                '金精軒', '八幡屋礒五郎', '草笛', '養老軒', 'さわやか', 'マウンテン', '赤福', '一升びん',
                'おやつタウン', '加茂みたらし', '大中', '551', '蓬莱', 'だるま', '美津の', 'りくろーおじさん',
                'かに道楽', 'ふくちぁん', 'ココガーデン', 'すなば珈琲', '桃子', '大手まんぢゅう',
                '日曜市', '田しゅう', '牧のうどん', '資さんうどん', '山田屋', '明月堂', 'ドライブイン鳥',
                'からつバーガー', '井手ちゃんぽん', 'ウエスト', '福砂屋', '蘇州林', '天外天', '文龍', '黒亭',
                'うめちゃんち', '岡本屋', '武蔵屋', '直ちゃん', 'おぐら', 'ひでじビール', 'むじゃき', 'やぶ金'
            ];

            const formattedItems = rawItems.map(item => {{
                let cleanName = item.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '').replace(/[（\\(][^）\\)]*[）\\)]/g, '').trim();
                // 検索ノイズとなる接頭修飾フレーズを自動トリミング
                cleanName = cleanName.replace(/^(世界遺産・国宝|世界遺産|国宝|特別名勝|名勝|国史跡|国指定史跡|国指定天然記念物|天然記念物|日本百名山|日本三名城|新日本三大夜景|現存天守|奇跡の清流|日本最後の清流|特別天然記念物|大本山|世界新三大夜景|名物|元祖)\\s*/g, '').trim();
                const cleanQuery = (prefName + ' ' + cleanName).trim();
                const cleanPlain = item.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '');
                
                const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${{encodeURIComponent(cleanQuery)}}`;
                const searchUrl = `https://www.google.com/search?q=${{encodeURIComponent(cleanQuery)}}`;
                
                const isSightseeing = (category === 'sightseeing');
                const hasSpecificLoc = isSightseeing || locationKeywords.some(kw => cleanPlain.includes(kw));
                
                let btnsHtml = '';
                if (hasSpecificLoc) {{
                    btnsHtml += `<a href="${{mapsUrl}}" target="_blank" rel="noopener noreferrer" class="action-btn map-btn" title="${{cleanPlain}} をGoogleマップで見る">🗺️</a>`;
                }}
                btnsHtml += `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="action-btn search-btn" title="${{cleanPlain}} をGoogleで検索する">🔍</a>`;
                
                return `<li class="tooltip-list-item">
                    <div class="item-row">
                        <span class="item-text">${{item}}</span>
                        <div class="item-action-btns">
                            ${{btnsHtml}}
                        </div>
                    </div>
                </li>`;
            }});
            
            return `<ul class="tooltip-items-list">${{formattedItems.join('')}}</ul>`;
        }}

        const option = {{
            tooltip: {{
                trigger: 'item',
                enterable: true,
                hideDelay: 300,
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                borderColor: '#f43f5e',
                borderWidth: 2,
                padding: 0,
                borderRadius: 14,
                extraCssText: 'box-shadow: 0 10px 28px rgba(0,0,0,0.18); overflow: hidden; border-radius: 14px;',
                textStyle: {{ color: '#333' }},
                position: function (point, params, dom, rect, size) {{
                    const x = point[0];
                    const y = point[1];
                    const boxWidth = size.contentSize[0];
                    const boxHeight = size.contentSize[1];
                    const viewWidth = size.viewSize[0];
                    const viewHeight = size.viewSize[1];

                    let posX = x + 18;
                    if (posX + boxWidth > viewWidth - 15) {{
                        posX = x - boxWidth - 18;
                    }}
                    if (posX < 10) posX = 10;

                    let posY = y - (boxHeight / 2);
                    if (posY < 15) posY = 15;
                    if (posY + boxHeight > viewHeight - 15) {{
                        posY = viewHeight - boxHeight - 15;
                    }}

                    return [posX, posY];
                }},
                formatter: function (params) {{
                    const prefName = params.name;
                    const prefData = patamapData[prefName];
                    if (prefData) {{
                        const region = prefData['地区'] || 'その他';
                        const colorInfo = regionColors[region] || regionColors['その他'];
                        const sightHtml = formatList(prefData['観光地'], 'sightseeing', prefName);
                        const foodHtml = formatList(prefData['食べ物'], 'food', prefName);
                        const drinkHtml = formatList(prefData['お酒'], 'drink', prefName);

                        return `
                            <div class="tooltip-card">
                                <div class="tooltip-header" style="border-bottom-color: ${{colorInfo.hover}};">
                                    <div class="tooltip-pref-title" style="color: ${{colorInfo.text}};">
                                        <span>📍 ${{prefName}}</span>
                                    </div>
                                    <span class="tooltip-region-badge" style="background:${{colorInfo.badge_bg}}; color:${{colorInfo.text}}; border:1px solid ${{colorInfo.color}};">
                                        ${{region}}
                                    </span>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title sightseeing-title">
                                        <span>📸 観光地・名所</span>
                                        <span class="tooltip-title-badge">🗺️ 地図 ＆ 🔍 検索</span>
                                    </div>
                                    <div class="tooltip-content sightseeing-box">${{sightHtml}}</div>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title food-title">
                                        <span>🍽️ ご当地グルメ・食べ物</span>
                                        <span class="tooltip-title-badge">🔍 検索 ＆ 🗺️ 地図</span>
                                    </div>
                                    <div class="tooltip-content food-box">${{foodHtml}}</div>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title drink-title">
                                        <span>🍶 地酒・お酒</span>
                                        <span class="tooltip-title-badge">🔍 検索連動</span>
                                    </div>
                                    <div class="tooltip-content drink-box">${{drinkHtml}}</div>
                                </div>
                            </div>
                        `;
                    }} else {{
                        return `
                            <div style="padding: 15px; text-align: center; width: 200px;">
                                <h3 style="margin:0 0 5px 0;">${{params.name}}</h3>
                                <span style="color: #888;">データがありません</span>
                            </div>
                        `;
                    }}
                }}
            }},
            series: [
                {{
                    name: '日本地図',
                    type: 'map',
                    map: 'Japan',
                    roam: true,
                    center: [{INITIAL_CENTER[0]}, {INITIAL_CENTER[1]}],
                    zoom: {INITIAL_ZOOM},
                    scaleLimit: {{ min: 1.0, max: 20.0 }},
                    itemStyle: {{
                        borderColor: '#ffffff',
                        borderWidth: 1.2
                    }},
                    emphasis: {{
                        label: {{
                            show: true,
                            color: '#111',
                            fontWeight: 'bold',
                            fontSize: 13
                        }}
                    }},
                    label: {{
                        show: true,
                        color: '#333',
                        fontSize: 11,
                        fontWeight: '500',
                        formatter: '{{b}}'
                    }},
                    data: mapData
                }}
            ]
        }};

        myChart.setOption(option);

        // 地図クリック・タップ時の連動処理
        myChart.on('click', function (params) {{
            if (params.componentType === 'series' && params.name) {{
                const sel = document.getElementById('pref-select');
                if (sel) sel.value = params.name;
                myChart.dispatchAction({{
                    type: 'showTip',
                    seriesIndex: 0,
                    name: params.name
                }});
                myChart.dispatchAction({{
                    type: 'highlight',
                    seriesIndex: 0,
                    name: params.name
                }});
            }}
        }});

        function navigateMap(centerCoords, zoomLevel) {{
            myChart.setOption({{
                series: [{{
                    center: centerCoords,
                    zoom: zoomLevel
                }}]
            }});
        }}

        // 都道府県ジャンプ時に自動でポップアップとハイライトを表示
        function jumpToPref(prefName) {{
            if (!prefName || !prefCenters[prefName]) return;
            navigateMap(prefCenters[prefName], 8);
            setTimeout(function () {{
                myChart.dispatchAction({{
                    type: 'showTip',
                    seriesIndex: 0,
                    name: prefName
                }});
                myChart.dispatchAction({{
                    type: 'highlight',
                    seriesIndex: 0,
                    name: prefName
                }});
            }}, 350);
        }}

        function jumpToRegion(regionName) {{
            if (!regionName || !regionCenters[regionName]) return;
            const rInfo = regionCenters[regionName];
            navigateMap(rInfo.center, rInfo.zoom);
        }}

        function resetToJapan() {{
            document.getElementById('pref-select').value = '';
            navigateMap([137.5, 37.5], 1.25);
        }}

        window.addEventListener('resize', function () {{
            myChart.resize();
        }});
    </script>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[ステップ2 完了] 地区別色分け日本地図HTMLを生成しました: {os.path.abspath(output_html_path)}")
    return output_html_path


# ==============================================================================
# 3. メインエントリーポイント
# ==============================================================================

def main():
    print("=" * 60)
    print("🚀 PataMap（パタマップ）旅行マップ自動生成パイプライン 開始")
    print("=" * 60)

    html_file = create_interactive_map_html(
        json_data_path="patamap_data.json",
        geojson_path="japan.geojson",
        output_html_path="index.html"
    )

    if AUTO_OPEN_BROWSER and os.path.exists(html_file):
        print(f"[ステップ3] デフォルトブラウザで地図を開きます: {os.path.abspath(html_file)}")
        webbrowser.open(f"file:///{os.path.abspath(html_file)}")

    print("=" * 60)
    print("🎉 すべての処理が正常に完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()
