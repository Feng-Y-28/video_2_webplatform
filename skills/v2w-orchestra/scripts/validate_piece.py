#!/usr/bin/env python3
"""Report a piece's gates and check the artefacts every ticked gate needs.
Exit 0 clean, 1 artefact/order FAIL, 2 not a piece / usage.

Gate order is fixed: A -> B -> C -> music -> review -> D -> sample -> published.
A gate ticked while an earlier one is open is reported as ILLEGAL.

    python3 validate_piece.py <piece>
"""
import json
import re
import subprocess
import sys
from pathlib import Path

GATES = [  # label in STATUS.md, short key used by the checkers
    ("A content critique passed", "A"),
    ("B script critique passed", "B"),
    ("C visual critique passed", "C"),
    ("music checks passed", "music"),
    ("review checks passed", "review"),
    ("D final critique passed", "D"),
    ("sample approved", "sample"),
    ("published", "published"),
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
# Every list item: top-level or indented "-", "+", or an ordered "1." / "1)".
ITEM = re.compile(r"^\s*(?:[-+]|\d+[.)])\s+(.*)$")
ANCHOR = re.compile(r"§|\b(?:table|fig(?:ure)?|section|appendix)\b|表\s*\d|图\s*\d|章节", re.I)
ARROW = re.compile(r"(?:→|->)\s*\S+")
# A repo/document path after an em dash is a source, e.g. "— v2w-critique/SKILL.md".
PATH_REF = re.compile(r"—\s*[\w./-]+\.(?:md|py|json|js|mjs|sh|pdf|txt|csv|html)\b", re.I)
SIMPLIFIED_CN = ("简化示例", "示意", "推导")
REVIEW_HEAD = re.compile(r"^## v\d+ review", re.M)
DERIVED = re.compile(
    r"(?:re-?encode[ds]?|derived|derivation|export(?:ed)?|encoded|made)\b[^\n]{0,100}"
    r"renders/share\.mp4|renders/share\.mp4[^\n]{0,100}"
    r"(?:re-?encode[ds]?|derived|derivation|export(?:ed)?|encoded)",
    re.I,
)
CRITIQUE_GATE = (Path(__file__).resolve().parents[2]
                 / "v2w-critique" / "scripts" / "critique_gate.py")


def read(p: Path) -> str:
    try:
        return p.read_text()
    except (OSError, ValueError):
        return ""


def gates(status: str) -> dict:
    out = {}
    for label, _ in GATES:
        m = re.search(r"- \[([ xX])\] " + re.escape(label), status)
        out[label] = bool(m and m.group(1).lower() == "x")
    return out


WAIVER = re.compile(
    r"^-\s*(?P<gate>[A-Da-d]|music|review)\b[^\n]*"
    r"accepted with open issues by user",
    re.M | re.I,
)


def has_waiver(piece: Path, key: str) -> bool:
    """A user waiver line in STATUS.md names the gate it accepts."""
    return any(m.group("gate").lower() == key.lower()
               for m in WAIVER.finditer(read(piece / "STATUS.md")))


def section(text: str, title: str) -> str:
    return text.split(f"## {title}", 1)[-1].split("\n## ", 1)[0] if f"## {title}" in text else ""


def has_source(text: str) -> bool:
    """A URL, a document anchor, an internal '->' reference, or an exemption."""
    low = text.lower()
    return bool(
        URL.search(text)
        or "simplified example" in low
        or any(mark in text for mark in SIMPLIFIED_CN)
        or re.search(r"\bderived\b", low)
        or ANCHOR.search(text)
        or ARROW.search(text)
        or PATH_REF.search(text)
    )


def sourced_lines(block: str, out: list, where: str) -> None:
    """Every list item needs a URL, a source anchor, or an explicit exemption."""
    rows = []
    for line in block.splitlines():
        m = ITEM.match(line)
        if m:
            rows.append(m.group(1).strip())
    if not rows:
        out.append(("FAIL", f"{where}: empty"))
        return
    for text in rows:
        if not has_source(text):
            out.append(("FAIL", f"{where}: no source: {text[:68]}"))


def load_piece_json(piece: Path, out: list):
    """Return piece.json data, or None after adding a FAIL (never raise)."""
    pj = piece / "piece.json"
    if not pj.exists():
        out.append(("FAIL", "piece.json missing"))
        return None
    try:
        return json.loads(pj.read_text())
    except ValueError as e:
        out.append(("FAIL", f"piece.json: invalid JSON ({e})"))
    except OSError as e:
        out.append(("FAIL", f"piece.json: cannot read ({e})"))
    return None


def check_principle(piece: Path, out: list) -> None:
    t = read(piece / "principle.md")
    for s in ("Problem", "Mechanism", "Proof numbers", "Left out"):
        if not section(t, s).strip():
            out.append(("FAIL", f"principle.md: '{s}' empty"))
    sourced_lines(section(t, "Proof numbers"), out, "principle.md proof numbers")


def check_brief(piece: Path, out: list) -> None:
    t = read(piece / "brief.md")
    for s in ("Hook", "Explanation order", "Beats", "Claims + sources"):
        if not section(t, s).strip():
            out.append(("FAIL", f"brief.md: '{s}' empty"))
    sourced_lines(section(t, "Claims + sources"), out, "brief.md claims")
    if not read(piece / "refs" / "refcard.md"):
        out.append(("WARN", "refs/refcard.md missing — critique B has no topic checks"))


def check_production(piece: Path, out: list) -> None:
    data = load_piece_json(piece, out)
    if data is None:
        return
    if not isinstance(data, dict):
        out.append(("FAIL", "piece.json: top level is not an object"))
        return
    for k in ("name", "format", "style"):
        if k not in data:
            out.append(("FAIL", f"piece.json: '{k}' missing"))
    scenes = data.get("scenes", ["src/scenes.js"])
    if not isinstance(scenes, list) or not all(isinstance(s, str) for s in scenes):
        out.append(("FAIL", "piece.json: 'scenes' must be a list of paths"))
    else:
        for s in scenes:
            if not (piece / s).exists():
                out.append(("FAIL", f"scene file {s} missing"))
    for img in ("look.png", "board.png"):
        if not (piece / "review" / img).exists():
            out.append(("INFO", f"review/{img} not made yet (needed for critique C)"))


def check_music(piece: Path, out: list) -> None:
    data = load_piece_json(piece, out)
    if data is None:
        return
    if not isinstance(data, dict):
        out.append(("FAIL", "piece.json: top level is not an object"))
        return
    music = data.get("music", {})
    music = music.get("file") if isinstance(music, dict) else None
    if music and not (piece / music).exists():
        out.append(("FAIL", f"music file {music} missing"))
    if music and not (piece / "mix.sh").exists():
        out.append(("WARN", "external track without mix.sh — export's one-pass loudnorm flattens automation"))
    if not nonempty(piece / "renders" / "share.mp4"):
        out.append(("INFO", "renders/share.mp4 not exported yet"))


def check_review(piece: Path, out: list) -> None:
    if not any(p.is_file() for p in (piece / "review").glob("shot*-sheet.jpg")):
        out.append(("FAIL", "review/shot*-sheet.jpg missing"))
    if not (piece / "review" / "phone.jpg").is_file():
        out.append(("FAIL", "review/phone.jpg missing"))
    if not nonempty(piece / "renders" / "share.mp4"):
        out.append(("FAIL", "renders/share.mp4 missing or empty — nothing to review"))
    log = read(piece / "LOG.md")
    heads = list(REVIEW_HEAD.finditer(log))
    if not heads:
        out.append(("FAIL", "LOG.md: no '## vN review' block"))
        return
    block = log[heads[-1].start():]
    if "Checks:" not in block:
        out.append(("FAIL", "LOG.md: review block has no 'Checks:' line"))
    if "Weakest shot:" not in block:
        out.append(("FAIL", "LOG.md: review block has no 'Weakest shot:' line"))


def nonempty(p: Path) -> bool:
    try:
        return p.is_file() and p.stat().st_size > 0
    except OSError:
        return False


def max_retries(piece: Path) -> int:
    cfg = piece.parent.parent / "v2w.config.json"
    try:
        return max(0, int(json.loads(cfg.read_text()).get("max_retries", 2)))
    except (OSError, ValueError, TypeError):
        return 2


def critique_rounds(piece: Path, gate: str) -> list:
    """Only critique/<gate>-r<n>.json; never the .inputs.json stamp sidecars."""
    found = []
    for p in (piece / "critique").glob(f"{gate}-r*.json"):
        m = re.fullmatch(rf"{gate}-r(\d+)\.json", p.name)
        if m:
            found.append((int(m.group(1)), p.name, p))
    return [p for _, _, p in sorted(found)]


def has_critique_rounds(piece: Path) -> bool:
    for p in (piece / "critique").glob("*.json"):
        if re.fullmatch(r"[A-D]-r\d+\.json", p.name):
            return True
    return False


def critique_verdict(piece: Path, gate: str) -> tuple:
    """Return (state, detail); state is pass / missing / unmarked / invalid / stale / fail."""
    rounds = critique_rounds(piece, gate)
    if not rounds:
        return ("missing", f"no critique/{gate}-r*.json")
    latest = rounds[-1]
    try:
        data = json.loads(latest.read_text())
    except ValueError as e:
        return ("invalid", f"{latest.name}: invalid JSON ({e})")
    except OSError as e:
        return ("invalid", f"{latest.name}: cannot read ({e})")
    if not isinstance(data, dict) or not ("schema" in data or "version" in data
                                          or "rubric_version" in data):
        return ("unmarked", f"{latest.name}: no schema/version marker (legacy)")
    if not CRITIQUE_GATE.exists():
        return ("invalid", f"critique_gate.py not found at {CRITIQUE_GATE}")
    n = int(re.search(r"-r(\d+)", latest.name).group(1))
    verify_round = max_retries(piece) + 2
    cmd = [sys.executable, str(CRITIQUE_GATE), str(piece), gate]
    if n >= verify_round:
        cmd.append("--verify")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as e:
        return ("invalid", f"critique_gate.py could not run ({e})")
    state = {0: "pass", 1: "fail", 2: "fail", 3: "invalid", 4: "stale"}.get(r.returncode, "invalid")
    detail = (r.stdout.strip().splitlines() or [f"exit {r.returncode}"])[-1]
    return (state, detail)


def check_critique(piece: Path, gate: str, out: list, legacy: bool, final: bool = False) -> None:
    state, detail = critique_verdict(piece, gate)
    if state == "pass":
        return
    if legacy and state == "missing":
        out.append(("WARN", f"gate {gate}: legacy piece with no critique JSON ({detail})"))
    elif not final and state == "unmarked":
        out.append(("WARN", f"gate {gate}: critique JSON has no schema/version marker ({detail})"))
    else:
        out.append(("FAIL", f"gate {gate}: critique did not pass ({state}: {detail})"))


def check_sample_critique(piece: Path, out: list, legacy: bool) -> None:
    state, detail = critique_verdict(piece, "D")
    if state == "pass":
        return
    if state == "fail" and has_waiver(piece, "D"):
        out.append(("WARN", f"sample approved with D open issues (user waiver): {detail}"))
        return
    if legacy and state == "missing":
        out.append(("WARN", f"sample approved: legacy piece, D critique not recorded ({detail})"))
    else:
        out.append(("FAIL", f"sample approved requires a passing D critique ({state}: {detail})"))


def check_published(piece: Path, out: list) -> None:
    project = piece.parent.parent
    exports = []
    for folder in (project / "exports", piece / "exports"):
        exports += [p for p in folder.glob("*.mp4") if nonempty(p)]
    if not exports:
        out.append(("FAIL", "no non-empty exports/*.mp4 — nothing delivered"))
        return
    publish = piece / "publish.md"
    if not publish.is_file():
        out.append(("FAIL", "publish.md missing — cannot record the published state"))
        return
    text = read(publish) + "\n" + read(piece / "LOG.md")
    status = re.search(
        r"^\s*(?:[-*+]\s+)?(?:\*\*)?Status(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.+)$",
        read(publish), re.M | re.I)
    line = status.group(1).strip() if status else ""
    live = bool(re.search(r"\b(?:published|live)\b", line, re.I) and URL.search(line))
    if live or DERIVED.search(text):
        return
    if status:
        out.append(("FAIL", f"publish.md Status is not published/live with a URL: {line[:60]}"))
    else:
        out.append(("FAIL", "publish.md has no Status line and no recorded derivation from renders/share.mp4"))


def check_artifacts(key: str, piece: Path, out: list) -> None:
    """The files a gate needs, without requiring its critique (also used to preview)."""
    if key == "A":
        check_principle(piece, out)
    elif key == "B":
        check_brief(piece, out)
    elif key == "C":
        check_production(piece, out)
    elif key == "music":
        check_music(piece, out)
    elif key == "review":
        check_review(piece, out)
    elif key == "D":
        if not (piece / "publish.md").is_file():
            out.append(("FAIL", "publish.md missing — critique D has nothing to check"))
    elif key == "sample":
        if not nonempty(piece / "renders" / "share.mp4"):
            out.append(("FAIL", "renders/share.mp4 missing or empty — nothing to review"))
        if not (piece / "publish.md").is_file():
            out.append(("FAIL", "publish.md missing — the sample review needs the post copy"))
    elif key == "published":
        check_published(piece, out)


def check_ticked(key: str, piece: Path, out: list, legacy: bool) -> None:
    check_artifacts(key, piece, out)
    if key == "A":
        check_critique(piece, "A", out, legacy)
    elif key == "B":
        check_critique(piece, "B", out, legacy)
    elif key == "C":
        check_critique(piece, "C", out, legacy)
    elif key == "D":
        check_critique(piece, "D", out, legacy, final=True)
    elif key == "sample":
        check_sample_critique(piece, out, legacy)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    piece = Path(sys.argv[1]).expanduser().resolve()
    status = read(piece / "STATUS.md")
    if not status:
        print(f"{piece.name}: no STATUS.md (created by new_piece.py for v2w pieces)")
        return 2
    g = gates(status)
    print(f"piece: {piece.name}")
    for label, _ in GATES:
        print(f"  [{'x' if g[label] else ' '}] {label}")

    out = []
    ticked = [(i, label, key) for i, (label, key) in enumerate(GATES) if g[label]]
    for i, label, _ in ticked:
        for earlier, ekey in GATES[:i]:
            if g[earlier]:
                continue
            if has_waiver(piece, ekey):
                out.append(("WARN", f"{label} accepted with '{earlier}' open (user waiver)"))
            else:
                out.append(("ILLEGAL", f"{label} ticked while '{earlier}' is open"))

    # A malformed piece.json is always a FAIL, whichever gate is open.
    if (piece / "piece.json").exists():
        try:
            json.loads((piece / "piece.json").read_text())
        except ValueError as e:
            out.append(("FAIL", f"piece.json: invalid JSON ({e})"))
        except OSError as e:
            out.append(("FAIL", f"piece.json: cannot read ({e})"))

    legacy = not has_critique_rounds(piece)
    for _, _, key in ticked:
        check_ticked(key, piece, out, legacy)

    nxt = next((label for label, _ in GATES if not g[label]), None)
    if "TODO" in read(piece / "principle.md") + read(piece / "brief.md"):
        out.append(("INFO", "templates still contain TODO"))
    if nxt:  # preview the files the next gate will need; its critique cannot exist yet
        check_artifacts(dict(GATES)[nxt], piece, out)

    printed = set()
    for level, msg in out:
        if (level, msg) in printed:
            continue
        printed.add((level, msg))
        print(f"  {level:7} {msg}")
    if not nxt:
        print("all gates closed")
    else:
        print(f"next gate: {nxt}  →  {NEXT_STEP[nxt]}")
    return 1 if any(level in ("FAIL", "ILLEGAL") for level, _ in out) else 0


if __name__ == "__main__":
    sys.exit(main())
