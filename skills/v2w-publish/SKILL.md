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
   - **Declarations**: AI-generated content (music / visuals) if any, and the
     original / self-made claim.
2. **Export preflight** (before any upload):
   - Compare the file you are about to upload with the cut: the **sha256**
     (first 12 hex characters) and the byte size must match
     `renders/share.mp4`. A re-encode is allowed only when `publish.md` records
     how it was derived (filter and target bitrate).
   - Read the cap from `max_upload_mb` in `v2w.config.json`; when that key is
     absent, read the **live upload-page limit**. Never assume an undocumented
     fixed cap and never copy a remembered number into this skill.
   - Over the cap: encode in **two passes** to the target bitrate, keep the
     original file, and **re-run the loudness checks** on the encoded file.
     Record both files and their sizes.
   - Record measured bytes, the cap, PASS/FAIL and the sha256 in `publish.md`.
3. Copy `renders/share.mp4` (or the recorded encode) to
   `<project>/exports/<human-readable name>.mp4`.
4. **Only after `sample approved (user)` is ticked**, act on
   `publish_after_approval`:
   - `none` → stop; publish.md is the deliverable.
   - `fill_form` → in the user's logged-in browser (e.g. claude-in-chrome),
     open the creator page, upload the export, and fill every field from
     `publish.md`:
     * Locate fields by **role and accessible name**, never by coordinates.
     * After each field, do a **DOM read-back** (`input.value`, `innerText`)
       and compare it with `publish.md`. On a mismatch, fix the field or stop;
       never click the final button with a value that differs.
     * Set the **cover timestamp**, then read back the selected time.
     * Set the **AI-content and original / self-made toggles**, then read back
       the checked / `aria-checked` state.
     * Screenshot, **cropped** to the form or dialog: creator-page account
       chrome (avatar, handle, sidebar, URL bar) must never be saved.
     Then **stop before the final Publish button**. Report what was filled.
   - `publish` → as above, then click Publish. Record the post URL.
5. Record date, platform, status and URL in `publish.md` and `LOG.md`; tick
   `published` when it is live (or when the form is filled and the user posts it).

## Updating an already-published note

- Read the note's **Status** first. If a post URL is recorded, open that note's
  edit page; never create a duplicate note.
- On the edit page the final button **updates the live post**. Treat Publish
  there as "update the live post", and only do it when the user asked for an
  update.
- Record `updated <date>` beside the original published line; keep the
  original date and URL, and log which fields changed.

## Campaign and activity topics

- A topic or tag that carries a campaign / activity / event marker may attach
  the note to that event. Select one only when `allow_campaign_topics` is
  `true` in `v2w.config.json`; **missing means false**.
- When one is used, log the tag and the attached event in `LOG.md`.

## Optional: translated version

If the user asks for a translated version, create a sibling piece with
`new_piece.py <project> <name>-<lang> --from <name>` and follow
`references/localize.md`. It goes through review and critique D again, then
gets its own sample review.

## Rules

- Never write account names, cookies or upload URLs with tokens into any file.
- Fill by role/name locator and verify by DOM value. A screenshot is evidence,
  not verification.
- Crop every saved screenshot so account chrome is out of frame.
- Only a `max_upload_mb` from the config or the live page limit counts.
- Platform limits change; confirm them on the live upload page and update
  `references/platforms.md` via the maintaining flow when they differ.
