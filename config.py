import os
from dotenv import load_dotenv

load_dotenv()

# ── 地區設定 ──────────────────────────────────────────────
REGIONS = [
    # 東南亞
    {"name": "🇸🇬 新加坡",   "appstore": "sg", "gplay": "sg", "lang": "en",  "group": "東南亞"},
    {"name": "🇲🇾 馬來西亞", "appstore": "my", "gplay": "my", "lang": "en",  "group": "東南亞"},
    # 東北亞
    {"name": "🇹🇼 台灣",     "appstore": "tw", "gplay": "tw", "lang": "zh",  "group": "東北亞"},
    {"name": "🇯🇵 日本",     "appstore": "jp", "gplay": "jp", "lang": "ja",  "group": "東北亞"},
    {"name": "🇰🇷 韓國",     "appstore": "kr", "gplay": "kr", "lang": "ko",  "group": "東北亞"},
    # 美洲
    {"name": "🇺🇸 美國",     "appstore": "us", "gplay": "us", "lang": "en",  "group": "美洲"},
    {"name": "🇧🇷 巴西",     "appstore": "br", "gplay": "br", "lang": "pt",  "group": "美洲"},
    # 歐洲
    {"name": "🇬🇧 英國",     "appstore": "gb", "gplay": "gb", "lang": "en",  "group": "歐洲"},
    # 亞洲
    {"name": "🇭🇰 香港",     "appstore": "hk", "gplay": "hk", "lang": "zh",  "group": "亞洲"},
    {"name": "🇮🇳 印度",     "appstore": "in", "gplay": "in", "lang": "en",  "group": "亞洲"},
]

TOP_N = int(os.getenv("TOP_N", 15))

# ── Azure / Graph API ─────────────────────────────────────
AZURE_CLIENT_ID     = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID     = os.getenv("AZURE_TENANT_ID")
SENDER_EMAIL        = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAILS    = [e.strip() for e in os.getenv("RECIPIENT_EMAILS", "").split(",") if e.strip()]
