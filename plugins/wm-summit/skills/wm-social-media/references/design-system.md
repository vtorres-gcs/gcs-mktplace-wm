# Design system — the social-canvas translation

`DESIGN.md` ("Lisbon Nocturne") and `PRODUCT.md` are the source of truth and sit next to this file, unmodified. **This file adds nothing to the identity.** It only says how the page's rules land on a 1080px social canvas, and records what was deliberately left behind from the previous GCS social skill so nobody reintroduces it.

Hex values are **not repeated here**. They are parsed from `DESIGN.md`'s front matter by `scripts/summit_assets.py` and exposed as CSS custom properties (`--navy`, `--navy-deep`, `--navy-wash`, `--dawn-blue`, `--dawn-low`, `--gold`, `--gold-bright`, `--mist`, `--white`). Run `python3 scripts/summit_assets.py` to print them with the contrast of every text/ground pair.

## How each DESIGN.md rule lands on a canvas

| DESIGN.md | On a social canvas |
|---|---|
| **One navy ground, unbroken; sections differ by tone** | **Departure (see below):** a set alternates white and navy slides. Every slide is still a flat ground token; no container surfaces. |
| **The Hour Rule** — darker toward the programme, lighter toward the footer | Kept for the navy tones (`g-navy`, `g-deep` for the programme, `g-low` / `g-dawn` toward the close); the programme is always dark. White slides alternate in between. See `slide-library.md`. |
| **The One Light Rule** — one lit gold block per viewport | One gold thing per canvas: service line, day marker, programme line, a ledger of figures, or the single `.lit` block. `qa.py` rejects two `.lit`. |
| **Gold Never Touches Paper** | On any white surface (a white slide or the register panel) gold is only a mark — `.mark-gold` rule, programme dot, lamp square, the `.lit` block — never text. `qa.py` rejects gold text on `.g-white` and in `.panel`. |
| **The Named Alpha Rule** | Every alpha is a role token (`--rule`, `--rule-strong`, `--mist-dim`, `--scrim-*`, `--gold-edge`, `--ink-soft`…). `qa.py` rejects literal `rgba()` and hex in slide markup. |
| **Light Sources Are Tokens** | The only shadows are `--glow-mark` (the masthead lamp), `--glow-line` / `--glow-dot` (the programme), `--lift-night` (the register panel). |
| **The Scrim Is Layered Rule** | The cover uses `.scrim-cover` (one gradient fitted to the client's reference cover); other photo slides use `scrim-cross` + `scrim-rise`. Verify with `qa.py scrim` — ground under the text < 0.04 relative luminance; on the cover, contrast ≥ 3:1 per text colour (`qa.py scrim … white|gold`). |
| **The Ramp Is Closed** (ten steps) | Ten type classes (below). A new element takes the nearest step. |
| **The Sentence Stays A Sentence** | Headlines in sentence case. Uppercase belongs to labels only, tracked 0.16em. |
| **Times Line Up** (tabular figures) | `.datum` carries `tnum`; programme times use it. |
| **Square throughout; hairlines instead of boxes** | `border-radius` 0 everywhere; 50% only for programme dots and nothing else. Flags are rectangles, portraits are rectangles. |
| **Don't set an eyebrow above a heading** | Only the cover's service line and the programme's day marker precede a heading. |
| **Real photographic material; no simulated surface** | A cover with no photograph is a flat navy typographic cover — no gradient "texture" substitute. |
| **One authored motion, belonging to the programme** | A still has none; its trace is the Timed Line (gold line + rings). No other decorative device. |
| **Reduced motion / 44px targets / skip links** | Not applicable to a static image. Contrast and a 24px type floor stand in for them. |
| **Register is the only white surface** | **Departure:** white slides alternate with navy; the register is a white slide (or a navy slide with the white `.panel`). Never a white card on a white slide. |

## Type ramp — canvas scale

Roughly twice the page's rem scale, so the ramp reads on a phone. Defined once in `TOKENS_CSS`; Story and LinkedIn-landscape override a few steps in their canvas class.

| Class | Family | Feed (1080) | Role |
|---|---|---|---|
| `.display` | Caladea 400 | 96px / .95 | The one headline of a cover or LinkedIn post |
| `.headline` | Caladea 400 | 76px / 1.0 | Every other slide's heading, the quote |
| `.title` | Caladea 400 | 56px / 1.05 | A programme day's theme, a speaker's name |
| `.subtitle` | Caladea 400 | 44px / 1.05 | A ledger figure, an entry title, an attribution name |
| `.session` | Caladea 400 | 40px / 1.2 | A programme session title |
| `.lead` | Archivo 400 | 42px / 1.5 | First paragraph (white) |
| `.body` | Archivo 400 | 38px / 1.55 | Further paragraphs (mist), ≤ 40 words |
| `.datum` | Archivo 400, tabular | 32px / 1.4 | Times, descriptions, roles, fact lines |
| `.label` | Archivo 500, uppercase, .16em | 28px | Service line, day marker, wordmark, action line |
| `.label-sm` | Archivo 500, uppercase, .16em | 24px | Captions, "Swipe" |

Floor: **24px** on a 1080 canvas. Archivo is bundled at 400/500/600 only (500 is the heaviest in use). No italic anywhere.

## Colour roles (names, not values)

- **Navy** — base ground, text on the white panel. **Navy-deep** — the programme band, the darkest point. **Dawn-low / dawn-blue** — the closing movement. **Navy-wash** — the left wash of a photographic scrim; never a surface.
- **Mist** — secondary text, hairlines (at `--rule`, `--rule-strong`), captions. **White** — headlines, lead, the register panel.
- **Gold** — the one warm light: service line, day marker, programme line and dots, ledger figures, the lit block, the register slide's action line, the quote mark. **Gold-bright** — the hover/active state; here, the active session's title. Never body text, never on white.

## Masthead and marks

`DESIGN.md` describes the wordmark as a small gold square with a soft halo. On the canvas the masthead is the **event's horizontal lockup** instead (`assets/logos/w&m-horizontal White|blue.svg`, W mark + name on one line, via `mast("dark" | "light")`), top-left on every slide, 705px wide; margins are 125px on every side, as on the client's reference cover (`references/img/cover-reference.webp`). The **Global Citizen Solutions** and **CNN Portugal** marks sit side by side, left-aligned at the foot of the cover and the closing slide (`marks("dark" | "light")`), the way the site hero pairs them. Files are used as supplied, never recoloured: white marks on dark grounds; on white, the primary blue GCS (`GCS-Primary-Blue.png`) and the red CNN Portugal (`Logo CNN PORTUGAL Float Final.png`).

**Nothing is written above, beside or over the GCS mark** — no "Curated by", no caption; its name is in the mark. `qa.py lint` rejects text next to it. Any other partner logo needs the user's confirmation for the post.

## Imagery

Photography is the material: blue-hour river, wet street, still water, graded into the navy. No GCS-owned Lisbon or venue photography exists and the page's own imagery is generated and on the client's replacement list. Speaker portraits are the client's headshots only.

**Sourcing, generating, handing off** — read this part only when a layout needs a photograph and the user wants help getting one.

The HTML preview, live editing, rendering and review flow is unchanged once an image is available.

### What the evidence allows

From `PRODUCT.md` and `FACTS.md`: GCS owns **no** photography of Lisbon or of EPIC SANA Marques; the page's imagery is generated (Freepik / Magnific) and is on the client's replacement list. So, for social:

| Use | Allowed? |
|---|---|
| A generated "Lisbon nocturne" scene as atmosphere (river, wet street, still water, city lights at blue hour) | Yes — treat it as a **placeholder on the replacement list** and say so in the plan |
| A licensed stock photograph of a real Lisbon place (`assets/img/lisbon-*`: Vasco da Gama bridge, sunset panorama, Arco da Rua Augusta) | Yes — real photographs, rights cleared; no replacement-list caveat. Not the venue, and never with people added |
| A generated image presented as a real, specific place or the venue (caption "EPIC SANA Marques Hotel", a named landmark as a claim) | **No.** A generated image cannot be the venue. Captions name nothing the image cannot prove |
| A speaker, delegate, client or anyone resembling a real person | **No.** Speaker portraits are the client's supplied headshots only — never generated, never retouched into a different face |
| Sponsor or partner logos, signage, documents, passport / ID replicas, a screen with text | **No** — a generated image never carries a partner mark; real partner logos are placed only from `assets/img/` and only when the user confirms them for the post (`FACTS.md` → Partners and media) |
| A client-supplied photograph (event, speaker, venue) | Yes — it outranks any generated image; grade it into the navy with the scrims |

If the intended use is unclear and changes eligibility, ask one short question about where the image will be used.

### The look — "Lisbon Nocturne"

Blue-hour river, wet street, still water. The ground of the image is navy; the only warm light is amber, spent on one thing. A real photograph, graded dark, with quiet negative space for the headline. Nothing bevelled, embossed, glossy or textured; no neon, no lime (the reference's palette is ruled out).

### Generate here, or hand off

If a connected image-generation tool is available (for example the Magnific MCP) and generation is requested: use it with the brief below, then **check the result before using it** — ratio, subject, quiet area for text, no accidental text/logos/faces, navy-dominant grade. If the user prefers an external tool, say "ℹ️ We will use your chosen external image tool." If no tool is connected, say first, in the user's language: "ℹ️ This session has no connected image-generation tool." Then:

"📋 Copy the prompt below into Gemini or ChatGPT with image generation enabled. Generate the image there, then upload the result here. I will check it and add it to the design before the preview."

Fill **every** field from the brief and the chosen layout before showing one fenced `text` block. Ask only for a missing detail that materially changes the image; never deliver unresolved fields as a ready-to-copy prompt.

```text
Create a realistic, restrained editorial photograph for a private two-day wealth and
migration summit in Lisbon, used as atmosphere on a social post (placeholder imagery).
Subject and setting: [concrete scene — e.g. the Tagus at blue hour from a quiet quay, wet
cobbled street after rain reflecting a single warm lamp, still water at dusk].
Aspect ratio: [chosen ratio and pixel size — 4:5 = 1080x1350, 9:16 = 1080x1920, 1.91:1 = 1200x627].
Composition: [subject placement and camera framing]. Keep [specified side/area] quiet,
dark and uncluttered for a headline; do not generate the headline.
Light and grade: last minute of blue hour, deep navy dominant, one warm amber light as the
only warm note, fine natural grain, no HDR, no glow effects.
Exclude: text, letters, numbers, logos, signage, watermarks, people or faces, passport or
document replicas, skyline clichés (postcard tram, sunset flare), neon, lime green,
bevelled / embossed / glossy surfaces, visible AI defects.
Do not imply the image shows the real venue, a real event, or a real person.
```

State "⏳ Waiting for the image" and the next action. When the file returns, inspect ratio, subject, available text space, realism, and that it contains no text, logo or face; record it in the plan as **externally generated — client replacement list**. If unsuitable, explain one concrete correction and provide a revised prompt. A prompt or a placeholder is not a completed image: never render a photo-led layout as if the image exists. The typographic layout (no photograph) is always available as the fallback.

## Left behind from the GCS social skill (do not reintroduce)

| Dropped | Why |
|---|---|
| Night Blue `#000957`, Electric Blue `#3F8CFF`, their tints | Different brand. The Summit's palette is navy / gold / mist / white. |
| Yrsa + Heebo | Replaced by Caladea + Archivo. |
| Italic highlight line on the cover | Not in the system; the second headline line is a tone step (mist). |
| Electric-blue overlines above headings | "Don't set an eyebrow above a heading." |
| Trustpilot slide, quote-mark PNGs, the blue line-art CTA background | No testimonials exist; a typeset quote mark replaces the PNG; the line-art is off-palette and a simulated surface. |
| Material Symbols icons, icon-led lists, icon grids | Not part of the system; "no icon tiles". Ruled entries replace them. |
| Stat cards, bar charts, round flags, round portraits | "No further boxes or rounded corners." Ledger rows, ruled tables, rectangular flags and portraits replace them. |

## Departures from `DESIGN.md`, decided 20 Oct 2026

`DESIGN.md` is the site's system and stays untouched. For social, the client's designer chose:

1. **White and navy alternate.** The site is one navy ground with a single white surface; a carousel alternates white and navy slides (cover and programme stay dark). On white, ink is navy and gold is a mark only.
2. **The event logo is the masthead,** and the GCS + CNN Portugal marks close the cover and the final slide, instead of the gold square + name lockup and a "Curated by" label.
3. **The cover follows the client's reference image** (`references/img/cover-reference.webp`): hero photograph under one dawn-blue → navy-wash gradient fitted to it, left-aligned foot block, GCS + CNN marks bottom-left. It keeps more photograph than the 0.04 limit allows, so the cover is gated by 3:1 contrast instead. (An earlier version copied the site hero's 65.4° wash and failed the limit anyway.)

## Open assumptions to confirm with the design lead

1. **Masthead** is the event logo file; the gold-square lockup in `DESIGN.md` is no longer drawn.
2. **Programme dot** is a navy-deep dot with a 3px gold ring on the 4px gold line (`DESIGN.md` specifies navy-deep, 8px on the page); the ring keeps it legible at canvas scale.
3. **Canvas ramp** is ≈2× the page ramp; the ten steps map one-to-one.
4. **`--mist-dim`** (72% mist) and **`--ink-soft`** (72% navy on white) are social-only quiet-text roles; both pass AA on every ground they are used on.
5. **Cover echo** (the wet-street reflection) is dropped: the client's reference cover has none.
