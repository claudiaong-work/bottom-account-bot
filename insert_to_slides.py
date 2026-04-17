import os
import sys
import time
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import SLIDES_ID, MEETING_SLIDES_ID

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
CREDS_FILE = os.path.join(BASE_DIR, "credentials.json")

TEMPLATE_SLIDE_ID = "g3d6e96f1cc9_0_0"
TEMPLATE_TITLE_ID = "g3d6e96f1cc9_0_1"
TEMPLATE_SUBTITLE_ID = "g3d6e96f1cc9_0_2"
TEMPLATE_LOGO_ID = "g3d6e96f1cc9_0_3"
TEMPLATE_RECT_ID = "g3d6e96f1cc9_0_4"


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                print(f"ERROR: {CREDS_FILE} not found!")
                print("Please download OAuth credentials from Google Cloud Console.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds


def upload_image_to_drive(drive_service, image_path):
    filename = os.path.basename(image_path)
    file_metadata = {"name": filename}
    media = MediaFileUpload(image_path, mimetype="image/png")
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
    ).execute()
    file_id = file.get("id")

    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    time.sleep(3)

    return f"https://lh3.googleusercontent.com/d/{file_id}=w2000"


def delete_existing_brand_slides(slides_service, brand_akun):
    presentation = slides_service.presentations().get(
        presentationId=SLIDES_ID
    ).execute()

    delete_requests = []
    for slide in presentation.get("slides", []):
        slide_id = slide.get("objectId")
        if slide_id == TEMPLATE_SLIDE_ID:
            continue
        for element in slide.get("pageElements", []):
            shape = element.get("shape", {})
            placeholder = shape.get("placeholder", {})
            if placeholder.get("type") == "TITLE":
                text = shape.get("text", {})
                for t in text.get("textElements", []):
                    run = t.get("textRun", {})
                    content = run.get("content", "").strip()
                    if content == brand_akun or content.startswith(f"{brand_akun} -"):
                        delete_requests.append({"deleteObject": {"objectId": slide_id}})
                        break

    if delete_requests:
        print(f"  Deleting {len(delete_requests)} existing slide(s) for {brand_akun}...")
        slides_service.presentations().batchUpdate(
            presentationId=SLIDES_ID,
            body={"requests": delete_requests},
        ).execute()


def add_brand_slide(slides_service, drive_service, brand_akun, screenshots):
    print(f"  Uploading screenshots to Drive...")
    img_urls = [upload_image_to_drive(drive_service, s) for s in screenshots]

    labels = ["SHO ROAS 1 Bulan Terakhir", "SHO ROAS 3 Bulan Terakhir"]

    safe_name = brand_akun.replace(".", "_")
    for idx, (url, label) in enumerate(zip(img_urls, labels)):
        rand = os.urandom(4).hex()
        new_slide_id = f"slide_{safe_name}_{idx}_{rand}"
        new_title_id = f"title_{safe_name}_{idx}_{rand}"
        new_subtitle_id = f"sub_{safe_name}_{idx}_{rand}"
        new_logo_id = f"logo_{safe_name}_{idx}_{rand}"
        new_rect_id = f"rect_{safe_name}_{idx}_{rand}"
        img_id = f"img_{safe_name}_{idx}_{rand}"

        dup_requests = [{
            "duplicateObject": {
                "objectId": TEMPLATE_SLIDE_ID,
                "objectIds": {
                    TEMPLATE_SLIDE_ID: new_slide_id,
                    TEMPLATE_TITLE_ID: new_title_id,
                    TEMPLATE_SUBTITLE_ID: new_subtitle_id,
                    TEMPLATE_LOGO_ID: new_logo_id,
                    TEMPLATE_RECT_ID: new_rect_id,
                },
            }
        }]
        slides_service.presentations().batchUpdate(
            presentationId=SLIDES_ID,
            body={"requests": dup_requests},
        ).execute()

        update_requests = [
            {
                "deleteText": {
                    "objectId": new_title_id,
                    "textRange": {"type": "ALL"},
                }
            },
            {
                "insertText": {
                    "objectId": new_title_id,
                    "text": brand_akun,
                }
            },
            {
                "deleteText": {
                    "objectId": new_subtitle_id,
                    "textRange": {"type": "ALL"},
                }
            },
            {
                "insertText": {
                    "objectId": new_subtitle_id,
                    "text": label,
                }
            },
            {
                "createImage": {
                    "objectId": img_id,
                    "url": url,
                    "elementProperties": {
                        "pageObjectId": new_slide_id,
                        "size": {
                            "width": {"magnitude": 8500000, "unit": "EMU"},
                            "height": {"magnitude": 3600000, "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1, "scaleY": 1,
                            "translateX": 322000,
                            "translateY": 1100000,
                            "unit": "EMU",
                        },
                    },
                }
            },
        ]
        slides_service.presentations().batchUpdate(
            presentationId=SLIDES_ID,
            body={"requests": update_requests},
        ).execute()

    print(f"  Added 2 slides for {brand_akun}")


def find_sho_roas_slides(slides_service, pres_id):
    """Find the first pair of ROAS slides (Shopee) for each brand in the meeting deck."""
    pres = slides_service.presentations().get(presentationId=pres_id).execute()
    brand_slides = {}  # {brand: {"1bulan": (slide_id, img_element_id), "3bulan": ...}}

    for slide in pres.get("slides", []):
        slide_id = slide.get("objectId")
        texts = []
        brand = None
        screenshot_id = None

        for el in slide.get("pageElements", []):
            if el.get("image"):
                transform = el.get("transform", {})
                ty = transform.get("translateY", 0)
                if ty > 500000:
                    screenshot_id = el["objectId"]
            shape = el.get("shape", {})
            for t in shape.get("text", {}).get("textElements", []):
                c = t.get("textRun", {}).get("content", "").strip()
                if c:
                    texts.append(c)

        has_roas = any("ROAS" in t and "Bulan" in t for t in texts)
        if not has_roas:
            continue

        for t in texts:
            if "ROAS" not in t and "Bulan" not in t and len(t) <= 10:
                brand = t
                break

        if not brand or not screenshot_id:
            continue

        is_1bulan = any("1 Bulan" in t for t in texts)
        key = "1bulan" if is_1bulan else "3bulan"

        if brand not in brand_slides:
            brand_slides[brand] = {}
        if key not in brand_slides[brand]:
            brand_slides[brand][key] = (slide_id, screenshot_id)

    return brand_slides


def replace_meeting_screenshots(slides_service, drive_service, brand_akun, screenshots):
    """Replace ad screenshots in the meeting presentation."""
    roas_map = find_sho_roas_slides(slides_service, MEETING_SLIDES_ID)

    if brand_akun not in roas_map:
        print(f"  No ROAS slides found for {brand_akun} in meeting deck, skipping")
        return

    brand_data = roas_map[brand_akun]
    print(f"  Uploading screenshots to Drive...")
    filters = [("1bulan", screenshots[0]), ("3bulan", screenshots[1])]

    for key, img_path in filters:
        if key not in brand_data:
            print(f"  No {key} ROAS slide for {brand_akun}, skipping")
            continue

        slide_id, old_img_id = brand_data[key]
        img_url = upload_image_to_drive(drive_service, img_path)
        safe_name = brand_akun.replace(".", "_")
        new_img_id = f"meeting_img_{safe_name}_{key}_{os.urandom(4).hex()}"

        # Get old image position/size to match
        pres = slides_service.presentations().get(presentationId=MEETING_SLIDES_ID).execute()
        old_size = None
        old_transform = None
        for slide in pres.get("slides", []):
            if slide["objectId"] != slide_id:
                continue
            for el in slide.get("pageElements", []):
                if el["objectId"] == old_img_id:
                    old_size = el["size"]
                    old_transform = el["transform"]
                    break

        requests = [
            {"deleteObject": {"objectId": old_img_id}},
            {
                "createImage": {
                    "objectId": new_img_id,
                    "url": img_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": old_size,
                        "transform": old_transform,
                    },
                }
            },
        ]
        slides_service.presentations().batchUpdate(
            presentationId=MEETING_SLIDES_ID,
            body={"requests": requests},
        ).execute()
        label = "1 Bulan" if key == "1bulan" else "3 Bulan"
        print(f"  Replaced {label} screenshot for {brand_akun}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 insert_to_slides.py BRAND1 BRAND2 ...")
        sys.exit(1)

    brand_list = [b.strip().upper() for b in sys.argv[1:]]

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    screenshots_dir = os.path.join(BASE_DIR, "screenshots")

    for akun in brand_list:
        files = sorted([
            f for f in os.listdir(screenshots_dir)
            if f.startswith(f"{akun}_")
        ])

        one_bulan = next((f for f in reversed(files) if "1bulan" in f), None)
        three_bulan = next((f for f in reversed(files) if "3bulan" in f), None)

        if not one_bulan or not three_bulan:
            print(f"Missing screenshots for {akun}, skipping")
            continue

        screenshots = [
            os.path.join(screenshots_dir, one_bulan),
            os.path.join(screenshots_dir, three_bulan),
        ]
        print(f"\n{akun}: {one_bulan}, {three_bulan}")
        delete_existing_brand_slides(slides_service, akun)
        add_brand_slide(slides_service, drive_service, akun, screenshots)
        print(f"  Replacing in meeting deck...")
        replace_meeting_screenshots(slides_service, drive_service, akun, screenshots)

    print("\nDone! Check your Google Slides.")


if __name__ == "__main__":
    main()
