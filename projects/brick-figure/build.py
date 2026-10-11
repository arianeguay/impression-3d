"""Copy the Basic Big Brick Figure V3 parts, giving the head socket a clearance over the neck stud and
fusing the two hip studs (the source's loose tubes) onto the waist.

usage: build.py <dir of source STLs> <out_dir>
"""
import os
import shutil
import sys
import numpy as np
import trimesh

NECK_SOCKET_D = 25.65  # neck stud peaks at 25.47; the source socket narrows to 25.34 (a snap that prints too tight)
SOCKET_TOP = 14.5  # the grip band; above it the hollow head opens to 33 mm
STUD_PEG = 4.75  # each stud ends in a peg that the source plugs into a 4 mm hole in the waist
OVERLAP = 0.3  # sink the stud shoulder into the waist so the union fuses instead of touching

PARTS = {
    "obj_1_leg": "legs",
    "obj_2_Torso_v3": "torso",
    "obj_3_Waist2": "waist",
    "obj_4_Arm": "arms",
    "obj_7_head": "head",
    "obj_8_Assembly": "hands",
}

src, out = sys.argv[1], sys.argv[2]
for name, part in PARTS.items():
    path = os.path.join(src, name + ".stl")
    if part == "waist":
        waist = trimesh.load(path)
        s = waist.section(plane_origin=[0, 0, 2], plane_normal=[0, 0, 1])
        holes = [np.array(e).mean(0) for e in s.discrete if np.ptp(np.array(e), 0).max() < 13]
        tubes = []
        for tube, hole in zip(trimesh.load(os.path.join(src, "obj_5_Assembly.stl")).split(), sorted(holes, key=lambda h: h[0])):
            tube.apply_translation([hole[0], hole[1], STUD_PEG + OVERLAP - tube.bounds[1, 2]] - np.r_[tube.bounds.mean(0)[:2], 0])
            tubes.append(tube)
        # the studs point down from the waist face that meets the torso, so the hip prints standing on them
        m = trimesh.boolean.union([waist, *tubes], engine="manifold")
        m = max(m.split(), key=lambda b: b.volume)  # peg and hole share a diameter, leaving zero-volume slivers
        m.apply_translation(-m.bounds[0])
        assert m.is_watertight and m.volume > waist.volume
        m.export(os.path.join(out, "hip.stl"))
        continue
    if part != "head":
        shutil.copy(path, os.path.join(out, part + ".stl"))
        continue
    m = trimesh.load(path)
    c = m.bounds.mean(0)
    bore = trimesh.creation.cylinder(radius=NECK_SOCKET_D / 2, segment=[[c[0], c[1], -1], [c[0], c[1], SOCKET_TOP]], sections=128)
    m = m.difference(bore, engine="manifold")
    assert m.is_watertight
    m.export(os.path.join(out, part + ".stl"))
