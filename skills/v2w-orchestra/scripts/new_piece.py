#!/usr/bin/env python3
"""Start a piece at <project>/pieces/<name>/.

Fresh piece: copies piece.json + src/ from an animate template, then adds the
v2w layer (STATUS.md, principle.md, refs/refcard.md, brief.md, LOG.md and the
source/ refs/ critique/ audio/ review/ renders/ folders). Never overwrites a file.

Sibling piece (--from): copies another piece's source for a translation or
variant (renders and critiques are not copied; gates start open).

    python3 new_piece.py <project> <name> [--input paper.pdf|"idea text"] [--template beat-cut]
    python3 new_piece.py <project> <name>-en --from <name>
"""
import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
DEFAULT_ANIMATE = Path(os.environ.get("ANIMATE_DIR", "~/.claude/skills/animate")).expanduser()
DIRS = ["source", "refs/transcripts", "refs/frames", "critique", "audio", "review", "renders"]
LAYER = {  # template -> path in piece
    "STATUS.md": "STATUS.md",
    "principle.md": "principle.md",
    "refcard.md": "refs/refcard.md",
    "brief.md": "brief.md",
    "LOG.md": "LOG.md",
}
SIBLING_ITEMS = ["principle.md", "refs/refcard.md", "brief.md", "LOG.md", "piece.json",
                 "src", "audio", "mix.sh", "voice", "assets", "source"]


def animate_template(animate: Path, template: str) -> Path:
    if template.startswith("style:"):
        return animate / "styles" / template.split(":", 1)[1] / "demo"
    return animate / "templates" / template


def copy_missing(src: Path, dst: Path) -> None:
    if src.is_dir():
        for item in src.rglob("*"):
            target = dst / item.relative_to(src)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
    elif src.exists() and not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def rename_piece_json(piece: Path) -> None:
    pj = piece / "piece.json"
    if pj.exists():
        data = json.loads(pj.read_text())
        data["name"] = piece.name
        pj.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_layer(piece: Path, input_desc: str, only=None) -> None:
    today = datetime.date.today().isoformat()
    for tpl, out in LAYER.items():
        if only and out not in only:
            continue
        dst = piece / out
        if dst.exists():
            continue
        text = (TEMPLATES / tpl).read_text()
        text = text.replace("{{name}}", piece.name).replace("{{date}}", today).replace("{{input}}", input_desc)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text)
        print(f"  new  {out}")


def place_input(piece: Path, value: str) -> str:
    if not value:
        return "TODO"
    path = Path(value).expanduser()
    if path.is_file():
        dst = piece / "source" / path.name
        if not dst.exists():
            shutil.copy2(path, dst)
        return f"source/{path.name}"
    if value.startswith(("http://", "https://", "arxiv:", "doi:")) or value[:4].isdigit():
        return value
    idea = piece / "source" / "idea.md"
    if not idea.exists():
        idea.write_text(value.strip() + "\n")
    return "idea: source/idea.md"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("name")
    ap.add_argument("--input", default="", help="paper file, arXiv id / DOI / URL, or the idea as text")
    ap.add_argument("--template", default="beat-cut", help="animate template: beat-cut | piece | style:<name>")
    ap.add_argument("--from", dest="base", help="copy source from an existing piece (translation / variant)")
    ap.add_argument("--animate-dir", type=Path, default=DEFAULT_ANIMATE)
    args = ap.parse_args()

    project = args.project.expanduser().resolve()
    if not (project / "pieces").is_dir():
        sys.exit(f"{project} has no pieces/ — run init_project.py first")
    piece = project / "pieces" / args.name
    for d in DIRS:
        (piece / d).mkdir(parents=True, exist_ok=True)
    print(f"piece: {piece}")

    if args.base:
        base = project / "pieces" / args.base
        if not base.is_dir():
            sys.exit(f"--from piece not found: {base}")
        for item in SIBLING_ITEMS:
            copy_missing(base / item, piece / item)
        rename_piece_json(piece)
        write_layer(piece, f"sibling of {args.base}", only={"STATUS.md"})
        with (piece / "LOG.md").open("a") as f:
            f.write(f"\n## Sibling of {args.base} ({datetime.date.today().isoformat()})\n"
                    f"- Copied source from `{args.base}`; renders and critiques not copied.\n")
        print(f"  copied source from {args.base}")
    else:
        src = animate_template(args.animate_dir, args.template)
        if src.is_dir():
            copy_missing(src / "piece.json", piece / "piece.json")
            copy_missing(src / "src", piece / "src")
            rename_piece_json(piece)
            print(f"  animate template: {src}")
        else:
            print(f"  ! animate template not found at {src}; piece.json/src/ left for the animate skill")
        write_layer(piece, place_input(piece, args.input))
    print("next: v2w-distill (principle.md), then validate_piece.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
