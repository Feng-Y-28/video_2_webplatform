---
name: v2w-production
description: Stage 4 of the v2w pipeline. Produce the video from an approved brief by driving the animate skill (procedural canvas video) and optionally the anatomy skill (isometric technical figures) — look frames, storyboard, build, export — with v2w's conventions for technical explainers. TRIGGER when the v2w-orchestra reaches stage 4, or the user asks to "animate / build / export piece X", "make the look frames", "make the storyboard" for a v2w piece.
---

# v2w-production

This stage is a thin layer over the **animate** skill. Load animate's own
`SKILL.md` and follow its story → look → storyboard → build → export loop,
**with one change: animate's user check-ins are replaced by critique C.**
animate's intake questions are already answered: take them from `brief.md` (spec,
beats, sound plan) and `v2w.config.json` (platforms → formats). This file adds
only what is specific to technical explainers and to the v2w layout.
Dependencies: `../../docs/dependencies.md`.

## Inputs / outputs

- In: `brief.md` (gate B passed), `refs/refcard.md` (devices worth borrowing).
- Out: `review/look.png`, `review/board.png`, `src/`, `index.html`,
  `renders/final.mp4`, `renders/share.mp4`.
- Gate: **C visual critique passed**, run on look + board *before* the full build.

## Order

1. Look frames (2–4 most different beats) → `review/look.png`.
2. Storyboard of every beat → `review/board.png`.
3. **v2w-critique gate C**; fix → re-run (≤ 2 retries). Only then build.
4. Build the first 10 s, tile it, fix; then build and export the whole piece.
5. Record the cut list, critique fixes and build errors in `LOG.md`.

## Environment

Before the first build in a shell, check animate's requirements (Node,
Playwright + Chromium, ffmpeg). See `../shared/pitfalls.md` for the
`NODE_PATH` and `ffmpeg-full` issues — both show up on a fresh macOS install.

## Conventions for technical explainers

1. **Story format.** For "mechanism" pieces use animate's **beat-cut**
   template: hard cuts on the 8th-note grid, one era per shot, no morphs.
   Morphs are better suited to a single object turning into another.
2. **Isometric style** suits hardware, dataflow and systems. One object per
   shot, labels in screen space.
3. **Split long peak shots.** A shot longer than ~4 s in the peak act will
   trip dead-beat checks and lose viewers. Split it into wide → mid →
   following close-up → wide, and add a second highlighted element.
4. **Screen-space labels do not ride world points while the camera moves.**
   Pin them, or hide them during the move.
5. **Every 2–3 s something new appears.** If nothing new can appear, emit
   a small result (a value popping out, a counter ticking).
6. Keep text out of the phone safe zones in `piece.json` → `review.safe`.
   Something leaving the frame on purpose goes in `review.textIgnore` with
   a reason.
7. Use one scene file per act (`src/scenes-a.js`, `src/scenes-b.js`, …) when
   the piece is long or several agents work on it.

## Anatomy (optional)

For an interactive companion figure (blog post, landing page) of the same
mechanism, use the **anatomy** skill on the same brief. Keep the colours and
labels consistent with the video so the two can be published together.

## Hand-off

Go to v2w-score (always: even a synthesized score needs the music checks).
