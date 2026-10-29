# Architecture

```
                         v2w-orchestra  (directories, gates, order, config)
                                │
 distill ─A─ reference ── script ─B─ production ─C─ score ─M─ review ─D─ [sample: user] ─ publish
    │            │                       │            │          │                          │
 nature-reader  browser +             animate      animate    animate review            browser
 deep-research  transcript skill      anatomy      ACE-Step   band_energy.py
                                │
                         v2w-critique  (fresh subagent + rubric + critique_gate.py)
                         shared/  claims-and-sources · pitfalls
```

## Design choices

- **Autonomous until the sample.** Every place a human used to approve
  (content, script, look, storyboard, music) is a rubric critique or a machine
  check. The user's single review then deals with taste, not basic errors.
- **Independent critics.** A critique runs in a fresh subagent that receives
  only the artefact, the rubric and an output schema, never the author's
  reasoning or the piece's history. A deterministic script turns its JSON
  into PASS/FAIL so that the bar cannot drift.
- **Bounded retries.** Each gate gets at most 2 automatic retries; after that
  the pipeline carries the open issues to the sample review instead of looping.
- **Thin wrappers over existing skills.** Paper reading, fact checking,
  transcripts, rendering, review metrics and music generation belong to other
  skills and tools. v2w adds the order, the rubrics and the glue that a
  technical explainer needs.
- **Standing consent.** Outward actions (browsing, hosted APIs, uploading,
  publishing) are decided once in `v2w.config.json`; publishing additionally
  waits for the approved sample.
- **Deterministic scripts only.** Scripts never call an LLM or the network.
