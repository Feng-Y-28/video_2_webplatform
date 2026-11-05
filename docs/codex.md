# Codex setup

This branch uses Codex project skills and instructions. The seven production
stages, four critique rubrics, deterministic gates and sample approval remain
the same as the original pipeline.

## Install into a video project

From this repository's `codex/port` checkout:

```bash
bash setup.sh ~/my-videos
codex -C ~/my-videos
```

Ask `$v2w-orchestra` to create or resume a piece. Setup links all nine
`v2w-*` folders and `shared/` into `<project>/.agents/skills/`, and writes
project `AGENTS.md` and `v2w.config.json` only when missing. Existing real
skill folders are skipped, with a diagnostic. The source checkout must stay
available because these are live symlinks. Resolve a skill's symlink before
reading its repository-relative `../../docs/` links.

For all projects, use `bash setup.sh --global` (`~/.agents/skills/`). For a
host that discovers skills in another location, pass it explicitly, for
example `bash setup.sh --global ~/.codex/skills`. Use one installation scope
per workspace to avoid duplicate skills. The installer does not edit Codex
settings, enable tools, select a model, or install third-party dependencies.

To migrate an existing Claude project, run `bash setup.sh <project>` again.
Its config, piece records, existing `AGENTS.md` and `.claude/` files are kept.
If `AGENTS.md` already exists, merge relevant guidance from
`skills/v2w-orchestra/templates/project_AGENTS.md` as appropriate.
Start a new Codex session if project instructions have changed.

## Tool routing

- Research: use available search/document tools and installed paper-reading
  skills. Discover the actual tool names; do not assume Claude tools exist.
- Reference videos: prefer a connected service with suitable capabilities,
  then browser automation. Without either, record the fallback in `LOG.md`.
- Rendering: `animate` is still required. See [dependencies.md](dependencies.md)
  for its installation and shared path discovery in `new_piece.py` and
  `check_env.py`; Codex itself is not a renderer.
- Uploads: use an authorized connector or browser automation in an available
  signed-in session. Follow that tool's own instructions and verify the form
  values required by `v2w-publish`. If the tool cannot verify them, leave a
  local export and `publish.md` with the limitation recorded.

Workflow configuration cannot grant missing tools or override host approvals.
Sample approval remains required before upload; `fill_form` stops before the
final button, and `publish` needs the configured authorization. A missing
browser is never evidence that a post was published.

## Independent critiques

Use one fresh context for each review round, with only the rubric, listed
artefacts, output schema and the bounded prior findings in `v2w-critique`.
When the host offers `fork_turns`, set it to `none`. Otherwise use its
equivalent isolated session capability; a conversation fork is not independent.
Do not pin a model or invent a subagent tool name in the prompt.

The critic reads artefacts and returns JSON. The orchestrator saves it unchanged
to the designated round file and runs `critique_gate.py`. Stamp inputs before
the critic starts and keep that stamp. If an independent session cannot be
created, leave the gate open and report that limitation; self-review cannot
be recorded as an independent PASS.

## Verify the installation

```bash
python3 skills/v2w-orchestra/scripts/check_env.py --project ~/my-videos
python3 -m unittest discover -s tests -v
```

Tests use temporary fixtures and do not render a real video, start a paid model
session, call hosted music APIs or publish a post. Complete a real sample review
after installing the rendering dependencies before treating a video as ready.

Official references: [local skills and symlinks](https://learn.chatgpt.com/docs/build-skills),
[project AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
and [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
