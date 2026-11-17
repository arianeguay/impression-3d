# Vintage speaker case for a JBL Charge 4

Source: `~/Téléchargements/Vintage+Speaker+for+JBL+Speaker.zip`, nine STLs: body (203.2 x 103.6 x
101.6 mm, open front, 3 mm walls), grille face, face rim, a 60 mm dial, three small knobs, a button
and one leg. The case was drawn for a smaller JBL (a Flip): `build.py` resizes it for a Charge 4 and
splits it for the 220 mm bed. Third-party STLs and outputs live in `parts/` (git-ignored); copy
the zip's STLs into `parts/source/` and run `build.py` to regenerate.

## Fit, measured on the source

| Feature | Source | Charge 4 (JBL spec) |
|---|---|---|
| Inner length | 197.2 | 221 |
| Inner height, floor to lid | 95.6, but a cradle on the floor reaches z 27 | 94 |
| Inner depth, open front to back wall | 100.6 | 94 |

The cradle is shaped for a ~70 mm cylinder: a 94 mm one rests on its edges, 4 mm higher, and no
longer fits under the lid.

## Changes

- **Cradle removed**: cut with the inner cavity's convex hull (vertices at least 2.5 mm inside the
  outer hull), so the end-wall fillets stay whole. The cradle's feet are wider than its section
  (y 15 to 70, z up to 27); a narrower first cut left two loose strips and 4 mm ramps.
- **+27 mm long, +3 mm tall, by insertion, not scaling**: a slab that repeats is copied and inserted,
  so corners, the dial hole and the grille stay as drawn. 27 and 3 are 9 and 1 grille pitches
  (3.0 mm, holes at x = 8.6 + 3k, z = 18.8 + 3k), with every cut between two holes. Body slab at
  x 80 to 107 (between the dial hole and the knob pad), face slab at x 73.1 to 100.1, rows at z 56.3
  to 59.3. Result: inner 224.2 x 98.6 x 100.6 mm, outer 230.2 x 104.6 x 103.6.
- **Split for the bed**: diagonal does not fit either, (230 + 104) x 0.707 = 236 mm. Body and face
  split at x 115.1 (between grille columns); rim split at x 70 so it bridges the case seam.
- **Glue tongues** on the left body half: five 20 x 1.5 mm tongues reaching 10 mm into the right
  half (floor and lid, front and back, plus the back wall), 0.1 mm off the mating wall. They sit
  away from where the speaker's cylinder touches.
- **"BOONE" script removed** from the grille: it stood 1 mm proud, so with the face printed front
  down the whole grille would hang over air.

## Print plan (sliced 2026-11-16, Creality CR-PETG, `functional` profile, 240 C, bed 70)

| Plate | Parts, face on the plate | Supports | Sliced |
|---|---|---|---|
| 1 | Body left, closed end down (tongues up) | grid, only under the end fillet (z 0 to 10) | 3 h 52, 140 g |
| 2 | Body right, closed end down | same | 3 h 56, 143 g |
| 3 | Both face halves front down, dial flat side down, knobs and button top down, 4 legs | legs only | 4 h 28, 39 g |
| 4 | Both rims, body side down | under the outer fillet | 46 min, 25 g |

The 55 mm dial hole ends up in a vertical wall and prints as a bridge: Orca put no support in it.
Every object has model extrusion on every layer of its height.

Not printed yet.
