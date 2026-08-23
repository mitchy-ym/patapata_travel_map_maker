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

def create_interactive_map_html(geojson_path="japan.geojson", output_html_path="index.html"):
    """
    GeoJSONを読み込み、Google スプレッドシートと直接連携するスタンドアロンWeb地図HTMLを生成します。
    """
    print(f"[ステップ1] 地図GeoJSONデータを読み込み中: {geojson_path}")
    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"エラー: 地図ファイル '{geojson_path}' が見つかりません。")

    with open(geojson_path, "r", encoding="utf-8") as f:
        japan_geojson = json.load(f)

    # 47都道府県の地区デフォルト定義
    pref_regions_default = {}
    for region, prefs in REGION_PREFECTURES.items():
        for p in prefs:
            pref_regions_default[p] = {
                "地区": region,
                "観光地": "読み込み中...",
                "食べ物": "読み込み中...",
                "お酒": "読み込み中...",
                "メモ": ""
            }

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
    <title>リスナーと作る！全国観光マップ～フロリの47都道府県パタパタ旅行～</title>
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
            background-color: {MAP_BG_COLOR};
            background-image: 
                radial-gradient(#dcd5c7 1.2px, transparent 1.2px),
                linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(244, 239, 230, 0.3) 100%);
            background-size: 24px 24px, 100% 100%;
            position: relative;
            overflow: hidden;
        }}
        #main {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }}

        /* 左上フローティングカード（和紙すりガラス調・折りたたみ対応） */
        .floating-card {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 100;
            background: rgba(255, 253, 248, 0.82);
            backdrop-filter: blur(5px);
            padding: 15px 16px 12px 16px;
            border-radius: 18px;
            box-shadow: 0 10px 28px rgba(120, 95, 70, 0.08), 0 2px 6px rgba(120, 95, 70, 0.04);
            border: 1.5px solid rgba(229, 215, 199, 0.85);
            width: 360px;
            max-width: calc(100vw - 32px);
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .floating-card.collapsed {{
            width: auto;
            max-width: calc(100vw - 30px);
            padding: 9px 14px;
            gap: 0;
            border-radius: 14px;
        }}
        .floating-card.collapsed .card-body-collapsible {{
            display: none;
        }}
        .floating-card.collapsed .card-title-sub {{
            display: none;
        }}
        .card-header {{
            display: block;
            width: 100%;
        }}
        .card-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            width: 100%;
        }}
        .card-toggle-btn {{
            background: rgba(120, 95, 70, 0.08);
            border: 1px solid rgba(120, 95, 70, 0.22);
            border-radius: 7px;
            padding: 3px 7px;
            font-size: 10.5px;
            font-weight: 700;
            color: #6b5e50;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 2px;
            flex-shrink: 0;
        }}
        .card-toggle-btn:hover {{
            background: #b91c1c;
            color: #ffffff;
            border-color: #b91c1c;
        }}
        .card-body-collapsible {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
        }}
        .card-title-main {{
            display: block;
            font-size: 15px;
            font-weight: 800;
            color: #b91c1c; /* 茜・朱赤 */
            letter-spacing: -0.3px;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* スポット件数バッジ（提案4） */
        .pref-badge-group {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-left: auto;
        }}
        .count-pill {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 8px;
            line-height: 1.3;
            letter-spacing: -0.2px;
        }}
        .pill-sightseeing {{
            background: rgba(30, 78, 121, 0.1);
            color: #1e4e79;
            border: 1px solid rgba(30, 78, 121, 0.2);
        }}
        .pill-food {{
            background: rgba(185, 28, 28, 0.1);
            color: #991b1b;
            border: 1px solid rgba(185, 28, 28, 0.2);
        }}
        .pill-drink {{
            background: rgba(35, 99, 41, 0.1);
            color: #236329;
            border: 1px solid rgba(35, 99, 41, 0.2);
        }}

        /* 画面全体の同期中オーバーレイ（極薄すりガラス・操作完全ブロック） */
        .full-loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(249, 246, 240, 0.35);
            backdrop-filter: blur(2px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }}
        .full-loading-overlay.hidden {{
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }}
        .loading-card {{
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(6px);
            border: 1.5px solid rgba(229, 215, 199, 0.9);
            padding: 24px 32px;
            border-radius: 20px;
            box-shadow: 0 16px 40px rgba(120, 95, 70, 0.12);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            text-align: center;
            max-width: 90vw;
        }}
        .large-spinner {{
            width: 42px;
            height: 42px;
            border: 3.5px solid #f3e8d8;
            border-top-color: #b91c1c;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }}
        .large-check {{
            width: 42px;
            height: 42px;
            background: #16a34a;
            color: #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: bold;
        }}
        .loading-title {{
            font-size: 17px;
            font-weight: 800;
            color: #2b2b2b;
        }}
        .loading-desc {{
            font-size: 12px;
            font-weight: 500;
            color: #786d5f;
        }}

        /* スマホ・レスポンシブ最適化（提案2） */
        @media (max-width: 640px) {{
            .floating-card {{
                top: 8px;
                left: 8px;
                right: 8px;
                width: auto;
                max-width: none;
                padding: 10px 12px;
                gap: 6px;
            }}
            .card-title-main {{
                font-size: 15px;
            }}
            .card-footer-tip {{
                display: none;
            }}
            .custom-popup-content {{
                max-height: 52vh !important;
                max-width: calc(100vw - 24px) !important;
            }}
        }}
    </style>
</head>
<body>
    <div id="map-container">
        <!-- 操作＆凡例カード（折りたたみ対応） -->
        <div id="floatingCard" class="floating-card">
            <div class="card-header">
                <div class="card-header-row">
                    <div class="card-title-main">リスナーと作る！全国観光マップ</div>
                    <button type="button" id="cardToggleBtn" class="card-toggle-btn" onclick="toggleFloatingCard()" title="メニューを開閉">閉じる ▲</button>
                </div>
                <div class="card-title-sub">～フロリの47都道府県パタパタ旅行～</div>
            </div>
            <div class="card-body-collapsible">
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
                </div>
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

    <!-- 画面全体の同期中オーバーレイ（操作完全ブロック） -->
    <div id="fullLoadingOverlay" class="full-loading-overlay">
        <div class="loading-card">
            <div id="loadingIcon" class="large-spinner"></div>
            <div class="loading-title" id="loadingTitle">🔄 最新データを同期中...</div>
            <div class="loading-desc" id="loadingDesc">Googleスプレッドシートから47都道府県の最新情報を取得しています</div>
        </div>
    </div>

    <!-- フローティング通知（自動で消えるトースト） -->
    <div id="toastNotification" class="toast-notification">✅ 保存しました</div>

    <style>
        .toast-notification {{
            position: fixed;
            top: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(-24px);
            background: rgba(30, 41, 59, 0.94);
            backdrop-filter: blur(8px);
            color: #ffffff;
            padding: 10px 24px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 700;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.15);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 99999;
            opacity: 0;
            pointer-events: none;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .toast-notification.show {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}
    </style>

    <script>
        let patamapData = {json.dumps(pref_regions_default, ensure_ascii=False)};
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

        // 都道府県のメモテキストを辞書化する関数（複数口コミ・長文対応）
        function parsePrefMemos(memoText) {{
            const memoMap = {{}};
            if (!memoText || memoText === 'なし') return memoMap;
            
            // 改行または特殊区切りで1件ずつ分割（改行がない場合は読点分割）
            let entries = [];
            if (memoText.indexOf('\\n') !== -1) {{
                entries = memoText.split(/\\r?\\n/);
            }} else {{
                entries = memoText.split('、');
            }}

            entries.forEach(entry => {{
                if (!entry || !entry.trim()) return;
                const idx = entry.indexOf(':');
                const idxZen = entry.indexOf('：');
                const sepIdx = (idx !== -1 && idxZen !== -1) ? Math.min(idx, idxZen) : (idx !== -1 ? idx : idxZen);
                
                if (sepIdx !== -1) {{
                    const rawKey = entry.substring(0, sepIdx).trim();
                    const key = rawKey.replace(/<rt>[^<]*<\\/rt>/g, '').replace(/<[^>]+>/g, '');
                    const val = entry.substring(sepIdx + 1).trim();
                    if (key && val) {{
                        if (!memoMap[key]) {{
                            memoMap[key] = [];
                        }}
                        memoMap[key].push(val);
                    }}
                }}
            }});

            // 複数口コミがある場合は見やすく箇条書きで結合
            const mergedMap = {{}};
            for (let k in memoMap) {{
                if (memoMap[k].length === 1) {{
                    mergedMap[k] = memoMap[k][0];
                }} else {{
                    mergedMap[k] = memoMap[k].map((m, i) => `<div style="margin-bottom:6px; padding-bottom:4px; border-bottom:1px dashed #e2d9cc;">💬 ${{m}}</div>`).join('');
                }}
            }}
            return mergedMap;
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

        // Google Apps Script (スプレッドシート直結エンドポイント)
        const GAS_API_URL = "https://script.google.com/macros/s/AKfycbyJTZ65iQGVbYd5MvJhyEK7jdV5ceh_O12vjtm2TCAUFqB3cykww9U6fkfojw90ySjx/exec";

        // スプレッドシートから最新データを非同期で取得して地図データをリアルタイム更新（全画面オーバーレイ連動）
        async function fetchLatestDataFromSpreadsheet() {{
            const overlay = document.getElementById('fullLoadingOverlay');
            const icon = document.getElementById('loadingIcon');
            const title = document.getElementById('loadingTitle');
            const desc = document.getElementById('loadingDesc');

            try {{
                const res = await fetch(GAS_API_URL);
                if (res.ok) {{
                    const latest = await res.json();
                    if (latest && typeof latest === 'object' && !latest.status && Object.keys(latest).length >= 40) {{
                        patamapData = latest;
                        console.log("✅ Googleスプレッドシートから最新データを同期しました (47都道府県)");
                    }}
                }}
            }} catch (err) {{
                console.warn("⚠️ スプレッドシート同期スキップ（初期キャッシュデータを使用）:", err);
            }}

            // 同期完了の視覚フィードバック
            if (icon && title && desc) {{
                icon.className = 'large-check';
                icon.innerHTML = '✓';
                title.textContent = '🎉 最新データ同期完了！';
                desc.textContent = '47都道府県の最新マップを開きます...';
            }}

            // 0.45秒後に全画面オーバーレイをふわっと解除して操作可能に
            setTimeout(() => {{
                if (overlay) overlay.classList.add('hidden');
            }}, 450);
        }}
        fetchLatestDataFromSpreadsheet();

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

            // Google スプレッドシートに非同期送信
            fetch(GAS_API_URL, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
                body: JSON.stringify({{
                    pref: pref,
                    category: cat,
                    itemName: itemName,
                    itemRuby: itemRuby,
                    memo: memo,
                    author: author
                }})
            }}).then(() => {{
                console.log("✅ スプレッドシートに投稿が保存されました！");
            }}).catch(err => {{
                console.error("❌ スプレッドシート送信エラー:", err);
            }});

            const modal = document.getElementById('addModal');
            if (modal) modal.style.display = 'none';

            // 自動で消えるトースト通知を表示
            showToast('✅ 保存しました');
            
            // ポップアップを更新
            jumpToPref(pref);
        }};

        // フローティング・トースト通知表示関数
        function showToast(message) {{
            const toast = document.getElementById('toastNotification');
            if (!toast) return;
            toast.textContent = message || '✅ 保存しました';
            toast.classList.add('show');
            clearTimeout(window.toastTimer);
            window.toastTimer = setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2400);
        }}

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

                        function getCount(text) {{
                            if (!text || text === 'なし' || text === '読み込み中...') return 0;
                            return text.replace(/\\n/g, '、').replace(/,/g, '、').split('、').map(s => s.trim()).filter(s => s).length;
                        }}
                        const countSight = getCount(prefData['観光地']);
                        const countFood = getCount(prefData['食べ物']);
                        const countDrink = getCount(prefData['お酒']);

                        return `
                            <div class="tooltip-card">
                                <div class="tooltip-header" style="border-bottom-color: ${{colorInfo.hover}};">
                                    <div class="tooltip-pref-title" style="color: ${{colorInfo.text}};">
                                        <span>📍 ${{prefName}}</span>
                                    </div>
                                    <div class="pref-badge-group">
                                        <span class="count-pill pill-sightseeing" title="観光地 ${{countSight}}件">📸 ${{countSight}}</span>
                                        <span class="count-pill pill-food" title="グルメ ${{countFood}}件">🍽️ ${{countFood}}</span>
                                        <span class="count-pill pill-drink" title="地酒 ${{countDrink}}件">🍶 ${{countDrink}}</span>
                                        <span class="tooltip-region-badge" style="background:${{colorInfo.badge_bg}}; color:${{colorInfo.text}}; border:1px solid ${{colorInfo.color}};">
                                            ${{region}}
                                        </span>
                                    </div>
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

        // 左上操作ボックスの折りたたみ／展開切り替え関数
        function toggleFloatingCard() {{
            const card = document.getElementById('floatingCard');
            const btn = document.getElementById('cardToggleBtn');
            if (!card || !btn) return;
            card.classList.toggle('collapsed');
            if (card.classList.contains('collapsed')) {{
                btn.innerHTML = 'メニュー開く ▼';
                btn.title = 'メニューを展開';
            }} else {{
                btn.innerHTML = '閉じる ▲';
                btn.title = 'メニューを折りたたむ';
            }}
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
        geojson_path="japan.geojson",
        output_html_path="index.html"
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
