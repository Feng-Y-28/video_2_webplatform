#!/usr/bin/env bash
# video_2_webplatform setup.
#
#   bash setup.sh <project-dir>     scaffold (or update) a project and link the v2w skills into
#                                   <project>/.claude/skills/ — the skills load only in that project
#   bash setup.sh --global          link the v2w skills into ~/.claude/skills/ (every project)
#   bash setup.sh --dev             enable this repo's pre-commit privacy hook (contributors)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

case "${1:-}" in
  ""|-h|--help)
    sed -n '2,8p' "$0"; exit 0 ;;
  --global)
    mkdir -p "$HOME/.claude/skills"
    for s in "$HERE"/skills/v2w-*/; do
      s="${s%/}"; link="$HOME/.claude/skills/$(basename "$s")"
      if [ -L "$link" ]; then rm "$link"; elif [ -e "$link" ]; then echo "skip (real dir): $link"; continue; fi
      ln -s "$s" "$link"; echo "linked $link"
    done ;;
  --dev)
    git -C "$HERE" config core.hooksPath .githooks
    chmod +x "$HERE/.githooks/pre-commit"
    echo "pre-commit hook enabled. Put private patterns in $HERE/.denylist.local (git-ignored)." ;;
  *)
    python3 "$HERE/skills/v2w-orchestra/scripts/init_project.py" "$1" ;;
esac
