#!/usr/bin/env python3
"""Say which part and height a running print is at, and the time left, from the local G-code.

usage: where.py <the .gcode that was uploaded>

The printer's layer counter does not follow the G-code; printProgress is the position in the file.
The last `; printing object`, `;Z:` and `M73 R` lines before that position answer the question.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import printer  # noqa: E402


def where(gcode, fraction):
    size, pos, part, z, left = os.path.getsize(gcode), 0, None, 0.0, None
    with open(gcode, "rb") as f:
        for line in f:
            pos += len(line)
            if m := re.match(rb"; printing object (\S+)", line):
                part = m.group(1).decode()
            elif m := re.match(rb";Z:([\d.]+)", line):
                z = float(m.group(1))
            elif m := re.match(rb"M73 P\d+ R(\d+)", line):
                left = int(m.group(1))
            if pos >= fraction * size:
                break
    return part, z, left


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    d = printer.http("/detail")["detail"]
    part, z, left = where(sys.argv[1], d["printProgress"])
    print(f'{d["status"]} {d["printProgress"]:.1%} part={part} z={z} mm left={left} min '
          f'nozzle={d["rightTemp"]:.0f} bed={d["platTemp"]:.0f}')


if __name__ == "__main__":
    main()
