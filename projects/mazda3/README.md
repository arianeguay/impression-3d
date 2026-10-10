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
| `mazda3-2018.stl` | upright on its wheels | under the underbody (from 1.7 mm up) and the mirrors | first print |

Height over the square root of contact: 23.2 / 7.0 = 3.3, under the ~5 where small parts topple.
