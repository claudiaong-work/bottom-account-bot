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
6. **Force "Semua Iklan Produk" tab**: click `SEMUA_IKLAN_PRODUK_TAB`. Shopee's tab choice is sticky across navigations within a session, so even though `/portal/marketing/pas/index` is the right URL, the page may open on whatever tab was last used (e.g. Iklan Toko). The explicit click is a no-op if already correct.
7. **Auto-detect y-offset**: scans for the top of row 1 cards (looks for the structural pattern of two long white runs — row 1 and row 2 interiors — separated by a short non-white gap, at the Iklan Dilihat column) and computes offset from calibrated `EXPECTED_CARD_TOP_Y`. The offset is then added to all card click positions, date filter clicks, and the screenshot crop region — handles brands where the page has less content above (e.g. ALUN-M, TH.KSB-M) so a fixed scroll lands the Performa section higher than calibrated. If the pattern isn't found (rare), falls back to offset=0.
8. Smart metric card detection: scans all 8 metric cards for colored top border (selected state). Deselects everything except **Biaya Iklan + ROAS**. Only clicks cards that need toggling.
9. For each of `1 bulan terakhir` and `3 bulan terakhir`: open date filter, pick option, screencapture, crop to the Performa region (offset-adjusted), save.
10. Go back to Pilih Toko via Cmd+L + `https://seller.shopee.co.id/portal/shop` (always `.co.id`, even for Thai brands).

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

### 2. Meeting decks (`MEETING_SLIDES_IDS`)

Two meeting decks share the same structure, and the bot updates both:

- `12BCe2jvkoG1z01il6bBQRHkW3Z2aOSMUAIKG8JzqFuM` — original "FBI Bottom Account"
- `1f2QVMCagabXk6RidXLIYhpI6uBCVBougOKs7RPEotCE` — newer "FBI Bottom Account (13 Mei 2026)"

Each has hundreds of slides covering many topics per brand (GMV, harga, stok, profit, ads). Each brand has 4 ROAS slides: first pair = **Shopee**, second pair = **TikTok**. Bot finds and replaces images on the **first pair only** (Shopee). Detection: finds slides with "ROAS" + "Bulan" in text, identifies brand name, takes the first match per filter.

`replace_meeting_screenshots()` iterates over `MEETING_SLIDES_IDS` from `config.py` — to add another deck, append its ID there. `MEETING_SLIDES_ID` (singular) is kept as a back-compat alias for `MEETING_SLIDES_IDS[0]`.

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

- Row 1 (~y=552): Iklan Dilihat, Jumlah Klik, Persentase Klik, Pesanan
- Row 2 (~y=657): Produk Terjual, Penjualan dari Iklan, Biaya Iklan, ROAS

Detection: scans a strip of pixels above the card center (y-70 to y-5) for colored top border. Colored = selected.

Recalibrated 2026-05-11 after a small layout shift moved cards ~19 logical px up.

## Auto-detect y-offset

`detect_y_offset()` is called after `scroll_to_performa()` and the Semua Iklan Produk tab click in each brand's flow. It screencaptures, then scans a vertical line at the Iklan Dilihat column (logical x=461) from screen y=400 to y=1800, collecting every white run (`R,G,B > 248`). It then looks for the **structural pattern of two consecutive long white runs** (each ≥100 screen px = ≥50 logical) separated by a short non-white gap (20–80 screen px) — that's row 1 + row 2 card interiors with the inter-row gap between them. The top of the first matching run = actual row 1 top. Offset = `actual_top - EXPECTED_CARD_TOP_Y` (= 517). The offset is threaded into `is_card_selected` (via pre-adjusted card positions), `select_date_filter`, and `take_screenshot` so all clicks/screenshots track the actual layout per brand.

Why it's needed: brands like ALUN-M and TH.KSB-M have less promo/banner content above the Performa section, so the fixed `pyautogui.scroll(-7, -8, -3)` lands the cards ~80–100 logical px higher than for brands with full banners. Without the offset, the bot would click row-1 coords and hit row-2 cards (or vice versa) and the crop would clip the cards while leaking "Semua Daftar Iklan" at the bottom.

Why two-run pattern (added 2026-05-11): the old single-run scan false-matched plain white space above the cards (e.g., the gap between promo banners and the tabs row on the Iklan Toko view), returning offsets like -217 that cascaded into the date-option click landing on the "Iklan Toko" tab and silently switching tabs mid-run. Requiring the two-row pattern eliminates that false match — empty white space produces only one run.

## Gotchas

- `pyautogui.FAILSAFE = True` — slam the mouse to a corner to abort.
- CAPTCHA/OTP at login is manual; start the script only after you're logged in and on Pilih Toko.
- Drive upload sleeps 3s before returning the URL so Slides' image fetcher doesn't 404 on a fresh file.
- All navigation uses Cmd+L + URL (sidebar clicks and "Ganti toko" dropdown were unreliable).
- Script runs non-interactively (no stdin) — use `osascript display dialog` for user prompts, not `input()`.
- Brand names with dots break Slides object IDs — sanitize to underscores.
- `click_iklan_shopee` waits `PAGE_LOAD_WAIT + 7` (= ~10s) after navigating — Shopee's Iklan page can be slow and a too-short wait causes the bot to scroll/click before the page is ready (e.g. landing on the "Iklan Live" tab).
- The bot's fixed-tick scroll (`scroll_to_performa`) lands at different positions across brands. The auto-detect y-offset compensates; don't assume row-1 cards are always at calibrated y.
- **Iklan Shopee tab is sticky across sessions.** Even with the right URL, Shopee opens whichever tab was last used (Iklan Toko, Iklan Banner, etc.). The bot always clicks `SEMUA_IKLAN_PRODUK_TAB` after scrolling to defend against this — do NOT remove that step.
- **When verifying calibrated coords, never use osascript Yes/No dialogs.** The dialog appears centered on screen and can physically cover the cursor at the hovered position, producing false-negative "No" answers even when the coord is correct. Use `pyautogui.moveTo` + `screencapture` + read the PNG to check where the cursor actually landed.
- **Wrong date filter clicks ≠ stale date filter calibration.** When a click lands wrong, the usual cause is `detect_y_offset` returning a bad value (or the bot being on the wrong tab), which shifts every downstream click. Check the bot's stdout for the printed offset before re-calibrating the date filter coords.
