"""
主程式：抓取排行榜 → 比對排名變化 → 產生 HTML → 寄信
執行方式：python main.py
可加 --preview 只產生 HTML 預覽，不寄信
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


def main(preview_only: bool = False):
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

    # ── 5. 產生 HTML ──────────────────────────────────────
    print("\n🖼️  產生 HTML 報告...")
    html_preview = build_html(appstore_data, gplay_data)
    report_url   = os.getenv("REPORT_URL", "")
    html_email   = build_email_html(appstore_data, gplay_data)
    subject      = build_subject()

    # 瀏覽器互動版
    preview_path = Path("preview_report.html")
    preview_path.write_text(html_preview, encoding="utf-8")
    print("   互動預覽：{}".format(preview_path.resolve()))

    # Email 靜態版
    email_path = Path("preview_email.html")
    email_path.write_text(html_email, encoding="utf-8")
    print("   Email版本：{}".format(email_path.resolve()))

    if preview_only:
        print("\n✅ --preview 模式：僅產生 HTML，不寄信。")
        print("   用瀏覽器開啟 preview_report.html 確認互動版")
        print("   用瀏覽器開啟 preview_email.html 確認 Email 版")
        return

    # ── 6. 寄信 ───────────────────────────────────────────
    print("\n📧 寄送郵件...")
    send_email(subject=subject, html_body=html_email)

    print("\n🎉 完成！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="遊戲排行榜週報自動化")
    parser.add_argument("--preview", action="store_true", help="只產生 HTML，不寄信")
    args = parser.parse_args()
    main(preview_only=args.preview)
