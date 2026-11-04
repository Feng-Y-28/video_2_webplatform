#!/usr/bin/env python3
"""Preflight the tools the pipeline needs. Deterministic, standard library only.

Prints PASS / WARN / FAIL lines and exits 1 only when something FAILs.
Paths under the home directory are printed with a `~/` placeholder.

    python3 check_env.py [--project <project>] [--animate-dir <animate skill dir>]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PY = (3, 9)
DEFAULT_ANIMATE = Path(os.environ.get("ANIMATE_DIR", "~/.claude/skills/animate")).expanduser()
TOOLS = ("export.mjs", "review.mjs", "beats.mjs")
PLAYWRIGHT_MODULES = ("playwright", "playwright-core")


def pretty(path) -> str:
    """Never print an expanded home path."""
    s = str(path)
    home = str(Path.home())
    if s == home:
        return "~"
    if s.startswith(home + os.sep):
        return "~" + s[len(home):]
    return s


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None


def find_playwright(animate: Path) -> dict:
    """Where Playwright resolves from, keyed by the mechanism that found it."""
    found = {}
    for entry in os.environ.get("NODE_PATH", "").split(os.pathsep):
        if not entry:
            continue
        for module in PLAYWRIGHT_MODULES:
            p = Path(entry) / module
            if p.is_dir():
                found.setdefault("NODE_PATH", pretty(p))
    for module in PLAYWRIGHT_MODULES:
        p = animate / "node_modules" / module
        if p.is_dir():
            found.setdefault("animate node_modules", pretty(p))
    npm = shutil.which("npm")
    if npm:
        r = run([npm, "root", "-g"])
        if r is not None and r.returncode == 0 and r.stdout.strip():
            for module in PLAYWRIGHT_MODULES:
                p = Path(r.stdout.strip()) / module
                if p.is_dir():
                    found.setdefault("npm root -g", pretty(p))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, help="check a scaffolded project directory too")
    ap.add_argument("--animate-dir", type=Path, default=DEFAULT_ANIMATE)
    args = ap.parse_args()

    project = args.project.expanduser().resolve() if args.project else None
    animate = args.animate_dir.expanduser().resolve()
    results = []

    def add(level: str, message: str) -> None:
        results.append(level)
        print(f"{level:4} {message}")

    # Python
    have = sys.version_info[:2]
    if have >= MIN_PY:
        add("PASS", f"Python {sys.version.split()[0]} (>= 3.9)")
    else:
        add("FAIL", f"Python {sys.version.split()[0]} is older than 3.9")

    # ffmpeg with drawtext
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        add("FAIL", "ffmpeg not on PATH")
    else:
        r = run([ffmpeg, "-hide_banner", "-filters"])
        filters = (r.stdout + r.stderr) if r is not None else ""
        if "drawtext" in filters:
            add("PASS", f"ffmpeg with the drawtext filter ({pretty(ffmpeg)})")
        else:
            add("FAIL", "ffmpeg found but the drawtext filter is missing (use a full build)")

    # Node
    node = shutil.which("node")
    if not node:
        add("FAIL", "Node not on PATH")
    else:
        r = run([node, "--version"])
        version = r.stdout.strip() if r is not None and r.returncode == 0 else "unknown"
        major = re.match(r"v?(\d+)", version)
        if major and int(major.group(1)) < 18:
            add("FAIL", f"Node {version} is older than 18")
        else:
            add("PASS", f"Node {version} ({pretty(node)})")

    # Playwright, resolved the three supported ways
    found = find_playwright(animate)
    if not found:
        add("WARN", "Playwright not resolvable via NODE_PATH, the animate node_modules "
                    "or `npm root -g`; animate export/review will fail")
    elif len(found) > 1:
        where = "; ".join(f"{k}: {v}" for k, v in sorted(found.items()))
        add("WARN", f"Playwright resolves from more than one place (ambiguous): {where}")
    else:
        where, path = next(iter(found.items()))
        add("PASS", f"Playwright via {where} ({path})")

    # animate tools
    if not animate.is_dir():
        add("WARN", f"animate directory not found at {pretty(animate)}; gates C/review need it")
    else:
        add("PASS", f"animate directory {pretty(animate)}")
        for tool in TOOLS:
            p = animate / "tools" / tool
            if p.is_file():
                add("PASS", f"animate tool {tool}")
            else:
                add("WARN", f"animate tool missing: {pretty(p)}")

    # Project
    if project is not None:
        if not project.is_dir():
            add("FAIL", f"project not found: {pretty(project)}")
        else:
            add("PASS", f"project {pretty(project)}")
            cfg = project / "v2w.config.json"
            if cfg.is_file():
                add("PASS", "v2w.config.json present")
            else:
                add("WARN", "no v2w.config.json; run init_project.py")

    return 1 if "FAIL" in results else 0


if __name__ == "__main__":
    sys.exit(main())
