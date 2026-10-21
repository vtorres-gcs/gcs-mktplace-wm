#!/usr/bin/env python3
"""Wealth & Migration Summit paid ads: ad pack JSON -> checked copy, upload files, image creatives.

    python3 ads.py rate      [--on YYYY-MM-DD]            # which rate tier is in force, and when it changes
    python3 ads.py formats [--platform google|meta]
    python3 ads.py lint      pack.json [--on YYYY-MM-DD] [--today YYYY-MM-DD]
    python3 ads.py export    pack.json --out DIR
    python3 ads.py render    pack.json --out DIR [--creative ID] [--only FORMAT,...] [--keep-html]
    python3 ads.py check     DIR
    python3 ads.py preflight URL [--pack pack.json]      # does the page load, and does its price match the ad's?
    python3 ads.py photo     IMAGE --out DIR --formats F,F [--focus 0.5,0.4] [--name slug]   # crop a CLIENT-CLEARED photo, no overlay
    python3 ads.py build     pack.json --out DIR          # lint (stops on errors) + export + render + check

Limits and sizes come from references/specs.json; facts (rate tiers, programme times) from references/data/.
The navy ground, type and marks come from this folder. Needs Python 3, `playwright` (with Chromium) and `pillow`.
HTML is always written from Python, never a shell heredoc (base64 and `$` get mangled).

Ad pack (JSON). Everything is optional except `name`; lint says what an upload still needs:

    {
      "name": "plan-b-final-rate",
      "goes_live": "2026-10-31", "ends": "2026-11-04",
      "final_url": "https://wealthandmigrationsummit.com/", "url_confirmed": false,
      "utm": {"campaign": "wms26-final-rate"},
      "business_name": "Wealth & Migration Summit",
      "google": {
        "rsa": {"campaign": "...", "ad_group": "...", "path1": "Summit", "path2": "Lisbon",
                "headlines": ["text" | {"text": "...", "pin": 1}, ...], "descriptions": [...]},     # dict or list of dicts
        "display":    {"short_headlines": [...], "long_headline": "...", "descriptions": [...]},
        "pmax":       {"short_headlines": [...], "long_headlines": [...], "descriptions": [...]},
        "demand_gen": {"headlines": [...], "descriptions": [...]},
        "cta": "Learn more"
      },
      "meta": {"primary_texts": [...], "headlines": [...], "descriptions": [...], "cta": "Learn more"},
      "creatives": [
        {"id": "plan-b", "headline": "Your residency, your citizenship, your Plan B.",
         "subline": "5–6 November 2026 · Lisbon",          # default; "" drops it
         "support": "Two days. Ten workshops.",             # optional one quiet line under the headline
         "marks": "gcs-cnn",                                # gcs-cnn (default) | summit-only
         "formats": ["meta_feed_4x5", "meta_story_9x16", "google_landscape", "google_square"],
         "by_format": {"meta_story_9x16": {"headline": "..."}},   # optional per-format override of headline / subline / support
         "style": "plate"}                                         # google formats default to 'plate' (service line + headline, no lockup,
                                                                   # no marks, no support line); meta formats to 'full'; set to override
      ],
      "google_logos": true                                   # also write the 1:1 and 4:1 Google logo assets
    }
"""

from datetime import date
from pathlib import Path
from string import Template
import argparse
import base64
import csv
import html
import json
import re
import sys
import urllib.error
import urllib.request

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
REFS = SKILL_DIR / "references"
DATA = REFS / "data"
SPECS = json.loads((REFS / "specs.json").read_text(encoding="utf-8"))

NAVY, GOLD, MIST, WHITE = "#121B31", "#C2A358", "#C8CCD7", "#FFFFFF"   # pinned by the site's DESIGN.md
SERVICE_LINE = "5–6 November 2026 · Lisbon"
EVENT_START = date(2026, 11, 5)
EVENT_END = date(2026, 11, 6)
BUSINESS_NAME = "Wealth & Migration Summit"

LOGOS = {  # key -> (file, intrinsic w, intrinsic h)
    "horizontal": ("wm/wm-horizontal-white.svg", 1124, 85),
    "default": ("wm/wm-default-white.svg", 523, 397),
}
GCS = ("gcs/gcs-primary-white.svg", 199, 71)          # symbol + wordmark in one file
CNN = ("cnn-portugal/cnn-portugal-white.png", 905, 625)


# ---------------------------------------------------------------------------------------------
# Facts — read from references/data, never typed
# ---------------------------------------------------------------------------------------------

def _data(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def tiers():
    return _data("rates.json")["tiers"]


def rate_on(on):
    for t in tiers():
        if date.fromisoformat(t["start"]) <= on <= date.fromisoformat(t["end"]):
            return t
    return None


def known_times():
    return {r["time"] for d in _data("programme.json")["days"] for k in ("main", "workshops") for r in d[k]}


# ---------------------------------------------------------------------------------------------
# Copy lint — the words in an ad, whichever platform shows them
# ---------------------------------------------------------------------------------------------

URGENCY = re.compile(
    r"last chance|book now|hurry|don[’']?t miss|don[’']?t wait|act now|limited time|only \d+ (?:seats?|places?|tickets?|spots?)"
    r"|running out|selling fast|filling (?:up |fast)|sold out|final call|ends soon|now or never|before it[’']?s too late"
    r"|(?:few|last) (?:seats?|places?|tickets?|spots?)(?: left)?|almost full|today only|expires", re.I)
COUNTDOWN = re.compile(r"\b\d+\s+days?\s+(?:to go|left|until|remaining)\b|\bcountdown\b", re.I)
GCS_TERMS = re.compile(r"relocation firm|passport shop|passport scheme|passport programme|borderless living|dream lifestyle|fallback option", re.I)
STALE = [
    (r"golden visa pathway", "retired Day One theme (now 'The New Geography of Wealth & Mobility')"),
    (r"structuring, context", "retired Day Two theme (now 'Global Wealth & the International Family')"),
    (r"\bdinner\b", "there is no networking dinner on the programme"),
    (r"\b150\b", "the cap is 200 attendees, not 150"),
    (r"register (?:your )?interest", "the CTA is 'Secure your place'"),
]
PAST_EDITION = re.compile(r"last year|previous edition|past edition|inaugural|\bannual\b|returns? (?:to|for)|now in its|\bedition\b", re.I)
OUTCOME = re.compile(
    r"\b(?:get|obtain|buy|purchase|secure|apply for|receive|claim|win)\s+(?:your\s+|a\s+|an\s+|the\s+)?(?:second\s+|new\s+|eu\s+|portuguese\s+)?"
    r"(?:passport|citizenship|visa|golden visa|residency|residence permit)\b", re.I)
GUARANTEE = re.compile(
    r"guarantee[ds]?|\bassured\b|risk[- ]free|no[- ]risk|100\s?%|fast[- ]track(?:ed)?|instant (?:visa|residency|citizenship|passport)"
    r"|approval in \d+|certain approval", re.I)
PERSONAL_ATTR = re.compile(
    r"\b(?:are you|you are|you[’']re|do you|if you(?:[’']re| are)|as a)\b[^.?!]{0,50}?\b(?:wealthy|rich|millionaire|high[- ]net[- ]worth|hnwi?|ultra[- ]high|immigrant|expat|refugee)\b", re.I)
YOUR_WEALTH = re.compile(r"\byour (?:wealth|net worth|fortune|millions)\b", re.I)
SUPERLATIVE = re.compile(r"\b(?:best|#1|number one|leading|premier|biggest|largest|unrivalled|unmatched|top[- ]rated|world[’']?s (?:largest|leading|first|best))\b", re.I)
OFFICIAL = re.compile(r"\bofficial\b", re.I)
FREE = re.compile(r"\bfree\b", re.I)
SOCIAL_ISSUE = re.compile(r"\bimmigra\w*|\bmigrants?\b|\basylum\b|\brefugees?\b|\bborders?\b|\bdeport\w*", re.I)
SANCTIONS = re.compile(r"\bsanction\w*|restricted nationals", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
URL = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(?:com|pt|org|net|io|co)\b|@[a-z0-9-]+\.", re.I)
PRICE = re.compile(r"(?:€|EUR\s?)\s?(\d[\d,.]*)|(\d[\d,.]*)\s?(?:€|EUR\b)", re.I)
TIME = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
CAPS = re.compile(r"\b[A-Z]{4,}\b")
CAPS_OK = {"IFICI", "CNN", "EPIC", "SANA"}   # acronyms are not shouting; "LISBON" or "SUMMIT" in capitals is
MONTHDAY = re.compile(r"\b(\d{1,2})(?:\s?(?:–|-|and|&)\s?(\d{1,2}))?\s+(Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?)\b", re.I)
DATE_OK = {("sep", 1), ("oct", 3), ("oct", 4), ("oct", 30), ("oct", 31), ("nov", 4), ("nov", 5), ("nov", 6)}
WORDNUM = {"two": 2, "ten": 10, "twenty-six": 26, "two hundred": 200}
COUNTS = {"speaker": 26, "workshop": 10, "day": 2, "attendee": 200, "delegate": 200}
COUNT_RE = re.compile(r"\b(\d[\d,]*|two hundred|twenty-six|ten|two)[\s-]+(speakers?|workshops?|days?|attendees|delegates|sessions?)\b", re.I)


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, where, msg):
        self.items.append((level, where, msg))

    def err(self, where, msg):
        self.add("ERROR", where, msg)

    def warn(self, where, msg):
        self.add("WARN", where, msg)

    @property
    def errors(self):
        return [i for i in self.items if i[0] == "ERROR"]

    @property
    def warnings(self):
        return [i for i in self.items if i[0] == "WARN"]

    def print(self):
        for level, where, msg in self.items:
            print(f"{level:5}  {where}: {msg}")
        print(f"-- {len(self.errors)} error(s), {len(self.warnings)} warning(s)")


def texts_of(field):
    """['a', {'text': 'b', 'pin': 1}] -> [('a', None), ('b', 1)]; a bare string is one item."""
    if field is None:
        return []
    if isinstance(field, (str, dict)):
        field = [field]
    out = []
    for x in field:
        out.append((x, None) if isinstance(x, str) else (x.get("text", ""), x.get("pin")))
    return out


def lint_text(text, where, platform, rep, ctx):
    """Facts, voice and platform-policy checks shared by every text asset and every graphic."""
    on, ends = ctx["on"], ctx["ends"]
    if "!" in text:
        rep.err(where, "exclamation mark - the voice is restrained" + (", and Google rejects it in headlines" if platform == "google" else ""))
    if EMOJI.search(text):
        rep.err(where, "emoji - none, anywhere")
    hits = sorted({m.group(0).lower() for m in URGENCY.finditer(text)})
    if hits:
        rep.err(where, f"urgency mechanic ({', '.join(repr(h) for h in hits)}) - scarcity is factual (\"Limited to 200 attendees\"), a deadline is a date")
    if m := COUNTDOWN.search(text):
        rep.err(where, f"a day count or countdown ({m.group(0)!r}) goes stale overnight - state the date")
    if m := GCS_TERMS.search(text):
        rep.err(where, f"term GCS never uses ({m.group(0)!r})")
    for pat, why in STALE:
        if re.search(pat, text, re.I):
            rep.err(where, f"stale or retired fact: {why}")
    if m := PAST_EDITION.search(text):
        rep.err(where, f"past-edition framing ({m.group(0)!r}) - no past-edition figures or history exist on file")
    if m := OUTCOME.search(text):
        rep.err(where, f"reads as an offer of a visa / passport / citizenship ({m.group(0)!r}) - the ad sells a conference place, not an immigration outcome (Google's government-documents policy and Meta's deceptive-practices policy both look for this)")
    if m := GUARANTEE.search(text):
        rep.err(where, f"guarantee / outcome claim ({m.group(0)!r}) - nothing on file supports it")
    if m := PERSONAL_ATTR.search(text):
        rep.err(where, f"implies the viewer's wealth or status ({m.group(0)!r}) - Meta and Google both bar ads that assert or imply a personal attribute; address roles in the third person (advisors, family offices)")
    if m := YOUR_WEALTH.search(text):
        rep.warn(where, f"{m.group(0)!r} assumes the viewer has wealth - borderline under the personal-attributes rule; prefer the topic, not the viewer")
    if m := SUPERLATIVE.search(text):
        rep.warn(where, f"superlative ({m.group(0)!r}) - both platforms want it verifiable and no evidence is on file")
    if m := OFFICIAL.search(text):
        rep.warn(where, "'official' can imply a government or partner role - not supported by the site")
    if m := FREE.search(text):
        rep.warn(where, "'free' - the Summit is a paid place; nothing free is published")
    if platform in ("meta", "image") and (m := SOCIAL_ISSUE.search(text)):
        rep.warn(where, f"{m.group(0)!r} can trip Meta's social-issues classifier (immigration is on its list, and EU targeting bars those ads) - say 'global mobility' or name the topic instead, and expect the event name to need an appeal if flagged")
    if m := SANCTIONS.search(text):
        rep.warn(where, f"{m.group(0)!r} - the sanctions / restricted-nationals workshop is the most policy-sensitive title on the programme; keep it out of paid copy")
    if re.search(r"\bturkey\b", text, re.I):
        rep.warn(where, "'Turkey' is in the site's intro sentence but not in the timed workshop list - confirm with the user")
    for m in CAPS.finditer(text):
        if m.group(0) not in CAPS_OK:
            rep.warn(where, f"capitals ({m.group(0)!r}) - set in sentence case; Google rejects shouting")
            break
    if URL.search(text):
        if platform == "google":
            rep.err(where, "a URL in Google ad text - the display URL comes from the final URL and path fields")
        elif not ctx["url_confirmed"]:
            rep.err(where, "a URL in the copy but the user has not confirmed it (the site may still sit behind its staging gate)")
    # published prices only, only the tier in force for the whole flight
    by_eur = {t["eur"]: t for t in tiers()}
    for m in PRICE.finditer(text):
        raw = (m.group(1) or m.group(2)).replace(",", "")
        try:
            amt = int(float(raw))
        except ValueError:
            continue
        if amt not in by_eur:
            rep.err(where, f"price {m.group(0).strip()} is not one of the three published tiers (€399 / €499 / €599); the partner landing pages carry partner-only prices and codes - those never go in a public ad")
            continue
        now = rate_on(on)
        if now is None:
            rep.err(where, f"a price but no tier is published for {on} - say nothing about price")
        elif now["eur"] != amt:
            rep.err(where, f"{by_eur[amt]['name']} (€{amt}) is not the tier in force on {on} - that is the {now['name']} (€{now['eur']})")
        elif ends and ends > date.fromisoformat(now["end"]):
            rep.err(where, f"the ad runs to {ends} but the {now['name']} (€{amt}) ends on {now['end']} - from the next day this price is wrong; split the flight or drop the price")
    times = known_times()
    for m in TIME.finditer(text):
        hhmm = f"{int(m.group(1)):02d}:{m.group(2)}"
        if hhmm not in times:
            rep.err(where, f"time {hhmm} is not on the site's published programme")
    for m in MONTHDAY.finditer(text):
        mon = m.group(3)[:3].lower()
        for d in (m.group(1), m.group(2)):
            if d and (mon, int(d)) not in DATE_OK:
                rep.err(where, f"date '{d} {m.group(3)}' is not one the site publishes (rate windows and 5-6 Nov)")
    for m in COUNT_RE.finditer(text):
        raw = m.group(1).lower()
        n = WORDNUM.get(raw) or int(raw.replace(",", ""))
        noun = m.group(2).lower().rstrip("s")
        if noun == "session":
            rep.err(where, "a 'session' count - the site never defines a session; the countable facts are 2 days, 10 workshops, 26 speakers")
        elif COUNTS.get(noun) not in (None, n):
            rep.err(where, f"'{m.group(0)}' - the site says {COUNTS[noun]} {noun}s")
    if re.search(r"Marqu[eê]s", text):
        ctx.setdefault("venue", set()).add("Marquês" if "Marquês" in text else "Marques")


def check_len(text, limit, where, rep, hard=True, label="characters"):
    n = len(text)
    if "{=" in text:
        rep.warn(where, "ad customizer: Google counts the rendered text, not this template - confirm length in the UI")
        return
    if n > limit:
        (rep.err if hard else rep.warn)(where, f"{n} {label}, limit {limit}: {text[:40]!r}…")


def lint_group(items, spec, where, platform, rep, ctx, hard=True, pin_ok=None, recommend=None):
    """Count, length, duplicates and copy lint for one list of text assets."""
    n = len(items)
    if n < spec.get("min", 0):
        rep.err(where, f"{n} given, at least {spec['min']} needed")
    if n > spec.get("max", 99):
        rep.err(where, f"{n} given, at most {spec['max']} allowed")
    if recommend and n < recommend:
        rep.warn(where, f"{n} given; Google rates ad strength on variety - aim for {recommend}+ distinct ones")
    seen = {}
    for i, (text, pin) in enumerate(items, 1):
        w = f"{where}[{i}]"
        if not text.strip():
            rep.err(w, "empty")
            continue
        check_len(text, spec["chars"], w, rep, hard=hard)
        key = re.sub(r"\W+", " ", text.lower()).strip()
        if key in seen:
            rep.err(w, f"duplicate of #{seen[key]} - Google rejects repeated assets; Meta variants must differ")
        seen[key] = i
        if pin is not None and pin_ok and pin not in pin_ok:
            rep.err(w, f"pin {pin} is not a valid position (use {pin_ok})")
        if platform == "google" and text.rstrip()[-1:] in ".,;:" and "headline" in where:
            rep.warn(w, "Google headlines should not end in punctuation")
        lint_text(text, w, platform, rep, ctx)


def lint_pack(pack, on, today):
    rep = Report()
    ends = date.fromisoformat(pack["ends"]) if pack.get("ends") else None
    ctx = {"on": on, "ends": ends, "url_confirmed": bool(pack.get("url_confirmed"))}

    # flight
    if not pack.get("goes_live"):
        rep.warn("pack.goes_live", "no go-live date - the rate tier is judged on today's date; set goes_live and ends")
    if not ends:
        rep.warn("pack.ends", "no end date - a price or deadline in the copy cannot be checked past the go-live day")
    elif ends >= EVENT_START:
        rep.err("pack.ends", f"{ends}: the Summit opens on {EVENT_START} (09:00 Lisbon) - end every ad before it")
    if on > EVENT_END:
        rep.err("pack.goes_live", "the Summit is over - nothing to advertise")
    elif on < today and pack.get("goes_live"):
        rep.warn("pack.goes_live", f"{on} is in the past - the tier is judged on that date")
    t = rate_on(on)
    if ends and t and date.fromisoformat(t["end"]) < ends:
        rep.warn("pack.flight", f"the flight crosses a rate change: {t['name']} ends {t['end']}. Any ad that shows a price must end that day, or ship a second version for the next tier")
    if not pack.get("final_url"):
        rep.warn("pack.final_url", "no final URL - Google requires one to upload; ask the user and say whether the site is still behind its staging gate (run: ads.py preflight URL)")
    elif not pack.get("url_confirmed"):
        rep.warn("pack.final_url", "URL not confirmed by the user - run ads.py preflight; a reviewer who hits the staging password gate disapproves the ad")

    bn = pack.get("business_name") or BUSINESS_NAME
    if len(bn) > 25:
        rep.err("pack.business_name", f"{len(bn)} characters, limit 25")

    g = pack.get("google") or {}
    gs = SPECS["google"]
    rsas = g.get("rsa") or []
    if isinstance(rsas, dict):
        rsas = [rsas]
    for k, rsa in enumerate(rsas, 1):
        w = f"google.rsa{k if len(rsas) > 1 else ''}"
        hs = texts_of(rsa.get("headlines"))
        ds = texts_of(rsa.get("descriptions"))
        lint_group(hs, gs["rsa"]["headline"], f"{w}.headline", "google", rep, ctx, pin_ok=gs["rsa"]["pin_positions"]["headline"], recommend=gs["rsa"]["headline"]["recommend_min"])
        lint_group(ds, gs["rsa"]["description"], f"{w}.description", "google", rep, ctx, pin_ok=gs["rsa"]["pin_positions"]["description"], recommend=gs["rsa"]["description"]["recommend_min"])
        for pk in ("path1", "path2"):
            if rsa.get(pk) and len(rsa[pk]) > gs["rsa"]["path"]["chars"]:
                rep.err(f"{w}.{pk}", f"{len(rsa[pk])} characters, limit {gs['rsa']['path']['chars']}")
            if rsa.get(pk):
                lint_text(rsa[pk], f"{w}.{pk}", "google", rep, ctx)
        pins = [p for _, p in hs if p]
        if sorted(set(pins)) == [1, 2, 3]:
            rep.warn(f"{w}.headline", "all three headline positions are pinned - one combination only; Ad Strength drops")
    if g.get("display"):
        d = g["display"]
        lint_group(texts_of(d.get("short_headlines")), gs["display"]["short_headline"], "google.display.short_headline", "google", rep, ctx)
        lint_group(texts_of(d.get("long_headline")), gs["display"]["long_headline"], "google.display.long_headline", "google", rep, ctx)
        lint_group(texts_of(d.get("descriptions")), gs["display"]["description"], "google.display.description", "google", rep, ctx)
    if g.get("pmax"):
        d = g["pmax"]
        sh = texts_of(d.get("short_headlines"))
        lint_group(sh, gs["pmax"]["short_headline"], "google.pmax.short_headline", "google", rep, ctx)
        if sh and not any(len(t) <= 15 for t, _ in sh):
            rep.err("google.pmax.short_headline", "Performance Max needs at least one headline of 15 characters or fewer")
        lint_group(texts_of(d.get("long_headlines")), gs["pmax"]["long_headline"], "google.pmax.long_headline", "google", rep, ctx)
        lint_group(texts_of(d.get("descriptions")), gs["pmax"]["description"], "google.pmax.description", "google", rep, ctx)
    if g.get("demand_gen"):
        d = g["demand_gen"]
        hs = texts_of(d.get("headlines"))
        lint_group(hs, gs["demand_gen"]["headline"], "google.demand_gen.headline", "google", rep, ctx)
        if hs and not any(len(t) <= 30 for t, _ in hs):
            rep.err("google.demand_gen.headline", "Demand Gen needs at least one headline of 30 characters or fewer (Display placements)")
        lint_group(texts_of(d.get("descriptions")), gs["demand_gen"]["description"], "google.demand_gen.description", "google", rep, ctx)
    if g.get("cta") and g["cta"] not in SPECS["google_cta"]:
        rep.warn("google.cta", f"{g['cta']!r} is not on the usual list {SPECS['google_cta']} - check the UI")

    m = pack.get("meta")
    if m:
        ms = SPECS["meta"]["text"]
        pts, hls, dss = texts_of(m.get("primary_texts")), texts_of(m.get("headlines")), texts_of(m.get("descriptions"))
        if not pts:
            rep.err("meta.primary_texts", "none given - every Meta ad needs primary text")
        if not hls:
            rep.warn("meta.headlines", "none given - the headline sits under the image and carries the click")
        for i, (text, _) in enumerate(pts, 1):
            w = f"meta.primary_text[{i}]"
            lint_text(text, w, "meta", rep, ctx)
            if len(text) > ms["primary_text"]["recommend_chars"]:
                rep.warn(w, f"{len(text)} characters; only ~{ms['primary_text']['recommend_chars']} show before 'See more' - the first sentence must carry the message alone")
        for i, (text, _) in enumerate(hls, 1):
            w = f"meta.headline[{i}]"
            lint_text(text, w, "meta", rep, ctx)
            if len(text) > ms["headline"]["soft_max_chars"]:
                rep.warn(w, f"{len(text)} characters; cut off past ~{ms['headline']['soft_max_chars']}")
            elif len(text) > ms["headline"]["recommend_chars"]:
                rep.warn(w, f"{len(text)} characters; the feed shows ~{ms['headline']['recommend_chars']}")
        for i, (text, _) in enumerate(dss, 1):
            w = f"meta.description[{i}]"
            lint_text(text, w, "meta", rep, ctx)
            if len(text) > ms["description"]["recommend_chars"]:
                rep.warn(w, f"{len(text)} characters; usually ~{ms['description']['recommend_chars']} and often not shown")
        for name, group in (("primary_text", pts), ("headline", hls), ("description", dss)):
            keys = [re.sub(r"\W+", " ", t.lower()).strip() for t, _ in group]
            if len(set(keys)) < len(keys):
                rep.err(f"meta.{name}", "duplicate variants - Meta tests variants against each other, so they must differ")
        if m.get("cta") and m["cta"] not in SPECS["meta"]["cta"]:
            rep.warn("meta.cta", f"{m['cta']!r} is not on the usual list {SPECS['meta']['cta']} - the UI offers what fits the objective")

    creatives = pack.get("creatives") or []
    ids = set()
    for c in creatives:
        cid = c.get("id") or "?"
        w = f"creative[{cid}]"
        if cid in ids:
            rep.err(w, "duplicate id")
        ids.add(cid)
        if not c.get("headline"):
            rep.err(w, "no headline")
            continue
        for fld in ("headline", "subline", "support"):
            if c.get(fld):
                lint_text(c[fld], f"{w}.{fld}", "image", rep, ctx)
        for fk, ov in (c.get("by_format") or {}).items():
            if fk not in SPECS["formats"]:
                rep.err(w, f"by_format: unknown format {fk!r}")
            for fld in ("headline", "subline", "support"):
                if ov.get(fld):
                    lint_text(ov[fld], f"{w}.by_format[{fk}].{fld}", "image", rep, ctx)
        if c.get("photo"):
            try:
                resolve_photo(c["photo"])
            except SystemExit as e:
                rep.err(w, str(e))
        if c.get("style", "plate") not in ("plate", "full"):
            rep.err(w, "style must be 'plate' or 'full'")
        n = len(c["headline"].split())
        if n > 12:
            rep.warn(w, f"headline is {n} words (bar: 12 or fewer)")
        if c.get("marks", "gcs-cnn") not in ("gcs-cnn", "summit-only"):
            rep.err(w, "marks must be 'gcs-cnn' or 'summit-only'")
        for f in c.get("formats", []):
            if f not in SPECS["formats"]:
                rep.err(w, f"unknown format {f!r} (run: ads.py formats)")
        if not c.get("formats"):
            rep.warn(w, "no formats listed - nothing to render")
    if len(ctx.get("venue", ())) > 1:
        rep.warn("pack.venue", "both 'Marques' and 'Marquês' appear - the site uses both; pick one per pack and tell the user")
    return rep


# ---------------------------------------------------------------------------------------------
# Export — copy sheet, long-form CSV, Google Ads Editor RSA CSV
# ---------------------------------------------------------------------------------------------

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def slug_of(pack):
    return re.sub(r"[^a-z0-9_-]+", "-", (pack.get("name") or "wms-ads").lower()).strip("-") or "wms-ads"


def utm(pack, platform, content):
    u = pack.get("utm") or {}
    src, med = ("google", "cpc") if platform == "google" else ("meta", "paid-social")
    parts = {"utm_source": u.get("source", src), "utm_medium": u.get("medium", med),
             "utm_campaign": u.get("campaign", slug_of(pack)), "utm_content": content}
    return "&".join(f"{k}={v}" for k, v in parts.items())


def alt_text(c):
    t = f'Navy graphic reading "{c["headline"].rstrip(".")}" with the Wealth & Migration Summit lockup' + ("." if c.get("marks") == "summit-only" else ", Global Citizen Solutions and CNN Portugal marks.")
    return t if len(t) <= 125 else f'Navy graphic: "{c["headline"].rstrip(".")}" - Wealth & Migration Summit.'[:125]


def pack_prices(pack):
    """Every euro amount that appears in the pack's copy or on its graphics."""
    texts = [r[4] for r in rows_of(pack)]
    for c in pack.get("creatives") or []:
        texts += [c.get(f, "") for f in ("headline", "subline", "support")]
        for ov in (c.get("by_format") or {}).values():
            texts += [ov.get(f, "") for f in ("headline", "subline", "support")]
    out = set()
    for tx in texts:
        for m in PRICE.finditer(tx or ""):
            try:
                out.add(int(float((m.group(1) or m.group(2)).replace(",", ""))))
            except ValueError:
                pass
    return out


def rows_of(pack):
    """Long-form rows: platform, format, field, index, text, chars, limit, pin."""
    rows = []
    gs, ms = SPECS["google"], SPECS["meta"]["text"]
    g = pack.get("google") or {}
    rsas = g.get("rsa") or []
    if isinstance(rsas, dict):
        rsas = [rsas]
    for k, rsa in enumerate(rsas, 1):
        fmt = "RSA" if len(rsas) == 1 else f"RSA {k}"
        for i, (t, p) in enumerate(texts_of(rsa.get("headlines")), 1):
            rows.append(("google", fmt, "headline", i, t, len(t), gs["rsa"]["headline"]["chars"], p or ""))
        for i, (t, p) in enumerate(texts_of(rsa.get("descriptions")), 1):
            rows.append(("google", fmt, "description", i, t, len(t), gs["rsa"]["description"]["chars"], p or ""))
        for pk in ("path1", "path2"):
            if rsa.get(pk):
                rows.append(("google", fmt, pk, 1, rsa[pk], len(rsa[pk]), gs["rsa"]["path"]["chars"], ""))
    for key, label, groups in (
        ("display", "Responsive display", (("short_headlines", "short headline", "short_headline"), ("long_headline", "long headline", "long_headline"), ("descriptions", "description", "description"))),
        ("pmax", "Performance Max", (("short_headlines", "short headline", "short_headline"), ("long_headlines", "long headline", "long_headline"), ("descriptions", "description", "description"))),
    ):
        d = g.get(key)
        if d:
            for fld, fname, spec_key in groups:
                for i, (t, _) in enumerate(texts_of(d.get(fld)), 1):
                    rows.append(("google", label, fname, i, t, len(t), gs[key][spec_key]["chars"], ""))
    if g.get("demand_gen"):
        d = g["demand_gen"]
        for i, (t, _) in enumerate(texts_of(d.get("headlines")), 1):
            rows.append(("google", "Demand Gen", "headline", i, t, len(t), gs["demand_gen"]["headline"]["chars"], ""))
        for i, (t, _) in enumerate(texts_of(d.get("descriptions")), 1):
            rows.append(("google", "Demand Gen", "description", i, t, len(t), gs["demand_gen"]["description"]["chars"], ""))
    bn = pack.get("business_name") or BUSINESS_NAME
    if g:
        rows.append(("google", "all", "business name", 1, bn, len(bn), 25, ""))
    m = pack.get("meta")
    if m:
        for i, (t, _) in enumerate(texts_of(m.get("primary_texts")), 1):
            rows.append(("meta", "Feed / Stories / Reels", "primary text", i, t, len(t), ms["primary_text"]["recommend_chars"], ""))
        for i, (t, _) in enumerate(texts_of(m.get("headlines")), 1):
            rows.append(("meta", "Feed / Stories / Reels", "headline", i, t, len(t), ms["headline"]["recommend_chars"], ""))
        for i, (t, _) in enumerate(texts_of(m.get("descriptions")), 1):
            rows.append(("meta", "Feed / Stories / Reels", "description", i, t, len(t), ms["description"]["recommend_chars"], ""))
    return rows


def export(pack, out):
    out.mkdir(parents=True, exist_ok=True)
    slug = slug_of(pack)
    rows = rows_of(pack)
    (out / f"{slug}_pack.json").write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / f"{slug}_copy.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["platform", "format", "field", "index", "text", "chars", "limit", "pin"])
        w.writerows(rows)

    g = pack.get("google") or {}
    rsas = g.get("rsa") or []
    if isinstance(rsas, dict):
        rsas = [rsas]
    if rsas:
        head = ["Campaign", "Ad group", "Ad type"]
        for i in range(1, 16):
            head += [f"Headline {i}", f"Headline {i} position"]
        for i in range(1, 5):
            head += [f"Description {i}", f"Description {i} position"]
        head += ["Path 1", "Path 2", "Final URL", "Final URL suffix", "Status"]
        with (out / f"{slug}_google_rsa_editor.csv").open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(head)
            for k, rsa in enumerate(rsas, 1):
                hs, ds = texts_of(rsa.get("headlines")), texts_of(rsa.get("descriptions"))
                row = [rsa.get("campaign") or f"WMS26 | Search | {slug}", rsa.get("ad_group") or "Event | Lisbon", "Responsive search ad"]
                for i in range(15):
                    row += [hs[i][0], hs[i][1] or "-"] if i < len(hs) else ["", ""]
                for i in range(4):
                    row += [ds[i][0], ds[i][1] or "-"] if i < len(ds) else ["", ""]
                row += [rsa.get("path1", ""), rsa.get("path2", ""), pack.get("final_url", ""), utm(pack, "google", slugify(rsa.get("ad_group", slug))), "Paused"]
                w.writerow(row)

    # human copy sheet
    L = [f"# Ad copy - {pack.get('name', slug)}", ""]
    L.append(f"- Goes live: {pack.get('goes_live', 'not set')} · ends: {pack.get('ends', 'not set')}")
    t = rate_on(date.fromisoformat(pack["goes_live"])) if pack.get("goes_live") else None
    shown = pack_prices(pack)
    if not shown:
        L.append("- Price: none shown in any text or image")
    elif t:
        L.append(f"- Price shown: {t['name']} {t['price']} - true through {t['end']}; the ad schedule must start on or after {max(t['start'], pack.get('goes_live', t['start']))} and end by {t['end']}")
    else:
        L.append("- Price shown, but no tier is published for the go-live date - fix before upload")
    L.append(f"- Final URL: {pack.get('final_url') or 'NOT SET'}" + ("" if pack.get("url_confirmed") else " (not confirmed by the user)"))
    L.append(f"- Google final URL suffix: `{utm(pack, 'google', '<ad-group>')}`")
    L.append(f"- Meta URL parameters: `{utm(pack, 'meta', '<creative-id>')}`")
    L.append("")
    for plat in ("google", "meta"):
        pr = [r for r in rows if r[0] == plat]
        if not pr:
            continue
        L.append(f"## {'Google Ads' if plat == 'google' else 'Meta Ads'}")
        cur = None
        for _, fmt, fld, i, text, n, lim, pin in pr:
            if (fmt, fld) != cur:
                cur = (fmt, fld)
                L += ["", f"### {fmt} - {fld}", "", "| # | Text | Chars | Limit | Pin |", "|---|---|---|---|---|"]
            L.append(f"| {i} | {text.replace('|', '/')} | {n} | {lim} | {pin} |")
        L.append("")
    cs = pack.get("creatives") or []
    if cs:
        L += ["## Image creatives - alt text", ""]
        for c in cs:
            L.append(f"- **{c['id']}** ({', '.join(c.get('formats', []))}): {alt_text(c)}")
        L.append("")
    (out / f"{slug}_copy.md").write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {slug}_pack.json, {slug}_copy.md, {slug}_copy.csv" + (f", {slug}_google_rsa_editor.csv" if rsas else ""))


# ---------------------------------------------------------------------------------------------
# Render — image creatives and Google logo assets
# ---------------------------------------------------------------------------------------------

def b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def svg_uri(path):
    return "data:image/svg+xml;base64," + b64(path)


def png_uri(path):
    return "data:image/png;base64," + b64(path)


def font_css():
    faces = [("Caladea", 400, "Caladea-Regular.ttf"), ("Archivo", 400, "Archivo-400.ttf"), ("Archivo", 500, "Archivo-500.ttf")]
    return "\n".join(f'@font-face{{font-family:"{fam}";font-weight:{wt};font-display:block;'
                     f'src:url(data:font/ttf;base64,{b64(ASSETS / "fonts" / f)}) format("truetype")}}' for fam, wt, f in faces)


def lockup(key, w=None, h=None):
    f, iw, ih = LOGOS[key]
    if h is not None:
        w = h * iw / ih
    else:
        h = w * ih / iw
    return f'<img class="lockup" alt="Wealth &amp; Migration Summit" src="{svg_uri(ASSETS / "logos" / f)}" width="{w:.1f}" height="{h:.1f}">'


def marks(ph):
    """GCS (symbol + wordmark) and CNN Portugal at equal height, gap 0.6 x height - the hero's pair."""
    gw = ph * GCS[1] / GCS[2]
    cw = ph * CNN[1] / CNN[2]
    return (f'<div class="marks" style="gap:{ph * 0.6:.1f}px">'
            f'<img alt="Global Citizen Solutions" src="{svg_uri(ASSETS / "logos" / GCS[0])}" width="{gw:.1f}" height="{ph:.1f}">'
            f'<img alt="CNN Portugal" src="{png_uri(ASSETS / "logos" / CNN[0])}" width="{cw:.1f}" height="{ph:.1f}"></div>')


def esc(text, sentences=False):
    """Escape; keep a hyphenated word from breaking across lines; with `sentences`, put each sentence on its own line
    (a full stop after two lowercase letters, so 'St.' or 'Dr.' never splits) and honour an explicit newline."""
    s = html.escape(text).replace("\n", "<br>")
    if sentences:
        s = re.sub(r"(?<=[a-z]{2}\.)\s+(?=[A-Z])", "<br>", s)
    if "<br>" in s:   # each line is one unit: the fit loop shrinks the type rather than let a line wrap
        s = "<br>".join(f'<span class="ln">{part}</span>' for part in s.split("<br>"))
    return re.sub(r"\b\w+(?:-\w+)+\b", lambda m: f'<span class="nb">{m.group(0)}</span>', s)


PAGE = Template("""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${title}</title><style>
${fonts}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:${navy}}
.canvas{position:relative;width:${W}px;height:${H}px;background:${navy}${bg};overflow:hidden;color:${white};font-family:Archivo,Helvetica,Arial,sans-serif}
.scrim{position:absolute;inset:0;background:${scrim}}
.safe{position:absolute;left:${px}px;right:${px}px;top:${pt}px;bottom:${pb}px;display:flex;flex-direction:column;justify-content:space-between;gap:${gap}px}
.lockup{display:block}
.copy{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:${align};overflow:hidden}
.copy-in{display:block;max-width:${copy_w}px}
.service{font:500 ${label}px/1 Archivo,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:${gold};margin-bottom:${label_gap}px}
.headline{font:400 ${hmax}px/1.04 Caladea,Georgia,serif;letter-spacing:-.01em;color:${white};text-wrap:balance}
.support{font:400 ${support}px/1.4 Archivo,sans-serif;letter-spacing:.005em;color:${mist};margin-top:${label_gap}px}
.nb,.ln{white-space:nowrap}
.marks{display:flex;align-items:center}
.gcs{display:inline-flex;align-items:center}
.marks img,.gcs img{display:block}
</style></head><body><div class="canvas">${scrimel}<div class="safe" data-max="${hmax}" data-min="${hmin}">
${header}
<div class="copy"><div class="copy-in">${service}<h1 class="headline">${headline}</h1>${supportel}</div></div>
${footer}
</div></div></body></html>""")

FIT_JS = """() => {
  const safe = document.querySelector('.safe'), copy = document.querySelector('.copy');
  const inner = document.querySelector('.copy-in'), h = document.querySelector('.headline');
  const max = +safe.dataset.max, min = +safe.dataset.min;
  let px = max;
  const fits = () => inner.offsetHeight <= copy.clientHeight && h.scrollWidth <= h.clientWidth + 1;
  for (; px >= min; px -= 2) { h.style.fontSize = px + 'px'; if (fits()) break; }
  if (px < min) { px = min; h.style.fontSize = px + 'px'; }
  const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
  const s = r(safe);
  const lk = document.querySelector('.lockup');
  return {px, ok: fits(), safe: s, inner: r(inner), lock: lk ? r(lk) : null,
          marks: document.querySelector('.marks') ? r(document.querySelector('.marks')) : null};
}"""


def layout_params(fmt_key):
    f = SPECS["formats"][fmt_key]
    W, H = f["design"]
    s = f["safe"]
    ratio = W / H
    if ratio > 1.5:   # landscape 1.91:1, designed at 1200 wide
        p = dict(label=22, label_gap=18, hmax=68, hmin=38, support=24, mark_h=40, lock_w=380, copy_w=int(W * 0.70), align="center", gap=18)
    elif ratio < 0.7:  # 9:16
        p = dict(label=28, label_gap=26, hmax=110, hmin=64, support=34, mark_h=60, lock_w=640, copy_w=int(W * 0.85), align="flex-end", gap=40)
    else:              # 1:1, 4:5
        p = dict(label=28, label_gap=26, hmax=112 if H <= W else 104, hmin=60, support=34, mark_h=56, lock_w=640 if W > 1000 else 560, copy_w=int(W * 0.85), align="center" if H <= W else "flex-end", gap=36)
    p.update(W=W, H=H, px=round(W * s["side"]), pt=round(H * max(s["top"], 0.075)), pb=round(H * max(s["bottom"], 0.075)), out=f["out"])
    return p


def creative_html(c, fmt_key):
    c = {**c, **((c.get("by_format") or {}).get(fmt_key, {}))}
    p = layout_params(fmt_key)
    # Google's responsive-image guidance: no overlaid logo, no repeated copy, never a button. Its formats are a
    # "plate" (service line + headline) and the logo travels as the separate logo asset. Meta formats carry the
    # lockup, the support line and the GCS + CNN Portugal marks. `style` overrides either default.
    plate = c.get("style", "plate" if SPECS["formats"][fmt_key]["platform"] == "google" else "full") == "plate"
    if plate:
        p["align"] = "center" if p["H"] <= p["W"] * 1.3 else p["align"]
    subline = c["subline"] if "subline" in c else SERVICE_LINE
    header = "" if plate else lockup("horizontal", w=p["lock_w"])
    footer = "" if plate or c.get("marks", "gcs-cnn") != "gcs-cnn" else marks(p["mark_h"])
    photo = resolve_photo(c.get("photo")) if not plate else None
    page = PAGE.substitute(
        bg=f' url({photo_uri(photo)}) center / cover no-repeat' if photo else "", scrim=SCRIM if photo else "none",
        scrimel='<div class="scrim"></div>' if photo else "",
        title=html.escape(c["id"]), fonts=font_css(), navy=NAVY, white=WHITE, gold=GOLD, mist=MIST, W=p["W"], H=p["H"],
        px=p["px"], pt=p["pt"], pb=p["pb"], gap=p["gap"], align=p["align"], copy_w=p["copy_w"], label=p["label"],
        label_gap=p["label_gap"], hmax=p["hmax"], hmin=p["hmin"], support=p["support"], header=header, footer=footer,
        service=f'<div class="service">{esc(subline)}</div>' if subline else "",
        headline=esc(c["headline"], sentences=True),
        supportel=f'<div class="support">{esc(c["support"])}</div>' if c.get("support") and not plate else "")
    return page, p


def resolve_photo(ref):
    """A photograph named in a creative: an absolute path, or a file under assets/imagery/."""
    if not ref:
        return None
    for cand in (Path(ref), ASSETS / "imagery" / ref):
        if cand.is_file():
            return cand
    raise SystemExit(f"photo {ref!r} not found (looked in assets/imagery/ and as a path)")


def photo_uri(path):
    mime = {".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}[path.suffix.lower()]
    return f"data:{mime};base64," + b64(path)


SCRIM = ("linear-gradient(0deg,rgba(10,16,31,.94) 0%,rgba(10,16,31,.80) 40%,rgba(10,16,31,.30) 74%,rgba(10,16,31,.58) 100%),"
         "linear-gradient(90deg,rgba(10,16,31,.55) 0%,rgba(10,16,31,0) 72%)")   # layered: one rising from the ground, one crossing from the text side


def shrink_png(path, max_kb):
    """Flat navy and type compress hard; if a file is still over its ceiling, palette-reduce it (never resize)."""
    from PIL import Image
    if path.stat().st_size <= max_kb * 1024:
        return
    im = Image.open(path).convert("RGB")
    for colours in (128, 64, 32):
        im.quantize(colors=colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)
        if path.stat().st_size <= max_kb * 1024:
            return


def render_all(pack, out, only_creative=None, only_formats=None, keep_html=False):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    slug = slug_of(pack)
    src = out / "src"
    jobs = []
    for c in pack.get("creatives") or []:
        if only_creative and c["id"] != only_creative:
            continue
        for f in c.get("formats", []):
            if only_formats and f not in only_formats:
                continue
            jobs.append((c, f))
    problems, written = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for c, f in jobs:
            if c.get("photo") and SPECS["formats"][f]["platform"] == "google" and c.get("style", "plate") == "plate":
                # Google wants the picture clean: crop it, lay nothing over it
                written += fit_photo(resolve_photo(c["photo"]), out, [f], tuple(c.get("focus", (0.5, 0.5))), f"{slug}_{c['id']}", quiet=True)
                continue
            page_html, p = creative_html(c, f)
            W, H = p["W"], p["H"]
            ow, oh = p["out"]
            tmp = (src if keep_html else out / ".tmp") / f"{slug}_{c['id']}_{f}.html"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(page_html, encoding="utf-8")
            ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=ow / W)
            pg = ctx.new_page()
            pg.goto(tmp.resolve().as_uri())
            pg.evaluate("document.fonts.ready.then(() => true)")
            res = pg.evaluate(FIT_JS)
            png = out / f"{slug}_{c['id']}_{f}_{ow}x{oh}.png"
            pg.locator(".canvas").screenshot(path=str(png))
            ctx.close()
            where = f"{c['id']}/{f}"
            if not res["ok"]:
                problems.append(f"ERROR  {where}: copy does not fit at {res['px']}px (the floor for this format) - shorten the headline or drop the support line")
            sl, st, sr, sb = res["safe"]
            for name in ("inner", "lock", "marks"):
                box = res.get(name)
                if box and (box[0] < sl - 1 or box[1] < st - 1 or box[2] > sr + 1 or box[3] > sb + 1):
                    problems.append(f"ERROR  {where}: {name} leaves the safe zone")
            if res["px"] < p["hmin"] + 8:
                problems.append(f"WARN   {where}: headline shrank to {res['px']}px (floor {p['hmin']}) - consider fewer words")
            shrink_png(png, SPECS["formats"][f]["max_kb"])
            written.append(png)
            print(f"{png.name}  headline {res['px']}px  {png.stat().st_size // 1024} KB")
        if pack.get("google_logos"):
            for key in ("google_logo_square", "google_logo_landscape"):
                spec = SPECS["logos"][key]
                ow, oh = spec["out"]
                stack = lockup("default", h=oh * (0.44 if key.endswith("square") else 0.74))
                html_ = (f'<!doctype html><html><body style="margin:0;background:{NAVY}"><div style="width:{ow}px;height:{oh}px;background:{NAVY};'
                         f'display:flex;align-items:center;justify-content:center">{stack}</div></body></html>')
                tmp = out / ".tmp" / f"{slug}_{key}.html"
                tmp.parent.mkdir(parents=True, exist_ok=True)
                tmp.write_text(html_, encoding="utf-8")
                ctx = browser.new_context(viewport={"width": ow, "height": oh})
                pg = ctx.new_page()
                pg.goto(tmp.resolve().as_uri())
                png = out / f"{slug}_{key}_{ow}x{oh}.png"
                pg.screenshot(path=str(png))
                ctx.close()
                shrink_png(png, spec["max_kb"])
                written.append(png)
                print(f"{png.name}  {png.stat().st_size // 1024} KB")
        browser.close()
    for tmpdir in (out / ".tmp",):
        if tmpdir.exists():
            for f in tmpdir.iterdir():
                f.unlink()
            tmpdir.rmdir()
    for line in problems:
        print(line)
    if written:
        sheet(written, out / f"{slug}_sheet.png")
    return written, problems


def sheet(files, dest, cols=4, thumb=360):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(str(ASSETS / "fonts" / "Archivo-400.ttf"), 14)
    cells = []
    for f in files:
        im = Image.open(f).convert("RGB")
        im.thumbnail((thumb, thumb))
        cells.append((im, f.name))
    rows = (len(cells) + cols - 1) // cols
    cw, ch = thumb + 20, thumb + 44
    canvas = Image.new("RGB", (cols * cw, rows * ch), (236, 238, 242))
    d = ImageDraw.Draw(canvas)
    for i, (im, name) in enumerate(cells):
        x, y = (i % cols) * cw + 10, (i // cols) * ch + 10
        canvas.paste(im, (x, y))
        d.text((x, y + im.height + 6), name[:52], fill=(18, 27, 49), font=font)
    canvas.save(dest)
    print(f"contact sheet: {dest.name}")


def fit_photo(src, out, keys, focus=(0.5, 0.5), name="photo", quiet=False):
    """Cover-crop a photograph the client has cleared for paid use to each format's exact pixels. No text, no logo, no
    filter: Google's responsive-image guidance wants a clean picture, with the words carried by the text assets."""
    from PIL import Image
    im = Image.open(src).convert("RGB")
    written = []
    for key in keys:
        spec = SPECS["formats"].get(key)
        if not spec:
            print(f"ERROR  unknown format {key!r} (run: ads.py formats)")
            continue
        ow, oh = spec["out"]
        k = max(ow / im.width, oh / im.height)
        if k > 1.15:
            print(f"WARN   {key}: the source is {im.width}x{im.height}; this format needs an upscale of x{k:.2f} - it will look soft and Google flags blurry images. Ask for a larger original")
        r = im.resize((max(ow, round(im.width * k)), max(oh, round(im.height * k))), Image.LANCZOS)
        left = round((r.width - ow) * min(max(focus[0], 0), 1))
        top = round((r.height - oh) * min(max(focus[1], 0), 1))
        crop = r.crop((left, top, left + ow, top + oh))
        dest = out / f"{name}_{key}_{ow}x{oh}.jpg"
        out.mkdir(parents=True, exist_ok=True)
        for q in (92, 85, 75, 65):
            crop.save(dest, quality=q, optimize=True)
            if dest.stat().st_size <= spec["max_kb"] * 1024:
                break
        written.append(dest)
        print(f"{dest.name}  {dest.stat().st_size // 1024} KB")
    if not quiet:
        print("Before upload: confirm the licence covers paid advertising. Files in assets/imagery/ are licensed stock, per the user (2026-10-21).")
    return written


def check_outputs(out):
    """Every PNG in `out` against the exact size, minimum size and file-size ceiling in specs.json."""
    from PIL import Image
    bad = 0
    for png in sorted(list(out.glob("*.png")) + list(out.glob("*.jpg"))):
        if png.name.endswith("_sheet.png"):
            continue
        m = re.search(r"_(\d+)x(\d+)\.(?:png|jpg)$", png.name)
        im = Image.open(png)
        key = next((k for k in list(SPECS["formats"]) + list(SPECS["logos"]) if f"_{k}_" in png.name), None)
        spec = SPECS["formats"].get(key) or SPECS["logos"].get(key)
        line = f"{png.name}: {im.width}x{im.height}, {png.stat().st_size // 1024} KB"
        issues = []
        if not spec:
            issues.append("not a known ad format")
        else:
            if [im.width, im.height] != spec["out"]:
                issues.append(f"expected {spec['out'][0]}x{spec['out'][1]}")
            if "min" in spec and (im.width < spec["min"][0] or im.height < spec["min"][1]):
                issues.append(f"below the minimum {spec['min']}")
            if png.stat().st_size > spec["max_kb"] * 1024:
                issues.append(f"over {spec['max_kb']} KB")
        if m and (int(m.group(1)), int(m.group(2))) != (im.width, im.height):
            issues.append("file name does not match the pixel size")
        print(("FAIL  " if issues else "ok    ") + line + (" - " + "; ".join(issues) if issues else ""))
        bad += bool(issues)
    return bad


# ---------------------------------------------------------------------------------------------
# Preflight — can a reviewer reach the landing page?
# ---------------------------------------------------------------------------------------------

def preflight(url, pack=None):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; AdsBot-Google; +http://www.google.com/adsbot.html)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read(200_000).decode("utf-8", "replace")
            title = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
            print(f"200  {r.geturl()}  title: {html.unescape(title.group(1)).strip() if title else '(none)'}")
            if "noindex" in body.lower():
                print("note: the page carries noindex - fine for an ad destination, but it will not rank organically")
            text = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I))
            text = re.sub(r"\s+", " ", html.unescape(text))
            on_page = sorted({int(x) for x in re.findall(r"€\s?(\d{3})\b", text)})
            now_marked = sorted({int(x) for x in re.findall(r"\bNOW\b[^€]{0,80}€\s?(\d{3})", text)})
            if on_page:
                print(f"prices in the served HTML: {', '.join('€' + str(x) for x in on_page)}" + (f"; marked NOW: {', '.join('€' + str(x) for x in now_marked)}" if now_marked else ""))
            if pack is not None:
                shown = pack_prices(pack)
                if shown and now_marked and set(now_marked) != shown:
                    print(f"WARN  the ad says {', '.join('€' + str(x) for x in sorted(shown))} but the page marks {', '.join('€' + str(x) for x in now_marked)} as the current rate - a price that differs from the landing page is a disapproval reason on both platforms. Fine before the tier switch; re-run on the go-live day, and have the web team switch the page")
                elif shown and on_page and not shown <= set(on_page):
                    print(f"WARN  the ad says {', '.join('€' + str(x) for x in sorted(shown))} but that price is not in the page's HTML")
                print("note: this reads the HTML as served; a rate that JavaScript switches by date is not seen - open the page in a browser on the go-live day")
            return 0
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"401  {url}  - HTTP Basic Auth: the site is still behind its staging password. Platform reviewers cannot get in, so the ads will be disapproved (destination not working). Lift the gate before upload.")
        else:
            print(f"{e.code}  {url}  - the landing page does not return 200; fix before uploading")
        return 1
    except Exception as e:  # network down, DNS, TLS
        print(f"could not reach {url}: {e}")
        return 2


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------

def print_rate(on):
    now = rate_on(on)
    if on > EVENT_END:
        print(f"{on}: the Summit (5-6 Nov 2026) is over")
        return
    if on >= EVENT_START:
        print(f"{on}: the Summit is under way - nothing to advertise")
        return
    if now:
        print(f"{on}: {now['name']} {now['price']} - true through {now['end']}")
        nxt = [t for t in tiers() if t["start"] > now["end"]]
        print(f"next: {nxt[0]['name']} {nxt[0]['price']} from {nxt[0]['start']}" if nxt else "after that no price is published; every ad ends before 5 Nov 09:00 Lisbon")
    else:
        print(f"{on}: no rate tier is published for this date - say nothing about price")


def print_formats(platform=None):
    for k, f in SPECS["formats"].items():
        if platform and f["platform"] != platform:
            continue
        print(f"{k:22} {f['out'][0]}x{f['out'][1]:<5} {f['ratio']:7} {f['label']}")
        if f.get("note"):
            print(f"{'':22} {f['note']}")
    if not platform or platform == "google":
        print("\nGoogle logos: " + ", ".join(f"{k} {v['out'][0]}x{v['out'][1]}" for k, v in SPECS["logos"].items()))
        print("Uploaded display sizes (build with wm-web-banners): " + ", ".join(SPECS["uploaded_display"]["sizes"]))


def load(path):
    try:
        pack = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"cannot read {path}: {e}")
    if not isinstance(pack, dict) or not pack.get("name"):
        raise SystemExit("pack: a JSON object with a 'name' is required")
    return pack


def when(pack, args):
    today = date.fromisoformat(args.today) if getattr(args, "today", None) else date.today()
    on = date.fromisoformat(args.on) if getattr(args, "on", None) else (date.fromisoformat(pack["goes_live"]) if pack.get("goes_live") else today)
    return on, today


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("formats")
    s.add_argument("--platform", choices=["google", "meta"])
    s = sub.add_parser("rate")
    s.add_argument("--on")
    for name in ("lint", "export", "render", "build"):
        s = sub.add_parser(name)
        s.add_argument("pack")
        s.add_argument("--on")
        s.add_argument("--today")
        if name != "lint":
            s.add_argument("--out", required=True)
        if name in ("render", "build"):
            s.add_argument("--creative")
            s.add_argument("--only")
            s.add_argument("--keep-html", action="store_true")
    s = sub.add_parser("check")
    s.add_argument("dir")
    s = sub.add_parser("preflight")
    s.add_argument("url")
    s.add_argument("--pack")
    s = sub.add_parser("photo")
    s.add_argument("image")
    s.add_argument("--out", required=True)
    s.add_argument("--formats", required=True)
    s.add_argument("--focus", default="0.5,0.5")
    s.add_argument("--name", default="photo")
    a = ap.parse_args(argv)

    if a.cmd == "formats":
        print_formats(a.platform)
        return 0
    if a.cmd == "rate":
        print_rate(date.fromisoformat(a.on) if a.on else date.today())
        return 0
    if a.cmd == "check":
        return 1 if check_outputs(Path(a.dir)) else 0
    if a.cmd == "preflight":
        return preflight(a.url, load(a.pack) if a.pack else None)
    if a.cmd == "photo":
        fx, fy = (float(v) for v in a.focus.split(","))
        fit_photo(a.image, Path(a.out), [k for k in a.formats.split(",") if k], (fx, fy), a.name)
        return 0

    pack = load(a.pack)
    on, today = when(pack, a)
    if a.cmd in ("lint", "build"):
        rep = lint_pack(pack, on, today)
        rep.print()
        if rep.errors:
            return 1
        if a.cmd == "lint":
            return 0
    out = Path(a.out) if a.cmd != "lint" else None
    if a.cmd in ("export", "build"):
        export(pack, out)
    if a.cmd in ("render", "build"):
        only = set(a.only.split(",")) if a.only else None
        _, problems = render_all(pack, out, a.creative, only, a.keep_html)
        if any(p.startswith("ERROR") for p in problems):
            return 1
        if a.cmd == "build":
            return 1 if check_outputs(out) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
