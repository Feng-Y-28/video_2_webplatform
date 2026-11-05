# Dependencies

v2w composes other open-source skills and tools; it does not vendor them.

**Required set:** Python 3.9+, ffmpeg **with drawtext**, Node 18+ with
Playwright + Chromium, and the **animate** skill. Everything else has a
fallback that each stage describes (and logs when used).

| Dependency | Stage | Without it | Install |
|---|---|---|---|
| [animate](https://github.com/cth9191/animate) skill | production, score, review | — (required) | clone it, then make `<skills>/animate/` point at the folder holding its `SKILL.md` (in that repo: `plugins/animate/skills/animate/`) |
| Node 18+, Playwright + Chromium | animate | — (required) | `npm i -g playwright && npx playwright install chromium` |
| ffmpeg **with drawtext** | review, score | — (required) | macOS: `brew install ffmpeg-full` (keg-only; see `skills/shared/pitfalls.md`) |
| Python 3.9+ | v2w scripts | — (required) | standard library only |
| [nature-reader](https://github.com/Yuan1z0825/nature-skills) skill | distill | read the PDF directly | from the nature-skills pack |
| [deep-research](https://github.com/Imbad0202/academic-research-skills) skill | distill (fact-check mode) | open each primary source yourself | from academic-research-skills |
| Codex search, connected plugins or browser automation | reference, publish | no references; publish.md and local export only | use tools available in the session; see [Codex setup](codex.md) |
| A transcript skill (yt-dlp + whisper style) | reference | read platform captions | any; `yt-dlp` + `faster-whisper` |
| [anatomy](https://github.com/wheresryan22/anatomy) skill | production (companion figure) | skip | clone into your skills dir |
| [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | score (ACE-Step client) | synthesized score | clone into `<project>/third_party/`; see `skills/v2w-score/references/ace-step.md` |
| Codex with fresh-context subagents | critique | new session with only the listed files; otherwise leave the gate open | see [Codex setup](codex.md) |

Playwright is found through Node's module path. After a global install, set
`NODE_PATH="$(npm root -g)"` so the Playwright check can resolve it.

## Check the environment

`skills/v2w-orchestra/scripts/check_env.py` checks the toolchain and prints
PASS / WARN / FAIL diagnostics (only FAIL exits 1; missing animate or
Playwright currently warns, so resolve those warnings before rendering):

```bash
python3 <repo>/skills/v2w-orchestra/scripts/check_env.py --project <project>
python3 <repo>/skills/v2w-orchestra/scripts/check_env.py --animate-dir <path>
```

`bash setup.sh --dev` enables the privacy hook for contributors and prints this
command. Run it before the first export on a new machine.

`new_piece.py` and `check_env.py` share animate discovery: `--animate-dir`,
then `ANIMATE_DIR`, project `.agents/skills/animate`, user
`~/.agents/skills/animate`, `$CODEX_HOME/skills/animate` (defaults to
`~/.codex/skills/animate`), then project and user `.claude/skills/animate`
for existing installs. Explicit overrides are authoritative, even if missing.
With no installed match the diagnostic path is `~/.agents/skills/animate`. When the template is missing it prints
the path it tried and the override to use, and exits 1 unless you pass
`--allow-missing-template` (gate C will fail without `piece.json`/`src/`).
`check_env.py` reports the same resolved path in its animate check.
