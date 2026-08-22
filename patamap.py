#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
PataMap（パタマップ）- Vtuberリスナー参加型 全国観光マップ自動生成パイプライン
==============================================================================
Excelファイル（旅行企画用.xlsx）のシート（地区）ごとに都道府県を色分けし、
EChartsを使用した日本地図のみ（日本語都道府県表示・関東初期フォーカス）の
インタラクティブHTML（index.html）を自動生成します。
"""

import os
import json
import webbrowser
import requests
import pandas as pd

# ==============================================================================
# 【ユーザー設定エリア】環境や用途に合わせてここを変更してください
# ==============================================================================

# 入力元Excelファイルのパス（ルートまたはoriginal/フォルダ内を自動探索）
EXCEL_FILE_PATH = "旅行企画用.xlsx"

# 読み込むシート設定
# None: 全シートを自動スキャンして結合（Excelの全シート＝地区として扱います）
SHEET_NAME = None

# 出力ファイル設定
JSON_OUTPUT_PATH = "patamap_data.json"   # ステップ1で出力するJSONファイル名
HTML_OUTPUT_PATH = "index.html"          # ステップ2で出力するHTMLファイル名（GitHub Pages用）

# GeoJSONファイル（日本の都道府県境界データ）のパス
GEOJSON_FILE_PATH = "japan.geojson"
# GeoJSONがローカルにない場合の自動ダウンロード先URL
GEOJSON_DOWNLOAD_URL = "https://raw.githubusercontent.com/dataofjapan/land/master/japan.geojson"

# Excelの列名・項目名設定
COL_PREFECTURE = "都道府県"   # 都道府県名を示す列名/キーワード
COL_SIGHTSEEING = "観光地"    # 観光地を示す列名/キーワード
COL_FOOD = "食べ物"          # 食べ物を示す列名/キーワード
COL_DRINK = "お酒"           # お酒を示す列名/キーワード

# 地図の初期表示設定（関東地方中心）
INITIAL_CENTER = [139.6, 36.3]  # [経度, 緯度] 関東地方中心
INITIAL_ZOOM = 4.5              # 初期のズームレベル (全国: 1.25, 関東拡大: 4〜5)

# 背景カラー設定
MAP_BG_COLOR = "#fcf9f2"        # 背景色（優しいクリーム色）

# ==============================================================================
# 地区（Excelシート）ごとのカラー設定
# ==============================================================================
REGION_COLORS = {
    "北海道+東北": {
        "color": "#93C5FD",        # 塗りつぶし色（淡いスカイブルー）
        "hover": "#60A5FA",        # ホバー色
        "text": "#1D4ED8",         # テキスト色
        "badge_bg": "#EFF6FF"      # バッジ背景色
    },
    "関東": {
        "color": "#FDA4AF",        # 塗りつぶし色（淡いローズピンク）
        "hover": "#F43F5E",        # ホバー色
        "text": "#BE123C",         # テキスト色
        "badge_bg": "#FFF1F2"      # バッジ背景色
    },
    "中部": {
        "color": "#A7F3D0",        # 塗りつぶし色（淡いミントグリーン: 中部1+中部2統合）
        "hover": "#34D399",        # ホバー色
        "text": "#047857",         # テキスト色
        "badge_bg": "#ECFDF5"      # バッジ背景色
    },
    "関西": {
        "color": "#D8B4FE",        # 塗りつぶし色（淡いパープル）
        "hover": "#A855F7",        # ホバー色
        "text": "#7E22CE",         # テキスト色
        "badge_bg": "#FAF5FF"      # バッジ背景色
    },
    "中国+四国": {
        "color": "#FDBA74",        # 塗りつぶし色（淡いコーラルオレンジ）
        "hover": "#FB923C",        # ホバー色
        "text": "#C2410C",         # テキスト色
        "badge_bg": "#FFF7ED"      # バッジ背景色
    },
    "九州+沖縄": {
        "color": "#99F6E4",        # 塗りつぶし色（淡いターコイズグリーン）
        "hover": "#2DD4BF",        # ホバー色
        "text": "#0F766E",         # テキスト色
        "badge_bg": "#F0FDFA"      # バッジ背景色
    },
    "その他": {
        "color": "#E5E7EB",        # 未分類用グレー
        "hover": "#CBD5E1",
        "text": "#475569",
        "badge_bg": "#F8FAFC"
    }
}

# 地図生成後に自動でデフォルトブラウザを開くかどうか (True: 開く, False: 開かない)
AUTO_OPEN_BROWSER = True

# ==============================================================================
# 日本の47都道府県マスター定義
# ==============================================================================
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

# 地区ごとの中心座標と推奨ズーム
REGION_CENTERS = {
    "北海道+東北": {"center": [141.0, 39.5], "zoom": 3.0},
    "関東": {"center": [139.6, 36.3], "zoom": 4.5},
    "中部": {"center": [137.5, 36.0], "zoom": 3.8},
    "関西": {"center": [135.5, 34.8], "zoom": 4.5},
    "中国+四国": {"center": [133.2, 34.3], "zoom": 4.0},
    "九州+沖縄": {"center": [130.2, 32.2], "zoom": 3.5}
}


def normalize_prefecture_name(raw_name: str) -> str:
    """都道府県名から『県』『府』『都』『道』の表記ゆれを吸収して正式名称を返します"""
    if not raw_name or not isinstance(raw_name, str):
        return None
    name = raw_name.strip().replace("\n", "").replace(" ", "").replace("\u3000", "")
    for pref in ALL_PREFECTURES:
        if name == pref:
            return pref
        short_name = pref[:-1] if pref.endswith(("都", "道", "府", "県")) else pref
        if name == short_name or name.startswith(short_name):
            return pref
    return None


# ==============================================================================
# 【ステップ1】データ抽出とJSON化 (Excel -> JSON)
# ==============================================================================
def extract_excel_to_json(
    excel_path: str = EXCEL_FILE_PATH,
    sheet_name=SHEET_NAME,
    json_path: str = JSON_OUTPUT_PATH
) -> dict:
    """
    Excelファイルを読み込み、都道府県ごとの「地区」「観光地」「食べ物」「お酒」を抽出して
    JSONファイルに保存します。
    """
    if not os.path.exists(excel_path):
        alt_path = os.path.join("original", os.path.basename(excel_path))
        if os.path.exists(alt_path):
            excel_path = alt_path
        else:
            raise FileNotFoundError(f"指定されたExcelファイルが見つかりません: {excel_path}")

    print(f"[ステップ1] Excelファイル '{excel_path}' を読み込み中...")
    xl = pd.ExcelFile(excel_path)

    # 読み込む対象シートの決定
    if sheet_name is None:
        target_sheets = [s for s in xl.sheet_names if s != "原本"]
    elif isinstance(sheet_name, (int, str)):
        target_sheets = [xl.sheet_names[sheet_name] if isinstance(sheet_name, int) else sheet_name]
    elif isinstance(sheet_name, list):
        target_sheets = sheet_name
    else:
        target_sheets = xl.sheet_names

    # 結果を保持する辞書（47都道府県を初期化）
    result_data = {
        pref: {"地区": "その他", "観光地": "なし", "食べ物": "なし", "お酒": "なし"}
        for pref in ALL_PREFECTURES
    }

    def clean_cell_value(val):
        """セルの欠損値を処理し、末尾の不要な記号をトリムします"""
        if pd.isna(val) or val is None:
            return "なし"
        s = str(val).strip()
        s = s.rstrip("、").rstrip(",").strip()
        return s if s else "なし"

    def map_sheet_to_region(name):
        """Excelシート名を統一地区名にマッピング（中部統合、編の除去）"""
        s = str(name).strip()
        if s in ["中部1", "中部2", "中部１", "中部２"]:
            return "中部"
        if s in ["北海道+東北編", "北海道＋東北編", "北海道+東北", "北海道＋東北"]:
            return "北海道+東北"
        if s in ["関東編", "関東"]:
            return "関東"
        return s

    # 各シートをスキャン
    for s_name in target_sheets:
        region_name = map_sheet_to_region(s_name)
        df = pd.read_excel(excel_path, sheet_name=s_name, header=None)
        if df.empty:
            continue

        # ヘッダー行を検索して「観光地」「食べ物」「お酒」の列位置を特定
        col_sightseeing = None
        col_food = None
        col_drink = None

        for r_idx in range(min(10, len(df))):
            row_vals = [str(v).strip() if pd.notna(v) else "" for v in df.iloc[r_idx]]
            for c_idx, val in enumerate(row_vals):
                if COL_SIGHTSEEING in val and col_sightseeing is None:
                    col_sightseeing = c_idx
                elif COL_FOOD in val and col_food is None:
                    col_food = c_idx
                elif COL_DRINK in val and col_drink is None:
                    col_drink = c_idx

        # デフォルト列インデックス（旅行企画用.xlsx の 13, 17, 21）
        if col_sightseeing is None and df.shape[1] > 13:
            col_sightseeing = 13
        if col_food is None and df.shape[1] > 17:
            col_food = 17
        if col_drink is None and df.shape[1] > 21:
            col_drink = 21

        # 各行を走査して都道府県データを抽出
        for r_idx in range(len(df)):
            cell_val = df.iat[r_idx, 0] if df.shape[1] > 0 else None
            if pd.isna(cell_val):
                continue

            matched_pref = normalize_prefecture_name(str(cell_val))
            if matched_pref:
                sight_val = df.iat[r_idx, col_sightseeing] if (col_sightseeing is not None and col_sightseeing < df.shape[1]) else None
                food_val = df.iat[r_idx, col_food] if (col_food is not None and col_food < df.shape[1]) else None
                drink_val = df.iat[r_idx, col_drink] if (col_drink is not None and col_drink < df.shape[1]) else None

                result_data[matched_pref] = {
                    "地区": region_name,
                    "観光地": clean_cell_value(sight_val),
                    "食べ物": clean_cell_value(food_val),
                    "お酒": clean_cell_value(drink_val),
                }

    # 通常テーブル形式（列ヘッダー型）の場合の追加チェック
    if all(result_data[p]["観光地"] == "なし" for p in ALL_PREFECTURES):
        print("※ 通常テーブル形式として再スキャンします...")
        for s_name in target_sheets:
            df_named = pd.read_excel(excel_path, sheet_name=s_name)
            col_map = {}
            for c in df_named.columns:
                c_str = str(c).strip()
                if COL_PREFECTURE in c_str: col_map["pref"] = c
                elif COL_SIGHTSEEING in c_str: col_map["sight"] = c
                elif COL_FOOD in c_str: col_map["food"] = c
                elif COL_DRINK in c_str: col_map["drink"] = c

            if "pref" in col_map:
                for _, row in df_named.iterrows():
                    p_name = normalize_prefecture_name(str(row.get(col_map["pref"], "")))
                    if p_name:
                        result_data[p_name] = {
                            "地区": s_name,
                            "観光地": clean_cell_value(row.get(col_map.get("sight"), "なし")),
                            "食べ物": clean_cell_value(row.get(col_map.get("food"), "なし")),
                            "お酒": clean_cell_value(row.get(col_map.get("drink"), "なし")),
                        }

    # JSONファイルとして出力・保存（UTF-8 & インデント整形）
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    valid_count = sum(1 for p, d in result_data.items() if d["観光地"] != "なし" or d["食べ物"] != "なし" or d["お酒"] != "なし")
    print(f"[ステップ1 完了] {len(result_data)}都道府県中 {valid_count}件のデータを抽出しました。")
    print(f" -> JSON保存先: {os.path.abspath(json_path)}")
    return result_data


# ==============================================================================
# GeoJSONデータの準備ヘルパー
# ==============================================================================
def prepare_geojson(geojson_path: str = GEOJSON_FILE_PATH, download_url: str = GEOJSON_DOWNLOAD_URL) -> dict:
    """ローカルにGeoJSONがあれば読み込み、なければ自動ダウンロードしてキャッシュします"""
    if os.path.exists(geojson_path):
        print(f"GeoJSONファイル '{geojson_path}' を読み込みます。")
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    else:
        print(f"GeoJSONがローカルにないため、ダウンロード中: {download_url}")
        resp = requests.get(download_url, timeout=30)
        resp.raise_for_status()
        geojson_data = resp.json()

        def round_coords(coords, precision=4):
            if isinstance(coords, (int, float)):
                return round(coords, precision)
            elif isinstance(coords, list):
                return [round_coords(c, precision) for c in coords]
            return coords

        for feat in geojson_data.get("features", []):
            feat["geometry"]["coordinates"] = round_coords(feat["geometry"]["coordinates"], 4)

        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f, ensure_ascii=False)
        print(f"GeoJSONを最適化して保存しました: {geojson_path}")

    # 各featureのnameプロパティを日本語都道府県名に正規化
    for feat in geojson_data.get("features", []):
        props = feat.setdefault("properties", {})
        raw_name = props.get("nam_ja") or props.get("name_ja") or props.get("nam") or props.get("name") or ""
        normalized = normalize_prefecture_name(raw_name)
        props["name"] = normalized if normalized else raw_name

    return geojson_data


# ==============================================================================
# 【ステップ2】EChartsによる日本地図HTML生成 (JSON -> HTML)
# ==============================================================================
def generate_map_html(
    json_path: str = JSON_OUTPUT_PATH,
    html_path: str = HTML_OUTPUT_PATH,
    geojson_path: str = GEOJSON_FILE_PATH
) -> str:
    """
    patamap_data.json と GeoJSON を読み込み、地区ごとに色分けされた
    インタラクティブ日本地図HTML（index.html）を生成します。
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSONファイルが見つかりません: {json_path}")

    print(f"[ステップ2] 地図データを読み込み中: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data_dict = json.load(f)

    # GeoJSONの準備（日本語都道府県名プロパティ付き）
    geojson_data = prepare_geojson(geojson_path)

    # HTMLにインライン埋め込み（CORSエラーを回避し完全スタンドアロンで動作）
    geojson_json_str = json.dumps(geojson_data, ensure_ascii=False)
    data_json_str = json.dumps(data_dict, ensure_ascii=False)
    centers_json_str = json.dumps(PREFECTURE_CENTERS, ensure_ascii=False)
    region_centers_json_str = json.dumps(REGION_CENTERS, ensure_ascii=False)
    region_colors_json_str = json.dumps(REGION_COLORS, ensure_ascii=False)

    # 都道府県セレクトボックス用のオプションHTML（地区ごとにオプショングループ分け）
    region_to_prefs = {}
    for p in ALL_PREFECTURES:
        reg = data_dict.get(p, {}).get("地区", "その他")
        region_to_prefs.setdefault(reg, []).append(p)

    options_html_parts = ['<option value="">🔍 都道府県へジャンプ...</option>']
    for reg_name, prefs in region_to_prefs.items():
        options_html_parts.append(f'<optgroup label="📍 {reg_name}">')
        for p in prefs:
            options_html_parts.append(f'<option value="{p}">{p}</option>')
        options_html_parts.append('</optgroup>')
    options_html = "".join(options_html_parts)

    # 地区凡例バッジのHTML
    legend_badges_parts = []
    for reg_name, c_info in REGION_COLORS.items():
        if reg_name == "その他":
            continue
        legend_badges_parts.append(
            f'<button class="region-chip" onclick="jumpToRegion(\'{reg_name}\')" '
            f'style="background:{c_info["badge_bg"]}; border:1px solid {c_info["color"]}; color:{c_info["text"]};" '
            f'title="{reg_name}にフォーカス">'
            f'<span class="region-dot" style="background:{c_info["color"]};"></span>{reg_name}'
            f'</button>'
        )
    legend_badges_html = "".join(legend_badges_parts)

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リスナーと作る！全国観光マップ フロリの47都道府県パタパタ旅行企画</title>
    <!-- EChartsライブラリの読み込み -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
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

        /* 地区別カラー凡例バー */
        .region-legend-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            padding: 6px 0;
            border-top: 1px dashed #e2e8f0;
            border-bottom: 1px dashed #e2e8f0;
        }}
        .region-chip {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 7px;
            border-radius: 10px;
            font-size: 10.5px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.15s ease;
            outline: none;
        }}
        .region-chip:hover {{
            transform: scale(1.04);
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .region-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }}

        .card-action-row {{
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .pref-select-box {{
            flex: 1;
            padding: 7px 8px;
            border-radius: 8px;
            border: 1.5px solid #cbd5e1;
            font-size: 11.5px;
            background: #ffffff;
            color: #1e293b;
            outline: none;
            cursor: pointer;
            transition: border-color 0.2s;
        }}
        .pref-select-box:focus {{
            border-color: #f43f5e;
        }}
        .btn-all-japan {{
            padding: 7px 12px;
            background: #f43f5e;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 11.5px;
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
            color: #94a3b8;
            line-height: 1.3;
        }}
        .card-footer-tip strong {{
            color: #64748b;
        }}

        /* ツールチップ内のカスタムスタイル */
        .tooltip-card {{
            padding: 14px 16px;
            width: 330px;
            max-height: 480px;
            overflow-y: auto;
            white-space: normal;
            line-height: 1.5;
            font-size: 13px;
            box-sizing: border-box;
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
            margin-bottom: 9px;
        }}
        .tooltip-title {{
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 3px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .sightseeing-title {{ color: #2e7d32; }}
        .food-title {{ color: #ef6c00; }}
        .drink-title {{ color: #0288d1; }}
        .tooltip-content {{
            font-size: 12px;
            background: #f9f9f9;
            padding: 6px 8px;
            border-radius: 6px;
            border-left: 3px solid #ccc;
            max-height: 100px;
            overflow-y: auto;
        }}
        .sightseeing-box {{ background: #f1f8e9; border-left-color: #81c784; }}
        .food-box {{ background: #fff8e1; border-left-color: #ffb74d; }}
        .drink-box {{ background: #e1f5fe; border-left-color: #4fc3f7; }}
    </style>
</head>
<body>
    <div id="map-container">
        <!-- 左上フローティングカード -->
        <div class="floating-card">
            <div class="card-header">
                <div class="card-title-main">リスナーと作る！全国観光マップ</div>
                <div class="card-title-sub">フロリの47都道府県パタパタ旅行企画</div>
            </div>

            <!-- 地区別カラー凡例 & クイックジャンプ -->
            <div class="region-legend-row">
                {legend_badges_html}
            </div>

            <div class="card-action-row">
                <select id="pref-select" class="pref-select-box" onchange="jumpToPref(this.value)">
                    {options_html}
                </select>
                <button class="btn-all-japan" onclick="resetToJapan()" title="日本全国を表示">全国</button>
            </div>

            <div class="card-footer-tip">
                💡 地区ボタンで地区拡大 / 都道府県に<strong>ホバー</strong>で詳細表示
            </div>
        </div>

        <!-- 地図描画領域 -->
        <div id="main"></div>
    </div>

    <script>
        // Pythonからインライン展開されたデータ
        const patamapData = {data_json_str};
        const geoJsonData = {geojson_json_str};
        const prefCenters = {centers_json_str};
        const regionCenters = {region_centers_json_str};
        const regionColors = {region_colors_json_str};

        const chartDom = document.getElementById('main');
        const myChart = echarts.init(chartDom);

        // 日本地図 GeoJSON を ECharts に登録
        echarts.registerMap('Japan', geoJsonData);

        // 各都道府県のデータを構築（地区ごとに色分け）
        const mapData = [];
        geoJsonData.features.forEach(function (feature) {{
            const prefName = feature.properties.name;
            const prefInfo = patamapData[prefName] || {{}};
            const region = prefInfo['地区'] || 'その他';
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

        // テキストを箇条書きHTMLに整形する関数
        function formatList(text) {{
            if (!text || text === 'なし') return '<span style="color:#999; font-style:italic;">なし</span>';
            const items = text.replace(/\\n/g, '、').replace(/,/g, '、').split('、').map(s => s.trim()).filter(s => s);
            if (items.length === 0) return '<span style="color:#999; font-style:italic;">なし</span>';
            if (items.length === 1) return items[0];
            return '<ul style="margin:0; padding-left:16px; list-style-type:disc;">' +
                   items.map(i => '<li style="margin-bottom:2px;">' + i + '</li>').join('') +
                   '</ul>';
        }}

        const option = {{
            tooltip: {{
                trigger: 'item',
                enterable: true,
                confine: true,
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                borderColor: '#f43f5e',
                borderWidth: 2,
                padding: 0,
                borderRadius: 14,
                extraCssText: 'box-shadow: 0 10px 28px rgba(0,0,0,0.18);',
                textStyle: {{ color: '#333' }},
                formatter: function (params) {{
                    const prefName = params.name;
                    const prefData = patamapData[prefName];
                    if (prefData) {{
                        const region = prefData['地区'] || 'その他';
                        const colorInfo = regionColors[region] || regionColors['その他'];
                        const sightHtml = formatList(prefData['観光地']);
                        const foodHtml = formatList(prefData['食べ物']);
                        const drinkHtml = formatList(prefData['お酒']);

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
                                    <div class="tooltip-title sightseeing-title">📸 観光地・名所</div>
                                    <div class="tooltip-content sightseeing-box">${{sightHtml}}</div>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title food-title">🍽️ ご当地グルメ・食べ物</div>
                                    <div class="tooltip-content food-box">${{foodHtml}}</div>
                                </div>
                                <div class="tooltip-section">
                                    <div class="tooltip-title drink-title">🍶 地酒・お酒</div>
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

        function navigateMap(centerCoords, zoomLevel) {{
            myChart.setOption({{
                series: [{{
                    center: centerCoords,
                    zoom: zoomLevel
                }}]
            }});
        }}

        function jumpToPref(prefName) {{
            if (!prefName || !prefCenters[prefName]) return;
            navigateMap(prefCenters[prefName], 8);
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

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[ステップ2 完了] 地区別色分け日本地図HTMLを生成しました: {os.path.abspath(html_path)}")
    return html_path


# ==============================================================================
# メイン実行パイプライン
# ==============================================================================
def main():
    print("=" * 60)
    print("🚀 PataMap（パタマップ）旅行マップ自動生成パイプライン 開始")
    print("=" * 60)

    try:
        # ステップ1: Excelからデータを抽出しJSON化
        extract_excel_to_json(
            excel_path=EXCEL_FILE_PATH,
            sheet_name=SHEET_NAME,
            json_path=JSON_OUTPUT_PATH
        )

        # ステップ2: JSONからインタラクティブ日本地図HTMLを生成
        generate_map_html(
            json_path=JSON_OUTPUT_PATH,
            html_path=HTML_OUTPUT_PATH,
            geojson_path=GEOJSON_FILE_PATH
        )

        # ステップ3: デフォルトブラウザで自動起動
        if AUTO_OPEN_BROWSER:
            abs_html_path = os.path.abspath(HTML_OUTPUT_PATH)
            print(f"[ステップ3] デフォルトブラウザで地図を開きます: {abs_html_path}")
            webbrowser.open(f"file://{abs_html_path}")

        print("=" * 60)
        print("🎉 すべての処理が正常に完了しました！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
