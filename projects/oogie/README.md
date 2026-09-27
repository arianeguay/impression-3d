# Oogie Boogie, LEGO minifig scale

Source: MakerWorld "Oogie Boogie * 500% ~22 cm" by HeiHei (`Oogie.3mf`), designed at 5x a minifig.
Printed at **20%** in Polymaker Panchroma Neon PLA with the `figurine` profile (0.08 mm layers).

## Parts (`parts/`, already scaled and oriented for printing)

| Part | Orientation | Supports | Status |
|---|---|---|---|
| `hip.stl` | lying on its front face, studs horizontal | a few under the studs, no raft | validated v12 |
| `leg_r.stl`, `leg_l.stl` | standing | none | validated v12 |
| `head.stl` | upright, socket down | raft + normal | validated v12 (PLA) |
| `torso.stl` | upright, neck stud up | none | shoulders accepted; neck raised to 5.0, printing in v13 |
| `arm.stl` (print two) | on its edge | raft + normal, 45 degree threshold | accepted v13; standing (v10) was clean inside but snapped at a 2.3 mm2 layer |

## Geometry changes from the source, and why

| Joint | Source | Now | Evidence |
|---|---|---|---|
| Neck stud | 4.76 x 3.4 mm | 5.0 x 4.8 mm | official 4.8 x 4.8; 4.76 loose, 4.9 gripped in PETG but was loose in PLA |
| Head socket | = stud (zero clearance) | 5.06 x 4.95 deep | fits both printed and real torsos |
| Hip top studs | hollow, 0.78 mm wall, 4.7 | solid D, 4.5 | hollow snapped; vertical ones snapped, so printed lying |
| Leg pin hole | 2.45 (0.07 clearance) | 2.50 (0.15 clearance) | 2.45 seized, 2.65 fell out, 2.50 clips |
| Foot hole | 4.70 x 4.90 x 1.47 | 5.1 x 5.1 x 1.9 | official 4.8 x 4.8 x 1.6; 5.0 fit "just" |
| Shoulder hole | 3.74 blind | 4.0 | official 4.0 |
| Arm joint | 4.4 ball on the hole rim | ball + 3.85 cylindrical peg | the ball alone fell out |

Clearance that grips but turns, measured on this printer: about **0.15 mm on the diameter**.
