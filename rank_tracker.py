"""
排名追蹤：儲存本次資料、比對上次資料、計算排名變化
"""
import json
import os
from datetime import datetime

SNAPSHOT_FILE = "rank_snapshot.json"


def load_previous() -> dict:
    """讀取上次的排名快照"""
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    try:
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_snapshot(appstore_data: dict, gplay_data: dict):
    """將本次排名存成快照供下次比對"""
    snapshot = {
        "date": datetime.now().strftime("%Y/%m/%d"),
        "appstore": appstore_data,
        "gplay": gplay_data,
    }
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print("  💾 排名快照已儲存：{}".format(SNAPSHOT_FILE))


def build_rank_map(data: dict) -> dict:
    """
    將 {country: {chart: [{app_id, rank, ...}]}} 轉成
    {country: {chart: {app_id: rank}}} 方便查找
    """
    result = {}
    for country, charts in data.items():
        result[country] = {}
        for chart, apps in charts.items():
            result[country][chart] = {
                a["app_id"]: a["rank"] for a in apps if a.get("app_id")
            }
    return result


def add_rank_changes(appstore_data: dict, gplay_data: dict, previous: dict):
    """
    在每個 app 資料中加入 rank_change 欄位：
    正數 = 上升（e.g. +3），負數 = 下降（e.g. -2），0 = 不變，None = 新進榜
    """
    prev_as = build_rank_map(previous.get("appstore", {}))
    prev_gp = build_rank_map(previous.get("gplay", {}))

    def annotate(data, prev_map):
        for country, charts in data.items():
            for chart, apps in charts.items():
                prev_chart = (prev_map.get(country) or {}).get(chart, {})
                for app in apps:
                    app_id = app.get("app_id", "")
                    if app_id in prev_chart:
                        app["rank_change"] = prev_chart[app_id] - app["rank"]
                    else:
                        app["rank_change"] = None  # 新進榜

    annotate(appstore_data, prev_as)
    annotate(gplay_data, prev_gp)
