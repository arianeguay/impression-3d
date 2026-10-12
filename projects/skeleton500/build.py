"""Scale the minifig skeleton (Skeleton_Full.stl, one plate at 1x) to 500% and fix what scaling breaks.

usage: build.py <Skeleton_Full.stl> <out_dir>
"""
import collections
import os
import sys
import numpy as np
import trimesh

SCALE = 5
NECK_SOCKET_D = 24.25 / SCALE  # stud 4.8 (24.0 at 500%), source socket 4.97 (0.85 loose); the faceted socket measures ~0.1 under its vertex radius
SOCKET_GRIP_TOP = 1.6  # the 4.97 ring runs to z 1.5, then opens into a 5.62 cavity
JAW_GAP = 2.06  # shoulder socket jaws 1.95 apart over a 2.16 ball: both arms cracked snapping on at 500%
FLAT = 1.0  # mm cut off the rounded side that meets the plate at 500%: legs 19 to 190 mm2, arms 19 to 248 mm2

def _edges(f):
    return ((f[0], f[1]), (f[1], f[2]), (f[2], f[0]))


def split_nonmanifold(m):
    """Make a mesh manifold where two sheets share an edge, by giving each sheet its own copy of the edge's vertices."""
    m = m.copy()
    m.merge_vertices()
    faces = m.faces.copy()
    verts = list(m.vertices)
    ec = collections.defaultdict(list)
    for fi, f in enumerate(faces):
        for a, b in _edges(f):
            ec[tuple(sorted((a, b)))].append((fi, a, b))
    linked = set()  # (edge, face, face) pairs allowed to stay connected across a non-manifold edge
    for e, uses in ec.items():
        if len(uses) != 4:
            continue
        fwd = [fi for fi, a, b in uses if (a, b) == e]
        bwd = [fi for fi, a, b in uses if (a, b) != e]
        p0, p1 = np.array(verts[e[0]]), np.array(verts[e[1]])
        axis = (p1 - p0) / np.linalg.norm(p1 - p0)
        ref = None

        def angle(fi):
            nonlocal ref
            c = np.array(verts[[v for v in faces[fi] if v not in e][0]]) - p0
            c -= axis * c.dot(axis)
            if ref is None:
                ref = c / np.linalg.norm(c)
            return np.arctan2(np.cross(ref, c).dot(axis), ref.dot(c)) % (2 * np.pi)

        order = sorted(fwd + bwd, key=angle)
        # angular neighbours of opposite direction belong to one sheet
        first = order[0]
        mate = order[1] if (order[1] in bwd) != (first in bwd) else order[-1]
        rest = [f for f in order if f not in (first, mate)]
        linked |= {(e, first, mate), (e, mate, first), (e, rest[0], rest[1]), (e, rest[1], rest[0])}
    bad_v = {v for e, uses in ec.items() if len(uses) != 2 for v in e}
    for v in bad_v:
        fl = [fi for fi, f in enumerate(faces) if v in f]
        parent = {fi: fi for fi in fl}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for fi in fl:
            for gi in fl:
                if fi >= gi:
                    continue
                shared = set(faces[fi]) & set(faces[gi])
                if len(shared) != 2:
                    continue
                e = tuple(sorted(shared))
                if len(ec[e]) == 2 or (e, fi, gi) in linked:
                    parent[find(fi)] = find(gi)
        groups = collections.defaultdict(list)
        for fi in fl:
            groups[find(fi)].append(fi)
        for k, fs in enumerate(groups.values()):
            if k == 0:
                continue
            # STL keeps no topology: a copy left on the same point is merged back on load, so nudge it into its own sheet
            centre = np.mean([np.mean([verts[u] for u in faces[fi]], axis=0) for fi in fs], axis=0)
            nudge = centre - verts[v]
            verts.append(verts[v] + nudge / np.linalg.norm(nudge) * 0.002)
            for fi in fs:
                faces[fi][faces[fi] == v] = len(verts) - 1
    return trimesh.Trimesh(np.array(verts), faces, process=False)


src, out = sys.argv[1], sys.argv[2]
bodies = trimesh.load(src).split(only_watertight=False)
solid = sorted([b for b in bodies if b.is_watertight and b.volume > 1], key=lambda b: -b.volume)
torso, legs, arms = solid[0], solid[1:3], solid[3:5]
# the head has four tiny edges shared by two sheets of its face; Orca dropped head layers 8 to 12 mm over them
head = split_nonmanifold(max([b for b in bodies if not b.is_watertight], key=lambda b: b.extents.max()))

s = head.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
ring = min((np.array(e) for e in s.discrete), key=lambda e: np.ptp(e, 0)[0])
c = ring.mean(0)[:2]
r = np.linalg.norm(head.vertices[:, :2] - c, axis=1)
ring_r = np.ptp(ring, 0)[0] / 2
grip = (r > ring_r - 0.08) & (r < ring_r + 0.1) & (head.vertices[:, 2] < SOCKET_GRIP_TOP)  # wall vertices wander 2.43 to 2.54; the cavity step starts at 2.67
head.vertices[grip, :2] = c + (head.vertices[grip, :2] - c) * (NECK_SOCKET_D / 2 / r[grip, None])

# the socket's two floating side walls (solid[5:7]) are left out; the jaws open further so the ball snaps in with half the spread
fused = []
for arm in arms:
    arm = arm.copy()
    v = arm.vertices
    jaw = v[:, 1] > arm.bounds[1, 1] - 2.4
    lo, hi = jaw & (np.abs(v[:, 2] - 1.65) < 0.07), jaw & (np.abs(v[:, 2] - 3.62) < 0.07)
    widen = (JAW_GAP - (v[hi, 2].mean() - v[lo, 2].mean())) / 2
    v[lo, 2] -= widen
    v[hi, 2] += widen
    arm.vertices = v
    fused.append(arm)

parts = {"torso": torso, "leg_a": legs[0], "leg_b": legs[1], "arm_a": fused[0], "arm_b": fused[1], "head": head}
def most_contact_pose(m, keep):
    """Stable pose with the most bed contact among those whose rotation passes keep(t)."""
    best = None
    for t in trimesh.poses.compute_stable_poses(m, n_samples=1)[0]:
        if not keep(t):
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
        # the jaws part along the source's z: keep that axis horizontal so they flex within a layer
        m = most_contact_pose(m, lambda t: abs(t[2, 2]) < 0.2)
    if name.startswith(("leg", "arm")):
        m = m.slice_plane([0, 0, FLAT], [0, 0, 1], cap=True)
        m.apply_translation([0, 0, -FLAT])
    assert m.is_watertight and len(m.split()) == 1, name
    m.export(os.path.join(out, name + ".stl"))
    print(f"{name:6s} {np.round(m.extents, 1)}")
