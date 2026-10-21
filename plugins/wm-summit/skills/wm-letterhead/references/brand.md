# Letterhead — brand facts, geometry and gaps

Read the site repo's own files before changing anything here (`gcs-wealth-migration-summit`, read-only for this skill): `CLAUDE.md`, `PRODUCT.md`, `DESIGN.md`, `ONBOARDING.md`, `HUBSPOT.md`, `content/` (copy deck), `programme/` (including `build.py`'s A4 programme PDF, the site's only A4 document), `references/`, and `index.html` / `agenda.html`. Facts below were read at site commit `ab1fe08` (20 Oct 2026).

## Facts the letterhead may state

| What | Value | Where it comes from |
|---|---|---|
| Event title (footer, left) | **Wealth and Migration Summit 2026** | `PRODUCT.md` (page title); footer of `index.html` and the copy deck ("© 2026 Wealth and Migration Summit · Global Citizen Solutions") |
| Website (footer, right) | **wealthandmigrationsummit.com**, linked to `https://wealthandmigrationsummit.com` | domain in the site's share metadata (`og:image`, `index.html`); the user asked for the site to be printed |
| Convened by | Global Citizen Solutions (the GCS mark in the footer) | `PRODUCT.md`, site footer |
| Dates / place, if a letter needs them | 5–6 November 2026 · Lisbon · EPIC SANA Marques Hotel | `PRODUCT.md`; the site spells the venue both *Marques* and *Marquês* — use what the user gives |
| Cap, if a letter needs it | "Limited to 200 attendees" (site); `PRODUCT.md` still says 150–200 — that is the older page | the banner and social skills carry the full fact sheet (`wm-web-banners/references/FACTS.md`) |

A letter's own text — recipient, subject, body, signatory — always comes from the user. This skill never writes a name, role, price or claim into a letter.

## Palette (binding — `PRODUCT.md`, `DESIGN.md`)

| Token | Hex | Use on the letterhead |
|---|---|---|
| Night Navy | `#121B31` | all text; the Summit logo's wordmark |
| Transit Gold | `#C2A358` | the header hairline and the logo's symbol only. **Never text on white** (2.6:1 fails AA) |
| Dawn Mist | `#C8CCD7` | the footer hairline |
| Mist dim | `#636B7C` | the website line (5.5:1 on white — the value `HUBSPOT.md` uses for quiet text on white) |
| GCS blue | `#000957` | inside the official GCS mark; never re-coloured to the Summit navy |

## Logos (use as supplied — never recolour, redraw or add words around them)

| File (`assets/logos/`) | Source | Used for |
|---|---|---|
| `wm-horizontal-blue.svg` → `.png` | `assets/logos/w&m-horizontal blue.svg` in the marketplace repo (the site's masthead lockup, blue wordmark + gold symbol) | header, 80 mm wide |
| `GCS-Secondary-Blue.svg` → `.png` | Global Citizen Solutions' **official one-line lockup** (symbol + wordmark) in GCS blue, from the GCS brand package (`02_LOGOS/svg/`; the same file ships in the gcs-word plugin's `ds/assets/logos/`). The site's dark footer uses the stacked *Primary* lockup (`GCS-Primary-White`); on a one-line footer row the Secondary is the right sibling. The user chose it for the letterhead on 2026-10-21, by exception to the white-ground pair (GCS Primary Blue + red CNN Portugal) the other Summit skills use | footer centre, 46 mm wide (2.9 mm tall) |

The white GCS and W&M files are for navy grounds; a letterhead is white paper, so they stay out. Do not recolour the white PNGs to make a blue one — the official blue exists (the test runs without this skill did exactly that, in the Summit navy, and the mark no longer matched GCS blue). `scripts/prepare_logos.py` rebuilds the PNGs from the SVGs (needs `cairosvg`); the PNGs are shipped, so a normal build needs nothing extra.

## Type

The site sets headings in **Caladea** and reading text in **Archivo** (`DESIGN.md`). Neither ships with Office, so the default is the pairing the presentations skill already uses: **Cambria** (Caladea is its metric-compatible twin) and **Arial**. `"fonts": "brand"` writes Caladea + Archivo **and embeds them in the file** (`assets/fonts/`, both OFL; `embed_fonts()` obfuscates them as Word does and flags `embedTrueTypeFonts`). Only the Regular weight is embedded, so bold is synthesised. Word for Windows and Mac honour embedded fonts; Word Online, Google Docs, phone viewers and some PDF exporters ignore them and fall back to a serif/sans — that is why Cambria + Arial stays the default. Cost: ~210 KB more per file.

- Footer title: a **label** — uppercase, 6.5 pt, tracked 0.16em (`DESIGN.md`: uppercase belongs to labels only, always at 0.16em). The site's own A4 programme PDF footer is 6.5 pt too.
- Footer website: 7.5 pt, Mist dim, a live link, no underline.
- Letter body: Arial 10 pt, 1.2 line spacing, 6 pt between paragraphs. Subject: Cambria 13 pt, sentence case ("Sentence Stays A Sentence").

## Geometry (A4 = 210 × 297 mm)

| | mm |
|---|---|
| Left / right margin | 24 (the GCS house letterhead uses 23.8; header and footer sit on the same edges as the text) |
| Header | 12 from the top edge; logo 80 wide; gold hairline 0.5 pt, 3 mm below the logo |
| Body starts | 40 from the top |
| Footer | 10 from the bottom edge; hairline 0.5 pt Mist; row of three zones: title 58 · GCS 54 (mark 46) · website 50 |
| Body ends | 28 from the bottom |

Keep a picture at least 6 mm narrower than its table cell: LibreOffice clips one that nearly fills it (the `check` command errors on this).

## House precedent — the GCS letterhead

`GCS-General.docx` (gcs-word plugin, `resources/ds/templates/letterheads/`; HTML source `letterhead-general/Letterhead.dc.html`) is Global Citizen Solutions' own A4 letterhead: Primary-Blue logo top-left (36.8 × 13 mm) with a hairline under it; footer with a hairline, an uppercase light label (`GLOBALCITIZENSOLUTIONS.COM`) on the left and the page number on the right; margins 23.8 mm L/R, 45 top, 25.4 bottom; Yrsa headings over Roboto. This letterhead keeps that skeleton (logo + hairline header, hairline + label footer, same side margins) and differs on purpose: the Summit's own horizontal lockup, a gold hairline under it, a three-zone footer (title · GCS · website) and no page number, because the user specified those three footer items. For a GCS (not Summit) letter, use `gcs-word`.

## Gaps and calls the repo does not settle

- **No Summit stationery spec exists.** The site repo's `DESIGN.md` is a web system. The layout is this skill's own, drawn from the site's principles (navy text, hairlines instead of boxes, gold as a rule, no gold text on white, labels in tracked caps), the A4 programme PDF's footer and the GCS house letterhead's skeleton. Say so if asked who approved it.
- **"Título" in the footer** was read as the event title. Pass `"title"` to change it (a long title wraps to two lines; ~34 characters fit on one).
- **Website printed.** The user asked for it. The site's `CLAUDE.md` says it "currently sits behind HTTP Basic Auth" — whether the gate has been lifted is unknown; tell the user once in the hand-off.
- **No address, phone or e-mail** is printed — none was asked for and the repo gives none for letters (`events@globalcitizensolutions.com` is the partner-enquiry route in `PRODUCT.md`). Add one only if the user supplies it.
- **No CNN Portugal or other partner mark.** The banner skill's rule that every banner carries GCS + CNN Portugal was the user's decision for web art; it was not extended to stationery. On 2026-10-21 the user set a white-ground rule for the Summit skills (GCS Primary Blue + red CNN Portugal) and then excepted the letterhead: **only the GCS Secondary Blue**. Ask before adding any partner logo, and never give one a role ("official partner").
- **Page numbers and a different first/continuation page** are not included (the GCS house letterhead does carry a page number — offer it); every page repeats the same header and footer.
- Word is the target but only LibreOffice is available to render here; the file passes the OOXML schema validator and sets compatibility mode 15, so a look in Word is still the final check.
