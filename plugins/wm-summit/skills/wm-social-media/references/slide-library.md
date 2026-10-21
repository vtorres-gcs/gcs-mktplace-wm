# Slide Library — Wealth & Migration Summit 2026

Templates for carousel, single post, story and LinkedIn post. All of them are written **against the class vocabulary in `scripts/summit_assets.py` (`BASE_CSS`)** and the tokens in `TOKENS_CSS`. A slide never writes a literal `font-size`, `font-family`, `rgba()`, hex colour or `box-shadow` — it picks a class or a `var(--token)`. `scripts/qa.py lint` fails the deck if one slips in.

`{PLACEHOLDERS}` are filled at generation time. `{PHOTO}` is a data URI (see `rendering.md`). `{MAST}` is `mast("dark")` on navy and photographic slides and `mast("light")` on white ones; `{MARKS}` is `marks("dark")` or `marks("light")` — both from `summit_assets`, so the right logo file is always on the right ground. Each template is the **inner markup** of one slide; `build_document()` wraps it in `<div data-slide … class="slide canvas-… g-…">`.

Read `PRODUCT.md` and `DESIGN.md` first. Where this file and `DESIGN.md` disagree, `DESIGN.md` wins.

## Contents

1. [Formats and canvases](#formats-and-canvases)
2. [Alternating grounds across a set](#alternating-grounds-across-a-set)
3. [Slide types](#slide-types) — cover · statement · plate-text · plate-split · plate-only · programme · ledger · entries · speaker · quote · register
4. [Sequences](#sequences)
5. [LinkedIn post](#linkedin-post)
6. [Visual snippets](#visual-snippets) — ruled table with flags · countdown · day-by-day split
7. [Custom layout](#custom-layout)
8. [Rules that apply to every type](#rules-that-apply-to-every-type)

---

## Formats and canvases

| Format | Canvas | `build_document` key | Outputs |
|---|---|---|---|
| Carousel — Instagram / LinkedIn | 1080 × 1350 (4:5) | `carousel-4x5` | PNG per slide + PDF |
| Carousel — X / Facebook | 1080 × 1080 (1:1) | `carousel-1x1` | PNG per slide + PDF |
| Single Post | 1080 × 1350 (or 1080 × 1080) | `post` | PNG |
| Story | 1080 × 1920 (9:16) | `story` | PNG per frame |
| LinkedIn Post — landscape | 1200 × 627 | `linkedin-landscape` | PNG |
| LinkedIn Post — square | 1080 × 1080 | `linkedin-square` | PNG |

The canvas class sets the type ramp and padding (`--pad-*`). Story keeps Instagram's UI-safe margins (250px top, 310px bottom). On a 1080 × 1080 canvas, shorten photo plates (e.g. 560px → 380px) rather than shrinking type.

## Alternating grounds across a set

The set alternates **white and navy** (decided with the client's designer, 20 Oct 2026; `DESIGN.md` itself keeps the page one navy ground). The cover is a photograph on navy; from slide 2 the content slides alternate. Ink flips with the ground: white type on navy, navy type on white; gold is spent as a mark on white (a rule, a dot, the lamp, the `.lit` block) and as text only on navy.

| Role in the set | Class passed to `build_document` |
|---|---|
| Cover | `g-navy` with the photograph and `.scrim-cover` (a flat navy cover when there is no photograph) |
| Statement, ledger, entries, speaker — the content slides | alternate `g-white` and `g-navy` |
| The programme (the signature, darkest slide) | `g-deep` — always navy, whatever its position |
| Register / closing | `g-white` when the previous slide is dark, `g-navy` or `g-low` when it is white — and the one with the `.lit` call to action |

Rules: never two white slides in a row (`qa.py` warns); the programme stays dark; a white slide has no photograph and no `.panel` (paper on paper); on a white slide gold text is an error. In a two-slide set keep cover dark, closing white.

---

## Slide types

Each block starts with a `<!-- TYPE name -->` marker. Copy the markup, fill the placeholders, delete the optional lines you don't need.

### Masthead and marks (every slide)

```python
mast("dark")    # navy / photographic slides: the event logo, white
mast("light")   # white slides: the event logo, blue
marks("dark")   # cover, closing: Global Citizen Solutions + CNN Portugal, white, left-aligned — as in the site hero and the reference cover
marks("light")  # white closing: GCS primary blue, CNN Portugal red
```

The masthead is the **event's horizontal lockup** (`assets/logos/w&m-horizontal White|blue.svg`: the W mark and the name on one line, no GCS line), top-left, 705px wide, on every slide. The **GCS and CNN Portugal marks** sit side by side, **left-aligned** at the foot of the cover and of the closing slide only (80px tall, 40px apart), the way the site hero pairs them. The GCS mark **stands alone: nothing is written above, beside or over it** — no "Convened by", no caption (`qa.py` rejects text next to it). Use the files as supplied (`assets/logos/`), never recoloured; white marks on dark grounds; on white, the primary blue GCS and the red CNN Portugal. Any other partner logo needs the user's confirmation for the post.

### 1 · Cover — always slide 1

**The reference.** `references/img/cover-reference.webp` is the client's cover and the model for every cover: the hero photograph under one blue-navy wash; the event's horizontal lockup top-left; at the foot, left-aligned on a 125px margin, a gold service line, the headline in Caladea, a swipe cue with a long arrow, and the GCS and CNN Portugal marks. Margins are 125px on every side. **Look at it before building a cover.** The reference's own copy ("Where international wealth and global mobility meet") is the retired headline — take the layout, not the words; the headline is the site's current one (`FACTS.md`).

```html
<!-- TYPE cover -->
<img class="photo" src="{PHOTO}" alt="">
<div class="scrim-cover"></div>
<div class="frame between">
  {MAST}
  <div class="cover-stack">
    <p class="label service">{SERVICE_LINE}</p>
    <h1 class="display">{HEADLINE}<span class="dim"> {HEADLINE_SECOND_LINE}</span></h1>
    <span class="swipe label">Swipe <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
    {MARKS}
  </div>
</div>
```

- **The wash** (`.scrim-cover`, token `--scrim-cover`) is fitted to the reference by measuring it against the bare photograph: a `dawn-blue` tint at ~75% under the masthead easing to ~60% by the horizon, then navy-wash closing to ~96% at the foot where the marks sit. Between the horizon and the swipe cue (where the service line and headline land) it is held at ~70% — the reference is ~50% there, but the gold service line needs 3:1. Don't lighten it. The photograph is `photo.bridge` (`hero-1920.webp`, the site hero's), centred (`object-position: 50% 50%`).
- **Contrast gate for the cover.** The cover keeps more photograph than the 0.04 house limit allows (that is the look the client chose), so it is checked by contrast, not by the limit: `qa.py scrim <deck>.html 1 x y w h white|gold` must report ≥ 3:1 for each text box and the logos (masthead ≈ 5:1, headline ≈ 7:1, service line ≈ 3.3:1, marks > 14:1 on the sample). Other photo slides stay on the 0.04 limit.
- `{SERVICE_LINE}` is the site's own line, `5–6 November 2026 · Lisbon` (`facts.site()["service_line"]`; the copy deck's longer form ends "Lisbon, Portugal"), gold, Archivo 600, uppercase, no lamp. Put the venue line in the body or on a second slide, not here. It is the **only** label allowed above a headline on a cover.
- `{HEADLINE}` ≤ 12 words, sentence case, three lines at most. The optional `dim` second line is a tone step in Dawn Mist — **not italic**.
- No wet-street echo on the cover: the reference has none. Headline in sentence case; a long headline (the site's runs to four lines) simply starts higher.
- Drop the swipe cue (and its 56px of space) on a Single Post and on the last Story frame.

### 2 · Statement — headline + lead, no photograph

```html
<!-- TYPE statement -->
<div class="frame">
  {MAST}
  <div class="grow stack centre gap-m">
    <h2 class="headline">{HEADLINE}</h2>
    <p class="lead">{LEAD — max 40 words}</p>
    <p class="body">{OPTIONAL SECOND PARAGRAPH — mist}</p>
  </div>
</div>
```

The first paragraph is the lead (white); anything after it is body (mist). Delete the body paragraph if the slide breathes better without it.

### 3 · Plate with text — full-bleed photograph, text on two scrims

```html
<!-- TYPE plate-text -->
<img class="photo" src="{PHOTO}" alt="">
<div class="scrim-cross"></div>
<div class="scrim-rise"></div>
<div class="frame between">
  {MAST}
  <div class="stack gap-m">
    <h2 class="headline">{HEADLINE}</h2>
    <p class="lead">{LEAD — max 40 words}</p>
  </div>
</div>
```

After rendering, measure the ground under the text with `python3 scripts/qa.py scrim <png> x y w h` — it must stay under 0.04 relative luminance. If the photograph is bright, the text goes on the scrim-rise side lower or the `scrim-flat` veil is added (`<div class="scrim-flat"></div>` after the photo).

### 4 · Plate split — photograph above, text below

```html
<!-- TYPE plate-split -->
<div class="frame">
  {MAST}
  <div class="plate plate-fade" style="margin-top:56px; height:{PLATE_HEIGHT}px;">
    <img src="{PHOTO}" alt="">
    <span class="caption label-sm">{CAPTION}</span>
  </div>
  <div class="grow stack centre gap-m">
    <h2 class="headline">{HEADLINE}</h2>
    <p class="body">{BODY — max 40 words}</p>
  </div>
</div>
```

`{PLATE_HEIGHT}` — 560 on 4:5, 380 on 1:1, 760 on Story. The plate has no border and no radius, and dissolves into the ground by mask. The caption is optional (a place name, never a claim).

### 5 · Plate only — visual break, no copy

```html
<!-- TYPE plate-only -->
<img class="photo" src="{PHOTO}" alt="">
<div class="scrim-top"></div>
<div class="frame">
  {MAST}
</div>
```

### 6 · Programme — the Timed Line (signature)

The one authored motion of the page, as a still: a 4px amber line down the gutter, a ring on the line for each session, tabular times against session titles, hairlines between rows. Use `g-deep`.

```html
<!-- TYPE programme -->
<div class="frame">
  {MAST}
  <div class="grow stack centre gap-m">
    <p class="label day">{DAY_MARKER}</p>
    <h2 class="title">{DAY_THEME}</h2>
    <ol class="timed">
      <li class="station"><span class="datum">{TIME}</span><span class="session">{SESSION_TITLE}</span></li>
      <li class="station is-active"><span class="datum">{TIME}</span><span class="session">{SESSION_TITLE}</span></li>
      <li class="station"><span class="datum">{TIME}</span><span class="session">{SESSION_TITLE}</span></li>
    </ol>
  </div>
</div>
```

- `{DAY_MARKER}` — `Day one · 5 November` / `Day two · 6 November`. `{DAY_THEME}` — "The New Geography of Wealth & Mobility" / "Global Wealth & the International Family" (`facts.programme()[i]["theme"]`; the older themes "The Golden Visa Pathway" and "Structuring, Context & Experience" are retired and `qa.py lint` rejects them).
- **Only sessions and times the site publishes** — `python3 scripts/facts.py programme 1` prints them; `references/data/programme.json` holds them. Every title is verbatim (`full`, or the lead-in `title` alone), every `{TIME}` is a published start time. Never compute an end time, never pair a speaker with a session (`FACTS.md` → Programme, rule 3). `qa.py lint` checks times and warns on a title it cannot find.
- 3–6 stations per slide. A day is 15 main-stage rows (coffee, lunch and registration included) plus 5 workshops: show breaks only when they are the point (the lunch, the closing). Main stage and workshops are separate slides — the site keeps them as separate tracks ("Main Stage" / "Workshops · Breakout Room").
- `is-active` (filled gold dot, Lit Gold title) marks the one session the post is about. At most one per slide.
- A programme post's caption carries "Programme subject to change."

### 7 · Ledger — facts between hairlines

```html
<!-- TYPE ledger -->
<div class="frame">
  {MAST}
  <div class="grow stack centre gap-m">
    <h2 class="headline">{HEADLINE}</h2>
    <div class="ledger">
      <div class="ledger-row"><span class="subtitle">{FIGURE}</span><span class="datum">{DESCRIPTION}</span></div>
      <div class="ledger-row"><span class="subtitle">{FIGURE}</span><span class="datum">{DESCRIPTION}</span></div>
      <div class="ledger-row"><span class="subtitle">{FIGURE}</span><span class="datum">{DESCRIPTION}</span></div>
    </div>
  </div>
</div>
```

Figures come from `FACTS.md`: `5–6 Nov` · `2 days` · `200` attendees (limited to) · `26` speakers · `10` workshops · GCS: `10+ years`, `100+ professionals`. **Do not state a session count** — nothing on the site defines "session" and the 15 main-stage rows a day include breaks. Nothing else: no past-edition numbers, no attendance claims, no "150". Two to four rows. Figures are Transit Gold (the footer's figures are gold on the page).

**Rates as a ledger** (rate-change post): one row per tier — `{PRICE}` as the figure, `{TIER} · {WINDOW}` as the description — from `facts.rates()["tiers"]`, only the tier in force and the next one (a tier that has ended is not shown). The deadline is a date in the description, never a pressure line. Lint flags a price that is not one of the three published, and one whose tier has ended.

### 8 · Entries — ruled list (who's in the room, themes)

```html
<!-- TYPE entries -->
<div class="frame">
  {MAST}
  <div class="grow stack centre gap-m">
    <h2 class="headline">{HEADLINE}</h2>
    <div class="entries">
      <div class="entry"><h3 class="subtitle">{ENTRY_TITLE}</h3><p class="datum">{ENTRY_DESCRIPTION}</p></div>
      <div class="entry"><h3 class="subtitle">{ENTRY_TITLE}</h3><p class="datum">{ENTRY_DESCRIPTION}</p></div>
      <div class="entry"><h3 class="subtitle">{ENTRY_TITLE}</h3><p class="datum">{ENTRY_DESCRIPTION}</p></div>
    </div>
  </div>
</div>
```

Three to four entries per slide. The site lists four audiences under "Who's in the room" (`facts.site()["who_is_in_the_room"]`: Global individuals & families · Legal & tax counsel · Private banking · Industry and Government) — one slide. The seven segments of the older copy deck are retired. The site gives no description for any of them; don't invent one — a description may only restate the about-copy. No icons, no tiles, no cards.

### 9 · Speaker — only from the supplied roster

```html
<!-- TYPE speaker -->
<div class="frame">
  {MAST}
  <div class="grow stack centre gap-l">
    <div style="display:grid; grid-template-columns:400px 1fr; gap:56px; align-items:end;">
      <div class="plate" style="width:400px; height:500px;"><img src="{PORTRAIT}" alt="{NAME}"></div>
      <div class="stack gap-s"><h2 class="title">{NAME}</h2><p class="datum">{ROLE}</p></div>
    </div>
    <p class="body">{BIO — max 40 words}</p>
  </div>
</div>
```

Look the person up, don't type them: `s = facts.speaker("pucca")` gives `display` (the name), `role` and `bio`; `facts.speaker_photo("pucca")` gives the portrait path for `embed_image()`. All 26 portraits are bundled, so there is no initials fallback today; if a future sync reports a missing portrait, replace the `.plate` with

```html
<div class="plate plate-initials" style="width:400px; height:500px;"><span class="title">{INITIALS}</span></div>
```

Name and role are the site's card, verbatim; the bio, if used, is whole sentences from the card, ≤ 40 words. Roster order (`facts.speakers()`) decides the order of a multi-speaker set. Portraits are the client-supplied headshots only — never generated, never altered. A person who is not on the site's roster is not drawn or named (the agenda-only names are listed in `FACTS.md` and rejected by lint). Check the "known inconsistencies" table in `FACTS.md` before quoting a bio (Ayoub Rebroub and Yanimar Hernandez have bios that contradict their cards).

### 10 · Quote — only a real, supplied quote

```html
<!-- TYPE quote -->
<div class="frame">
  {MAST}
  <div class="grow stack centre gap-m">
    <p class="headline"><span class="ink-gold">&ldquo;</span>{QUOTE — max 25 words}&rdquo;</p>
  </div>
  <div class="stack gap-s rule" style="padding-top:32px;">
    <p class="subtitle">{NAME}</p>
    <p class="datum">{ROLE}</p>
  </div>
</div>
```

The opening mark is gold, set inline in the quote's own type — not a separate graphic. Use the `title` class instead of `headline` when the quote runs past 25 words. There are no delegate testimonials and no past-edition quotes. A quote slide exists only when the user supplies a real quotation from a named roster speaker. Never put words in a real person's mouth.

### 11 · Register — always the last slide

Default: a **white slide** (`g-white`) after a dark one — navy type, a gold rule as the mark, the `.lit` block as the one call to action, `marks("light")` in the footer. When the previous slide is white, the register is navy (`g-navy` / `g-low`) with `marks("dark")`; a white `.panel` on that navy ground is the alternative treatment. On paper, gold appears **only as a mark**, never as text.

```html
<!-- TYPE register — white slide (g-white) -->
<div class="frame between">
  {MAST}
  <div class="stack gap-m">
    <i class="mark-gold"></i>
    <h2 class="headline">{CTA_HEADLINE}</h2>
    <p class="lead">{BODY — one or two sentences}</p>
    <div class="rule"></div>
    <p class="datum">{FACT_LINE — e.g. Advance Rate · €499 · until 30 October}</p>
    <span class="lit" style="align-self:flex-start;">{ACTION_LINE}</span>
  </div>
  {MARKS}
</div>
```

```html
<!-- TYPE register — navy slide with the white panel (g-low) -->
<div class="frame between">
  {MAST}
  <div class="panel">
    <i class="mark-gold"></i>
    <h2 class="headline">{CTA_HEADLINE}</h2>
    <p class="lead">{BODY}</p>
    <div class="rule"></div>
    <p class="datum">{FACT_LINE}</p>
  </div>
  <div class="mast"><span class="lit">{ACTION_LINE}</span>{MARKS}</div>
</div>
```

- Register slide: the site's call is **"Secure your place"**, and it leads to a booking page with payment ("Your place is confirmed once payment is received"). So `{CTA_HEADLINE}` invites a booking — not an enquiry, and not "the start of a vetted process" (that was the older page). `{BODY}` may carry the facts that make the decision: both days, the included items (`facts.rates()["included"]`), "Limited to 200 attendees". No urgency mechanics, no countdown pressure.
- **Price on the panel:** only the tier in force on the post date (`facts.rate_on()`), as a datum line — `Advance Rate · €499 · until 30 October`. Say in the hand-off which tier and until when it is true. Outside 1 Sep – 4 Nov: no price.
- `{ACTION_LINE}` is the one lit thing (`.lit`, gold block, navy text): **"Link in bio"** (Instagram), or the confirmed URL — the headline already says "Secure your place" or the URL the user has confirmed. The domain is `wealthandmigrationsummit.com` and the booking page `/claim-your-seat`, but whether the site's staging gate is lifted is unverified (`FACTS.md` → Rates and booking) — ask once before a URL is printed on a graphic.
- **Partner variant** — swap the headline for the site's ("Interested in partnering with the Summit?") and the body for its sentence. `{ACTION_LINE}` is the route the user confirms (the site uses a form; `events@globalcitizensolutions.com` is in `PRODUCT.md` but is no longer printed on the site) or "Link in bio". No sponsor logos, no tiers, no prices.
- A Story's last frame is this slide.

---

## Sequences

```
Slide 1      cover
Slides 2…    statement · plate-text · plate-split · ledger · entries · programme (the darkest point)
             speaker slides group together, after the argument
Slide N-1    quote (only when a real quote exists) — optional
Slide N      register
```

- More recipes — workshop series, rate change, countdown, Plan B, partner call, and the **caption file every job ships** — are in `content-playbook.md`.
- **Announcement:** cover → statement (why now) → ledger (the facts) → programme day one → programme day two → register.
- **Programme deep-dive:** cover → statement → programme ×2–4 → entries (who's in the room) → register.
- **Speaker spotlight:** cover → speaker → statement (what they will cover — only from the roster bio/programme) → register.
- **Audience:** cover → entries ×2 → ledger → register.

Platform limits: Instagram / LinkedIn max 20 slides (practical 6–9) · Facebook 10 (practical 5–7) · X **4** — pick the strongest points. Instagram: ask for a *save* in the register slide's body; LinkedIn: PDF carousels outperform image posts.

The Single Post uses one of: cover (photo hook, no swipe cue), ledger (one strong fact), statement (one claim). It must be self-sufficient: headline + one supporting element + where to go next.

---

## LinkedIn post

Landscape 1200 × 627 (default) or square 1080 × 1080 (use the **cover** template). Headline only — no body copy, no CTA on the canvas; the call to action goes in the caption.

```html
<!-- TYPE linkedin-landscape -->
<img class="photo" src="{PHOTO}" alt="">
<div class="scrim-cover"></div>
<div class="frame between">
  {MAST}
  <div class="stack gap-s">
    <p class="label service">{SERVICE_LINE}</p>
    <h1 class="display">{HEADLINE — two lines at most}</h1>
  </div>
  {MARKS}
</div>
```

No photograph: delete the `<img>` and the scrim — a typographic LinkedIn post on flat navy is a complete design.

---

## Visual snippets

Palette discipline: gold on the active thing only; hairlines, never boxes.

### Ruled table with flags (country comparison)

Only for comparisons the approved copy supports (the Portugal / Italy / Greece / Malta landscape is a session topic; figures are not ours to supply). Flags are small rectangles — the system is square.

```html
<div class="rtable" style="--cols:1.2fr repeat(3, 1fr);">
  <div class="rtable-row rtable-head">
    <span class="label-sm">{CRITERIA_LABEL}</span>
    <div><img class="flag" src="{FLAG_1}" alt=""><span class="label-sm ink-white">{COUNTRY_1}</span></div>
    <div><img class="flag" src="{FLAG_2}" alt=""><span class="label-sm ink-white">{COUNTRY_2}</span></div>
    <div><img class="flag" src="{FLAG_3}" alt=""><span class="label-sm ink-white">{COUNTRY_3}</span></div>
  </div>
  <div class="rtable-row">
    <span class="datum">{ROW_LABEL}</span><span class="datum ink-white">{VALUE}</span><span class="datum ink-white">{VALUE}</span><span class="datum ink-white">{VALUE}</span>
  </div>
</div>
```

A flag appears only when the slide is specifically about that country (`flag_uri("pt")`, network). Highlight at most one winning cell with `ink-gold`.

### Countdown

Not four tiles — a static image cannot count. State the days left as a single Display figure in a Statement slide:

```html
<p class="display">{N}</p><p class="label">Days to go</p>
```

Compute `{N}` with `facts.days_to_go()` — never by hand. It is true on the day it is generated and wrong a day later: the hand-off says "valid on <date> only". A countdown is a fact, not a pressure device: no "hurry", no "last".

### Day-by-day split

When one slide has to show both days, use two Entries blocks side by side only on 1080 × 1350; otherwise two slides. Asymmetric pairs, never a row of equal cards.

---

## Custom layout

A free composition inside the system — the normal way to work, not the exception: the types above are a vocabulary, the layout is decided from `DESIGN.md` and the content. One line per slide in the plan (SKILL.md, Step 3); a fuller sketch only when the composition is far from anything here.

**Invariants:** palette tokens only · Caladea + Archivo through the type classes · masthead lockup always present · `border-radius` 0 (50% only for lamps) · shadows only from `--glow-*` / `--lift-night` · scrims layered, navy, never black · one lit gold block per canvas · the ramp stays closed · grounds alternate white and navy, white slides carry no gold text · the GCS mark stands alone.

**QA gate before rendering:**
- [ ] Masthead present (`mast()`: the event logo)?
- [ ] Only palette tokens and type classes (`python3 scripts/qa.py lint` is clean)?
- [ ] Gold spent on one active thing, and never as text on a white slide?
- [ ] White slides alternate with navy, none in a row, the programme dark, no `.panel` on a white slide?
- [ ] Nothing written above, beside or over the GCS mark?
- [ ] No eyebrow above a heading (service line and day marker excepted)?
- [ ] Grounds alternate as planned?
- [ ] Headline ≤ 12 words, body ≤ 40?
- [ ] Layout matches the plan?

## Rules that apply to every type

- **One anchor per slide.** The eye lands on one thing: a headline, a Display figure, a plate.
- **Never overcrowd.** Whitespace is structure. Content grows → add a slide, do not shrink type.
- **No icons, no tiles, no chips, no cards.** The container vocabulary of the system is the countdown tiles, the audience entries and the rates panel — none of which this skill redraws except as ruled entries. The only paper is a white slide or the register panel — never a card on a white slide.
- **No row gets a hover-look.** A programme row is not a button; it has no arrow, no underline.
- **No invented facts.** Sponsor roles, testimonials, past-edition figures, GCS-owned venue photography, speaker↔session pairings and session end times are absent from the evidence and stay absent. Prices are allowed only as the published tiers (`FACTS.md` → Rates and booking); partner logos only when the user confirms them for this post.
