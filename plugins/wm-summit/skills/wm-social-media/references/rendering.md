# Rendering pipeline — editable HTML → lint → PNG / PDF

The deliverable HTML is the **source of truth**: one standalone file with fonts, the token sheet, the base CSS, logos and photographs embedded, one `<div data-slide>` per slide. PNGs and the PDF are screenshots of those divs, so anyone can edit the HTML and re-render.

**Review loop (SKILL.md Steps 5–6):** the `.html` is opened in the Browser pane for live text edits **before** `render()` is ever called. After that, `render()` runs again whenever the user asks for a change — it is idempotent (reloads the HTML, overwrites the PNGs). Between calls the `.html` is the only thing Claude edits: apply changes with the **Edit** tool on the existing slide markup. Never rebuild the deck from scratch mid-review; that discards approved edits. Assemble the PDF once, after final approval.

## Dependencies

```bash
pip3 install playwright pillow beautifulsoup4 lxml --break-system-packages -q
python3 -m playwright install chromium
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(args=['--no-sandbox']); b.close(); p.stop(); print('OK')"
```

## Bootstrap — top of every generation script

```python
import sys, asyncio
from pathlib import Path

SKILL_DIR = Path("<absolute path of the folder you read SKILL.md from>")
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from summit_assets import (
    mast, marks,    # masthead (event logo) and footer marks (GCS + CNN Portugal), "dark" or "light" ground
    asset_uri,      # any bundled asset by key, e.g. asset_uri("photo.bridge")
    embed_image,    # user / client photograph -> data: URI
    flag_uri,       # country flag — the one network call
)
from summit_render import build_document, render, pngs_to_pdf, CANVASES
import facts        # confirmed facts: speaker(), rate_on(), days_to_go(), programme(), find_session()
```

`FONTS_CSS`, `TOKENS_CSS` and `BASE_CSS` are inlined by `build_document()` — you do not paste them yourself. The palette inside `TOKENS_CSS` is parsed from `references/DESIGN.md`.

Verify the bundle (also the first thing to run after copying the skill to another machine):

```bash
python3 "<SKILL_DIR>/scripts/summit_assets.py"
```

It lists fonts and marks, prints the palette it read, and checks the contrast of every text/ground pair.

## Build

```python
slides = [
    (cover_html,     "g-navy"),    # photograph + .scrim-cover
    (statement_html, "g-white"),   # white and navy alternate
    (programme_html, "g-deep"),    # always dark
    (register_html,  "g-white"),   # the opposite of the slide before it
]
html = build_document(slides, canvas="carousel-4x5", title="Summit announcement")
Path(out_dir, f"{slug}.html").write_text(html, encoding="utf-8")   # always from Python
```

`canvas` is one of `carousel-4x5`, `carousel-1x1`, `post`, `story`, `linkedin-landscape`, `linkedin-square` (see `CANVASES`). Each slide item is `inner_html` or `(inner_html, "g-…")`; the tone class sets `--ground`.

⚠️ **Always write HTML with Python** (`Path.write_text`). A shell heredoc silently corrupts base64 through `$` and backtick interpolation.

⚠️ **Playwright renders from `file://`; an external image URL is silently ignored.** Never put `https://` in `<img src>`. Photographs go through `embed_image()`.

## Lint — before the browser, again after every edit

```bash
python3 "<SKILL_DIR>/scripts/qa.py" lint "<deck>.html"
```

ERRORs block delivery. It enforces the checkable rules of `DESIGN.md`: no literal `font-size` / `font-family` / `rgba()` / hex in slide markup, shadows only from light-source tokens, square corners, no coloured side-stripes, no italic, no external images, masthead on every slide, one lit gold block, one white panel and no gold text on it, no eyebrow above a heading, no exclamation marks, no emoji, no urgency phrasing, and no residue of the old GCS identity. It also checks the facts against `references/data/` (see `FACTS.md`): a price that is not a published tier or whose tier has ended, a time that is not on the programme, an agenda-only name, a retired fact (old day themes, a 150–200 cap, a dinner). WARNs (long headlines or bodies, the rate tier in force, a partner logo, an unfound session title, US spelling) are judgement calls. After the caption is written: `qa.py caption <slug>_caption.md <deck>.html`. For HTML not built with `build_document`, run `qa.py facts <file>.html`.

## Render

```python
paths = asyncio.run(render(str(html_path.resolve()), out_dir, slug, *CANVASES["carousel-4x5"][:2]))
# prefix naming: single slide -> <slug>.png ; several -> <slug>_slide_NN.png
```

`render()` launches Chromium with `--no-sandbox --disable-setuid-sandbox` (required in this environment — never omit), waits for fonts, screenshots each `[data-slide]`. For a Story use `slug + "_story"` as the prefix; for a LinkedIn post, `slug + "_linkedin"`.

```python
pdf = pngs_to_pdf(paths, f"{out_dir}/{slug}.pdf")   # carousels only, after approval
```

## Check the ground under text

For every slide that has a photograph **and** text:

```bash
python3 "<SKILL_DIR>/scripts/qa.py" scrim "<deck>.html" <slide#> <x> <y> <w> <h>
```

It re-renders the slide with all type hidden and measures the ground in that box: relative luminance p95 must stay under **0.04**. (Measuring the finished PNG would count the white glyphs themselves.) If it fails, deepen the scrim, move the text to the scrimmed side, add `<div class="scrim-flat"></div>`, or choose a darker crop of the photograph — never lighten the threshold. For an image that already has no text on it: `qa.py scrim-png <png> x y w h`.

## Look at the PNGs

Open every rendered PNG before delivering. Check: headings are Caladea serif and reading text Archivo (system fonts mean the bootstrap or `assets/` is broken — run the self-check, do not redraw anything); the masthead lamp and wordmark are there; nothing is clipped; no `{PLACEHOLDER}` survived; the cover's echo is a sliver; gold appears on one active thing; the GCS mark is the white one on a dark ground.

## Flags (network)

```python
FLAG_PT = flag_uri("pt")   # also "it", "gr", "mt"; "gb" is mapped to uk upstream
```

1200×800 PNGs from `msikma/country-flags`, rendered as rectangles by `.flag` (54×36). A missing territory 404s — tell the user and show the name without a flag; never source one elsewhere.

## Per-format checklist

| Format | Canvas key | Deliverables |
|---|---|---|
| Carousel IG/LinkedIn | `carousel-4x5` | `<slug>.html`, `<slug>_slide_NN.png` ×N, `<slug>.pdf` |
| Carousel X/FB | `carousel-1x1` | same |
| Single Post | `post` | `<slug>.html`, `<slug>.png` |
| Story — single frame | `story` | `<slug>_story.html`, `<slug>_story.png` |
| Story — multi-frame | `story` | `<slug>_story.html`, `<slug>_story_slide_NN.png` ×N |
| LinkedIn Post | `linkedin-landscape` / `linkedin-square` | `<slug>_linkedin.html`, `<slug>_linkedin.png` |

## Running outside the original machine

| Works offline | Needs internet |
|---|---|
| Fonts, GCS marks, tokens, every layout, lint, scrim check, render, PDF | `flag_uri()` only |

There are no icons to fetch: Material Symbols are not part of this system.
