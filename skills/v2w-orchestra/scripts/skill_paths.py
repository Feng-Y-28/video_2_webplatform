#!/usr/bin/env python3
"""Resolve optional skills and install the local v2w bundle (no network)."""
import argparse
import os
from pathlib import Path
from typing import Optional

SKILLS_ROOT = Path(__file__).resolve().parents[2]


def resolve_animate(project: Optional[Path] = None,
                    explicit: Optional[Path] = None) -> Path:
    """Explicit overrides are authoritative, even when the path is missing."""
    override = explicit if explicit is not None else os.environ.get("ANIMATE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))).expanduser()
    candidates = []
    if project is not None:
        candidates.append(project / ".agents" / "skills" / "animate")
    candidates.extend([
        home / ".agents" / "skills" / "animate",
        codex_home / "skills" / "animate",
    ])
    if project is not None:
        candidates.append(project / ".claude" / "skills" / "animate")
    candidates.append(home / ".claude" / "skills" / "animate")
    return next((p for p in candidates if p.is_dir()),
                home / ".agents" / "skills" / "animate").resolve()


def link_skill_bundle(target: Path) -> None:
    """Link skills and their shared references, preserving real user paths."""
    target = target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in SKILLS_ROOT.glob("v2w-*")
                     if (p / "SKILL.md").is_file())
    sources.append(SKILLS_ROOT / "shared")
    for source in sources:
        link = target / source.name
        if link.is_symlink():
            if link.resolve() == source.resolve():
                continue
            link.unlink()
        elif link.exists():
            print(f"  ! {link} is a real path, skipped")
            continue
        link.symlink_to(source, target_is_directory=True)
        print(f"  link {link} -> {source}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Link v2w skills and shared references into a skills directory.")
    ap.add_argument("target", type=Path)
    link_skill_bundle(ap.parse_args().target)
