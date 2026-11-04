#!/usr/bin/env python3
"""Decide PASS / FAIL for the latest critique round of a gate.

Reads the rubric (item ids, which are blocking), <piece>/critique/<gate>-r<n>.json
and, when present, the matching <gate>-r<n>.inputs.json stamp.

Stamp the inputs BEFORE spawning the critic subagent:

    python3 critique_gate.py <piece> <A|B|C|D> --stamp

`--stamp` writes <piece>/critique/<gate>-r<n>.inputs.json: a JSON object mapping
every piece-relative POSIX input path to its sha256. The critique JSON itself is
never hashed. A normal run resolves the latest round, recomputes that file set
and every digest, and refuses to score a stale critique.

    python3 critique_gate.py <piece> <A|B|C|D> [--verify]

Rounds: `<gate>-r1` .. `<gate>-r<max_retries+1>` are the automatic rounds. After
that budget there is exactly one manual-fix + verification round, selected with
`--verify`; the gate is ticked only when that verification round PASSes.

Exit codes:
    0 = PASS
    1 = FAIL, another round is still available (automatic retry or verification)
    2 = FAIL on the verification round: stop, carry open issues to the sample review
    3 = bad input, bad round layout, a round outside the allowed sequence, or a
        schema-2 critique whose inputs were never stamped
    4 = STALE: a stamped input is missing or its digest changed
"""
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

RUBRICS = Path(__file__).resolve().parents[1] / "references"
ROW = re.compile(r"^\|\s*([A-D]\d+)\s*\|[^|]*\|\s*(blocking|—|-)\s*\|", re.M)
MEAN_MIN, BLOCKING_MIN = 4.0, 3
NEEDS_TAKEAWAY = {"B", "D"}

# One table for stamping and checking. Later stages add files as production
# records them (`review/text-boxes.json`, the rendered video and audio).
GATE_INPUTS = {
    "A": ["principle.md", "source/**/*"],
    "B": ["brief.md", "principle.md", "refs/refcard.md"],
    "C": ["review/look.png", "review/board.png", "review/text-boxes.json",
          "brief.md", "refs/refcard.md", "piece.json"],
    "D": ["review/shot*-sheet.jpg", "review/phone.jpg", "brief.md",
          "principle.md", "publish.md", "renders/share.mp4", "renders/audio.wav"],
}
# A legacy gate-C piece predates the measured text boxes; warn instead of failing.
OPTIONAL_INPUTS = {"C": {"review/text-boxes.json"}}
# LOG.md and STATUS.md are evidence the critic reads, not stamped inputs: a
# summary appended or a gate ticked after the round must not void it.
# publish.md's workflow-state lines change after D (approval, upload, live edit),
# so only its copy body is hashed.
PUBLISH_STATE = re.compile(
    r"^\s*(?:\*\*)?(?:status|form verification|file(?: size)?|master|"
    r"limit check|sha256)(?:\*\*)?\s*:",
    re.I,
)
# Read-back and campaign fields are filled during upload, after D.
PUBLISH_READBACK = re.compile(
    r"\s*·\s*(?:read back|state read back|campaign/activity):[^\n]*", re.I)


class RoundError(Exception):
    """A critique directory that cannot be read as a contiguous round sequence."""


def rubric_items(gate: str) -> dict:
    files = list(RUBRICS.glob(f"rubric-{gate}-*.md"))
    if len(files) != 1:
        sys.exit(f"rubric for gate {gate} not found in {RUBRICS}")
    return {m.group(1): m.group(2) == "blocking" for m in ROW.finditer(files[0].read_text())}


def max_retries(piece: Path) -> int:
    cfg = piece.parent.parent / "v2w.config.json"
    try:
        return max(0, int(json.loads(cfg.read_text()).get("max_retries", 2)))
    except (OSError, ValueError, TypeError):
        return 2


def schema_version(data: dict) -> int:
    for key in ("schema", "rubric_version"):
        if key in data:
            try:
                return int(data[key])
            except (TypeError, ValueError):
                return 1
    return 1  # pre-schema critique files are legacy


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_input(piece: Path, rel: str) -> str:
    """Hash one declared input. publish.md ignores workflow-state lines."""
    path = piece / rel
    if rel == "publish.md":
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        kept = [PUBLISH_READBACK.sub("", line) for line in lines
                if not PUBLISH_STATE.match(line)]
        return hashlib.sha256(("\n".join(kept) + "\n").encode("utf-8")).hexdigest()
    return sha256(path)


def collect_inputs(piece: Path, gate: str):
    """Return (present POSIX paths, missing required specs, warnings)."""
    files, missing, warns = set(), [], []
    optional = OPTIONAL_INPUTS.get(gate, set())
    for spec in GATE_INPUTS[gate]:
        if any(c in spec for c in "*?["):
            matches = sorted(p for p in piece.glob(spec) if p.is_file())
        else:
            p = piece / spec
            matches = [p] if p.is_file() else []
        if not matches:
            if spec in optional:
                warns.append(f"optional input missing: {spec}")
            else:
                missing.append(spec)
            continue
        for p in matches:
            files.add(p.relative_to(piece).as_posix())
    return files, missing, warns


def round_files(piece: Path, gate: str):
    """Parse critique/<gate>-r<n>.json into {n: path}; WARN on malformed names."""
    rounds, warns = {}, []
    cdir = piece / "critique"
    if not cdir.is_dir():
        return rounds, warns
    for p in sorted(cdir.glob("*.json")):
        name = p.name
        if name.endswith(".inputs.json") or not name.startswith(f"{gate}-") or not name.endswith(".json"):
            continue
        m = re.fullmatch(rf"{gate}-r(\d+)\.json", name)
        if not m:
            warns.append(f"ignoring non-round file: critique/{name}")
            continue
        n = int(m.group(1))
        if n in rounds:
            raise RoundError(
                f"duplicate round number {n}: critique/{rounds[n].name}, critique/{name}")
        rounds[n] = p
    return rounds, warns


def check_contiguous(rounds: dict) -> None:
    nums = sorted(rounds)
    if not nums:
        raise RoundError("no critique rounds")
    if nums[0] != 1 or nums != list(range(1, nums[-1] + 1)):
        expected = list(range(1, nums[-1] + 1))
        missing = [n for n in expected if n not in rounds]
        invalid = [n for n in nums if n < 1]
        detail = f"present {nums}"
        if missing:
            detail += f", missing {missing}"
        if invalid:
            detail += f", invalid {invalid}"
        raise RoundError(f"non-contiguous rounds: {detail}")


def do_stamp(piece: Path, gate: str) -> int:
    try:
        rounds, warns = round_files(piece, gate)
        if rounds:
            check_contiguous(rounds)
    except RoundError as e:
        print(f"round layout: {e}")
        return 3
    for w in warns:
        print(f"WARN: {w}")
    # Stamp the round the critic is about to write; if a legacy round exists
    # without its stamp, fill that one first instead of skipping ahead.
    n = 1
    while n in rounds and (piece / "critique" / f"{gate}-r{n}.inputs.json").is_file():
        n += 1
    files, missing, warns = collect_inputs(piece, gate)
    for w in warns:
        print(f"WARN: {w}")
    if missing:
        print(f"STALE: cannot stamp round {n}; missing inputs: {', '.join(missing)}")
        return 4
    cdir = piece / "critique"
    cdir.mkdir(parents=True, exist_ok=True)
    sidecar = {rel: digest_input(piece, rel) for rel in sorted(files)}
    path = cdir / f"{gate}-r{n}.inputs.json"
    path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n")
    print(f"stamped critique/{path.name} ({len(sidecar)} files)")
    return 0


def check_stale(piece: Path, gate: str, n: int, data: dict) -> int:
    """0 = verified or legacy, 3 = malformed/missing stamp, 4 = stale inputs."""
    path = piece / "critique" / f"{gate}-r{n}.inputs.json"
    if not path.is_file():
        if schema_version(data) >= 2:
            print(f"critique/{gate}-r{n}.json declares schema "
                  f"{schema_version(data)} but has no inputs stamp; "
                  "run --stamp before the critic")
            return 3
        print("WARN: critique has no inputs stamp (legacy round); scoring without a staleness check")
        return 0
    try:
        recorded = json.loads(path.read_text())
    except ValueError as e:
        print(f"critique/{path.name}: invalid inputs JSON ({e})")
        return 3
    if not isinstance(recorded, dict):
        print(f"critique/{path.name}: inputs stamp must be a JSON object")
        return 3
    for key in recorded:
        if not isinstance(key, str):
            print(f"critique/{path.name}: non-string input key {key!r}")
            return 3
        rel = PurePosixPath(key)
        if rel.is_absolute() or ".." in rel.parts:
            print(f"critique/{path.name}: unsafe input path {key!r}")
            return 3

    files, missing, warns = collect_inputs(piece, gate)
    for w in warns:
        print(f"WARN: {w}")
    stale = [f"missing input: {spec}" for spec in missing]
    for rel in sorted(files):
        if rel not in recorded:
            stale.append(f"input not stamped: {rel}")
        elif digest_input(piece, rel) != recorded[rel]:
            stale.append(f"changed since stamp: {rel}")
    for rel in sorted(recorded):
        if rel not in files:
            stale.append(f"missing input: {rel}")
    if stale:
        for s in stale:
            print(f"  STALE {s}")
        print("STALE — re-stamp the inputs and redo this round")
        return 4
    print(f"inputs verified: {len(files)} files match critique/{path.name}")
    return 0


def score_round(gate: str, data: dict):
    """Return (problems, mean) for one critique JSON."""
    items = rubric_items(gate)
    got = {i.get("id"): i for i in data.get("items", [])}
    problems = []
    if gate == "D" and "D8" not in got and schema_version(data) < 2:
        print("WARN: gate D critique has no D8 and schema < 2 (legacy rubric); scoring without D8")
        items.pop("D8", None)
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
    return problems, mean


def parse_args(argv):
    stamp = verify = False
    positional = []
    for a in argv[1:]:
        if a == "--stamp":
            stamp = True
        elif a == "--verify":
            verify = True
        elif a.startswith("-"):
            return None
        else:
            positional.append(a)
    if len(positional) != 2:
        return None
    piece, gate = positional
    if len(gate) != 1 or gate not in "ABCD" or (stamp and verify):
        return None
    return Path(piece).expanduser().resolve(), gate, stamp, verify


def main(argv=None) -> int:
    argv = sys.argv if argv is None else argv
    parsed = parse_args(argv)
    if not parsed:
        print(__doc__)
        return 3
    piece, gate, stamp, verify = parsed
    if stamp:
        return do_stamp(piece, gate)

    try:
        rounds, warns = round_files(piece, gate)
        for w in warns:
            print(f"WARN: {w}")
        if not rounds:
            print(f"no critique/{gate}-r*.json yet")
            return 3
        check_contiguous(rounds)
    except RoundError as e:
        print(f"round layout: {e}")
        return 3

    n = max(rounds)
    auto_max = max_retries(piece) + 1
    verify_round = auto_max + 1
    if n > verify_round:
        print(f"round {n} is past the verification round (r{verify_round}); no further rounds allowed")
        return 3
    if verify and n < verify_round:
        print(f"--verify needs the round after the automatic budget (r{verify_round}); latest is r{n}")
        return 3
    if not verify and n == verify_round:
        print(f"round {n} is the verification round; re-run with --verify")
        return 3

    latest = rounds[n]
    try:
        data = json.loads(latest.read_text())
    except ValueError as e:
        print(f"{latest.name}: invalid JSON ({e})")
        return 3

    rc = check_stale(piece, gate, n, data)
    if rc:
        return rc

    problems, mean = score_round(gate, data)
    print(f"gate {gate} round {n}: mean {mean:.2f}")
    if gate in NEEDS_TAKEAWAY:
        print(f"  takeaway: {data.get('takeaway', '')}")
        print("  -> compare with principle.md's mechanism; a mismatch is a FAIL")
    if not problems:
        print("PASS")
        return 0
    for p in problems:
        print(f"  FAIL {p}")
    if verify:
        print("FAIL — verification round failed: stop and carry these issues into the sample review")
        return 2
    if n < auto_max:
        left = auto_max - n
        print(f"FAIL — fix and re-run critique ({left} automatic retr{'y' if left == 1 else 'ies'} left)")
    else:
        print("FAIL — automatic retries exhausted; apply manual fixes, then run one --verify round")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
