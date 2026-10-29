# cache-miss — brief

<!-- A made-up example. Not a published piece. -->

## Spec
- 40 s · 9:16 · 24 fps · 120 BPM · isometric · beat-cut

## Audience
- Undergraduates who can write a nested loop; never heard of a cache line.
- Term policy: caption says what a thing *does*, then its name as a small label; ≤ 4 terms.

## Hook
- 0–3 s line: "Same loop. 16× the fetches."
- Alternatives considered: "Stop looping by columns." / "My loop was slow for one silly reason."
- Payoff that resolves it, and when: 27 s — the column walk uses 1 of 16 numbers per fetch.

## Explanation order
1. Two identical loops, two timers → why is one slow?
2. Memory arrives in 64 B blocks → what does each loop do with a block?
3. Row walk uses all 16; column walk uses 1 → how much extra fetching?
4. 16× the blocks, each a long wait → payoff.
- Why this order: references usually explain caches first and lose viewers by 10 s; starting from the two timers keeps the conflict in front.

## Beats
| t (s) | shot | one message | on-screen text |
|---|---|---|---|
| 0–3 | hook | two loops, two timers | Same loop. 16× the fetches. |
| 3–7 | target | you'd blame the math | Is it the math? |
| 7–15 | evidence | memory comes in blocks | fetched 64 B at a time — cache line |
| 15–27 | evidence | row uses the block, column wastes it | uses 16 of 16 / uses 1 of 16 |
| 27–33 | turn | the slow loop is waiting | waiting, not computing |
| 33–40 | line | order loops along memory | Walk memory the way it's laid out. |

## Claims + sources
- Cache line is 64 B on mainstream x86 — Intel Optimization Reference Manual https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html
- 16 floats per line; 16 of 16 vs 1 of 16 — simplified example: 32-bit floats, aligned rows
- Long wait per fetch — simplified example: no cycle count shown on screen

## Sound plan
- Source: synthesized score
- Arc: build → peak → payoff hit at 27 s → goodbye
