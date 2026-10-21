---
name: wm-assets
description: "Finds and sends existing Wealth and Migration Summit 2026 assets (Lisbon, 5–6 Nov 2026, convened by Global Citizen Solutions) from a bundled library: the W&M logos and lockups (horizontal, stacked, vertical, symbol; white or navy; SVG + PNG), the Global Citizen Solutions and CNN Portugal marks, partner logos, the 28 speakers' portraits, the share card, the hero, venue, Lisbon photographs, plates and textures and the brand fonts (Caladea, Archivo). Picks the colourway that fits the user's background, converts WebP to JPG/PNG or resizes on request, zips big sets, and flags what is not cleared or not confirmed. Use whenever someone asks for, or needs, a file that already exists — 'me manda o logo', 'preciso da foto do speaker', 'logo branco em SVG', 'imagem de partilha', 'fontes da marca', 'send me the logo', 'all speaker photos', 'where is the …' — even if they never say 'asset'. Not for making anything new: carousels and posts (wm-social-media), banners (wm-web-banners), decks (wm-presentations), letterhead (wm-letterhead)."
allowed-tools: Bash(*), Read, AskUserQuestion, SendUserFile
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "Sync with site repo at 6725cff: 28 speakers (added José Carlos Reis, John McNertney), American Club partner logo added (14 partners total), IMGW promo code updated to WMSIMGLOBALWEALTH25, 4 new partner booking pages. catalog.json and site_map updated."
---

# Assets — Wealth & Migration Summit 2026

One job: someone asks for **a file the Summit already has** — a logo, a speaker's portrait, the share card, the fonts — you find it in the library and **send it**. Retrieval, not design. `scripts/assets.py` does the lookup, the copy and the conversion; your work is picking the right file for the person's use and telling them what they need to know about it.

Reply in the user's language (Portuguese in, Portuguese out). File names stay as they are.

## What is in the library

Everything is inside this folder (`<SKILL_DIR>` = the folder that holds this `SKILL.md`; `${CLAUDE_SKILL_DIR}` when loaded from the plugin). `references/catalog.json` is the source of truth; `assets.py list` prints it.

| Group (`get group:…`) | What | Formats |
|---|---|---|
| `wm-logos` (7) | W&M lockups: **horizontal** (the masthead), **default** (stacked, left-aligned), **vertical** (centred), each in white type for dark grounds and navy type for light ones, plus the gold **symbol** | SVG + PNG |
| `gcs-logos` (6) | Global Citizen Solutions: primary (symbol + name), one-line wordmark, symbol; white and blue | PNG, mostly + SVG |
| `cnn-portugal-logos` (4) | CNN Portugal: white, red, black, square badge | PNG |
| `partner-logos` (14) | The nine on the site's partner strip + American Club of Lisbon, GFPI, IMGlobalWealth, RedBridge, Trusted Advisor (their own booking pages) | PNG / SVG |
| `speakers` (28) | One 480×480 headshot per speaker on the site's roster, in the site's order | WebP / JPG |
| `imagery` (10) | Share card (1200×630), hero (the red bridge at sunset), EPIC SANA at night, nocturne texture, three darkened Lisbon plates, three Lisbon stock photographs (sunset rooftops, Vasco da Gama Bridge, Arco da Rua Augusta; 2400 px) | WebP / JPG |
| `fonts` (1) | Caladea + Archivo with their OFL licences | TTF + TXT |

Bundles: `bundle:logos` (the three Summit logo groups, no partners) and `bundle:brand-kit` (logos + fonts). A snapshot of 21 Oct 2026; see "Keeping it current".

## Workflow

```
1. Resolve  → which catalogue entry?        assets.py list | find | speaker
2. Choose   → colourway, format, size       infer; ask only if the answer changes the file
3. Get      → copy / convert to outputs     assets.py get …
4. Send     → the files themselves          SendUserFile, else the paths
5. Say      → one line per file + the NOTEs
```

### 1 — Resolve

```bash
python3 <SKILL_DIR>/scripts/assets.py list                   # whole catalogue, ~85 lines: id · ground · formats · title
python3 <SKILL_DIR>/scripts/assets.py find logo branco       # filter by any words, Portuguese or English
python3 <SKILL_DIR>/scripts/assets.py speaker nuno           # roster lookup (accent- and case-insensitive)
```

Read `list` once per session; after that `find` is enough. The **ground** column says where a file works: `dark` = navy or other dark backgrounds, `light` = white or light ones, `any` = both.

### 2 — Choose, without over-asking

Send the pair when you don't know, rather than ask. The usual defaults:

| The request | Send |
|---|---|
| "the Summit logo", background not said | `wm.horizontal.white` **and** `wm.horizontal.blue`, SVG + PNG — say which is for dark and which for light |
| background is said ("slide azul", "fundo branco") | the one whose ground fits: dark → `.white`, light → `.blue` |
| "logo empilhado / quadrado / vertical" | `wm.default.*` (left-aligned) or `wm.vertical.*` (centred) |
| "the symbol / monogram / icon" | `wm.symbol` (gold, any ground); for GCS `gcs.symbol.*` |
| "the GCS logo" | `gcs.primary.*` (symbol + name); one-line version only if they say wordmark / horizontal / small |
| "the CNN Portugal logo" | `cnn.white` on dark, `cnn.red` on light |
| "all the logos" / "kit de marca" | `bundle:logos` / `bundle:brand-kit` (arrives as one zip) |
| a speaker's photo | `get "<name>"` — JPG by default; `--format png` if asked |
| "all the speakers" | `group:speakers` (one zip) |
| the share card / link-preview image | `img.og-share` |
| "a photo of Lisbon / a background" | offer what `imagery` has (hero, three photographs, three dark plates, texture) — send the one that fits, or all. |
| the fonts | `fonts.brand` (zip with licences) |

**Format.** PowerPoint, Word, email and Canva want **PNG**; print and design want **SVG** — when both exist send both. WebP is not opened everywhere, so WebP photographs go out as JPG unless `--format keep`. A size ("1000 px wide") is `--width N` (never upscales a raster; an SVG goes to PNG at that width). JPG of a transparent logo is flattened on white (`--bg` to change) and the NOTE says so — suggest PNG.

**When to ask** (one short question, `AskUserQuestion` if available): the name matches several speakers ("Nuno" → Sanches or Serafim; `assets.py speaker` shows them), or two entries differ in a way the message doesn't settle and the file would be wrong for one of them. Otherwise decide.

### 3 — Get

```bash
python3 <SKILL_DIR>/scripts/assets.py get wm.horizontal.white wm.horizontal.blue
python3 <SKILL_DIR>/scripts/assets.py get "patricia casaburi" --format png
python3 <SKILL_DIR>/scripts/assets.py get gcs.primary.white --format png --width 1200
python3 <SKILL_DIR>/scripts/assets.py get bundle:brand-kit --zip wm-brand-kit
```

Files go to `/mnt/user-data/outputs/` when it exists, otherwise `./output/assets/` (`--dest` overrides). More than 8 files become one zip. The output is `FILE` lines (absolute paths) and, when they apply, `NOTE`, `DRAFT` and `ROLE` lines — those are what you relay. An unknown id or name exits non-zero with the nearest candidates; never guess past it.

SVG → PNG needs `playwright` (+ Chromium); everything else needs only Python 3 and Pillow.

### 4 — Send

Send the files themselves, not a description of them: `SendUserFile` with the `FILE` paths (`display: "render"` for images, `"attach"` for zips and fonts). Where that tool does not exist, they are in the outputs folder — give the path or link the platform provides.

### 5 — Say

Short. Per file or pair: what it is and where it works ("horizontal lockup, white type — for dark backgrounds"). Then only the notes that apply:

- **Speaker:** name and role exactly as `ROLE` gives them (the site's card); 480×480 px, fine for slides and social, small for print.
- **Partner logo:** sent as a file; the site does not say what the partner is to the Summit.
- **Imagery:** the site's own docs call its page imagery generated and on the client's replacement list — not GCS-owned photography. The dark plates have no recorded source or licence; the three Lisbon photographs are licensed stock — GCS has the rights, but they are not GCS-owned photography.
- **JPG / resize:** what was flattened or not upscaled.

Then stop. Offer the other colourway or format only if the request left it open.

## What this skill will not do

- **Alter a file.** No recolouring, tinting, cropping, stretching, putting a logo on a background, redrawing or "cleaning up". Only the container format and the pixel width change. A version that is not in the library (an all-black or all-white W&M, an outline, a horizontal GCS with the symbol) → say it isn't there, send the closest, and say that a new version is the brand owner's to supply.
- **Make an asset that doesn't exist** — no generated logos, portraits or photographs. If it isn't in the library, say so; offer the nearest entry. If the site repo is on this machine (`/Volumes/GCS - DISK 1T/GCS 2026/Github/gcs-wealth-migration-summit`, read-only), `assets/img/` there may hold something newer — copy it as is and say it comes from the site, outside the library snapshot.
- **Send a portrait for, or name, someone who is not on the 28-speaker roster** (`assets.py speaker` says "not on the roster"). The older agenda page lists people with no card on the site; they are not speakers here. Never generate or retouch a portrait, never tie a speaker to a session, and don't send a bio — bios live in `wm-social-media`.
- **Give a partner or media mark a role.** The GCS mark stands alone — nothing written above, beside or over it. CNN Portugal is shown beside GCS in the site's hero; no "official partner" or "in partnership with" wording. The other logos go on a creative only if the user names them for that piece and confirms they are cleared.
- **Send fonts without their licences** — the SIL OFL texts travel with them.
- **Answer facts** — dates, prices, programme, who speaks. That is `wm-social-media`'s `FACTS.md`; this skill hands over files, and the programme PDF is not one of them.

A request that needs something new — "a post with Patricia's photo", "a banner with the logo" — is not this skill: `wm-social-media`, `wm-web-banners`, `wm-presentations` or `wm-letterhead` already carry these assets and the layout rules.

## Keeping it current

The library is a snapshot of **21 Oct 2026** (site repo HEAD `f7ed2f2`; speakers as of `1823ec1`). When the site changes:

```bash
python3 <SKILL_DIR>/scripts/assets.py check                                   # library intact: files ↔ catalogue
python3 <SKILL_DIR>/scripts/assets.py check --site "<path to gcs-wealth-migration-summit>"   # DRIFT, GONE, NEW — writes nothing
python3 <SKILL_DIR>/scripts/assets.py check --site "<path>" --update          # copy changed files over the library
```

`NEW` files (a new partner logo, a new speaker) are added by hand: copy into the right `assets/` folder with a clean kebab-case name, then add an entry (`id`, `title`, `group`, `files`, `ground`, `aliases` in Portuguese and English, `caution`) to `references/catalog.json`, or the speaker to `references/data/speakers.json` (a trimmed copy of `wm-social-media`'s roster: name, role, slug). Run `check` until it is quiet, then bump `version` in the plugin manifest and the marketplace and run `claude plugin validate .`.

> **Reminder:** find the entry, pick the colourway for the user's background (both when unknown), send the files, say what they are. Never alter a logo; no portrait without a roster entry; no role for a partner.
