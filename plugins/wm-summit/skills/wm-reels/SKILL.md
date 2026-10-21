---
name: wm-reels
description: "Writes and produces Instagram Reels for the Wealth and Migration Summit 2026 (Lisbon, 5–6 November 2026, curated by Global Citizen Solutions): a shootable script (hook, beat table, on-screen text, spoken lines, cover brief, caption, hashtags), and — only after the user approves that script — the finished 9:16 video, generated in Magnific with Kling 3.0 using the existing GCS-PPC characters and burned-in captions. Use whenever the user mentions a Reel, Reels, Instagram video, a short vertical video, a video script, a hook, 'vídeo para o Instagram', or wants any moving-image social content for this event, even if they never say 'reel'. Not for static posts, carousels or Stories (use wm-social-media), paid-ad creatives (use wm-paid-ads), web banners, decks, or general GCS content."
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__library_list, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__images_generate, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__video_generate, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__video_models_list, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__video_concatenate, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__video_extract_frames, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__video_extract_audio, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__video_analyze, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__audio_timing_get, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__creations_wait, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__creations_get, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__creations_register_download, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__simulate_cost, mcp__e560f0ae-6943-437b-90f5-ef99bacc2380__account_balance
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "New skill. Facts synced with site repo at 6725cff (copied from wm-social-media)."
---

# wm-reels — Reels for the Wealth and Migration Summit 2026

Two jobs in strict order: **(A) write the script and get it approved, (B) produce the video.** Nothing is generated before the user says yes to the script, because every clip costs credits and a script change after generation means paying twice.

Why Reels are different from the Summit's static posts: reach comes mostly from non-followers, decided by how viewers respond in the first seconds, by watch-through and by sends (DM shares) — not by follower count. So the script is built for a 3-second hook, for sound-off viewing, and for "who would send this to whom". Read `references/reels-playbook.md` before writing.

## Source of truth

| For | Read |
|---|---|
| Dates, prices, programme, speakers, capacity, CTA wording, what must never be invented | `references/FACTS.md` and `references/data/` (through `scripts/facts.py`) — overrides everything else |
| Voice, audience, positioning | `references/PRODUCT.md` (its fact sections are stale; FACTS.md wins) |
| Palette, type, on-screen text rules | `references/DESIGN.md`, `references/captions-style.md` |
| Instagram mechanics, hook, retention, safe zone | `references/reels-playbook.md` |
| The five characters and the rules for using them | `references/cast.md` |
| Magnific/Kling recipe, costs, failure modes | `references/kling-production.md` |

## What this skill will not do

- Generate anything before script approval, or spend credits without the user seeing the estimate.
- Make a character a **speaker, delegate, client, attendee or testimonial**. The five GCS-PPC characters are fictional production labels. They pose the question or explain the idea; they never claim a personal result ("I got my residency…"). Details in `references/cast.md`.
- Show a real person, the real venue, a passport/ID/document, a partner logo or readable text inside generated footage. AI video garbles text; all text is added in post.
- Promise visas, citizenship, tax outcomes or returns; use urgency mechanics ("last chance", "book now"); name anyone not on the speaker roster.
- Add trending audio. Instagram's licensed library is native-only: the script names the audio direction and a human adds the track in the app.
- Re-post a watermarked TikTok/CapCut export (originality gate) — re-cut a clean version instead.

## Part A — Script (stop at the gate)

**0. Freshness.** `python3 scripts/facts.py freshness` and `python3 scripts/facts.py rate`. Note which price tier is in force on the intended post date; use no price if the tier ends before it. If the site repo is newer than the bundled facts (`python3 scripts/sync_site_facts.py check "<site repo>"`, which may itself fail when the site markup changed), do not name sessions or times that may have moved; use only stable facts (dates, city, capacity, the site's headline) and tell the user the facts need a sync.

**1. Lock the brief.** One idea. One goal (reach, sends, saves, follows, comments — it shapes the close). Length tier: 15–35 s is the reach sweet spot; let the idea pick the length, never pad. Ask only what you cannot decide: the topic if none given, the intended post date, and whether the user already has a handle, hashtags or link cleared (none are in the repo — see FACTS.md "Booking"; default to "Link in bio" and no hashtag until supplied).
- Language: the Reel is **English by default** (every session is in English and the site has no other language), *whatever language the user writes to you in*. A request typed in Portuguese is not a request for a Portuguese Reel; reply to the user in their language, write the script, spoken lines, captions and caption copy in English. Portuguese or Spanish copy only when the user explicitly asks for it for the Reel itself, marked "not client-approved".

**2. Audio direction.** Two layers: (a) the characters' spoken lines (generated natively by Kling 3.0 with the clip); (b) optional music — name the direction ("restrained, low piano, no beat drop"), a human adds the licensed track in-app. Write the muted version first: on-screen text and captions must carry the whole story.

**3. Hook (0–3 s), three channels at once:** spoken line + bold on-screen text + a striking first frame. No intro, no logo, no "hey everyone". The hook must be true to what follows — a bait-and-switch creates a retention cliff. Prefer a question the audience actually asks ("Where would your family live if the rules changed?") over a claim.

**4. Structure.** Front-load value, open a loop early, change the visual every 2–4 s, cut dead air, end so the last frame feeds the first (loop/rewatch trigger). Then answer in one line: *who sends this to whom, and why?* Relatable, useful-reference or conversation-starting beats travel; generic tips do not.

**5. Production doc.** Write `output/<slug>/script.md` using `references/script-template.md`. It must contain: header (Facts as of, Platform: Instagram Reel, length, goal, post date, tier used and until when), the one-line concept and the send question, the **cast** (which characters, why), the **beat table** (beat · seconds · shot · on-screen text · spoken · audio/sfx), the cover-frame brief, caption (target keyword in the first ~3 s spoken, on-screen text and first caption sentence; British English; 60–90 words; no emoji, no exclamation marks), 3–5 hashtags only if supplied (otherwise proposed and marked unconfirmed), alt text, and a **"Before publishing"** list: AI label toggle, trending-audio step, link, tier validity, "Programme subject to change" if sessions are named, disclosure sentence ("Characters are AI-generated.").
Keep hook text, faces and CTA inside the safe zone (top 14 %, bottom 35 %, sides 7.5 % are covered by Instagram's UI).

**6. Check, then ask.** Run `python3 scripts/qa_reel.py script output/<slug>/script.md`. Fix every error. Then show the user the beat table and caption and ask for approval **in words**, with the estimated cost from `simulate_cost` (see `references/kling-production.md` → Cost) and the number of clips. Offer a Trial Reel recommendation if the hook or format is unproven. Silence or "looks good, but…" is not approval; apply the change and ask again.

## Part B — Production (only after approval)

**7. Set up.** `bash scripts/setup.sh` checks `ffmpeg`/`ffprobe` and Pillow, and prints the python interpreter that has Pillow (run the reel scripts with that one: `brew install ffmpeg` can put a newer Homebrew `python3` first on PATH). If ffmpeg is missing, ask the user, then `bash scripts/setup.sh --install` (it runs `brew install ffmpeg`; on an older macOS it may compile dependencies from source and take a long time). Confirm credits with `account_balance`.

**8. Cast and frames.** Resolve the chosen characters with `library_list type=character` (ids in `references/cast.md`; re-verify, they are the user's library). For each clip, generate a 9:16 start frame with `images_generate` using the character as a reference, then check it (identity, hands, no text, no logos, navy-dominant Lisbon-nocturne grade). Kling 3.0 character references *require* a start frame.

**9. Clips.** One `video_generate` per clip with `slug: "kling-30"`, 9:16, 1080p, `withSoundEffects: true`, the start frame, the character as a `references` entry, spoken lines in quotes after the speaker, and `multi_prompt` for the beats of that clip (≤15 s, ≤6 shots). Follow the prompt recipe and the failure modes in `references/kling-production.md`. `creations_wait`, inspect with `video_analyze` (identity drift, garbled text, hands, mouth sync), regenerate only the failing clip.

**10. Assemble.** `video_concatenate` the approved clips in order, download the MP4 (`creations_get` → `url`; call `creations_register_download` first) into `output/<slug>/raw.mp4`.

**11. Captions (mandatory).** Word timings from `audio_timing_get` are often unavailable ("No persisted alignment"). Then let `captions.py` estimate from the beat windows and tell it when the speech really starts and ends (`--speech START END`, seconds; read them from a few extracted frames or one listen): without that, captions can appear a half-second before the voice. Then:
`python3 scripts/captions.py build output/<slug>/script.md --out output/<slug>/reel.srt [--timings timings.json | --speech START END]`
`python3 scripts/captions.py burn output/<slug>/raw.mp4 output/<slug>/reel.srt output/<slug>/reel.mp4`
Captions are rendered as PNGs (Pillow) and overlaid with ffmpeg, so no libass/drawtext build is needed. They are phrase-level, Archivo, inside the safe zone, one gold keyword at most (`references/captions-style.md`). Hook text and CTA overlays come from the script's on-screen text column through the same tool.

**12. QA and look.** `python3 scripts/qa_reel.py video output/<slug>/reel.mp4 --script output/<slug>/script.md` (1080×1920, audio present, duration vs. script, caption boxes inside the safe zone). Add `--frames <dir>` to extract frames, then look at 4–5 of them (including the cover frame) and look at them yourself before claiming it is done; fix caption timing by hand-editing the SRT if a line is early or late.

**13. Deliver** in `output/<slug>/`: `reel.mp4` (final, captioned), `reel.srt`, `script.md`, `caption.md` (caption · hashtags · alt text · Before publishing), `cover.png`. Tell the user: credits spent, which tier the copy assumes and until when, that the AI label and any trending audio are added by hand in the Instagram app, and anything left unverified.

## When something is off

- Thin concept → shape the one idea; do not pad to a length tier.
- "Make it a polished brand ad" → authentic, person-led content out-travels glossy spots; deliver the native version that still hits the goal (a paid creative is `wm-paid-ads`).
- "Guarantee this goes viral" → no guarantees; a strong hook plus a send-worthy idea stacks the odds, a Trial Reel tests it at no cost to follower stats.
- Character asked to say a client story → decline the testimonial framing; offer the question-led version.
- Generation fails twice on the same beat → simplify the shot (one subject, locked camera), or cut the beat to on-screen text over a Lisbon-nocturne still.
