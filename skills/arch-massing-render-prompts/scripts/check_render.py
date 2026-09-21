# -*- coding: utf-8 -*-
"""Overlay a massing capture's outlines on a generated render and cut zoomed strips for counting floors.

The image model re-draws everything, so the useful check is structural: do the building corners,
roof lines, site boundary and roads of the render sit where the capture drew them, and does each
facade show as many window rows as the capture has floor lines. This script prepares the pictures
for that check; the judgement is made by eye.

Usage:
    python check_render.py capture.png render.png --out check/
        [--edges capture_edges.png]            # pre-made white-on-black outline image (optional)
        [--box  A 540 340 960 820 ...]         # region to zoom (name x0 y0 x1 y1), repeatable
        [--strip A 640 430 760 800 ...]        # facade strip for floor counting, repeatable
        [--zoom 2] [--strip-zoom 3] [--lang ko|en]

Outputs in --out:
    overlay.jpg              render with the capture outlines in red
    overlay_zoom_<NAME>.jpg  each --box region of the overlay, enlarged
    strip_<NAME>.jpg         each --strip region, capture and render side by side, enlarged
    check.json               boxes, strips, sizes and the edge source used

Requires Pillow only. Renders of a different size are resized to the capture size (noted in check.json);
if the aspect ratio differs the camera check is not meaningful.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

MSG = {
    "ko": {
        "resized": "렌더 크기 {} → 캡처 크기 {}로 맞춤. 비율이 다르면 카메라 판정은 의미가 없다.",
        "edges_made": "캡처에서 윤곽선 추출 (임계 {}).",
        "edges_file": "윤곽선 파일 사용: {}",
        "done": "저장: {}",
    },
    "en": {
        "resized": "Render {} resized to capture size {}. If the aspect ratio differs, the camera check is not meaningful.",
        "edges_made": "Outlines extracted from the capture (threshold {}).",
        "edges_file": "Using outline file: {}",
        "done": "Saved: {}",
    },
}


def parse_regions(items, what):
    out = []
    for it in items or []:
        if len(it) != 5:
            raise SystemExit(f"--{what} needs NAME x0 y0 x1 y1, got {it}")
        name = it[0]
        x0, y0, x1, y1 = (int(v) for v in it[1:])
        if x1 <= x0 or y1 <= y0:
            raise SystemExit(f"--{what} {name}: x1,y1 must exceed x0,y0")
        out.append((name, (x0, y0, x1, y1)))
    return out


def extract_edges(capture, threshold, dilate):
    g = capture.convert("L").filter(ImageFilter.FIND_EDGES)
    g = g.point(lambda v: 255 if v > threshold else 0)
    if dilate:
        g = g.filter(ImageFilter.MaxFilter(3))
    return g


def overlay(render, edges, color=(255, 0, 0)):
    red = Image.new("RGB", render.size, color)
    return Image.composite(red, render, edges)


def enlarge(im, k):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


def side_by_side(images, gap=10):
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    h = max(i.height for i in images)
    out = Image.new("RGB", (w, h), "white")
    x = 0
    for i in images:
        out.paste(i, (x, 0))
        x += i.width + gap
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("capture")
    ap.add_argument("render")
    ap.add_argument("--out", default="check")
    ap.add_argument("--edges", help="white-on-black outline image of the capture")
    ap.add_argument("--edge-threshold", type=int, default=40)
    ap.add_argument("--edge-dilate", action="store_true", help="thicken extracted outlines by one pixel")
    ap.add_argument("--box", nargs=5, action="append", metavar=("NAME", "X0", "Y0", "X1", "Y1"))
    ap.add_argument("--strip", nargs=5, action="append", metavar=("NAME", "X0", "Y0", "X1", "Y1"))
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--strip-zoom", type=int, default=3)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--lang", choices=["ko", "en"], default="ko")
    a = ap.parse_args()
    m = MSG[a.lang]

    os.makedirs(a.out, exist_ok=True)
    cap = Image.open(a.capture).convert("RGB")
    ren = Image.open(a.render).convert("RGB")
    info = {"capture": os.path.basename(a.capture), "render": os.path.basename(a.render),
            "capture_size": cap.size, "render_size": ren.size, "resized": False}
    if ren.size != cap.size:
        print(m["resized"].format(ren.size, cap.size))
        ren = ren.resize(cap.size, Image.LANCZOS)
        info["resized"] = True

    if a.edges:
        edges = Image.open(a.edges).convert("L").resize(cap.size)
        edges = edges.point(lambda v: 255 if v > 128 else 0)
        info["edges"] = os.path.basename(a.edges)
        print(m["edges_file"].format(a.edges))
    else:
        edges = extract_edges(cap, a.edge_threshold, a.edge_dilate)
        info["edges"] = f"extracted(threshold={a.edge_threshold})"
        print(m["edges_made"].format(a.edge_threshold))

    ov = overlay(ren, edges)
    p = os.path.join(a.out, "overlay.jpg")
    ov.save(p, quality=a.quality)
    saved = [p]

    boxes = parse_regions(a.box, "box")
    for name, bx in boxes:
        p = os.path.join(a.out, f"overlay_zoom_{name}.jpg")
        enlarge(ov.crop(bx), a.zoom).save(p, quality=a.quality)
        saved.append(p)

    strips = parse_regions(a.strip, "strip")
    for name, bx in strips:
        p = os.path.join(a.out, f"strip_{name}.jpg")
        side_by_side([enlarge(cap.crop(bx), a.strip_zoom), enlarge(ren.crop(bx), a.strip_zoom)]).save(p, quality=a.quality)
        saved.append(p)

    info["boxes"] = {n: b for n, b in boxes}
    info["strips"] = {n: b for n, b in strips}
    info["outputs"] = [os.path.basename(s) for s in saved]
    with open(os.path.join(a.out, "check.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(m["done"].format(", ".join(os.path.basename(s) for s in saved) + ", check.json"))


if __name__ == "__main__":
    main()
