#!/usr/bin/env python3
"""Compare an original architectural image with an edited result.

Produces one readable report image plus supporting files:

  report.png   원본 | 결과 | 검사 세 장을 나란히 놓고, 허용 영역 안 변경은 노란색,
               허용 영역 밖 변경(누출)은 빨간색으로 채워 표시. 아래에 수치와 판정 힌트.
  overlay.png  결과 위에 원본 윤곽(빨강)과 결과 윤곽(청록)을 겹친 그림. 시점 이동 확인용.
  diff.png     픽셀 차이 흑백 이미지.
  report.json  변경 비율(전체 / 허용 영역 안 / 밖), 윤곽 일치율.

Usage:
    python compare_edit.py original.png result.png [--mask allowed.png] [--out DIR]
                           [--threshold 40] [--edge-threshold 60] [--lang ko|en]

--mask : 흰색(>=128)이 변경 허용 영역, 검정이 보존 영역인 이미지.
비율은 절대 합격선이 아니라 같은 원본에서 나온 결과들을 서로 비교하는 용도다.
Requires Pillow only.
"""
import argparse
import json
import os
import sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

try:  # Windows consoles default to a legacy code page; keep Korean hints readable
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FONT_CANDIDATES = [
    "C:/Windows/Fonts/malgun.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

LABELS = {
    "ko": {"orig": "원본", "res": "결과", "check": "검사 (구조 단위)", "inside": "허용 영역 안 변경",
           "outside": "허용 영역 밖 변경 (누출)", "boundary": "허용 영역 경계",
           "total": "전체 변경", "edge": "구조 윤곽 일치",
           "hint_leak": "허용 영역 밖에 변경이 있습니다. 층수·시점·추가 요소를 확인하세요.",
           "hint_ok": "허용 영역 밖 변경이 거의 없습니다. 층수와 글자를 눈으로 다시 확인하세요.",
           "hint_nomask": "마스크가 없어 안팎을 나누지 못했습니다. 윤곽 겹침으로 시점을 확인하세요.",
           "hint_view": "윤곽 일치율이 낮습니다. 시점이 이동했거나 매스가 변형된 가능성이 있습니다."},
    "en": {"orig": "Original", "res": "Result", "check": "Check (structure level)", "inside": "Changed inside allowed region",
           "outside": "Changed outside allowed region (leak)", "boundary": "Allowed-region boundary",
           "total": "Total changed", "edge": "Structural edge match",
           "hint_leak": "Changes exist outside the allowed region. Check floor count, camera and added elements.",
           "hint_ok": "Almost no change outside the allowed region. Recount floors and check text by eye.",
           "hint_nomask": "No mask given. Use the edge overlay to check the camera.",
           "hint_view": "Edge match is low. The camera may have moved or the mass may be deformed."},
}


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size), True
            except OSError:
                continue
    return ImageFont.load_default(), False


def load_rgb(path, size=None):
    img = Image.open(path).convert("RGB")
    if size and img.size != size:
        img = img.resize(size, Image.LANCZOS)
    return img


def edges(img, threshold):
    gray = ImageOps.autocontrast(img.convert("L"))
    e = gray.filter(ImageFilter.FIND_EDGES)
    return e.point(lambda v: 255 if v >= threshold else 0)


def ratio(binary_img, region=None):
    px = binary_img.tobytes()
    if region is None:
        return sum(1 for v in px if v) / len(px) if px else 0.0
    rpx = region.tobytes()
    total = on = 0
    for v, r in zip(px, rpx):
        if r:
            total += 1
            if v:
                on += 1
    return on / total if total else 0.0


def tint(base, region, color, alpha):
    """Fill `region` (L mask) on `base` with color at alpha."""
    layer = Image.new("RGB", base.size, color)
    a = region.point(lambda v: int(alpha * 255) if v else 0)
    return Image.composite(layer, base, a)


def mask_outline(mask, width=4):
    grown = mask.filter(ImageFilter.MaxFilter(width * 2 + 1))
    return ImageChops.subtract(grown, mask)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("result")
    ap.add_argument("--mask", help="white = allowed-change region")
    ap.add_argument("--out", default="compare")
    ap.add_argument("--threshold", type=int, default=40, help="per-pixel diff threshold 0-255")
    ap.add_argument("--edge-threshold", type=int, default=60)
    ap.add_argument("--lang", choices=["ko", "en"], default="ko")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    orig = load_rgb(args.original)
    res = load_rgb(args.result, orig.size)
    resized = Image.open(args.result).size != orig.size
    W, H = orig.size

    def chan_max_diff(a, b):
        """Per-pixel max over RGB channels, so hue changes at equal brightness (stone -> brick) count."""
        d = ImageChops.difference(a, b)
        r, g, bch = d.split()
        return ImageChops.lighter(ImageChops.lighter(r, g), bch)

    # --- fine difference (pixel level; sensitive to re-render texture noise)
    diff = chan_max_diff(orig, res)
    changed_fine = diff.point(lambda v: 255 if v >= args.threshold else 0)
    diff.save(os.path.join(args.out, "diff.png"))

    # --- coarse difference (structure level). Generative editors re-render the whole
    # image, so leaves, shadows and textures move everywhere. Downsampling + blur
    # averages that out; material swaps, added objects and missing floors survive.
    cw = 256
    ch = max(1, round(H * cw / W))
    def coarse(img):
        return img.resize((cw, ch), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    cdiff = chan_max_diff(coarse(orig), coarse(res))
    changed_coarse_small = cdiff.point(lambda v: 255 if v >= args.threshold else 0)
    changed = changed_coarse_small.resize((W, H), Image.NEAREST)

    # fine edge match (texture sensitive) and structural edge match (coarse, dilated)
    eo, er = edges(orig, args.edge_threshold), edges(res, args.edge_threshold)
    both, union = ImageChops.multiply(eo, er), ImageChops.lighter(eo, er)
    u = ratio(union)
    edge_match = round(ratio(both) / u, 4) if u else None

    sw = 384
    sh = max(1, round(H * sw / W))
    def sedges(img):
        g = ImageOps.autocontrast(img.resize((sw, sh), Image.LANCZOS).convert("L")).filter(ImageFilter.GaussianBlur(0.8))
        e = g.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v >= 40 else 0)
        return e.filter(ImageFilter.MaxFilter(3))
    so, sr = sedges(orig), sedges(res)
    su = ratio(ImageChops.lighter(so, sr))
    structure_match = round(ratio(ImageChops.multiply(so, sr)) / su, 4) if su else None

    dim = Image.blend(res, Image.new("RGB", orig.size, (255, 255, 255)), 0.55)
    overlay = tint(dim, eo, (220, 40, 40), 0.9)
    overlay = tint(overlay, er, (0, 180, 200), 0.9)
    overlay = tint(overlay, both, (255, 255, 255), 0.9)
    overlay.save(os.path.join(args.out, "overlay.png"))

    report = {
        "original": os.path.basename(args.original),
        "result": os.path.basename(args.result),
        "size": [W, H],
        "result_resized_to_match": resized,
        "diff_threshold": args.threshold,
        "changed_ratio_total": round(ratio(changed), 4),
        "changed_ratio_total_fine": round(ratio(changed_fine), 4),
        "structure_match_ratio": structure_match,
        "edge_match_ratio_fine": edge_match,
        "note": "ratios prefixed 'changed_ratio' use the coarse (256px, blurred) difference; '_fine' values are pixel level and inflate on re-rendered images",
    }

    # --- check panel
    check = Image.blend(res, Image.new("RGB", orig.size, (255, 255, 255)), 0.45)
    allowed = preserved = None
    if args.mask:
        mask = Image.open(args.mask).convert("L").resize(orig.size, Image.NEAREST)
        allowed = mask.point(lambda v: 255 if v >= 128 else 0)
        preserved = ImageChops.invert(allowed)
        inside = ImageChops.multiply(changed, allowed)
        leak = ImageChops.multiply(changed, preserved)
        report["changed_ratio_inside_allowed"] = round(ratio(changed, allowed), 4)
        report["changed_ratio_outside_allowed"] = round(ratio(changed, preserved), 4)
        report["changed_ratio_inside_allowed_fine"] = round(ratio(changed_fine, allowed), 4)
        report["changed_ratio_outside_allowed_fine"] = round(ratio(changed_fine, preserved), 4)
        check = tint(check, inside, (250, 200, 40), 0.75)
        check = tint(check, leak, (230, 40, 40), 0.9)
        check = tint(check, mask_outline(allowed), (30, 160, 60), 1.0)
        Image.blend(res, tint(res, leak, (230, 40, 40), 1.0), 0.8).save(os.path.join(args.out, "leak_outside_mask.png"))
    else:
        check = tint(check, changed, (230, 40, 40), 0.9)

    # --- report composite
    lab = LABELS[args.lang]
    gap, pad = 24, 28
    pw = W // 2 if W > 1800 else W  # panel width
    scale = pw / W
    ph = int(H * scale)
    RW = pad * 2 + pw * 3 + gap * 2
    font, has_font = load_font(max(20, RW // 60))
    small, _ = load_font(max(16, RW // 80))
    if not has_font and args.lang == "ko":
        lab = LABELS["en"]
    header = int(RW // 60 * 1.8) + 10
    footer = int(RW // 80 * 1.7) * (7 if args.mask else 5) + 30
    RH = pad * 2 + header + ph + footer
    rep = Image.new("RGB", (RW, RH), (248, 248, 246))
    rd = ImageDraw.Draw(rep)

    panels = [(orig, lab["orig"]), (res, lab["res"]), (check, lab["check"])]
    for i, (img, title) in enumerate(panels):
        x = pad + i * (pw + gap)
        rd.text((x, pad), title, fill=(30, 30, 30), font=font)
        rep.paste(img.resize((pw, ph), Image.LANCZOS), (x, pad + header))
        rd.rectangle([x, pad + header, x + pw - 1, pad + header + ph - 1], outline=(120, 120, 120))

    y = pad + header + ph + 18
    x = pad
    lh = int(small.size * 1.7) if hasattr(small, "size") else 26

    def legend(color, text):
        nonlocal y
        rd.rectangle([x, y + 4, x + lh - 8, y + lh - 4], fill=color, outline=(80, 80, 80))
        rd.text((x + lh, y), text, fill=(40, 40, 40), font=small)
        y += lh

    if args.mask:
        legend((250, 200, 40), f"{lab['inside']}: {report['changed_ratio_inside_allowed']*100:.1f}%")
        legend((230, 40, 40), f"{lab['outside']}: {report['changed_ratio_outside_allowed']*100:.2f}%")
        legend((30, 160, 60), lab["boundary"])
    else:
        legend((230, 40, 40), f"{lab['total']}: {report['changed_ratio_total']*100:.1f}%")
    rd.text((x, y), f"{lab['edge']}: {structure_match*100:.1f}%" if structure_match is not None else f"{lab['edge']}: -",
            fill=(40, 40, 40), font=small)
    y += lh

    hints = []
    if structure_match is not None and structure_match < 0.55:
        hints.append(lab["hint_view"])
    if args.mask:
        hints.append(lab["hint_leak"] if report["changed_ratio_outside_allowed"] > 0.005 else lab["hint_ok"])
    else:
        hints.append(lab["hint_nomask"])
    report["hints"] = hints
    for h in hints:
        rd.text((x, y), "• " + h, fill=(150, 30, 30) if "누출" in h or "outside" in h or "low" in h or "낮" in h else (40, 40, 40), font=small)
        y += lh

    rep.save(os.path.join(args.out, "report.png"))
    with open(os.path.join(args.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nwrote: {args.out}/report.png, overlay.png, diff.png, report.json"
          + (", leak_outside_mask.png" if args.mask else ""))


if __name__ == "__main__":
    main()
