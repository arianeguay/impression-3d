"""Copy the Basic Big Brick Figure V3 parts, giving the head socket a clearance over the neck stud.

usage: build.py <dir of source STLs> <out_dir>
"""
import os
import shutil
import sys
import trimesh

NECK_SOCKET_D = 25.65  # neck stud peaks at 25.47; the source socket narrows to 25.34 (a snap that prints too tight)
SOCKET_TOP = 14.5  # the grip band; above it the hollow head opens to 33 mm

PARTS = {
    "obj_1_leg": "legs",
    "obj_2_Torso_v3": "torso",
    "obj_3_Waist2": "waist",
    "obj_4_Arm": "arms",
    "obj_5_Assembly": "tubes",
    "obj_7_head": "head",
    "obj_8_Assembly": "hands",
}

src, out = sys.argv[1], sys.argv[2]
for name, part in PARTS.items():
    path = os.path.join(src, name + ".stl")
    if part != "head":
        shutil.copy(path, os.path.join(out, part + ".stl"))
        continue
    m = trimesh.load(path)
    c = m.bounds.mean(0)
    bore = trimesh.creation.cylinder(radius=NECK_SOCKET_D / 2, segment=[[c[0], c[1], -1], [c[0], c[1], SOCKET_TOP]], sections=128)
    m = m.difference(bore, engine="manifold")
    assert m.is_watertight
    m.export(os.path.join(out, part + ".stl"))
