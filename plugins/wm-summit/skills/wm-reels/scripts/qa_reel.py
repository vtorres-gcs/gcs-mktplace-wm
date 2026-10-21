"""QA for a Reel: the script before approval, the video before delivery.

    python3 qa_reel.py script <script.md>
    python3 qa_reel.py video  <reel.mp4> [--script script.md] [--frames <dir>]

script  Structure (references/script-template.md), voice, facts (prices, times, names), the
        characters rules (references/cast.md) and disclosure. Exit 1 on any ERROR.
video   ffprobe: 1080x1920, audio stream, duration vs the script, fps; caption file limits
        (<=2 lines, <=32 chars, cue length) and overlay boxes from reel.captions.json (safe zone); writes frames for you to LOOK at
        (cue midpoints + first/last) when --frames is given. Pixels are judged by eye, not by code.

Standard library only (ffprobe/ffmpeg for `video`). Python 3.9+.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reelscript  # noqa: E402

try:
    import facts
except (ImportError, FileNotFoundError) as e:  # pragma: no cover
    facts = None
    print(f"WARN  fact checks skipped: {e}")

EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
TIME = re.compile(r"(?<![\d:])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])")
URGENCY = re.compile(r"\b(last chance|only \d+ (seats|places|tickets)|hurry|don'?t miss|sold out|book now|act now|running out)\b", re.I)
OUTCOME = re.compile(r"\b(guarantee[sd]?|guaranteed|you will (get|obtain|receive|become)|get(ting)? (your )?(a )?(passport|visa|citizenship|residency) (in|within)|tax[- ]free|zero tax|pay no tax|no taxes|risk[- ]free|returns? of|\d+% (return|yield))\b", re.I)
TESTIMONIAL = re.compile(r"\b(I|we|I've|we've|I'm|we're)\s+(moved|got|obtained|received|saved|became|relocated|secured|bought|invested|left|applied)\b", re.I)
SUPERLATIVE = re.compile(r"\b(best|world[- ]class|unmissable|unparalleled|ultimate|incredible|amazing|exclusive)\b", re.I)
STALE = {
    "golden visa pathway": "Day One theme is now 'The New Geography of Wealth & Mobility'",
    "networking dinner": "there is no dinner; Day Two has a cocktail reception",
    "private dinner": "there is no dinner",
    "150\u2013200": "capacity is 'Limited to 200'",
    "150-200": "capacity is 'Limited to 200'",
    "14 speakers": "the site lists 28 speakers",
    "register your interest": "the CTA is 'Secure your place'",
}
AGENDA_ONLY = ["Maggie Williams", "Grazi Fulchiron", "Sheree M. Mitchell", "Adrien Bridge", "Joana Costa",
               "Diogo Pedro", "Joana M.", "Gon\u00e7alo Peixoto", "Louren\u00e7o Alvares", "Gizane Campos"]
CAST = ["Daniel", "Clara", "Thomas", "Elena", "Adrian"]
DASH = "\u2013"
DISCLOSURE = "characters are ai-generated"
MAX_LINE, MAX_LINES = 32, 2
SAFE = {"x": (80, 1000), "y": (270, 1250)}


def _fact_check(tag, txt, errors, warns, today):
    if not facts:
        return
    low = txt.lower()
    for stale, why in STALE.items():
        if stale in low:
            errors.append(f"{tag}: '{stale}' \u2014 {why}")
    for m in re.finditer(r"\u20ac\s?(\d[\d,.]*)|\b(\d[\d,.]*)\s?(?:euros?|eur)\b", txt, re.I):
        amount = int(re.sub(r"\D", "", (m.group(1) or m.group(2)).split(".")[0]) or 0)
        tiers = [t for t in facts.rates()["tiers"] if t["eur"] == amount]
        if not tiers:
            errors.append(f"{tag}: \u20ac{amount} is not a published rate")
            continue
        t = tiers[0]
        if date.fromisoformat(t["end"]) < today:
            errors.append(f"{tag}: \u20ac{amount} was the {t['name']} and has ended")
        elif date.fromisoformat(t["start"]) > today:
            warns.append(f"{tag}: \u20ac{amount} ({t['name']}) starts {t['when'].split(DASH)[0].strip()}")
        else:
            warns.append(f"{tag}: \u20ac{amount} ({t['name']}) valid until {t['when'].split(DASH)[-1].strip()} \u2014 say so in the hand-off")
    known = facts.known_times()
    for m in TIME.finditer(txt):
        hhmm = f"{int(m.group(1)):02d}:{m.group(2)}"
        if hhmm not in known:
            errors.append(f"{tag}: time {hhmm} is not on the site's programme")
    for name in AGENDA_ONLY:
        if name.lower() in low:
            errors.append(f"{tag}: '{name}' is an agenda-only name, not a speaker")


def qa_script(path):
    md = Path(path).read_text(encoding="utf-8")
    s = reelscript.parse(md)
    errors, warns = [], []

    for f, key in (("Facts as of", "facts_as_of"), ("Platform", "platform"), ("Goal", "goal"), ("Length", "length"),
                   ("Post date", "post_date"), ("Cast", "cast")):
        if not s[key]:
            errors.append(f"missing header line '{f}:'")
    if s["platform"] and "reel" not in s["platform"].lower():
        errors.append("Platform must be 'Instagram Reel'")
    if s["language"] and s["language"].lower() != "english":
        warns.append(f"language is {s['language']} \u2014 English is the default; mark non-English as 'not client-approved'")
    for h in ("## Concept", "## Beats", "## Cover", "## Caption", "## Alt text", "## Before publishing"):
        if h not in md:
            errors.append(f"missing section '{h}'")
    if not s["keyword"]:
        errors.append("Concept needs 'Keyword:'")
    if not s["sends"]:
        errors.append("Concept needs 'Sends test:' (who sends this to whom, and why)")

    beats = s["beats"]
    if not beats:
        errors.append("no beats parsed from the table")
    else:
        prev = 0.0
        for b in beats:
            if abs(b["start"] - prev) > 0.05:
                errors.append(f"beat {b['n']}: starts at {b['start']}s but the previous beat ended at {prev}s (beats are contiguous)")
            if b["end"] <= b["start"]:
                errors.append(f"beat {b['n']}: end <= start")
            prev = b["end"]
        if s["length_s"] and abs(prev - s["length_s"]) > 0.5:
            errors.append(f"last beat ends at {prev}s but Length says {s['length_s']}s")
        total = prev
        if total < 10:
            warns.append(f"{total:.0f}s is short; fine if the idea is complete")
        if total > 35:
            warns.append(f"{total:.0f}s: above the ~15\u201335s reach sweet spot \u2014 earn it or cut")
        if any(b["end"] - b["start"] > 4.5 for b in beats):
            warns.append("a beat is longer than ~4s \u2014 change the visual every 2\u20134s")
        first = beats[0]
        if not first["onscreen"]:
            errors.append("beat 1 (hook) has no on-screen text \u2014 the hook must work on mute")
        elif len(first["onscreen"].split()) > 7:
            errors.append(f"hook on-screen text is {len(first['onscreen'].split())} words (max 7)")
        if not first["spoken"]:
            warns.append("beat 1 has no spoken line \u2014 hook should fire on verbal + text + visual")
        elif len(" ".join(first["spoken"]).split()) > 12:
            warns.append("hook spoken line is over 12 words")
        if first["start"] != 0 or first["end"] > 3.5:
            warns.append("hook beat should run 0\u20133s")
        if s["keyword"]:
            k = s["keyword"].lower()
            early = " ".join(" ".join(b["spoken"]) + " " + b["onscreen"] for b in beats if b["start"] < 3.5).lower()
            if k not in early:
                warns.append(f"keyword '{s['keyword']}' is not in the spoken/on-screen text of the first ~3s")
            if k not in s["caption"].split(".")[0].lower():
                warns.append("keyword is not in the caption's first sentence")
        mid_text = [b["n"] for b in beats[1:-1] if b["onscreen"]]
        if mid_text:
            warns.append(f"on-screen text in beat(s) {', '.join(mid_text)}: captions carry the speech; keep text to the hook and the CTA")
        for b in beats:
            sp = " ".join(b["spoken"])
            dur = max(b["end"] - b["start"], 0.1)
            if sp and len(sp.split()) / dur > 4.2:
                errors.append(f"beat {b['n']}: {len(sp.split())} words in {dur:.1f}s \u2014 too fast to lip-sync (max ~12 words per 3s)")
            if len(b["spoken"]) > 1 and not all(isinstance(x, str) for x in b["spoken"]):
                errors.append(f"beat {b['n']}: one speaker per beat")
        last_n = beats[-1]["onscreen"]
        if last_n and len(last_n.split()) > 7:
            errors.append("CTA on-screen text is over 7 words")

    texts = {"caption": s["caption"], "alt": " ".join(s["alt"])}
    for b in beats:
        texts[f"beat {b['n']} spoken"] = " ".join(b["spoken"])
        texts[f"beat {b['n']} text"] = b["onscreen"]
    texts["cover"] = s["cover"]
    allt = " ".join(texts.values()) + " " + " ".join(b["shot"] for b in beats)
    if EMOJI.search(md):
        errors.append("emoji \u2014 voice is restrained")
    for tag, t in texts.items():
        if "!" in t:
            errors.append(f"{tag}: exclamation mark")
        for rx, why in ((URGENCY, "urgency mechanics \u2014 scarcity is factual ('Limited to 200 attendees')"),
                        (OUTCOME, "outcome promise \u2014 no visa, citizenship, tax or return guarantees"),
                        (SUPERLATIVE, "superlative \u2014 say what happens, not how special it is")):
            m = rx.search(t)
            if m:
                errors.append(f"{tag}: '{m.group(0)}' \u2014 {why}")
        if tag.endswith("spoken") or tag == "caption":
            m = TESTIMONIAL.search(t)
            if m:
                errors.append(f"{tag}: '{m.group(0)}\u2026' reads as a testimonial \u2014 characters ask and explain, they do not report results (cast.md rule 2)")
    for c in CAST:
        for tag in ("caption", "alt"):
            if re.search(rf"\b{c}\b", texts[tag]):
                errors.append(f"{tag}: character name '{c}' \u2014 characters are not named in public copy (cast.md rule 1)")
        for b in beats:
            if re.search(rf"\b{c}\b", b["onscreen"]):
                errors.append(f"beat {b['n']} on-screen text names '{c}'")
    for tag in ("caption",):
        if DISCLOSURE not in texts[tag].lower():
            errors.append("caption must carry 'Characters are AI-generated.'")
    if re.search(r"\b(client|investor|delegate|attendee)\b[^.]*\b(says?|said|tells?)\b", allt, re.I):
        warns.append("a character may be framed as a client/delegate \u2014 check cast.md rule 1")
    shots = re.sub(r"\b(no|without|never|nothing)\b[^.;]*", " ", " ".join(b["shot"] for b in beats), flags=re.I)  # "no signage" is the instruction, not the problem
    if re.search(r"(passport|visa document|\bID\b|logo|signage)", shots, re.I):
        warns.append("a Shot mentions passport/ID/logo/signage \u2014 nothing legible may appear in generated footage (it is added in post)")

    words = len(s["caption"].split())
    if words > 110:
        warns.append(f"caption is {words} words (aim 60\u201390)")
    if words < 30:
        warns.append(f"caption is {words} words (aim 60\u201390)")
    if re.search(r"https?://\S+", s["caption"]):
        warns.append("a URL is in the caption \u2014 only one the user confirmed (FACTS.md \u2192 Booking)")
    if len(s["hashtags"]) > 5:
        errors.append(f"{len(s['hashtags'])} hashtags (3\u20135)")
    if s["hashtags"] and "unconfirmed" not in s["hashtags_line"].lower() and "supplied" not in s["hashtags_line"].lower():
        warns.append("hashtags present \u2014 make sure the user supplied them, or mark them 'unconfirmed'")
    if not s["alt"]:
        errors.append("no alt text lines ('Frame N \u2014 \u2026')")
    for a in s["alt"]:
        if len(a) > 125:
            warns.append(f"alt text over 125 chars: '{a[:50]}\u2026'")
    bp = s["before_publishing"].lower()
    for need, label in (("ai label", "Instagram AI label reminder"), ("audio", "audio / trending-track step"),
                        ("link", "link decision"), ("tier", "price-tier validity line")):
        if need not in bp:
            warns.append(f"'Before publishing' lacks the {label}")
    if facts and re.search(r"\b(main stage|session|panel|workshop)\b", allt, re.I) and "subject to change" not in md.lower():
        warns.append("sessions are mentioned \u2014 add 'Programme subject to change' to the caption")

    today = date.today()
    if s["post_date"]:
        try:
            today = date.fromisoformat(s["post_date"][:10])
        except ValueError:
            warns.append("Post date is not YYYY-MM-DD; prices are checked against today")
    if facts:
        for note in facts.freshness():
            print("NOTE ", note)
        for tag, t in texts.items():
            _fact_check(tag, t, errors, warns, today)

    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\nscript \u00b7 {len(beats)} beat(s) \u00b7 {len(errors)} error(s) \u00b7 {len(warns)} warning(s)")
    return not errors


def _probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return json.loads(r.stdout)


def qa_video(path, script=None, frames=None):
    errors, warns = [], []
    if not shutil.which("ffprobe"):
        print("ERROR ffprobe not found \u2014 run: bash scripts/setup.sh")
        return False
    p = Path(path)
    if not p.is_file():
        print(f"ERROR {p} not found")
        return False
    info = _probe(p)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        errors.append("no video stream")
    else:
        if (v["width"], v["height"]) != (1080, 1920):
            errors.append(f"{v['width']}x{v['height']} \u2014 a Reel is 1080x1920 (9:16)")
        num, den = (v.get("avg_frame_rate") or "0/1").split("/")
        fps = float(num) / float(den or 1) if float(den or 1) else 0
        if fps and fps < 24:
            warns.append(f"{fps:.0f} fps is low")
    if not a:
        errors.append("no audio stream \u2014 a Reel with no audio fails an eligibility gate")
    dur = float(info["format"].get("duration", 0))
    if dur > 180:
        errors.append(f"{dur:.0f}s is over the 3-minute cap")
    if script:
        s = reelscript.parse(Path(script).read_text(encoding="utf-8"))
        if s["beats"]:
            planned = s["beats"][-1]["end"]
            if abs(dur - planned) > 2.0:
                warns.append(f"video is {dur:.1f}s, script planned {planned:.1f}s")

    srt = p.with_suffix(".srt")
    if not srt.is_file():
        srt = p.parent / "reel.srt"
    manifest = p.with_suffix(".captions.json")
    if not srt.is_file():
        errors.append("reel.srt not found next to the video (captions are mandatory)")
    else:
        import captions
        cues = captions.read_srt(srt)
        if not cues:
            errors.append("reel.srt has no cues")
        for i, c in enumerate(cues, 1):
            if len(c["lines"]) > MAX_LINES or any(len(l) > MAX_LINE for l in c["lines"]):
                errors.append(f"cue {i}: over {MAX_LINES} lines / {MAX_LINE} chars")
            if c["end"] - c["start"] < 0.6:
                warns.append(f"cue {i}: {c['end'] - c['start']:.2f}s is too short to read")
            if c["end"] > dur + 0.2:
                errors.append(f"cue {i} ends after the video")
        if cues and cues[-1]["end"] < dur - 6:
            warns.append("captions stop long before the end of the video")
        if cues and cues[0]["start"] > 3.0:
            warns.append("first caption appears after 3s \u2014 the hook must be readable on mute")
    if not manifest.is_file():
        warns.append("no .captions.json next to the video \u2014 captions may not have been burned by captions.py")
    else:
        items = json.loads(manifest.read_text(encoding="utf-8"))
        if not any(i["kind"] == "caption" for i in items):
            errors.append("no caption overlays in the manifest")
        for i in items:
            if i["x"] < SAFE["x"][0] or i["x"] + i["w"] > SAFE["x"][1]:
                errors.append(f"{i['kind']} '{i['text'][:30]}' spans x {i['x']}\u2013{i['x'] + i['w']}, outside the safe zone {SAFE['x']}")
            if i["y"] < SAFE["y"][0] or i["y"] + i["h"] > SAFE["y"][1]:
                errors.append(f"{i['kind']} '{i['text'][:30]}' spans y {i['y']}\u2013{i['y'] + i['h']}, outside the safe zone {SAFE['y']}")

    if frames and shutil.which("ffmpeg") and dur:
        out = Path(frames)
        out.mkdir(parents=True, exist_ok=True)
        stamps = [0.5]
        if srt.is_file():
            import captions
            stamps += [round((c["start"] + c["end"]) / 2, 2) for c in captions.read_srt(srt)][:8]
        stamps.append(max(dur - 0.3, 0))
        for i, t in enumerate(stamps):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(p), "-frames:v", "1",
                            str(out / f"frame-{i:02d}-{t:.2f}s.png")])
        print(f"wrote {len(stamps)} frames to {out} \u2014 look at them: caption inside the box, off the bottom UI zone, readable")

    print(f"video: {dur:.1f}s" + (f" \u00b7 {v['width']}x{v['height']}" if v else "") + (" \u00b7 audio" if a else " \u00b7 NO AUDIO"))
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\nvideo \u00b7 {len(errors)} error(s) \u00b7 {len(warns)} warning(s)")
    return not errors


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("script")
    s1.add_argument("path")
    s2 = sub.add_parser("video")
    s2.add_argument("path")
    s2.add_argument("--script")
    s2.add_argument("--frames")
    a = ap.parse_args()
    ok = qa_script(a.path) if a.cmd == "script" else qa_video(a.path, a.script, a.frames)
    sys.exit(0 if ok else 1)
