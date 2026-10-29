#!/usr/bin/env python3
"""Band energy and per-segment loudness shape for a mix or a track.

Heuristics, not truth: they flag what a structure-and-loudness review misses
(low-mid mud, a thin top end). Thresholds were calibrated on a handful of
mixes: a produced track sits at high-mid ~ -17..-19 dB and lowmid-mid ~ 0 dB;
a muddy synthesized score showed lowmid-mid +2.6 dB; thin synthesized scores
-21..-23 dB high-mid. Repetition (a loop that goes on too long) is NOT detected —
energy envelopes cannot see pitch. Always follow with a human listen.

    python3 band_energy.py <audio> [--segments 0,8,15,27,32,45]

Needs ffmpeg on PATH. Standard library only.
"""
import argparse
import array
import math
import subprocess
import sys

SR = 32000
BANDS = {  # name: ffmpeg filter chain
    "sub <120": "lowpass=f=120",
    "lowmid 150-350": "highpass=f=150,lowpass=f=350",
    "mid 350-2k": "highpass=f=350,lowpass=f=2000",
    "high >3k": "highpass=f=3000",
}


def decode(path: str, filt: str) -> array.array:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path,
           "-af", filt, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    a = array.array("h")
    a.frombytes(raw[: len(raw) // 2 * 2])
    if sys.byteorder == "big":
        a.byteswap()
    return a


def rms_db(x, lo: int, hi: int) -> float:
    n = max(1, hi - lo)
    s = 0.0
    for v in x[lo:hi]:
        s += v * v
    r = math.sqrt(s / n) / 32768.0
    return 20 * math.log10(r) if r > 0 else -120.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--segments", help="comma-separated boundaries in seconds, e.g. 0,8,15,27,45")
    args = ap.parse_args()

    full = decode(args.audio, "anull")
    dur = len(full) / SR
    bands = {k: decode(args.audio, f) for k, f in BANDS.items()}
    print(f"{args.audio}: {dur:.1f} s")

    bounds = [float(b) for b in args.segments.split(",")] if args.segments else [0.0, dur]
    print("\nsegment        all   " + "  ".join(f"{k:>14}" for k in BANDS))
    for a, b in zip(bounds, bounds[1:]):
        lo, hi = int(a * SR), int(min(b, dur) * SR)
        row = [rms_db(full, lo, hi)] + [rms_db(bands[k], lo, hi) for k in BANDS]
        print(f"{a:5.1f}-{b:5.1f}  {row[0]:6.1f}  " + "  ".join(f"{v:14.1f}" for v in row[1:]))

    whole = {k: rms_db(v, 0, len(v)) for k, v in bands.items()}
    mud = whole["lowmid 150-350"] - whole["mid 350-2k"]
    top = whole["high >3k"] - whole["mid 350-2k"]
    print(f"\nwhole: lowmid-mid {mud:+.1f} dB, high-mid {top:+.1f} dB")
    warns = []
    if mud > 1.5:
        warns.append(f"low-mid mud: 150-350 Hz is {mud:+.1f} dB vs 350-2k (produced tracks ~0)")
    if top < -20:
        warns.append(f"thin top end: >3 kHz is {top:+.1f} dB vs 350-2k (produced tracks ~-17..-19)")

    print()
    for w in warns:
        print("WARN", w)
    if not warns:
        print("no warnings (heuristic)")
    print("repetition is not checked — a human must listen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
