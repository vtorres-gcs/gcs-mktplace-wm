# Deck design — how "Lisbon Nocturne" lands on a 16:9 slide

`DESIGN.md` describes a scrolling web page. A slide is a different object: it is seen for 90 seconds, from the back of a room or on a phone, and it is **edited later in PowerPoint by someone who did not build it**. This file records what carries over from `DESIGN.md`, what changes at slide scale, and the spec each slide type takes. Where this file and `DESIGN.md` disagree about a *slide*, this file wins; for colour, voice and the "never" list, `DESIGN.md` and `PRODUCT.md` win.

## What carries over unchanged

- **Palette** is parsed from `DESIGN.md` at build time (`wm_deck.PAL`) — a newer export re-colours every future deck. Navy `121B31` ground; gold `C2A358` is light, not colour; mist `C8CCD7` for secondary text; white for headlines.
- **Night grounds by default, white slides interleaved.** Slides differ by tone, not by container: `navy` (default), `deep` (`0A101F`, the programme band), `dawn` (`232F52`) and **`paper`** (white). The **cover and the back cover are always dark blue** (`navy`); in between, white slides may be interleaved with the night ones — the user's decision of 20 Oct 2026, which overrides `DESIGN.md`'s "the register is the only paper" for decks (as the white banners were). Put white where the slide is reading, not atmosphere: the rates, a day's workshops, the roster, a ledger of figures, a text-heavy statement; keep the photograph slides and the main-stage timeline dark. `meta.alternate: true` alternates night and white automatically for slides with no `tone` of their own. The old **Hour rule** (deepen toward the programme, lift toward the close) still guides the *night* tones, but no longer limits the white ones.
- **One light per slide.** Gold marks the single active thing: the service line, a day marker with its programme line, one ledger of figures, the current rate, or the call-to-action block. Never several at once.
- **Gold never touches paper.** Gold is for dark grounds. On a white slide gold stays a *mark* — the lamp, the programme line and its dots — and every text that is gold on night turns navy; the call to action becomes a navy block with white text; hairlines are navy at 16% (32% where a rule ends a group); quiet text is navy at 66%. `check_deck.py` fails gold text on any light ground (contrast < 4.5:1).
- **Square.** No rounded corners, no cards, no chips, no icon tiles. Structure is hairlines and ruled columns. The only filled blocks are the call-to-action and the caption chip over a photograph.
- **No eyebrow above a heading.** The only labels above a headline are the cover's service line and a programme slide's day marker — both are data with a lamp, not captions.
- **Sentence case** for every headline and title; uppercase only for 12pt labels, tracked 0.16em.
- **Programme is the argument.** If a slide can name a session, it names it — pulled from `data/programme.json`, verbatim.
- **Photographs are material, graded into the navy:** a layered scrim (one crossing from the text side, one rising from the ground) over a full-bleed photo; a dissolve gradient where a plate bleeds off an edge. No simulated textures, no bevels, no shadows.

## What changes at slide scale

| Role | Web (`DESIGN.md`) | Slide | Notes |
|---|---|---|---|
| display | 48–96px serif | **48pt** | cover headline and closing headline, 3 lines at most |
| headline | 32–54px serif | **36pt** | every slide's one statement; ≤ 3 lines |
| title | 26–36px serif | **28pt** | a programme day's theme; a speaker-grid heading |
| subtitle | 24–28px serif | **22pt** | ledger entry, rate-tier name, audience entry |
| session | 21–22px serif | **18pt** | a programme session title; a speaker's name in the 8-up grid |
| lead | 18px grotesk | **20pt** | the sentence under a headline |
| body | 17px grotesk | **16pt** | paragraphs, never below |
| datum | 15px grotesk | **14pt** | session subtitles, roles, notes |
| label | 13px, 0.16em caps | **12pt**, 0.16em caps | the floor: nothing below 12pt, because the audience skews older |

The ramp is closed. A figure in a ledger takes `display`; a new element takes the nearest step. If it does not fit, **cut words or add a slide — never shrink type.** `check_deck.py` fails any run below 12pt.

Other slide-scale facts:

- **Margins:** 0.8in gutter, content to 6.6in, footer at 6.95in. Hairlines are 0.75pt, mist at 20% (32% where a rule ends a group), pre-mixed onto the ground so they print.
- **A slide carries one message.** ≤ ~40 words of body, headline ≤ 12 words. A programme day is paged by the builder — balanced across pages, never one full page and one nearly empty.
- **Times** sit in their own fixed column (PowerPoint has no tabular-figures switch, so alignment comes from the column, not the font).
- **Motion:** none. No transitions, no animation — the programme line "draws in" on the web, on a slide it is simply drawn.

## Fonts — two modes

| `--fonts` | Heading | Body | When |
|---|---|---|---|
| `office` (default) | Cambria | Arial | any machine. Caladea (the brand serif) *is* Cambria's metric-compatible twin, so line breaks match the brand exactly; Arial stands in for Archivo |
| `brand` | Caladea | Archivo | only where both are installed (`assets/fonts/*.ttf`). Otherwise PowerPoint substitutes silently |

The fonts live in the **theme** (`+mj-lt` / `+mn-lt`); no slide hard-codes a font name. Changing Design → Variants → Fonts in PowerPoint restyles the whole deck. Fit is always *measured* with the real Caladea and Archivo files (plus a 4% margin, because PowerPoint sets text without kerning).

## Anatomy of the file (so a colleague can edit it)

- Three layouts only: **WM Cover** (cover and back cover, no footer), **WM Content** (night: title + footer label + slide number) and **WM Content Paper** (the same on white). Footer and slide number live on the layout, never on a slide.
- Every slide's heading is the layout's real **title placeholder** — the outline view, accessibility checker and slide sorter all see it.
- The theme carries the palette (`Lisbon Nocturne`: dk1 navy, lt1 white, accent1 gold…) with a **dark colour map**, so a text box added in PowerPoint is white on navy instead of invisible; the paper layout flips the map, so there it is navy on white.
- Every shape is named (`Day marker`, `Session 09:10`, `Price Advance Rate`…) for the Selection Pane. Every picture has alt text (decorative ones are named `Decor…`).
- Speaker notes: `"notes"` on any slide.
- Cover and speaker photographs are converted to JPEG ≤ 2000px; a full 26-speaker deck is ~3 MB.

## Slide types and their spec

A deck spec is `{"meta": {...}, "slides": [ {...}, ... ]}`. `meta`: `title`, `author`, `fonts` (`office`|`brand`), `lang` (default `en-GB`; use `pt-PT` for Portuguese text so spellcheck is right), `as_of` (date the deck is valid for — decides the current rate tier), `confirmed` (list: `url`, `email` — only once the user has said so).

Any string value that starts `@site.` or `@rates.` is pulled **verbatim** from the bundled facts (`@site.headline`, `@site.lede`, `@site.service_line`, `@site.about_heading`, `@site.setting_heading`, `@site.programme_heading`, `@site.partner_cta`, `@rates.cta`). Prefer these to retyping the site's own words. Every slide takes `tone` (`navy`|`deep`|`dawn`|`paper`; not `paper` on the cover or back cover) and `notes`. `meta.alternate: true` hands the slides that name no tone an alternating night / white rhythm.

| `type` | Use it for | Fields |
|---|---|---|
| `cover` | slide 1 — always dark | `title` (**required**), `lede`, `service_line` (default the site's), `image` (`hero`\|`venue`\|`night`\|path), `image_alt`, `marks` (default `["gcs", "cnn"]`: the white Global Citizen Solutions and CNN Portugal marks side by side (on a white ground: GCS primary blue + red CNN Portugal), left-aligned at the foot, as the site hero and the social cover carry them; the GCS mark stands alone — nothing written above, beside or over it) |
| `statement` | one idea in a headline | `headline`, `lead`, `body` (list of paragraphs), optional `image`+`image_alt` (right plate) |
| `split` | an idea beside a photograph that bleeds off the right edge | `headline`, `body`, `image`, `image_alt`, `caption`, `focus` ([x,y] 0–1) |
| `photo` | a full-bleed breath between sections | `headline`, `image`, `image_alt`, `caption` |
| `ledger` | 2–4 figures | `headline`, `items`: `{"auto": "days"\|"workshops"\|"speakers"\|"capacity"}` (computed from the data) or `{"figure","label"}`; `note` |
| `entries` | 3–6 short ruled columns (audience, pillars) | `headline`, `items`: `"@audience"` (the site's four) or `[{"title","text"}]` |
| `days` | the two day-themes side by side | `headline` (default the site's), `pick`: `{"1": [ids], "2": [ids]}` of session ids to preview |
| `programme` | a day's timed line, auto-paged, with each session's speakers as the agenda writes them | `day` 1\|2, `track` `main`\|`workshops`, optional `from`/`to` ("09:00"), `ids`, `breaks` (default true), `speakers` (default true), `end_times` (default false), `note` (default the agenda's "Programme subject to change."), `columns` (1 default; 2 = two timed lines side by side, ~10 rows a page — a Day's main stage fits in 2 slides instead of 3), `note` |
| `speakers` | the roster | `names` (`"all"` or a list of names/slugs), `headline`, `per_slide` 4\|8 |
| `speaker` | one speaker, full bio | `name` |
| `rates` | the three tiers, the current one marked, what's included, the CTA | `headline`, `url` |
| `section` | a divider | `headline`, `number` |
| `closing` | the **back cover** — dark blue (`navy`), the cover's masthead and the same GCS + CNN marks at the foot | `headline`, `lead`, `cta` (default "Secure your place"; `false` = no button, for people who already hold a place), `url`, `contact`, `service_line`, `marks` |

**Session ids** are in `references/data/programme.json` (`d1-0915`, `d2-w1200`…, `HH:MM` of the start); `python3 scripts/facts.py programme 1` prints times, titles and speakers. An unknown id fails the build and lists the valid ones.

### What the builder will not do

It will not draw a speaker who is not on the roster (it raises), will not link the call-to-action unless `confirmed` includes `url`, will not show a price (the rates slide excepted) that is not the tier in force on `as_of`, and attaches speakers to sessions only as the agenda prints them (never a guessed name; "to be announced" stays "to be announced"). For anything outside the slide types (a chart, a table, a diagram), build the closest slide, then add it in PowerPoint, or hand the finished deck to the general `pptx` skill to extend; keep the ground, the type ramp and the one-light rule.

Not offered, deliberately: partner/sponsor logo walls (the site does not say what each partner is), and testimonials or past-edition figures (none exist).
