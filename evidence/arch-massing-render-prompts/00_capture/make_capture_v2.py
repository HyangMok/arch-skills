# -*- coding: utf-8 -*-
"""가상 매스 뷰포트 캡처 생성기 v2: 층수 보존 대책을 넣은 캡처.

make_capture.py와 같은 배치·카메라에 네 가지 대책을 더한다.
  1. 층 분절선을 굵고 어둡게 (1px 회색 → 3px 진회색)
  2. 동마다 지붕 위에 층수 라벨 ("15F")
  3. C 동을 L자 한 덩어리로 (내부 모서리선 없음)
  4. 타워 D 지붕에 옥탑 박스 (지붕선 고정용)
대책이 동마다 다르므로 결과를 동별로 가려 볼 수 있다. 실제 프로젝트와 무관한 가상 배치.

실행: python make_capture_v2.py → capture_v2.png, capture_v2_edges.png(라벨 제외), spec_v2.json
Pillow만 필요.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1536, 1024
FH = 3.1

# 건물: 바닥 다각형(반시계), 층수, 필로티, 라벨 위치(지붕 중심)
BUILDINGS = [
    {"name": "A", "poly": [(0, 0), (62, 0), (62, 16), (0, 16)], "floors": 15, "pilotis": 0},
    {"name": "B", "poly": [(78, 6), (124, 6), (124, 22), (78, 22)], "floors": 12, "pilotis": 2},
    {"name": "C", "poly": [(6, 44), (40, 44), (40, 59), (21, 59), (21, 83), (6, 83)], "floors": 10, "pilotis": 0},
    {"name": "D", "poly": [(96, 58), (118, 58), (118, 80), (96, 80)], "floors": 20, "pilotis": 0,
     "rooftop": {"poly": [(101, 63), (113, 63), (113, 75), (101, 75)], "h": 3.5}},
]
SITE = [(-12, -14), (136, -14), (136, 96), (-12, 96)]
ROADS = [[(-30, -22), (160, -22), (160, -14), (-30, -14)], [(136, -30), (146, -30), (146, 110), (136, 110)]]
CAM = {"pos": (-115.0, -175.0, 135.0), "target": (60.0, 42.0, 12.0), "fov_deg": 46}


def look_at(pos, target):
    f = [t - p for p, t in zip(pos, target)]
    n = math.sqrt(sum(c * c for c in f)); f = [c / n for c in f]
    up = (0, 0, 1)
    r = [f[1] * up[2] - f[2] * up[1], f[2] * up[0] - f[0] * up[2], f[0] * up[1] - f[1] * up[0]]
    n = math.sqrt(sum(c * c for c in r)); r = [c / n for c in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    return f, r, u


F, R, U = look_at(CAM["pos"], CAM["target"])
FOCAL = (W / 2) / math.tan(math.radians(CAM["fov_deg"]) / 2)


def project(p):
    d = [c - o for c, o in zip(p, CAM["pos"])]
    z = max(0.1, sum(a * b for a, b in zip(d, F)))
    x = sum(a * b for a, b in zip(d, R)); y = sum(a * b for a, b in zip(d, U))
    return (W / 2 + FOCAL * x / z, H / 2 - FOCAL * y / z), z


def depth_of(pts3):
    return sum(project(p)[1] for p in pts3) / len(pts3)


def shade(base, normal):
    light = (-0.4, -0.6, 0.7)
    n = math.sqrt(sum(c * c for c in light)); light = [c / n for c in light]
    k = max(0.0, sum(a * b for a, b in zip(normal, light)))
    v = int(base * (0.62 + 0.38 * k))
    return (v, v, v)


def prism_faces(poly, z0, z1, owner):
    """바닥 다각형(반시계)을 z0..z1로 세운 기둥의, 카메라를 향한 면들."""
    out = []
    top = [(x, y, z1) for x, y in poly]
    out.append((depth_of(top), top, (0, 0, 1), owner, None))
    n = len(poly)
    for i in range(n):
        (px, py), (qx, qy) = poly[i], poly[(i + 1) % n]
        dx, dy = qx - px, qy - py
        L = math.hypot(dx, dy); normal = (dy / L, -dx / L, 0)
        pts = [(px, py, z0), (qx, qy, z0), (qx, qy, z1), (px, py, z1)]
        center = [sum(p[k] for p in pts) / 4 for k in range(3)]
        to_cam = [c - p for c, p in zip(CAM["pos"], center)]
        if sum(a * b for a, b in zip(to_cam, normal)) <= 0:
            continue
        out.append((depth_of(pts), pts, normal, owner, ((px, py), (qx, qy))))
    return out


def render(with_labels):
    img = Image.new("RGB", (W, H), (244, 244, 242))
    d = ImageDraw.Draw(img)
    for gx in range(-40, 171, 10):
        d.line([project((gx, -40, 0))[0], project((gx, 130, 0))[0]], fill=(214, 214, 210), width=1)
    for gy in range(-40, 131, 10):
        d.line([project((-40, gy, 0))[0], project((170, gy, 0))[0]], fill=(214, 214, 210), width=1)
    for road in ROADS:
        d.polygon([project((x, y, 0))[0] for x, y in road], fill=(200, 200, 198))
    d.polygon([project((x, y, 0))[0] for x, y in SITE], outline=(90, 90, 90), width=2)

    faces = []
    for b in BUILDINGS:
        faces += prism_faces(b["poly"], 0, b["floors"] * FH, b)
        if "rooftop" in b:
            rt = b["rooftop"]; z0 = b["floors"] * FH
            faces += prism_faces(rt["poly"], z0, z0 + rt["h"], {"name": b["name"] + "_rooftop", "floors": 0, "pilotis": 0})
    faces.sort(key=lambda f: -f[0])
    for depth, pts3, normal, b, edge in faces:
        poly2 = [project(p)[0] for p in pts3]
        d.polygon(poly2, fill=shade(228, normal), outline=(40, 40, 40))
        if normal[2] == 0 and b["floors"]:
            (px, py), (qx, qy) = edge
            for k in range(1, b["floors"]):
                z = k * FH
                d.line([project((px, py, z))[0], project((qx, qy, z))[0]], fill=(60, 60, 60), width=3)
            if b["pilotis"]:
                zp = b["pilotis"] * FH
                quad = [project((px, py, 0))[0], project((qx, qy, 0))[0], project((qx, qy, zp))[0], project((px, py, zp))[0]]
                d.polygon(quad, fill=(196, 196, 194), outline=(40, 40, 40))
                n = 7
                for k in range(1, n):
                    t = k / n; gx = px + (qx - px) * t; gy = py + (qy - py) * t
                    d.line([project((gx, gy, 0))[0], project((gx, gy, zp))[0]], fill=(60, 60, 60), width=3)
        d.polygon(poly2, outline=(30, 30, 30), width=2)

    if with_labels:
        try:
            font = ImageFont.truetype("arial.ttf", 34)
        except OSError:
            font = ImageFont.load_default()
        for b in BUILDINGS:
            cx = sum(x for x, _ in b["poly"]) / len(b["poly"]); cy = sum(y for _, y in b["poly"]) / len(b["poly"])
            if b["name"] == "C":
                cx, cy = 23, 51  # L자 남쪽 날개 위
            if b["name"] == "D":
                cx, cy = 107, 59.5  # 옥탑 앞쪽 지붕
            (x, y), _ = project((cx, cy, b["floors"] * FH))
            text = f"{b['floors']}F"
            tw, th = d.textbbox((0, 0), text, font=font)[2:]
            d.rectangle([x - tw / 2 - 6, y - th / 2 - 4, x + tw / 2 + 6, y + th / 2 + 4], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
            d.text((x - tw / 2, y - th / 2 - 2), text, fill=(0, 0, 0), font=font)
    return img


out = os.path.dirname(os.path.abspath(__file__))
render(True).save(os.path.join(out, "capture_v2.png"))
plain = render(False)
plain.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0).save(os.path.join(out, "capture_v2_edges.png"))
spec = {
    "image": "capture_v2.png", "size": [W, H], "floor_height_m": FH,
    "buildings": [{"name": b["name"], "floors": b["floors"], "height_m": round(b["floors"] * FH, 1),
                   "pilotis_floors": b["pilotis"], "footprint_polygon_m": b["poly"],
                   "rooftop_box": b.get("rooftop")} for b in BUILDINGS],
    "changes_from_v1": ["floor lines 3px dark", "floor-count labels on roofs", "C drawn as one L-shaped prism", "rooftop box on D"],
    "camera": CAM, "site_boundary_m": SITE,
}
json.dump(spec, open(os.path.join(out, "spec_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", out)
