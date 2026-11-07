#!/usr/bin/env python3
"""Flatten Orca user presets into files the Orca CLI accepts.

usage: orca_presets.py <out_dir> [--machine NAME] [--process NAME] [--filament NAME]
                       [--profile NAME] [--set kind.key=value ...]

The CLI rejects a user preset as-is: it needs the whole inherits chain merged, a "type",
and compatible_printers naming the machine and its system parent. A profile is a named set of
overrides kept in the repo's profiles/ folder (e.g. "figurine").
"""
import argparse, glob, json, os, shutil

ROOT = os.path.expanduser("~/.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer")
USER = f"{ROOT}/user/default"
PROFILES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "profiles")
DEFAULT_MACHINE = "Flashforge Adventurer 5M 0.4 Nozzle - custom"
DEFAULT_PROCESS = "0.20mm Standard @Flashforge AD5M 0.4 Nozzle - Settings"
DEFAULT_FILAMENT = "Polymaker Panchroma Neon PLA"


def system_index():
    # Orca >= 2.5.0 packs the system presets in .opc files: the index is then empty and
    # a preset keeps its "inherits" for Orca to resolve itself (slice.py passes --datadir).
    idx = {}
    for p in glob.glob(f"{ROOT}/system/**/*.json", recursive=True):
        try:
            d = json.load(open(p))
        except (ValueError, UnicodeDecodeError):
            continue
        if "name" in d:
            idx[(p.split("/")[-2], d["name"])] = d
    return idx


def flatten(path, kind, idx):
    chain = [json.load(open(path))]
    while (kind, chain[-1].get("inherits")) in idx:
        chain.append(idx[(kind, chain[-1]["inherits"])])
    out = {}
    for c in reversed(chain):
        out.update(c)
    parent = out.get("inherits", "")
    if len(chain) > 1:
        out.pop("inherits", None)
    out["from"] = "User"
    return out, parent


def profile_sets(name):
    d = json.load(open(os.path.join(PROFILES, f"{name}.json")))
    base = profile_sets(d["_extends"]) if "_extends" in d else []
    return base + [f"{k}={v}" for k, v in d.items() if not k.startswith("_")]


def write(out_dir, machine=DEFAULT_MACHINE, process=DEFAULT_PROCESS, filament=DEFAULT_FILAMENT,
          profile=None, sets=()):
    idx = system_index()
    os.makedirs(out_dir, exist_ok=True)
    m, m_parent = flatten(f"{USER}/machine/{machine}.json", "machine", idx)
    m["inherits"] = m_parent
    presets = {
        "machine": m,
        "process": flatten(f"{USER}/process/{process}.json", "process", idx)[0],
        "filament": flatten(f"{USER}/filament/{filament}.json", "filament", idx)[0],
    }
    for kind in ("process", "filament"):
        presets[kind]["compatible_printers"] = [m["name"], m_parent]
        presets[kind]["compatible_printers_condition"] = ""
    presets["process"].update({"gcode_label_objects": "1", "exclude_object": "1"})
    for s in (profile_sets(profile) if profile else []) + list(sets):
        k, v = s.split("=", 1)
        kind, key = k.split(".", 1)
        cur = presets[kind].get(key)
        presets[kind][key] = [v] if isinstance(cur, list) else v
    # Orca 2.5.0 only parses a preset that sits in a datadir's user/default/<kind>/ folder
    dd = f"{out_dir}/datadir"
    shutil.rmtree(dd, ignore_errors=True)
    shutil.copytree(f"{ROOT}/system", f"{dd}/system")
    paths = []
    for kind, d in presets.items():
        os.makedirs(f"{dd}/user/default/{kind}")
        paths.append(f"{dd}/user/default/{kind}/{d['name']}.json")
        json.dump(d, open(paths[-1], "w"), indent=2)
    return paths


def main():
    a = argparse.ArgumentParser()
    a.add_argument("out_dir")
    a.add_argument("--machine", default=DEFAULT_MACHINE)
    a.add_argument("--process", default=DEFAULT_PROCESS)
    a.add_argument("--filament", default=DEFAULT_FILAMENT)
    a.add_argument("--profile")
    a.add_argument("--set", action="append", default=[], help="kind.key=value, e.g. process.layer_height=0.12")
    o = a.parse_args()
    print("\n".join(write(o.out_dir, o.machine, o.process, o.filament, o.profile, o.set)))


if __name__ == "__main__":
    main()
