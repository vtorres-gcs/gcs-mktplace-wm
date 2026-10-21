"""Confirmed Summit facts, as data — and the date arithmetic that goes with them.

Reads references/data/*.json (written by sync_site_facts.py from the site's index.html).
Use it instead of typing a price, a session time or a speaker's role from memory.

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path("<SKILL_DIR>") / "scripts"))
    import facts

    facts.rate_on()               # the rate tier in force today (or on a date)
    facts.days_to_go()            # whole days to 5 Nov 2026
    facts.speaker("pucca")        # one speaker: name, display, role, slug, photo_bundled
    facts.programme()[0]["main"]  # Day One main-stage rows
    facts.freshness()             # warnings: facts older than the site, event over, rate about to change

CLI (same functions, for a quick look):

    python3 facts.py rate | days | freshness | speakers | speaker <query> | programme [1|2] | names | overlaps

Standard library only.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import json
import re
import sys
import unicodedata

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA = SKILL_DIR / "references" / "data"

EVENT_START = date(2026, 11, 5)
EVENT_END = date(2026, 11, 6)
STALE_AFTER_DAYS = 7  # bundled facts older than this: re-run sync_site_facts.py check


def _load(name: str) -> dict:
    p = DATA / name
    if not p.is_file():
        raise FileNotFoundError(f"{p} not found — run: python3 {SKILL_DIR / 'scripts' / 'sync_site_facts.py'} sync <site-repo>")
    return json.loads(p.read_text(encoding="utf-8"))


def _fold(s: str) -> str:
    """Case- and accent-insensitive key: 'João Pacheco Gonçalves' ~ 'joao pacheco goncalves'; curly and straight quotes alike."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("’", "'").replace("'", "").replace("-", " ").split())


def _on(d) -> date:
    if d is None:
        return date.today()
    return date.fromisoformat(d) if isinstance(d, str) else (d.date() if isinstance(d, datetime) else d)


# ----------------------------------------------------------------------------
# Speakers — 26 on the site, in site order (the order the roster must be shown in)
# ----------------------------------------------------------------------------

def speakers() -> list:
    return _load("speakers.json")["speakers"]


def speaker(query: str) -> dict:
    """One speaker by any unambiguous part of the name, or by slug. Raises if none or several match."""
    q = _fold(query)
    hits = [s for s in speakers() if q in _fold(s["name"]) or q in _fold(s["display"]) or q == _fold(s["slug"].replace("-", " "))]
    if len(hits) != 1:
        names = ", ".join(s["display"] for s in hits) or "none"
        raise LookupError(f"{query!r} matches {len(hits)} speakers ({names}) — a name not on the site's roster is not drawn")
    return hits[0]


def speaker_photo(query: str) -> Path:
    s = speaker(query)
    p = SKILL_DIR / "assets" / "speakers" / f"{s['slug']}.webp"
    if not p.is_file():
        raise FileNotFoundError(f"no bundled portrait for {s['display']} — use initials, never a generated face")
    return p


# ----------------------------------------------------------------------------
# Programme — programme/build.py (the agenda page's table) is the source, by the user's decision of 20 Oct 2026.
# It carries start AND end times, a format, and the speakers of every session; index.html's version differs.
# ----------------------------------------------------------------------------

def programme() -> list:
    return _load("programme.json")["days"]


def site() -> dict:
    """Hero line, lede, audience, venue spellings, partner logos on the site — see references/FACTS.md."""
    return _load("site.json")


def programme_disclaimer() -> str | None:
    """The line the agenda page prints under its heading ("Programme subject to change.")."""
    return _load("programme.json").get("disclaimer")


def known_times() -> set:
    """Every HH:MM the agenda publishes, start or end. A time on a slide must be in here."""
    out = set()
    for d in programme():
        for track in ("main", "workshops"):
            for r in d[track]:
                out.add(r["time"])
                if r.get("end"):
                    out.add(r["end"])
    return out


TBA = "To be announced"


def speaker_line(row: dict) -> str:
    """One line for a session's speakers, as the agenda writes them: 'Name, Org (Role) · Name, Org'.
    A slot the agenda marks 'To be announced' reads 'Speaker · to be announced' — never a guessed name."""
    parts = []
    for s in row.get("speakers", []):
        if isinstance(s, str):  # a workshop leader
            parts.append("Leader to be announced" if s == TBA else s)
        elif s.get("org") == TBA:
            parts.append(f"{s['name']} · to be announced")
        else:
            txt = s["name"] + (f", {s['org']}" if s.get("org") else "")
            parts.append(txt + (f" ({s['role']})" if s.get("role") else ""))
    return " · ".join(parts)


_TITLES = {"dr", "he", "md", "phd", "h", "e"}


def _tokens(name: str) -> set:
    return {t for t in _fold(re.sub(r"[().,]", " ", name)).split() if t not in _TITLES}


def agenda_only_names() -> list:
    """Named people on the agenda who are NOT among the 26 on the site's speaker roster (no portrait, no bio on
    the site) and are not a 'To be announced' slot. They may be shown as the agenda writes them — but they must be
    confirmed before the deck leaves GCS."""
    roster = [_tokens(s["name"]) for s in speakers()]
    seen, out = set(), []
    for d in programme():
        for track in ("main", "workshops"):
            for r in d[track]:
                for s in r.get("speakers", []):
                    name, org = (s, None) if isinstance(s, str) else (s["name"], s.get("org"))
                    if name == TBA or org == TBA or name in seen:
                        continue
                    seen.add(name)
                    if not any(_tokens(name) <= r_ for r_ in roster):
                        out.append(name)
    return out


def overlaps() -> list:
    """Main-stage rows whose time range runs into the next row's start — the site's THEMES.md flags these as needing
    organiser confirmation. Returns (day, earlier row, later row)."""
    out = []
    for d in programme():
        rows = d["main"]
        for a, b in zip(rows, rows[1:]):
            if a.get("end") and a["end"] > b["time"]:
                out.append((d["day"], a, b))
    return out


def find_session(text: str) -> list:
    """Rows whose title contains `text` (folded). Use to confirm a title is verbatim before it goes on a slide."""
    q = _fold(text)
    return [(d["day"], r) for d in programme() for track in ("main", "workshops") for r in d[track] if q in _fold(r["full"])]


# ----------------------------------------------------------------------------
# Rates — published by date, so the right figure depends on the day you generate
# ----------------------------------------------------------------------------

def rates() -> dict:
    return _load("rates.json")


def rate_on(on=None):
    """The tier in force on `on` (default today), or None when no published tier covers the date.

    None before 1 Sep 2026 and after 4 Nov 2026 (the site lists nothing for 5–6 Nov): say nothing about price then."""
    d = _on(on)
    for t in rates()["tiers"]:
        if date.fromisoformat(t["start"]) <= d <= date.fromisoformat(t["end"]):
            return t
    return None


def next_rate(on=None):
    d = _on(on)
    later = [t for t in rates()["tiers"] if date.fromisoformat(t["start"]) > d]
    return min(later, key=lambda t: t["start"]) if later else None


def published_amounts() -> set:
    return {t["eur"] for t in rates()["tiers"]}


# ----------------------------------------------------------------------------
# Dates
# ----------------------------------------------------------------------------

def days_to_go(on=None) -> int:
    """Whole days from `on` (default today) to the first day, 5 Nov 2026. Negative once it has started."""
    return (EVENT_START - _on(on)).days


def freshness(on=None) -> list:
    """Warnings the hand-off must carry. Empty list = nothing to flag."""
    d, out = _on(on), []
    if d > EVENT_END:
        out.append("The Summit is over (6 Nov 2026). Every fact in this skill is forward-looking — "
                   "no recap copy without facts the user supplies.")
    meta = _load("site.json")["_meta"]
    age = (d - date.fromisoformat(meta["extracted_on"])).days
    if age > STALE_AFTER_DAYS:
        out.append(f"Bundled facts were extracted {age} days ago from site commit {meta['site_commit']}. "
                   "Run `python3 scripts/sync_site_facts.py check <site-repo>` before relying on prices, times or speakers.")
    t, nxt = rate_on(d), next_rate(d)
    if t and nxt:
        left = (date.fromisoformat(t["end"]) - d).days
        if left <= 7:
            out.append(f"The {t['name']} ({t['price']}) ends {t['when'].split('–')[-1].strip()} — {left} day(s). "
                       f"A post published after that must use the {nxt['name']} ({nxt['price']}), or leave price out.")
    return out


# ----------------------------------------------------------------------------

def _cli(argv):
    cmd = argv[0] if argv else "freshness"
    if cmd == "rate":
        t = rate_on()
        print(f"{t['name']} {t['price']} ({t['when']})" if t else "no published rate for today")
    elif cmd == "days":
        print(days_to_go())
    elif cmd == "freshness":
        print("\n".join(freshness()) or "nothing to flag")
    elif cmd == "speakers":
        for s in speakers():
            print(f"{s['order']:>2}  {s['display']:<34} {s['role']}" + ("" if s["photo_bundled"] else "   [no portrait]"))
    elif cmd == "speaker":
        s = speaker(" ".join(argv[1:]))
        print(f"{s['display']}\n{s['role']}\nportrait: assets/speakers/{s['slug']}.webp\n\n{s['bio']}")
    elif cmd == "names":
        print("on the agenda but not on the 26-speaker roster:", ", ".join(agenda_only_names()) or "none")
    elif cmd == "overlaps":
        for day, a, b in overlaps():
            print(f"{day}: {a['time']}–{a['end']} {a['title']!r} runs into {b['time']} {b['title']!r}")
    elif cmd == "programme":
        which = int(argv[1]) - 1 if len(argv) > 1 else None
        for i, d in enumerate(programme()):
            if which is not None and i != which:
                continue
            print(f"\n{d['day']} · {d['date']} — {d['theme']}")
            for track in ("main", "workshops"):
                print(f"  [{track}]")
                for r in d[track]:
                    end = f"–{r['end']}" if r.get("end") else ""
                    spk = speaker_line(r)
                    print(f"   {r['time']}{end}  {'· ' if r['kind'] == 'break' else ''}{r['full']}" + (f"\n          {spk}" if spk else ""))
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    _cli(sys.argv[1:])
