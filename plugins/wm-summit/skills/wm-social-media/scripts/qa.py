"""QA for Summit social creatives — enforces the checkable rules of references/DESIGN.md.

    python3 qa.py lint  <deck.html>                 # rule lint on the slide markup + fact check (prices, times, names)
    python3 qa.py facts <deck.html>                 # fact check only — for HTML not built with build_document()
    python3 qa.py caption <caption.md> [deck.html]  # caption file: sections, tone, price, one alt text per slide
    python3 qa.py scrim <deck.html> <slide#> x y w h [white|mist|gold]   # ground luminance under a text box (text hidden); with a colour: contrast >= 3:1, for the cover
    python3 qa.py scrim-png <ground.png> x y w h       # same, on an image that already has no text
    python3 qa.py palette                           # contrast of every text/ground pair

Exit code 1 on any ERROR. WARN lines are judgement calls to look at, not blockers.
The fact check reads references/data/*.json through facts.py; see references/FACTS.md.
"""

from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

# ----------------------------------------------------------------------------
# Contrast
# ----------------------------------------------------------------------------


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(fg, bg, a):
    return tuple(round(f * a + b * (1 - a)) for f, b in zip(fg, bg))


def contrast(fg, bg):
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def check_palette(verbose=False) -> bool:
    from summit_assets import PALETTE as P
    c = {k: _hex(v) for k, v in P.items()}
    grounds = ["navy", "navy-deep", "dawn-low", "dawn-blue"]
    ok = True
    rows = []
    for g in grounds:
        for name, fg in (("white", c["white"]), ("mist", c["mist"]),
                         ("mist-dim (72%)", blend(c["mist"], c[g], .72)),
                         ("gold", c["gold"]), ("gold-bright", c["gold-bright"])):
            ratio = contrast(fg, c[g])
            rows.append((name, g, ratio, 4.5))
    # paper: navy text on white; ink-soft; gold must never be text on white (reported, expected to fail)
    rows.append(("navy", "white", contrast(c["navy"], c["white"]), 4.5))
    rows.append(("ink-soft (72%)", "white", contrast(blend(c["navy"], c["white"], .72), c["white"]), 4.5))
    gold_on_white = contrast(c["gold"], c["white"])
    for name, g, ratio, need in rows:
        flag = "ok " if ratio >= need else "FAIL"
        if ratio < need:
            ok = False
        if verbose:
            print(f"  {flag} {name:<16} on {g:<10} {ratio:5.2f}:1")
    if verbose:
        print(f"  --  gold on white    (never text) {gold_on_white:5.2f}:1  <- fails AA by design; gold is a mark on paper")
    return ok


# ----------------------------------------------------------------------------
# Scrim luminance — The Scrim Is Layered Rule: ground under text < 0.04
# ----------------------------------------------------------------------------

def _measure(im, label, x, y, w, h, text=None):
    """Ground luminance under a text box. Default: the house limit, p95 < 0.04.

    With `text` ('white' | 'mist' | 'gold' | 'navy') the cover rule applies instead: the client's reference cover keeps
    more of the photograph than 0.04 allows, so the gate is WCAG contrast of that text colour against the ground's
    p95 - at least 3:1 (large text and logos: 24px and up, or the marks). Use it on the cover only."""
    im = im.convert("RGB").crop((x, y, x + w, y + h))
    raw = im.tobytes()
    px = list(zip(raw[0::3], raw[1::3], raw[2::3]))
    lums = sorted(luminance(p) for p in px)
    mean = sum(lums) / len(lums)
    p95 = lums[int(len(lums) * .95)]
    if text:
        from summit_assets import PALETTE as P
        ratio = (luminance(_hex(P[text])) + 0.05) / (p95 + 0.05)
        ok = ratio >= 3.0
        print(f"{label}  box=({x},{y},{w},{h})  mean={mean:.4f}  p95={p95:.4f}  {text} contrast={ratio:.1f}:1  need 3:1 (4.5 for text under 24px)  -> {'ok' if ok else 'TOO LIGHT under text'}")
        return ok
    verdict = "ok" if p95 < 0.04 else "TOO LIGHT under text"
    print(f"{label}  box=({x},{y},{w},{h})  mean={mean:.4f}  p95={p95:.4f}  limit=0.04  -> {verdict}")
    return p95 < 0.04


def scrim_png(png, x, y, w, h, text=None):
    """For an image that already has no text on it (a photograph + scrims only)."""
    from PIL import Image
    return _measure(Image.open(png), png, x, y, w, h, text)


def scrim(html, slide, x, y, w, h, text=None):
    """Render slide N of the deck with all type hidden, then measure the ground under the box.

    Measuring a finished PNG would count the white glyphs themselves; the rule is about
    the ground the text sits on."""
    import asyncio, io
    from PIL import Image
    from playwright.async_api import async_playwright

    async def go():
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            pg = await b.new_page(viewport={"width": 1400, "height": 2200})
            await pg.goto(f"file://{Path(html).resolve()}", wait_until="networkidle")
            await pg.add_style_tag(content=".slide *{color:transparent !important} .reflect,.lamp-sq,.service::before{display:none !important} .slide img:not(.photo){visibility:hidden}")
            el = (await pg.query_selector_all("[data-slide]"))[slide - 1]
            png = await el.screenshot()
            await b.close()
            return png
    im = Image.open(io.BytesIO(asyncio.run(go())))
    return _measure(im, f"{html} slide {slide}", x, y, w, h, text)


# ----------------------------------------------------------------------------
# Lint
# ----------------------------------------------------------------------------

FORBIDDEN_LEGACY = ["Yrsa", "Heebo", "#000957", "#3F8CFF", "#ECF4FF", "Night Blue", "Electric Blue",
                    "Trustpilot", "border-radius:50px", "background-cta"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")

# Facts that were true in an earlier copy deck / PRODUCT.md and are not any more (references/FACTS.md,
# "What PRODUCT.md still says that is no longer true"). Plain text, matched case-insensitively.
STALE_FACTS = {
    "golden visa pathway": "Day One theme is now 'The New Geography of Wealth & Mobility'",
    "structuring, context": "Day Two theme is now 'Global Wealth & the International Family'",
    "networking dinner": "there is no dinner; Day Two has a cocktail reception, both days have networking lunches",
    "private dinner": "there is no dinner",
    "150–200": "capacity is 'Limited to 200'",
    "150-200": "capacity is 'Limited to 200'",
    "150 curated": "capacity is 'Limited to 200'",
    "14 named speakers": "the site lists 26 speakers",
    "14 speakers": "the site lists 26 speakers",
    "register your interest": None,  # WARN, not ERROR: CTA is now 'Secure your place'
}
# On the agenda page of 16 Oct but not a speaker card on the site — never named (FACTS.md, Speakers).
AGENDA_ONLY_NAMES = ["Maggie Williams", "Grazi Fulchiron", "Sheree M. Mitchell", "Adrien Bridge", "Joana Costa",
                     "Diogo Pedro", "Joana M.", "Gonçalo Peixoto", "Lourenço Alvares", "Gizane Campos"]
# The two marks the site hero shows next to the title (and the skill's cover / closing slides carry by default).
# Every other partner logo needs the user's confirmation for the post.
HERO_MARKS = {"Global Citizen Solutions", "CNN Portugal"}
TIME = re.compile(r"(?<![\d:])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])")


def _facts():
    try:
        import facts
        return facts
    except (ImportError, FileNotFoundError) as e:
        print(f"WARN  fact check skipped — {e}")
        return None


def _fact_check(F, tag, txt, errors, warns, today=None):
    """Prices against the published tiers, times against the published programme, names against the roster."""
    from datetime import date
    today = today or date.today()
    low = txt.lower()
    for stale, why in STALE_FACTS.items():
        if stale in low:
            (warns if why is None else errors).append(
                f"{tag}: '{stale}' — " + (why or "the CTA is now 'Secure your place' (a booking, not an enquiry)"))
    # prices
    for m in re.finditer(r"€\s?(\d[\d,.]*)|\b(\d[\d,.]*)\s?(?:euros?|eur)\b", txt, re.I):
        amount = int(re.sub(r"\D", "", (m.group(1) or m.group(2)).split(".")[0].replace(",", "")) or 0)
        tiers = [t for t in F.rates()["tiers"] if t["eur"] == amount]
        if not tiers:
            errors.append(f"{tag}: €{amount} is not a published rate ({', '.join('€%d' % a for a in sorted(F.published_amounts()))})")
            continue
        t = tiers[0]
        if date.fromisoformat(t["end"]) < today:
            errors.append(f"{tag}: €{amount} was the {t['name']} and ended {t['when'].split('–')[-1].strip()} — not true today")
        elif date.fromisoformat(t["start"]) > today:
            warns.append(f"{tag}: €{amount} is the {t['name']}, which starts {t['when'].split('–')[0].strip()} — true only from then")
        else:
            warns.append(f"{tag}: €{amount} ({t['name']}) is in force until {t['when'].split('–')[-1].strip()} — say so in the hand-off")
    # times
    known = F.known_times()
    for m in TIME.finditer(txt):
        hhmm = f"{int(m.group(1)):02d}:{m.group(2)}"
        if hhmm not in known:
            errors.append(f"{tag}: time {hhmm} is not on the site's programme (FACTS.md → Programme)")
    # names that must not appear
    for name in AGENDA_ONLY_NAMES:
        if name.lower() in low:
            errors.append(f"{tag}: '{name}' is not a speaker on the site — agenda-only name (FACTS.md → Speakers)")
    if "turkey" in low:
        warns.append(f"{tag}: Turkey — in the site's intro sentence but there is no Turkey workshop in the timed programme")


def lint(path):
    from bs4 import BeautifulSoup
    html = Path(path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    for s in soup.find_all("style"):
        s.decompose()
    errors, warns = [], []
    F = _facts()
    if F:
        for note in F.freshness():
            print("NOTE ", note)

    slides = soup.select("[data-slide]")
    if not slides:
        errors.append("no [data-slide] elements found")

    body_text = soup.get_text(" ")
    for bad in FORBIDDEN_LEGACY:
        if bad in str(soup):
            errors.append(f"legacy GCS-social artefact present: {bad!r}")

    for n, sl in enumerate(slides, 1):
        tag = f"slide {n}"
        # --- inline style rules
        for el in sl.find_all(style=True):
            st = el["style"].replace(" ", "").lower()
            where = f"{tag} <{el.name}>"
            if re.search(r"font-(size|family|weight)\s*:", el["style"], re.I):
                errors.append(f"{where}: inline font-size/family/weight — use a type class (the ramp is closed)")
            if re.search(r"rgba?\(", st):
                errors.append(f"{where}: literal rgb()/rgba() — name an alpha role token")
            if re.search(r"#[0-9a-f]{3,6}\b", st) and "mask-image" not in st:
                errors.append(f"{where}: literal hex colour — use a palette token var(--…)")
            if re.search(r"(box|text)-shadow|drop-shadow", st) and not re.search(r"var\(--(glow|lift)", st):
                errors.append(f"{where}: shadow not from a light-source token (--glow-*, --lift-night)")
            for m in re.finditer(r"border-radius:([^;]+)", st):
                if m.group(1) not in ("0", "0px", "50%"):
                    errors.append(f"{where}: border-radius {m.group(1)} — square system (0), 50% only for lamps")
            if re.search(r"border-(left|right)\s*:", st) and not re.search(r"border-(left|right):(0|none)", st):
                errors.append(f"{where}: coloured side-stripe border — use a hairline above instead")
            if "font-style:italic" in st:
                errors.append(f"{where}: italic — not part of the system")
        # --- external images
        for img in sl.find_all("img"):
            if str(img.get("src", "")).startswith("http"):
                errors.append(f"{tag}: external <img src> — embed as data: URI")
        # --- masthead
        if not sl.select_one(".lockup"):
            errors.append(f"{tag}: no masthead lockup (.lockup)")
        # --- one light
        if len(sl.select(".lit")) > 1:
            errors.append(f"{tag}: {len(sl.select('.lit'))} lit gold blocks — One Light Rule")
        # --- gold text on paper
        for panel in sl.select(".panel"):
            for el in panel.select(".ink-gold, .ink-gold-bright, .service, .day"):
                errors.append(f"{tag}: gold text inside the white panel — gold never touches paper")
            for el in panel.find_all(style=True):
                if re.search(r"color:var\(--gold", el["style"].replace(" ", "")):
                    errors.append(f"{tag}: gold colour inside the white panel")
        if len(sl.select(".panel")) > 1:
            errors.append(f"{tag}: more than one white panel on a slide")
        # --- white slides (alternate with navy): gold is a mark, never text; no paper on paper
        if "g-white" in sl.get("class", []):
            if sl.select(".panel"):
                errors.append(f"{tag}: a white panel on a white slide — paper on paper")
            if sl.select(".photo, .scrim-cross, .scrim-rise, .scrim-cover"):
                errors.append(f"{tag}: photograph scrim on a white slide")
            for el in sl.select(".ink-gold, .ink-gold-bright"):
                errors.append(f"{tag}: gold text on a white slide — gold never touches paper (use it as a rule, dot or the .lit block)")
            for el in sl.find_all(style=True):
                if re.search(r"color:var\(--gold", el["style"].replace(" ", "")):
                    errors.append(f"{tag}: gold colour on a white slide")
        # --- logos: the GCS mark stands alone (no text above, beside or over it)
        for img in sl.find_all("img"):
            if (img.get("alt") or "").strip() == "Global Citizen Solutions":
                box = img.parent
                texts = [c.get_text(strip=True) if hasattr(c, "get_text") else str(c).strip() for c in box.children if c is not img]
                if any(texts):
                    errors.append(f"{tag}: '{next(x for x in texts if x)[:30]}' next to the Global Citizen Solutions mark — nothing is written above, beside or over it")
        # --- eyebrows
        for h in sl.find_all(["h1", "h2", "h3"]):
            prev = h.find_previous_sibling()
            if prev is not None:
                cls = set(prev.get("class", []))
                if cls & {"label", "label-sm"} and not cls & {"service", "day"}:
                    errors.append(f"{tag}: eyebrow label above a heading — only the service line / day marker may sit there")
        # --- length
        for h in sl.select(".display, .headline"):
            words = len(h.get_text(" ").split())
            if words > 14:
                warns.append(f"{tag}: headline {words} words (aim ≤ 12)")
        for b in sl.select(".body, .lead"):
            words = len(b.get_text(" ").split())
            if words > 45:
                warns.append(f"{tag}: body/lead {words} words (aim ≤ 40) — split the slide")
        # --- tone
        txt = sl.get_text(" ")
        if "!" in txt:
            errors.append(f"{tag}: exclamation mark — voice is restrained")
        if EMOJI.search(txt):
            errors.append(f"{tag}: emoji")
        if re.search(r"\b(last chance|only \d+ (seats|places)|hurry|don'?t miss|sold out|book now)\b", txt, re.I):
            errors.append(f"{tag}: urgency mechanics — scarcity is factual (~150–200 curated delegates), never theatrical")
        if F:
            _fact_check(F, tag, txt, errors, warns)
            for el in sl.select(".session"):
                title = " ".join(el.get_text(" ").split())
                if title and not F.find_session(title):
                    warns.append(f"{tag}: session title not found verbatim in the programme — '{title[:70]}'")
            # --- partner / sponsor marks: roles are unconfirmed (FACTS.md → Partners and media)
            partners = [p for p in F.site()["partner_logos_on_site"] if p not in HERO_MARKS]
            for img in sl.find_all("img"):
                alt = (img.get("alt") or "").strip()
                if alt and any(alt.lower() == p.lower() or alt.lower() in p.lower() for p in partners):
                    warns.append(f"{tag}: partner logo '{alt}' — only if the user named it for this post and confirmed it is cleared for social")
        elif re.search(r"[€$£]\s?\d|\b\d+\s?(euro|usd|eur)\b", txt, re.I):
            warns.append(f"{tag}: a price appears and the fact data is missing — check it against references/FACTS.md")
        if re.search(r"\b(organized|program\b|color\b|authorized)", txt):
            warns.append(f"{tag}: US spelling — authored copy is British (programme, organised). Verbatim site copy keeps its own spelling (the site writes 'organized')")

    tones = ["white" if "g-white" in sl.get("class", []) else "dark" for sl in slides]
    for i in range(1, len(tones)):
        if tones[i] == tones[i - 1] == "white":
            warns.append(f"slides {i} and {i + 1}: two white slides in a row — alternate white and navy")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(slides)} slide(s) · {len(errors)} error(s) · {len(warns)} warning(s)")
    return not errors


def facts_only(path):
    """Fact check alone — for HTML the design lint does not apply to (not built with build_document)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(Path(path).read_text(encoding="utf-8"), "lxml")
    for s in soup.find_all(["style", "script"]):
        s.decompose()
    F = _facts()
    if not F:
        return False
    for note in F.freshness():
        print("NOTE ", note)
    errors, warns = [], []
    slides = soup.select("[data-slide]") or [soup.body]
    for n, sl in enumerate(slides, 1):
        tag = f"slide {n}"
        txt = sl.get_text(" ")
        _fact_check(F, tag, txt, errors, warns)
        if "!" in txt:
            errors.append(f"{tag}: exclamation mark — voice is restrained")
        partners = [p for p in F.site()["partner_logos_on_site"] if p not in HERO_MARKS]
        for img in sl.find_all("img"):
            alt = (img.get("alt") or "").strip()
            if alt and any(alt.lower() == p.lower() or alt.lower() in p.lower() for p in partners):
                warns.append(f"{tag}: partner logo '{alt}' — only if the user named it for this post and confirmed it is cleared for social")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\nfacts · {len(slides)} slide(s) · {len(errors)} error(s) · {len(warns)} warning(s)")
    return not errors


# ----------------------------------------------------------------------------
# Caption file — the part of a job that makes it publishable (references/content-playbook.md)
# ----------------------------------------------------------------------------

def caption(path, deck=None):
    md = Path(path).read_text(encoding="utf-8")
    errors, warns = [], []
    for h in ("## Caption", "## Alt text", "## Before publishing"):
        if h not in md:
            errors.append(f"missing section '{h}'")
    for field in ("Facts as of:", "Platform:"):
        if field not in md:
            errors.append(f"missing header line '{field}'")
    cap = md.split("## Caption", 1)[-1].split("## Alt text", 1)[0]
    alt = md.split("## Alt text", 1)[-1].split("## Before publishing", 1)[0]
    alts = re.findall(r"^\s*(?:Slide|Frame)\s*\d+\s*[—–-]\s*(\S.*)$", alt, re.M)
    if EMOJI.search(md):
        errors.append("emoji — voice is restrained")
    if "!" in cap:
        errors.append("exclamation mark in the caption")
    if re.search(r"\b(last chance|only \d+ (seats|places)|hurry|don'?t miss|sold out|book now)\b", cap, re.I):
        errors.append("urgency mechanics in the caption — scarcity is factual ('Limited to 200 attendees')")
    if re.search(r"(?<!\w)#\w+", cap):
        warns.append("hashtags present — only keep ones the user supplied")
    if re.search(r"https?://\S+", cap):
        warns.append("a URL is in the caption — it must be one the user confirmed (FACTS.md → Booking)")
    if len(cap.split()) > 160:
        warns.append(f"caption is {len(cap.split())} words (aim 60–120)")
    for a in alts:
        if len(a) > 125:
            warns.append(f"alt text over 125 characters: '{a[:50]}…'")
    if deck:
        from bs4 import BeautifulSoup
        n = len(BeautifulSoup(Path(deck).read_text(encoding="utf-8"), "lxml").select("[data-slide]"))
        if len(alts) != n:
            errors.append(f"{len(alts)} alt text line(s) for {n} slide(s) — one per slide, 'Slide N — …'")
    elif not alts:
        errors.append("no alt text lines ('Slide N — …')")
    F = _facts()
    if F:
        _fact_check(F, "caption", cap, errors, warns)
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\ncaption · {len(alts)} alt text(s) · {len(errors)} error(s) · {len(warns)} warning(s)")
    return not errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "lint":
        sys.exit(0 if lint(sys.argv[2]) else 1)
    if cmd == "facts":
        sys.exit(0 if facts_only(sys.argv[2]) else 1)
    if cmd == "caption":
        sys.exit(0 if caption(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None) else 1)
    if cmd == "scrim":
        a = [int(v) for v in sys.argv[3:8]]
        sys.exit(0 if scrim(sys.argv[2], *a, text=(sys.argv[8] if len(sys.argv) > 8 else None)) else 1)
    if cmd == "scrim-png":
        a = [int(v) for v in sys.argv[3:7]]
        sys.exit(0 if scrim_png(sys.argv[2], *a) else 1)
    if cmd == "palette":
        sys.exit(0 if check_palette(verbose=True) else 1)
    print(__doc__)
    sys.exit(2)
