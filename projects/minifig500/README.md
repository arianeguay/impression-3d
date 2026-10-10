# Jumbo minifig, ~20 cm

Source: `~/dev/3d-prints/models/minifig-500%.3mf` (Bambu Studio, no designer description), printed by
its author on a P1S in four colours (yellow PLA, black/blue/red PETG), 0.2 mm layers. Despite the
name, the file is about **10x** a minifig (torso 154 mm wide against 15.2 official, head 102 mm):
printed at **50%**, which is the real 500%, the size of `oogie500`. One colour here: Polymaker
Panchroma Neon PLA in pink, with the green preset's settings.

Head: the one-piece blank (`head-solid-blank`, plate 7 of the source). The source's other plates are
alternative heads (two-piece, face inserts) and the face pins, not used.

## Geometry changes from the source, and why

`build.py <export_3mf.py output> <out_dir>` does all of it.

| Joint | Source at 50% | Now | Why |
|---|---|---|---|
| Connector pins (octagonal) | 2.5 across flats, holes 2.6 | 2.3 | 0.1 mm of clearance, and printed holes come out ~0.15 small: they would not go in |
| Head socket on neck stud | 23.9 over a 24.0 stud | 24.16 (cut as a cylinder up to 42.2, where the hollow head closes) | the socket was smaller than the stud; 0.16 over is the Oogie head's fit |
| Shoulder (arm peg in torso tube) | 10.1 in 10.3 | unchanged | 0.2 modelled, near the 0.15 that clips on this printer |

## Parts (`parts/`, scaled, in the designer's orientation)

| Part | Count | Height / sqrt(contact) | Supports |
|---|---|---|---|
| `torso.stl` | 1 | 2.8 | none |
| `hips.stl` | 1 | 0.8 | none |
| `hip_peg.stl` | 2 | 1.3 | none |
| `leg_l.stl`, `leg_r.stl` | 1 each | 2.6 | none |
| `arm_l.stl`, `arm_r.stl` | 1 each | 3.8 | none |
| `hand.stl`, `wrist.stl`, `limb_clip.stl` | 2 each | 1.4 to 2.3 | none |
| `head.stl` | 1 | 3.2 | normal, as the designer enabled them |
| `pin.stl` | 32 (the designer's count, spares included) | 0.9 | none |

Parts over 27 mm tall cannot print by object on the AD5M; in "by object" Orca 2.4.2 silently dropped
the arm, hand and wrist from the test plate. Slice these plates by layer.

## Prints

- Test plate v1: `arm_l`, `hand`, `wrist`, `limb_clip`, 8 pins, by layer, 0.2 mm standard process,
  47 min, 12.8 g. Checks the slimmed pins and the arm chain before the big parts.
