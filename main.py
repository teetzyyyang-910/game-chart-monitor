"""
主程式：抓取排行榜 → 產生 HTML → 寄信
執行方式：python main.py
可加 --preview 只產生 HTML 預覽，不寄信
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

from config import REGIONS
from fetchers.appstore  import fetch_all_regions as fetch_appstore
from fetchers.googleplay import fetch_all_regions as fetch_gplay
from email_template     import build_html, build_email_html, build_subject
from send_email         import send_email


def main(preview_only: bool = False):
    print("=" * 55)
    print(f"🎮 遊戲排行榜週報  {datetime.now().strftime('%Y/%m/%d %H:%M')}")
    print("=" * 55)

    # ── 1. 抓 App Store ──────────────────────────────────
    print("\n📱 開始抓取 App Store 資料...")
    appstore_data = fetch_appstore(REGIONS)

    # ── 2. 抓 Google Play ────────────────────────────────
    print("\n🤖 開始抓取 Google Play 資料...")
    gplay_data = fetch_gplay(REGIONS)

    # ── 3. 產生 HTML ─────────────────────────────────────
    print("\n🖼️  產生 HTML 報告...")
    html_preview = build_html(appstore_data, gplay_data)
    report_url   = os.getenv('REPORT_URL', '')
    html_email   = build_email_html(appstore_data, gplay_data, report_url=report_url)
    subject      = build_subject()

    # 瀏覽器互動版
    preview_path = Path("preview_report.html")
    preview_path.write_text(html_preview, encoding="utf-8")
    print(f"   互動預覽：{preview_path.resolve()}")

    # Email 靜態版
    email_path = Path("preview_email.html")
    email_path.write_text(html_email, encoding="utf-8")
    print(f"   Email版本：{email_path.resolve()}")

    if preview_only:
        print("\n✅ --preview 模式：僅產生 HTML，不寄信。")
        print(f"   用瀏覽器開啟 {preview_path} 確認排版。")
        return

    # ── 4. 寄信 ──────────────────────────────────────────
    print("\n📧 寄送郵件...")
    send_email(subject=subject, html_body=html_email)

    print("\n🎉 完成！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="遊戲排行榜週報自動化")
    parser.add_argument(
        "--preview", action="store_true",
        help="只產生 HTML 預覽，不寄信（測試用）"
    )
    args = parser.parse_args()
    main(preview_only=args.preview)
