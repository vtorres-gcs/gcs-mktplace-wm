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

    python3 facts.py rate | days | freshness | speakers | speaker <query> | programme [1|2]

Standard library only.
"""

from datetime import date, datetime
from pathlib import Path
import json
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
# Programme — index.html is the source; session↔speaker pairings are NOT in it
# ----------------------------------------------------------------------------

def programme() -> list:
    return _load("programme.json")["days"]


def site() -> dict:
    """Hero line, lede, audience, venue spellings, partner logos on the site — see references/FACTS.md."""
    return _load("site.json")


def known_times() -> set:
    """Every HH:MM that index.html publishes. A time on a slide must be in here."""
    return {r["time"] for d in programme() for track in ("main", "workshops") for r in d[track]}


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
    elif cmd == "programme":
        which = int(argv[1]) - 1 if len(argv) > 1 else None
        for i, d in enumerate(programme()):
            if which is not None and i != which:
                continue
            print(f"\n{d['day']} · {d['date']} — {d['theme']}")
            for track in ("main", "workshops"):
                print(f"  [{track}]")
                for r in d[track]:
                    print(f"   {r['time']}  {'· ' if r['kind'] == 'break' else ''}{r['full']}")
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    _cli(sys.argv[1:])
