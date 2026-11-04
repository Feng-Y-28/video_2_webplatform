# Pipeline detail

```
paper/idea ─▶ 1 distill ─A─▶ 2 reference ─▶ 3 script ─B─▶ 4 production ─C─▶ 5 score ─M─▶ 6 review ─D─▶ [sample: user] ─▶ 7 publish
                  ▲                             ▲              ▲              ▲              │                │
                  └── each gate: max_retries + 1 automatic rounds, one fix + --verify round, then stop ┘   revise ─┘
```

A–D: fresh-subagent critiques (v2w-critique). M: machine checks plus a manual
`score.js` read (the measurement cannot hear a loop).
The only human step is the sample review.

**Gate order is fixed:** A → B → C → music → review → D → sample → published.
A gate ticked while an earlier one is open is `ILLEGAL`.

**Retry budget:** `max_retries` counts automatic retries after the first round,
so `max_retries + 1` automatic rounds in total; then exactly one manual-fix
round plus its `--verify` verification round. Tick the gate only on PASS.

**Writers:** v2w-production writes `renders/final.mp4`; only v2w-score writes
`renders/share.mp4`; `exports/` is written by publish only; `publish.md` is
drafted by review before critique D (stage 6) and updated by publish (stage 7).
Run `scripts/check_env.py` before the first production export.

## Why this order

- **Distill before reference.** You need to know what the mechanism *is*
  before judging how others explain it; otherwise the reference videos
  decide the content.
- **Reference before script.** Other creators' explanation order, analogies
  and common confusions (from comments) feed the script, not only the visuals.
- **Critiques replace check-ins.** Each place where a human used to approve
  (brief, look, storyboard) is now a rubric critique. The user's one review
  then deals with taste, not basic mistakes.
- **Revise notes route back.** Map each note from the sample review to the
  earliest stage it touches (content → 1, order → 3, picture → 4, sound → 5),
  redo from there, and re-run every gate after it.

## Time budget (one 45 s piece, first time through)

| Stage | Typical loops | Main cost |
|---|---|---|
| distill | 1–2 | reading the paper; sourcing numbers |
| reference | 1 | finding 3–5 good same-topic videos |
| script | 1–3 | conflict + order |
| production | look 1–2, board 1–2, build 3–6 | dead beats, labels out of frame |
| score | 2–4 takes | picking by measured shape, not by ear |
| review | 2–4 | each loop re-exports |
| publish | 1 | platform rules, cover frame |

## Shortcuts

- **Make 10 seconds first**: build and review only the hook + first beat
  before the full export.
- **Music first**: if the input comes with a track, run animate's
  `beats.mjs` on it and cut to its shape (v2w-score → Track-first).
- **No good references found**: record that in `refcard.md` and continue;
  critique B then relies on the base rubric only.
- **Translated version**: optional, at publish time — `v2w-publish/references/localize.md`.
