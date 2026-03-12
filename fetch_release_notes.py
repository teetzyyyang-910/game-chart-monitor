"""
抓取遊戲版更資訊
App Store: iTunes Lookup API
Google Play: google_play_scraper
"""
import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_appstore_notes(app_id: str, country: str = "us") -> dict:
    """從 iTunes API 抓版更資訊"""
    try:
        url = f"https://itunes.apple.com/lookup?id={app_id}&country={country}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        if data.get("resultCount", 0) > 0:
            result = data["results"][0]
            return {
                "version":       result.get("version", ""),
                "release_notes": result.get("releaseNotes", ""),
                "release_date":  result.get("currentVersionReleaseDate", "")[:10],
            }
    except Exception as e:
        print(f"    iTunes lookup failed ({app_id}): {e}")
    return {}


def fetch_gplay_notes(app_id: str, lang: str = "en", country: str = "us") -> dict:
    """從 google_play_scraper 抓版更資訊"""
    try:
        from google_play_scraper.features.app import app as gp_app
        d = gp_app(app_id, lang=lang, country=country)
        return {
            "version":       d.get("version", ""),
            "release_notes": d.get("recentChangesHTML") or d.get("recent_changes") or "",
            "release_date":  (d.get("updated") or ""),
        }
    except Exception as e:
        print(f"    GP scraper failed ({app_id}): {e}")
    return {}


def get_notable_games(appstore_data: dict, gplay_data: dict, min_change: int = 3) -> list:
    """
    找出值得關注的遊戲：
    - 新進 Top 10（rank_change is None and rank <= 10）
    - 排名變動 >= min_change 且在 Top 10 內
    回傳 list of dict
    """
    notable = []
    seen = set()  # 避免同一遊戲重複

    for country, charts in appstore_data.items():
        for chart_key, apps in charts.items():
            for app in apps:
                rank   = app.get("rank", 99)
                change = app.get("rank_change")
                name   = app.get("name", "")
                app_id = app.get("app_id", "")

                if rank > 10:
                    continue

                # 新進榜只在 rank <= 3 才算，避免無快照時全部觸發
                is_new = (change is None and rank <= 3)
                is_moved = (change is not None and abs(change) >= min_change)
                if (is_new or is_moved) and app_id and app_id not in seen:
                    seen.add(app_id)
                    notable.append({
                        "platform":   "appstore",
                        "name":       name,
                        "app_id":     app_id,
                        "country":    country,
                        "rank":       rank,
                        "rank_change": change,
                        "chart":      chart_key,
                    })

    for country, charts in gplay_data.items():
        for chart_key, apps in charts.items():
            for app in apps:
                rank   = app.get("rank", 99)
                change = app.get("rank_change")
                name   = app.get("name", "")
                app_id = app.get("app_id", "")

                if rank > 10:
                    continue

                is_new = (change is None and rank <= 3)
                is_moved = (change is not None and abs(change) >= min_change)
                if (is_new or is_moved) and app_id and app_id not in seen:
                    seen.add(app_id)
                    notable.append({
                        "platform":   "gplay",
                        "name":       name,
                        "app_id":     app_id,
                        "country":    country,
                        "rank":       rank,
                        "rank_change": change,
                        "chart":      chart_key,
                    })

    return notable[:15]  # 最多分析 15 個，避免 API 費用過高


def enrich_with_notes(notable_games: list, regions: list) -> list:
    """為每個遊戲補上版更資訊"""
    # 建立 country -> lang 對照
    lang_map = {r["appstore"]: r["lang"] for r in regions}

    for game in notable_games:
        country = game["country"]
        lang    = lang_map.get(country, "en")

        if game["platform"] == "appstore":
            notes = fetch_appstore_notes(game["app_id"], country=country)
        else:
            notes = fetch_gplay_notes(game["app_id"], lang=lang, country=country)

        game["version"]       = notes.get("version", "")
        game["release_notes"] = notes.get("release_notes", "")
        game["release_date"]  = notes.get("release_date", "")
        time.sleep(0.3)

    return notable_games
