# Mazda3, 1:64

Sources: `~/dev/3d-prints/models/mazda3-2018.stl` (sedan) and `mazda3-2025.stl` (hatchback).
Both watertight and clean, unitless (about 1.17 long), five bodies each: the car and four wheels.
Printed in Flashforge Duramic PLA.

## Geometry changes from the source, and why

`build.py <src.stl> <real length mm> <out.stl>` does all of it:

| Change | Why |
|---|---|
| Scaled to real length / 64 (2018 sedan: 4580 mm, so 71.6 mm) | 1:64, the Hot Wheels scale |
| A 2.4 mm axle joins each wheel pair through the body | the wheels float 0.33 to 0.46 mm off the body, so they would print as loose parts |
| 0.3 mm cut off the bottom | the tires touch the plate on four lines; the cut gives four patches, 49 mm2 in all |

## Parts (`parts/`, scaled and oriented for printing)

| Part | Orientation | Supports | Status |
|---|---|---|---|
| `mazda3-2018.stl` | upright on its wheels | under the underbody (from 1.7 mm up) and the mirrors | v2 with a 3-layer raft: 2 h 23, 17.3 g, in black |
| `mazda3-2025.stl` | upright on its wheels (4460 mm hatchback, so 69.7 mm; 57 mm2 of contact, ratio 3.2) | same, plus a 3-layer raft from v2 | v1 failed, v2: 2 h 19, 17.7 g |

Height over the square root of contact: 23.2 / 7.0 = 3.3, under the ~5 where small parts topple.

## Prints

- 2025 v1 (2026-10-12, Duramic PLA, `figurine` 0.08 mm, supports, no raft): cancelled by the user at
  2.3 mm. The tire flats and most of the support base held and came off as one sheet; at one end the
  support base lines curled up and the nozzle dragged them into a tangle. Thin isolated 0.08 mm
  support lines in fast-cooled PLA curl; v2 adds a 3-layer raft so the tires and supports start on a
  solid base.
- 2025 v2 (raft): past v1's failure height cleanly; paused at 55% (about 11 mm) and stopped
  (2026-10-12, cause not recorded). The watcher answered "unsure" throughout: it cannot see dark
  filament on this plate.
