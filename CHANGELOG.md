# Changelog

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
