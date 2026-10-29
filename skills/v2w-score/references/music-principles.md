# Music principles for explainer shorts

Distilled from common editing advice on short-video platforms and from what
held up in practice. Level figures are rules of thumb.

## 1. Content first

The more important the content, the more restrained the music. For science and
tech explainers, aim for a *light tech* character (airy, light electronic) at
low-to-medium presence. Tech feel does not mean loud.

Order of choice: content type → mood → tempo → how present the music is.

## 2. Match the emotional curve

- Mark the story's nodes first (setup → build → release), then fit the music to them.
- Do not put the climax at the start; leave room to rise.
- A small hit or sound effect on each **knowledge turn** marks the change in pace.
  Use one per turn. Stacking effects sounds cheap.
- **Riser + cut to silence (≈ 0.2–1 s) before the payoff** creates strong
  tension; the silence works as much as the hit does.
- Cutting the sound at the right moment is a fast way to change pace.
- When searching or prompting for a track, describe the shape in time: "45 s,
  quiet first 15 s, light electronic groove building, a clean break near 36 s,
  calm ending".

## 3. Three layers, fixed priority

narrative (voice, action sounds) > ambience (room tone, air) > emotion (music, hits, transitions).

- Silence throughout sounds fake. A very quiet air or ambience bed helps.
- If the music stays at the same level from start to end, the piece sounds flat.
- Many tracks with no layering compete with each other.

## 4. Levels (relative; trust LUFS over meters)

| Layer | With voice | No voice |
|---|---|---|
| Voice | −6 … −3 dB | — |
| SFX | −8 … −20 dB | −8 … −12 dB |
| Music | −18 … −12 dB (duck under voice) | −12 … −8 dB (music is the lead) |
| Ambience | −24 … −18 dB | −24 … −18 dB |

Deliver at **−14 LUFS integrated, true peak ≤ −1 dBTP** (−1.5 dB gives margin).

## 5. Timbre rules for synthesized scores

A score can pass every structural check and still be unbearable. Causes found
in practice, and their fixes:

| Problem | Fix |
|---|---|
| Energy piled at 200–300 Hz, nothing above 3 kHz → muddy, dull | High-pass pads (~220 Hz); add off-beat / 16th hi-hats for top end |
| Detuned pads (±7 cents) → audible wobble | ≤ ±3 cents; sine + triangle |
| Low bass note on every beat for 15 s | One root note per bar, a light kick |
| Same 4-note arpeggio looping ~17 s | Follow the chord progression (e.g. I–V–vi–IV); change voicing |
| ~100+ high sine blips as SFX | One effect per knowledge turn, lower pitch and level |

## 6. Licensing

- Synthesized in code: yours.
- AI models: check the **weights'** licence. Some popular music models are
  non-commercial. Declare AI-generated content where the platform asks.
- Libraries: read each track's licence; some need attribution. Do not reuse
  trending in-app audio from one platform on another.
