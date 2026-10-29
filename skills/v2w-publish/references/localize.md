# Translated version

Same story, look, music and timing; only the words change. If the story needs
to change for another audience, start a new piece from v2w-distill.

1. `new_piece.py <project> <name>-<lang> --from <name>` (copies source; gates open).
2. List every on-screen string (grep the scene files for text draws and the
   `TIMELINE` captions) as a source → target table in the new piece's LOG.md.
3. Translate with the rules below; numbers and units stay identical to the claims.
4. Build, export, `mix.sh` if present, v2w-review, critique D, sample review.
5. Write this language's post copy fresh. Platform norms differ, so do not just
   translate the other post.

## Rules for on-screen text

1. **Fit first.** On-screen text has the slot the original had. If the
   translation is longer, shorten the wording before you shrink the font.
   Abbreviate units the way engineers do (`B/cyc`, `GB/s`, `ops/B`).
2. **Hook ≤ 23 characters** in CJK, roughly ≤ 6 words in English.
3. **Verdict lines get rewritten, not translated.** Find the idiomatic
   equivalent: "慢在等数据，不在算" → "It waits for data, not for math".
4. Keep technical terms as the field writes them (DSP, BRAM, HBM, GEMM). Do
   not translate an acronym into a phrase that nobody uses.
5. Numbers, units and ratios stay exactly as in the claims table. Check the
   decimal separator and thousands separator.
6. Fonts: the build may not embed web fonts; check that the target script
   renders in the system font used by the style (CJK ↔ Latin fallback).
7. Re-check every caption against the phone safe area; English often runs
   wider than Chinese for the same meaning.
