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

MAP_BG_COLOR = "#f9f6f0"          # 地図全体の背景色（生成り・鳥の子紙のような温かみのある和紙色）
INITIAL_CENTER = [137.5, 37.5]   # 初期の日本地図中心座標 [経度, 緯度]
INITIAL_ZOOM = 1.25              # 全体表示時のズームレベル
AUTO_OPEN_BROWSER = True         # 生成後にデフォルトブラウザで自動オープンするか

# 地区ごとのカラーパレット（日本の伝統色・和色パレット）
REGION_COLORS = {
    "北海道+東北": {
        "color": "#9bc4e2",        # 藍・水浅葱（みずあさぎ）
        "hover": "#6aa5d8",
        "text": "#1e4e79",
        "badge_bg": "#f0f7fc"
    },
    "関東": {
        "color": "#f7b2bd",        # 撫子（なでしこ）・桜色
        "hover": "#ee7b8e",
        "text": "#9e2a3b",
        "badge_bg": "#fdf2f4"
    },
    "中部": {
        "color": "#aeddb1",        # 若草（わかくさ）・萌黄
        "hover": "#6ec073",
        "text": "#236329",
        "badge_bg": "#f2faf3"
    },
    "関西": {
        "color": "#d2b4de",        # 藤（ふじ）・桔梗
        "hover": "#af7ac5",
        "text": "#5b2c6f",
        "badge_bg": "#f9f3fb"
    },
    "中国+四国": {
        "color": "#f9cb9c",        # 山吹（やまぶき）・杏色
        "hover": "#f39c12",
        "text": "#935116",
        "badge_bg": "#fdf6ee"
    },
    "九州+沖縄": {
        "color": "#a2ded0",        # 浅葱（あさぎ）・青緑
        "hover": "#48c9b0",
        "text": "#117864",
        "badge_bg": "#f0faf8"
    },
    "その他": {
        "color": "#e2ded6",
        "hover": "#cbd5e1",
        "text": "#475569",
        "badge_bg": "#f8fafc"
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

REGION_PREFECTURES = {
    "北海道+東北": ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"],
    "関東": ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県"],
    "中部": ["新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県"],
    "関西": ["滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"],
    "中国+四国": ["鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県"],
    "九州+沖縄": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]
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

    # 都道府県プルダウンの地区別グルーピングHTML生成（optgroup）
    pref_options = ['<option value="">都道府県を選択してジャンプ...</option>']
    for region_name, prefs in REGION_PREFECTURES.items():
        pref_options.append(f'<optgroup label="── {region_name} ──">')
        for p in prefs:
            pref_options.append(f'<option value="{p}">{p}</option>')
        pref_options.append('</optgroup>')
    pref_select_options_html = "\n                    ".join(pref_options)

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リスナーと作る！全国観光マップ フロリの47都道府県パタパタ旅行企画</title>
    <!-- Google Fonts: Zen Maru Gothic Light（和紙調に馴染む細身の上品な丸ゴシック） -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <!-- EChartsライブラリの読み込み -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            font-family: "Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", "Yu Gothic", Meiryo, sans-serif !important;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: "Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", "Yu Gothic", Meiryo, sans-serif !important;
            font-weight: 400 !important;
            background-color: {MAP_BG_COLOR};
            color: #333;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        #map-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {MAP_BG_COLOR};
            background-image: 
                radial-gradient(#dcd5c7 1.2px, transparent 1.2px),
                linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(244, 239, 230, 0.3) 100%);
            background-size: 24px 24px, 100% 100%;
            position: relative;
        }}
        #main {{
            width: 100%;
            height: 100%;
        }}

        /* 左上フローティングカード（和紙すりガラス調） */
        .floating-card {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 100;
            background: rgba(255, 253, 248, 0.95);
            backdrop-filter: blur(12px);
            padding: 16px 18px 12px 18px;
            border-radius: 18px;
            box-shadow: 0 12px 36px rgba(120, 95, 70, 0.12), 0 2px 8px rgba(120, 95, 70, 0.06);
            border: 2px solid #e5d7c7;
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
            font-weight: 800;
            color: #b91c1c; /* 茜・朱赤 */
            letter-spacing: 0;
            line-height: 1.25;
            white-space: nowrap;
            width: 100%;
            margin: 0;
        }}
        .card-title-sub {{
            display: block;
            font-size: 11.5px;
            color: #786d5f;
            font-weight: 600;
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .region-chip:hover {{
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 4px 10px rgba(120,90,60,0.15);
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
            border: 1.5px solid #dcd1c4;
            font-size: 12px;
            font-weight: bold;
            color: #3e3830;
            background: #fffdfa;
            outline: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .pref-select:focus {{
            border-color: #b91c1c;
            box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.15);
        }}
        .pref-select optgroup {{
            font-weight: 700;
            color: #b91c1c;
            background: #fdfcf9;
            font-style: normal;
        }}
        .pref-select option {{
            font-weight: 500;
            color: #2b2b2b;
            background: #ffffff;
            padding: 4px 8px;
        }}
        .btn-all-japan {{
            padding: 6px 12px;
            border-radius: 10px;
            border: none;
            background: #b91c1c;
            color: #fff;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(185, 28, 28, 0.25);
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .btn-all-japan:hover {{
            background: #991b1b;
            transform: translateY(-1px);
        }}
        .card-footer-tip {{
            font-size: 10.5px;
            color: #5c5346;
            background: #fbf8f2;
            border-radius: 10px;
            padding: 7px 10px;
            margin-top: 2px;
            display: grid;
            grid-template-columns: 34px auto 10px 1fr;
            row-gap: 4px;
            column-gap: 0;
            align-items: center;
            border: 1px solid #eee5d8;
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
            color: #3e3830;
            white-space: nowrap;
        }}
        .tip-sep {{
            color: #a89f91;
            text-align: center;
        }}
        .tip-desc {{
            color: #786d5f;
            white-space: nowrap;
        }}

        /* ツールチップ内のカスタムスタイル（和紙掛け紙風リッチ対話カード） */
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
            background: #fdfcf9;
            scrollbar-width: thin;
            scrollbar-color: #d1c7b8 transparent;
        }}
        /* スタイリッシュな和紙風スクロールバー */
        .tooltip-card::-webkit-scrollbar {{
            width: 5px;
        }}
        .tooltip-card::-webkit-scrollbar-track {{
            background: transparent;
            margin: 10px 0;
        }}
        .tooltip-card::-webkit-scrollbar-thumb {{
            background: #d1c7b8;
            border-radius: 10px;
        }}
        .tooltip-card::-webkit-scrollbar-thumb:hover {{
            background: #b5a998;
        }}

        .tooltip-header {{
            margin: 0 0 10px 0;
            border-bottom: 2px dashed #b91c1c;
            padding-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .tooltip-pref-title {{
            font-size: 18px;
            font-weight: bold;
            color: #b91c1c;
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
            color: #8c8273;
        }}
        .sightseeing-title {{ color: #196f3d; }} /* 常磐緑 */
        .food-title {{ color: #b95000; }}        /* 柿色・黄丹 */
        .drink-title {{ color: #1a5276; }}       /* 藍鉄 */
        .tooltip-content {{
            font-size: 12.5px;
            background: #fdfcf9;
            padding: 6px 8px;
            border-radius: 8px;
            border-left: 3.5px solid #ccc;
            max-height: none;
            overflow: visible;
        }}
        .sightseeing-box {{ background: #f2faf4; border-left-color: #52be80; }}
        .food-box {{ background: #fdf8ee; border-left-color: #f39c12; }}
        .drink-box {{ background: #f0f7fb; border-left-color: #5499c7; }}

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
        .memo-btn {{
            background: #fdf4ff;
            border-color: #f0abfc;
            color: #c026d3;
        }}
        .memo-btn:hover {{
            background: #fae8ff;
            border-color: #d946ef;
        }}
        .memo-btn.active {{
            background: #d946ef;
            color: #ffffff;
            border-color: #c026d3;
        }}

        /* 項目別吹き出しスタイル（和紙調ふんわりカード） */
        .item-memo-bubble {{
            margin: 4px 0 6px 0;
            padding: 8px 10px;
            background: #fffdf9;
            border: 1.5px solid #ecd8c5;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(120, 95, 70, 0.08);
            font-size: 11.5px;
            line-height: 1.55;
            color: #4a3f35;
            position: relative;
            animation: memoFadeIn 0.2s ease-out;
        }}
        @keyframes memoFadeIn {{
            from {{ opacity: 0; transform: translateY(-4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .memo-bubble-header {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 700;
            font-size: 11px;
            color: #b91c1c;
            margin-bottom: 3px;
        }}
        .edit-btn {{
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #64748b;
        }}
        .edit-btn:hover {{
            background: #e2e8f0;
            border-color: #94a3b8;
            color: #1e293b;
        }}
        .add-item-btn {{
            display: inline-flex;
            align-items: center;
            gap: 3px;
            padding: 2px 7px;
            border-radius: 12px;
            font-size: 10.5px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
            outline: none;
            user-select: none;
        }}
        .add-sightseeing-btn {{
            color: #196f3d;
            border: 1px solid #52be80;
            background: #f2faf4;
        }}
        .add-sightseeing-btn:hover {{
            background: #e1f7e7;
            transform: scale(1.06);
        }}
        .add-food-btn {{
            color: #b95000;
            border: 1px solid #f39c12;
            background: #fdf8ee;
        }}
        .add-food-btn:hover {{
            background: #faefd9;
            transform: scale(1.06);
        }}
        .add-drink-btn {{
            color: #1a5276;
            border: 1px solid #5499c7;
            background: #f0f7fb;
        }}
        .add-drink-btn:hover {{
            background: #dff0fa;
            transform: scale(1.06);
        }}

        /* 投稿モーダル（ダイアログ）スタイル */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(30, 25, 20, 0.48);
            backdrop-filter: blur(4px);
            z-index: 1000;
            display: none;
            justify-content: center;
            align-items: center;
            padding: 15px;
        }}
        .modal-card {{
            background: #fdfcf9;
            border: 2px solid #e5d7c7;
            border-radius: 18px;
            width: 440px;
            max-width: 100%;
            box-shadow: 0 16px 40px rgba(90, 70, 50, 0.25);
            padding: 22px 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            animation: modalPop 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        @keyframes modalPop {{
            from {{ opacity: 0; transform: scale(0.92); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px dashed #b91c1c;
            padding-bottom: 10px;
        }}
        .modal-title {{
            font-size: 16px;
            font-weight: 800;
            color: #b91c1c;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .modal-close-btn {{
            background: none;
            border: none;
            font-size: 22px;
            cursor: pointer;
            color: #8c8273;
            padding: 0;
            line-height: 1;
            transition: color 0.15s ease;
        }}
        .modal-close-btn:hover {{
            color: #b91c1c;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .form-label {{
            font-size: 12px;
            font-weight: 700;
            color: #3e3830;
        }}
        .form-input, .form-textarea, .form-select {{
            padding: 8px 12px;
            border-radius: 9px;
            border: 1.5px solid #dcd1c4;
            font-size: 13px;
            color: #2b2b2b;
            background: #ffffff;
            outline: none;
            font-family: inherit;
            transition: all 0.2s ease;
        }}
        .form-input:focus, .form-textarea:focus, .form-select:focus {{
            border-color: #b91c1c;
            box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.12);
        }}
        .form-textarea {{
            resize: vertical;
            min-height: 70px;
        }}
        .modal-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 6px;
        }}
        .btn-secondary {{
            padding: 8px 16px;
            border-radius: 9px;
            border: 1.5px solid #dcd1c4;
            background: #fdfcf9;
            color: #5c5346;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .btn-secondary:hover {{
            background: #f1ebd8;
        }}
        .btn-primary {{
            padding: 8px 20px;
            border-radius: 9px;
            border: none;
            background: #b91c1c;
            color: #ffffff;
            font-weight: 700;
            font-size: 12px;
            cursor: pointer;
            box-shadow: 0 3px 10px rgba(185, 28, 28, 0.25);
            transition: all 0.15s ease;
        }}
        .btn-primary:hover {{
            background: #991b1b;
            transform: translateY(-1px);
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
                    {pref_select_options_html}
                </select>
                <button class="btn-all-japan" onclick="resetToJapan()" title="日本全体表示に戻す">全体</button>
            </div>
            <div class="card-footer-tip">
                <span class="tip-icon">🗺️/🔍</span>
                <span class="tip-label">項目クリック</span>
                <span class="tip-sep">:</span>
                <span class="tip-desc">Googleマップ/検索を開く</span>
                <span class="tip-icon">💬</span>
                <span class="tip-label">メモボタン</span>
                <span class="tip-sep">:</span>
                <span class="tip-desc">リスナーの口コミを表示</span>
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

    <!-- 投稿モーダル（ダイアログ） -->
    <div id="addModal" class="modal-overlay" onclick="closeAddModal(event)">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle">新しい項目・口コミを追加</div>
                <button type="button" class="modal-close-btn" onclick="closeAddModal()">&times;</button>
            </div>
            <form id="addForm" onsubmit="submitForm(event)">
                <div class="form-group">
                    <label class="form-label">都道府県</label>
                    <select id="modalPref" class="form-select" required>
                        {pref_select_options_html}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">カテゴリ</label>
                    <select id="modalCategory" class="form-select" required>
                        <option value="sightseeing">観光地・名所</option>
                        <option value="food">ご当地グルメ・食べ物</option>
                        <option value="drink">地酒・お酒</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label" id="modalItemLabel">項目・スポット名</label>
                    <input type="text" id="modalItemTextInput" class="form-input" placeholder="例: 大洗マリンタワー、水戸納豆">
                    <select id="modalItemSelectInput" class="form-select" style="display:none;"></select>
                </div>
                <div class="form-group" id="modalItemRubyGroup">
                    <label class="form-label">ふりがな・読み（任意）</label>
                    <input type="text" id="modalItemRubyInput" class="form-input" placeholder="例: おおあらいまりんたわー、みとなっとう">
                </div>
                <div class="form-group">
                    <label class="form-label">おすすめメモ・口コミ（任意）</label>
                    <textarea id="modalMemo" class="form-textarea" placeholder="例: 展望台から太平洋が一望できて夕日が最高です！"></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">ニックネーム（任意）</label>
                    <input type="text" id="modalAuthor" class="form-input" placeholder="例: フロリファンA">
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="closeAddModal()">キャンセル</button>
                    <button type="submit" class="btn-primary">登録・保存</button>
                </div>
            </form>
        </div>
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

        // 都道府県のメモテキストを辞書化する関数
        function parsePrefMemos(memoText) {{
            const memoMap = {{}};
            if (!memoText || memoText === 'なし') return memoMap;
            const entries = memoText.replace(/\\n/g, '、').split('、');
            entries.forEach(entry => {{
                const parts = entry.split(/[:：]/);
                if (parts.length >= 2) {{
                    const key = parts[0].trim().replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '');
                    const val = parts.slice(1).join(':').trim();
                    if (key && val) {{
                        memoMap[key] = val;
                    }}
                }}
            }});
            return memoMap;
        }}

        // アイテムに対応するメモを検索する関数
        function findItemMemo(cleanPlain, cleanName, memoMap) {{
            if (!memoMap || Object.keys(memoMap).length === 0) return null;
            if (memoMap[cleanPlain]) return memoMap[cleanPlain];
            if (memoMap[cleanName]) return memoMap[cleanName];
            for (let k in memoMap) {{
                if (cleanPlain.includes(k) || k.includes(cleanPlain) || cleanName.includes(k) || k.includes(cleanName)) {{
                    return memoMap[k];
                }}
            }}
            return null;
        }}

        // テキストをルビ付き・デュアルアクションボタン＆メモ吹き出しHTMLに整形する関数（v1.2）
        function formatList(text, category, prefName, memoMap) {{
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

            const formattedItems = rawItems.map((item, idx) => {{
                let cleanName = item.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '').replace(/[（\\(][^）\\)]*[）\\)]/g, '').trim();
                // 検索ノイズとなる接頭修飾フレーズを自動トリミング
                cleanName = cleanName.replace(/^(世界遺産・国宝|世界遺産|国宝|特別名勝|名勝|国史跡|国指定史跡|国指定天然記念物|天然記念物|日本百名山|日本三名城|新日本三大夜景|現存天守|奇跡の清流|日本最後の清流|特別天然記念物|大本山|世界新三大夜景|名物|元祖)\\s*/g, '').trim();
                const cleanQuery = (prefName + ' ' + cleanName).trim();
                const cleanPlain = item.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '');
                
                const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${{encodeURIComponent(cleanQuery)}}`;
                const searchUrl = `https://www.google.com/search?q=${{encodeURIComponent(cleanQuery)}}`;
                
                const isSightseeing = (category === 'sightseeing');
                
                // 観光地であっても特定の物理的固定ピンが存在しない概念・スラング・イベント・工芸品・アクティビティ等の除外判定
                let isNonGeo = false;
                if (isSightseeing) {{
                    const nonGeoExactList = [
                        'ヒョーゴスラビア（兵庫五国）', 'ヒョーゴスラビア', '公営競技の聖地', '三河湾海水浴場',
                        'ロマンシング佐賀（サガシリーズ連携）', 'ゾンビランドサガ聖地巡礼', 'ありあけハーバー',
                        '赤福氷', 'ハトシ（卓袱料理）', '皿鉢料理'
                    ];
                    if (nonGeoExactList.includes(cleanPlain)) {{
                        isNonGeo = true;
                    }} else if (/(伝統的工芸品|和紙|漆器|焼$|焼（|塗|織|細工|切子|うちわ|団扇|人形|赤べこ|さるぼぼ|シーサー|べく杯|瀬戸物|阿波人形浄瑠璃)/.test(cleanPlain) &&
                               !/(会館|村|の里|公園|ミュージアム|資料館|窯)/.test(cleanPlain)) {{
                        isNonGeo = true;
                    }} else if (/(まつり|祭り|祭$|祭（|花火大会|花火$|コンテスト|相馬野馬追|おどり|踊り|フェスティバル|夜神楽|流し雛|ガタリンピック)/.test(cleanPlain)) {{
                        isNonGeo = true;
                    }} else if (/(グランピング|サイクリング|ダイビング|シュノーケリング|ブラックバス釣り|潮干狩り|ホエールウォッチング|ジップライン)/.test(cleanPlain)) {{
                        isNonGeo = true;
                    }} else if (/(ライチョウ|雷鳥|流氷|ひこにゃん|ムツゴロウ|イリオモテヤマネコ|白虎隊|フェニックス並木|ガリンコ号|屋形船)/.test(cleanPlain)) {{
                        isNonGeo = true;
                    }}
                }}

                const hasFoodLocation = (!isSightseeing) && locationKeywords.some(kw => cleanPlain.includes(kw));
                const hasSpecificLoc = (isSightseeing && !isNonGeo) || hasFoodLocation;
                
                let btnsHtml = '';
                if (hasSpecificLoc) {{
                    btnsHtml += `<a href="${{mapsUrl}}" target="_blank" rel="noopener noreferrer" class="action-btn map-btn" title="${{cleanPlain}} をGoogleマップで見る">🗺️</a>`;
                }}
                btnsHtml += `<a href="${{searchUrl}}" target="_blank" rel="noopener noreferrer" class="action-btn search-btn" title="${{cleanPlain}} をGoogleで検索する">🔍</a>`;
                
                // おすすめメモのチェック
                const itemMemo = findItemMemo(cleanPlain, cleanName, memoMap);
                let memoBtnHtml = '';
                let memoBubbleHtml = '';
                if (itemMemo) {{
                    const memoId = 'memo-' + category + '-' + idx + '-' + Math.random().toString(36).substr(2, 5);
                    memoBtnHtml = `<button type="button" class="action-btn memo-btn" onclick="toggleMemo(this, '${{memoId}}')" title="リスナーのおすすめメモを見る">💬</button>`;
                    memoBubbleHtml = `
                        <div id="${{memoId}}" class="item-memo-bubble" style="display:none;">
                            <div class="memo-bubble-header">💡 リスナーおすすめ</div>
                            <div class="memo-bubble-text">${{itemMemo}}</div>
                        </div>
                    `;
                }}

                const editBtnHtml = `<button type="button" class="action-btn edit-btn" onclick="openAddModal('${{prefName}}', '${{category}}', '${{cleanPlain}}')" title="「${{cleanPlain}}」の口コミ・おすすめを書く">✏️</button>`;

                return `<li class="tooltip-list-item">
                    <div class="item-row">
                        <span class="item-text">${{item}}</span>
                        <div class="item-action-btns">
                            ${{btnsHtml}}${{memoBtnHtml}}${{editBtnHtml}}
                        </div>
                    </div>
                    ${{memoBubbleHtml}}
                </li>`;
            }});
            
            return `<ul class="tooltip-items-list">${{formattedItems.join('')}}</ul>`;
        }}

        // メモ吹き出しの開閉トグル関数
        window.toggleMemo = function(btn, memoId) {{
            const bubble = document.getElementById(memoId);
            if (!bubble) return;
            if (bubble.style.display === 'none' || bubble.style.display === '') {{
                bubble.style.display = 'block';
                btn.classList.add('active');
            }} else {{
                bubble.style.display = 'none';
                btn.classList.remove('active');
            }}
        }};

        // 投稿モーダルの開閉・送信制御
        window.openAddModal = function(pref, cat, itemName) {{
            // 開いていたポップアップ（ツールチップ）を閉じる
            if (typeof myChart !== 'undefined' && myChart) {{
                myChart.dispatchAction({{ type: 'hideTip' }});
            }}

            const modal = document.getElementById('addModal');
            if (!modal) return;

            const prefEl = document.getElementById('modalPref');
            const catEl = document.getElementById('modalCategory');
            const titleEl = document.getElementById('modalTitle');
            const textInput = document.getElementById('modalItemTextInput');
            const selectInput = document.getElementById('modalItemSelectInput');
            const labelEl = document.getElementById('modalItemLabel');

            prefEl.value = pref || '';
            catEl.value = cat || 'sightseeing';
            document.getElementById('modalMemo').value = '';
            document.getElementById('modalAuthor').value = '';

            const rubyGroup = document.getElementById('modalItemRubyGroup');
            const rubyInput = document.getElementById('modalItemRubyInput');
            if (rubyInput) rubyInput.value = '';

            if (itemName) {{
                // 口コミ追加モード：スポット名は選択式（自由編集不可）
                titleEl.innerHTML = `「${{itemName}}」に口コミを追加`;
                labelEl.innerHTML = `対象スポット（選択式）`;
                textInput.style.display = 'none';
                textInput.removeAttribute('required');
                selectInput.style.display = 'block';
                selectInput.setAttribute('required', 'required');
                if (rubyGroup) rubyGroup.style.display = 'none';

                // 該当都道府県・カテゴリの既存スポット一覧をオプションとして生成
                selectInput.innerHTML = '';
                const prefObj = patamapData[pref];
                const catKey = cat === 'food' ? '食べ物' : cat === 'drink' ? 'お酒' : '観光地';
                if (prefObj && prefObj[catKey] && prefObj[catKey] !== 'なし') {{
                    const rawItems = prefObj[catKey].replace(/\\n/g, '、').replace(/,/g, '、').split('、').map(s => s.trim()).filter(s => s);
                    rawItems.forEach(it => {{
                        const cleanP = it.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '').trim();
                        const opt = document.createElement('option');
                        opt.value = cleanP;
                        opt.textContent = cleanP;
                        if (cleanP === itemName || it.includes(itemName) || itemName.includes(cleanP)) {{
                            opt.selected = true;
                        }}
                        selectInput.appendChild(opt);
                    }});
                }}
                prefEl.disabled = true;
                catEl.disabled = true;
            }} else {{
                // 新規項目追加モード：スポット名は自由入力＋ふりがな入力
                const catLabel = cat === 'food' ? 'グルメ' : cat === 'drink' ? '地酒' : '観光地';
                titleEl.innerHTML = `【${{pref}}】に新しい${{catLabel}}を追加`;
                labelEl.innerHTML = `項目・スポット名`;
                selectInput.style.display = 'none';
                selectInput.removeAttribute('required');
                textInput.style.display = 'block';
                textInput.setAttribute('required', 'required');
                textInput.value = '';
                if (rubyGroup) rubyGroup.style.display = 'flex';
                prefEl.disabled = false;
                catEl.disabled = false;
            }}

            modal.style.display = 'flex';
        }};

        window.closeAddModal = function(e) {{
            if (!e || e.target === document.getElementById('addModal') || e.target.classList.contains('modal-close-btn') || e.target.classList.contains('btn-secondary')) {{
                const modal = document.getElementById('addModal');
                if (modal) modal.style.display = 'none';
                document.getElementById('modalPref').disabled = false;
                document.getElementById('modalCategory').disabled = false;
            }}
        }};

        window.submitForm = function(e) {{
            e.preventDefault();
            const prefEl = document.getElementById('modalPref');
            const catEl = document.getElementById('modalCategory');
            const pref = prefEl.value;
            const cat = catEl.value;
            const textInput = document.getElementById('modalItemTextInput');
            const selectInput = document.getElementById('modalItemSelectInput');
            const rubyInput = document.getElementById('modalItemRubyInput');
            const isCommentMode = (selectInput.style.display !== 'none');
            const itemName = isCommentMode ? selectInput.value.trim() : textInput.value.trim();
            const itemRuby = (!isCommentMode && rubyInput) ? rubyInput.value.trim() : '';
            const memo = document.getElementById('modalMemo').value.trim();
            const author = document.getElementById('modalAuthor').value.trim();

            if (!pref || !itemName) return;

            // ふりがなが入力されている場合はルビタグ付きで整形
            let finalItemName = itemName;
            if (!isCommentMode && itemRuby) {{
                finalItemName = `<ruby>${{itemName}}<rt>${{itemRuby}}</rt></ruby>`;
            }}

            // 送信用に disabled を解除
            prefEl.disabled = false;
            catEl.disabled = false;

            // ローカルデータに即時反映
            if (patamapData[pref]) {{
                const catKey = cat === 'food' ? '食べ物' : cat === 'drink' ? 'お酒' : '観光地';
                if (!isCommentMode) {{
                    if (!patamapData[pref][catKey] || patamapData[pref][catKey] === 'なし') {{
                        patamapData[pref][catKey] = finalItemName;
                    }} else if (!patamapData[pref][catKey].includes(itemName)) {{
                        patamapData[pref][catKey] += '、' + finalItemName;
                    }}
                }}
                if (memo) {{
                    const memoStr = author ? `${{itemName}}: ${{memo}}（by ${{author}}）` : `${{itemName}}: ${{memo}}`;
                    if (!patamapData[pref]['メモ'] || patamapData[pref]['メモ'] === 'なし') {{
                        patamapData[pref]['メモ'] = memoStr;
                    }} else {{
                        patamapData[pref]['メモ'] += '、' + memoStr;
                    }}
                }}
            }}

            const modal = document.getElementById('addModal');
            if (modal) modal.style.display = 'none';

            alert(`🎉 「${{itemName}}」の情報を登録・保存しました！\\n（※GitHub上のデータ更新時は patamap_data.json に保存されます）`);
            
            // ポップアップを更新
            jumpToPref(pref);
        }};

        const option = {{
            tooltip: {{
                trigger: 'item',
                enterable: true,
                hideDelay: 400,
                backgroundColor: 'rgba(255, 253, 248, 0.98)',
                borderColor: '#b91c1c',
                borderWidth: 2,
                padding: 0,
                borderRadius: 14,
                extraCssText: 'box-shadow: 0 10px 28px rgba(120,95,70,0.18); overflow: hidden; border-radius: 14px;',
                textStyle: {{
                    fontFamily: '"Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", "Yu Gothic", Meiryo, sans-serif',
                    color: '#2b2b2b'
                }},
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
                        const memoMap = parsePrefMemos(prefData['メモ'] || '');
                        const sightHtml = formatList(prefData['観光地'], 'sightseeing', prefName, memoMap);
                        const foodHtml = formatList(prefData['食べ物'], 'food', prefName, memoMap);
                        const drinkHtml = formatList(prefData['お酒'], 'drink', prefName, memoMap);

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
                                        <button type="button" class="add-item-btn add-sightseeing-btn" onclick="openAddModal('${{prefName}}', 'sightseeing', '')" title="【${{prefName}}】に新しい観光地を追加">➕ 観光地追加</button>
                                    </div>
                                    <div class="tooltip-content sightseeing-box">${{sightHtml}}</div>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title food-title">
                                        <span>🍽️ ご当地グルメ・食べ物</span>
                                        <button type="button" class="add-item-btn add-food-btn" onclick="openAddModal('${{prefName}}', 'food', '')" title="【${{prefName}}】に新しいグルメを追加">➕ グルメ追加</button>
                                    </div>
                                    <div class="tooltip-content food-box">${{foodHtml}}</div>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title drink-title">
                                        <span>🍶 地酒・お酒</span>
                                        <button type="button" class="add-item-btn add-drink-btn" onclick="openAddModal('${{prefName}}', 'drink', '')" title="【${{prefName}}】に新しい地酒を追加">➕ 地酒追加</button>
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
                            fontWeight: '700',
                            fontSize: 13,
                            fontFamily: '"Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", sans-serif'
                        }}
                    }},
                    label: {{
                        show: true,
                        color: '#333',
                        fontSize: 11.5,
                        fontWeight: '500',
                        fontFamily: '"Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", sans-serif',
                        formatter: '{{b}}'
                    }},
                    data: mapData
                }}
            ]
        }};

        myChart.setOption(option);

        // Webフォント（Zen Maru Gothic）のロード完了時に地図上の文字を確実に丸ゴシック（Regular/Medium）で再描画
        if (document.fonts) {{
            document.fonts.ready.then(function () {{
                myChart.setOption({{
                    series: [{{
                        label: {{
                            fontFamily: '"Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", sans-serif',
                            fontWeight: '500'
                        }},
                        emphasis: {{
                            label: {{
                                fontFamily: '"Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", sans-serif',
                                fontWeight: '700'
                            }}
                        }}
                    }}]
                }});
                myChart.resize();
            }});
        }}

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
# 3. 管理者専用データ編集画面（admin.html）の自動生成
# ==============================================================================

def create_admin_editor_html(
    json_data_path="patamap_data.json",
    output_html_path="admin.html"
):
    """
    管理者専用のデータ編集Web画面（admin.html）を生成する。
    """
    with open(json_data_path, "r", encoding="utf-8") as f:
        prefectures_data = json.load(f)

    admin_html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PataMap 管理者データ編集ツール（非公開）</title>
    <!-- Google Fonts: Zen Maru Gothic -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            font-family: "Zen Maru Gothic", "Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic UI", "Yu Gothic", Meiryo, sans-serif !important;
        }}
        body {{
            margin: 0;
            padding: 0;
            background-color: #fdfbf7;
            background-image: 
                radial-gradient(#dcd5c7 1.2px, transparent 1.2px),
                linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(244, 239, 230, 0.3) 100%);
            background-size: 24px 24px, 100% 100%;
            color: #2b2b2b;
            font-weight: 400;
            min-height: 100vh;
            padding-bottom: 80px;
        }}
        .header-bar {{
            background: rgba(255, 253, 248, 0.96);
            backdrop-filter: blur(10px);
            border-bottom: 2px solid #b91c1c;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 16px rgba(120, 95, 70, 0.1);
        }}
        .header-title-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-title {{
            font-size: 17px;
            font-weight: 800;
            color: #b91c1c;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .header-badge {{
            font-size: 11px;
            font-weight: 700;
            background: #fee2e2;
            color: #b91c1c;
            border: 1px solid #f87171;
            padding: 2px 8px;
            border-radius: 999px;
        }}
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 7px 14px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            border: 1.5px solid transparent;
            transition: all 0.15s ease;
            text-decoration: none;
            outline: none;
        }}
        .btn-primary {{
            background: #b91c1c;
            color: #ffffff;
            border-color: #991b1b;
        }}
        .btn-primary:hover {{
            background: #991b1b;
            box-shadow: 0 2px 8px rgba(185, 28, 28, 0.3);
        }}
        .btn-github {{
            background: #181717;
            color: #ffffff;
            border-color: #000000;
        }}
        .btn-github:hover {{
            background: #333333;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }}
        .btn-secondary {{
            background: #ffffff;
            color: #3e3830;
            border-color: #dcd1c4;
        }}
        .btn-secondary:hover {{
            background: #f7f3ec;
            border-color: #bfa895;
        }}
        .btn-danger {{
            background: #fee2e2;
            color: #b91c1c;
            border-color: #fca5a5;
        }}
        .btn-danger:hover {{
            background: #fecaca;
        }}
        .container {{
            max-width: 1100px;
            margin: 24px auto;
            padding: 0 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .pref-selector-card {{
            background: rgba(255, 253, 248, 0.95);
            border: 1.5px solid #e2d9cc;
            border-radius: 14px;
            padding: 16px 20px;
            box-shadow: 0 4px 14px rgba(120, 95, 70, 0.06);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .pref-select-label {{
            font-size: 14px;
            font-weight: 700;
            color: #3e3830;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .pref-select {{
            padding: 8px 16px;
            border-radius: 9px;
            border: 1.5px solid #dcd1c4;
            font-size: 15px;
            font-weight: 700;
            color: #b91c1c;
            background: #ffffff;
            outline: none;
            cursor: pointer;
            min-width: 220px;
        }}
        .pref-select:focus {{
            border-color: #b91c1c;
            box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.12);
        }}
        .region-badge-current {{
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid #dcd1c4;
            background: #f4efe6;
            color: #5c4f3d;
        }}
        .category-section {{
            background: rgba(255, 253, 248, 0.95);
            border: 1.5px solid #e2d9cc;
            border-radius: 14px;
            padding: 18px 22px;
            box-shadow: 0 4px 14px rgba(120, 95, 70, 0.06);
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1.5px solid #e2d9cc;
            padding-bottom: 10px;
        }}
        .category-title {{
            font-size: 15px;
            font-weight: 800;
            color: #2b2b2b;
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 0;
        }}
        .category-count {{
            font-size: 12px;
            font-weight: 700;
            color: #78716c;
            background: #f5f5f4;
            padding: 2px 8px;
            border-radius: 999px;
            margin-left: 6px;
        }}
        .items-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }}
        .item-card {{
            background: #ffffff;
            border: 1.5px solid #ebe5dc;
            border-radius: 10px;
            padding: 10px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            transition: all 0.15s ease;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
        }}
        .item-card:hover {{
            border-color: #b91c1c;
            box-shadow: 0 3px 8px rgba(185, 28, 28, 0.08);
        }}
        .item-card-text {{
            flex: 1;
            font-size: 13.5px;
            line-height: 1.6;
            word-break: break-word;
        }}
        .item-card-actions {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            flex-shrink: 0;
        }}
        .mini-btn {{
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: 1px solid #dcd1c4;
            background: #fdfbf7;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            transition: all 0.15s ease;
            color: #5c4f3d;
        }}
        .mini-btn:hover {{
            background: #b91c1c;
            color: #ffffff;
            border-color: #b91c1c;
        }}
        .mini-btn.delete-btn:hover {{
            background: #dc2626;
            border-color: #dc2626;
            color: #ffffff;
        }}
        .memo-card {{
            background: #ffffff;
            border: 1.5px solid #ebe5dc;
            border-radius: 10px;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
        }}
        .memo-spot {{
            font-weight: 700;
            font-size: 13px;
            color: #b91c1c;
            margin-bottom: 4px;
        }}
        .memo-body {{
            font-size: 13px;
            line-height: 1.5;
            color: #3e3830;
        }}
        .memo-author {{
            font-size: 11px;
            color: #78716c;
            margin-top: 4px;
            font-style: italic;
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
        }}

        /* モーダル */
        .modal-backdrop {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(43, 43, 43, 0.55);
            backdrop-filter: blur(4px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        .modal-box {{
            background: #fffdf9;
            border: 2px solid #b91c1c;
            border-radius: 16px;
            width: 90%;
            max-width: 480px;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22);
            padding: 22px 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            animation: modalPop 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        @keyframes modalPop {{
            from {{ opacity: 0; transform: scale(0.94); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px dashed #b91c1c;
            padding-bottom: 10px;
        }}
        .modal-title {{
            font-size: 16px;
            font-weight: 800;
            color: #b91c1c;
            margin: 0;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .form-label {{
            font-size: 12.5px;
            font-weight: 700;
            color: #3e3830;
        }}
        .form-input, .form-textarea, .form-select {{
            padding: 8px 12px;
            border-radius: 8px;
            border: 1.5px solid #dcd1c4;
            font-size: 13.5px;
            color: #2b2b2b;
            background: #ffffff;
            outline: none;
            font-family: inherit;
        }}
        .form-input:focus, .form-textarea:focus, .form-select:focus {{
            border-color: #b91c1c;
            box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.12);
        }}
        .form-textarea {{
            resize: vertical;
            min-height: 80px;
        }}
        .modal-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 6px;
        }}
        .toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #1e293b;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 700;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
            display: none;
            align-items: center;
            gap: 8px;
            z-index: 2000;
            animation: toastIn 0.2s ease;
        }}
        @keyframes toastIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>

    <!-- ヘッダーバー -->
    <header class="header-bar">
        <div class="header-title-group">
            <h1 class="header-title">🔒 PataMap 管理者データ編集ツール</h1>
            <span class="header-badge">秘匿管理画面</span>
        </div>
        <div class="header-actions">
            <button type="button" class="btn btn-secondary" onclick="exportJsonFile()" title="編集後の最新 patamap_data.json をダウンロード">📥 JSON保存</button>
            <button type="button" class="btn btn-secondary" onclick="copyJsonToClipboard()" title="JSONテキストをクリップボードにコピー">📋 JSONコピー</button>
            <button type="button" class="btn btn-github" onclick="openGithubModal()" title="GitHub API経由で直接リポジトリに保存">🚀 GitHub直接保存</button>
            <button type="button" class="btn btn-danger" onclick="resetAllChanges()" title="未保存の編集を破棄して初期状態に戻す">🔄 リセット</button>
            <a href="index.html" target="_blank" class="btn btn-primary" title="公開マップを別タブで開く">🌐 公開マップ</a>
        </div>
    </header>

    <div class="container">
        <!-- 都道府県セレクタ -->
        <div class="pref-selector-card">
            <div class="pref-select-label">
                <span>📍 編集する都道府県:</span>
                <select id="currentPrefSelect" class="pref-select" onchange="switchPref(this.value)"></select>
            </div>
            <div id="currentRegionBadge" class="region-badge-current">地区: -</div>
        </div>

        <!-- 📸 観光地・名所 -->
        <div class="category-section">
            <div class="category-header">
                <div class="category-title">
                    <span>📸 観光地・名所</span>
                    <span id="sightseeingCount" class="category-count">0件</span>
                </div>
                <button type="button" class="btn btn-secondary" onclick="openItemModal('sightseeing', -1)">➕ 観光地追加</button>
            </div>
            <div id="sightseeingGrid" class="items-grid"></div>
        </div>

        <!-- 🍽️ ご当地グルメ・食べ物 -->
        <div class="category-section">
            <div class="category-header">
                <div class="category-title">
                    <span>🍽️ ご当地グルメ・食べ物</span>
                    <span id="foodCount" class="category-count">0件</span>
                </div>
                <button type="button" class="btn btn-secondary" onclick="openItemModal('food', -1)">➕ グルメ追加</button>
            </div>
            <div id="foodGrid" class="items-grid"></div>
        </div>

        <!-- 🍶 地酒・お酒 -->
        <div class="category-section">
            <div class="category-header">
                <div class="category-title">
                    <span>🍶 地酒・お酒</span>
                    <span id="drinkCount" class="category-count">0件</span>
                </div>
                <button type="button" class="btn btn-secondary" onclick="openItemModal('drink', -1)">➕ 地酒追加</button>
            </div>
            <div id="drinkGrid" class="items-grid"></div>
        </div>

        <!-- 💬 リスナーおすすめメモ・口コミ -->
        <div class="category-section">
            <div class="category-header">
                <div class="category-title">
                    <span>💬 リスナーおすすめメモ・口コミ</span>
                    <span id="memoCount" class="category-count">0件</span>
                </div>
                <button type="button" class="btn btn-secondary" onclick="openMemoModal(-1)">➕ 口コミ追加</button>
            </div>
            <div id="memoGrid" style="display:flex; flex-direction:column; gap:10px;"></div>
        </div>
    </div>

    <!-- アイテム追加/編集モーダル -->
    <div id="itemModal" class="modal-backdrop" onclick="closeModalOnBackdrop(event, 'itemModal')">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="itemModalTitle" class="modal-title">項目を編集</h3>
                <button type="button" class="btn-secondary" style="border:none; background:none; font-size:20px; cursor:pointer;" onclick="closeModal('itemModal')">✕</button>
            </div>
            <form onsubmit="saveItem(event)">
                <input type="hidden" id="modalCategory">
                <input type="hidden" id="modalIndex">
                <div class="form-group">
                    <label class="form-label">項目・スポット名（漢字・カナ・英数）</label>
                    <input type="text" id="modalItemName" class="form-input" placeholder="例: 巌美渓、水戸納豆" required>
                </div>
                <div class="form-group">
                    <label class="form-label">ふりがな・読み（任意）</label>
                    <input type="text" id="modalItemRuby" class="form-input" placeholder="例: げんびけい、みとなっとう">
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('itemModal')">キャンセル</button>
                    <button type="submit" class="btn btn-primary">保存</button>
                </div>
            </form>
        </div>
    </div>

    <!-- メモ追加/編集モーダル -->
    <div id="memoModal" class="modal-backdrop" onclick="closeModalOnBackdrop(event, 'memoModal')">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="memoModalTitle" class="modal-title">口コミ・おすすめメモを編集</h3>
                <button type="button" class="btn-secondary" style="border:none; background:none; font-size:20px; cursor:pointer;" onclick="closeModal('memoModal')">✕</button>
            </div>
            <form onsubmit="saveMemo(event)">
                <input type="hidden" id="modalMemoIndex">
                <div class="form-group">
                    <label class="form-label">対象スポット・名物名</label>
                    <input type="text" id="modalMemoSpot" class="form-input" placeholder="例: 国営ひたち海浜公園" required>
                </div>
                <div class="form-group">
                    <label class="form-label">おすすめ内容・口コミ本文</label>
                    <textarea id="modalMemoBody" class="form-textarea" placeholder="例: ネモフィラの見頃は4月下旬！早朝開園が狙い目です" required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">投稿者ニックネーム（任意）</label>
                    <input type="text" id="modalMemoAuthor" class="form-input" placeholder="例: フロリファンA">
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('memoModal')">キャンセル</button>
                    <button type="submit" class="btn btn-primary">保存</button>
                </div>
            </form>
        </div>
    </div>

    <!-- GitHub直接保存モーダル -->
    <div id="githubModal" class="modal-backdrop" onclick="closeModalOnBackdrop(event, 'githubModal')">
        <div class="modal-box">
            <div class="modal-header">
                <h3 class="modal-title">🚀 GitHubへ直接コミット保存</h3>
                <button type="button" class="btn-secondary" style="border:none; background:none; font-size:20px; cursor:pointer;" onclick="closeModal('githubModal')">✕</button>
            </div>
            <form onsubmit="commitToGitHub(event)">
                <div class="form-group">
                    <label class="form-label">GitHub Personal Access Token (PAT)</label>
                    <input type="password" id="ghToken" class="form-input" placeholder="ghp_xxxxxxxxxxxx" required>
                    <span style="font-size:11px; color:#78716c;">※ブラウザのlocalStorageに安全に保持されます</span>
                </div>
                <div class="form-group">
                    <label class="form-label">リポジトリ</label>
                    <input type="text" id="ghRepo" class="form-input" value="mitchy-ym/patapata_travel_map_maker" required>
                </div>
                <div class="form-group">
                    <label class="form-label">ブランチ</label>
                    <input type="text" id="ghBranch" class="form-input" value="main" required>
                </div>
                <div class="form-group">
                    <label class="form-label">コミットメッセージ</label>
                    <input type="text" id="ghMessage" class="form-input" value="Update patamap_data.json via admin editor" required>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('githubModal')">キャンセル</button>
                    <button type="submit" id="ghSubmitBtn" class="btn btn-github">GitHubに保存＆自動デプロイ</button>
                </div>
            </form>
        </div>
    </div>

    <!-- トースト通知 -->
    <div id="toast" class="toast"></div>

    <script>
        // マスターデータ
        const initialData = {json.dumps(prefectures_data, ensure_ascii=False)};
        let currentData = JSON.parse(JSON.stringify(initialData));
        let selectedPref = '北海道';

        // 初期化
        document.addEventListener('DOMContentLoaded', () => {{
            initPrefSelector();
            renderCurrentPref();
            loadSavedGitHubSettings();
        }});

        function showToast(msg) {{
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.style.display = 'flex';
            setTimeout(() => {{ t.style.display = 'none'; }}, 3000);
        }}

        // 都道府県セレクタ初期化
        function initPrefSelector() {{
            const sel = document.getElementById('currentPrefSelect');
            sel.innerHTML = '';
            
            const regions = {{}};
            Object.keys(currentData).forEach(pref => {{
                const reg = currentData[pref]['地区'] || 'その他';
                if (!regions[reg]) regions[reg] = [];
                regions[reg].push(pref);
            }});

            for (let reg in regions) {{
                const group = document.createElement('optgroup');
                group.label = `【${{reg}}】`;
                regions[reg].forEach(pref => {{
                    const opt = document.createElement('option');
                    opt.value = pref;
                    opt.textContent = pref;
                    group.appendChild(opt);
                }});
                sel.appendChild(group);
            }}

            sel.value = selectedPref;
        }}

        function switchPref(pref) {{
            selectedPref = pref;
            renderCurrentPref();
        }}

        // ルビ付きHTMLから「プレーン名」と「ふりがな」を抽出するユーティリティ
        function parseRubyItem(rawItem) {{
            if (!rawItem) return {{ name: '', ruby: '' }};
            const match = rawItem.match(/<ruby>([^<]+)<rt>([^<]+)<\\/rt><\\/ruby>/);
            if (match) {{
                return {{ name: match[1], ruby: match[2] }};
            }}
            const plain = rawItem.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '').trim();
            return {{ name: plain, ruby: '' }};
        }}

        function buildRubyItem(name, ruby) {{
            if (!ruby) return name.trim();
            return `<ruby>${{name.trim()}}<rt>${{ruby.trim()}}</rt></ruby>`;
        }}

        // 現在選択中の都道府県を描画
        function renderCurrentPref() {{
            const prefData = currentData[selectedPref];
            if (!prefData) return;

            document.getElementById('currentRegionBadge').textContent = `地区: ${{prefData['地区'] || 'その他'}}`;

            renderCategoryGrid('sightseeing', '観光地', 'sightseeingGrid', 'sightseeingCount');
            renderCategoryGrid('food', '食べ物', 'foodGrid', 'foodCount');
            renderCategoryGrid('drink', 'お酒', 'drinkGrid', 'drinkCount');
            renderMemoGrid();
        }}

        function getCategoryItems(catKey) {{
            const val = currentData[selectedPref][catKey] || '';
            if (!val || val === 'なし') return [];
            return val.replace(/\\n/g, '、').replace(/,/g, '、').split('、').map(s => s.trim()).filter(s => s);
        }}

        function setCategoryItems(catKey, items) {{
            if (items.length === 0) {{
                currentData[selectedPref][catKey] = 'なし';
            }} else {{
                currentData[selectedPref][catKey] = items.join('、');
            }}
            renderCurrentPref();
        }}

        function renderCategoryGrid(cat, catKey, gridId, countId) {{
            const items = getCategoryItems(catKey);
            const grid = document.getElementById(gridId);
            document.getElementById(countId).textContent = `${{items.length}}件`;
            grid.innerHTML = '';

            if (items.length === 0) {{
                grid.innerHTML = `<span style="color:#999; font-size:13px; font-style:italic;">データがありません</span>`;
                return;
            }}

            items.forEach((item, idx) => {{
                const parsed = parseRubyItem(item);
                const card = document.createElement('div');
                card.className = 'item-card';
                card.innerHTML = `
                    <div class="item-card-text">${{item}}</div>
                    <div class="item-card-actions">
                        <button type="button" class="mini-btn edit-btn" onclick="openItemModal('${{cat}}', ${{idx}})" title="編集">✏️</button>
                        <button type="button" class="mini-btn delete-btn" onclick="deleteItem('${{catKey}}', ${{idx}})" title="削除">🗑️</button>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        function renderMemoGrid() {{
            const rawMemo = currentData[selectedPref]['メモ'] || '';
            const grid = document.getElementById('memoGrid');
            const countEl = document.getElementById('memoCount');

            if (!rawMemo || rawMemo === 'なし') {{
                countEl.textContent = '0件';
                grid.innerHTML = `<span style="color:#999; font-size:13px; font-style:italic;">登録された口コミはありません</span>`;
                return;
            }}

            const entries = rawMemo.replace(/\\n/g, '、').split('、').map(s => s.trim()).filter(s => s);
            countEl.textContent = `${{entries.length}}件`;
            grid.innerHTML = '';

            entries.forEach((entry, idx) => {{
                let spot = '';
                let body = entry;
                let author = '';

                const p1 = entry.split(/[:：]/);
                if (p1.length >= 2) {{
                    spot = p1[0].trim();
                    body = p1.slice(1).join(':').trim();
                }}
                const p2 = body.match(/^(.*?)[（\\(]by\\s*([^）\\)]+)[）\\)]$/);
                if (p2) {{
                    body = p2[1].trim();
                    author = p2[2].trim();
                }}

                const card = document.createElement('div');
                card.className = 'memo-card';
                card.innerHTML = `
                    <div style="flex:1;">
                        ${{spot ? `<div class="memo-spot">📍 ${{spot}}</div>` : ''}}
                        <div class="memo-body">${{body}}</div>
                        ${{author ? `<div class="memo-author">投稿者: ${{author}}</div>` : ''}}
                    </div>
                    <div class="item-card-actions">
                        <button type="button" class="mini-btn edit-btn" onclick="openMemoModal(${{idx}})" title="編集">✏️</button>
                        <button type="button" class="mini-btn delete-btn" onclick="deleteMemo(${{idx}})" title="削除">🗑️</button>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        // アイテムモーダル制御
        function openItemModal(cat, idx) {{
            const catKey = cat === 'food' ? '食べ物' : cat === 'drink' ? 'お酒' : '観光地';
            const catLabel = cat === 'food' ? 'グルメ' : cat === 'drink' ? '地酒' : '観光地';
            document.getElementById('modalCategory').value = cat;
            document.getElementById('modalIndex').value = idx;

            if (idx >= 0) {{
                const items = getCategoryItems(catKey);
                const parsed = parseRubyItem(items[idx] || '');
                document.getElementById('itemModalTitle').textContent = `【${{selectedPref}}】${{catLabel}}を編集`;
                document.getElementById('modalItemName').value = parsed.name;
                document.getElementById('modalItemRuby').value = parsed.ruby;
            }} else {{
                document.getElementById('itemModalTitle').textContent = `【${{selectedPref}}】新しい${{catLabel}}を追加`;
                document.getElementById('modalItemName').value = '';
                document.getElementById('modalItemRuby').value = '';
            }}

            document.getElementById('itemModal').style.display = 'flex';
        }}

        function saveItem(e) {{
            e.preventDefault();
            const cat = document.getElementById('modalCategory').value;
            const idx = parseInt(document.getElementById('modalIndex').value, 10);
            const catKey = cat === 'food' ? '食べ物' : cat === 'drink' ? 'お酒' : '観光地';
            const name = document.getElementById('modalItemName').value.trim();
            const ruby = document.getElementById('modalItemRuby').value.trim();

            if (!name) return;
            const finalItem = buildRubyItem(name, ruby);
            const items = getCategoryItems(catKey);

            if (idx >= 0) {{
                items[idx] = finalItem;
            }} else {{
                items.push(finalItem);
            }}

            setCategoryItems(catKey, items);
            closeModal('itemModal');
            showToast(`✅ 「${{name}}」を保存しました`);
        }}

        function deleteItem(catKey, idx) {{
            const items = getCategoryItems(catKey);
            const item = items[idx];
            const parsed = parseRubyItem(item);
            if (confirm(`本当に「${{parsed.name}}」を削除しますか？`)) {{
                items.splice(idx, 1);
                setCategoryItems(catKey, items);
                showToast(`🗑️ 「${{parsed.name}}」を削除しました`);
            }}
        }}

        // メモモーダル制御
        function openMemoModal(idx) {{
            document.getElementById('modalMemoIndex').value = idx;
            const rawMemo = currentData[selectedPref]['メモ'] || '';
            const entries = (!rawMemo || rawMemo === 'なし') ? [] : rawMemo.replace(/\\n/g, '、').split('、').map(s => s.trim()).filter(s => s);

            if (idx >= 0) {{
                document.getElementById('memoModalTitle').textContent = `【${{selectedPref}}】口コミ・メモを編集`;
                const entry = entries[idx] || '';
                let spot = '';
                let body = entry;
                let author = '';

                const p1 = entry.split(/[:：]/);
                if (p1.length >= 2) {{
                    spot = p1[0].trim();
                    body = p1.slice(1).join(':').trim();
                }}
                const p2 = body.match(/^(.*?)[（\\(]by\\s*([^）\\)]+)[）\\)]$/);
                if (p2) {{
                    body = p2[1].trim();
                    author = p2[2].trim();
                }}

                document.getElementById('modalMemoSpot').value = spot;
                document.getElementById('modalMemoBody').value = body;
                document.getElementById('modalMemoAuthor').value = author;
            }} else {{
                document.getElementById('memoModalTitle').textContent = `【${{selectedPref}}】新しい口コミ・メモを追加`;
                document.getElementById('modalMemoSpot').value = '';
                document.getElementById('modalMemoBody').value = '';
                document.getElementById('modalMemoAuthor').value = '';
            }}

            document.getElementById('memoModal').style.display = 'flex';
        }}

        function saveMemo(e) {{
            e.preventDefault();
            const idx = parseInt(document.getElementById('modalMemoIndex').value, 10);
            const spot = document.getElementById('modalMemoSpot').value.trim();
            const body = document.getElementById('modalMemoBody').value.trim();
            const author = document.getElementById('modalMemoAuthor').value.trim();

            if (!spot || !body) return;

            let entry = `${{spot}}: ${{body}}`;
            if (author) entry += `（by ${{author}}）`;

            const rawMemo = currentData[selectedPref]['メモ'] || '';
            const entries = (!rawMemo || rawMemo === 'なし') ? [] : rawMemo.replace(/\\n/g, '、').split('、').map(s => s.trim()).filter(s => s);

            if (idx >= 0) {{
                entries[idx] = entry;
            }} else {{
                entries.push(entry);
            }}

            currentData[selectedPref]['メモ'] = entries.length === 0 ? 'なし' : entries.join('、');
            renderMemoGrid();
            closeModal('memoModal');
            showToast(`✅ 口コミを保存しました`);
        }}

        function deleteMemo(idx) {{
            const rawMemo = currentData[selectedPref]['メモ'] || '';
            const entries = (!rawMemo || rawMemo === 'なし') ? [] : rawMemo.replace(/\\n/g, '、').split('、').map(s => s.trim()).filter(s => s);
            if (confirm('この口コミを削除しますか？')) {{
                entries.splice(idx, 1);
                currentData[selectedPref]['メモ'] = entries.length === 0 ? 'なし' : entries.join('、');
                renderMemoGrid();
                showToast('🗑️ 口コミを削除しました');
            }}
        }}

        function closeModal(id) {{
            document.getElementById(id).style.display = 'none';
        }}

        function closeModalOnBackdrop(e, id) {{
            if (e.target.id === id) closeModal(id);
        }}

        // JSONエクスポート（ダウンロード）
        function exportJsonFile() {{
            const jsonStr = JSON.stringify(currentData, null, 2);
            const blob = new Blob([jsonStr], {{ type: 'application/json;charset=utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'patamap_data.json';
            a.click();
            URL.revokeObjectURL(url);
            showToast('📥 patamap_data.json をダウンロードしました');
        }}

        // JSONコピー
        function copyJsonToClipboard() {{
            const jsonStr = JSON.stringify(currentData, null, 2);
            navigator.clipboard.writeText(jsonStr).then(() => {{
                showToast('📋 JSONをクリップボードにコピーしました');
            }}).catch(() => {{
                alert('クリップボードへのコピーに失敗しました');
            }});
        }}

        // 全リセット
        function resetAllChanges() {{
            if (confirm('すべての未保存の編集を破棄して、初期状態に戻しますか？')) {{
                currentData = JSON.parse(JSON.stringify(initialData));
                renderCurrentPref();
                showToast('🔄 データを初期状態にリセットしました');
            }}
        }}

        // GitHub保存モーダル
        function openGithubModal() {{
            document.getElementById('githubModal').style.display = 'flex';
        }}

        function loadSavedGitHubSettings() {{
            const token = localStorage.getItem('patamap_gh_token');
            const repo = localStorage.getItem('patamap_gh_repo');
            const branch = localStorage.getItem('patamap_gh_branch');
            if (token) document.getElementById('ghToken').value = token;
            if (repo) document.getElementById('ghRepo').value = repo;
            if (branch) document.getElementById('ghBranch').value = branch;
        }}

        async function commitToGitHub(e) {{
            e.preventDefault();
            const token = document.getElementById('ghToken').value.trim();
            const repo = document.getElementById('ghRepo').value.trim();
            const branch = document.getElementById('ghBranch').value.trim();
            const message = document.getElementById('ghMessage').value.trim();
            const btn = document.getElementById('ghSubmitBtn');

            if (!token || !repo || !branch || !message) return;

            localStorage.setItem('patamap_gh_token', token);
            localStorage.setItem('patamap_gh_repo', repo);
            localStorage.setItem('patamap_gh_branch', branch);

            btn.disabled = true;
            btn.textContent = '⏳ 保存中...';

            try {{
                // 1. 最新のファイルのSHAを取得
                const getUrl = `https://api.github.com/repos/${{repo}}/contents/patamap_data.json?ref=${{branch}}&t=${{Date.now()}}`;
                const getRes = await fetch(getUrl, {{
                    headers: {{
                        'Authorization': `token ${{token}}`,
                        'Accept': 'application/vnd.github.v3+json'
                    }}
                }});

                if (!getRes.ok) {{
                    throw new Error(`GitHub API エラー (GET): ${{getRes.status}} ${{getRes.statusText}}`);
                }}
                const getData = await getRes.json();
                const sha = getData.sha;

                // 2. 更新データをBase64エンコード
                const jsonContent = JSON.stringify(currentData, null, 2);
                const utf8Bytes = new TextEncoder().encode(jsonContent);
                let binaryStr = '';
                for (let i = 0; i < utf8Bytes.length; i++) {{
                    binaryStr += String.fromCharCode(utf8Bytes[i]);
                }}
                const base64Content = btoa(binaryStr);

                // 3. PUTでコミット更新
                const putUrl = `https://api.github.com/repos/${{repo}}/contents/patamap_data.json`;
                const putRes = await fetch(putUrl, {{
                    method: 'PUT',
                    headers: {{
                        'Authorization': `token ${{token}}`,
                        'Accept': 'application/vnd.github.v3+json',
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        message: message,
                        content: base64Content,
                        sha: sha,
                        branch: branch
                    }})
                }});

                if (!putRes.ok) {{
                    const errData = await putRes.json();
                    throw new Error(`GitHub API エラー (PUT): ${{putRes.status}} ${{errData.message || putRes.statusText}}`);
                }}

                closeModal('githubModal');
                alert('🎉 GitHub リポジトリへの保存が完了しました！\\n\\nGitHub Actions が自動で本番サイトの再ビルドを開始しました。（約15秒で反映されます）');
                showToast('🚀 GitHubへの保存完了！');
            }} catch (err) {{
                alert('❌ 保存に失敗しました:\\n' + err.message);
            }} finally {{
                btn.disabled = false;
                btn.textContent = 'GitHubに保存＆自動デプロイ';
            }}
        }}
    </script>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(admin_html_content)

    print(f"[ステップ2 完了] 管理者専用データ編集画面HTMLを生成しました: {os.path.abspath(output_html_path)}")
    return output_html_path


# ==============================================================================
# 4. メインエントリーポイント
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

    admin_file = create_admin_editor_html(
        json_data_path="patamap_data.json",
        output_html_path="admin.html"
    )

    is_ci = os.environ.get("CI", "false").lower() in ("true", "1")
    if AUTO_OPEN_BROWSER and not is_ci and os.path.exists(html_file):
        print(f"[ステップ3] デフォルトブラウザで地図を開きます: {os.path.abspath(html_file)}")
        webbrowser.open(f"file:///{os.path.abspath(html_file)}")

    print("=" * 60)
    print("🎉 すべての処理が正常に完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()

