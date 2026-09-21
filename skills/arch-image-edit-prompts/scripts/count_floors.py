#!/usr/bin/env python3
"""Estimate floor count of a building from a vertical strip of a facade image.

The strip should cover one facade column of repeating windows/balconies from the
lowest upper-floor row to the roof line (exclude the pilotis / ground floor and the sky).
The script averages brightness across the strip width, detrends the profile, and
counts dark rows (window bands). It also reports the dominant vertical period from
autocorrelation as a cross-check.

Usage:
    python count_floors.py image.png --strip x0 y0 x1 y1 [--strip ...] [--out annotated.png]

Each --strip is one facade column (pixel box). Several strips can be given in one call.
Results are estimates to be confirmed by eye; they are most reliable on frontal,
evenly lit facades and least reliable on tilted or heavily reflective ones.
Requires Pillow only.
"""
import argparse
import json
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def moving_avg(v, k):
    k = max(1, k)
    out = []
    n = len(v)
    for i in range(n):
        a, b = max(0, i - k // 2), min(n, i + k // 2 + 1)
        out.append(sum(v[a:b]) / (b - a))
    return out


def profile(img, box):
    x0, y0, x1, y1 = box
    g = img.convert("L").crop((x0, y0, x1, y1))
    w, h = g.size
    px = g.tobytes()
    return [sum(px[r * w:(r + 1) * w]) / w for r in range(h)]


def count_dark_rows(p, min_period):
    """Count local minima of a detrended profile, at least min_period apart."""
    base = moving_avg(p, max(min_period * 2, 9))
    d = [a - b for a, b in zip(p, base)]
    d = moving_avg(d, 3)
    thresh = -0.25 * (max(abs(v) for v in d) or 1)
    mins, last = [], -min_period
    for i in range(1, len(d) - 1):
        if d[i] < thresh and d[i] <= d[i - 1] and d[i] <= d[i + 1] and i - last >= min_period:
            mins.append(i)
            last = i
    return mins


def autocorr_period(p, lo, hi):
    mean = sum(p) / len(p)
    z = [v - mean for v in p]
    best, best_lag = -1, None
    for lag in range(lo, min(hi, len(z) // 2)):
        s = sum(z[i] * z[i + lag] for i in range(len(z) - lag))
        if s > best:
            best, best_lag = s, lag
    return best_lag


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--strip", nargs=4, type=int, action="append", metavar=("X0", "Y0", "X1", "Y1"), required=True)
    ap.add_argument("--min-period", type=int, default=12, help="minimum floor height in pixels")
    ap.add_argument("--out", help="annotated PNG path")
    args = ap.parse_args()

    img = Image.open(args.image).convert("RGB")
    ann = img.copy()
    d = ImageDraw.Draw(ann)
    results = []
    for i, box in enumerate(args.strip, 1):
        p = profile(img, box)
        mins = count_dark_rows(p, args.min_period)
        lag = autocorr_period(p, args.min_period, max(args.min_period + 1, len(p) // 3))
        by_period = round(len(p) / lag, 1) if lag else None
        results.append({"strip": i, "box": box, "dark_rows": len(mins), "period_px": lag, "height_over_period": by_period})
        x0, y0, x1, y1 = box
        d.rectangle(box, outline=(255, 60, 60), width=3)
        for m in mins:
            d.line([x0, y0 + m, x1, y0 + m], fill=(0, 220, 255), width=2)
        d.text((x0 + 4, y0 - 18 if y0 > 20 else y1 + 4), f"#{i}: {len(mins)} rows / {by_period} by period", fill=(255, 60, 60))

    if args.out:
        ann.save(args.out)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
