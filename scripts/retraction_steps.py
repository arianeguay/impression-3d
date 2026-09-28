#!/usr/bin/env python3
"""Turn a sliced retraction tower into a retraction test: one length per millimetre of height.

usage: retraction_steps.py <in.gcode> <out.gcode> [--start 0] [--step 0.2] [--end 2] [--base 0.4]

Orca's GUI changes the retraction length every 1 mm above a 0.4 mm base; its CLI does not, so the
plain `G1 E-<len>` retract and the matching `G1 E<len>` unretract are rewritten here by layer
height. Refuses a file whose retractions are folded into wipe moves, which this cannot rewrite.
"""
import argparse, math, re, sys


def main():
    a = argparse.ArgumentParser()
    a.add_argument("src")
    a.add_argument("dst")
    a.add_argument("--start", type=float, default=0.0)
    a.add_argument("--step", type=float, default=0.2)
    a.add_argument("--end", type=float, default=2.0)
    a.add_argument("--base", type=float, default=0.4)
    o = a.parse_args()
    lines = open(o.src).read().splitlines(keepends=True)
    if any(re.match(r"G1 X[^E\n]*E-", l) for l in lines):
        sys.exit("retraction is folded into wipe moves; set wipe off and reslice")
    sliced = re.search(r"^; retraction_length = ([\d.]+)", "".join(lines), re.M)
    if not sliced:
        sys.exit("no retraction_length in the G-code header")
    sliced = float(sliced.group(1))  # start/end G-code retract other lengths and stay untouched
    z, length, out, seen = 0.0, None, [], {}
    for i, l in enumerate(lines):
        m = re.match(r";Z:([\d.]+)", l)
        if m:
            z = float(m.group(1))
        r = re.match(r"G1 E(-?)([\d.]+)( F\d+)?\s*$", l)
        if r and abs(float(r.group(2)) - sliced) < 1e-6:
            if r.group(1) == "-":
                level = math.floor(max(0.0, z - o.base) + 1e-6)
                length = min(o.start + level * o.step, o.end)
                seen.setdefault(round(length, 3), z)
                l = f"G1 E-{length:.3f}{r.group(3) or ''}\n" if length > 0 else ";retraction 0\n"
            elif length is not None:
                l = f"G1 E{length:.3f}{r.group(3) or ''}\n" if length > 0 else ";unretraction 0\n"
        out.append(l)
    open(o.dst, "w").writelines(out)
    for length, first_z in sorted(seen.items()):
        print(f"{length:.1f} mm from z {first_z:.1f}")


if __name__ == "__main__":
    main()
