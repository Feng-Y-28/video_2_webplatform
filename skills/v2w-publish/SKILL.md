---
name: v2w-publish
description: Stage 7 of the v2w pipeline. Write per-platform post copy (title, body, tags, cover frame, AI-content and simplification declarations) into publish.md before the sample review, and after the user approves the sample, upload as v2w.config.json allows — fill the form only, or publish. Optional translated version. TRIGGER when the v2w-orchestra reaches stage 7 or v2w-review needs publish.md, or the user asks to "write the post / caption / title", "publish / upload piece X", "make an English / Chinese version".
---

# v2w-publish

Output: `<piece>/publish.md`. Gate: **published**.

## Steps

1. **Before the sample review** (called from v2w-review): for each platform in
   `v2w.config.json` → `platforms`, read its section in `references/platforms.md`
   and write `publish.md` from `references/publish-template.md`:
   - **Title** repeats the hook's conflict as a question or number, within the limit.
   - **Body**: 3–6 short lines: conflict, mechanism in one line, the number,
     the verdict, one line naming the simplified example.
   - **Tags**: field tags + one broad tag; no unrelated trending tags.
   - **Cover**: a timestamp whose frame shows the conflict (often the hook).
   - **Declarations**: AI-generated content (music / visuals) if any.
2. Copy `renders/share.mp4` to `<project>/exports/<human-readable name>.mp4`.
3. **Only after `sample approved (user)` is ticked**, act on
   `publish_after_approval`:
   - `none` → stop; publish.md is the deliverable.
   - `fill_form` → in the user's logged-in browser (e.g. claude-in-chrome),
     open the creator page, upload the export, fill every field from publish.md,
     screenshot, and **stop before the final Publish button**. Report what was filled.
   - `publish` → as above, then click Publish. Record the post URL.
4. Record date, platform, status and URL in `publish.md` and `LOG.md`; tick
   `published` when it is live (or when the form is filled and the user posts it).

## Optional: translated version

If the user asks for a translated version, create a sibling piece with
`new_piece.py <project> <name>-<lang> --from <name>` and follow
`references/localize.md`. It goes through review and critique D again, then
gets its own sample review.

## Rules

- Never write account names, cookies or upload URLs with tokens into any file.
- Selecting a tag can attach the post to a platform campaign or event. Note in LOG.md when this happens.
- Platform limits change; confirm them on the live upload page and update
  `references/platforms.md` via the maintaining flow when they differ.
