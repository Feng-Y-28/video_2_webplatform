#!/usr/bin/env python3
"""Decide PASS / FAIL for the latest critique round of a gate.

Reads the rubric (item ids, which are blocking) and <piece>/critique/<gate>-r<n>.json.
Exit 0 = PASS, 1 = FAIL with retries left, 2 = FAIL with no retries (stop), 3 = bad input.

    python3 critique_gate.py <piece> <A|B|C|D>
"""
import json
import re
import sys
from pathlib import Path

RUBRICS = Path(__file__).resolve().parents[1] / "references"
ROW = re.compile(r"^\|\s*([A-D]\d+)\s*\|[^|]*\|\s*(blocking|—|-)\s*\|", re.M)
MEAN_MIN, BLOCKING_MIN = 4.0, 3
NEEDS_TAKEAWAY = {"B", "D"}


def rubric_items(gate: str) -> dict:
    files = list(RUBRICS.glob(f"rubric-{gate}-*.md"))
    if len(files) != 1:
        sys.exit(f"rubric for gate {gate} not found in {RUBRICS}")
    return {m.group(1): m.group(2) == "blocking" for m in ROW.finditer(files[0].read_text())}


def max_retries(piece: Path) -> int:
    cfg = piece.parent.parent / "v2w.config.json"
    try:
        return int(json.loads(cfg.read_text()).get("max_retries", 2))
    except (OSError, ValueError):
        return 2


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in "ABCD" or len(sys.argv[2]) != 1:
        print(__doc__)
        return 3
    piece, gate = Path(sys.argv[1]).expanduser().resolve(), sys.argv[2]
    rounds = sorted((piece / "critique").glob(f"{gate}-r*.json"),
                    key=lambda p: int(re.search(r"-r(\d+)", p.name).group(1)))
    if not rounds:
        print(f"no critique/{gate}-r*.json yet")
        return 3
    latest = rounds[-1]
    try:
        data = json.loads(latest.read_text())
    except ValueError as e:
        print(f"{latest.name}: invalid JSON ({e})")
        return 3

    items = rubric_items(gate)
    got = {i.get("id"): i for i in data.get("items", [])}
    problems = []
    missing = [k for k in items if k not in got]
    if missing:
        problems.append(f"items not scored: {', '.join(missing)}")
    scores = []
    for k, blocking in items.items():
        if k not in got:
            continue
        s = got[k].get("score")
        if not isinstance(s, int) or not 1 <= s <= 5:
            problems.append(f"{k}: score {s!r} is not 1-5")
            continue
        scores.append(s)
        if blocking and s < BLOCKING_MIN:
            problems.append(f"{k} (blocking) = {s}: {got[k].get('fix', '')}")
        elif s < 4:
            print(f"  low  {k} = {s}: {got[k].get('fix', '')}")
    mean = sum(scores) / len(scores) if scores else 0.0
    if mean < MEAN_MIN:
        problems.append(f"mean {mean:.2f} < {MEAN_MIN}")
    for m in data.get("must_fix", []):
        problems.append(f"must_fix: {m}")
    if gate in NEEDS_TAKEAWAY and not str(data.get("takeaway", "")).strip():
        problems.append("takeaway is empty")

    n = len(rounds)
    left = max_retries(piece) + 1 - n
    print(f"gate {gate} round {n}: mean {mean:.2f}")
    if gate in NEEDS_TAKEAWAY:
        print(f"  takeaway: {data.get('takeaway', '')}")
        print("  -> compare with principle.md's mechanism; a mismatch is a FAIL")
    if not problems:
        print("PASS")
        return 0
    for p in problems:
        print(f"  FAIL {p}")
    if left > 0:
        print(f"FAIL — fix and re-run critique ({left} retr{'y' if left == 1 else 'ies'} left)")
        return 1
    print("FAIL — no retries left: stop and carry these issues into the sample review")
    return 2


if __name__ == "__main__":
    sys.exit(main())
