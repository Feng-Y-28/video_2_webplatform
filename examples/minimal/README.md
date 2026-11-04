# Minimal example

A made-up piece (`cache-miss`) used to show the layout, a filled principle card
and brief, and how critique rounds are judged. It runs **gate A before gate B**,
the order real pieces follow. The snippet copies both JSON files so the gates
can run without spawning a critic subagent; the checks are the same.

```bash
bash setup.sh /tmp/v2w-demo
python3 skills/v2w-orchestra/scripts/new_piece.py /tmp/v2w-demo cache-miss \
  --input "Why does walking a matrix by columns run so much slower than by rows?"
cp examples/minimal/principle.md examples/minimal/brief.md /tmp/v2w-demo/pieces/cache-miss/
cp examples/minimal/critique/A-r1.json examples/minimal/critique/B-r1.json \
  /tmp/v2w-demo/pieces/cache-miss/critique/
python3 skills/v2w-critique/scripts/critique_gate.py /tmp/v2w-demo/pieces/cache-miss A
python3 skills/v2w-critique/scripts/critique_gate.py /tmp/v2w-demo/pieces/cache-miss B
python3 skills/v2w-orchestra/scripts/validate_piece.py /tmp/v2w-demo/pieces/cache-miss
```

Expected output (exit codes in brackets):

```
gate A round 1: mean 4.86
PASS                                                   [0]

gate B round 1: mean 4.44
  takeaway: Memory arrives in blocks, and a column loop throws away most of
  each block, so it waits on far more fetches.
  -> compare with principle.md's mechanism; a mismatch is a FAIL
PASS                                                   [0]

piece: cache-miss
  [ ] A content critique passed
  ...
next gate: A content critique passed  →  v2w-distill → critique A   [0]
```

A low item prints `low <id> = <score>: <fix>`; a failing gate exits 1 while
retries remain and 2 when they are spent. `validate_piece.py` exits 1 when the
artefacts the next gate needs are missing, and 1 on an illegal gate order.

If animate is installed elsewhere, add `--animate-dir <path>` (or set
`ANIMATE_DIR`). To scaffold without animate, add `--allow-missing-template`;
the gate checks above still run, but `validate_piece.py` will stop at gate C
until `piece.json` and `src/` exist.

Expected tree after `new_piece.py` (with animate installed):

```
/tmp/v2w-demo/
├── v2w.config.json   .gitignore   .claude/skills/v2w-* → this repo
├── develop_log/   exports/   third_party/
└── pieces/cache-miss/
    ├── STATUS.md   principle.md   brief.md   LOG.md   piece.json
    ├── source/idea.md
    ├── refs/refcard.md   refs/transcripts/   refs/frames/
    ├── critique/   src/   audio/   review/   renders/
```

Then open the project in Claude Code and say *"run v2w on cache-miss"*.
