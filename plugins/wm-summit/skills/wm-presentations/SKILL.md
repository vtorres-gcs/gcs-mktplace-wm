---
name: wm-presentations
description: "Builds editable PowerPoint (.pptx) presentations for the Wealth and Migration Summit 2026 (Lisbon, 5–6 November 2026, convened by Global Citizen Solutions) in its own 'Lisbon Nocturne' identity (dark-blue ground with white slides interleaved, amber light, Caladea-style serif over a grotesk, hairlines not boxes, the real W&M, GCS and CNN Portugal marks on the cover and back cover). Give it a purpose and an audience — a Summit overview, the programme, the speaker line-up, a partner briefing, a booking/rates deck, a welcome slide, an internal briefing — and it plans the storyline, pulls every fact (the timed two-day programme, the 28-speaker roster with portraits, the three published rate tiers, the 200-attendee cap) verbatim from the site's confirmed data instead of retyping it, builds a real theme-driven deck (title placeholders, layouts, speaker notes, alt text), lints the facts and layout (retired facts, urgency wording, prices not in force, counts, overflow measured with the real fonts, 12pt floor, AA contrast), renders PNG previews to look at, and hands off what the user must confirm. Use whenever the user mentions a Summit presentation, deck, slides, apresentação, slides do Summit, PowerPoint or .pptx for this event — a pitch, a pre-read, a sponsor or partner deck, an agenda deck, a speaker deck, a team briefing — even if they never say 'pptx'. Not for editing an existing .pptx someone else made (use the general pptx skill), not for social carousels or web banners (use wm-social-media / w&m-web-banners), not for general GCS decks."
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "Sync with site repo at 6725cff: 28 speakers (added José Carlos Reis, John McNertney), FACTS.md + data JSONs + PRODUCT.md + DESIGN.md refreshed, new speaker photos added, partner booking pages documented."
---

# Presentations — Wealth & Migration Summit 2026

One job: turn **a purpose and an audience** into a finished, **editable** `.pptx` in the Summit's own identity, from confirmed facts only. `scripts/wm_deck.py` builds the deck from a JSON spec, `scripts/check_deck.py` lints and renders it; your work is the questions, the storyline, the spec, and the judgement about what the slides look like.

Reply in the user's language (Portuguese in, Portuguese out). The words **on the slides** are English with British spelling, because the Summit's copy is — unless the user asks for another language; then set `meta.lang` (`pt-PT`), say that a translation is not client-approved copy, and keep every fact pulled from the data.

## Source of truth

| File | What it is |
|---|---|
| `references/FACTS.md` | Every fact a slide may state — dates, programme, the 200 cap, 28 speakers, rate tiers, what is included, what is **retired** — dated, with its site source. **Read it in full on the first deck of a session.** It beats `PRODUCT.md` wherever they disagree |
| `references/deck-design.md` | How the site's design system lands on a 16:9 slide: tones, the closed type ramp at slide scale, fonts, file anatomy, and **the spec for every slide type**. Read before writing a spec |
| `references/deck-recipes.md` | What to build for which request — overview, programme, line-up, partner briefing, welcome, booking, internal — with the slide sequence for each |
| `references/PRODUCT.md`, `references/DESIGN.md` | Verbatim copies of the site's own files: voice, positioning, what must never be invented; palette, type ramp, named rules. The palette is parsed from `DESIGN.md` at build time |
| `references/data/*.json` | `programme.json` (from `programme/build.py`: start and end times, formats, speakers), `speakers.json`, `rates.json`, `site.json` — what the builder pulls and the linter checks against; `programme_index.json` is the home page's different schedule, kept for comparison only |
| `assets/` | Fonts (Caladea, Archivo + licences), the W&M and GCS marks as PNG, three photographs (hero, venue, night texture), 28 speaker portraits. Use as supplied; never recolour or redraw |
| `templates/summit-overview.json` | A complete 19-slide spec to copy from |

Everything is inside this folder; copy it alone to any machine with Python 3.9+, `python-pptx`, `Pillow`, `lxml` (and LibreOffice + `pdftoppm` for previews). The site's repo (`gcs-wealth-migration-summit`) is read-only for this skill; `scripts/sync_site_facts.py check <site-repo>` shows whether the bundled facts have drifted.

## Workflow

```
1. Freshness     → facts.py freshness · as-of date
2. Ask           → purpose · audience · how long · (only what is missing)
3. Plan          → purpose sentence + slide list, shown to the user
4. Write the spec→ pulls, not retyping
5. Build + lint  → wm_deck.py (runs check_deck.py lint)
6. Render, LOOK  → check_deck.py render · open every PNG
7. Hand off      → files, as-of tier, what to confirm
```

### 1 — Freshness

```bash
python3 scripts/facts.py freshness      # stale facts, rate about to change, event over
python3 scripts/facts.py rate           # the tier in force today
```

The deck's **as-of date** is today unless the user says the deck is for a later date (`--as-of 2026-11-03`). It decides which rate tier is marked current. Everything here expires after **6 Nov 2026**: afterwards, no recap deck without facts the user supplies.

### 2 — Ask

Ask in the user's language, as one `AskUserQuestion` call when it is available (otherwise plain chat), and only what the message does not already answer:

1. **Purpose and audience** — what the deck must make happen (a booking, a partner conversation, a decision about which sessions to attend) and who is in front of it. This picks the recipe.
2. **Length / use** — live pitch (≈ 1.5–2 min per slide), or a pre-read that must carry itself.
3. **Content the site does not have** — only for a partner or internal deck: the offer, the targets, the owners. If the user has none, say the offer slides are pending; do not fill them.

Do not ask about colours, fonts or layout — they are fixed. Do not ask about copy the site already supplies.

### 3 — Plan

Write the deck's purpose in one sentence, then the slide list (type + the one message of each) from `deck-recipes.md`, and show it. Wait for a go-ahead on anything custom; for a standard recipe, state the plan in two lines and build. The storyline rules that matter: the programme is the argument; vary the weight slide to slide; scarcity is the number 200, never urgency; the last slide is the "Secure your place" slide (or the partner route the user confirms).

### 4 — Write the spec

Copy `templates/summit-overview.json` or write a spec per `deck-design.md`. Save it next to the output as `<slug>.spec.json` so the deck can be rebuilt.

- **Pull, don't retype.** `@site.headline`, `@site.lede`, `{"auto": "speakers"}`, `programme` slides by `day`/`track`, `speakers` by name, `rates` — these come from the data, so a time, a price or a name cannot drift. Hand-typed text is for the user's own content and for headlines you write inside the confirmed facts.
- **Speakers:** the `speakers` / `speaker` slides take only names on the 28-person roster (`python3 scripts/facts.py speakers`); the builder refuses an unknown name. Programme rows carry the agenda's own speaker lines (`Name, Org (Role)`, *to be announced* kept as such) — never a pairing you invent.
- **Prices:** only through a `rates` slide, or — in one line of copy — the single tier in force on the as-of date. Never an invented price; never "from €…" unless that tier is in force.
- **CTA:** "Secure your place" (a booking). Not "Register your interest". It links only when `meta.confirmed` has `"url"`.
- **Logos:** the cover and the back cover carry the W&M horizontal lockup top-left and, at the foot, left-aligned, the white **Global Citizen Solutions and CNN Portugal** marks side by side (both are always on a dark ground; on any white ground the pair is the GCS **primary blue** + the **red** CNN Portugal `Float Final`) — the pair the site hero shows, as on the social cover (the user's decision; `"marks"` can drop one). The GCS mark stands alone: no "Convened by", nothing beside or over it. Any other partner logo needs the user's yes, and there is no partner logo wall — the site does not say what each partner is.
- **Ground:** the cover and the **back cover** (the `closing` slide) are always **dark blue**. Between them, white slides may be interleaved with the night ones — set `"tone": "paper"` on a slide, or `"meta": {"alternate": true}` for an automatic night/white rhythm. White suits reading slides (rates, workshops, roster, figures, long statements); keep photographs and the main-stage timeline dark. Gold is never text on white — the builder switches it to navy.
- **Photographs:** the three bundled ones are generated imagery on the client's replacement list; they set mood, they are not evidence of the venue. A user-supplied photo goes through `image` with an `image_alt`.
- **Notes:** put the talk track in `"notes"` when the deck will be presented live.

### 5 — Build and lint

```bash
python3 scripts/wm_deck.py output/<slug>/<slug>.spec.json output/<slug>/<slug>.pptx --as-of YYYY-MM-DD
```

The build prints layout warnings (a title past three lines, a stack running into the footer), then runs `check_deck.py lint` on the saved file. **Fix every ERROR** by changing the spec — cut words, split the slide, remove the claim — not by editing the lint. WARNs go in the hand-off. Fonts default to `office` (Cambria + Arial: opens correctly on any machine, and Caladea is Cambria's metric twin so line breaks match the brand); `--fonts brand` only when the user's machine has Caladea and Archivo installed.

### 6 — Render and look

```bash
python3 scripts/check_deck.py render output/<slug>/<slug>.pptx output/<slug>/preview
```

This writes `slide-N.png` per slide and `contact.png` (every slide on one sheet). **Open `contact.png`, then every slide that is dense or new** — after reading the spec you see what you expect, not what rendered. Look for:

- text colliding with a photo, a rule or the footer; a heading that wrapped to a fourth line and pushed into its body;
- a programme page left nearly empty, or a speaker row with a role cut short;
- one gold light per slide, no gold text on a light ground;
- the portrait crop (faces, not foreheads); the scrim over the cover photo keeps the headline legible;
- the same title position on slides of the same type.

Fix by editing the spec and rebuilding — the build is idempotent. If the user has already edited the `.pptx` by hand in PowerPoint, **do not rebuild over it**: apply the change to the file (python-pptx, or the general pptx skill) and re-run `lint`.

### 7 — Hand off

Say, in the reply, each that applies:

- the files: `<slug>.pptx` (the deck), `<slug>.spec.json` (to rebuild), `preview/contact.png`;
- the **rate tier marked current**, its price and the date it stops being true — or that no price is shown;
- anything the user must confirm before it is shown outside GCS: the booking URL (the site sat behind a staging password), the partner e-mail, the venue spelling (the site writes both "Marques" and "Marquês" — the deck follows the site verbatim where it pulls, so a mix is possible), the three photographs being placeholders;
- **if the deck shows the programme:** that it follows `programme/build.py` / `agenda.html` (the user's choice of 20 Oct 2026) and that the home page differs — the site's own `THEMES.md` flags this as an open editorial question; plus the build's deck-level warnings: agenda names not on the roster, "to be announced" slots, and the Day Two overlaps;
- the font mode, and that the preview was rendered with Caladea standing in for Cambria;
- what the lint cannot check: any figure or claim the user supplied;
- unresolved `freshness` / `sync_site_facts.py check` findings, and the 6 Nov 2026 expiry.

Then offer: adjust a slide · a shorter live version · the same deck for another audience · a Portuguese version (as an unapproved translation).

## Quality bar

- **The programme is the argument.** A specific session, name or time outranks any adjective.
- **One light per slide; one message per slide.** ≤ ~40 words of body, headline ≤ 12 words and ≤ 3 lines. Content grows → add a slide; never shrink type (the floor is 12pt).
- **No boxes, no eyebrows, no decorative bars.** Hairlines and ruled columns; the call-to-action is the only filled block.
- **Editable by someone else.** Real titles, theme fonts and colours, named shapes, notes in the notes pane. That is why the deck is built from layouts and placeholders rather than painted slide by slide.

### Redo the draft if any of these appear

- Three or more consecutive slides with identical structure (headline + paragraph).
- Any adjective carrying a claim the programme could carry instead.
- A price, time, count or name that is not in `references/data/` or in the user's own words.
- A photograph placed because a slide "needed one".
- A partner logo, a sponsor tier, a testimonial or a past-edition figure.

## Outputs & file naming

Write to `/mnt/user-data/outputs/` when it exists (Claude.ai); otherwise `./output/<slug>/` (`slug` = topic in `snake_case`).

| File | What |
|---|---|
| `<slug>.pptx` | the deck |
| `<slug>.spec.json` | the spec that rebuilds it |
| `preview/contact.png`, `preview/slide-N.png`, `preview/<slug>.pdf` | the render |

---

> **Reminder:** freshness first · read `FACTS.md` and `deck-design.md` before writing a spec · pull facts, never retype them · price = the tier in force on the as-of date, or none · no speaker off the roster, no speaker↔session pair, no partner logo, no URL without the user's yes · type roles and tones, never a literal size or colour · build, then lint, then look at every PNG · the last slide is the dark-blue back cover with "Secure your place" · only an explicit approval ends the loop.
