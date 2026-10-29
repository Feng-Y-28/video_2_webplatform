---
name: v2w-reference
description: Stage 2 of the v2w pipeline. Before scripting, study how other creators already explain the same topic — find 3–5 strong same-topic short videos, pull their transcripts and key frames, and distil their explanation order, analogies, visual devices, pacing and the confusions viewers raise in comments into refs/refcard.md. TRIGGER when the v2w-orchestra reaches stage 2, or the user asks to "look at how others explain X", "find reference videos", "what do popular videos on this topic do".
---

# v2w-reference

Output: `<piece>/refs/refcard.md`. No gate of its own; it feeds v2w-script
and critiques B and C.

## Steps

1. **Search** — only if `v2w.config.json` → `allow_browse_references` is true.
   Use the browser (e.g. **claude-in-chrome**) on the platforms in the config.
   Query the *mechanism* and the *problem*, not the paper title. Prefer
   recent videos, high engagement relative to the account's size, and the
   same audience level. If browsing is not allowed, write "no references
   (browsing disabled)" and continue.
2. **Pick 3–5.** Note per video: platform, title, length, engagement, URL.
   Skip anything without a clear explanation (memes, reposts).
3. **Transcript.** If a transcript skill is installed (yt-dlp + whisper style),
   use it into `refs/transcripts/<id>.md`; otherwise read the platform's
   captions. Grab 6–10 key frames into `refs/frames/<id>/` (git-ignored).
4. **Break each video down** (one table per video in refcard.md):
   - order of ideas, with timestamps;
   - the hook (first 3 s) and where the payoff lands;
   - analogies and visual devices (what object stands for what);
   - what it gets wrong or skips;
   - top comments: confusions and questions viewers still have.
5. **Synthesise** at the top of refcard.md:
   - the explanation order most of them use, and one order none of them use;
   - analogies worth borrowing as *mechanisms*, not copied wording or footage;
   - the confusion our video should settle (often the best payoff);
   - **topic-specific checks** for critiques B and C (e.g. "every video draws X
     wrong; ours must not"). Critiques score these under B7 / C7.

## Rules

- Learn the shared mechanics: structure, pacing, visual devices. Do not
  reuse another creator's private material: their footage, script lines,
  persona or exact examples.
- Cite reference videos only in `refcard.md`. Never in the video or the post.
- If nothing good exists, write that down. It is useful to know, and it may be the
  reason to make this video.
