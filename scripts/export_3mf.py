#!/usr/bin/env python3
"""Export each object of a Bambu Studio / MakerWorld 3MF to STL, with its placement applied.

usage: export_3mf.py <model.3mf> <out_dir>

Orca cannot slice these 3MFs (version 2.6). Each build item's mesh lives in a sub-model file under
3D/Objects/, placed by the component transform then the item transform (3MF row-vector matrices);
a negative determinant mirrors the mesh, so its triangle winding is flipped to keep normals out.
"""
import os, re, sys, zipfile
import numpy as np
import trimesh


def matrix(text):
    a = list(map(float, text.split()))
    m = np.eye(4)
    m[:3, :3] = np.array(a[:9]).reshape(3, 3)
    m[3, :3] = a[9:]
    return m


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    z = zipfile.ZipFile(src)
    model = z.read("3D/3dmodel.model").decode()
    cfg = z.read("Metadata/model_settings.config").decode()
    names = dict(re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', cfg))
    for oid, item in re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"', model):
        obj = re.search(r'<object id="%s".*?</object>' % oid, model, re.S).group(0)
        parts = []
        for path, sub_id, comp in re.findall(
                r'<component p:path="([^"]+)" objectid="(\d+)"[^>]*transform="([^"]+)"', obj):
            sub = z.read(path.lstrip("/")).decode()
            body = re.search(r'<object id="%s".*?</object>' % sub_id, sub, re.S).group(0)
            v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body), float)
            f = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
            t = matrix(comp) @ matrix(item)
            if np.linalg.det(t[:3, :3]) < 0:
                f = f[:, ::-1]
            parts.append(trimesh.Trimesh((np.c_[v, np.ones(len(v))] @ t)[:, :3], f))
        mesh = trimesh.util.concatenate(parts)
        mesh.apply_translation(-mesh.bounds[0])
        name = names.get(oid, oid).replace(".stl", "").split("_")[0] + "_" + oid
        mesh.export(os.path.join(out, name + ".stl"))
        print(f"{name}: {np.round(mesh.extents, 1)} mm")


if __name__ == "__main__":
    main()
