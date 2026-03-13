import requests
import re
import time
from config import TOP_N

CHARTS = {
    "top-free": "免費排行",
    "top-paid": "付費排行",
}
LOOKUP_URL = "https://itunes.apple.com/lookup"
HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _get_ids_from_page(country, chart, retries=3):
    url = "https://apps.apple.com/{}/iphone/charts/6014".format(country)
    for attempt in range(retries):
        try:
            r = requests.get(url, params={"chart": chart}, headers=HEADERS, timeout=20)
            if r.status_code == 429:
                wait = 10 * (attempt + 1)
                print("    [429] Too Many Requests，等待 {}s 後重試...".format(wait))
                time.sleep(wait)
                continue
            r.raise_for_status()
            ids = re.findall(r'/app/[^/"]+/id(\d{8,12})', r.text)
            seen, unique = set(), []
            for i in ids:
                if i not in seen:
                    seen.add(i)
                    unique.append(i)
            return unique
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                raise e
    return []


def _lookup(app_ids, country):
    try:
        r = requests.get(
            LOOKUP_URL,
            params={"id": ",".join(app_ids), "country": country, "entity": "software"},
            timeout=20
        )
        r.raise_for_status()
        return {str(a["trackId"]): a for a in r.json().get("results", []) if "trackId" in a}
    except Exception as e:
        print("    lookup error: {}".format(e))
        return {}


def fetch_chart(country, chart, limit=TOP_N):
    try:
        ids = _get_ids_from_page(country, chart)
        print("    [{}/{}] 頁面抓到 {} 個 ID".format(country, chart, len(ids)))
        if not ids:
            return []
        detail_map = _lookup(ids[:limit], country)
        result = []
        for i, app_id in enumerate(ids[:limit]):
            d = detail_map.get(app_id, {})
            score = d.get("averageUserRating")
            result.append({
                "rank":      i + 1,
                "name":      d.get("trackName", app_id),
                "developer": d.get("artistName", ""),
                "icon":      d.get("artworkUrl100", ""),
                "app_id":    app_id,
                "url":       "https://apps.apple.com/{}/app/id{}".format(country, app_id),
                "genre":     d.get("primaryGenreName", "Games"),
                "score":     round(score, 1) if score else 0,
            })
        return result
    except Exception as e:
        print("  WARNING App Store [{}/{}]: {}".format(country, chart, e))
        return []


def fetch_all_regions(regions):
    results = {}
    for region in regions:
        c = region["appstore"]
        print("  App Store {} ({})".format(region["name"], c))
        results[c] = {}
        for k in CHARTS:
            results[c][k] = fetch_chart(c, k)
            time.sleep(2.0)  # 增加間隔避免 rate limit
    return results
