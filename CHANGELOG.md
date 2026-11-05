# Changelog

## [Unreleased]

- Codex branch: project `.agents/skills/` installation, user-level installation
  with an optional destination, and non-overwriting `AGENTS.md` scaffolding.
  Link `shared/` alongside all nine skills so shared references remain usable.
- Shared animate discovery for project/user Codex locations, `CODEX_HOME`,
  explicit overrides and existing Claude installations.
- Codex tool routing and fresh-context critique instructions; the read-only
  critic returns JSON and the orchestrator saves it unchanged.
- Regression coverage for installation, preserved user files, symlink entry
  points and animate path precedence.

- `init_project.py`: project `.gitignore` is now a managed whitelist block — only `develop_log/` and per-piece text records (LOG, STATUS, principle, brief, refcard, critique JSON) are tracked.

## [0.2.0] — 2026-11-04

Reliability release: a gate cannot be ticked on a stale artefact or out of
order, publishing is preflighted, and a stdlib test suite runs without CI.

- `v2w-critique`: a round stores `sha256` of its inputs; a changed artefact
  prints `STALE` (exit 4) and the gate cannot be ticked. Legacy JSON without
  `inputs` only warns. Budget-spent gates allow one verification round; a
  later `must_fix` that contradicts an earlier gate's evidence is adjudicated
  instead of executed.
- `v2w-orchestra`: `validate_piece.py` rejects illegal gate order, revalidates
  ticked gates and checks the review / D / sample / published artefacts; the
  source check accepts Chinese sources, `derived`, tables and `→` references;
  `critique_gate` separates PASS from the retry budget. New `check_env.py`;
  `new_piece.py` finds animate via `--animate-dir` / `ANIMATE_DIR`.
- `v2w-publish`: export preflight compares size and `sha256` with
  `renders/share.mp4`; the upload cap comes from `max_upload_mb` or the live
  page (never a fixed number); over-cap files get a two-pass encode and a
  loudness re-check. Form filling reads every value back from the DOM, reads
  back the cover time and the declaration toggles, and saves only cropped
  screenshots. Campaign topics require `allow_campaign_topics`; editing a
  published note updates it in place.
- Docs: critique C runs on look + board **before the full build**; `max_retries`
  is defined as automatic retries after the first round plus one verification
  round; M includes a manual `score.js` read; dependencies list the required set
  and `check_env.py`.
- `tests/`: stdlib `unittest` suite for gates, critique, scaffolding, docs and
  environment, all fixtures in temp directories and no video render;
  `examples/minimal` gains critique A and expected exit codes.

## [0.1.0] — 2026-10-29

First version. Paper / idea in, short explainer video out; autonomous except
for the final sample review.

- `v2w-orchestra`: seven-stage pipeline, gates in `STATUS.md`, standing consent in
  `v2w.config.json`; `init_project.py`, `new_piece.py` (`--input`, `--from`), `validate_piece.py`.
- `v2w-distill`: paper / idea → principle card (problem, mechanism, sourced proof numbers, cuts).
- `v2w-reference`: same-topic videos → reference card (order, devices, viewer confusions, topic checks).
- `v2w-script`: hook, explanation order, beats, claims; short-video structure reference.
- `v2w-production`: conventions on top of animate; look + board critiqued before the full build.
- `v2w-score`: measured music gate, automatic take choice, music principles, ACE-Step notes;
  `mix_template.sh` (static-gain mix that keeps automation).
- `v2w-review`: checklist, `band_energy.py` (low-mid mud and thin-top heuristics), sample-review hand-off.
- `v2w-critique`: fresh-subagent protocol, rubrics A (content) B (script) C (visual) D (final),
  `critique_gate.py` (deterministic pass/fail and retry budget).
- `v2w-publish`: per-platform copy, config-driven upload after approval, optional translated version.
- `shared/`: claims-and-sources, pitfalls.
- Privacy pre-commit hook with a local, uncommitted denylist; `setup.sh`.
