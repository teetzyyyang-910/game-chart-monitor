"""
排名快照管理：儲存 / 載入 / 比對
支援自訂快照檔案名稱（daily / weekly 分開）
"""
import json
import os
from datetime import datetime

DEFAULT_SNAPSHOT = "rank_snapshot.json"


def load_previous(snapshot_file: str = DEFAULT_SNAPSHOT) -> dict:
    """載入上次快照"""
    if os.path.exists(snapshot_file):
        try:
            with open(snapshot_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_snapshot(appstore_data: dict, gplay_data: dict,
                  snapshot_file: str = DEFAULT_SNAPSHOT):
    """儲存本次快照"""
    snapshot = {
        "date": datetime.now().strftime("%Y/%m/%d"),
        "appstore": {},
        "gplay": {},
    }
    for country, charts in appstore_data.items():
        snapshot["appstore"][country] = {}
        for chart, apps in charts.items():
            snapshot["appstore"][country][chart] = [
                {"app_id": a["app_id"], "name": a["name"], "rank": a["rank"]}
                for a in apps
            ]
    for country, charts in gplay_data.items():
        snapshot["gplay"][country] = {}
        for chart, apps in charts.items():
            snapshot["gplay"][country][chart] = [
                {"app_id": a["app_id"], "name": a["name"], "rank": a["rank"]}
                for a in apps
            ]
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  💾 排名快照已儲存：{snapshot_file}")


def add_rank_changes(appstore_data: dict, gplay_data: dict, previous: dict):
    """把排名變化寫入 appstore_data / gplay_data"""
    prev_as = previous.get("appstore", {})
    prev_gp = previous.get("gplay", {})

    for country, charts in appstore_data.items():
        for chart, apps in charts.items():
            prev_map = {
                a["app_id"]: a["rank"]
                for a in prev_as.get(country, {}).get(chart, [])
            }
            for app in apps:
                prev_rank = prev_map.get(app["app_id"])
                app["rank_change"] = (prev_rank - app["rank"]) if prev_rank else None

    for country, charts in gplay_data.items():
        for chart, apps in charts.items():
            prev_map = {
                a["app_id"]: a["rank"]
                for a in prev_gp.get(country, {}).get(chart, [])
            }
            for app in apps:
                prev_rank = prev_map.get(app["app_id"])
                app["rank_change"] = (prev_rank - app["rank"]) if prev_rank else None
