# Minimal example

A made-up piece (`cache-miss`) used to show the layout, a filled principle card
and brief, and how a critique round is judged.

```bash
bash setup.sh /tmp/v2w-demo
python3 skills/v2w-orchestra/scripts/new_piece.py /tmp/v2w-demo cache-miss \
  --input "Why does walking a matrix by columns run so much slower than by rows?"
cp examples/minimal/principle.md examples/minimal/brief.md /tmp/v2w-demo/pieces/cache-miss/
cp examples/minimal/critique/B-r1.json /tmp/v2w-demo/pieces/cache-miss/critique/
python3 skills/v2w-critique/scripts/critique_gate.py /tmp/v2w-demo/pieces/cache-miss B
python3 skills/v2w-orchestra/scripts/validate_piece.py /tmp/v2w-demo/pieces/cache-miss
```

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
