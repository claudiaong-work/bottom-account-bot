import os
import base64
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import EMAIL_SENDER, EMAIL_SENDER_NAME, EMAIL_RECIPIENTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    # Domain-wide delegation: the service account impersonates EMAIL_SENDER.
    # Requires the SA's client ID to be authorized for gmail.send in the
    # Workspace Admin Console (Security > API Controls > Domain-wide Delegation).
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    ).with_subject(EMAIL_SENDER)
    return build("gmail", "v1", credentials=creds)


def send_email(subject, body):
    service = get_gmail_service()
    message = MIMEText(body)
    message["from"] = formataddr((str(Header(EMAIL_SENDER_NAME, "utf-8")), EMAIL_SENDER))
    message["to"] = ", ".join(EMAIL_RECIPIENTS)
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    print(f"  Email sent from {EMAIL_SENDER} to {', '.join(EMAIL_RECIPIENTS)}")


def send_login_reminder(brands):
    subject = "[Bottom Account Bot] Please login to Shopee Seller Centre"
    body = f"""Hi team,

The Bottom Account screenshot bot is ready to run.

Brands to process this week ({len(brands)}):
{', '.join(brands)}

Please login to Shopee Seller Centre (ahacommerce.biteam) and navigate to the "Pilih Toko" page.

Thanks,
Bottom Account Bot"""
    send_email(subject, body)


def send_success_report(results):
    success = [b for b, paths in results.items() if paths]
    failed = [b for b, paths in results.items() if not paths]

    subject = f"[Bottom Account Bot] Done - {len(success)}/{len(results)} brands completed"
    body = f"""Hi team,

The Bottom Account screenshot bot has finished.

Completed ({len(success)}):
{', '.join(success) if success else 'None'}
"""
    if failed:
        body += f"""
Failed ({len(failed)}):
{', '.join(failed)}
"""
    body += """
Screenshots have been inserted into Google Slides.

Thanks,
Bottom Account Bot"""
    send_email(subject, body)


if __name__ == "__main__":
    send_login_reminder(["BR", "GS", "SKF-M"])
