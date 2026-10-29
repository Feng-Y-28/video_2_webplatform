# Dependencies

v2w composes other open-source skills and tools; it does not vendor them.
Only **animate**, ffmpeg and Python are required. The others have a fallback
that each stage describes (and logs when used).

| Dependency | Stage | Without it | Install |
|---|---|---|---|
| [animate](https://github.com/cth9191/animate) skill | production, score, review | — (required) | clone it, then make `<skills>/animate/` point at the folder holding its `SKILL.md` (in that repo: `plugins/animate/skills/animate/`) |
| Node 18+, Playwright + Chromium | animate | — (required) | `npm i -g playwright && npx playwright install chromium` |
| ffmpeg **with drawtext** | review, score | — (required) | macOS: `brew install ffmpeg-full` (keg-only; see `skills/shared/pitfalls.md`) |
| Python 3.9+ | v2w scripts | — (required) | standard library only |
| [nature-reader](https://github.com/Yuan1z0825/nature-skills) skill | distill | read the PDF directly | from the nature-skills pack |
| [deep-research](https://github.com/Imbad0202/academic-research-skills) skill | distill (fact-check mode) | open each primary source yourself | from academic-research-skills |
| Browser automation (e.g. Claude in Chrome) | reference, publish | no references; publish.md only | Claude in Chrome extension |
| A transcript skill (yt-dlp + whisper style) | reference | read platform captions | any; `yt-dlp` + `faster-whisper` |
| [anatomy](https://github.com/wheresryan22/anatomy) skill | production (companion figure) | skip | clone into your skills dir |
| [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | score (ACE-Step client) | synthesized score | clone into `<project>/third_party/`; see `skills/v2w-score/references/ace-step.md` |
| A subagent-capable host (e.g. Claude Code) | critique | run the critique in a new session with only the listed files | — |

`new_piece.py` looks for animate at `~/.claude/skills/animate`; override with
`ANIMATE_DIR=…` or `--animate-dir`.
