"""Resize the Vintage Speaker case for a JBL Charge 4 and split it for a 220 mm bed.

Every resize is a translation, never a scale: a slab of the part that repeats is copied
and inserted, so rounded corners, the top holes and the 3 mm grille pitch stay as designed.
Reads parts/source/*.stl, writes parts/*.stl.
"""
from pathlib import Path

import manifold3d as m3
import numpy as np
import trimesh

HERE = Path(__file__).parent
SRC = HERE / "parts" / "source"
OUT = HERE / "parts"

GRID = 3.0
DX = 9 * GRID  # inner 197.2 -> 224.2 for a 221 mm speaker
DZ = 1 * GRID  # inner 95.6 -> 98.6 for a 94 mm speaker
EPS = 0.05
BIG = 1000.0

# Insertion planes sit where every part is a plain extrusion and, on the face, between grille holes
# (holes at x = 8.6 + 3k, z = 18.8 + 3k).
BODY_X = 107.0  # between the top dial hole (ends 77.5) and the knob pad (starts 110)
FACE_X = 100.1
Z_CUT = 59.3
SPLIT_X = 101.6 + DX / 2  # middle of the resized case, between two grille columns
RIM_SPLIT_X = 70.0  # off the case seam so the rim bridges it

TAB_W, TAB_T, TAB_L, TAB_GAP, TAB_EMBED = 20.0, 1.5, 10.0, 0.1, 0.3


def load(name):
    t = trimesh.load(SRC / f"{name}.stl")
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32),
                               tri_verts=np.asarray(t.faces, np.uint32)))


def save(man, name, down):
    """Write the part with the face pointing `down` (a unit vector) on the plate, or in place."""
    mm = man.to_mesh()
    t = trimesh.Trimesh(mm.vert_properties[:, :3], mm.tri_verts)
    if down is not None:
        t.apply_transform(trimesh.geometry.align_vectors(down, [0, 0, -1]))
        t.apply_translation(-t.bounds[0])
    assert t.is_watertight, name
    t.export(OUT / f"{name}.stl")
    print(f"{name:14s} {np.round(t.extents, 1)}  {t.volume / 1000:.0f} cm3")
    return t


def box(lo, hi):
    lo, hi = np.array(lo, float), np.array(hi, float)
    return m3.Manifold.cube(hi - lo).translate(lo)


def span(axis, a, b):
    lo, hi = [-BIG] * 3, [BIG] * 3
    lo[axis], hi[axis] = a, b
    return box(lo, hi)


def insert(man, axis, c, w):
    """Copy the slab [c - w, c] and insert it at c, pushing everything past c by w."""
    shift = [0.0, 0.0, 0.0]
    shift[axis] = w
    left = man ^ span(axis, -BIG, c + EPS)
    slab = (man ^ span(axis, c - w - EPS, c + EPS)).translate(shift)
    right = (man ^ span(axis, c - EPS, BIG)).translate(shift)
    return left + slab + right


def remove_cradle(body):
    """Cut the Flip cradle off the floor: it would lift a 94 mm speaker into the lid."""
    t = trimesh.load(SRC / "VintageSpeakerBody.stl")
    v = t.vertices
    depth = trimesh.proximity.signed_distance(t.convex_hull, v)
    cradle = (v[:, 1] > 15) & (v[:, 1] < 70) & (v[:, 2] > 13.05) & (v[:, 2] < 30)
    inner = trimesh.convex.convex_hull(v[(depth > 2.5) & ~cradle])
    cavity = m3.Manifold(m3.Mesh(vert_properties=np.asarray(inner.vertices, np.float32),
                                 tri_verts=np.asarray(inner.faces, np.uint32)))
    return body - (cavity ^ box([-BIG, 15, 13.0], [BIG, 70, 30]))


def tabs(z_floor, z_top, y_back):
    """Glue tongues on the left half's inner walls, reaching TAB_L into the right half."""
    out = m3.Manifold()
    x0, x1 = SPLIT_X - TAB_L, SPLIT_X + TAB_L
    for y in (8.0, 70.0):
        out += box([x0, y, z_floor - TAB_EMBED], [SPLIT_X + EPS, y + TAB_W, z_floor + TAB_T])
        out += box([SPLIT_X - EPS, y, z_floor + TAB_GAP], [x1, y + TAB_W, z_floor + TAB_T])
        out += box([x0, y, z_top - TAB_T], [SPLIT_X + EPS, y + TAB_W, z_top + TAB_EMBED])
        out += box([SPLIT_X - EPS, y, z_top - TAB_T], [x1, y + TAB_W, z_top - TAB_GAP])
    zc = (z_floor + z_top) / 2
    out += box([x0, y_back - TAB_T, zc - 12], [SPLIT_X + EPS, y_back + TAB_EMBED, zc + 12])
    out += box([SPLIT_X - EPS, y_back - TAB_T, zc - 12], [x1, y_back - TAB_GAP, zc + 12])
    return out


body = remove_cradle(load("VintageSpeakerBody"))
body = insert(insert(body, 0, BODY_X, DX), 2, Z_CUT, DZ)
face = insert(insert(load("VSFace"), 0, FACE_X, DX), 2, Z_CUT, DZ)
rim = insert(insert(load("FaceRim"), 0, BODY_X, DX), 2, Z_CUT, DZ)

# The designer's "BOONE" script stands 1 mm proud of the grille: printed face down it would leave
# the whole grille hanging over air.
face = face ^ span(1, -11.0, BIG)

X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX = np.vstack([np.eye(3) * -1, np.eye(3)])[[0, 3, 1, 4, 2, 5]]
floor_z, top_z, back_y = 13.0, 108.6 + DZ, 98.6
save((body ^ span(0, -BIG, SPLIT_X)) + tabs(floor_z, top_z, back_y), "body_left", X_MIN)
save(body ^ span(0, SPLIT_X, BIG), "body_right", X_MAX)
save(face ^ span(0, -BIG, SPLIT_X), "face_left", Y_MIN)
save(face ^ span(0, SPLIT_X, BIG), "face_right", Y_MIN)
save(rim ^ span(0, -BIG, RIM_SPLIT_X), "rim_short", Y_MAX)
save(rim ^ span(0, RIM_SPLIT_X, BIG), "rim_long", Y_MAX)
save(load("Knob"), "dial", Z_MIN)
for name in ("Knob2", "Knob3", "JBL Speaker #2", "Button", "Legs"):
    save(load(name), name.lower().replace(" #", "").replace(" ", "_"), Z_MAX)

# In place, for render.py.
(OUT / "assembly").mkdir(exist_ok=True)
save((body ^ span(0, -BIG, SPLIT_X)) + tabs(floor_z, top_z, back_y), "assembly/body_left", None)
save(body ^ span(0, SPLIT_X, BIG), "assembly/body_right", None)
save(face, "assembly/face", None)
save(rim, "assembly/rim", None)
