"""
透過 Gmail SMTP 寄出 HTML 郵件
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER     = os.getenv("GMAIL_USER")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAILS = [e.strip() for e in os.getenv("RECIPIENT_EMAILS", "").split(",") if e.strip()]


def send_email(subject: str, html_body: str) -> None:
    if not GMAIL_USER or not GMAIL_APP_PASS:
        raise ValueError("請確認 .env 檔案中的 GMAIL_USER 和 GMAIL_APP_PASSWORD 已填寫！")
    if not RECIPIENT_EMAILS:
        raise ValueError("請在 .env 設定 RECIPIENT_EMAILS！")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = ", ".join(RECIPIENT_EMAILS)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAILS, msg.as_string())

    print("✅ 郵件已成功寄出！收件人：{}".format(", ".join(RECIPIENT_EMAILS)))
