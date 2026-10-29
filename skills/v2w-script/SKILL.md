---
name: v2w-script
description: Stage 3 of the v2w pipeline. Turn the principle card and the reference card into the video script — conflict and hook, explanation order, one-message-per-beat table, on-screen claims with sources, sound plan — in brief.md, then send it to critique B. TRIGGER when the v2w-orchestra reaches stage 3, or the user asks to "write the script / brief / storyboard text", "find the hook", "decide the explanation order" for a v2w piece.
---

# v2w-script

Input: `principle.md` (gate A passed), `refs/refcard.md`.
Output: `<piece>/brief.md`. Gate: **B script critique passed**.

## Steps

1. **Conflict → hook.** From principle.md's problem, draft three hooks: one
   denial, one number, one confession (`references/short-video-structure.md`
   §Hooks). Pick the one that is most visual and needs the fewest words. Log
   the other two in LOG.md.
2. **Explanation order.** Start from the order most references use
   (refcard → Synthesis). Change it only for a stated reason, e.g. settling
   the confusion the references leave open. Each step must answer the
   question the previous step raised.
3. **Beats table.** One message per shot; something new every 2–3 s; no peak
   shot > 4 s; payoff at about 2/3–3/4 of the runtime, *computed* on screen
   from the proof numbers; closing line that restates the mechanism.
4. **Claims + sources.** Copy every number that will appear on screen from
   principle.md with its source. A number that is not in principle.md goes
   back to v2w-distill first.
5. **Term policy.** Caption first says what a thing does, then the name as a
   small label. ≤ 4 terms.
6. **Sound plan.** Synthesized score (exact sync, default) or an external
   track (only if `allow_hosted_music_api` or a track was supplied). Mark the
   payoff hit time.
7. Run **v2w-critique** gate `B`; fix → re-run (≤ 2 retries). Tick
   `B script critique passed`.

## Rules

- Do not include anything the conflict does not need, even if it is true and
  interesting. A list of a device's parts gives the viewer nothing to follow.
- "X is the bottleneck" is not a payoff. Showing X starving is.
- Reference videos shape the order and the devices, never the wording.
