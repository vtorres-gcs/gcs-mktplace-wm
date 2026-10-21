# Content playbook — what to post, from what facts, in what order

Read `FACTS.md` first: every post below is built only from it. Slide vocabulary is in `slide-library.md`; the layout itself is your call from `DESIGN.md`. A post that needs a fact not in `FACTS.md` or the user's message does not get made — ask, or drop the line.

## The argument the Summit makes

From `PRODUCT.md` and the site: residency and citizenship planning is part of a broader wealth strategy, not an isolated legal decision — and the specialisms a cross-border decision normally needs *one at a time* are in one room over two days. The site's own hook is **Plan B**: "Your residency, your citizenship, your Plan B. Don't let the world decide for you." The programme proves it, so the programme is the content. A post that can name a session or a workshop does so instead of using an adjective.

## Post types

Each recipe lists the facts it may use and the arc (grounds alternate white and navy, the programme stays dark, the closing is the opposite of the slide before it).

| Post | Facts allowed | Arc (Nocturne types) | Caption must carry |
|---|---|---|---|
| **Announcement / save the date** | dates, city, venue, "Limited to 200", two days, the lede | cover → statement → ledger (`5–6 Nov` · `2 days` · `200` · `28 speakers`) → register | the CTA + link; the tier in force *only if* it will still be true when published |
| **Day preview** (one per day) | day theme, timed rows from `programme.json`, workshops | cover → programme ×2 (main stage; workshops) → register | "Programme subject to change" |
| **Session spotlight** | one timed row, its day, the theme it sits in | cover (the session title is the headline) → statement (why it matters — only what the title itself says) → register | time + day; no speaker unless user-confirmed pairing |
| **Workshop series** (one post per country) | the timed workshop list: Italy, Spain, Portugal (IFICI; real estate), Greece, Caribbean, Panama, Malta, US taxes, Beyond Sanctions | single post / story: workshop title as headline, day + time as the datum | note these are parallel, in the breakout room; Turkey only if the user confirms it |
| **Speaker spotlight** | name, role, portrait from `facts.py`; ≤ 40 words of bio, whole sentences | cover → speaker ×N (one per card) → register | the day theme only — not a session |
| **Who's in the room** | the four audience entries; "Limited to 200" | cover → entries → register | |
| **What's included** | the three included items, verbatim | statement / entries → register | the tier in force, if any |
| **Plan B** (positioning) | the site's headline and about-copy, verbatim (Mode B) | cover → statement ×2 → register | |
| **Lisbon / the setting** | the setting copy, venue name, "networking lunches", "rooftop cocktail evening" | plate-split → statement → register | no claim a generated image cannot prove |
| **Countdown** | `facts.days_to_go()` computed on the post date | statement (Display figure + "Days to go") | a countdown is a fact, not pressure |
| **Rate change** | the tier table, the date it changes | ledger (tier · price · window) → register | the deadline as a date; never "last chance" |
| **Partner call** | the partner copy, "A limited number of partnership and sponsorship opportunities" | cover → statement → register (partner variant) | route confirmed by the user; no logos, no tiers |

**Series logic.** For a run of posts in the weeks before the event (today: 20 Oct, 16 days to go): Plan B → Who's in the room → a day preview per day → a workshop post per country → speaker spotlights (roster order) → countdown posts in the last week → rate-change post on the last day of a tier. Offer the sequence; don't generate it unasked.

## Copy

- **Hooks that work from the site's own language:** the Plan B line; "the right decisions need the right people in the room"; "one specialist at a time"; the programme row itself. Questions only when the site asks the question ("Are You Really Ready for a 100-Year Life?").
- **Headline ≤ 12 words**, sentence case, no exclamation marks, no emoji, no superlatives. Say what happens, not how special it is.
- **CTA:** "Secure your place". Not "Register your interest"; not "Book now".
- **Scarcity:** "Limited to 200 attendees." Said once, flat.
- **No promises about outcomes** ("you will leave with a clear, practical plan" is the site's sentence — quote it, don't strengthen it).
- Residency/citizenship wording: "citizenship programme", "residency programme"; never "passport programme", "relocation firm", "borderless living", "dream lifestyle".

## The caption file — every job ships one

Write `<slug>_caption.md` next to the renders. It is what makes the post publishable; the PNGs alone are not.

```
# <slug> — caption and alt text
Platform: <Instagram | LinkedIn | X | Facebook>   Format: <carousel 4:5 | …>
Facts as of: <date> (site commit <hash>) · Rate used: <tier, price, valid until> | none
Source of each fact: <FACTS.md section / user message>

## Caption
<British English; no emoji; no exclamation marks; 60–120 words on LinkedIn, ≤ 90 on Instagram>

<one CTA line>  <link only if the user has confirmed it — otherwise "Link in bio">

Programme subject to change.   <only if sessions are named>

## Alt text
Slide 1 — <what is visible and what the text says, ≤ 125 characters>
Slide 2 — …

## Before publishing
- <anything the user must confirm: URL, venue spelling, a speaker↔session pairing, the rate window>
```

- **Alt text is mandatory** — the audience skews older and international, and an image post without it is unreadable to a screen reader. Describe the slide as a reader would hear it; include the date, the headline and the number that carries the slide.
- **No hashtags unless the user supplies them.** No hashtag set is part of the approved evidence. If asked for suggestions, give at most three built from the event's own name, flagged as suggestions.
- **Tagging people:** a speaker may be tagged only if the user supplies the handle. Never guess a handle.
- **Link placement:** Instagram captions don't link — "Link in bio". LinkedIn: put the link in the caption body only once confirmed.

## Timing facts to flag at hand-off

`python3 scripts/facts.py freshness` prints them. Always say in the hand-off: which rate tier is in the creative and when it stops being true; the number of days if a countdown is on it ("true on <date> only"); that the venue is spelled as the hero spells it and the site also uses *Marquês*.
