# Platform notes

Limits change. Treat these as a starting point and confirm them on the upload page.

## Upload preflight (all platforms)

Run this before touching the creator page.

1. **Size + hash.** Record the byte size and the first 12 characters of the
   sha256 of the file to upload. Both must match `renders/share.mp4`, or the
   file must be a re-encode whose derivation is recorded in `publish.md`.
2. **Cap.** Read `max_upload_mb` from `v2w.config.json`. If it is missing, read
   the live upload-page limit. Never assert a fixed cap: the page is the
   authority, and a remembered number may be stale.
3. **Over the cap.** Two-pass encode to the target bitrate, keep the original,
   re-run the loudness checks on the new file, and record both files, their
   sizes and the hash.
4. Record measured bytes, cap, PASS/FAIL and sha256 in `publish.md`.

## Form filling (all platforms)

- Locate each field by role and accessible name; do not click coordinates.
- After typing, do a **DOM read-back** (`input.value` / `innerText`) and compare
  it with `publish.md`. On a mismatch, stop and fix it; never click Publish.
- Set the cover timestamp and read the selected time back.
- Set AI-content and original / self-made toggles; read back the
  checked / `aria-checked` state.
- Save only **cropped** screenshots (form or dialog). Creator-page account
  chrome — avatar, handle, sidebar, URL bar — is never written to disk.

## Already published

Read Status first. When a URL exists, use the edit page; its final button
updates the live post. Record `updated <date>` beside the original line and
never create a duplicate.

## Topics and campaigns

Select a topic that carries a campaign / activity / event marker only when
`allow_campaign_topics` is `true` in `v2w.config.json`; missing means false.
Log the tag and the attached event in `LOG.md`.

## Xiaohongshu (小红书)

- Upload: creator centre → publish video.
- Title: short (about 20 characters max). A question or a number works well:
  "缓存这么大，为什么程序还是慢？"
- Body: about 1000 characters max; short lines, one idea per line; hashtags at the end.
- Topics: 3–5 field topics (e.g. #FPGA #硬件加速 #计算机体系结构) plus one broad
  one (#科普). Some topics attach the post to an ongoing campaign; select one
  only under the `allow_campaign_topics` rule above, and tell the user.
- Content-type declaration: mark "contains AI-generated content" when music or
  visuals are AI-generated, then read the toggle state back.
- 9:16, 1080×1920 is what the platform calls high-definition.
- Edit page: opening a published note and clicking its final button updates the
  live post; there is no draft step.

## YouTube Shorts

- Vertical, ≤ 3 min. Title up to 100 characters; put `#Shorts` in title or description.
- Description: first line is what shows; add sources as links.
- Altered or synthetic content disclosure applies to realistic content; procedural
  animation usually does not need it, but AI music can be noted in the description.
- The upload page shows its own file-size limit; use it rather than a fixed number.

## Bilibili (B 站)

- Vertical videos go to the vertical feed. Title up to about 80 characters; a partition (分区) is required.
- Declare self-made (自制) vs reposted (转载); add an AI-content note if relevant,
  then read back the selected option.
- Descriptions can hold full source links. Bilibili viewers often check sources, so include them.
- Editing a published entry re-submits it live; check Status before using it.
