# Vintage radio speaker (Alexa Dot vintage vertical 2.0)

Source: `~/Téléchargements/alexa_dot_vintage_vertical_2.0(2)_stls.zip`, three STLs: body
(`Assemblaggio`), grille (`griglia`), knob (`pomello`). Made for an Echo Dot; built here with the
same parts as the smart speaker (`projects/smart-speaker`): ESP32 DevKit V1, MAX98357, INMP441,
ACEIRMC 4 ohm 5 W speaker (51.6 mm frame).

## Parts, measured on the source

| Part | Size (mm) | Bed contact | Overhang > 45 deg | Notes |
|---|---|---|---|---|
| `body` | 128 x 195 x 125 | 22332 mm2 (back) | 6632 mm2, mostly chamfers at 45 deg under the front rim | 2 mm walls, open front. A 3.6 mm divider at y 46 to 50 splits a 124 x 34.5 bay (bottom, behind the knob band) from a 124 x 143.5 speaker chamber. 15 x 15 mm wire pass at the bottom of the divider. 15 mm cable hole in the back, inside the bay. Flat overhangs: a 7 mm ledge framing the bay's front opening, the feet's undersides |
| `grille` | 111 x 170 x 7.7 | 12835 mm2 (back) | 80 mm2 | front face up. Slot field over the speaker chamber; the bottom band has a 5.1 mm square knob hole and two slots (8.4 x 2.5, 4.7 x 2.9) |
| `knob` | 16 x 16 x 12 | 139 mm2 after flipping | 27 mm2 after flipping | 4.8 mm square stem into the 5.1 mm hole (0.15 mm a side) |

## Changes

- `knob.stl`: flipped so its cap's top face is on the plate. As designed it stood on its 18 mm2
  stem with 184 mm2 of cap overhanging; flipped it sits on 139 mm2 with 27 mm2 of overhang.
- `body_sealed.stl`: the divider raised from 107.25 to 117.5 mm, 0.5 mm under the grille, which
  rests on the rim's ledge at 118.1 (measured across the rim). As designed, a 10 mm gap over the
  divider let the speaker's sound straight into the mic bay; a plain ESP32 has no echo
  cancellation, unlike the Echo Dot. A 3.6 x 124 x 10.6 mm block in line with the wall, no new
  overhang (6632 to 6618 mm2), watertight, extents unchanged. Seal the 15 mm wire pass with hot
  glue once the wires are through.
- Nothing else changes. Every part fits as is:
  - the 51.6 mm speaker fits the 124 x 143.5 chamber, glued behind the slot field;
  - the ESP32 (51.5 x 28) and MAX98357 fit the 34.5 mm deep bay, taped to the back wall;
  - the INMP441 goes behind the grille's 8.4 x 2.5 slot, in the bay, away from the speaker;
  - the speaker wires cross through the divider's 15 mm pass;
  - a USB-C or micro-USB plug fits the 15 mm back hole.

## Print plan

| G-code | Filament | Time | Weight |
|---|---|---|---|
| `Vintage radio body - Overture PLA White - v2` (`body_sealed`) | `Overture PLA White` | 5 h 51 | 289 g |
| `Vintage radio grille and knob - Silk PLA Gold - v1` | `Silk PLA+ Pharaonic Gold` | 2 h 15 | 45 g |

`functional` profile (0.2 mm, 3 walls, 15% gyroid), no supports, as the designer printed it.
Every layer of every part carries model extrusion (checked in the G-code).
