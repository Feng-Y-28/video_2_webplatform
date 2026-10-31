#!/usr/bin/env python3
"""Scaffold a v2w project directory.

Idempotent: creates what is missing, never overwrites an existing file.
Keeps a whitelist block in .gitignore (only logs and piece records are tracked);
other lines in an existing .gitignore are left alone.
Writes v2w.config.json (standing consent for browsing, hosted music, publishing).

    python3 init_project.py <project> [--no-git] [--no-link]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[2]  # .../skills
TEMPLATES = Path(__file__).resolve().parents[1] / "templates"

CONFIG = {  # standing consent; the pipeline never stops to ask about these
    "allow_browse_references": True,
    "allow_hosted_music_api": False,
    "publish_after_approval": "fill_form",  # none | fill_form | publish
    "platforms": ["xiaohongshu"],
    "max_retries": 2,
}

DIRS = ["develop_log", "pieces", "exports", "third_party", ".claude/skills"]

BEGIN, END = "# >>> v2w (managed by init_project.py)", "# <<< v2w"
# Whitelist: ignore everything, then track only the text records of the work —
# raw logs and each piece's decisions and critiques. Media, source, images,
# config and cloned tools stay local.
GITIGNORE = [
    BEGIN,
    "*",
    "!*/",
    "/third_party/",  # cloned repos would be added as embedded repos
    "/exports/",
    "!/.gitignore",
    "!/develop_log/**",
    "!/pieces/*/LOG.md",
    "!/pieces/*/STATUS.md",
    "!/pieces/*/principle.md",
    "!/pieces/*/brief.md",
    "!/pieces/*/refs/refcard.md",
    "!/pieces/*/critique/*.json",
    ".DS_Store",
    END,
]


def ensure_gitignore(project: Path) -> None:
    path = project / ".gitignore"
    text = path.read_text() if path.exists() else ""
    block = "\n".join(GITIGNORE) + "\n"
    if BEGIN in text and END in text:
        head, rest = text.split(BEGIN, 1)
        new = head + block + rest.split(END, 1)[1].lstrip("\n")
    else:
        new = text + ("\n" if text and not text.endswith("\n") else "") + block
    if new == text:
        print("  .gitignore up to date")
        return
    path.write_text(new)
    print("  .gitignore: v2w whitelist block written (tracks logs and piece records only)")


def link_skills(project: Path) -> None:
    target = project / ".claude" / "skills"
    for link in target.glob("v2w-*"):  # skills renamed or removed upstream
        if link.is_symlink() and not link.exists():
            link.unlink()
            print(f"  drop {link.relative_to(project)} (dangling)")
    for skill in sorted(SKILLS_ROOT.iterdir()):
        if not (skill / "SKILL.md").exists():
            continue  # skips shared/
        link = target / skill.name
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            print(f"  ! {link} is a real path, skipped")
            continue
        link.symlink_to(skill)
        print(f"  link {link.relative_to(project)} -> {skill}")


def copy_if_missing(src: Path, dst: Path) -> None:
    if dst.exists():
        return
    dst.write_text(src.read_text())
    print(f"  new  {dst.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("--no-git", action="store_true", help="do not run git init")
    ap.add_argument("--no-link", action="store_true", help="do not symlink skills into .claude/skills")
    args = ap.parse_args()

    project = args.project.expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    print(f"project: {project}")

    for d in DIRS:
        (project / d).mkdir(parents=True, exist_ok=True)
    copy_if_missing(TEMPLATES / "develop_log_README.md", project / "develop_log" / "README.md")
    ensure_gitignore(project)
    cfg = project / "v2w.config.json"
    if not cfg.exists():
        cfg.write_text(json.dumps(CONFIG, indent=2) + "\n")
        print("  new  v2w.config.json (review the consent flags)")
    if not args.no_link:
        link_skills(project)

    if not args.no_git and not (project / ".git").exists():
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        print("  git init (local only; add a remote yourself if you want one)")

    print("done. next: new_piece.py", project, "<name>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
