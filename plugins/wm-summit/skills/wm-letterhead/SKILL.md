---
name: wm-letterhead
description: "Creates the A4 letterhead (papel timbrado) of the Wealth and Migration Summit 2026 (Lisbon, 5–6 Nov 2026, curated by Global Citizen Solutions) as an editable Word .docx: the Summit's horizontal blue logo in the header; in the footer the title, the Global Citizen Solutions mark and the Summit website (a live link), on every page. Delivers a blank letterhead to type into, or pours the user's own letter (date, recipient, subject, body, signatory) in verbatim. Builds with python-docx, checks A4 / logos / footer / alt text, renders through LibreOffice and shows a PNG preview. Use whenever the user mentions a letterhead, papel timbrado, timbre, carta, ofício, letter template or Word stationery for the Summit — even just 'a carta do Summit em Word'. Not for decks, banners, social posts or PDF brochures (other w&m skills), not for editing someone else's .docx (docx skill), not for general GCS letterhead (gcs-word)."
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "First version. Layout is this skill's own (no Summit stationery spec exists) on the skeleton of the GCS house letterhead (GCS-General.docx: logo + hairline header, hairline footer, 24 mm margins); brand facts and palette from the site repo at ab1fe08; the GCS mark is the official GCS-Secondary-Blue from the GCS brand package, alone (no CNN Portugal) — the user's decision of 2026-10-21, the one exception to the white-ground pair of the other Summit skills; --fonts brand embeds Caladea + Archivo. Tested on 4 prompts with and without the skill (iteration 2: 100% vs 92% of assertions, 37 s vs 323 s)."
---

# Letterhead — Wealth & Migration Summit 2026

One job: produce the Summit's **A4 letterhead as a `.docx`** — header logo, footer with title, GCS mark and website — either **blank** or with the user's **letter already poured in**. `scripts/letterhead.py` does the build, the checks and the preview; your work is the few questions, handing it the user's text untouched, and looking at the result.

Reply in the user's language (Portuguese in, Portuguese out). Text **on the letterhead** (footer title, anything you set) is English unless the user gives other text — the Summit's copy is English, British spelling.

## What the user asked for, exactly

| Zone | Content |
|---|---|
| Header | Summit **horizontal blue** logo (`assets/logos/wm-horizontal-blue`), left, 80 mm wide, with a gold hairline under it |
| Footer | **title** (default *Wealth and Migration Summit 2026*) · **GCS** mark (the official one-line lockup, GCS blue) · **website** (*wealthandmigrationsummit.com*) |
| Page | A4 portrait, same header and footer on every page |
| Output | `.docx` |

"Título" was read as the event title; if the user meant another title, pass it (`--title`). Everything else about the layout — margins, hairlines, type — is in `references/brand.md` with the reasoning, so you can answer "why is it like that" and change it deliberately.

## Source of truth

| File | What it is |
|---|---|
| `references/brand.md` | Facts the letterhead may state, palette, which logo file is used where, type, geometry in millimetres, and **the gaps the site repo leaves open**. Read it before changing the layout or when the user asks for something it does not cover |
| `assets/logos/` | The two logos Word embeds: the Summit's horizontal blue lockup and the official `GCS-Secondary-Blue` (PNG, built from the SVG sources next to them). Use as supplied — never recolour, redraw, crop or put words around them. If a GCS logo is missing in blue, take the official one from the GCS brand package; never tint a white one |
| `assets/fonts/` | Caladea + Archivo (OFL), embedded only with `--fonts brand` |
| `scripts/letterhead.py` | `build` (docx + checks + preview) and `check` (any letterhead docx) |
| `scripts/prepare_logos.py` | Rebuilds the PNGs from the SVGs; only when a logo changes |

The site repo (`gcs-wealth-migration-summit`) is read-only for this skill. Needs Python 3 with `python-docx`; the render step also uses LibreOffice (`soffice`) and poppler, and says so when they are missing.

## Workflow

```
1. Ask (only what's missing)  → blank or a letter? · another footer title/website?
2. Write the spec             → defaults need none; a letter goes in verbatim
3. Build                      → letterhead.py build  (docx + checks + preview PNG)
4. Look                       → open every preview page; iterate
5. Hand off                   → file, what is on it, what to confirm
```

### 1 — Ask

Ask in one go, only what the message does not answer (`AskUserQuestion` if available, otherwise chat):

1. **Blank letterhead or a letter?** If the user already pasted or attached the text, it is a letter — don't ask.
2. Anything to change from the defaults? Offer them, don't interrogate: footer title *Wealth and Migration Summit 2026*, website *wealthandmigrationsummit.com*, gold hairline under the header (on), fonts Cambria + Arial.

Do not ask about margins, colours or logos — they are fixed by the brand.

### 2 — Spec

Defaults need no spec: `python3 <SKILL_DIR>/scripts/letterhead.py build --out <dir>` makes the blank letterhead. For a letter, or several overrides, write the spec from Python (`Path.write_text(json.dumps(...))`, never a shell heredoc — apostrophes and accents break it) **into the output folder, named after the file** (`<out>/<name>.spec.json`). A shared temp path such as `/tmp/spec.json` gets overwritten when two letters are built at once, and a spec kept beside its `.docx` makes a rebuild reproducible. Keys are listed in the script's docstring:

```json
{
  "name": "carta-parceria",
  "title": "Wealth and Migration Summit 2026",
  "url": "wealthandmigrationsummit.com",
  "letter": {
    "date": "20 October 2026",
    "recipient": ["Name", "Company", "Address"],
    "subject": "Subject line",
    "salutation": "Dear Name,",
    "body": ["First paragraph.", "Second paragraph."],
    "closing": "Yours sincerely,",
    "signatory": ["Name", "Role"]
  }
}
```

**The letter is the user's text, verbatim.** One body paragraph per list item. Don't reword, correct, add a claim, invent a signatory or fill a missing field — leave it out and say so. If the user wants you to *draft* the letter, that is a separate job: use `gcs-writer`, then bring the approved text here; facts about the Summit come from `wm-web-banners/references/FACTS.md` (dates, venue, the 200 cap), never from memory.

### 3 — Build

```bash
python3 <SKILL_DIR>/scripts/letterhead.py build spec.json --out <out dir>
python3 <SKILL_DIR>/scripts/letterhead.py check <out dir>/<name>.docx      # any existing letterhead
```

`build` writes the `.docx`, runs the checks and renders `<name>_preview-N.png`. Fix every **ERROR**, read every **WARN**:

- *not A4 portrait*, *picture is not the supplied logo*, *no alt text*, *footer has no link* — the file was edited or built by hand; rebuild from the script rather than patching.
- *a N mm picture sits in a M mm cell* — LibreOffice clips pictures that nearly fill their cell; widen the column or shrink the picture (constants at the top of the script).
- *title is N characters* — it will wrap to two lines in the footer. Shorten it or accept two lines.
- *fonts outside the brand sets* — only Cambria + Arial (default) or Caladea + Archivo (`--fonts brand`, embedded) belong here.
- *brand fonts used but not embedded* — the file was not built through the script.
- *render failed / skipped* — no LibreOffice or poppler on this machine; say so, and ask the user to open the file in Word.

### 4 — Look at it

A passing check is not a good page. **Read every preview PNG**: logo crisp and left-aligned with the text edge, gold hairline under it, nothing between the header and the date, footer hairline with the three zones on one line (or two lines for a long title), the GCS mark complete (not cut at the right), the website readable, the signature block not orphaned on a page of its own. With a long letter, look at page 2 too — the header and footer must repeat. If something is off, change the spec or the constants, rebuild — the pipeline is idempotent. Show the user the preview (`SendUserFile` when available) and let them steer. Only their approval ends the loop.

### 5 — Hand off

Say, in the reply:

- the file and where it is, and whether it is blank or holds the letter;
- what is on it in one line (header logo · footer title · GCS · website) and the page count;
- **fonts**, said plainly: the footer and the letter text are **Arial**; a letter's subject line is **Cambria** (an empty letterhead shows only the Arial footer). Both ship with Office, so it looks the same everywhere; `--fonts brand` switches to the real Caladea + Archivo, embedded in the file (Regular only; Word on Windows/Mac honours them, Word Online and some viewers fall back);
- **to confirm**: the website is printed because the user asked, but the site's own repo says it sits behind a staging password — has it gone public? And that "título" was read as the event title;
- what is *not* on it: no address, phone or e-mail, no CNN Portugal or partner mark, no page numbers — offer any of them (partner marks only after the user confirms they are cleared, with no wording that gives a partner a role).
- that it was checked against the OOXML schema and rendered in LibreOffice, not in Word — a quick look in Word is the final check.

Then offer: the same letterhead with another title for a specific team or programme; the brand fonts embedded; a page number in the footer (the GCS house letterhead has one); a version whose continuation pages drop the header; a `.dotx` template.

## What this skill will not do

- write, reword or "improve" letter text, invent a recipient, signatory, role, price or Summit claim, or fill a missing field with a placeholder that looks real;
- recolour, redraw, crop, stretch or caption the logos; use the white logos on white paper; set gold as text on white (it fails contrast — gold is the hairline and the logo's symbol only);
- add CNN Portugal or any other partner or sponsor logo, address, phone or e-mail the user did not give or confirm;
- put the footer in anything but the three zones asked for without saying so.

## Outputs and naming

Write to `/mnt/user-data/outputs/` when it exists, otherwise `./output/<name>/` (`name` in `kebab-case`: `wm-letterhead`, `carta-<assunto>`).

| Output | Files |
|---|---|
| Blank | `wm-letterhead.docx` · `wm-letterhead_preview-1.png` |
| Letter | `<name>.docx` · `<name>_preview-1.png` … one PNG per page |

> **Reminder:** blank or a letter → build with the script → read every preview page → the user's text goes in verbatim → say what to confirm (website gate, "título", Word check).
