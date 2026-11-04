# Rubric C — visual (look + storyboard)

Score 1–5. 5 = nothing to change · 3 = usable with one clear fix · 1 = wrong or missing.
Judge the images at phone size (about 1/3 scale) as well as full size.

| id | item | blocking | what 5 looks like |
|---|---|---|---|
| C1 | Each frame carries its beat | blocking | With the caption covered, the frame still shows that beat's one message. |
| C2 | Hook frame | blocking | The 0–3 s frame shows the conflict at a glance at phone size. |
| C3 | Text placement and size, measured | blocking | All text inside the safe area (top 240 / bottom 420 / right 140 px at 1080×1920 unless piece.json says otherwise); in the rendered 1080-wide frame body text is ≥ 40 px and label text is ≥ 32 px tall (scale the label floor for other widths). Measure pixel heights from the rendered frame, never from the set font size: CJK glyphs often render smaller than the size set. Production records the measurements in `review/text-boxes.json`. |
| C4 | Accurate metaphor | blocking | Shapes, counts and flows match the mechanism (e.g. the number of units drawn matches the number stated); nothing misleading. |
| C5 | Active vs idle | — | What is working is clearly distinguishable from what is idle (contrast, colour, motion cue). |
| C6 | Consistency | — | One palette, line weight and label style across frames. |
| C7 | Borrowed devices | — | Devices taken from the references are adapted to this mechanism, not copied. |

`review/text-boxes.json` holds the measured box and rendered pixel height of every
text element. A legacy piece without it only WARNS; new production records it.
