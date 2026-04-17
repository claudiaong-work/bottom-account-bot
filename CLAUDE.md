# Bottom Account Automation

Weekly Thursday automation: screenshot Shopee ads performance for underperforming brands and insert the images into Google Slides, one brand per pair of slides.

## Context

"Bottom Account" is a weekly meeting where underperforming brand ads are reviewed. The manual flow is highly repetitive — 51 shops on `ahacommerce.biteam`, only a subset flagged "bottom" each week. The user handles CAPTCHA/OTP at login; the bot handles the rest via PyAutoGUI on the default browser (macOS, 2560x1664 Retina → pyautogui uses 1710x1112 logical coords, screencapture returns 2x).

## Files

- `shopee_ads_screenshot.py` — PyAutoGUI bot. Drives the browser, takes cropped screenshots, saves to `screenshots/`.
- `insert_to_slides.py` — Duplicates a template slide, fills brand name + subtitle + screenshot image. Deletes prior slides for the same brand first.
- `read_brands_from_sheet.py` — Fetches brand list from Google Sheet "Bottom" tab via service account. Skips red-text rows (belum sebulan) and HOL (Lazada-only).
- `config.py` — URLs, Slides ID, timing constants.
- `brands.csv` — Maps brand `akun` → `shopee_username`. Source of truth for brand lookups.
- `capture_ref_images.py` / `ref_images/` — Reference images for visual debugging / calibration aids.
- `mouse_tracker.py` — Helper to print live mouse position while calibrating.
- `credentials.json` / `token.pickle` — Google OAuth for Slides/Drive (gitignored).
- `service_account.json` — Service account key for Sheets read (gitignored).

## Usage

```
python3 shopee_ads_screenshot.py                   # auto-fetch brands from Google Sheet
python3 shopee_ads_screenshot.py BRAND1 BRAND2 ... # manual override
python3 shopee_ads_screenshot.py --calibrate       # re-record click coords
python3 insert_to_slides.py BRAND1 BRAND2 ...      # insert latest screenshots to Slides
```

Brand args are uppercased and must exist in `brands.csv`. Screenshots land in `screenshots/{AKUN}_{1bulan|3bulan}_{YYYYMMDD}.png`.

## Flow (per brand)

1. On "Pilih Toko" page: switch search filter to "Username Toko", type username, Enter.
2. Click first "Detail" link.
3. Navigate directly to `https://seller.shopee.co.id/portal/marketing/pas/index` via Cmd+L (sidebar click was flaky).
4. Popup handling: checks if dimmed overlay present → tries Escape → only shows macOS dialog if popup persists after 2 attempts. No notification if no popup.
5. Scroll down to "Performa Seluruh Iklan".
6. Smart metric card detection: scans all 8 metric cards for colored top border (selected state). Deselects everything except **Biaya Iklan + ROAS**. Only clicks cards that need toggling.
7. For each of `1 bulan terakhir` and `3 bulan terakhir`: open date filter, pick option, screencapture, crop to the Performa region, save.
8. Scroll to top → Account menu → "Ganti toko" to return to Pilih Toko for the next brand.

## Google Sheet integration

- **Sheet:** `1POC6XDI1WEcSUEQG4rXgW5I2SkQwicduVJ9OY1wOW_4` tab **"Bottom"**
- Auto-updates every Thursday. Brand codes in column C ("Akun"), starting row 4.
- **Exclusions:** red-text rows (belum sebulan), HOL (Lazada-only).
- **Auth:** service account `bottom-ads-bot-shopee@fbi-dev-484410.iam.gserviceaccount.com`.

## Slides insertion

Uses a template slide (slide 1 in the presentation) that is duplicated per brand. Template contains:
- **Title placeholder** (top-left): brand name with hyperlink
- **Subtitle text box** (center-top): "ROAS 1 Bulan Terakhir" / "ROAS 3 Bulan Terakhir", Nunito 22pt bold
- **Logo image** (top-right): AHA Commerce logo
- **Background image**: includes blue bar at bottom

Template IDs are hardcoded in `insert_to_slides.py`. If the template slide is recreated, update `TEMPLATE_SLIDE_ID`, `TEMPLATE_TITLE_ID`, `TEMPLATE_SUBTITLE_ID`, `TEMPLATE_LOGO_ID`, `TEMPLATE_RECT_ID`.

Existing slides for a brand are deleted before insertion (matched by title text = brand code). Images uploaded to Drive with `anyone/reader` permission. `insert_to_slides.py` always picks the latest screenshot files (sorted by date suffix).

## Coordinates

All click targets are hardcoded at the top of `shopee_ads_screenshot.py` and assume a 1710x1112 logical viewport. If the browser window size, zoom, or Shopee's layout changes, run `--calibrate` to re-record them. Screenshot crop uses `CROP_TOP_LEFT` and `CROP_BOTTOM_RIGHT` multiplied by 2 for Retina.

## Metric card positions

8 cards in 2 rows (y=564, y=666), 4 per row (x=442, 789, 1135, 1482):
- Row 1: Iklan Dilihat, Produk Terjual, Jumlah Klik, Penjualan dari Iklan
- Row 2: Persentase Klik, Biaya Iklan, Pesanan, ROAS

Detection: scans a strip of pixels above the card center (y-35 to y-25) for colored top border. Colored = selected.

## Gotchas

- `pyautogui.FAILSAFE = True` — slam the mouse to a corner to abort.
- CAPTCHA/OTP at login is manual; start the script only after you're logged in and on Pilih Toko.
- Drive upload sleeps 3s before returning the URL so Slides' image fetcher doesn't 404 on a fresh file.
- Sidebar "Iklan Shopee" click was replaced with direct URL navigation because sidebar positions shift per shop.
- "Ganti toko" via direct URL 404s — must use the account dropdown (scroll to top first).
- Script runs non-interactively (no stdin) — use `osascript display dialog` for user prompts, not `input()`.
