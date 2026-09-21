#!/usr/bin/env python3
"""Simple color statistics for named rectangular regions of one or more images.

Used in the evidence gallery to back numbers such as "brick-colored pixels in the
curtain-wall area" or "mean saturation of the center building". It is deliberately
crude: a pixel is 'brick-like' when R > G + 15 and G > B, 'glass-like' when B is the
largest channel. Use it to compare results from the same original, not as an
absolute measurement.

Usage:
    python region_stats.py --box NAME x0 y0 x1 y1 [--box ...] image1 [image2 ...]

Example (gallery cases 01/03):
    python region_stats.py --box curtain 800 160 940 600 --box center 700 140 1085 632 \
        cases/00_base/base.jpg cases/01_A_material_swap/result.jpg cases/03_control_weak_prompt/result.jpg

Requires Pillow only.
"""
import argparse
import json
import sys

try:
    from PIL import Image, ImageStat
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def stats(img, box):
    crop = img.crop(box)
    px = crop.tobytes()
    n = len(px) // 3
    brick = glass = 0
    for i in range(0, len(px), 3):
        r, g, b = px[i], px[i + 1], px[i + 2]
        if r > g + 15 and g > b:
            brick += 1
        if b >= r and b >= g:
            glass += 1
    mean_rgb = [round(v) for v in ImageStat.Stat(crop).mean]
    sat = round(ImageStat.Stat(crop.convert("HSV").split()[1]).mean[0])
    lum = round(ImageStat.Stat(crop.convert("L")).mean[0])
    return {"mean_rgb": mean_rgb, "mean_saturation_0_255": sat, "mean_luminance_0_255": lum,
            "brick_like_pct": round(100 * brick / n, 1), "glass_like_pct": round(100 * glass / n, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--box", nargs=5, action="append", metavar=("NAME", "X0", "Y0", "X1", "Y1"), required=True)
    args = ap.parse_args()
    out = {}
    for path in args.images:
        img = Image.open(path).convert("RGB")
        out[path] = {name: stats(img, tuple(int(v) for v in coords)) for name, *coords in args.box}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
