"""Shaded render of the assembled case with a Charge 4 inside, and of the split body.

Reads parts/assembly/ (written by build.py) and parts/source/, writes render.png.
"""
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
ASM = HERE / "parts" / "assembly"
SRC = HERE / "parts" / "source"
DX = 27.0
TOP = 114.6
RECESS = 113.6
CENTER_X, CENTER_Y = 115.1, 49.8

WALNUT = (122, 74, 42)
GRILLE = (46, 44, 42)
BLACK = (28, 28, 30)
BRASS = (196, 160, 90)
SPEAKER = (90, 110, 140)


def load(path, offset=(0, 0, 0)):
    m = trimesh.load(path)
    m.apply_translation(offset)
    return m


def seat(name, x):
    """Place a knob so its cap sits on the pad recess, pin in the hole at x."""
    m = load(SRC / f"{name}.stl")
    z = m.bounds[0][2]
    while m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]).extents.max() < 4:
        z += 0.1
    m.apply_translation([x - m.bounds[:, 0].mean(), 40 - m.bounds[:, 1].mean(), RECESS - z])
    return m


def legs():
    leg = load(SRC / "Legs.stl", (DX, 0, 0))
    out = []
    for sx in (1, -1):
        for sy in (1, -1):
            m = leg.copy()
            m.apply_transform(np.diag([sx, sy, 1, 1]))
            m.apply_translation([CENTER_X * (1 - sx), CENTER_Y * (1 - sy), 0])
            out.append(m)
    return out


def charge4():
    m = trimesh.creation.cylinder(radius=47, height=221, sections=96)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    m.apply_translation([CENTER_X, 50, 13 + 47])
    return m


def render(parts, view, size=(1200, 800), ss=2):
    w, h = size[0] * ss, size[1] * ss
    d = np.array(view, float)
    d /= np.linalg.norm(d)
    right = np.cross(d, [0, 0, 1])
    right /= np.linalg.norm(right)
    up = np.cross(right, d)
    lights = [(np.array([-0.4, -0.7, 0.6]), 0.65), (np.array([0.8, -0.3, 0.3]), 0.25)]
    allv = np.vstack([m.vertices for m, _ in parts])
    u, v = allv @ right, allv @ up
    scale = 0.9 * min(w / np.ptp(u), h / np.ptp(v))
    cu, cv = (u.max() + u.min()) / 2, (v.max() + v.min()) / 2
    zbuf = np.full((h, w), np.inf)
    img = np.empty((h, w, 3))
    img[:] = (245, 243, 238)
    for mesh, color in parts:
        n = mesh.face_normals
        n = np.where((n @ d)[:, None] > 0, -n, n)
        shade = 0.3 + sum(k * np.clip(n @ (L / np.linalg.norm(L)), 0, None) for L, k in lights)
        rgb = np.clip(np.outer(shade, color), 0, 255)
        tri = mesh.vertices[mesh.faces]
        px = (tri @ right - cu) * scale + w / 2
        py = h / 2 - (tri @ up - cv) * scale
        pz = tri @ d
        for i in range(len(tri)):
            x0, x1 = int(max(px[i].min(), 0)), int(min(np.ceil(px[i].max()), w - 1))
            y0, y1 = int(max(py[i].min(), 0)), int(min(np.ceil(py[i].max()), h - 1))
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, bx, cx), (ay, by, cy) = px[i], py[i]
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-12:
                continue
            l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
            l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
            if not inside.any():
                continue
            z = l1 * pz[i, 0] + l2 * pz[i, 1] + l3 * pz[i, 2]
            win = zbuf[y0:y1 + 1, x0:x1 + 1]
            hit = inside & (z < win)
            win[hit] = z[hit]
            img[y0:y1 + 1, x0:x1 + 1][hit] = rgb[i]
    return Image.fromarray(img.astype(np.uint8)).resize(size, Image.LANCZOS)


def caption(im, text):
    ImageDraw.Draw(im).text((24, 20), text, fill=(60, 60, 60), font=ImageFont.load_default(size=26))
    return im


body = [load(ASM / "body_left.stl"), load(ASM / "body_right.stl")]
small = [(load(SRC / "Knob.stl", (0, 0, TOP - 163.6)), BRASS),
         (seat("Button", 155), BRASS), (seat("Knob3", 176), BRASS), (seat("Knob2", 195), BRASS)]
small += [(m, WALNUT) for m in legs()]

front = render([(b, WALNUT) for b in body] + small + [
    (load(ASM / "face.stl"), GRILLE), (load(ASM / "rim.stl"), BLACK), (charge4(), SPEAKER)],
    view=[0.55, 1.0, -0.42])
caption(front, "Assembled, Charge 4 (221 x 94 mm) in blue behind the grille")

split = render([(body[0], WALNUT), (load(ASM / "body_right.stl", (45, 0, 0)), (150, 96, 60))],
               view=[0.35, 1.0, -0.55])
caption(split, "Body halves apart: glue tongues on the left half, cradle removed")

sheet = Image.new("RGB", (1200, 1600), (245, 243, 238))
sheet.paste(front, (0, 0))
sheet.paste(split, (0, 800))
sheet.save(HERE / "render.png")
print(HERE / "render.png")
