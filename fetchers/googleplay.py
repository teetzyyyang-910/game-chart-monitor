"""
Google Play 遊戲排行榜
使用 Playwright 瀏覽器自動化確保地區資料正確
"""
import time
import re
import asyncio
from config import TOP_N

try:
    from google_play_scraper.features.app import app as gp_detail
    HAS_DETAIL = True
except ImportError:
    HAS_DETAIL = False

CHARTS = {
    "topselling_free":     "免費遊戲榜",
    "topselling_grossing": "暢銷遊戲榜",
}

GROSSING_TEXTS = [
    "创收最高", "創收最高",          # 中文（台灣/香港）
    "Top grossing",                  # 英文（新加坡/馬來西亞/美國/英國/印度）
    "Les plus rentables",            # 法文
    "Erfolgreichste",                # 德文
    "Mais rentáveis",                # 葡文（巴西）
    "売上トップ",                     # 日文
    "최고 매출",                      # 韓文
]

LANG_LOCALE = {
    "tw": "zh-TW", "hk": "zh-HK", "sg": "en-SG",
    "my": "en-MY", "us": "en-US", "gb": "en-GB",
    "fr": "fr-FR", "de": "de-DE", "br": "pt-BR",
    "in": "en-US",  # en-IN 有時載入失敗，改用 en-US
    "jp": "ja-JP",
    "kr": "ko-KR",
}

EXCLUDE_PREFIXES = (
    "com.google.", "com.android.", "com.samsung.",
    "com.facebook.", "com.instagram.", "com.whatsapp.",
    "com.netflix.", "com.microsoft.", "com.amazon.",
)
EXCLUDE_IDS = {"com.google.android.gms", "com.android.vending"}


async def _fetch_ids_playwright(country, lang, chart_id, limit):
    from playwright.async_api import async_playwright

    locale = LANG_LOCALE.get(country, "en-US")
    url = "https://play.google.com/store/games?device=phone&hl={}&gl={}".format(lang, country)
    is_grossing = (chart_id == "topselling_grossing")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale=locale, viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        if is_grossing:
            clicked = False

            # 方法一：get_by_text 精確匹配
            for text in GROSSING_TEXTS:
                try:
                    el = page.get_by_text(text, exact=True)
                    if await el.count() > 0:
                        await el.first.click()
                        clicked = True
                        print("    clicked by text:", text)
                        break
                except Exception:
                    pass

            # 方法二：找葉節點文字
            if not clicked:
                clicked_text = await page.evaluate('''() => {
                    const keywords = ["创收最高", "創收最高", "grossing", "rentables",
                                     "Erfolgreichste", "rentáveis", "売上トップ", "최고 매출"];
                    const all = Array.from(document.querySelectorAll("*"));
                    for (const el of all) {
                        if (el.children.length === 0) {
                            const t = el.textContent.trim();
                            if (keywords.some(k => t === k || t.toLowerCase() === k.toLowerCase())) {
                                el.click();
                                return t;
                            }
                        }
                    }
                    return null;
                }''')
                if clicked_text:
                    clicked = True
                    print("    clicked leaf node:", clicked_text)

            if not clicked:
                print("    WARNING: 無法點擊 grossing tab")

            # 等待頁面資料刷新
            try:
                await page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                await page.wait_for_timeout(2000)

        # 等待頁面第一個 app 連結真正改變（確認 tab 切換後 DOM 已更新）
        if is_grossing:
            try:
                # 先記錄現在的第一個 app ID
                first_id_before = await page.evaluate('''() => {
                    const links = document.querySelectorAll('a[href*="details?id="]');
                    for (const a of links) {
                        const m = a.href.match(/id=([\w.]+)/);
                        if (m && m[1].length > 8) return m[1];
                    }
                    return null;
                }''')

                # 等到第一個 app ID 改變，最多等 8 秒
                for _ in range(16):
                    await page.wait_for_timeout(500)
                    first_id_after = await page.evaluate('''() => {
                        const links = document.querySelectorAll('a[href*="details?id="]');
                        for (const a of links) {
                            const m = a.href.match(/id=([\w.]+)/);
                            if (m && m[1].length > 8) return m[1];
                        }
                        return null;
                    }''')
                    if first_id_after and first_id_after != first_id_before:
                        print("    DOM 已更新：{} → {}".format(first_id_before, first_id_after))
                        break
                else:
                    print("    WARNING: DOM 可能未更新，仍使用現有內容")
            except Exception as e:
                await page.wait_for_timeout(2000)

        # 精確抓取排行榜區域（用排名數字定位）
        links = await page.evaluate('''() => {
            const allEls = Array.from(document.querySelectorAll("*"));
            let rankEls = allEls.filter(el => {
                if (el.children.length > 0) return false;
                const t = el.textContent.trim();
                return /^([1-9]|1[0-5])$/.test(t);
            });

            if (rankEls.length < 3) {
                const all = Array.from(document.querySelectorAll('a[href*="details?id="]'));
                return all.slice(6).map(a => a.href);
            }

            let container = null;
            let el = rankEls[0];
            for (let i = 0; i < 8; i++) {
                el = el.parentElement;
                if (!el) break;
                const links = el.querySelectorAll('a[href*="details?id="]');
                if (links.length >= 5) {
                    container = el;
                    break;
                }
            }

            if (container) {
                return Array.from(container.querySelectorAll('a[href*="details?id="]'))
                    .map(a => a.href);
            }

            const minY = rankEls[0].getBoundingClientRect().top + window.scrollY - 20;
            const maxY = minY + 1200;
            return Array.from(document.querySelectorAll('a[href*="details?id="]'))
                .filter(a => {
                    const y = a.getBoundingClientRect().top + window.scrollY;
                    return y >= minY && y <= maxY;
                })
                .map(a => a.href);
        }''')

        await browser.close()

    seen, ids = set(), []
    for link in links:
        m = re.search(r'id=([\w.]+)', link)
        if m:
            aid = m.group(1)
            if (aid not in seen and aid not in EXCLUDE_IDS and len(aid) > 8
                    and not any(aid.startswith(p) for p in EXCLUDE_PREFIXES)):
                seen.add(aid)
                ids.append(aid)
    return ids[:limit * 2]


def _get_detail(app_id, lang, country):
    if not HAS_DETAIL:
        return None
    try:
        d = gp_detail(app_id, lang=lang, country=country)
        if len(d.get("title", "")) <= 1:
            return None
        return d
    except Exception:
        return None


def fetch_chart(country, lang, chart_id, limit=TOP_N):
    try:
        ids = asyncio.run(_fetch_ids_playwright(country, lang, chart_id, limit))
        print("    [{}/{}] 抓到 {} 個 ID: {}".format(country, chart_id, len(ids), ids[:3]))
        if not ids:
            return []
        results, rank = [], 1
        for app_id in ids:
            if rank > limit:
                break
            d = _get_detail(app_id, lang, country)
            if not d:
                continue
            results.append({
                "rank":      rank,
                "name":      d.get("title", app_id),
                "developer": d.get("developer", ""),
                "icon":      d.get("icon", ""),
                "app_id":    app_id,
                "url":       "https://play.google.com/store/apps/details?id={}&hl={}&gl={}".format(app_id, lang, country),
                "genre":     d.get("genre", ""),
                "score":     round(d.get("score") or 0, 1),
            })
            rank += 1
            time.sleep(0.3)
        return results
    except Exception as e:
        print("  WARNING Google Play [{}/{}]: {}".format(country, chart_id, e))
        return []


def fetch_all_regions(regions):
    results = {}
    for region in regions:
        c, lang = region["gplay"], region["lang"]
        print("  Google Play {} ({})".format(region["name"], c))
        results[c] = {}
        for k in CHARTS:
            results[c][k] = fetch_chart(c, lang, k)
            time.sleep(1.0)
    return results
