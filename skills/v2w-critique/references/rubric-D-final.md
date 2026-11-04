# Rubric D — final cut (before the sample review)

Score 1–5. 5 = nothing to change · 3 = usable with one clear fix · 1 = wrong or missing.

Critique JSON carries `"schema": 2`. A schema-1 file without D8 is a legacy
critique and only WARNS; a schema-2 file without D8 FAILs.

| id | item | blocking | what 5 looks like |
|---|---|---|---|
| D1 | Machine checks | blocking | animate review: cuts, story arc ≥ 4/5, text, sound all PASS; every WARN has a written reason in LOG.md. |
| D2 | Numbers on screen | blocking | Every number visible in the sheets matches brief.md Claims + sources. |
| D3 | Sound measurements | blocking | Measured on the final `renders/share.mp4` after the last edit: −14 ± 1 LUFS, TP ≤ −1 dBTP, loudest 100 ms in the payoff act, and every `band_energy.py` WARN has a written reason in `LOG.md`; an unexplained WARN fails. This deliberately repeats the music gate on the delivered file. |
| D4 | Post copy | blocking | publish.md matches the video, declares simplified examples and AI-generated content. |
| D5 | Arc visible | — | The contact sheets show build → payoff → close; the payoff shot is visually distinct. |
| D6 | Weakest shot | — | The shot named weakest in LOG.md is still clear; no stretch where nothing changes for > 3 s (except an agreed ending). |
| D7 | Phone read | — | `phone.jpg`: captions readable, nothing under the platform UI. |
| D8 | Changed after gate C | blocking | Any picture, label or number changed after the gate C tick was re-critiqued with gate C, or recorded as an 'After C:' line in the latest `LOG.md` review block. |
