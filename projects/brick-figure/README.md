# Basic Big Brick Figure V3, ~20 cm

Source: `~/dev/3d-prints/models/BASIC_BIG_BRICK_FIGURE_V3_stls/` (nine STLs, no description), already
at about 5x a minifig (torso 77 mm wide). Chosen over `minifig500` for having no connector pins and
fewer parts. Printed in Polymaker Panchroma Neon PLA in pink, with the green preset's settings.
Blank head (`obj_7_head`); the face head and its eye/mouth inserts are not used.

## Joints, measured

| Joint | Source | Now | Why |
|---|---|---|---|
| Head socket on neck stud | narrows to 25.34 over a stud of up to 25.47 (a snap) | 25.65 up to 14.5 mm (`build.py`) | 0.1 interference becomes ~0.25 once printed holes come out small: the head would not go on in PLA |
| Hand stem in arm | stem tapers 12.15 to 13.07, hole 13.09 to 12.66 | unchanged | a designed taper: it wedges near the mouth of the hole |
| Leg on waist axle | axle 11.81, leg hole 12.0 | unchanged | 0.19, near the 0.15 that clips on this printer |
| Shoulder pegs | split, ~20 mm, fused into the arms (overlapping shells) | unchanged | big enough to flex at this size |
| Hip studs into torso | two loose tubes (`obj_5`, 22.38 OD) ending in a 4.75 mm peg that fills a 11.76 hole in the waist, peg and hole at the same diameter | fused onto the waist as `hip.stl` | one part, nothing to glue; the waist holes (+-15.77) sit on the torso's stud pockets (+-15.79, 22.0 wide) |

The Oogie 500% hip was considered instead: its leg pins (11.86) fit these legs (12.0) and its axle sits
within 1.2 mm of this one, but its studs are 23.5 wide at +-23.5 mm, so they cannot enter this torso.

## Plates (designer's orientation, 0.2 mm standard process, grid supports with 0.4 mm gaps)

| Plate | Parts | Supports | Time | Filament |
|---|---|---|---|---|
| A | torso, head, hip | head and hip only, `support_on_build_plate_only=0` so the hip axle (which sits over the waist plate, not the bed) gets them; the hip stands on its studs (406 mm2), supports under the waist face that meets the torso | 3 h 43 | 105 g |
| B | legs, arms, hands | auto, build plate only; 5 mm brim (hands stand 57 mm on a 131 mm2 stem tip) | 3 h 46 | 101 g |

The torso needs no support: its only overhang is the shoulder tunnel's ceiling, a 16 mm bridge. With
supports on, Orca filled the whole inside of the torso with them from 0 to 55 mm.
