---
name: wm-social-media
description: "Creates social creatives for the Wealth and Migration Summit 2026 (Lisbon, 5–6 November 2026, curated by Global Citizen Solutions) in its own 'Lisbon Nocturne' identity (navy ground, amber light, Caladea + Archivo): carousels (Instagram/LinkedIn/X/Facebook), single posts, Stories (1080×1920) and LinkedIn posts. Give it a topic, programme day, workshop, speaker, rate change, draft copy, a DOCX/Markdown file or a URL — it checks its facts against the Summit site's published programme, 28-speaker roster and rate tiers, plans the slides, writes or preserves the copy from confirmed facts only, builds one editable HTML file, opens it for live text edits, lints layout and facts (prices, times, names), renders PNG/PDF after approval, and ships a caption with alt text. Use whenever the user mentions the Summit, Wealth & Migration Summit, WMS, the Lisbon summit, a programme day, a workshop, a speaker spotlight, tickets, rates, securing a place, partnering with the Summit, a countdown, or any post/carousel/story for this event, even without saying 'carousel'. Not for paid ads (use wm-paid-ads), the landing page itself, or general GCS social content."
allowed-tools: Bash(*), Edit, Write, mcp__Claude_Browser__preview_start, mcp__Claude_Browser__navigate, mcp__Claude_Browser__javascript_tool, mcp__Claude_Browser__computer, mcp__Claude_Browser__read_page, mcp__Claude_Browser__tabs_create, mcp__Claude_Browser__tabs_close
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "Sync with site repo at f2fbee2: 31 speakers (added Sheree Mitchell, Teresa Barbosa, António Henriques; Sheree Mitchell upgraded from agenda-only); Hadley Gamble added as Summit Host (not a speaker); 8 new partner booking pages (AmCham, PHKCCI, Bison Bank, Atlântico, BPCC, WMS50, LinkedIn, GCS Clients); Bison Bank added as strategic partner; homepage session titles now canonical (approved); FACTS.md + data JSONs refreshed; new speaker photos added."
---

# Social Media — Wealth & Migration Summit 2026

Generates **Carousels**, **Single Posts**, **Stories** and **LinkedIn Posts** for one event, in that event's own identity. Slides are authored as one editable HTML file and rendered with **Playwright**. Before any PNG/PDF is rendered, the generated HTML always opens in the Browser pane so the user can click into any text and retype it directly; plain-language chat requests cover everything else (swap a photo, reorder, remove). Only after the user approves does rendering happen.

## Source of truth — read first, every time

| File | What it is |
|---|---|
| `references/FACTS.md` | **Every fact a post may state**, dated, with the site source: event, programme, 28 speakers, rate tiers, booking, partners — plus what `PRODUCT.md` still says that is no longer true, and where the site's own pages disagree. Data in `references/data/*.json`, read through `scripts/facts.py` |
| `references/PRODUCT.md` | Who the Summit is for, positioning, voice, what must never be invented, accessibility floor. Its **fact sections** (programme, pricing, roster, registration, capacity) lag the live site and are overridden by `FACTS.md` |
| `references/DESIGN.md` | The visual system: palette, type ramp, rules (One Light, Hour, Gold Never Touches Paper, Named Alpha, Ramp Is Closed…), components, do's and don'ts |
| `references/content-playbook.md` | What to post: the post types, the facts each may use, the arc, copy rules, and the **caption + alt-text file** every job ships |
| `references/design-system.md` | How those two land on a 1080px social canvas — canvas-scale ramp, what carries over, what was dropped from the old GCS skill, open assumptions |
| `references/img/cover-reference.webp` | **The client's reference cover.** Look at it before building any cover — layout, masthead, type, marks and wash all follow it (`slide-library.md` → Cover) |
| `references/slide-library.md` | Vocabulary of slide compositions and markup, written against the class vocabulary — a starting point; the layout is decided from `DESIGN.md` |
| `references/rendering.md` | Build, lint, render, PDF — at generation time |

`PRODUCT.md` and `DESIGN.md` are verbatim copies of the project's own files. **When the project updates them, replace the two files here** — the palette is parsed from `DESIGN.md` at import time, so new colours flow into every slide without editing code. `sync_site_facts.py check` tells you when they differ.

**Precedence.** Facts: `FACTS.md` / `data/` beat everything, `PRODUCT.md` included. Voice, positioning and the "never invent" edges: `PRODUCT.md`. Visuals: `DESIGN.md` beats the other references. The site moved on after `PRODUCT.md` was written — a post built from `PRODUCT.md`'s fact sections alone (the "Golden Visa Pathway" day, a 150–200 cap, "register your interest", no prices, 14 speakers, a networking dinner) is wrong today.

## Assets — look here before anything else

Every image, logo, font and speaker portrait this skill uses lives inside the skill folder. Resolve them from `<SKILL_DIR>`, the folder that holds this `SKILL.md` (`${CLAUDE_SKILL_DIR}` when the skill is loaded from the plugin).

| Path under `<SKILL_DIR>` | Holds | Notes |
|---|---|---|
| `assets/logos/` | Event lockups (`w&m-horizontal White/blue.svg` = the masthead; `w&m-default`, `w&m-vertical`, `w&m-symbol.svg`), Global Citizen Solutions marks (`GCS-Primary-White.png` / `GCS-Primary-Blue.png`, `GCS-Secondary/Symbol-White.png`, `gcs-footer-{symbol,text}-{navy,white}.svg`), CNN Portugal (`Logo CNN PORTUGAL Float BRANCO` / `BLACK` / `Float` / square `Final`) | Use as supplied; never recolour or redraw. Don't pick files by hand: `mast(on)` and `marks(on)` in `summit_assets` choose the right one per ground (white marks on dark; on white, the primary blue GCS and the red CNN Portugal `Float Final`). **The GCS mark stands alone — nothing written above, beside or over it** |
| `assets/speakers/` | 26 square headshots, `<first-last>.webp` — one per speaker on the site's roster | Look people up with `facts.speaker("name")` / `facts.speaker_photo("name")`; a name not in `facts.speakers()` is not drawn |
| `assets/img/` | Photographs and graphics: `carousel-*` (Lisbon bridge / MAAT / castle, darkened — usable as plates), `hero*`, `epic-sana*`, `og-share.jpg`, `nocturne-texture*`, `claim-your-seat.webp`, `reg-*.svg`, partner logos, `lisbon-*-2400.webp` (Vasco da Gama bridge at sunrise `photo.vasco-da-gama-sunrise` — blue hour, fits the Nocturne grade; Lisbon sunset panorama `photo.lisbon-sunset` — warm amber; Arco da Rua Augusta `photo.arco-rua-augusta` — bright daylight, off the Nocturne look, grade it hard under the scrims or use it sparingly) | The three `lisbon-*` photos are licensed stock-library photographs (real photos, not AI; rights cleared for use) — no licence caveat needed. Partner / sponsor logos in this folder are **not cleared for use** unless the user confirms them for the post — see "What this skill will not do". Embed with `embed_image(path)`; measure any photo under text with `qa.py scrim` |
| `references/data/` | `speakers.json`, `programme.json`, `rates.json`, `site.json` — extracted from the site's `index.html` | Read through `scripts/facts.py`; refreshed by `scripts/sync_site_facts.py` |
| `assets/fonts/` | Caladea, Archivo + OFL licences | Loaded through `summit_assets.py` |

**Rules.** (1) Reuse an existing asset from the table before producing or fetching a new one. (2) A new asset goes into the matching `assets/` sub-folder, never next to the output. (3) An output HTML that leaves the skill folder must inline its assets (`embed_image()`, base64 `@font-face`) — `build_document()` does this for fonts and tokens.

## Self-contained — runs anywhere

Copy this folder alone to any machine with Python 3, `playwright`, `pillow`, `beautifulsoup4` and `lxml`; every format renders. Fonts (Caladea, Archivo), the Global Citizen Solutions marks, the palette and the confirmed facts (`references/data/`) all come from this folder, via `scripts/summit_assets.py` and `scripts/facts.py`. Only `scripts/sync_site_facts.py` ever looks outside it, and only to read the site repo when you refresh the facts.

```bash
python3 <SKILL_DIR>/scripts/summit_assets.py   # verify the bundle + palette contrast before a long job
python3 <SKILL_DIR>/scripts/facts.py freshness # rate about to change? facts older than a week? event over?
```

Only `flag_uri()` (country flags) needs internet. **Never** resolve an asset through a repo root or a `Path.cwd()` walk-up. If a new asset is needed, bundle it under `assets/` and expose it in `scripts/summit_assets.py`.

## What this skill will not do

The brand and the evidence on hand set hard edges. Never, in any mode:

- invent **sponsor or partner roles, testimonials, past-edition figures, attendance numbers so far**, or photography of Lisbon / EPIC SANA Marques owned by GCS (none exists);
- state a **price** that is not one of the three published rate tiers, or that is not the tier in force on the day the post goes live (`facts.rate_on()`); outside 1 Sep – 4 Nov say nothing about price. State the tier and its end date in the hand-off;
- put a **partner or sponsor logo** on a creative unless the user names it for this post and confirms it is cleared for social use (the site shows ten logos and never says what each one is). The exception is the pair the site hero itself shows beside the title — **Global Citizen Solutions and CNN Portugal** — which the cover and closing slide carry by default (`marks()`);
- write anything above, beside or over the GCS mark (no "Curated by");
- name a person who is not on the site's 28-speaker roster (`facts.speakers()`), or alter / generate a speaker's portrait. The names that appear only on the older agenda page are listed in `FACTS.md` and rejected by `qa.py lint`;
- **pair a speaker with a session** without the user confirming it in this conversation — the site's two programme pages disagree about who is where;
- state a session title or time that is not in `references/data/programme.json`; compute end times; state a "session" count;
- use urgency mechanics ("last chance", "only N seats", "book now"). Scarcity is factual and said once: "Limited to 200 attendees." A deadline is a date, never a pressure line;
- put a URL on a graphic that the user has not confirmed (the domain and the booking page are known; whether the site's staging gate is lifted is not) — use "Link in bio" until they say;
- mention a networking dinner, Turkey (workshop), or anything else `FACTS.md` lists as retired or contradicted;
- produce paid-ad formats (Google Ads, Meta Ads) — that is `wm-paid-ads`.

## Supported formats

| Format | Dimensions | Outputs |
|---|---|---|
| **Carousel** — Instagram / LinkedIn | 1080 × 1350 (4:5) | PNG per slide + PDF |
| **Carousel** — X / Facebook | 1080 × 1080 (1:1) | PNG per slide + PDF |
| **Single Post** | 1080 × 1350 (or 1080 × 1080) | PNG |
| **Story** | 1080 × 1920 (9:16) | PNG per frame |
| **LinkedIn Post** — landscape / square | 1200 × 627 / 1080 × 1080 | PNG |

Every job delivers the editable HTML (source of truth) plus the renders.

---

## Workflow

```
0. Freshness check        → are the bundled facts still the site's facts? which rate is in force today?
1. Understand the input   → what was given, which format, which photograph situation
2. Create the content     → adapt or write the copy, from confirmed facts only
3. Plan (+ approval when Claude authored the content)
4. Generate               → build the editable HTML, lint it (no render yet)
5. Open in browser        → live text edits, captured back into the HTML file
6. Render & review        → PNGs, scrim check, look at every slide; iterate until approved
7. Deliver                → PDF (carousels) + caption/alt-text file → hand-off notes → offer next steps
```

### Step 0 — Freshness check (every job, before anything is written)

The site changes under this skill: `PRODUCT.md` was written before the current day themes, cap, roster, prices and booking flow, and speakers were still being added to the site on 20 Oct. Two commands, both cheap:

```bash
python3 <SKILL_DIR>/scripts/facts.py freshness
python3 <SKILL_DIR>/scripts/sync_site_facts.py check "/Volumes/GCS - DISK 1T/GCS 2026/Github/gcs-wealth-migration-summit"   # when that repo is on this machine
```

- `freshness` prints what the hand-off must carry: facts older than a week, a rate tier ending within seven days, the event being over.
- `check` reports **DRIFT** when the site's speakers, programme, rates or hero facts no longer match the bundled data, and when `PRODUCT.md` / `DESIGN.md` have been replaced upstream. On drift: tell the user in one line, run `sync`, re-read the changed part of `FACTS.md`, then continue. If the site repo is not on this machine, say the facts are dated (the "As of" line in `FACTS.md`) and carry on.
- Read `references/FACTS.md` in full on the first job of a session. It is the shortest path to not repeating a retired fact.
- The site's repo is **read-only** for this skill.

### Step 1 — Understand the input

The user may give any combination of: a topic, a programme day, a speaker, complete text, a draft, a DOCX / Markdown file, a URL, and instructions (audience, objective, tone, CTA, slide count, format). Reading files: DOCX → `pandoc` if installed, else python-docx, else unzip `word/document.xml` and read the `<w:t>` runs; Markdown → read directly; URL → fetch and extract (if it fails, ask the user to paste).

**Infer before asking.** Only ask about what you genuinely cannot infer:

- **Format** — multi-point content → Carousel; one strong message → Single Post; teaser / date / a single fact → Story; one headline for the LinkedIn feed → LinkedIn Post. Ask once if truly ambiguous.
- **Platform** (carousels) — default Instagram / LinkedIn 4:5.
- **Language** — authored copy is **British English**; write English by default. Another language only on explicit request, and say that a translation is not client-approved copy.
- **Audience slice** — the site names four: global individuals & families · legal & tax counsel · private banking · industry and government (its lede adds advisors and family offices). Or prospective partners and sponsors. Pick the one the post speaks to; "everyone" is not a slice.
- **Date** — today's date decides the rate tier, the countdown and whether a deadline has passed. Don't assume it; read it (`facts.rate_on()`, `facts.days_to_go()`), and for a post scheduled for later, ask when it goes live.

#### Photograph — resolve only when the chosen layout needs one

`DESIGN.md`: photography is the material — blue-hour river, wet street, still water. But GCS owns **no** Lisbon / venue photography, and the page's own imagery is generated and on the client's replacement list. So, for any photo-led layout with no usable image, ask once, in the user's language:

> 🖼️ **Where should the image come from?**
> 1. I have a photograph (or the client supplied one) — I'll upload it.
> 2. Help me create one — a generated Lisbon-nocturne image or a prompt to take elsewhere.
> 3. No photograph — a typographic layout on the navy ground (a complete design in this system).
>
> Reply with the number or describe what you prefer.

Option 3 is always valid and often best. Text, ledger, entries, programme, speaker (initials) and register slides need no photograph. Do not silently replace a requested photo or read silence as a choice. For option 2 apply `references/design-system.md` → Imagery. Use any image the user already supplied; never ask twice.

#### Reference image gate — runs after the photograph gate

An image that is a **layout reference** (signals: "make something like this", "take inspiration from this", "use as reference", an image with no copy attached) activates **Reference Mode**:

1. Confirm: *"I'll use this as a layout reference — reading the structure, not the content or the branding."*
2. Describe in writing: zones and hierarchy · background type · masthead position · headline treatment · secondary elements · density.
3. Map it to an existing type in `slide-library.md`, or propose a **Custom layout**.
4. Show the proposal and wait for approval before writing HTML.
5. Never copy another brand's colours, logos or typefaces. `PRODUCT.md` sets the visual reference as a **craft and finish bar only** — its layout and its lime palette are ruled out. The output is the Summit, not a copy.
6. If the reference cannot be analysed, ask the user to describe what they want.

### Step 2 — Create the content

Understand the *purpose* and adapt to the format:

- **Carousel** — hook → one idea per slide → the programme at the darkest point → register. Typically 5–9 slides.
- **Single Post** — one headline, one supporting element, where to go next.
- **Story** — concise, high-impact; same types as the carousel on a 1080 × 1920 canvas.
- **LinkedIn Post** — headline only; the call to action belongs in the caption.

**Two modes — choose before touching the text:**

**A — You are authoring** (topic, brief or rough notes): write freely **within the confirmed facts**. Every claim must trace to `FACTS.md` / `references/data/` or text the user supplied. The programme is the argument: a specific session or sequence beats any adjective about exclusivity. `content-playbook.md` says which facts each kind of post may use.

**B — Ready-to-use content** (finished text, the site's own copy, a DOCX the user calls done): **preserve verbatim** — text, URLs, e-mail addresses, the source's spelling (the site itself writes "organized" and both "Marques" and "Marquês"; flag, don't fix). You may split a long block across slides (one idea per slide); do not rewrite, reorder into new prose, correct or add claims.

**Voice:** restrained, factual, institutional. No emoji, no exclamation marks, no superlatives, no hype. UK English in authored copy: *programme, organised, colour*. Residency and citizenship planning is part of a broader wealth strategy rather than an isolated legal decision. The call to action is **"Secure your place"** — a booking, which the site now takes payment for — not "Register your interest".

**Inherited GCS terms (still apply):** never "relocation firm", "passport shop", "passport scheme", "borderless living", "dream lifestyle" or "fallback option"; say "citizenship programme" / "residency programme", never "passport programme".

### Step 3 — Plan and approval

**A — Claude authored the content.** Present for approval before building:

```
📋 PLAN — [Carousel / Single Post / Story / LinkedIn Post]

Topic · Language · Platform · No. of slides · Photograph: [supplied / generated / none]
Goes live: [date] · Rate shown: [tier · price · true until — or "none"] · Countdown: [N days, valid <date> only — or "none"]

Slide 1 — cover · tone g-navy (photograph, .scrim-cover, as references/img/cover-reference.webp)
  Service line: …
  Headline: …
Slide 2 — programme (day one) · tone g-deep
  Stations: …
[…one block per slide with its ground (white / navy alternating, programme g-deep) and its layout in one line — zones, what carries the weight, photograph or none…]

Facts used: … (each traceable to a FACTS.md section / data file / user text)
To confirm with you: … (a URL, a speaker↔session pairing, the venue spelling — only what the post actually needs)
Approve, or tell me what to change.
```

Wait for an explicit go-ahead. Silence or a question is not approval.

**B — User gave ready content.** Skip approval: state the slide mapping in a sentence or two and generate. Fall back to A only if the content is too unstructured to order.

### Step 4 — Generate

1. Read `references/FACTS.md`, `references/PRODUCT.md`, `references/DESIGN.md`, `references/design-system.md`, `references/slide-library.md`, and `references/content-playbook.md` for the post type. Pull facts through `scripts/facts.py` (`speaker()`, `rate_on()`, `days_to_go()`, `programme()`, `find_session()`) — never type a price, time, title or role from memory.
2. **Bootstrap** (`references/rendering.md`): put `<SKILL_DIR>/scripts` on `sys.path`, then `from summit_assets import …` and `from summit_render import build_document, render, pngs_to_pdf`.
3. **Decide the layout of each slide yourself, from `DESIGN.md`** (the site's design system), the content of the slide and its place in the arc. `slide-library.md` is a vocabulary of proven compositions and markup to start from, not a menu: adapt, combine or compose a new layout when the content calls for it. **Use type classes and `var(--token)` only** — never a literal `font-size`, `font-family`, `rgba()`, hex colour or `box-shadow`.
4. Give each slide its ground: the cover is a photograph on navy; then alternate `g-white` and `g-navy`, the programme always `g-deep`, never two white slides in a row, the closing the opposite of the slide before it (`slide-library.md` → Alternating grounds). Masthead from `mast("dark"|"light")`, footer marks from `marks(...)` on the cover and the closing slide only.
5. Embed user/client photographs with `embed_image(path)`; never put an `https://` URL in `<img src>`. Write the HTML from Python — never a shell heredoc.
6. `build_document(slides, canvas, title)` → write the `.html`. **Do not render yet.**
7. **Lint:** `python3 <SKILL_DIR>/scripts/qa.py lint <deck>.html`. Fix every ERROR before continuing; read every WARN. Besides the design rules it checks the facts: every price is a published tier (and not an ended one), every `HH:MM` is on the site's programme, no agenda-only names, no retired facts, partner logos flagged. For HTML that was not built with `build_document` run `qa.py facts <file>.html` (fact check only).

### Step 5 — Open in browser for live edit

The generated `.html` is always opened for a visual check before anything is rasterised.

1. Open a **fresh** Browser pane tab (`tabs_create`, then `navigate`) — a reused tab can retain a stale DOM.
   - `file://` only works for small files; a real deck with embedded fonts and photographs is several MB and `navigate`/`preview_start` fail on it. Serve the output folder over local HTTP: `npx --yes http-server -p <port> -c-1 "<output dir>"` (background), then `navigate` to `http://127.0.0.1:<port>/<slug>.html`. Do not use Python's `http.server` — it fails on this repo's volume.
2. Via `javascript_tool`, make every text-bearing **leaf** editable, leaving structure untouched. The `.reflect` echo is excluded (it is a decorative copy of the cover headline):
   ```js
   document.querySelectorAll('[data-slide] *').forEach(el => {
     if (el.closest('.reflect')) return;
     const isLeafText = el.children.length === 0
       && el.textContent.trim().length > 0
       && !['IMG', 'SVG', 'STYLE', 'SCRIPT'].includes(el.tagName);
     if (isLeafText) el.setAttribute('contenteditable', 'true');
   });
   ```
   **Do not use `document.designMode = 'on'`** — it turns the page into one flowed surface and a retype can swallow a neighbour's closing tag.
3. Tell the user: *"The preview is open — click into any text to edit it directly. Say when you're done, or ask me for anything else (swap a photo, remove/reorder a slide, change a tone) and I'll edit the file directly."*
4. Do **not** capture `outerHTML` (megabytes of base64). Pull back only the editable text:
   ```js
   const edits = [];
   document.querySelectorAll('[contenteditable="true"]').forEach(el => edits.push({id: el.id || null, text: el.textContent}));
   JSON.stringify(edits, null, 2)
   ```
5. Diff against the text you wrote. Apply each change to the `.html` with the **Edit** tool (plain old → new replacement). If a cover headline changed, apply the same change to its `.reflect` copy. Sanity check: if an old text cannot be found verbatim, or a new text is empty where the old was not, stop and show the user.
6. Close the tab once the edits are applied; re-run `qa.py lint` (a retype can introduce an exclamation mark or a price).

### Step 6 — Render & review

1. `render()` each slide to PNG. **Do not assemble the PDF yet.**
2. For every slide with a photograph and text on it, measure the ground under the text: `python3 <SKILL_DIR>/scripts/qa.py scrim <deck>.html <slide#> x y w h` — it must stay under 0.04 relative luminance. Fix the scrim or the crop, not the threshold. **The cover is the one exception:** it follows the client's reference and is gated by contrast — add the text colour (`… x y w h white` or `gold`) and it must read ≥ 3:1 for the masthead, headline, service line and marks.
3. **Look at every PNG** (Read tool): fonts are Caladea (serif headings) and Archivo; masthead present; nothing clipped; no placeholder left; gold is spent on one active thing; the cover echo reads as a sliver, not a second headline.
4. Show the PNGs. Further changes come two ways: back to the browser (Step 5), or in chat — find the slide's `[data-slide="N"]` block and apply it with the **Edit** tool (never regenerate the whole file; that reverts approved edits), then `render()` again — it is idempotent.
5. Repeat. Only an explicit approval ("looks good", "aprovado", "pode finalizar", "ship it") ends the loop.

### Step 7 — Deliver

1. For carousels, assemble the PDF from the latest approved PNGs (`pngs_to_pdf`); name it after the title for LinkedIn.
2. **Write `<slug>_caption.md`** per `content-playbook.md` (caption, one alt-text line per slide, "before publishing" list), then `python3 <SKILL_DIR>/scripts/qa.py caption <slug>_caption.md <deck>.html` — fix every ERROR.
3. Confirm the files against the naming table below.
4. **Hand-off notes — say each that applies, in the reply:**
   - the rate tier shown, its price, and the date it stops being true — or that no price is shown;
   - a countdown figure and "valid on <date> only";
   - anything the user must confirm before publishing (URL, speaker↔session pair, partner logo clearance, venue spelling);
   - which source decided any fact on which the site's pages disagree (`FACTS.md` → Sources disagree);
   - any `facts.py freshness` / `sync_site_facts.py check` finding that was not resolved.
5. Offer: adjust a slide · adapt to another format (a Story of slide 1) · the next post in the series (`content-playbook.md`) · start a new piece.

---

## Layout quality — the bar

- **The programme is the argument.** If the post can name a session, name it.
- **One light per canvas.** Gold marks the one active thing: the service line, a day marker, the programme line, one ledger of figures, or one lit block. Not all at once. Never gold text on white.
- **Alternate the grounds.** Cover on a navy photograph, then white and navy in turn; the programme stays dark; the closing is the opposite of the slide before it. Gold is text only on navy; on white it is a mark.
- **Never overcrowd.** ≤ ~40 words of body, headline ≤ 12 words. Content grows → add a slide; never shrink type — the ramp is closed.
- **One anchor per slide.** A headline, a Display figure, or a plate.
- **No eyebrow above a heading.** The cover's service line and the programme's day marker are the only labels that sit there.
- **No boxes.** Hairlines, ruled entries and ruled tables. Paper is a white slide, or the register panel on a navy one — never a card on a white slide.
- **Vary the weight.** A carousel of six identical statement slides reads as generated: alternate statement, plate, ledger, entries, programme.

### Anti-generic checklist — redo the draft if any appear

- Three or more consecutive slides with identical structure (headline + paragraph).
- A generic label ("Key Point", "Did you know?").
- Two competing figures at the same weight on one slide.
- A photograph placed because a slide "needed" one.
- Any adjective carrying a claim the programme could carry instead.

## Custom layout

The default, not the exception: you choose the layout from `DESIGN.md` and the content. State each slide's layout in one line in the Step 3 plan (zones, what carries the weight, photograph or none) — the plan's approval is the go-ahead; a separate sketch is needed only for a composition far from the library or when Reference Mode maps to nothing. The invariants and the QA gate are in `slide-library.md` ("Custom layout"). Custom dimensions outside the supported list: confirm first, then scale padding and ramp proportionally.

## Outputs & file naming

Write to `/mnt/user-data/outputs/` when it exists (Claude.ai); otherwise `./output/<slug>/`. `slug` = topic in `snake_case`.

| Format | Files |
|---|---|
| Carousel | `<slug>.html` · `<slug>_slide_01.png` … `_NN.png` · `<slug>.pdf` · `<slug>_caption.md` |
| Single Post | `<slug>.html` · `<slug>.png` · `<slug>_caption.md` |
| Story — single frame | `<slug>_story.html` · `<slug>_story.png` · `<slug>_story_caption.md` |
| Story — multi-frame | `<slug>_story.html` · `<slug>_story_slide_01.png` … `_NN.png` · `<slug>_story_caption.md` |
| LinkedIn Post | `<slug>_linkedin.html` · `<slug>_linkedin.png` · `<slug>_linkedin_caption.md` |

A Story is single-file only when the whole message fits one frame; from two frames it is named like a carousel. The caption file's alt-text lines are numbered per slide / frame.

---

> **Reminder:** freshness check first · read `FACTS.md`, `PRODUCT.md` and `DESIGN.md` before the first line of HTML · facts from `facts.py` and the user, never from memory or from `PRODUCT.md`'s fact sections · price = the tier in force on the post date, or none · no speaker↔session pair, no partner logo, no URL without the user's yes · type classes and tokens, never literals · lint before the browser, scrim-check before the render, look at every PNG · the last slide is the "Secure your place" slide · every job ships a caption with alt text · only an explicit approval ends the loop.
