---
name: wm-web-banners
description: "Creates web banners for the Wealth and Migration Summit 2026 (Lisbon, 5–6 Nov 2026, curated by Global Citizen Solutions) in the size the user gives (728x90, 300x250, 970x250, 160x600, 320x50 or any WxH) as a PNG or an animated GIF. Always asks which output the user wants; for a GIF it asks the maximum file size and compresses to fit without changing the dimensions. Follows the site's identity, navy first (white Caladea + Archivo type, gold only for the button and one rule, W&M lockup) and always carries the Global Citizen Solutions and CNN Portugal marks. Copy from confirmed facts only; lints words and layout before rendering; ships alt text. Use whenever the user mentions a banner, web or display banner, leaderboard, skyscraper, medium rectangle, billboard, GIF animado, banner animado, or any WxH graphic for the Summit. Not for social carousels, stories or LinkedIn posts (use wm-social-media), Google Ads or Meta Ads campaigns (use wm-paid-ads), the landing page, or general GCS banners."
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "Sync with site repo at f2fbee2: 31 speakers (added Sheree Mitchell, Teresa Barbosa, António Henriques); Hadley Gamble as Summit Host; homepage session titles now canonical; FACTS.md + data JSONs refreshed."
---

# Web banners — Wealth & Migration Summit 2026

One job: turn **a size the user gives** into a finished **PNG** or **animated GIF** banner on the Summit's **navy ground** — blue first, as on the site — in its own identity, from confirmed facts only. `scripts/banner.py` does the build, the checks and the render; your work is the questions, the copy and the judgement about what the result looks like.

Reply in the user's language (Portuguese in, Portuguese out). The words **on the banner** are English, British spelling, because the Summit's copy is — unless the user asks for another language, in which case say that a translation is not client-approved copy.

## Source of truth

| File | What it is |
|---|---|
| `references/FACTS.md` | Every fact a banner may state — dates, programme, the 200 cap, rate tiers, what is included, what is retired — dated, with its site source. **Read it in full on the first banner of a session.** It beats `PRODUCT.md` wherever they disagree |
| `references/banner-design.md` | How the site's design system lands on a web banner: navy ground, the three marks, layouts by shape, type, gold, motion, GIF mechanics, copy length by size. **Read before writing a spec** |
| `references/PRODUCT.md`, `references/DESIGN.md` | Verbatim copies of the site's own files: voice, positioning, what must never be invented; palette, type ramp and the named rules. `DESIGN.md` is the system the banners follow — navy ground, gold as the one light. `banner-design.md` says how it scales down to a banner |
| `references/data/*.json` | `rates.json`, `programme.json`, `site.json` — what `banner.py check` reads to validate prices and times |
| `assets/` | Fonts (Caladea, Archivo + licences) and the logos for a navy ground: the four W&M lockups (white + gold), the Global Citizen Solutions symbol and wordmark and CNN Portugal in white — the same files and pairing as the site's hero. Use as supplied; never recolour or redraw |

Everything is inside this folder; copy it alone to any machine with Python 3, `playwright` (with Chromium) and `pillow`. The site's repo (`gcs-wealth-migration-summit`) is read-only for this skill.

## Workflow

```
1. Ask            → size · PNG or animated GIF · (GIF) the maximum file size
2. Write the copy → confirmed facts only, sized to the banner
3. Build + check  → spec.json → HTML → lint the words, fit, contrast
4. Render         → PNG, or GIF squeezed under the limit
5. Look           → open every output; iterate
6. Hand off       → files, sizes, alt text, what to confirm
```

### 1 — Ask

Ask in the user's language, as one `AskUserQuestion` call when it is available (otherwise plain chat). Ask only what is missing; skip anything the message already answers.

1. **Size** — only if the user gave none. Offer the usual ones (`python3 scripts/banner.py presets`): 300x250, 728x90, 970x250, 300x600, 160x600, 320x50 — and "other (WxH)". More than one size is fine: one spec per size, same copy.
2. **Output** — *always ask*, unless the user already said it: **PNG** (static) or **GIF** (animated).
3. **GIF only — maximum file size.** Ask what ceiling the placement allows. Offer 150 KB (the usual ceiling for display networks), 300 KB, 1 MB, and "other". Never guess it and never skip it: the whole encoder is built to land under this number, and a GIF over a platform's limit is rejected on upload.

Do not ask about copy, language, fonts or colours — they are fixed or inferable. If the user gave several sizes and the output is GIF, one size limit covers all unless they say otherwise.

Defaults you state in the hand-off rather than ask: a GIF plays **3 times and stops on the final frame** (the common display-network rule; `--plays 0` loops forever for a site or newsletter that wants it), the banner has a **1px hairline border** (`"border": false` removes it).

### 2 — Write the copy

Two modes, chosen before touching the text:

- **A — you author** (a topic or a goal): write inside the confirmed facts. Every claim must trace to `FACTS.md` or text the user supplied. The programme is the argument: a specific fact beats an adjective. Usable lines: the site's hero ("Your residency, your citizenship, your Plan B. Don't let the world decide for you."), the service line (`5–6 November 2026 · Lisbon`), "Limited to 200 attendees", "2 days · 10 workshops · 28 speakers" (written as words: *Two days. Ten workshops. Twenty-eight speakers.*), a day theme, a workshop title verbatim from `programme.json`.
- **B — the user gives finished copy**: keep it verbatim. Shorten only by splitting across scenes; never reword, and flag (don't fix) spelling the site itself mixes.

The CTA is **"Secure your place"** — a booking, which the site takes payment for. Not "Register your interest", not "Book now".

**Sized to the banner** (the checker will fail copy that does not fit, but write short in the first place):

| Banner | Headline | Notes |
|---|---|---|
| ≥ 250 tall, or ≥ 300 wide boxes | up to 12 words | rule + service line shown |
| 90–120 tall (728x90, 970x90) | 5–9 words | service line shown, no rule |
| ≤ 60 tall (320x50, 468x60) | 2–4 words | no second line; on 320x50 the Summit lockup is left out so the GCS and CNN marks fit — put the event name in the headline |
| 120–160 wide skyscrapers | 5–8 words | wraps to many short lines — read it aloud |

A banner is read in two seconds: **one message, one button**. Use **scenes** (1–3, each its own headline) only when the user wants a sequence or the facts do not fit one line; the button appears on the last scene only. Scene 1 is never "Hi" — it is the most important thing.

### 3 — Build and check

Write the spec from Python (`Path.write_text(json.dumps(...))`), never a shell heredoc. Fields and defaults are in the docstring of `scripts/banner.py`; the common case:

```json
{
  "name": "plan-b",
  "width": 300, "height": 250,
  "scenes": [
    {"headline": "Your residency, your citizenship, your Plan B."},
    {"headline": "Two days. Ten workshops. Twenty-eight speakers.", "subline": "Limited to 200 attendees"}
  ],
  "cta": "Secure your place"
}
```

`subline` defaults to the service line (`5–6 November 2026 · Lisbon`); set it to `""` to drop it. Then:

```bash
python3 <SKILL_DIR>/scripts/banner.py build  plan-b.json --out <out dir>
python3 <SKILL_DIR>/scripts/banner.py check  <out dir>/plan-b_300x250.html --on <date it goes live>
```

`check` renders in a real browser and reports. Fix every **ERROR**, read every **WARN**:

- *copy does not fit at 12px or larger* / *text is clipped* — the copy is too long for the box. Shorten it, drop the subline (`"subline": ""`), use fewer scenes, or `"cta": null`. Do not shrink type below 12px; that floor is the site's.
- *price … is not the tier in force* — a price is only ever the published tier on the date the banner goes live (`€399` to 3 Oct, `€499` to 30 Oct, `€599` to 4 Nov); outside 1 Sep–4 Nov say nothing about price. Pass `--on` with the go-live date.
- *urgency mechanic*, *stale or retired fact*, *exclamation mark*, *emoji* — see "What this skill will not do".
- *a URL is printed on the graphic* — fine when the user asked for it in this conversation (set `"url_confirmed": true`, and say in the hand-off that the site may still sit behind its staging gate); otherwise leave it off — the click-through belongs to the placement, not to the artwork. A URL line is set in lowercase automatically (capitals with wide tracking would not fit); never patch the HTML by hand after `build`, change the spec instead, so a rebuild reproduces it.
- *the GCS and CNN Portugal marks are missing* / *elements overlap* — the marks are mandatory and need room; shorten the copy, drop the button, or use a bigger banner. There is no switch to remove them.
- *contrast* — the checker computes every text element (gold is a ground for the button and a rule, never small text on white).

### 4 — Render

```bash
python3 <SKILL_DIR>/scripts/banner.py render <html> --type png [--scale 2] [--max-kb N]
python3 <SKILL_DIR>/scripts/banner.py render <html> --type gif --max-kb 150 [--plays 3]
```

- **PNG** is the final state of the banner at exactly the given size. `--scale 2` also writes an `@2x` file for retina screens.
- **GIF** is captured frame by frame from the page's animation, identical frames are merged (holds cost nothing), then it walks a quality ladder — more colours → fewer colours → fewer frames per second — until the file is under `--max-kb`. **It never changes the dimensions.** It also writes `<name>_static.png`, the final state, because mail clients such as Outlook show only a GIF's first frame (the first frame here is the logo alone) and some placements block animation.
- Exit code 2 means the GIF could not reach the limit; the smallest attempt is kept. Offer the user the real options: shorter copy, one scene fewer, or a higher limit. Do not quietly change the size or ship a file over their ceiling.

### 5 — Look at it

A script passing is not the same as the banner being good. **Read every PNG**, and for a GIF make a contact sheet and read that: `python3 <SKILL_DIR>/scripts/banner.py sheet <gif>` (12 frames; `--frames N` for more). Judge as a person would: is the headline the biggest thing, is the button obvious, does the empty navy feel intentional, are the three marks readable at this size, does the animation read in order (headline → rule → date → button)? If something is off, edit the spec, `build` again, re-check, re-render — the pipeline is idempotent. Show the user the result (`SendUserFile` when available) and let them steer in chat. Only their approval ends the loop.

### 6 — Hand off

Say, in the reply, each that applies:

- the files and their real sizes (`banner.py` prints them), and for a GIF the limit it landed under, colours / fps / seconds per play / plays;
- the **alt text**, one line per banner (what is visible and what it says, ≤ 125 characters) — the user needs it where they place the image;
- the rate tier on the banner and the date it stops being true — or that no price is shown;
- anything to confirm before publishing: the click-through URL (the site may still sit behind its staging gate), the venue spelling (the site writes both *Marques* and *Marquês*; the banner uses what you were given);
- the static companion for GIFs and why (first-frame clients);
- small-size warnings from `check` (partner marks under ~18px high, a headline under 16px);
- that `--plays`, `--scale` and `"border"` are adjustable if they want something other than the defaults.

Then offer: the same copy at another size; a variant; a static PNG fallback for a GIF placement.

## What this skill will not do

The brand and the evidence on hand set hard edges. Never, in any mode:

- invent **sponsor or partner roles, testimonials, past-edition figures, attendance so far**, or photography of Lisbon / the venue owned by GCS (none exists);
- state a **price** that is not one of the three published tiers, or not the tier in force on the go-live date; use **urgency mechanics** ("last chance", "only N seats", "book now"). Scarcity is factual and said once: "Limited to 200 attendees." A deadline is a date;
- put any **partner or sponsor logo other than Global Citizen Solutions and CNN Portugal** on a banner unless the user names it for this banner and confirms it is cleared (the site never says what each logo is). The user decided on 2026-10-20 that every banner carries GCS and CNN Portugal — the pair the site's hero shows beside the title — so those two are always on, with no wording that gives either a role ("official partner of…", "in partnership with…");
- name a **speaker**, draw a portrait, or pair a speaker with a session — this skill is typographic. Speaker spotlights belong to `wm-social-media`, which carries the roster and the rules;
- state a session title or time that is not in `references/data/programme.json`, compute end times, or give a "session" count (the countable facts are 2 days · 10 workshops · 28 speakers);
- print a **URL** on the artwork the user did not ask for or confirm;
- use a retired fact: "Golden Visa Pathway" / "Structuring, Context & Experience" day themes, a 150–200 cap, a networking dinner, "Register your interest", the older "passport programme" vocabulary (`FACTS.md` lists them; `check` rejects them);
- set type below 12px, small gold text, or a headline in capitals (sentence case, exactly as written; capitals are for labels only).

## Outputs and naming

Write to `/mnt/user-data/outputs/` when it exists, otherwise `./output/<slug>/` (`slug` = the banner's topic in `kebab-case`).

| Output | Files |
|---|---|
| PNG | `<slug>_<W>x<H>.html` · `<slug>_<W>x<H>.png` (· `…@2x.png`) |
| GIF | `<slug>_<W>x<H>.html` · `<slug>_<W>x<H>.gif` · `<slug>_<W>x<H>_static.png` |

The HTML is the editable source (spec embedded, fonts and logos inlined — click it in a browser to replay the animation). Keep it with the renders.

> **Reminder:** ask size · PNG or GIF · the GIF's size limit — then write short copy from confirmed facts, `check` before `render`, look at every output, never change the dimensions to hit a size limit.
