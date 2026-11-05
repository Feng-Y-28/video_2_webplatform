#!/usr/bin/env bash
# video_2_webplatform setup.
#
#   bash setup.sh <project-dir>     scaffold (or update) a project and link the v2w skills into
#                                   <project>/.agents/skills/ and write AGENTS.md for Codex
#   bash setup.sh --global [dir]    link into ~/.agents/skills/ (or an explicit skills dir)
#   bash setup.sh --dev             enable this repo's pre-commit privacy hook (contributors)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

case "${1:-}" in
  ""|-h|--help)
    sed -n '2,7p' "$0"; exit 0 ;;
  --global)
    if [ "$#" -gt 2 ]; then echo "usage: bash setup.sh --global [skills-dir]" >&2; exit 2; fi
    python3 "$HERE/skills/v2w-orchestra/scripts/skill_paths.py" "${2:-$HOME/.agents/skills}" ;;
  --dev)
    git -C "$HERE" config core.hooksPath .githooks
    chmod +x "$HERE/.githooks/pre-commit"
    echo "pre-commit hook enabled. Put private patterns in $HERE/.denylist.local (git-ignored)."
    echo "environment check: python3 $HERE/skills/v2w-orchestra/scripts/check_env.py --project <project>" ;;
  --*)
    echo "unknown option: $1 (see --help)" >&2; exit 2 ;;
  *)
    python3 "$HERE/skills/v2w-orchestra/scripts/init_project.py" "$@" ;;
esac
