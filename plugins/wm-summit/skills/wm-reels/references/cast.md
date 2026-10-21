# Cast — the five GCS-PPC characters

The user's Magnific library holds five reusable, fictional, AI-generated characters (library type `character`, project "GCS"). They are **production labels, not real clients or testimonials**. Re-check with `library_list type=character` before use — ids and descriptions belong to the user and may change; if a character is missing, say so and ask instead of substituting.

| Name | Library id | Look (from the library description) | Natural role in a Summit Reel |
|---|---|---|---|
| GCS-PPC-Daniel-2026 | `2283000` | 46, light olive skin, short dark-brown hair greying at temples, clean-shaven, blue-grey eyes, broad jaw; charcoal-navy jacket, pale-blue open-collar shirt; relaxed three-quarter stance | Family decision-maker asking the practical question |
| GCS-PPC-Clara-2026 | `2282999` | 48, shoulder-length chestnut hair with honey highlights, hazel eyes; cream tailored jacket, ivory blouse, discreet gold earrings; seated | Private-client voice; Plan B, family and succession angles |
| GCS-PPC-Thomas-2026 | `2282998` | 53, salt-and-pepper swept-back hair, short grey beard, brown eyes; navy blazer, white open-collar shirt; seated, welcoming | Experienced global citizen; "decisions need the right people in the room" |
| GCS-PPC-Elena-2026 | `2282941` | adult woman, light olive skin, brown eyes, chin-length dark wavy bob with silver strands; sand linen blazer, navy blouse | Calm explainer; longevity / family-and-future themes |
| GCS-PPC-Adrian-2026 | `2282940` | adult man, medium-brown skin, short curly black hair greying at temples, clean-shaven, brown eyes; navy unstructured jacket, cream shirt | Younger-family or entrepreneur angle; mobility and cross-border planning |

The mapping is a starting point; pick by the idea, and use **one or two characters per Reel** (Kling accepts ≤ 3 character references and drifts more as the cast grows). Keep one character per clip when the clip has speech, so each voice stays distinct.

## Rules (the exception to `wm-social-media`'s no-generated-people rule, scoped)

`wm-social-media` bans generated people. The user chose to cast these five for Reels, so this skill allows **only these five library characters**, under these conditions:

1. **Never a real role.** Not a speaker, moderator, delegate, attendee, client, partner or journalist. Never labelled with a title ("investor", "client of GCS"), never given a company. Their names are not shown on screen or in the caption.
2. **No testimonials, no results.** Characters ask, explain or set up the idea. They do not say "I moved…", "we got our residency…", "it saved us tax…". Spoken lines are in the second person or general ("Where would your family live if…?") or are facts from `FACTS.md` presented as the Summit's own message.
3. **Not the venue, not the city as proof.** Settings are generic ("a quiet study", "a rooftop at dusk", "a Lisbon-nocturne street"). Never claim or imply a generated scene is EPIC SANA Marques or a real landmark; do not name a place the image cannot prove.
4. **Nothing legible in the footage.** No passports, IDs, documents, screens with text, signage, logos or partner marks inside generated frames. All text is added in post. Hands on a table or lap are fine; hands holding documents are not.
5. **Disclose.** The caption ends with "Characters are AI-generated." and the "Before publishing" list reminds the user to switch on Instagram's AI label (manual; the skill cannot set it).
6. **Fidelity.** Reference the library character; do not describe a different face. If a result drifts from the reference (different jaw, hair, age), regenerate the beat; do not ship a lookalike.
7. **Wardrobe and tone** stay as in the library: restrained, believable, naturally warm, never fashion-model posed, no exaggerated emotion.
8. **No lookalikes of real people.** Never prompt for a likeness of a speaker, public figure or named person.

## Prompt handles

In `images_generate` the character is a reference: `{"type": "character", "identifier": "<id>"}`, and the prompt may mention it as `@GCS-PPC-Daniel-2026`. In `video_generate` it is `{"type": "character", "custom_model_id": "<id>", "name": "<library name>"}`. Both are covered in `kling-production.md`.
