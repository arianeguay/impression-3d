# Minifig skeleton at 500%

Source: `~/dev/3d-prints/models/Skeleton_Full.stl`, one plate of a LEGO-style skeleton at 1x (35 x 40 mm):
torso in one piece (ribs, spine, hip bar, shoulder balls, hollow neck stud), two legs (hip clip and foot),
two arms (shoulder clip and claw hand), skull. Printed at 5x in IEMAI Glow PETG (250 C, bed 65).

## Changes from the source, and why

`build.py <Skeleton_Full.stl> <out_dir>` does all of it.

| Change | Why |
|---|---|
| Scale 5x | 500% |
| Head socket 4.97 to 4.85 (24.25 at 500%, measures 24.17 to 24.23 on the faceted mesh), by moving its wall vertices | the neck stud is 24.0 at 500%: the source's 0.17 clearance becomes 0.85 and the head would flop; 0.16 is the Oogie head's fit. The head mesh has four non-manifold edges in its face, so no boolean |
| Each claw's fingertip pair moved 0.08 mm onto its arm and fused | they float off the arm; at 500% the gap is 0.4 mm and they would print as loose bits |
| Zero-volume shards dropped; the head keeps the ones cut off at its non-manifold edges | debris in the source |
| Legs: 1 mm cut off their rounded back | lying as designed they touch the plate on 19 mm2 at 32 mm tall (ratio 7.4); with the flat, 210 mm2 (2.1). Standing would put the hip clip across layers |
| Arms: the stable pose with the most contact whose clip plane stays within 15 degrees of flat | 54 mm2 instead of 10, clip tilted 11 degrees |

Clips and ball joints are left as designed: scaling every dimension by 5 keeps the strain of a snap the same.

## Prints

| File | Parts | Supports | Time | Filament |
|---|---|---|---|---|
| neck coupon v1 | `neck_stud.stl` (last 14 mm of the torso's neck stud, same height as on the torso), `head_ring.stl` (bottom 9 mm of the skull) | stud only | 42 min | 8 g |
| v1 | torso, both legs, both arms, head | all, grid, 0.4 mm gaps | 6 h 46 | 140 g |

The coupon answers whether PETG's fit on this printer moves the 0.16 clearance: in PETG a 4.9 neck stud
gripped a real LEGO head where PLA was loose, so studs come out fatter, not smaller.
