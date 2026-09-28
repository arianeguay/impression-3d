#!/usr/bin/env python3
"""Slice STLs with the OrcaSlicer CLI (Flatpak) using the user's presets.

usage: slice.py <out_dir> <model.stl>... [--filament NAME] [--profile NAME] [--set kind.key=value ...]
                [--supported NAME ...] [--no-raft NAME ...]

--supported gives support + a 3-layer raft (none with --no-raft) to the named models only (file stem, e.g. "head"); the
others print without. Prints the G-code path, time, grams and support moves per object.
The Flatpak sandbox cannot read /tmp: keep out_dir and models under $HOME.
"""
import argparse, collections, json, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import orca_presets  # noqa: E402

ORCA = ["flatpak", "run", "--command=orca-slicer", "io.github.softfever.OrcaSlicer"]
SUPPORT = ('\n    <metadata key="enable_support" value="1"/>'
              '\n    <metadata key="support_type" value="normal(auto)"/>'
              '\n    <metadata key="raft_layers" value="{raft}"/>')


def _run(args, out_dir):
    subprocess.run(ORCA + args + ["--outputdir", out_dir], cwd=out_dir,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
    res = json.load(open(os.path.join(out_dir, "result.json")))
    if res.get("return_code") != 0:
        raise RuntimeError(f"Orca: {res.get('error_string')}")


def slice_models(out_dir, models, filament=orca_presets.DEFAULT_FILAMENT, sets=(), supported=(),
                 profile=None, no_raft=()):
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    for f in ("result.json", "plate_1.gcode"):
        if os.path.exists(os.path.join(out_dir, f)):
            os.remove(os.path.join(out_dir, f))
    sets = list(sets)
    if supported:
        sets += ["process.enable_support=0", "process.raft_layers=0"]
    orca_presets.write(out_dir, filament=filament, profile=profile, sets=sets)
    local = []
    for m in models:
        dst = os.path.join(out_dir, os.path.basename(m))
        if os.path.abspath(m) != dst:
            shutil.copy(m, dst)
        local.append(os.path.basename(m))
    settings = ["--load-settings", f"{out_dir}/machine.json;{out_dir}/process.json",
                "--load-filaments", f"{out_dir}/filament.json"]
    if supported:
        _run(["--arrange", "1", *settings, "--export-3mf", "plate.3mf", *local], out_dir)
        src = os.path.join(out_dir, "plate.3mf")
        zi = zipfile.ZipFile(src)
        items = [(i, zi.read(i.filename)) for i in zi.infolist()]
        zi.close()
        names = "|".join(re.escape(n) for n in supported)

        def tag(m):
            name = re.search(r'value="([^"]+)\.stl"', m.group(1)).group(1)
            return m.group(1) + SUPPORT.format(raft=0 if name in no_raft else 3)
        with zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED) as zo:
            for i, d in items:
                if i.filename == "Metadata/model_settings.config":
                    d = re.sub(rf'(<metadata key="name" value="(?:{names})\.stl"/>\s*'
                               r'<metadata key="extruder" value="1"/>)',
                               tag, d.decode()).encode()
                zo.writestr(i, d)
        _run(["--arrange", "1", "--slice", "0", "plate.3mf"], out_dir)
    else:
        _run(["--arrange", "1", "--slice", "0", *settings, *local], out_dir)
    return summarize(os.path.join(out_dir, "plate_1.gcode"))


def summarize(gcode):
    info = {"gcode": gcode}
    per_obj = collections.Counter()
    cur, typ = None, ""
    for line in open(gcode):
        if line.startswith("; estimated printing time (normal mode)"):
            info["time"] = line.split("=", 1)[1].strip()
        elif line.startswith("; total filament used [g]"):
            info["grams"] = float(line.split("=", 1)[1])
        elif line.startswith("; printing object "):
            cur = line.split()[3].split(".stl")[0]
        elif line.startswith("; stop printing object"):
            cur = None
        elif line.startswith(";TYPE:"):
            typ = line[6:].strip()
        elif line.startswith("G1") and " E" in line and "upport" in typ:
            per_obj[cur] += 1
    info["support_moves_per_object"] = dict(per_obj)
    return info


def main():
    a = argparse.ArgumentParser()
    a.add_argument("out_dir")
    a.add_argument("models", nargs="+")
    a.add_argument("--filament", default=orca_presets.DEFAULT_FILAMENT)
    a.add_argument("--profile")
    a.add_argument("--set", action="append", default=[])
    a.add_argument("--supported", action="append", default=[])
    a.add_argument("--no-raft", action="append", default=[], help="supported model that gets no raft")
    o = a.parse_args()
    print(json.dumps(slice_models(o.out_dir, o.models, o.filament, o.set, o.supported, o.profile, o.no_raft), indent=2))


if __name__ == "__main__":
    main()
