---
name: v2w-distill
description: Stage 1 of the v2w pipeline. Read a paper (PDF / arXiv / DOI / URL) or take a short idea and extract the one principle a short video can carry — the problem, the core mechanism, the 2–4 numbers that prove it (each with a source), and what to leave out — into principle.md, then send it to critique A. TRIGGER when the v2w-orchestra reaches stage 1, or the user asks to "break down / distill this paper for a video", "what's the core idea of this paper", "pick what to explain from X".
---

# v2w-distill

Output: `<piece>/principle.md` (template written by `new_piece.py`).
Gate: **A content critique passed**.

## Steps

1. **Get the source text.**
   - Paper: put the PDF (or the arXiv id / DOI) in `<piece>/source/`. If the
     **nature-reader** skill is installed, use it to build a figure-aware
     reader of the paper into `source/`; otherwise read the PDF directly and
     note page numbers as you go.
   - Idea: write the idea as the user stated it into `source/idea.md`, unchanged.
2. **Find the problem.** One sentence a non-specialist can follow: what was
   slow / wrong / expensive before. This becomes the video's conflict.
3. **Find the mechanism.** The *one* thing that resolves the problem, written
   as cause → effect in ≤ 3 steps. If the paper has several contributions,
   pick the one that is visual and that the main result depends on; list the rest
   under *Left out*.
4. **Pick the proof numbers.** 2–4 numbers that let a viewer *see* the
   mechanism work (before/after, needed/available, used/idle). Each gets a
   source: paper section/table/figure, or a primary external source. Prefer a
   clean simplified example over a paper's full configuration, and label it.
5. **Check facts** that come from outside the paper (hardware specs, prior
   results). If the **deep-research** skill is installed, run its fact-check
   mode on them; otherwise open each primary source yourself.
   Remove any number you cannot source.
6. **Audience and depth.** One line: who watches, what they already know.
   Default for technical topics: undergraduates outside the field.
7. **Left out.** List what is true but not needed for this conflict. A short
   video carries one idea.
8. Run **v2w-critique** with gate `A`. Fix and re-run (≤ 2 rounds), then
   tick `A content critique passed` in `STATUS.md`.

## Rules

- For an idea without a paper, the "mechanism" must still be checkable:
  find a source for every factual step or mark the step as an assumption.
- Do not let the paper's framing pick the hook. The hook comes from the
  problem as a viewer would feel it, not from the paper's title.
