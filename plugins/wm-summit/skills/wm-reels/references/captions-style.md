# Burned-in captions and on-screen text

Captions are mandatory in the final MP4. Most viewers watch on mute, and AI video cannot be trusted to render letters, so every character of text is added in post by `scripts/captions.py`.

## Style (from `DESIGN.md`)

| Property | Value |
|---|---|
| Font | Archivo 600 (`assets/fonts/Archivo-600.ttf`), rendered with Pillow — no 700 is bundled; do not substitute |
| Size | 56 px at 1080 wide (readable on a phone; never below the 12 px floor in DESIGN.md at any scale) |
| Colour | white `#FFFFFF` on a navy `#121B31` box at ~72 % opacity |
| Highlight | **at most one** gold word or short key phrase (the script's `Keyword:`) per caption cue, `#DCC08B` (lit gold, passes contrast on navy). Plain gold `#C2A358` only on navy — never on white or a light frame |
| Shape | square corners, no pills, no outlines, no shadows, no emoji |
| Case | sentence case, as spoken; British spelling |
| Lines | ≤ 2 lines, ≤ 32 characters per line; split on phrase boundaries, never mid-word |
| Duration | each cue 0.9–4.0 s; ≤ 17 characters per second |
| Position | centred horizontally; box vertical centre at ≈ 60 % of the frame height (≈ y 1150), above the bottom 35 % UI zone (y > 1250 is covered) and inside the side margins (x 80–1000) |
| Words | what is said, trimmed lightly for reading; numbers and prices exactly as in FACTS.md |

## Hook and CTA text

The script's *on-screen text* column (hook ≤ 7 words, CTA) is rendered by the same tool as separate overlays: hook text at ≈ 28 % height (y ≈ 540) in Caladea, white, with the navy box; CTA (Archivo, ≈ 42 % height, y ≈ 810) in the last ≤ 3 s, above the captions. No logo or end card is burned in by default (a GCS or partner mark only if the user asks, placed by hand; nothing is written beside or over the GCS mark).

## Timings

Best case is real word timings: `video_extract_audio` on the clip, then `audio_timing_get` on the audio creation, saved as `timings.json` (`[{"word": "...", "start": 0.0, "end": 0.4}, …]`) and passed with `--timings`. In practice the Magnific audio often has no persisted alignment ("unavailable"; do not invent timings). The fallback is an estimate: `captions.py` spreads each beat's words over the beat window by character weight, and `--speech START END` stretches those cues into the window where the voice really is (in the 5 s test clip the voice ran from 0.7 s to 4.2 s; unaligned estimates started at 0.15 s). Find START/END from `video_analyze` or by looking at frames, then always scrub the result against the video and hand-edit the SRT where a line is early or late. With several clips, build and burn per clip, or hand-edit the joined SRT.

## Checks (`qa_reel.py video`)

Code checks, no pixel analysis: the output is 1080×1920 with an audio stream; `reel.srt` cues are ≤ 2 lines / ≤ 32 characters, not shorter than 0.6 s, and end inside the video; the first caption starts within 3 s; every overlay box in `reel.captions.json` (written by `captions.py burn`) sits inside x 80–1000, y 270–1250. Then `--frames <dir>` extracts frames at the first/last second and each cue midpoint: **look at them** (caption fully inside its box, clear of the bottom UI zone, readable over the footage, gold word legible) before saying the Reel is done.
