# Minifig skeleton at 500%

Source: `~/dev/3d-prints/models/Skeleton_Full.stl`, one plate of a LEGO-style skeleton at 1x (35 x 40 mm):
torso in one piece (ribs, spine, hip bar, shoulder balls, hollow neck stud), two legs (hip clip and foot),
two arms (shoulder clip and claw hand), skull. Printed at 5x in IEMAI Glow PETG (250 C, bed 65).

## Changes from the source, and why

`build.py <Skeleton_Full.stl> <out_dir>` does all of it.

| Change | Why |
|---|---|
| Scale 5x | 500% |
| Head socket 4.97 to 4.85 (24.25 at 500%, measures 24.17 to 24.23 on the faceted mesh), by moving its wall vertices | the neck stud is 24.0 at 500%: the source's 0.17 clearance becomes 0.85 and the head would flop; 0.16 is the Oogie head's fit |
| Head: the four tiny edges (0.004 to 0.027 mm) that two sheets of the face share get their own vertex copies, nudged 0.002 mm into each sheet | v1 kept them and Orca printed no head layer from 8 to 12 mm: the head came out in two pieces. pymeshfix closed the mesh but filled in part of the nose and an eye. A copy left on the same point is merged back when the STL is read, hence the nudge |
| Shoulder clips: the two floating side walls (solid bodies 5 and 6) left out, gap unchanged (about 10 mm over the 10.8 mm ball at 500%) | v1 fused one wall across the clip and it cracked on both arms; a real LEGO skeleton arm has an open C clip at both ends, as the user's own piece shows. A coupon with the gap opened to 10.3 to 10.5 held without cracking but was too loose |
| Zero-volume shards dropped | debris in the source |
| Legs: 1 mm cut off their rounded back | lying as designed they touch the plate on 19 mm2 at 32 mm tall (ratio 7.4); with the flat, 210 mm2 (2.1). Standing would put the hip clip across layers |
| Arms: turned so the socket jaws part horizontally (within a layer), then 1 mm cut off the side on the plate | 264 mm2 of contact at 25.5 mm tall. The claw hand now flexes across layers; it holds nothing at this size |

Clips and ball joints are left as designed: scaling every dimension by 5 keeps the strain of a snap the same.

## Prints

| File | Parts | Supports | Time | Filament |
|---|---|---|---|---|
| neck coupon v1 | `neck_stud.stl` (last 14 mm of the torso's neck stud, same height as on the torso), `head_ring.stl` (bottom 9 mm of the skull) | stud only | 42 min | 8 g |
| v1 | torso, both legs, both arms, head | all, grid, 0.4 mm gaps | 6 h 46 | 140 g |

The coupon answers whether PETG's fit on this printer moves the 0.16 clearance: in PETG a 4.9 neck stud
gripped a real LEGO head where PLA was loose, so studs come out fatter, not smaller.

## Results

- Neck coupon v1 (2026-10-11, bed at 85 C: the preset's textured-plate temperature, inherited from
  the Flashforge generic PETG; its 65 C is the smooth-plate value): the head ring goes onto the stud
  "perfectly". The 24.25 socket over the 24.0 stud holds in Glow PETG, so v1 prints with it unchanged.
- Skeleton v1 (2026-10-11, 6 h 46): torso and legs usable, legs clip onto the hip bar. Head in two
  pieces (missing layers 8 to 12 mm, see the non-manifold edges above); neck fit confirmed on it.
  Both arms cracked at the shoulder socket when snapped on; one claw lost a finger. The legs' foot
  and band faces sat 7 mm up on supports (0.4 mm gap) and their skin tore off with the supports:
  PETG welds to supports at 0.4.
- Shoulder coupon v1: last 20 mm of `arm_a` as printed, to try on the v1 torso before the reprint.
- Shoulder coupon v1 (gap 10.3 to 10.5): no crack, but too loose on the torso's ball.
- Head and arms v3 (original gap, open clip, clip parting within a layer): supports at 0.6 mm (three
  0.2 mm layers) top and bottom, 0.5 mm XY; 2 h 34, 56 g.
