# Production recipe — Magnific + Kling 3.0

Facts below were read from the Magnific MCP catalog on 21 Oct 2026. Models change: re-run `video_models_list search=kling` when something is rejected, and trust its limits over this file.

## Contents
1. Model choice
2. Cost and credits
3. Start frames
4. Clip prompt recipe
5. Dialogue and voice
6. Checking a clip
7. Failure modes
8. Assembly and download
9. Fallbacks

## 1. Model choice

| Need | Use | Why |
|---|---|---|
| Default | `kling-30` | up to 15 s, `multi_prompt` ≤ 6 shots, native sound (`withSoundEffects`), ≤ 3 `character` references, 9:16, 720p / 1080p / 4K |
| Reference video or element mix | `kling-omni3` | like 3.0 plus a video reference (3–10 s) |
| Voice control (≤ 2 voices) | `kling-26` | 5 or 10 s, 1080p only, no character references |
| Cheap silent b-roll / cutaway | `kling-30-turbo` | no sound, no references; only for non-character shots |

`kling-30` constraints that matter: **character references require a start frame**; `negativePrompt` cannot be combined with `multi_prompt`; prompt ≤ 2500 characters; duration 3–15 s.

## 2. Cost and credits

Before any paid call: `account_balance`. Then `simulate_cost` with `tool: "video_generate"` and the exact arguments of the first clip, and `tool: "images_generate"` for the start frame. Multiply by the number of clips plus one regeneration per clip as a planning margin. Put the total next to the script at the approval gate. Never start generation without the user seeing it. 1080p is enough for Reels; use 4K only if asked.

## 3. Start frames

For each clip, one 9:16 image per clip:

```
images_generate
  prompt: "@GCS-PPC-Daniel-2026 seated at a desk by a window at blue hour, Lisbon nocturne, deep navy
           ambient light with one warm amber lamp, relaxed attentive expression, hands resting on the
           desk, nothing on the desk. No text, no logos, no documents, no signage."
  aspectRatio: "9:16"
  references: [{"type": "character", "identifier": "2283000"}]
  count: 2
```

Pick the better of two. Reject frames with: different face from the reference, text or logos, documents/passports, a place presented as a real landmark, plastic skin, extra fingers. Navy-dominant grade with a single amber warm note keeps it on the "Lisbon Nocturne" look from `DESIGN.md`. Keep the top 14 % and bottom 35 % free of important content (faces sit in the middle band).

## 4. Clip prompt recipe

One `video_generate` per clip (≤ 15 s). Use `multi_prompt` for the beats inside that clip; each shot gets its own `duration` summing to the clip length (shot 1 = the hook, ≤ 3 s).

```
video_generate
  slug: "kling-30"
  aspectRatio: "9:16"
  resolution: "1080p"
  duration: 12
  withSoundEffects: true
  keyframes: {"start": {"type": "image", "url": "<start frame creation identifier>"}}
  references: [{"type": "character", "custom_model_id": "2283000", "name": "GCS-PPC-Daniel-2026"}]
  multi_prompt: [
    {"index": 1, "duration": 3, "prompt": "Close, eye-level. Daniel looks to camera and says: \"Where would your family live if the rules changed?\" Quiet room, blue-hour light, one warm lamp. Locked camera, slight push-in."},
    {"index": 2, "duration": 4, "prompt": "Medium shot, same room. Daniel says: \"Residency, citizenship and a Plan B are one wealth decision, not three.\" Calm gesture with one hand."},
    {"index": 3, "duration": 5, "prompt": "Wider, over his shoulder to the window and the lit river beyond. Daniel says: \"Two days in Lisbon, one room.\" Ends on a still, held look."}
  ]
```

Guidelines that follow from how Kling behaves:
- **Direct, don't decorate.** Subject, action, camera, light. Camera: locked or one slow move; fast moves break identity.
- **One speaker per shot.** Quote each line right after the speaker's name. Keep a line ≤ ~12 words per 3 s so mouth movement stays believable.
- **State what must not appear** in the shot text itself ("empty desk, no documents, no screen") — `negativePrompt` is unavailable with `multi_prompt`.
- **Never ask Kling to render text.** No titles, captions, logos, signage.
- Keep the scene continuous across clips (same room, same wardrobe) so the cut is invisible; reuse the same start-frame style and the same character reference.
- Lines must come from the approved script, verbatim. Spoken facts come only from `FACTS.md`.

## 5. Dialogue and voice

Kling 3.0 generates speech natively with the clip when `withSoundEffects: true` and the lines are quoted. Voice is not controlled across clips: the same character may sound slightly different in clip 2. Mitigations, in order: keep the Reel to one clip if the idea fits in ≤ 15 s; start clip 2 with a visibly different framing so the join reads as an edit; if the voice drifts audibly, re-roll clip 2 with the same prompt, or use `video_speak` (lip-sync with an exact voice, see `video_speak_models_list`) on all clips to hold one voice. Tell the user which route was used.

Background music is not requested here; if Kling adds a bed you do not want, pass `noMusic: true`. The human adds a licensed track in the Instagram app.

## 6. Checking a clip

`creations_wait` (≤ 8 identifiers, long-polls up to 55 s; a 5 s clip took ~2 min in testing, Magnific quotes up to 10). Then `video_analyze` with a concrete question, for example: "Does the same person appear throughout? Do the lips move in time with the speech, and from what second to what second? Is there any visible text, logo, document or screen? Describe the hands. Any visual glitches?" It is good for speech timing and sync but **it can invent things**: in testing it reported on-screen subtitles that were not in the video. Never trust it on text or logos; pull frames with `video_extract_frames` (timestamps like `"1.5"`, `"last"`; the result URLs download with `curl -L`) and look at them. Regenerate only the clip that fails.

## 7. Failure modes

| Symptom | Fix |
|---|---|
| Face drifts from the library character | Stronger start frame; one character per clip; fewer camera moves; re-roll |
| Garbled signage/text appears | Add "no signage, no text" to the shot text; reframe away from walls and screens |
| Hands odd | Hands resting and still; or crop below the hands |
| Mouth out of sync | Shorter lines (≤ 12 words / 3 s); one speaker per shot; re-roll or `video_speak` |
| Lines changed or dropped | Re-roll; lines are in quotes with the speaker name directly before them |
| Voice differs between clips | Section 5 |
| Scene looks like a real landmark | Reframe to a generic interior or dusk street; never caption it as a place |
| Plastic or over-glossy look | Natural skin texture, restrained light; use the character's reference |

## 8. Assembly and download

`video_concatenate` takes 2–10 completed identifiers in playback order and keeps each clip's audio. For one clip, skip it. To save locally: `creations_register_download` with the identifier, then `creations_get` and `curl -L -o output/<slug>/raw.mp4 "<url>"` (use the full-res `url`, not `previewUrl`). Always `ffprobe` the file afterwards (`qa_reel.py video`).

## 9. Fallbacks

- Kling unavailable or beat keeps failing → cut the beat to on-screen text over a Lisbon-nocturne still (generated without people) and keep the voice line as a caption.
- Audio missing on a clip → regenerate with `withSoundEffects: true`; a Reel with no audio fails an eligibility gate.
- `ffmpeg` cannot be installed (or its overlay filter is missing) → deliver `raw.mp4` + `reel.srt` and say plainly that captions are **not** burned in; the brief required burned captions, so this counts as incomplete.
