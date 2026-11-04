# I/O contract

Files marked *(animate)* follow the [animate](https://github.com/cth9191/animate)
skill's own format — v2w wraps it and does not redefine it.

## Project level

| Path | Written by | Notes |
|---|---|---|
| `v2w.config.json` | init_project | standing consent + platforms; see below |
| `.gitignore` | init_project | whitelist block: ignore everything, track only `develop_log/` and each piece's LOG / STATUS / principle / brief / refcard / critique JSON |
| `.claude/skills/v2w-*` | init_project / setup.sh | symlinks into this repo |
| `develop_log/` | you (a debug-log skill) | private raw notes |
| `pieces/` | new_piece | one folder per video |
| `exports/` | publish only | delivered MP4s, human-readable names (stage 7; never written by an earlier stage) |
| `third_party/` | user | cloned tools; not tracked |

## Piece level (`pieces/<name>/`)

| Path | Stage | Notes |
|---|---|---|
| `STATUS.md` | all | input, gates (checkboxes), critique log |
| `source/` | 1 | the paper PDF or idea text; reader output |
| `principle.md` | 1 | principle card — problem, mechanism, key numbers + sources, what to leave out |
| `refs/refcard.md` | 2 | per-video notes + synthesis: order, analogies, visuals, confusions |
| `refs/transcripts/`, `refs/frames/` | 2 | raw material from reference videos (frames git-ignored) |
| `brief.md` | 3 | spec, audience, hook, explanation order, beats, claims, sound plan |
| `critique/<gate>-r<n>.json` | A–D | one file per critique round; carries the schema/version marker below |
| `piece.json`, `src/`, `index.html` | 4 *(animate)* | |
| `audio/`, `mix.sh` | 5 | raw takes, automated track; mix only for external tracks |
| `renders/` | 4–5 *(animate)* | `final.mp4` (production), `share.mp4` (v2w-score only writer), `audio.wav`, stems |
| `review/` | 4–6 | look / board (kept), contact sheets (regenerated) |
| `LOG.md` | all | dated decisions; conflict/ruling record, critique log, per-shot PASS table after each review |
| `publish.md` | 6–7 | drafted by v2w-review before critique D (stage 6), updated by v2w-publish (stage 7) |

Only v2w-score writes renders/share.mp4; v2w-production writes
renders/final.mp4. exports/ is written by publish only. Run the Setup
preflight (scripts/check_env.py) before the first production export; it
reports Python, ffmpeg + drawtext, Node, Playwright and animate's tools.

## Gates (`STATUS.md`)

```
- [ ] A content critique passed
- [ ] B script critique passed
- [ ] C visual critique passed
- [ ] music checks passed
- [ ] review checks passed
- [ ] D final critique passed
- [ ] sample approved (user)
- [ ] published
```

Only `sample approved` is ticked by the user's word; every other gate is
ticked on a tool or critique PASS. `validate_piece.py` reads the lines by
label; keep the wording.

**Order is fixed:** A → B → C → music → review → D → sample → published.
A gate ticked while an earlier one is open is `ILLEGAL`; `validate_piece.py`
runs the artefact check of every ticked gate, even when all gates are closed.

**Retry budget:** `max_retries` counts automatic retries *after* the first
round — `max_retries + 1` automatic rounds in total. If those still fail, do
one manual fix and one verification round; tick the gate only on PASS, otherwise
carry the open issues into the sample review.

**User waivers:** `sample approved` may coexist with an open gate only when
`STATUS.md` → `User waivers` contains
`- <gate> accepted with open issues by user (YYYY-MM-DD): <one line>`.
`validate_piece.py` treats a matching waiver as a WARN; without it, an open
prerequisite or a failed D is an `ILLEGAL`/`FAIL`.

## Project config (`v2w.config.json`)

```json
{
  "allow_browse_references": true,
  "allow_hosted_music_api": false,
  "allow_campaign_topics": false,
  "publish_after_approval": "fill_form",
  "platforms": ["xiaohongshu"],
  "max_upload_mb": null,
  "max_retries": 2
}
```

`publish_after_approval`: `"none"` (write publish.md only), `"fill_form"`
(upload and fill, stop before the final button), `"publish"` (also click
publish once the sample is approved).
A missing `allow_campaign_topics` means `false`: do not select a platform
campaign or event topic. `max_upload_mb: null` means read the limit on the live
upload page; do not assert a fixed browser or platform cap in these docs.
`max_retries` counts automatic retries after the first critique round (so
`max_retries + 1` automatic rounds in total), followed by one manual fix and one
verification round.

## Critique JSON marker

Each critique file records the format so older piece folders can be told apart:

```json
{"schema": 2, "gate": "A", "round": 1, "items": [], "must_fix": [], "summary": ""}
```

`schema` (or `rubric_version` / `version`) is the marker; `2` is the current
format. A file without it is legacy: gates A–C
warn instead of failing, but D, sample approval and published still need their
own evidence. `validate_piece.py` asks `v2w-critique/scripts/critique_gate.py`
for the verdict and maps exit 0 to PASS, 1/2 to did-not-pass, 3 to invalid and
4 to stale.
