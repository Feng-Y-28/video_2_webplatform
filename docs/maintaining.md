# Maintaining: private workspace → public skill

The intended way to develop v2w is to use it on your own videos and improve
the skills as you go, without publishing the videos or the debugging behind them.

```
<project>/  (private, local git)              video_2_webplatform/  (public)
  develop_log/   raw notes, errors, dead ends   skills/…/references   rules
  pieces/*/LOG.md  per-video decisions   ──▶    shared/pitfalls.md   breakages
  .claude/skills/v2w-* → symlinks ────────────▶ skills/v2w-*         (edited live)
```

Keep the two folders **side by side, not nested**, so that one `git add -A`
can never pick up the other.

## Editing loop

1. Work in `<project>`. The symlinks mean the skills you load there *are* this
   repo's working tree, so a fix you make to a SKILL.md takes effect at once.
2. Commit skill changes in this repo; commit piece/log changes in the project.
   The two repos never see each other's files.

## Promoting a lesson

When a thread in `develop_log/` closes with something reusable:

1. **Is it general?** It should still hold for a different topic, a different
   machine and a different user. If not, it stays private.
2. **Generalise.** Remove paths, names, piece titles, exact timings of a
   real piece. Keep the symptom → cause → fix shape.
3. **Place it.** Tool breakage → `skills/shared/pitfalls.md`. Craft rule →
   the stage's `SKILL.md` or `references/`. Script fix → `scripts/`.
4. **CHANGELOG** entry under *Unreleased*.
5. **Back-pointer** in the private log: `→ promoted to v2w <file> (<version>)`.
6. Review the diff (the pre-commit hook checks paths, emails, keys and your
   local denylist), then commit.

## Privacy hook

`bash setup.sh --dev` turns on `.githooks/pre-commit`. Put your own private
words (username, handles, account names, private repo names) in
`.denylist.local`. That file is git-ignored on purpose: a committed denylist
would publish exactly the words it is meant to protect.

## Releases

Semantic versions in `CHANGELOG.md`. Bump minor for a new stage behaviour or
script, patch for wording and pitfalls.
