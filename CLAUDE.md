# Bottom Account Automation

Weekly Thursday automation: screenshot Shopee ads performance for underperforming brands and insert the images into Google Slides, one brand per pair of slides.

## Context

"Bottom Account" is a weekly meeting where underperforming brand ads are reviewed. The manual flow is highly repetitive — 51 shops on `ahacommerce.biteam`, only a subset flagged "bottom" each week. The user handles CAPTCHA/OTP at login; the bot handles the rest via PyAutoGUI on the default browser (macOS, 2560x1664 Retina → pyautogui uses 1710x1112 logical coords, screencapture returns 2x).

## Files

- `shopee_ads_screenshot.py` — PyAutoGUI bot. Drives the browser, takes cropped screenshots, saves to `screenshots/`.
- `insert_to_slides.py` — Inserts screenshots into both the template deck and meeting deck. Duplicates template slide for template deck; replaces images in-place for meeting deck.
- `read_brands_from_sheet.py` — Fetches brand list from Google Sheet "Bottom" tab via service account. Skips red-text rows (belum sebulan) and HOL (Lazada-only).
- `send_email.py` — Sends email notifications via Gmail API (login reminders and success reports).
- `config.py` — URLs, Slides IDs, email recipients, timing constants.
- `brands.csv` — Maps brand `akun` → `shopee_username`. Source of truth for brand lookups.
- `capture_ref_images.py` / `ref_images/` — Reference images for visual debugging / calibration aids.
- `mouse_tracker.py` — Helper to print live mouse position while calibrating.
- `credentials.json` / `token.pickle` — Google OAuth for Slides/Drive (gitignored).
- `token_gmail.pickle` — Google OAuth for Gmail send (gitignored).
- `service_account.json` — Service account key for Sheets read (gitignored).

## Usage

```
python3 shopee_ads_screenshot.py                   # auto-fetch brands from Google Sheet
python3 shopee_ads_screenshot.py BRAND1 BRAND2 ... # manual override
python3 shopee_ads_screenshot.py --calibrate       # re-record click coords
python3 insert_to_slides.py BRAND1 BRAND2 ...      # insert latest screenshots to both slide decks
```

Brand args are uppercased and must exist in `brands.csv`. Screenshots land in `screenshots/{AKUN}_{1bulan|3bulan}_{YYYYMMDD}.png`.

## Flow (per brand)

User must navigate to Pilih Toko page manually before starting the bot. The bot does NOT navigate there at the start — it assumes you're already on Pilih Toko.

1. Switch search filter to "Username Toko", type username, Enter.
2. Click first "Detail" link.
3. Navigate to Iklan Shopee via Cmd+L + URL:
   - Indonesian brands: `https://seller.shopee.co.id/portal/marketing/pas/index`
   - Thai brands (`TH.*`): `https://seller.shopee.co.th/portal/marketing/pas/index`
4. Popup handling: checks if dimmed overlay present → tries Escape (twice if needed) → only shows macOS dialog if popup persists. No notification if no popup.
5. Scroll down to "Performa Seluruh Iklan".
6. Smart metric card detection: scans all 8 metric cards for colored top border (selected state). Deselects everything except **Biaya Iklan + ROAS**. Only clicks cards that need toggling.
7. For each of `1 bulan terakhir` and `3 bulan terakhir`: open date filter, pick option, screencapture, crop to the Performa region, save.
8. Go back to Pilih Toko via Cmd+L + `https://seller.shopee.co.id/portal/shop` (always `.co.id`, even for Thai brands).

## Domain handling

- Most brands → `seller.shopee.co.id`
- Brands starting with `TH.` → `seller.shopee.co.th` (for Iklan Shopee page only)
- Pilih Toko page is always `seller.shopee.co.id/portal/shop` (main account page)

## Google Sheet integration

- **Sheet:** `1POC6XDI1WEcSUEQG4rXgW5I2SkQwicduVJ9OY1wOW_4` tab **"Bottom"**
- Auto-updates every Thursday. Brand codes in column C ("Akun"), starting row 4.
- **Exclusions:** red-text rows (belum sebulan), HOL (Lazada-only).
- **Auth:** service account `bottom-ads-bot-shopee@fbi-dev-484410.iam.gserviceaccount.com`.

## Two presentations

### 1. Template deck (`SLIDES_ID`)

`1Ott0JcNme2979Obe4VpJNQey7Pyr6mP5YNGeK2XiFC4`

Uses a template slide (slide 1) that is duplicated per brand. Template contains:
- **Title placeholder** (top-left): brand name with hyperlink
- **Subtitle text box** (center-top): "SHO ROAS 1 Bulan Terakhir" / "SHO ROAS 3 Bulan Terakhir", Nunito 22pt bold
- **Logo image** (top-right): AHA Commerce logo
- **Background image**: includes blue bar at bottom

Template IDs are hardcoded in `insert_to_slides.py`. If the template slide is recreated, update `TEMPLATE_SLIDE_ID`, `TEMPLATE_TITLE_ID`, `TEMPLATE_SUBTITLE_ID`, `TEMPLATE_LOGO_ID`, `TEMPLATE_RECT_ID`.

Existing slides for a brand are deleted before insertion (matched by title text = brand code). Images uploaded to Drive with `anyone/reader` permission. Always picks the latest screenshot files (sorted by date suffix).

### 2. Meeting deck (`MEETING_SLIDES_ID`)

`12BCe2jvkoG1z01il6bBQRHkW3Z2aOSMUAIKG8JzqFuM`

"FBI Bottom Account" — 681 slides covering many topics per brand (GMV, harga, stok, profit, ads). Each brand has 4 ROAS slides: first pair = **Shopee**, second pair = **TikTok**. Bot finds and replaces images on the **first pair only** (Shopee). Detection: finds slides with "ROAS" + "Bulan" in text, identifies brand name, takes the first match per filter.

Brand names with dots (e.g., `TH.KSB-M`) are sanitized to underscores in Slides object IDs (dots are invalid).

## Email notifications

- **Recipients:** `tfbi@ahacommerce.net`, `claudia.ong@ahacommerce.net`
- **Login reminder:** sent before bot runs, includes brand list from Google Sheet
- **Success report:** sent after the FULL run finishes (screenshots + Slides insertion). Must list, per brand, whether the screenshot was captured and whether it was inserted into both decks. Surface any failures explicitly so the user knows which brands to redo manually.
- **Auth:** Gmail API via `token_gmail.pickle` (separate from Slides OAuth), uses `gmail.send` scope
- **Sender:** `claudia.ong@ahacommerce.net` (via OAuth)

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
- All navigation uses Cmd+L + URL (sidebar clicks and "Ganti toko" dropdown were unreliable).
- Script runs non-interactively (no stdin) — use `osascript display dialog` for user prompts, not `input()`.
- Brand names with dots break Slides object IDs — sanitize to underscores.
