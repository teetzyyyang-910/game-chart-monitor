"""
每日 Slack 通知：極簡格式排名變動
執行方式：python slack_notify.py
"""
import os
import json
from dotenv import load_dotenv
load_dotenv()
import requests
from datetime import datetime
from config import REGIONS
from fetchers.appstore   import fetch_all_regions as fetch_appstore
from fetchers.googleplay import fetch_all_regions as fetch_gplay
from rank_tracker        import load_previous, save_snapshot, add_rank_changes

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#game-charts")

# 只追蹤重點地區（可自行調整）
FOCUS_REGIONS = ["tw", "us", "jp"]

# 有變化才通知（變動幅度門檻）
CHANGE_THRESHOLD = 1


def build_slack_message(appstore_data: dict, gplay_data: dict) -> list[dict]:
    """產生 Slack Block Kit 格式訊息"""
    today = datetime.now().strftime("%Y/%m/%d")
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🎮 每日遊戲排行榜變動 {}".format(today)}
        },
        {"type": "divider"}
    ]

    region_map = {r["appstore"]: r["name"] for r in REGIONS}
    has_any_change = False

    for platform_label, data, chart_map in [
        ("🍎 App Store", appstore_data, {"top-free": "免費榜", "top-paid": "付費榜"}),
        ("🤖 Google Play", gplay_data, {"topselling_free": "免費榜", "topselling_grossing": "暢銷榜"}),
    ]:
        platform_lines = []

        for country in FOCUS_REGIONS:
            region_name = region_map.get(country, country)
            country_data = data.get(country, {})

            for chart_key, chart_label in chart_map.items():
                apps = country_data.get(chart_key, [])
                if not apps:
                    continue

                changes = []
                new_entries = []
                big_drops = []

                for app in apps[:10]:  # 只看 Top 10
                    change = app.get("rank_change")
                    name = app.get("name", "")
                    rank = app.get("rank", 0)

                    if change is None:
                        new_entries.append("*{}* 🆕 新進 #{}".format(name, rank))
                    elif change >= 3:
                        changes.append("*{}* ▲{} → #{}".format(name, change, rank))
                        has_any_change = True
                    elif change <= -3:
                        big_drops.append("*{}* ▼{} → #{}".format(name, abs(change), rank))
                        has_any_change = True

                notable = changes + big_drops + new_entries[:2]
                if notable:
                    platform_lines.append(
                        "*{} {}* {}\n{}".format(
                            region_name, chart_label,
                            "",
                            "\n".join("  • " + l for l in notable[:4])
                        )
                    )

        if platform_lines:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*{}*\n\n{}".format(platform_label, "\n\n".join(platform_lines))
                }
            })
            blocks.append({"type": "divider"})

    # 如果沒有顯著變化
    if not has_any_change:
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🎮 每日遊戲排行榜變動 {}".format(today)}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "今日排名無顯著變動 ✨\n（Top 10 內無 3 名以上的移動）"
                }
            }
        ]

    return blocks


def send_to_slack(blocks: list[dict]):
    if not SLACK_WEBHOOK:
        print("❌ 未設定 SLACK_WEBHOOK_URL，請在 .env 或 GitHub Secrets 設定")
        # 本機測試時印出訊息預覽
        print("\n📱 Slack 訊息預覽：")
        for b in blocks:
            if b.get("type") == "header":
                print("=" * 40)
                print(b["text"]["text"])
                print("=" * 40)
            elif b.get("type") == "section":
                print(b["text"]["text"])
                print()
        return

    payload = {
        "channel": SLACK_CHANNEL,
        "blocks": blocks,
        "text": "每日遊戲排行榜變動通知",  # fallback text
    }
    resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=15)
    if resp.status_code == 200:
        print("✅ Slack 通知已發送到 {}".format(SLACK_CHANNEL))
    else:
        print("❌ Slack 發送失敗: {} {}".format(resp.status_code, resp.text))


def main():
    print("📊 載入上次排名...")
    previous = load_previous()

    print("📱 抓取 App Store...")
    appstore_data = fetch_appstore(REGIONS)

    print("🤖 抓取 Google Play...")
    gplay_data = fetch_gplay(REGIONS)

    print("📈 計算排名變化...")
    if previous:
        add_rank_changes(appstore_data, gplay_data, previous)

    print("💾 儲存快照...")
    save_snapshot(appstore_data, gplay_data)

    print("📨 發送 Slack 通知...")
    blocks = build_slack_message(appstore_data, gplay_data)
    send_to_slack(blocks)


if __name__ == "__main__":
    main()
