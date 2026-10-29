# Maintaining video_2_webplatform

This repo is **public**. It holds the v2w skills only — never a user's videos,
briefs, logs or environment.

## Hard rules for agents editing this repo

1. Do not copy files from a project directory (anything with `pieces/`,
   `develop_log/`, `exports/`) into this repo. Write new text that states the rule.
2. No absolute paths, usernames, emails, account names, API keys, or
   platform post titles from real pieces. Use `<project>/`, `<piece>/`, `~/`.
3. Examples use neutral, made-up topics. They must not let a reader find a
   real published piece.
4. Do not quote third-party posts or notes; restate the principle in your own words.
5. Commit with the hook on (`bash setup.sh --dev`). If it blocks a commit, fix
   the content. Do not use `--no-verify` unless the user explicitly says so.
6. Do not push without the user's explicit OK for that push.

## Promoting a lesson from a private log

See `docs/maintaining.md`. In short: lesson → generalise → put it in the right
skill file (`shared/pitfalls.md` for tool breakage) → CHANGELOG entry → the user
reviews the diff → commit.

## Layout

`skills/v2w-*/SKILL.md` (instructions), `references/` (rules, templates),
`scripts/` (deterministic helpers: standard library + ffmpeg, no network, no LLM).
`skills/shared/` is read by several stages.
