"""Scale the MakerWorld 'minifig 500%' parts to 50% (the file is really 10x a minifig) and fix fits.

usage: build.py <dir of STLs from export_3mf.py> <out_dir>
"""
import os
import sys
import numpy as np
import trimesh

SCALE = 0.5
PIN_ACROSS = 2.3  # octagon across flats; holes are 2.6 at 50%, and printed holes come out ~0.15 small
NECK_SOCKET_D = 24.16  # body neck stud is 24.0 at 50%; the source socket was 0.1 smaller than the stud
SOCKET_TOP = 42.2  # the socket runs up to 42.4, then the head is closed

PARTS = {
    "Minifigure - body (12)_2": "torso",
    "Minifigure - hips (2)_12": "hips",
    "Minifigure - left leg (2)_8": "leg_l",
    "Minifigure - right leg (13)_4": "leg_r",
    "Minifigure - left arm (3)_27": "arm_l",
    "Minifigure - right arm (6)_35": "arm_r",
    "Minifigure - hand (3)_23": "hand",
    "Minifigure - wrist (2)_50": "wrist",
    "Minifigure - limb clip (1)_57": "limb_clip",
    "Minifigure - hip peg (3)_17": "hip_peg",
    "head-solid-blank_6": "head",
    "connector pins - connector pin_37": "pin",
}

src, out = sys.argv[1], sys.argv[2]
for name, part in PARTS.items():
    m = trimesh.load(os.path.join(src, name + ".stl"))
    m.apply_scale(SCALE)
    if part == "pin":
        across = m.extents[0]
        c = m.bounds.mean(0)
        m.vertices[:, [0, 2]] = (m.vertices[:, [0, 2]] - c[[0, 2]]) * PIN_ACROSS / across + c[[0, 2]]
    if part == "head":
        m.apply_translation(-m.bounds[0])
        c = m.bounds.mean(0)
        bore = trimesh.creation.cylinder(radius=NECK_SOCKET_D / 2, segment=[[c[0], c[1], -1], [c[0], c[1], SOCKET_TOP]], sections=128)
        m = m.difference(bore, engine="manifold")
    m.apply_translation(-m.bounds[0])
    assert m.is_watertight, part
    m.export(os.path.join(out, part + ".stl"))
    print(f"{part:10s} {np.round(m.extents, 2)}")
