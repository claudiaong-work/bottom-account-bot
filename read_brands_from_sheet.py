import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")
SHEET_ID = "1POC6XDI1WEcSUEQG4rXgW5I2SkQwicduVJ9OY1wOW_4"
TAB_NAME = "Bottom"
BRAND_COL = 2  # column C "Akun"
FIRST_DATA_ROW = 3  # row 4 in sheet (0-indexed row 3)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def is_red_text(color):
    if not color:
        return False
    r = color.get("red", 0)
    g = color.get("green", 0)
    b = color.get("blue", 0)
    return r > 0.8 and g < 0.2 and b < 0.2


def fetch_bottom_brands():
    """Return list of brand codes from the Bottom tab, skipping red-text rows."""
    service = get_service()
    result = service.spreadsheets().get(
        spreadsheetId=SHEET_ID,
        ranges=[f"{TAB_NAME}!C4:C40"],
        includeGridData=True,
        fields="sheets(data(rowData(values(formattedValue,effectiveFormat(textFormat(foregroundColor))))))",
    ).execute()

    rows = result["sheets"][0]["data"][0].get("rowData", [])
    brands = []
    for row in rows:
        values = row.get("values", [])
        if not values:
            continue
        cell = values[0]
        code = cell.get("formattedValue", "").strip()
        if not code:
            continue
        fg = cell.get("effectiveFormat", {}).get("textFormat", {}).get("foregroundColor")
        if is_red_text(fg):
            continue
        if code == "HOL":
            continue
        brands.append(code)
    return brands


if __name__ == "__main__":
    brands = fetch_bottom_brands()
    print(f"Found {len(brands)} brands (excluded red-text):")
    for b in brands:
        print(f"  {b}")
