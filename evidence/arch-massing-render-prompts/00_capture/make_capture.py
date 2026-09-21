# -*- coding: utf-8 -*-
"""가상 매스 뷰포트 캡처 생성기.

3D 상자(건물 매스)를 투시 투영해 Rhino/SketchUp 뷰포트 캡처처럼 보이는 이미지를 만든다.
회색 면, 검은 윤곽선, 층 분절선, 바닥 격자, 대지 경계와 도로. 실제 프로젝트와 무관한 가상 배치이며,
층수·치수는 spec.json에 기록되어 이후 렌더 결과의 보존 판정 기준이 된다.

실행: python make_capture.py  → capture.png, capture_edges.png, spec.json
Pillow만 필요.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFilter

W, H = 1536, 1024
FH = 3.1  # 층고 m

# 건물: 이름, 원점(x,y), 폭(x), 깊이(y), 층수, 필로티 층수
BUILDINGS = [
    {"name": "A", "x": 0, "y": 0, "w": 62, "d": 16, "floors": 15, "pilotis": 0},
    {"name": "B", "x": 78, "y": 6, "w": 46, "d": 16, "floors": 12, "pilotis": 2},
    {"name": "C1", "x": 6, "y": 44, "w": 34, "d": 15, "floors": 10, "pilotis": 0, "group": "C"},
    {"name": "C2", "x": 6, "y": 59, "w": 15, "d": 24, "floors": 10, "pilotis": 0, "group": "C"},
    {"name": "D", "x": 96, "y": 58, "w": 22, "d": 22, "floors": 20, "pilotis": 0},
]
SITE = [(-12, -14), (136, -14), (136, 96), (-12, 96)]
ROADS = [[(-30, -22), (160, -22), (160, -14), (-30, -14)], [(136, -30), (146, -30), (146, 110), (136, 110)]]

# 카메라: 남서쪽 상공에서 단지 중심을 본다
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
    z = sum(a * b for a, b in zip(d, F))
    x = sum(a * b for a, b in zip(d, R))
    y = sum(a * b for a, b in zip(d, U))
    if z <= 0.1:
        z = 0.1
    return (W / 2 + FOCAL * x / z, H / 2 - FOCAL * y / z), z


def depth_of(pts3):
    return sum(project(p)[1] for p in pts3) / len(pts3)


def shade(base, normal):
    light = (-0.4, -0.6, 0.7)
    n = math.sqrt(sum(c * c for c in light)); light = [c / n for c in light]
    k = max(0.0, sum(a * b for a, b in zip(normal, light)))
    v = int(base * (0.62 + 0.38 * k))
    return (v, v, v)


img = Image.new("RGB", (W, H), (244, 244, 242))
d = ImageDraw.Draw(img)

# 바닥 격자 (10m)
for gx in range(-40, 171, 10):
    a, _ = project((gx, -40, 0)); b, _ = project((gx, 130, 0))
    d.line([a, b], fill=(214, 214, 210), width=1)
for gy in range(-40, 131, 10):
    a, _ = project((-40, gy, 0)); b, _ = project((170, gy, 0))
    d.line([a, b], fill=(214, 214, 210), width=1)
# 도로, 대지 경계
for road in ROADS:
    d.polygon([project((x, y, 0))[0] for x, y in road], fill=(200, 200, 198))
d.polygon([project((x, y, 0))[0] for x, y in SITE], outline=(90, 90, 90), width=2)

faces = []  # (depth, polygon2d, color, edges3d)
for b in BUILDINGS:
    x0, y0, w, dd = b["x"], b["y"], b["w"], b["d"]
    h = b["floors"] * FH
    x1, y1 = x0 + w, y0 + dd
    corners = {"a": (x0, y0), "b": (x1, y0), "c": (x1, y1), "d": (x0, y1)}
    quads = {
        "top": ([(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)], (0, 0, 1)),
        "south": ([(x0, y0, 0), (x1, y0, 0), (x1, y0, h), (x0, y0, h)], (0, -1, 0)),
        "west": ([(x0, y0, 0), (x0, y1, 0), (x0, y1, h), (x0, y0, h)], (-1, 0, 0)),
        "east": ([(x1, y0, 0), (x1, y1, 0), (x1, y1, h), (x1, y0, h)], (1, 0, 0)),
        "north": ([(x0, y1, 0), (x1, y1, 0), (x1, y1, h), (x0, y1, h)], (0, 1, 0)),
    }
    for name, (pts, normal) in quads.items():
        center = [sum(p[i] for p in pts) / 4 for i in range(3)]
        to_cam = [c - p for c, p in zip(CAM["pos"], center)]
        if sum(a * b for a, b in zip(to_cam, normal)) <= 0:
            continue  # 카메라를 등진 면
        faces.append((depth_of(pts), [project(p)[0] for p in pts], shade(228, normal), pts, normal, b))

faces.sort(key=lambda f: -f[0])
for depth, poly, color, pts3, normal, b in faces:
    d.polygon(poly, fill=color, outline=(40, 40, 40))
    if normal[2] == 0:  # 수직면: 층 분절선과 필로티
        h = b["floors"] * FH
        base0, base1 = pts3[0], pts3[1]
        for k in range(1, b["floors"]):
            z = k * FH
            a, _ = project((base0[0], base0[1], z)); c, _ = project((base1[0], base1[1], z))
            d.line([a, c], fill=(120, 120, 120), width=1)
        if b["pilotis"]:
            zp = b["pilotis"] * FH
            p0, _ = project((base0[0], base0[1], 0)); p1, _ = project((base1[0], base1[1], 0))
            p2, _ = project((base1[0], base1[1], zp)); p3, _ = project((base0[0], base0[1], zp))
            d.polygon([p0, p1, p2, p3], fill=(196, 196, 194), outline=(40, 40, 40))
            n = 7
            for k in range(1, n):
                t = k / n
                gx = base0[0] + (base1[0] - base0[0]) * t; gy = base0[1] + (base1[1] - base0[1]) * t
                q0, _ = project((gx, gy, 0)); q1, _ = project((gx, gy, zp))
                d.line([q0, q1], fill=(60, 60, 60), width=3)
    # 윤곽 강조
    d.polygon(poly, outline=(30, 30, 30))

out = os.path.dirname(os.path.abspath(__file__))
img.save(os.path.join(out, "capture.png"))
edges = img.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
edges.save(os.path.join(out, "capture_edges.png"))

spec = {
    "image": "capture.png", "size": [W, H], "floor_height_m": FH,
    "buildings": [{"name": b["name"], "footprint_m": [b["w"], b["d"]], "floors": b["floors"],
                   "height_m": round(b["floors"] * FH, 1), "pilotis_floors": b["pilotis"], "group": b.get("group")} for b in BUILDINGS],
    "note": "C1+C2 는 하나의 L자형 동(C). 총 4개 동: A 15F, B 12F(필로티 2F), C 10F L자, D 20F 타워.",
    "camera": CAM, "site_boundary_m": SITE,
}
json.dump(spec, open(os.path.join(out, "spec.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok", out)
