"""Captions for the Reel: SRT from the approved script, burned into the MP4 with ffmpeg, plus a cover frame.

    python3 captions.py build  <script.md> --out reel.srt [--timings timings.json] [--speech START END]
    python3 captions.py burn   <raw.mp4> <reel.srt> <reel.mp4> [--overlays reel.overlays.json]
    python3 captions.py cover  <reel.mp4> <cover.png> [--at 1.0]

build   Writes reel.srt (plain, deliverable) and reel.overlays.json (hook text, CTA, gold keyword).
        --timings: JSON list [{"word": "...", "start": 0.0, "end": 0.4}, ...] from audio_timing_get.
        Without it, each beat's words are spread over the beat window by character weight (estimate; scrub it).
        --speech START END: seconds at which the speech really starts and ends in the video (listen / scrub once);
        the estimated cues are stretched into that window. Use it when no word timings are available.
burn    Renders each cue/hook/CTA as a transparent PNG (Pillow, bundled fonts, Summit style from
        references/captions-style.md) and overlays them with ffmpeg. No libass/drawtext needed.
cover   Extracts one frame as PNG.

Needs ffmpeg for burn/cover (scripts/setup.sh) and Pillow for burn. Python 3.9+.
"""

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reelscript  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent
FONTS = SKILL_DIR / "assets" / "fonts"

W, H = 1080, 1920
MAX_LINE = 32
MAX_LINES = 2
MIN_CUE, MAX_CUE = 0.9, 4.0
WEAK_END = {"the", "a", "an", "of", "and", "to", "in", "on", "for", "your", "our", "is", "are", "at", "with", "or"}
CAPTION_Y = 1150      # box vertical centre, ~60% of H, above Instagram's bottom 35% (y > 1250)
HOOK_Y = 540          # ~28%
CTA_Y = 810           # ~42%
SAFE_X = (80, 1000)
SAFE_Y = (270, 1250)



# --------------------------------------------------------------------------- cues

def _norm(w):
    return re.sub(r"[^\w]", "", w.lower())


def _wrap(text):
    """Greedy wrap into <=2 lines of <=32 chars; returns list of lines or None if it does not fit."""
    lines, cur = [], ""
    for w in text.split():
        if len(cur) + (1 if cur else 0) + len(w) <= MAX_LINE:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines if len(lines) <= MAX_LINES and all(len(l) <= MAX_LINE for l in lines) else None


def _chunks(text):
    """Split a spoken line into cue-sized phrases: break at punctuation first, then pack greedily."""
    parts = re.findall(r"[^,;:.?!—]+[,;:.?!—]*", text) or [text]
    chunks, cur = [], ""
    for p in (x.strip() for x in parts):
        if not p:
            continue
        trial = f"{cur} {p}".strip()
        if cur and _wrap(trial) is None:
            chunks.append(cur)
            cur = p
        else:
            cur = trial
    if cur:
        chunks.append(cur)
    for i in range(1, len(chunks)):       # an orphan ("not three.") reads badly: rebalance with its neighbour
        if len(chunks[i]) < 14 and len(chunks[i - 1]) >= 14:
            ws = (chunks[i - 1] + " " + chunks[i]).split()
            ok = [k for k in range(1, len(ws))          # never strand "B" of "Plan B" or end a cue on "the"/"of"
                  if len(re.sub(r"\W", "", ws[k])) > 2 and re.sub(r"\W", "", ws[k - 1]).lower() not in WEAK_END]
            if ok:
                best = min(ok, key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
                left, right = " ".join(ws[:best]), " ".join(ws[best:])
                if _wrap(left) and _wrap(right):
                    chunks[i - 1], chunks[i] = left, right
    out = []
    for c in chunks:                      # a single phrase can still be too long: split by words
        while _wrap(c) is None:
            ws, take = c.split(), []
            while ws and _wrap(" ".join(take + [ws[0]])) is not None:
                take.append(ws.pop(0))
            out.append(" ".join(take))
            c = " ".join(ws)
        out.append(c)
    return out


def _estimate(beats):
    """Cues with estimated times: words of each beat spread over the beat window by character weight."""
    cues = []
    for b in beats:
        text = " ".join(b["spoken"]).strip()
        if not text:
            continue
        lead, tail = 0.15, 0.1
        s, e = b["start"] + lead, max(b["start"] + lead + 0.5, b["end"] - tail)
        chunks = _chunks(text)
        weights = [max(len(c), 1) for c in chunks]
        total, t = sum(weights), s
        for c, wt in zip(chunks, weights):
            d = (e - s) * wt / total
            cues.append({"start": t, "end": t + d, "text": c})
            t += d
    return cues


def _remap(cues, start, end):
    """Stretch estimated cues linearly so the first starts at `start` and the last ends at `end`."""
    t0, t1 = cues[0]["start"], cues[-1]["end"]
    k = (end - start) / (t1 - t0) if t1 > t0 else 1.0
    return [{"start": start + (c["start"] - t0) * k, "end": start + (c["end"] - t0) * k, "text": c["text"]} for c in cues]


def _snap(cues, script_words, timings):
    """Replace estimated times by real word times: script words map to timing words (same order)."""
    tw = [t for t in timings if _norm(t["word"])]
    sw = [_norm(w) for w in script_words]
    tn = [_norm(t["word"]) for t in tw]
    if len(sw) == len(tn):
        idx = list(range(len(sw)))
    else:
        sm = difflib.SequenceMatcher(None, sw, tn, autojunk=False)
        idx = [None] * len(sw)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n):
                idx[a + k] = b + k
        known = [(i, v) for i, v in enumerate(idx) if v is not None]
        if len(known) < max(3, len(sw) // 3):
            print(f"WARN  only {len(known)}/{len(sw)} script words match the timings; keeping estimated times", file=sys.stderr)
            return cues
        for i in range(len(idx)):         # interpolate gaps
            if idx[i] is None:
                prev = max((v for j, v in known if j < i), default=0)
                nxt = min((v for j, v in known if j > i), default=len(tn) - 1)
                idx[i] = min(prev + 1, nxt)
    out, pos = [], 0
    for c in cues:
        n = len(c["text"].split())
        seg = idx[pos:pos + n]
        pos += n
        if not seg:
            out.append(c)
            continue
        out.append({"start": tw[seg[0]]["start"], "end": tw[seg[-1]]["end"], "text": c["text"]})
    return out


def _fit(cues):
    """Enforce cue duration bounds and no overlaps."""
    cues = sorted(cues, key=lambda c: c["start"])
    for i, c in enumerate(cues):
        nxt = cues[i + 1]["start"] if i + 1 < len(cues) else c["end"] + MAX_CUE
        c["end"] = max(c["end"], min(c["start"] + MIN_CUE, nxt - 0.02))
        c["end"] = min(c["end"], c["start"] + MAX_CUE, nxt - 0.02)
    return cues


def _ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def cmd_build(a):
    s = reelscript.parse(Path(a.script).read_text(encoding="utf-8"))
    if not s["beats"]:
        sys.exit("ERROR no beats found in the script table (references/script-template.md)")
    cues = _estimate(s["beats"])
    estimated = True
    if a.timings:
        timings = json.loads(Path(a.timings).read_text(encoding="utf-8"))
        script_words = [w for b in s["beats"] for l in b["spoken"] for w in l.split()]
        snapped = _snap(cues, script_words, timings)
        estimated = snapped is cues
        cues = snapped
    if a.speech and estimated and cues:
        cues = _remap(cues, a.speech[0], a.speech[1])
    cues = _fit(cues)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, c in enumerate(cues, 1):
        wrapped = _wrap(c["text"]) or [c["text"]]
        lines += [str(i), f"{_ts(c['start'])} --> {_ts(c['end'])}", "\n".join(wrapped), ""]
    out.write_text("\n".join(lines), encoding="utf-8")

    first, last = s["beats"][0], s["beats"][-1]
    overlays = {"keyword": s["keyword"], "hook": None, "cta": None}
    if first["onscreen"]:
        overlays["hook"] = {"text": first["onscreen"], "start": first["start"], "end": min(first["end"], first["start"] + 3.0)}
    if len(s["beats"]) > 1 and last["onscreen"]:
        overlays["cta"] = {"text": last["onscreen"], "start": max(last["start"], last["end"] - 3.0), "end": last["end"]}
    ov = out.with_suffix(".overlays.json")
    ov.write_text(json.dumps(overlays, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} ({len(cues)} cues, {'ESTIMATED' if estimated else 'real'} timings) and {ov}")
    if estimated:
        print("WARN  times are estimated from the beat windows; scrub the SRT against the video before delivery")


# --------------------------------------------------------------------------- PNG overlays + burn
# The brew/stock ffmpeg often ships without libass and drawtext, so text is rendered to transparent
# PNGs with Pillow (bundled fonts) and laid over the video with the plain `overlay` filter.

FONT_FILES = {"Caption": ("Archivo-600.ttf", 56), "Cta": ("Archivo-600.ttf", 60), "Hook": ("Caladea-Regular.ttf", 76)}
PAD_X, PAD_Y, LINE_GAP = 34, 22, 14
GOLD_LIT = (0xDC, 0xC0, 0x8B)
NAVY = (0x12, 0x1B, 0x31)
BOX_OPACITY = 184  # ~72 %


def read_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8").strip()):
        ls = block.splitlines()
        if len(ls) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", ls[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        cues.append({"start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
                     "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000,
                     "lines": ls[2:]})
    return cues


def _render(lines, kind, keyword, path):
    """Transparent PNG: navy box (72 %), white text, one gold keyword. Returns (w, h)."""
    from PIL import Image, ImageDraw, ImageFont
    fname, size = FONT_FILES[kind]
    font = ImageFont.truetype(str(FONTS / fname), size)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    asc, desc = font.getmetrics()
    lh = asc + desc
    widths = [probe.textlength(l, font=font) for l in lines]
    w = int(max(widths)) + 2 * PAD_X
    h = lh * len(lines) + LINE_GAP * (len(lines) - 1) + 2 * PAD_Y
    im = Image.new("RGBA", (w, h), NAVY + (BOX_OPACITY,))
    d = ImageDraw.Draw(im)
    pat = re.compile(r"(?<!\w)(" + re.escape(keyword) + r")(?!\w)", re.I) if keyword else None
    gold_used = False
    for i, line in enumerate(lines):
        x = (w - widths[i]) / 2
        y = PAD_Y + i * (lh + LINE_GAP)
        m = pat.search(line) if (pat and not gold_used and kind == "Caption") else None
        if m:
            gold_used = True
            for chunk, colour in ((line[:m.start()], (255, 255, 255)), (m.group(1), GOLD_LIT), (line[m.end():], (255, 255, 255))):
                if chunk:
                    d.text((x, y), chunk, font=font, fill=colour + (255,))
                    x += probe.textlength(chunk, font=font)
        else:
            d.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    im.save(path)
    return w, h


def build_items(cues, overlays, workdir):
    items = []
    keyword = (overlays or {}).get("keyword", "")
    for i, c in enumerate(cues):
        png = workdir / f"cap-{i:03d}.png"
        w, h = _render(c["lines"], "Caption", keyword, png)
        items.append({"kind": "caption", "png": str(png), "w": w, "h": h, "x": (W - w) // 2,
                      "y": CAPTION_Y - h // 2, "start": c["start"], "end": c["end"], "text": " / ".join(c["lines"])})
    for key, kind, y in (("hook", "Hook", HOOK_Y), ("cta", "Cta", CTA_Y)):
        o = (overlays or {}).get(key)
        if o and o.get("text"):
            lines = _wrap(o["text"]) or [o["text"]]
            png = workdir / f"{key}.png"
            w, h = _render(lines, kind, "", png)
            items.append({"kind": key, "png": str(png), "w": w, "h": h, "x": (W - w) // 2, "y": y - h // 2,
                          "start": o["start"], "end": o["end"], "text": " / ".join(lines)})
    return items


def _need_ffmpeg():
    if not shutil.which("ffmpeg"):
        sys.exit("ERROR ffmpeg not found. Run: bash scripts/setup.sh (it asks before installing)")


def cmd_burn(a):
    _need_ffmpeg()
    srt = Path(a.srt)
    ov_path = Path(a.overlays) if a.overlays else srt.with_suffix(".overlays.json")
    overlays = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.is_file() else {}
    out = Path(a.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    src = Path(a.video).resolve()
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        items = build_items(read_srt(srt), overlays, td)
        # manifest next to the video: qa_reel.py checks positions and timing from it
        manifest = [{k: v for k, v in it.items() if k != "png"} for it in items]
        out.with_suffix(".captions.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src)]
        for it in items:
            cmd += ["-i", it["png"]]
        chain = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0]"]
        for n, it in enumerate(items, 1):
            chain.append(f"[v{n - 1}][{n}:v]overlay={it['x']}:{it['y']}:enable='between(t,{it['start']:.3f},{it['end']:.3f})'[v{n}]")
        cmd += ["-filter_complex", ";".join(chain), "-map", f"[v{len(items)}]", "-map", "0:a?",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ERROR ffmpeg failed: " + (r.stderr.strip().splitlines() or ["?"])[-1])
    print(f"wrote {out} ({len(items)} overlays burned in; positions in {out.with_suffix('.captions.json').name})")


def cmd_cover(a):
    _need_ffmpeg()
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a.at), "-i", a.video,
                        "-frames:v", "1", a.output], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ERROR ffmpeg failed: " + (r.stderr.strip().splitlines() or ["?"])[-1])
    print(f"wrote {a.output}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("script")
    b.add_argument("--out", required=True)
    b.add_argument("--timings")
    b.add_argument("--speech", nargs=2, type=float, metavar=("START", "END"))
    u = sub.add_parser("burn")
    u.add_argument("video")
    u.add_argument("srt")
    u.add_argument("output")
    u.add_argument("--overlays")
    c = sub.add_parser("cover")
    c.add_argument("video")
    c.add_argument("output")
    c.add_argument("--at", type=float, default=1.0)
    a = p.parse_args()
    {"build": cmd_build, "burn": cmd_burn, "cover": cmd_cover}[a.cmd](a)
