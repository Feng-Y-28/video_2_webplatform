# ACE-Step tracks

ACE-Step 1.5 can be called through the `tools/music_gen.py` client in
[digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit).
Clone it into `<project>/third_party/` (git-ignored), make a venv with
`requests` and `python-dotenv`, and put the API key in that folder's `.env`
(`chmod 600`). **Only call it when `v2w.config.json` → `allow_hosted_music_api` is true**: the prompt goes
to a hosted API under the user's key.

## Prompt

Describe the shape in time and give the structure tags, tempo and key that
match the piece:

```
python tools/music_gen.py \
  --prompt "Minimal light electronic background for a calm science explainer; airy pads, soft plucks, gentle hi-hats; builds from 8 s, peaks mid-way, calm resolve" \
  --duration 45 --bpm 120 --key "D Major" -o <piece>/audio/take1_raw.mp3
```

## What to expect

- One 45 s take takes about 10–15 s to generate.
- Takes **resolve on their own** (often around 40 s for a 45 s request) and
  ignore requested break/climax times. Choose by shape, then automate.
- `--variations N` may return a single file on the hosted API. Loop with
  different seeds or `--infer-method` instead.
- `--repaint --repaint-start/--repaint-end` can regenerate one section;
  results vary — re-measure the result like any take.
- Hosted endpoints may return 5xx under load; retry later, do not loop.

## Licence

Check the licence of the model weights you call. Mark the post as containing
AI-generated content where the platform offers it.
