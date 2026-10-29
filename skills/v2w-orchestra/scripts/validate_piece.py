#!/usr/bin/env python3
"""Report a piece's gates and check the artefacts the next gate needs.
Exit 1 if an artefact check FAILs.

    python3 validate_piece.py <piece>
"""
import json
import re
import sys
from pathlib import Path

GATES = [  # label in STATUS.md, artefact check to run before it
    ("A content critique passed", "principle"),
    ("B script critique passed", "brief"),
    ("C visual critique passed", "production"),
    ("music checks passed", "music"),
    ("review checks passed", "music"),
    ("D final critique passed", "publish"),
    ("sample approved", "publish"),
    ("published", "publish"),
]
NEXT_STEP = {
    "A content critique passed": "v2w-distill → critique A",
    "B script critique passed": "v2w-reference, v2w-script → critique B",
    "C visual critique passed": "v2w-production (look + board) → critique C",
    "music checks passed": "v2w-production (build/export), v2w-score",
    "review checks passed": "v2w-review (machine checks)",
    "D final critique passed": "v2w-publish (draft publish.md), then critique D",
    "sample approved": "show the user share.mp4 + publish.md + open issues",
    "published": "v2w-publish per v2w.config.json",
}
URL = re.compile(r"https?://\S+")


def read(p: Path) -> str:
    return p.read_text() if p.exists() else ""


def gates(status: str) -> dict:
    out = {}
    for label, _ in GATES:
        m = re.search(r"- \[([ xX])\] " + re.escape(label), status)
        out[label] = bool(m and m.group(1).lower() == "x")
    return out


def section(text: str, title: str) -> str:
    return text.split(f"## {title}", 1)[-1].split("\n## ", 1)[0] if f"## {title}" in text else ""


def sourced_lines(block: str, out: list, where: str) -> None:
    rows = [l for l in block.splitlines() if l.startswith("- ")]
    if not rows:
        out.append(("FAIL", f"{where}: empty"))
    for l in rows:
        low = l.lower()
        if not URL.search(l) and "simplified example" not in low and not low.rstrip().endswith("— derived") and not re.search(r"§|Table|Fig", l):
            out.append(("FAIL", f"{where}: no source: {l[2:70]}"))


def check(kind: str, piece: Path, out: list) -> None:
    if kind == "principle":
        t = read(piece / "principle.md")
        for s in ("Problem", "Mechanism", "Proof numbers", "Left out"):
            if not section(t, s).strip():
                out.append(("FAIL", f"principle.md: '{s}' empty"))
        sourced_lines(section(t, "Proof numbers"), out, "principle.md proof numbers")
    elif kind == "brief":
        t = read(piece / "brief.md")
        for s in ("Hook", "Explanation order", "Beats", "Claims + sources"):
            if not section(t, s).strip():
                out.append(("FAIL", f"brief.md: '{s}' empty"))
        sourced_lines(section(t, "Claims + sources"), out, "brief.md claims")
        if not read(piece / "refs" / "refcard.md"):
            out.append(("WARN", "refs/refcard.md missing — critique B has no topic checks"))
    elif kind == "production":
        pj = piece / "piece.json"
        if not pj.exists():
            out.append(("FAIL", "piece.json missing"))
            return
        data = json.loads(pj.read_text())
        for k in ("name", "format", "style"):
            if k not in data:
                out.append(("FAIL", f"piece.json: '{k}' missing"))
        for s in data.get("scenes", ["src/scenes.js"]):
            if not (piece / s).exists():
                out.append(("FAIL", f"scene file {s} missing"))
        for img in ("look.png", "board.png"):
            if not (piece / "review" / img).exists():
                out.append(("INFO", f"review/{img} not made yet (needed for critique C)"))
    elif kind == "music":
        data = json.loads(read(piece / "piece.json") or "{}")
        music = data.get("music", {}).get("file")
        if music and not (piece / music).exists():
            out.append(("FAIL", f"music file {music} missing"))
        if music and not (piece / "mix.sh").exists():
            out.append(("WARN", "external track without mix.sh — export's one-pass loudnorm flattens automation"))
        if not (piece / "renders" / "share.mp4").exists():
            out.append(("INFO", "renders/share.mp4 not exported yet"))
    elif kind == "publish":
        if not (piece / "publish.md").exists():
            out.append(("INFO", "publish.md not written yet"))


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    piece = Path(sys.argv[1]).expanduser().resolve()
    status = read(piece / "STATUS.md")
    if not status:
        print(f"{piece.name}: no STATUS.md (created by new_piece.py for v2w pieces)")
        return 1
    g = gates(status)
    print(f"piece: {piece.name}")
    for label, _ in GATES:
        print(f"  [{'x' if g[label] else ' '}] {label}")
    nxt = next((label for label, _ in GATES if not g[label]), None)
    if not nxt:
        print("all gates closed")
        return 0
    out = []
    check(dict(GATES)[nxt], piece, out)
    if "TODO" in read(piece / "principle.md") + read(piece / "brief.md"):
        out.append(("INFO", "templates still contain TODO"))
    for level, msg in out:
        print(f"  {level:4} {msg}")
    print(f"next gate: {nxt}  →  {NEXT_STEP[nxt]}")
    return 1 if any(l == "FAIL" for l, _ in out) else 0


if __name__ == "__main__":
    sys.exit(main())
