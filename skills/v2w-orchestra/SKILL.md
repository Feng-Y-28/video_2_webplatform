---
name: v2w-orchestra
description: Orchestrate the video_2_webplatform pipeline end to end, autonomously. Input is a paper (PDF / arXiv / DOI) or a one-paragraph idea; output is a ~30–60 s vertical explainer video plus platform-ready post copy. Sets up directories, then runs seven stages — distill, reference, script, production, score, review, publish — gated by fresh-subagent critiques against fixed rubrics and by machine checks. The only human step is approving the final sample. TRIGGER when the user wants to "turn this paper / idea into a short video", "make a short video explaining X", "start a new v2w project / piece", or asks what the next step of an in-progress piece is.
---

# v2w-orchestra (Orchestrator)

Top-level driver. Read this file, then load each stage's `SKILL.md` when you
reach that stage. Paths are relative to this skill's directory unless they
start with `<project>/` or `<piece>/`.

**Input:** a paper (PDF, arXiv id, DOI, URL) or an idea in a few sentences.
**Output:** `<piece>/renders/share.mp4` and `<piece>/publish.md`.

## Autonomy model

The pipeline runs **without asking the user** from input to sample. Quality
is held by:
- **critiques A–D** (v2w-critique): a fresh subagent scores the artefact
  against a fixed rubric, sees nothing of your reasoning;
- **machine checks**: animate review, `band_energy.py`, `validate_piece.py`.

A failed gate is fixed and re-checked automatically, at most **2 retries** per
gate. If it still fails, stop and present the sample with the open issues. Do
not loop forever, and do not lower the bar.

**The one human step: the sample review.** The user watches
`renders/share.mp4` with `publish.md`, and answers *approve* (then publish
proceeds as configured) or *revise* with notes (go back to the earliest stage the
notes touch).

**Standing consent** comes from `<project>/v2w.config.json` (written by
`init_project.py`): whether you may browse for references, call hosted music
APIs, and upload after approval. If a key is `false` or missing, skip that
action and use the fallback. Do not stop to ask.

## Pipeline

```
paper / idea
  │
1 distill     v2w-distill     → principle.md                  ⟶ critique A (content)
2 reference   v2w-reference   → refs/refcard.md
3 script      v2w-script      → brief.md                      ⟶ critique B (script)
4 production  v2w-production  → look, board, src/, final.mp4  ⟶ critique C (visual, on look + board)
5 score       v2w-score       → audio/, share.mp4             ⟶ music checks (machine)
6 review      v2w-review      → machine checks, LOG.md        ⟶ critique D (final)
  ── sample review (user) ── approve / revise
7 publish     v2w-publish     → publish.md, upload per config
```

## Setup

- New project: `python3 scripts/init_project.py <project>` (idempotent; local
  `git init`; writes `v2w.config.json` if missing).
- New piece: `python3 scripts/new_piece.py <project> <name>` →
  `STATUS.md`, `principle.md`, `refs/refcard.md`, `brief.md`, `LOG.md`, animate's `piece.json` + `src/`.
- Status: `python3 scripts/validate_piece.py <piece>` → open gates, next step.

Contracts: `references/io-contract.md`. Order and shortcuts:
`references/pipeline.md`. Skills this pipeline calls: `../../docs/dependencies.md`.

## Rules that hold in every stage

1. **Gates live in `<piece>/STATUS.md`.** Tick a critique gate only when
   `v2w-critique/scripts/critique_gate.py` prints PASS; tick a machine gate
   only on the tool's PASS; tick `sample approved` only on the user's word.
2. **You cannot hear.** Music is judged by measurements, never by "it sounds good".
   The user's sample review is the only listening.
3. **Every number on screen has a source** (`../shared/claims-and-sources.md`).
4. **Use the specialist skill when it is installed** (paper reading, fact
   checking, transcripts, animation, browser); fall back as each stage says,
   and record the fallback in `LOG.md`.
5. **Log every automatic decision** in `LOG.md` (take chosen, critique fixes,
   retries). This record is what the user reads instead of being asked.
6. Read `../shared/pitfalls.md` before the first export on a new machine.
