#!/usr/bin/env python3
"""Slice calibration/temp_tower_lego.stl and step the nozzle temperature down one level at a time.

usage: temp_tower.py <out_dir> [--start 230] [--step 5] [--levels 9] [--level-height 6]
                     [--profile lego_minifig] [--filament NAME]

Level 1 (bottom) prints at --start, each level above it --step cooler. Orca's own tower does the
same from its GUI only; the CLI cannot, so the M104 lines are inserted into the G-code here.
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import slice as slicer  # noqa: E402

TOWER = os.path.join(HERE, "..", "calibration", "temp_tower_lego.stl")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("out_dir")
    a.add_argument("--start", type=int, default=230)
    a.add_argument("--step", type=int, default=5)
    a.add_argument("--levels", type=int, default=9)
    a.add_argument("--level-height", type=float, default=6.0)
    a.add_argument("--profile", default="lego_minifig")
    a.add_argument("--filament", default=slicer.orca_presets.DEFAULT_FILAMENT)
    o = a.parse_args()
    temps = [o.start - i * o.step for i in range(o.levels)]
    info = slicer.slice_models(o.out_dir, [os.path.realpath(TOWER)], o.filament,
                               [f"filament.nozzle_temperature={o.start}",
                                f"filament.nozzle_temperature_initial_layer={o.start}"],
                               profile=o.profile)
    out, level, inserted = [], 0, []
    for line in open(info["gcode"]):
        m = re.match(r";Z:([\d.]+)", line)
        if m:
            z = float(m.group(1))
            want = min(int(z // o.level_height), o.levels - 1)
            if want > level:
                level = want
                out.append(f"M104 S{temps[level]} ; temperature tower level {level + 1}\n")
                inserted.append((level + 1, temps[level], z))
        elif re.match(r"M104 S\d+", line) and level > 0:
            continue  # keep the slicer from resetting the tower temperature
        out.append(line)
    open(info["gcode"], "w").writelines(out)
    info["levels"] = [f"level {n}: {t} C from z {z}" for n, t, z in [(1, temps[0], 0.0)] + inserted]
    print("\n".join([f"{k}: {v}" for k, v in info.items() if k != "levels"] + info["levels"]))


if __name__ == "__main__":
    main()
