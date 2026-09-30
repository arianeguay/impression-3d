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
| Neck stud | 4.76 x 3.4 mm | 4.9 x 4.8 mm | official 4.8 x 4.8; after PLA calibration the fit coupon picked 4.9 of 4.9/5.0/5.1 |
| Head socket | = stud (zero clearance) | 5.06 x 4.95 deep | fits both printed and real torsos |
| Hip top studs | hollow, 0.78 mm wall, 4.7 | solid D, 4.5 | hollow snapped; vertical ones snapped, so printed lying |
| Leg pin hole | 2.45 (0.07 clearance) | 2.50 (0.15 clearance) | 2.45 seized, 2.65 fell out, 2.50 clips |
| Foot hole | 4.70 x 4.90 x 1.47 | 5.1 x 5.1 x 1.9 | official 4.8 x 4.8 x 1.6; 5.0 fit "just" |
| Shoulder hole | 3.74 blind | 4.0 | official 4.0 |
| Arm joint | 4.4 ball on the hole rim | ball + 3.90 cylindrical peg | the ball fell out, 3.85 was loose, the coupon picked 3.90 |

Clearance that grips but turns, measured on this printer: about **0.15 mm on the diameter**.

## Reprint for a friend, 2026-09-28 to 2026-09-29

- v14 (full plate, by layer, calibrated 205 C / PA 0.045 / z -0.02, Orca 2.0.0): all spaghetti.
- v15 (by object, spread out, Orca 2.4.2, same calibrated values): hip and one leg printed; both
  arms and the head let go of their rafts, the other leg failed.
- v16 (head alone, same values): failed near the base.
- v17 (head alone, 210 C / PA 0.025 / no z offset): clean up to the eyes, then the lower half left
  the raft.
- v18 (as v17, raft contact gap 0.1 instead of 0.2): **whole and clean**.
- v19 (one arm alone, same settings): whole. Fits the old torso a little better, not perfectly.
- v20 (arm, right leg, torso, by object, spread out): all three whole. The second Oogie's parts are
  complete; fits on the new torso still to be judged.
