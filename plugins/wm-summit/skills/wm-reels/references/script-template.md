# Script template — `output/<slug>/script.md`

`scripts/qa_reel.py script` and `scripts/captions.py build` both read this exact structure. Keep the headings and the table columns.

```markdown
# <Working title>

Facts as of: <YYYY-MM-DD> (FACTS.md @ <commit>)
Platform: Instagram Reel
Language: English
Goal: <reach | sends | saves | follows | comments>
Length: <NN> s · clips: <N> (≤ 15 s each)
Post date: <YYYY-MM-DD> · Rate in force: <tier, €price, until DD Mon> | no price used
Cast: <character name(s)> — <why these>

## Concept
<one idea, one sentence>
Keyword: <target keyword>
Sends test: <who sends this to whom, and why>

## Beats

| # | Sec | Shot | On-screen text | Spoken | Audio / sfx |
|---|---|---|---|---|---|
| 1 | 0–3 | Close, eye-level, Daniel in a blue-hour study, one amber lamp | Where would your family live? | "Where would your family live if the rules changed?" | Daniel, room tone |
| 2 | 3–7 | … | … | "…" | … |

## Cover
<which frame, or custom cover text in the grid-safe centre>

## Caption
<British English, 60–90 words. First sentence carries the keyword. Ends with "Characters are AI-generated.">

Hashtags: <3–5, or "none supplied">

## Alt text
Frame 1 — <≤ 125 chars>
Frame 2 — <…>

## Before publishing
- Turn on Instagram's AI label (manual).
- Add the licensed audio in the app if a track is intended: <direction>.
- Link: <Link in bio | confirmed URL>.
- Price tier valid until <date>.
- <Programme subject to change — if sessions are named>
- <Trial Reel recommended: yes/no, why>
```

Rules for the table:
- **Sec** is `start–end` in seconds; beats are contiguous and the last end equals Length.
- **On-screen text** is hook (beat 1) and CTA (last beat) only; leave `—` elsewhere because the captions carry the speech. Max 7 words.
- **Spoken** lines are in straight double quotes, ≤ 12 words per 3 s, from one speaker per beat; `—` for no speech. Session titles verbatim from `data/programme.json`; times only if in `facts.known_times()`.
- A beat that is pure text over a still: say so in **Shot**.
