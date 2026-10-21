# Google Ads — formats, limits and how the Summit uses them

Limits are in `specs.json` (read from Google's help pages on 2026-10-21; `ads.py lint` enforces them). This file says what each format is for and the judgement around it. Google changes limits and policies without notice: when a number here disagrees with the Ads UI, the UI wins — fix `specs.json`.

## Which campaign type takes which assets

| Campaign type | What you give it | `ads.py` produces |
|---|---|---|
| **Search** — responsive search ad (RSA) | 3–15 headlines (30 chars), 2–4 descriptions (90), 2 path fields (15), a final URL. No images | `google.rsa` text, checked; `_google_rsa_editor.csv` (paused) |
| **Display** — responsive display ad | 1–5 short headlines (30), 1 long headline (90), 1–5 descriptions (90), business name (25), images 1.91:1 and 1:1, logos 1:1 and 4:1 | `google.display` text; `google_landscape`, `google_square`, `google_logo_*` PNGs |
| **Performance Max** — asset group | 3–15 headlines (30, one ≤ 15), 1–5 long headlines (90), 2–5 descriptions (90), business name, images 1.91:1 + 1:1 (+ 4:5 optional), logo 1:1, video optional | `google.pmax` text; the same image set + `google_portrait` |
| **Demand Gen** | 1–5 headlines (**40**, one ≤ 30), 1–5 descriptions (90), business name, images 1.91:1 + 1:1 (+ 4:5, 9:16 optional), logo 1:1 (**≤ 150 KB**) | `google.demand_gen` text; the image set + `google_vertical_9x16` |
| **Uploaded display ads** (IAB sizes) | A finished image, ≤ 150 KB: 300x250, 336x280, 728x90, 970x90, 160x600, 300x600, 320x50 | Not here — `wm-web-banners` builds them (with a button, GIF, size ceiling) |

Images: JPG/PNG, ≤ 5 MB. Recommended sizes: 1200x628, 1200x1200, 960x1200 (4:5), 1080x1920 (9:16).

**What Google wants in the picture** (Google's *Best practices guide for responsive display ads*, read 2026-10-21): no logo laid over an image (it repeats in some layouts; the logo goes in the logo asset), no text laid over it (it repeats the headlines and is unreadable when the ad is small; text that is part of the scene is fine), no collage, no heavy filter, and **no button graphics** such as "Play", "Download" or "Close" — those promise functions the ad does not have and **violate policy**. The first three are guidance, the button is policy. Google can also add its own text and logo overlays with asset enhancements; switch them off if you want none.

A creative without a photo is built as a **plate**: flat navy, the gold service line and the headline, nothing else — no lockup, no marks, no support line. That is the closest a typographic asset gets to the guidance, but it is still text on an image: say so. A creative with `"photo"` (a file from `assets/imagery/`) gets the clean crop instead: the picture alone, exact pixels, nothing laid over it — Google's preferred asset. The pictures are licensed stock (the user's statement of 2026-10-21): repeat that in the hand-off.

Video is out of scope for this skill (no video exists for the Summit); if the user supplies one, check it against the page the format links to.

## Writing an RSA that Google can use

Google picks any headline with any other, in any order, and shows 2–3 of them. So:

- **Every headline must stand alone** and not contradict another. No headline may need its neighbour to make sense ("…in Lisbon" after "Two days" is fine only if the first also works without it).
- **Cover different jobs**, not synonyms: the event name · the dates and place · a hard fact (two days, ten workshops, 26 speakers, limited to 200) · the topic (Plan B, C and D planning, cross-border strategy) · who it is for (advisors, family offices, global families — third person) · the rate tier and its end date · the call to action ("Secure your place"). Twelve distinct headlines beat fifteen restated ones.
- **Don't pin** unless a line must always show. Pinning one asset to a position removes combinations and lowers Ad Strength. The usual exception is the event name pinned to H1 (so the brand always leads); text that must appear in every ad is pinned to H1, H2 or D1.
- **No trailing full stop** in a headline; sentence case; no exclamation mark (Google rejects it in headlines); numerals for facts in text assets ("26 speakers"), words only on the graphics.
- Path fields: `Summit` / `Lisbon` (15 chars max each) — they build the display URL `wealthandmigrationsummit.com/Summit/Lisbon`; they are not links.
- Ad Strength is a hint, not a goal. Do not pad with near-duplicates to reach "Excellent".
- Optional: a countdown customizer (`{=COUNTDOWN("2026/11/05 09:00:00","en")}`) keeps "days to go" true without a daily edit. The syntax and availability are Google's — confirm in the UI before relying on it; `ads.py` skips the length check for any `{=` text and warns.

Older guides say Performance Max needs one description of 60 characters or fewer; the Help page read on 2026-10-21 lists only 90-character descriptions (2–5). If the UI asks for a short description, add one — `specs.json` is where to record it.

## Keywords and structure (Search) — a starting hypothesis for the user to review

The skill does not set budgets, bids or targeting. It can propose the shape of the campaign:

| Ad group | Intent | Seed phrases (phrase / exact match) |
|---|---|---|
| Brand | Someone looking for this event | wealth and migration summit · wealth & migration summit lisbon |
| Event | Looking for a conference | investment migration conference · global mobility summit · residency by investment event · golden visa conference lisbon |
| Place + time | Planning travel | lisbon conference november 2026 · lisbon summit 5 november |
| Topic | Learning about the subject | plan b residency planning · cross-border wealth planning event |

Negatives worth adding up front (these searches want a service, not a conference): *jobs, careers, free, visa application, apply, renew, passport renewal, work permit, student visa, tourist visa, cost of, requirements*. Volumes and costs are not on file; never quote any.

## Tracking and what Google can see

- The site's tags are consent-gated: the Google tag loads only after the HubSpot banner reports analytics/advertising consent (`tags.js`), so conversions are **under-counted** against Stripe receipts. Say so in the hand-off.
- The conversion that matters fires on `/thank-you` after a completed Stripe checkout. Optimise for it only if the campaign will realistically collect conversions in its window; for a two-week flight, a landing-page-view or "Secure your place" click goal gives Google more to learn from.
- Use the final URL suffix printed in `_copy.md` (`utm_source=google&utm_medium=cpc&…`) so GA4 separates paid from organic.
- Landing page: the home page carries the programme (the argument); `/claim-your-seat` is the booking page (`noindex`, payment). Cold traffic → home; people who already know the Summit → booking. The user decides; do not assume.

## Policy — check before uploading (verified 2026-10-21 unless marked)

1. **Destination must load.** The site's own `CLAUDE.md` says it sits behind HTTP Basic Auth until launch; a preflight on 2026-10-21 returned 200, and the gate can come back. A reviewer that meets a password prompt disapproves the ad ("destination not working"). Run `ads.py preflight <url>` for every final URL, on the day of upload.
2. **Government documents and services** — a third-party summary (TechWyse, not Google's page) says Google began enforcing a certification requirement for ads that promote visa, passport and similar government services on 5 Oct 2026. The Summit sells a conference place, not a visa, so the ad must say only that. The lint rejects copy that reads as an offer of a visa, passport or citizenship. If Google still flags the account, appeal as ticket sales for an event and point to the programme. **Unverified against Google's policy page — read it in the Policy Manager.**
3. **Business name** — max 25 characters and it must match the domain or the legally verified business name (Advertiser Verification). "Wealth & Migration Summit" is exactly 25. The advertiser is Global Citizen Solutions: confirm which name the account is verified under; the fallback is "Global Citizen Solutions" (23).
4. **Personal attributes** — Google bars ads that imply knowledge of a viewer's financial status or similar. Write about roles in the third person (advisors, family offices, global families), never "you, a high-net-worth individual".
5. **Unverifiable claims** — "best", "leading", "#1", guarantees, and outcome promises are rejected or require proof the Summit has not got. The lint blocks the common ones.
6. **Editorial** — no exclamation in headlines, no shouting capitals, no emoji, no URL or phone in text assets, no trailing punctuation in headlines.
