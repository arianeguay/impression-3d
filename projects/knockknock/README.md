# KnockKnock espresso knock box

Source: `~/dev/3d-prints/models/KnockKnock+–+3D+Printed+Espresso+Knock+Box.zip`
(MakerWorld 1664933), three STLs: body (152 x 180 x 164 mm, open shell, 8 mm side walls), insert
(135 x 155 x 119 mm, the bin, 3 mm floor) and bar (24.6 mm diameter, 198 mm). The designer's TPU
bar sleeve is only in the profile's 3MF, so it was modelled here.

## Fit, measured on the source

| Feature | Value |
|---|---|
| Body inside width (between side walls) | 135.8 mm, insert 135.0: 0.4 mm a side |
| Bar notch | open U on top of each side wall, 26.4 mm wide at the bar's centre height: 1.8 mm over the bar, no room for a sleeve |
| Bar overhang | 23 mm past each outer wall face |

The sleeve sits between the side walls, so it must stay within about 30 mm of the bar's centre or
the bar's far end no longer reaches its notch.

## Prints (2026-10-16 to 2026-10-22)

- Body, unbranded red PETG, 240 C, bed 70, 3 walls, 15% gyroid, no supports: 8 h 25 actual
  against 9 h 34 sliced. Insert, unbranded grey PETG, same settings, 5 h 34 sliced, about 5 h 30.
- Bar v2, unbranded blue PETG, lying along X, grid supports at 0.6/0.5 mm gaps: 8 walls (3.6 mm
  shell) at 25% instead of 100%, about 75% of a solid bar's bending stiffness for 69 g against 125 g.
- Sleeve v2, Tronxy TPU (preset `Tronxy TPU`, Flashforge TPU 95A at 225 C, bed 45), upright,
  5 walls, 5 mm brim, 1 h 48, 25 g. Printed clean on the first try with the TPU.
  Bore modelled at 24.6 mm, the bar's own diameter: it went on but stuck a third of the way,
  and could not be pushed to the middle.
- Sleeve v3 (`parts/sleeve_v3.stl`, not printed yet): bore 25.0, wall 2.0, 130 mm long.
