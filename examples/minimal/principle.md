# cache-miss — principle

<!-- A made-up example. Not a published piece. -->

## Source
- Input: idea: "Why does walking a matrix by columns run so much slower than by rows?"
- Reader / notes: source/idea.md

## Audience
- Undergraduates who can write a nested loop; have never heard of a cache line.

## Problem
Two loops do exactly the same arithmetic, yet one takes many times longer.

## Mechanism
1. Memory is fetched in fixed blocks (cache lines), not one number at a time.
2. A row walk uses every number in each block; a column walk uses one and jumps away.
3. So the column walk fetches far more blocks and spends most of its time waiting.

## Proof numbers
- Cache line = 64 B on mainstream x86 — Intel 64 and IA-32 Architectures Optimization Reference Manual https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html
- 4 B per float → 16 floats per line — simplified example: 32-bit floats, aligned rows
- Row walk uses 16/16 of each line, column walk 1/16 — derived
- ~100-cycle wait per miss — simplified example: order of magnitude, varies by system

## Derivation
Column walk on a large row-major matrix: one useful float per 64 B fetch → 16× more
lines fetched than the row walk for the same work.

## Left out
- Prefetchers, TLBs, cache levels, associativity — true, not needed for the conflict.
