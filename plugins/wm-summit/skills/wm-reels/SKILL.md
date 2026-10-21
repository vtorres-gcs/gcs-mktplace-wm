---
name: wm-reels
description: "Writes the shootable script for an Instagram Reel for the Wealth and Migration Summit 2026 (Lisbon, 5–6 November 2026, curated by Global Citizen Solutions): hook, beat table, on-screen text, spoken lines, cover brief, caption, hashtags, alt text and a before-publishing checklist, checked against the Summit's confirmed facts. Delivers the script only — it does not generate or edit video. Use whenever the user mentions a Reel, Reels, Instagram video, a short vertical video, a video script, a hook, 'roteiro de reel', 'vídeo para o Instagram', or wants any moving-image social content planned for this event, even if they never say 'reel'. Not for static posts, carousels or Stories (use wm-social-media), paid-ad creatives (use wm-paid-ads), web banners, decks, or general GCS content."
allowed-tools: Bash(*), Read, Write, Edit, AskUserQuestion
metadata:
  last_updated: "2026-10-21"
  updated_by: claude-skill-creator
  change_note: "Script only: video production (Magnific / Kling, characters, burned captions) removed. Facts synced with site repo at 6725cff (copied from wm-social-media)."
---

# wm-reels — Reel scripts for the Wealth and Migration Summit 2026

One job: **write the script** for an Instagram Reel, checked against the Summit's facts, ready for someone to shoot or edit. The skill does not generate or edit video, add captions to footage or pick a track.

Why Reels are different from the Summit's static posts: reach comes mostly from non-followers, decided by how viewers respond in the first seconds, by watch-through and by sends (DM shares) — not by follower count. So the script is built for a 3-second hook, for sound-off viewing, and for "who would send this to whom". Read `references/reels-playbook.md` before writing.

## Source of truth

| For | Read |
|---|---|
| Dates, prices, programme, speakers, capacity, CTA wording, what must never be invented | `references/FACTS.md` and `references/data/` (through `scripts/facts.py`) — overrides everything else |
| Voice, audience, positioning | `references/PRODUCT.md` (its fact sections are stale; FACTS.md wins) |
| Palette, type, on-screen text look | `references/DESIGN.md` |
| Instagram mechanics, hook, retention, safe zone | `references/reels-playbook.md` |
| Script structure | `references/script-template.md` |

## What this skill will not do

- Generate, edit or caption video, or call any video/image generation tool. If asked, say the skill delivers the script and that production happens elsewhere.
- Present a person as a **speaker, delegate, client, attendee or testimonial** unless they are on the speaker roster and the line is theirs to say. No invented people, no personal results ("I got my residency…").
- Promise visas, citizenship, tax outcomes or returns; use urgency mechanics ("last chance", "book now"); name anyone not on the speaker roster.
- Show or call for a passport/ID/document, a partner logo or the real venue as a prop in a shot unless the user has cleared that asset.
- Add trending audio. Instagram's licensed library is native-only: the script names the audio direction and a human adds the track in the app.
- Re-post a watermarked TikTok/CapCut export (originality gate) — re-cut a clean version instead.

## Workflow

**0. Freshness.** `python3 scripts/facts.py freshness` and `python3 scripts/facts.py rate`. Note which price tier is in force on the intended post date; use no price if the tier ends before it. If the site repo is newer than the bundled facts (`python3 scripts/sync_site_facts.py check "<site repo>"`, which may itself fail when the site markup changed), do not name sessions or times that may have moved; use only stable facts (dates, city, capacity, the site's headline) and tell the user the facts need a sync.

**1. Lock the brief.** One idea. One goal (reach, sends, saves, follows, comments — it shapes the close). Length tier: 15–35 s is the reach sweet spot; let the idea pick the length, never pad. Ask only what you cannot decide: the topic if none given, the intended post date, who delivers it on camera (a team member, a speaker who agreed, voiceover, or text only), and whether the user already has a handle, hashtags or link cleared (none are in the repo — see FACTS.md "Booking"; default to "Link in bio" and no hashtag until supplied).
- Language: the Reel is **English by default** (every session is in English and the site has no other language), *whatever language the user writes to you in*. A request typed in Portuguese is not a request for a Portuguese Reel; reply to the user in their language, write the script, spoken lines, on-screen text and caption copy in English. Portuguese or Spanish copy only when the user explicitly asks for it for the Reel itself, marked "not client-approved".

**2. Audio direction.** Two layers: (a) the spoken lines; (b) optional music — name the direction ("restrained, low piano, no beat drop"), a human adds the licensed track in-app. Write the muted version first: on-screen text must carry the whole story.

**3. Hook (0–3 s), three channels at once:** spoken line + bold on-screen text + a striking first frame. No intro, no logo, no "hey everyone". The hook must be true to what follows — a bait-and-switch creates a retention cliff. Prefer a question the audience actually asks ("Where would your family live if the rules changed?") over a claim.

**4. Structure.** Front-load value, open a loop early, change the visual every 2–4 s, cut dead air, end so the last frame feeds the first (loop/rewatch trigger). Then answer in one line: *who sends this to whom, and why?* Relatable, useful-reference or conversation-starting beats travel; generic tips do not.

**5. Write the script.** Save `output/<slug>/script.md` using `references/script-template.md`. It must contain: header (Facts as of, Platform: Instagram Reel, length, goal, post date, rate in force and until when, presenter), the one-line concept, keyword and the send question, the **beat table** (beat · seconds · shot · on-screen text · spoken · audio/sfx), the cover-frame brief, caption (target keyword in the first ~3 s spoken, on-screen text and first caption sentence; British English; 60–90 words; no emoji, no exclamation marks), 3–5 hashtags only if supplied (otherwise proposed and marked unconfirmed), alt text, and a **"Before publishing"** list: trending-audio step, link, tier validity, "Programme subject to change" if sessions are named, and a Trial Reel recommendation if the hook or format is unproven.
Keep hook text, faces and CTA inside the safe zone (top 14 %, bottom 35 %, sides 7.5 % are covered by Instagram's UI).

**6. Check, then deliver.** Run `python3 scripts/qa_reel.py script output/<slug>/script.md`. Fix every error; read the warnings and either fix them or say why they stay. Then show the user the beat table and caption, say which price tier the copy assumes and until when, and list anything left unverified (handle, hashtags, link, session times). Apply requested changes and re-run the check.

## When something is off

- Thin concept → shape the one idea; do not pad to a length tier.
- "Make it a polished brand ad" → authentic, person-led content out-travels glossy spots; deliver the native version that still hits the goal (a paid creative is `wm-paid-ads`).
- "Guarantee this goes viral" → no guarantees; a strong hook plus a send-worthy idea stacks the odds, a Trial Reel tests it at no cost to follower stats.
- Someone asked to tell a client story or a result → decline the testimonial framing; offer the question-led version.
- "Now make the video" → out of scope for this skill; hand over the script as the production brief.
