# v2w video workspace

This is a private video project. Keep its media, source material, account
details and raw logs here; the linked v2w repository contains reusable skills.

For a v2w request, load `$v2w-orchestra` from
`.agents/skills/v2w-orchestra/SKILL.md`, then the stage skill it selects.
Resolve the skill directory's symlink before following repository-relative
paths such as `../../docs/`; `../shared/` contains the shared rules.
If skills were installed globally, use the skill location supplied by Codex.

Read `v2w.config.json` and the selected piece's `STATUS.md` and `LOG.md`
before resuming. Run the orchestrator's `validate_piece.py` to find the next
step. Respect the gate order, retry budget, input hashes, and final sample
approval defined by the skills. An independent critique requires a fresh
context without the author's conversation; if unavailable, leave that gate
open and record the limitation.

Use available Codex tools or connected plugins for browsing and research.
Follow their usage instructions; do not assume a Claude-only browser tool
exists. Configuration records workflow preferences, not extra tool access or
permission to bypass the host's approval and sandbox rules. Require the user's
sample approval before uploads; publish only when authorized by the config
and the user's instructions. Record fallbacks and unresolved checks in LOG.md.
