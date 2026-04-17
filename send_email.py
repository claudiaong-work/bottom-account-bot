import os
import pickle
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import EMAIL_RECIPIENTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token_gmail.pickle")
CREDS_FILE = os.path.join(BASE_DIR, "credentials.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


def send_email(subject, body):
    service = get_gmail_service()
    message = MIMEText(body)
    message["to"] = ", ".join(EMAIL_RECIPIENTS)
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    print(f"  Email sent to {', '.join(EMAIL_RECIPIENTS)}")


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
