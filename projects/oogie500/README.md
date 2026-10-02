# Oogie Boogie at 500% (~22 cm)

The MakerWorld model "Oogie Boogie * 500% ~22 cm" (HeiHei) printed at its native size, in
Polymaker Panchroma Neon PLA (210 C, pressure advance 0.025), 0.2 mm layers. Parts were
exported with `scripts/export_3mf.py`; the arms were then laid on their edge. The designer printed it
in PLA on a multicolour machine; this one is single colour. Joints are the designer's, unchanged.

| Plate | Parts | Supports | Time | Filament |
|---|---|---|---|---|
| 1 | `Head_4.stl` | 3-layer raft (0.1 mm contact gap) + normal supports | 2 h 10 | 49 g |
| 2 | `Flosse_6_edge.stl`, `Flosse_7_edge.stl` (mirror pair) | raft + supports | 2 h 00 | 44 g |
| 3 | `Torso_9.stl`, `hip_2_lying.stl` | supports, no raft | 2 h 45 | 75 g |
| 4 | `Leg_11.stl`, `Leg_13.stl` (mirror pair) | supports, no raft | 1 h 40 | 51 g |

Supports: 0.3 mm top, bottom and XY gaps on plates 1 and 2; the user asked for a larger gap after
the arms, so plates 3 and 4 use 0.4 mm (two 0.2 mm layers). 45 degree threshold. Parts over 27 mm tall
cannot print by object on the AD5M (the head would hit finished parts), so each plate is one group.

Height over the square root of bed contact decided the rafts: head 17.5 (22 mm2 under an 83 mm
part), arms 10.7 in the file's pose. Torso 0.6, legs 2.7, hip 2.8 need none.

## What happened

- Head (plate 1, 2026-09-30): whole, watched end to end from apollon by `scripts/watch.py`.
- Arms in the file's pose (2026-10-01): each touched its raft on 15 mm2; the raft held and the
  arms went to spaghetti at 1.2 mm. `watch.py` saw it, confirmed it on a second frame a minute
  later, and cancelled 15 minutes in.
- Arms laid on their edge (`Flosse_6_edge.stl`, the stable pose with the most contact): 126 mm2 on
  the raft, ratio 4.0, weakest layer 56 mm2 at the tip. Clean past 2 mm, where the first try failed.
- Torso and hip, hip standing as in the file (2026-10-01, 0.4 mm support gaps): spaghetti at
  1.6 mm. Part of the hip's underside sat on supports whose first layer is spaced lines; per the
  user, holding it, the first layer lifted and the rest followed. Laid on its widest face
  (`hip_2_lying.stl`, 830 mm2 of solid part on the bed instead of 523, a quarter fewer supports,
  studs horizontal as on the minifig hip), after an alcohol wipe and with the enclosure lid off,
  the first layers went down flat.

## Second statue (2026-10-01)

- Head: completed with the plate 1 G-code. The palate inside the mouth came out full of
  spaghetti. Cause: the base Orca process sets `support_on_build_plate_only = 1`, so the mouth's
  roof, which would rest on the jaw, got no support at all.
- Arms face down (`arm_nice_A.stl` 64 mm2, `arm_nice_B.stl` 116 mm2 of raft contact; both lie on
  the same face, to give both arms the nicer outward side): the first try went to spaghetti at
  2 mm, and a second stopped before the raft. Cause: the Z offset was out of calibration; after a
  recalibration the pair printed clean. The result is worse than on the edge: the face on the
  supports is rough, and the shoulder stud fits loose.
- Torso + `hip_2_lying.stl` and legs: as on the first statue.

## For the third statue

- Arms: back to `Flosse_6_edge.stl` / `Flosse_7_edge.stl`. Face down is the worst pose, worse
  than the edge.
- Head (2026-10-02, `--set process.support_on_build_plate_only=0 --tree Head_4`, 3 h 12, 64 g):
  the palate came out clean, supported from the jaw. The tip, which is the bottom of the print
  and the head's only raft contact (22 mm2), came out open with infill showing: tree supports
  gave it a sparse contact where the normal supports of the first two heads gave a solid one.
  Next head: normal supports with `support_on_build_plate_only=0`, no `--tree`.
