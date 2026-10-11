"""Scale the minifig skeleton (Skeleton_Full.stl, one plate at 1x) to 500% and fix what scaling breaks.

usage: build.py <Skeleton_Full.stl> <out_dir>
"""
import os
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

SCALE = 5
NECK_SOCKET_D = 24.25 / SCALE  # stud 4.8 (24.0 at 500%), source socket 4.97 (0.85 loose); the faceted socket measures ~0.1 under its vertex radius
SOCKET_GRIP_TOP = 1.6  # the 4.97 ring runs to z 1.5, then opens into a 5.62 cavity
LEG_FLAT = 1.0  # mm cut off the leg's rounded back at 500%: the bed contact goes from 19 to 190 mm2

src, out = sys.argv[1], sys.argv[2]
bodies = trimesh.load(src).split(only_watertight=False)
solid = sorted([b for b in bodies if b.is_watertight and b.volume > 1], key=lambda b: -b.volume)
torso, legs, arms, tips = solid[0], solid[1:3], solid[3:5], solid[5:7]
head = max([b for b in bodies if not b.is_watertight], key=lambda b: b.extents.max())
shards = [b for b in bodies if not b.is_watertight and b is not head and b.extents.max() < 1.5]
# the head has four non-manifold edges in its face; split() cuts shards off there, so keep them with it
head = trimesh.util.concatenate([head, *[s for s in shards if np.all(s.bounds[0] >= head.bounds[0] - 0.1) and np.all(s.bounds[1] <= head.bounds[1] + 0.1)]])

s = head.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
ring = min((np.array(e) for e in s.discrete), key=lambda e: np.ptp(e, 0)[0])
c = ring.mean(0)[:2]
r = np.linalg.norm(head.vertices[:, :2] - c, axis=1)
ring_r = np.ptp(ring, 0)[0] / 2
grip = (r > ring_r - 0.08) & (r < ring_r + 0.1) & (head.vertices[:, 2] < SOCKET_GRIP_TOP)  # wall vertices wander 2.43 to 2.54; the cavity step starts at 2.67
head.vertices[grip, :2] = c + (head.vertices[grip, :2] - c) * (NECK_SOCKET_D / 2 / r[grip, None])

# each claw's fingertip pair floats 0.08 mm off its arm (0.4 mm at 500%): move it onto the arm
fused = []
for arm in arms:
    tip = min(tips, key=lambda t: cKDTree(arm.vertices).query(t.vertices)[0].min())
    d, i = cKDTree(arm.vertices).query(tip.vertices)
    j = d.argmin()
    gap = arm.vertices[i[j]] - tip.vertices[j]
    tip = tip.copy()
    tip.apply_translation(gap * (1 + 0.05 / d[j]))
    fused.append(trimesh.boolean.union([arm, tip], engine="manifold"))

parts = {"torso": torso, "leg_a": legs[0], "leg_b": legs[1], "arm_a": fused[0], "arm_b": fused[1], "head": head}
def most_contact_pose(m, max_tilt=15):
    """Stable pose with the most bed contact that keeps the part's clip plane within max_tilt of flat."""
    best = None
    for t in trimesh.poses.compute_stable_poses(m, n_samples=1)[0]:
        if np.degrees(np.arccos(abs(t[2, 2]))) > max_tilt:
            continue
        p = m.copy()
        p.apply_transform(t)
        p.apply_translation([0, 0, -p.bounds[0, 2]])
        s = p.section(plane_origin=[0, 0, 0.15], plane_normal=[0, 0, 1])
        area = s.to_2D()[0].area if s else 0
        if best is None or area > best[0]:
            best = (area, p)
    return best[1]


for name, m in parts.items():
    m = m.copy()
    m.apply_scale(SCALE)
    m.apply_translation([0, 0, -m.bounds[0, 2]])
    if name.startswith("arm"):
        m = most_contact_pose(m)
    if name.startswith("leg"):
        m = m.slice_plane([0, 0, LEG_FLAT], [0, 0, 1], cap=True)
        m.apply_translation([0, 0, -LEG_FLAT])
    if name != "head":
        assert m.is_watertight and len(m.split()) == 1, name
    m.export(os.path.join(out, name + ".stl"))
    print(f"{name:6s} {np.round(m.extents, 1)}")
