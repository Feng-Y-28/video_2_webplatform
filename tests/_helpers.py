"""Shared helpers for the v2w test suite.

Standard library only. Every fixture is created under
``tempfile.TemporaryDirectory()``; tests never read a real project, the local
denylist, a home path or the network, and never render video.
"""
import atexit
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# Subprocesses get an isolated HOME so no test can read a real one.
FAKE_HOME = tempfile.mkdtemp(prefix="v2w-test-home-")
atexit.register(shutil.rmtree, FAKE_HOME, True)
ORCH = REPO / "skills" / "v2w-orchestra" / "scripts"
CRIT = REPO / "skills" / "v2w-critique" / "scripts"
REFS = REPO / "skills" / "v2w-critique" / "references"
PUBLISH = REPO / "skills" / "v2w-publish"


def load_module(path, name):
    """Import a script by path without touching the real package layout."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run_py(script, *args, env=None):
    """Run a repository script with a clean, fixture-only environment."""
    clean = {k: v for k, v in os.environ.items()
             if k in ("PATH", "LANG", "LC_ALL", "TMPDIR", "SYSTEMROOT")}
    clean["HOME"] = FAKE_HOME
    clean.pop("ANIMATE_DIR", None)
    if env:
        clean.update(env)
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)],
        capture_output=True, text=True, env=clean, timeout=120,
    )


def rubric_items(gate):
    """Read the real rubric shipped with the repo: {id: blocking}."""
    files = sorted(REFS.glob(f"rubric-{gate}-*.md"))
    assert len(files) == 1, files
    rows = re.findall(
        r"^\|\s*([A-D]\d+)\s*\|[^|]*\|\s*(blocking|—|-)\s*\|",
        files[0].read_text(), re.M,
    )
    return {item: flag == "blocking" for item, flag in rows}


def new_project(root):
    """A temp project skeleton with just the config the scripts read."""
    project = Path(root) / "project"
    (project / "pieces").mkdir(parents=True)
    (project / "v2w.config.json").write_text(
        json.dumps({"max_retries": 2}) + "\n", encoding="utf-8")
    return project


def new_piece_dir(project, name="demo"):
    piece = project / "pieces" / name
    (piece / "critique").mkdir(parents=True)
    return piece


def critique_json(gate, n, score=5, schema=None, takeaway="fixture takeaway", **over):
    """Build a critique round for every rubric item, all at ``score``."""
    data = {
        "gate": gate,
        "round": n,
        "items": [
            {"id": item, "score": score, "evidence": "fixture", "fix": ""}
            for item in rubric_items(gate)
        ],
        "takeaway": takeaway,
        "must_fix": [],
        "summary": "fixture",
    }
    if schema is not None:
        data["schema"] = schema
    data.update(over)
    return data


def write_round(piece, gate, n, **kwargs):
    data = critique_json(gate, n, **kwargs)
    path = piece / "critique" / f"{gate}-r{n}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def failing_round(piece, gate, n):
    """One blocking item below 3, so the gate must FAIL."""
    data = critique_json(gate, n)
    blocking = next(item for item, flag in rubric_items(gate).items() if flag)
    for item in data["items"]:
        if item["id"] == blocking:
            item["score"] = 2
            item["fix"] = "fixture fix"
    path = piece / "critique" / f"{gate}-r{n}.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def status_text(labels_checked):
    lines = ["# demo — status", "", "## Gates"]
    for label in labels_checked:
        mark = "x" if label.endswith("*") else " "
        name = label.rstrip("*")
        lines.append(f"- [{mark}] {name}")
    return "\n".join(lines) + "\n"
