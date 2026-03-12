"""
主程式：抓取排行榜 → 比對排名變化 → 產生 HTML → 寄信/Slack
執行方式：
  python main.py            # 抓資料 + 寄 Email
  python main.py --preview  # 只產生 HTML，不寄信
  python main.py --slack    # 只產生 HTML + 發 Slack
  python main.py --preview --slack  # 產生 HTML + 發 Slack，不寄信
"""
import argparse
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from config import REGIONS
from fetchers.appstore   import fetch_all_regions as fetch_appstore
from fetchers.googleplay import fetch_all_regions as fetch_gplay
from email_template      import build_html, build_email_html, build_subject
from send_email          import send_email
from rank_tracker        import load_previous, save_snapshot, add_rank_changes
from fetch_release_notes import get_notable_games, enrich_with_notes
from ai_summary          import summarize_rank_changes


def main(preview_only: bool = False, send_slack: bool = False):
    print("=" * 55)
    print("🎮 遊戲排行榜週報  {}".format(datetime.now().strftime("%Y/%m/%d %H:%M")))
    print("=" * 55)

    # ── 1. 載入上次排名 ───────────────────────────────────
    previous = load_previous()
    if previous.get("date"):
        print("  📊 找到上次快照：{}".format(previous["date"]))
    else:
        print("  📊 無上次快照，本次為首次執行（不顯示排名變化）")

    # ── 2. 抓取資料 ───────────────────────────────────────
    print("\n📱 開始抓取 App Store 資料...")
    appstore_data = fetch_appstore(REGIONS)

    print("\n🤖 開始抓取 Google Play 資料...")
    gplay_data = fetch_gplay(REGIONS)

    # ── 3. 計算排名變化 ───────────────────────────────────
    if previous:
        print("\n📈 計算排名變化...")
        add_rank_changes(appstore_data, gplay_data, previous)

    # ── 4. 儲存本次快照 ───────────────────────────────────
    save_snapshot(appstore_data, gplay_data)

    # ── 5. 版更資訊 + AI 摘要 ────────────────────────────
    ai_summary = ""
    if not os.getenv("GEMINI_API_KEY"):
        print("\n  ⚠️  未設定 GEMINI_API_KEY，跳過 AI 摘要")
    elif not previous.get("date"):
        print("\n  ℹ️  無上次快照，AI 分析將從下次執行開始")
    else:
        print("\n🔍 抓取版更資訊...")
        notable = get_notable_games(appstore_data, gplay_data, min_change=3)
        print(f"   找到 {len(notable)} 個值得關注的遊戲")
        if notable:
            notable = enrich_with_notes(notable, REGIONS)
            print("\n🤖 AI 分析排名變動原因...")
            ai_summary = summarize_rank_changes(notable)
            if ai_summary:
                print("\n--- AI 摘要 ---")
                print(ai_summary)

    # ── 6. 產生 HTML ──────────────────────────────────────
    print("\n🖼️  產生 HTML 報告...")
    html_preview = build_html(appstore_data, gplay_data)
    report_url   = os.getenv("REPORT_URL", "")
    html_email   = build_email_html(appstore_data, gplay_data,
                                    report_url=report_url,
                                    ai_summary=ai_summary)
    subject      = build_subject()

    preview_path = Path("preview_report.html")
    preview_path.write_text(html_preview, encoding="utf-8")
    print("   互動預覽：{}".format(preview_path.resolve()))

    email_path = Path("preview_email.html")
    email_path.write_text(html_email, encoding="utf-8")
    print("   Email版本：{}".format(email_path.resolve()))

    # ── 7. 發送 Slack ─────────────────────────────────────
    if send_slack:
        print("\n📨 發送 Slack 通知...")
        from slack_notify import build_slack_message, send_to_slack
        blocks = build_slack_message(appstore_data, gplay_data, ai_summary=ai_summary)
        send_to_slack(blocks)

    if preview_only:
        print("\n✅ --preview 模式：僅產生 HTML，不寄信。")
        return

    # ── 8. 寄信 ───────────────────────────────────────────
    print("\n📧 寄送郵件...")
    send_email(subject=subject, html_body=html_email)

    print("\n🎉 完成！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="遊戲排行榜週報自動化")
    parser.add_argument("--preview", action="store_true", help="只產生 HTML，不寄信")
    parser.add_argument("--slack",   action="store_true", help="發送 Slack 通知")
    args = parser.parse_args()
    main(preview_only=args.preview, send_slack=args.slack)
