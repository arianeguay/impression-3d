# Plague doctor mask (wearable)

Source: `~/dev/3d-prints/models/plague+doc+mask_stls.zip`, ten STLs: the shell (face and beak,
153 x 196 x 183 mm, about 1.6 mm wall, laid face-opening down), two threaded eye rings (70 mm), two
knurled nuts (68 mm), three knurled filter caps (41 mm) and two vent caps (40 mm). All watertight.
Fit test in black Flashforge Duramic PLA; the mask itself in Creality CR-PETG.

## Fit, measured on the source

| Feature | Value |
|---|---|
| Face opening, inside | 149 x 191 mm |
| Eye hole centres | 74 mm apart, holes about 54 x 68 mm, rims up to 57 mm above the face edge |
| Largest scale that fits the 220 mm bed | about 112% |

The user's measurements, all with a soft tape over the skin: pupils 70 mm apart, face 22 cm wide
over the cheekbones, 26 cm from mid-forehead to under the chin, 28 cm ear to ear. She wears glasses
under the mask, so the fit at the temples (where the arms run) and in front of the lenses cannot be
read from tape measurements: a printed test decides the scale.

## Prints

- Face band v1: the shell's first 15 mm (`parts/face_band.stl`), the edge that meets the face, to try
  on with glasses. It leans inward enough to need supports (about 3200 mm2 over 45 degrees);
  without them it would droop. 0.2 mm standard process, 1 h 14, 28 g. A cut at 60 mm (whole eye
  area) sliced to 4 h 24 and 114 g, half the mask, so it was dropped.
- Face band v1 result (2026-10-15): the size is right with glasses, so the mask prints at 100%.
- Shell v1, Creality CR-PETG (240 C, bed 70): tree supports at 0.6 mm gaps (the beak is a long
  cavity that grid supports would fill solid), 5 mm outer brim to hold the 1.6 mm face edge down.
  3 h 41, 80 g; grid supports had sliced to 6 h 37 and 180 g in PLA.
- Shell v1 result (2026-10-16): first start printed in the air (filament not loaded right; the
  watcher answered "ok, plate empty" at 0%, it cannot tell a dry start from a real one). Second
  start: the shape is right and is kept, but the slim tree supports turned into spaghetti, with
  strings across every supported area that were cut off by hand. See print-prepare.
