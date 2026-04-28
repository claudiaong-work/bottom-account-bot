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
- `_calibrate_helper.py` — Navigates to a brand's Iklan Shopee page, scrolls to Performa, then runs `calibrate_cards()` (used when the page must be set up before card calibration).
- `_calibrate_crop_helper.py` — Same as above but runs `calibrate_crop()` to re-record the screenshot crop region.
- `_calibrate_date.py` — Standalone date-filter calibration (assumes Iklan Shopee page already in view).
- `_manual_capture.py` — Manual screenshot fallback: dialogs prompt the user to set up the page (correct metrics + filter), bot just screencaptures with the calibrated crop. Use when auto-detect can't recover.
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
6. **Auto-detect y-offset**: scans for the top of row 1 cards (first long run of white pixels at the Iklan Dilihat column) and computes offset from calibrated `EXPECTED_CARD_TOP_Y`. The offset is then added to all card click positions, date filter clicks, and the screenshot crop region — handles brands where the page has less content above (e.g. ALUN-M, TH.KSB-M) so a fixed scroll lands the Performa section higher than calibrated.
7. Smart metric card detection: scans all 8 metric cards for colored top border (selected state). Deselects everything except **Biaya Iklan + ROAS**. Only clicks cards that need toggling.
8. For each of `1 bulan terakhir` and `3 bulan terakhir`: open date filter, pick option, screencapture, crop to the Performa region (offset-adjusted), save.
9. Go back to Pilih Toko via Cmd+L + `https://seller.shopee.co.id/portal/shop` (always `.co.id`, even for Thai brands).

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

All click targets are hardcoded at the top of `shopee_ads_screenshot.py` and assume a 1710x1112 logical viewport. If the browser window size, zoom, or Shopee's layout changes, run the relevant `--calibrate*` flag to re-record them. Screenshot crop uses `CROP_TOP_LEFT` and `CROP_BOTTOM_RIGHT` multiplied by 2 for Retina.

Calibration flags (`--calibrate`, `--calibrate-cards`, `--calibrate-crop`) use **osascript dialogs** with a 5s hover delay (no `input()` since the script runs without a TTY). For card and crop calibration, the helpers `_calibrate_helper.py` / `_calibrate_crop_helper.py` first navigate to a brand's Iklan Shopee page and scroll, so the page is set up before dialogs prompt for hovers.

## Metric card positions

8 cards in 2 rows, 4 per row. **Shopee reordered the cards in 2026-04** — current layout (top row first):

- Row 1 (~y=571): Iklan Dilihat, Jumlah Klik, Persentase Klik, Pesanan
- Row 2 (~y=649): Produk Terjual, Penjualan dari Iklan, Biaya Iklan, ROAS

Detection: scans a strip of pixels above the card center (y-70 to y-5) for colored top border. Colored = selected.

## Auto-detect y-offset

`detect_y_offset()` is called after `scroll_to_performa()` in each brand's flow. It screencaptures, then scans a vertical line at the Iklan Dilihat column (logical x=459) starting at screen y=600 looking for the first run of white pixels ≥100 screen px (≈50 logical) — that's the top edge of row 1 cards. Offset = `actual_top - EXPECTED_CARD_TOP_Y` (= 536). The offset is threaded into `is_card_selected` (via pre-adjusted card positions), `select_date_filter`, and `take_screenshot` so all clicks/screenshots track the actual layout per brand.

Why it's needed: brands like ALUN-M and TH.KSB-M have less promo/banner content above the Performa section, so the fixed `pyautogui.scroll(-7, -8, -3)` lands the cards ~80–100 logical px higher than for brands with full banners. Without the offset, the bot would click row-1 coords and hit row-2 cards (or vice versa) and the crop would clip the cards while leaking "Semua Daftar Iklan" at the bottom.

## Gotchas

- `pyautogui.FAILSAFE = True` — slam the mouse to a corner to abort.
- CAPTCHA/OTP at login is manual; start the script only after you're logged in and on Pilih Toko.
- Drive upload sleeps 3s before returning the URL so Slides' image fetcher doesn't 404 on a fresh file.
- All navigation uses Cmd+L + URL (sidebar clicks and "Ganti toko" dropdown were unreliable).
- Script runs non-interactively (no stdin) — use `osascript display dialog` for user prompts, not `input()`.
- Brand names with dots break Slides object IDs — sanitize to underscores.
- `click_iklan_shopee` waits `PAGE_LOAD_WAIT + 7` (= ~10s) after navigating — Shopee's Iklan page can be slow and a too-short wait causes the bot to scroll/click before the page is ready (e.g. landing on the "Iklan Live" tab).
- The bot's fixed-tick scroll (`scroll_to_performa`) lands at different positions across brands. The auto-detect y-offset compensates; don't assume row-1 cards are always at calibrated y.
