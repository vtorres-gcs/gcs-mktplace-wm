---
name: wm-paid-ads
description: "Creates paid ads for the Wealth and Migration Summit 2026 (Lisbon, 5–6 Nov 2026, convened by Global Citizen Solutions) on Google Ads and Meta Ads: platform-exact text (responsive search ads, responsive display, Performance Max, Demand Gen; Meta feed, Stories/Reels, carousel, link ads) checked against each platform's limits and the Summit's confirmed facts, plus navy-ground image creatives at the right sizes and safe zones. Lints prices against the rate tier in force for the whole flight, blocks urgency, guarantees and visa-for-sale wording, exports a copy sheet, CSV and a paused Google Ads Editor file, and checks the landing page loads. Use whenever the user mentions anúncios pagos, paid ads, Google Ads, Meta Ads, Facebook or Instagram ads, search ads, RSA, display, Performance Max, Demand Gen, Stories ads, tráfego pago, criativos or copy de anúncio for the Summit. Not for organic social (wm-social-media), IAB banners or GIFs (wm-web-banners), or the landing page."
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "New skill. Platform limits read from Google Ads Help and Meta's Ads Guide on 2026-10-21 (references/specs.json); facts from the site repo commit 1823ec1 via the sibling skills' FACTS.md and data copies. Fills the gap the social and banner skills leave ('Not for paid ads')."
---

# Paid ads — Wealth & Migration Summit 2026

One job: turn **a brief** (platform, formats, flight dates, audience) into an **ad pack** the user can upload to Google Ads and Meta Ads — text assets that fit each platform's limits, image creatives at the exact sizes with safe zones respected, and a hand-off that names every risk the platforms or the facts can raise. `scripts/ads.py` does the checking, the export and the rendering; your work is the questions, the angle, the copy and the judgement about what the result looks like.

You do not log in to Google Ads or Meta, set budgets, bids or targeting, or upload anything. The user does that in the platform; the pack is built so that step is paste-and-check.

Reply in the user's language (Portuguese in, Portuguese out). The words **in the ads** are English, British spelling, because the Summit's copy is — unless the user asks for another language, in which case say that a translation is not client-approved copy.

## Source of truth

| File | What it is |
|---|---|
| `references/FACTS.md` | Every fact an ad may state — dates, programme, the 200 cap, rate tiers, what is included, what is retired — dated, with its site source. **Read it in full on the first job of a session.** It beats `PRODUCT.md` wherever they disagree |
| `references/ad-copy-playbook.md` | What an ad may say, the rate calendar, angles by audience, a lint-clean copy bank, voice. **Read before writing copy** |
| `references/google-ads.md` · `references/meta-ads.md` | Per platform: which campaign type takes which assets, how to write for it, structure suggestions, tracking, and the policy points to check. Read the one(s) in scope |
| `references/creative-design.md` | How the site's design system lands on an ad image: type, marks, no button, safe zones. Read before judging a render |
| `references/specs.json` | The limits and sizes `ads.py` enforces, with the date they were read. Google limits are hard (the UI rejects them); Meta's are guidance. If the platform UI disagrees, edit this file |
| `references/PRODUCT.md`, `references/DESIGN.md` | Verbatim copies of the site's files: voice, positioning, what must never be invented; palette and type |
| `references/data/*.json` | `rates.json`, `programme.json`, `site.json` — what `ads.py lint` reads to validate prices, times and counts |
| `references/example-pack.json` | A complete working pack (Advance Rate, Google + Meta). Copy it; don't start from a blank file |
| `assets/` | `fonts/` (Caladea, Archivo + licences), `logos/` (`wm/`, `gcs/`, `cnn-portugal/`, `partners/`), `imagery/` (hero, Lisbon photographs, dark plates, venue) and `speakers/` (26 portraits). The user confirmed on 2026-10-21 that the images are licensed stock with rights for paid use (not AI-generated) and cleared the logos and speaker portraits. Logos are used as supplied; never recoloured or redrawn |

`FACTS.md`, `PRODUCT.md`, `DESIGN.md` and `data/` are copies from the sibling skills (the site repo `gcs-wealth-migration-summit` is read-only for this purpose). When `wm-social-media` refreshes its facts, copy them here too. Everything here expires after **6 Nov 2026**.

## What it produces

| Platform | Campaign type | Text | Images |
|---|---|---|---|
| Google | Search (RSA) | 3–15 headlines ≤ 30, 2–4 descriptions ≤ 90, 2 paths ≤ 15 | none |
| Google | Responsive display | short headlines ≤ 30, long ≤ 90, descriptions ≤ 90 | 1200x628, 1200x1200 + logos 1200x1200, 1200x300 |
| Google | Performance Max | headlines ≤ 30, long ≤ 90, descriptions ≤ 90 | the set above + 960x1200 |
| Google | Demand Gen | headlines ≤ 40 (one ≤ 30), descriptions ≤ 90 | the set above + 1080x1920 |
| Meta | Feed / Stories / Reels / carousel / link | primary text, headline, description (guidance lengths) | 1440x1800, 1080x1080, 1080x1920 (safe zones), 1200x628 |

Google image assets are **plates** — the service line and the headline on flat navy, no lockup, no marks, no support line — because Google's responsive-image guidance says not to overlay logos or repeat the text assets on a picture; the logo travels as the separate logo asset. Meta images carry the lockup, the support line and the GCS + CNN Portugal marks. A creative with `"photo": "<file in assets/imagery/>"` puts the picture under a layered navy scrim on Meta formats, and on Google formats crops it clean with nothing laid over it (Google's preference).

`python3 <SKILL_DIR>/scripts/ads.py formats` lists the formats and their keys. Uploaded IAB display sizes (300x250, 728x90…, ≤ 150 KB, GIF) are `wm-web-banners`. Video is out of scope.

## Workflow

```
1. Ask         → platforms and formats · flight dates · audience · landing page
2. Facts       → which rate tier is in force for the whole flight (ads.py rate)
3. Write       → angle, then the pack JSON (copy + creatives)
4. Lint        → ads.py lint — fix every ERROR, read every WARN
5. Preflight   → ads.py preflight <url> — can a reviewer load the page?
6. Build       → ads.py build → copy sheet, CSVs, PNGs, contact sheet, size check
7. Look        → read the contact sheet and the tall formats; iterate
8. Hand off    → files, tiers and dates, risks to clear, what the user does in the UI
```

### 1 — Ask

Ask in the user's language as one `AskUserQuestion` call when it is available (otherwise plain chat). Ask only what the message does not answer, never more than four questions:

1. **Platforms and formats** — Google Search (RSA) · Google image assets (Display / Performance Max / Demand Gen) · Meta feed + Stories. Several can apply; "both, the full set" is a valid answer.
2. **Flight** — go-live and end date, and whether the ads show a price. The rate tier is decided by these dates (see step 2), so never guess them. Offer the real windows: Advance Rate to 30 Oct · Final Rate 31 Oct – 4 Nov · spans both (two versions) · no price.
3. **Audience** — one of the four rooms the site names (global families · legal and tax counsel · private banking · industry and government), or the warm audience (site visitors). One slice per ad group / ad set.
4. **Landing page** — home (cold traffic, the programme argues) or `/claim-your-seat` (warm, takes payment), and whether the user has confirmed the URL is public.

When the tool is not available (or nobody can answer), state the defaults you used and go on: both platforms; Google = RSA + Display image assets; Meta = feed 4:5 + Story 9:16 + square; audience = the broadest slice the playbook supports for the angle; flight = go-live today, end the day before the Summit, **no price** if that crosses a tier change; landing = home; URL unconfirmed (so it is flagged, not printed in copy).

### 2 — Facts and flight

```bash
python3 <SKILL_DIR>/scripts/ads.py rate --on <go-live date>
```

It prints the tier in force and when it changes. A price in an ad is only ever the tier in force for **every day of the flight** — an ad that outlives its tier is wrong the next morning, and nobody edits it. If the flight crosses a boundary, either ship two versions (each ending on its tier's last day) or leave the price out. Every ad ends before the Summit opens (5 Nov, 09:00 Lisbon). Before 1 Sep and after 4 Nov say nothing about price.

### 3 — Write the pack

Start from `references/example-pack.json`. Write the JSON from Python (`Path.write_text(json.dumps(pack, ensure_ascii=False, indent=2))`), never a shell heredoc — the dashes, `€` and `’` in the copy break there. The fields are in the docstring of `scripts/ads.py`; the playbook says what each angle may claim.

- **One angle per pack**, named in `name` (`wms26-<angle>-<tier>`). Choose the angle from the audience slice; the programme is the argument, so a specific fact (Ten workshops, Limited to 200 attendees, a session title verbatim from `programme.json`) outranks any adjective.
- **RSA:** about 12 headlines and 4 descriptions that do *different jobs* — event name, dates and place, a hard fact, the topic, who it is for, the rate tier and its end date, the call to action. Google shows any headline with any other, so each must stand alone and none may need its neighbour. Don't pin unless a line must always show.
- **Meta:** 2–3 primary texts and 2–3 headlines that genuinely differ; the first ~125 characters of a primary text carry the message because the rest sits behind "See more". The call-to-action button is the platform's (`Learn more` cold, `Book now` warm), not part of the image.
- **Creatives:** one or two. A headline of 12 words or fewer, sentence case, an optional support line, formats chosen from `ads.py formats` for the platforms in scope. Sentences on separate lines (*Two days. / Ten workshops.*) stay one line each — the type shrinks rather than wrap them. A different headline for one format goes in `by_format`. No button. Photography comes from `assets/imagery/` (`"photo"` in the creative; `plate-*-dark` files are already graded for text) or from a file the user supplies; `ads.py photo <image> --out <dir> --formats <keys>` crops any picture to the exact sizes with nothing laid over it. The user states these are licensed stock photographs, not AI (the site's `PRODUCT.md` still calls its page imagery generated and on a replacement list — that note is older; say in the hand-off that the licence is the user's statement and the stock licence should cover paid advertising). Never present a stock picture as the venue or a real event of this Summit. Speaker portraits are in `assets/speakers/`; the layout for a speaker ad is not built yet, so ask before promising one.
- **A price on cold traffic.** The playbook keeps price lines for the warm funnel (the programme argues first). When the user asks for a price on a cold campaign anyway, do it — their call — but put it second: in the last description, the last primary text and the support line, never in the opening line of a text or the headline of the graphic, and say in the hand-off that you did.
- **Mode B** — if the user hands you finished copy, keep it verbatim; lint it, report what fails, and propose a fix instead of rewriting it silently.

### 4 — Lint

```bash
python3 <SKILL_DIR>/scripts/ads.py lint pack.json
```

It checks counts and lengths (Google: hard; Meta: guidance), duplicates, the voice (no exclamation, emoji, superlatives, shouting capitals), the facts (prices vs the tier in force for the whole flight, times, dates, counts of speakers/workshops/days/attendees, retired facts, past-edition framing), and the policy edges (offers that read as selling a visa or passport, guarantees, second-person claims about the viewer's wealth, Meta's social-issues words, the sanctions workshop). Fix every ERROR. Read every WARN and decide; say in the hand-off which you chose to keep.

### 5 — Preflight

```bash
python3 <SKILL_DIR>/scripts/ads.py preflight <final url>
```

A platform reviewer who meets a password prompt disapproves the ad. The site's own repo says it sits behind HTTP Basic Auth until launch; the answer today may differ, and the gate can come back. Run it for each final URL on the day of upload, and say the result. Add `--pack pack.json` and it also reads the euro amounts in the page's HTML and warns when the ad's price differs from the rate the page marks as current — a mismatch between ad and landing page is a disapproval reason on both platforms (on 2026-10-21 `/claim-your-seat` marked the €499 Advance Rate as "NOW" in static HTML). It sees the HTML as served, not a rate JavaScript switches by date, so open the page in a browser on the go-live day.

### 6 — Build

```bash
python3 <SKILL_DIR>/scripts/ads.py build pack.json --out <out dir>
```

`build` lints (and stops on errors), writes the copy sheet and CSVs, renders every creative in every format from the pack, writes a contact sheet, and checks each PNG's exact pixels, minimum size and file-size ceiling. `render --creative <id> --only <format>` redoes one file; `--keep-html` keeps the editable HTML under `src/`. The pack JSON is the source of truth: change the pack and rebuild, never patch a render. If the copy does not fit at the type floor, `render` says so — shorten the copy, don't shrink the type.

### 7 — Look at it

A script passing is not the same as the ad being good. Read the contact sheet (`<slug>_sheet.png`), then open the 9:16 and the 1.91:1 at full size — those are the formats that break first. Judge as a person scrolling would: is the headline the biggest thing and does it read in one glance; is the gold service line the only warm light; are the marks legible; does the Story keep the top 14% and bottom 35% empty; does the empty navy look intentional. Show the user the renders (`SendUserFile` when available) and let them steer. Only their approval ends the loop.

### 8 — Hand off

Say, in the reply, each that applies:

- the files, and the pack they came from;
- **the rate tier(s) used, the first day each ad may run and the last day it is true** (a price ad scheduled before its tier begins is as wrong as one that outlives it; `_copy.md` prints both dates), and the flight dates — or that no price is shown; and that the landing page must show the same price on those days;
- the **preflight result** and which URL to use; the Editor CSV is written with `Paused` status, so nothing goes live by import;
- the **risks to clear before upload** (the playbook and platform files carry the detail): Google's business-name rule (Advertiser Verification; "Wealth & Migration Summit" is exactly 25 characters) · Google's government-documents policy (third-party summary, verify) · Meta's social-issues list (immigration) and its EU restriction (verify, and tell the user early) · the personal-attributes rule · consent-gated tracking, so reported conversions will sit below Stripe · the conversion's **value**: `/thank-you` reads `?value=` from the Stripe redirect (the site's own comment shows `value=499`), so a redirect that stays at 499 or drops the parameter reports the wrong revenue from 31 Oct · the **ad account's time zone** against Lisbon (a schedule set to end "4 Nov" ends at the account's midnight, not Lisbon's);
- the **marks assumption** (GCS + CNN Portugal on every creative, applied from the banner decision of 2026-10-20; `"marks": "summit-only"` removes them);
- what the user does in the platform: the call-to-action button, audiences, budget, bids, schedule — none of which this skill sets;
- the **date the platform limits were read** (`specs.json`, `checked_on`): they change without notice;
- the alt text per creative (in `_copy.md`), one line each;
- anything unconfirmed: the URL, the venue spelling (the site writes both *Marques* and *Marquês*), the Turkey/Malta inconsistency if a workshop line was used.

Then offer: the next tier's version of the same pack; a second audience slice; the same copy in Portuguese or Spanish; the IAB banner set from `wm-web-banners`.

## What this skill will not do

The brand and the evidence on hand set hard edges. Never, in any mode:

- invent **sponsor or partner roles, testimonials, past-edition figures, attendance so far, reach, CPC, CTR or any performance number**;
- state a **price** that is not one of the three published tiers, or that is not the tier in force for the whole flight; use **urgency mechanics** ("last chance", "only N seats", "book now" as copy), a day count, or a countdown that goes stale. Scarcity is factual and said once: "Limited to 200 attendees." A deadline is a date;
- write anything that reads as **selling a visa, passport, residency or citizenship**, or promises an outcome ("guaranteed", "fast-track", "approval in 30 days") — the ad sells a conference place;
- address the viewer as **wealthy, high-net-worth, an immigrant or an expat** — both platforms bar ads that assert or imply a personal attribute; speak of roles in the third person;
- pair a **speaker** with a session, or name anyone not in the 26-speaker roster — the two programme pages disagree about who is where, so a pairing needs the user's confirmation in this conversation; portraits come only from `assets/speakers/`, unaltered;
- put a **partner or sponsor logo** (`assets/logos/partners/`) on a creative unless the user names it for that ad, and never give any logo a role ("official partner of…") — the site does not say what each one is;
- generate a **new** AI image, present a stock picture as the real venue or a real event of this Summit, or draw a button, a play icon or a fake notification;
- show a **partner price or promo code** — the partner landing pages (`/gfpi`, `/redbridge`, `/trustedadvisor`, `/imglobalwealth`) carry partner-only prices and codes; they are not a public offer and the lint rejects the amounts;
- print a **URL** in the copy that the user has not confirmed, or put a URL in Google text assets at all;
- state a session title or time that is not in `references/data/programme.json`, compute end times, or give a "session" count (the countable facts are 2 days · 10 workshops · 26 speakers);
- use a retired fact: "Golden Visa Pathway" / "Structuring, Context & Experience" day themes, a 150–200 cap, a networking dinner, "Register your interest" (`FACTS.md` lists them; `lint` rejects them);
- keep the sanctions / restricted-nationals workshop in paid copy, or use "immigration", "migrants", "border", "refugee" or "asylum" on Meta (a warning, not a block: the user may overrule it knowingly).

## Outputs and naming

Write to `/mnt/user-data/outputs/` when it exists, otherwise `./output/<slug>/` (`slug` = the pack `name`, kebab-case).

| File | What it is |
|---|---|
| `<slug>_pack.json` | The pack — copy the one you wrote here so the job is reproducible |
| `<slug>_copy.md` | Every text asset with its character count, limit and pin; flight, tier and URL parameters; alt text |
| `<slug>_copy.csv` | The same in long form (platform, format, field, index, text, chars, limit, pin) |
| `<slug>_google_rsa_editor.csv` | One row per RSA with Headline 1–15 / Description 1–4 and positions, paths, final URL and suffix, status **Paused**. Column names follow Google Ads Editor's own export; if Editor rejects one on import, drop it or paste the text from `_copy.md` |
| `<slug>_<creative>_<format>_<W>x<H>.png` | One image per creative per format, at the platform's pixels |
| `<slug>_google_logo_square_1200x1200.png`, `…_landscape_1200x300.png` | Google logo assets when `google_logos` is true |
| `<slug>_photo_<format>_<W>x<H>.jpg` | A client-cleared photograph cropped to a format, from `ads.py photo`; nothing laid over it |
| `<slug>_sheet.png` | Contact sheet of everything rendered |

> **Reminder:** ask platforms · flight · audience · URL, then `ads.py rate` — a price is the tier in force on every day of the flight, or none · copy from confirmed facts, written for a conference place, never a visa · `lint` before `build`, `preflight` before upload · look at the 9:16 and the 1.91:1 · the Editor file is Paused · say what the user must clear in Google and Meta before they click publish.
