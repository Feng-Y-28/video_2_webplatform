# I/O contract

Files marked *(animate)* follow the [animate](https://github.com/cth9191/animate)
skill's own format — v2w wraps it and does not redefine it.

## Project level

| Path | Written by | Notes |
|---|---|---|
| `v2w.config.json` | init_project | standing consent + platforms; see below |
| `.gitignore` | init_project | media, renders, review images, reference frames, `third_party/`, `.env` |
| `.claude/skills/v2w-*` | init_project / setup.sh | symlinks into this repo |
| `develop_log/` | you (a debug-log skill) | private raw notes |
| `pieces/` | new_piece | one folder per video |
| `exports/` | score / publish | delivered MP4s, human-readable names |
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
| `critique/<gate>-r<n>.json` | A–D | one file per critique round (schema in v2w-critique) |
| `piece.json`, `src/`, `index.html` | 4 *(animate)* | |
| `audio/`, `mix.sh` | 5 | raw takes, automated track; mix only for external tracks |
| `renders/` | 4–5 *(animate)* | `final.mp4`, `share.mp4`, `audio.wav`, stems |
| `review/` | 4–6 | look / board (kept), contact sheets (regenerated) |
| `LOG.md` | all | dated decisions; per-shot PASS table after each review |
| `publish.md` | 7 | per-platform copy and status |

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

## Project config (`v2w.config.json`)

```json
{
  "allow_browse_references": true,
  "allow_hosted_music_api": false,
  "publish_after_approval": "fill_form",
  "platforms": ["xiaohongshu"],
  "max_retries": 2
}
```

`publish_after_approval`: `"none"` (write publish.md only), `"fill_form"`
(upload and fill, stop before the final button), `"publish"` (also click
publish once the sample is approved).
