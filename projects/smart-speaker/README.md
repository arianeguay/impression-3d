# Smart speaker (Bambu Lab)

Source: `~/dev/3d-prints/models/Smart+Speaker+-+Bambu+Lab_stls.zip`, nine STLs, already laid
flat in print orientation. Every part is watertight and fits the 220 mm bed. The model is the
Vesper voice satellite (ReSpeaker Lite + XIAO ESP32-S3, MAX98357A, 2 in 5 W speaker, a 4-LED
WS2812B strip, 20 magnets of 6 x 2 mm); its build notes are in the PDF the user downloaded.
Parts are renamed in `parts/` (the zip names are Fusion body numbers).

## Parts, measured on the source

| Part (zip name) | Size (mm) | Bed contact | Overhang > 45 deg | What it is |
|---|---|---|---|---|
| `front` (Body_13) | 166 x 69 x 10 | 6559 mm2 | 588 mm2, of which 297 are 6 mm square bridges at 2.1 mm | front panel: speaker hole, mic grille window (82 x 29), 3 LED windows (5.3 mm, 16.7 mm apart = the strip's pitch), 10 magnet pockets (6.1 mm, 2.1 deep). Outer face on the plate |
| `body` (Body_29) | 171 x 80 x 63 | 12642 mm2 | 916 mm2, slopes at 45 deg and one 0.5 mm bridge strip, between 39 and 56 mm | open box, back face on the plate, USB notch |
| `grille` (Body_02) | 67 x 67 x 6 | 3773 mm2 | 119 mm2 of 6 mm bridges | speaker grille, 121 holes |
| `ring_155x41` (Body_08 (2)) | 155 x 41 x 3 | 1057 mm2 | 0 | stadium-shaped ring |
| `plate_96x46` (Body_08) | 96 x 46 x 3 | 1891 mm2 | 119 mm2 | plate with a stadium cutout, 4 screw holes |
| `strip_96x20` (Body_10) | 96 x 20 x 3 | 1836 mm2 | 59 mm2 | strip, 2 screw holes and 3 small holes |
| `cover_86x36` (Body_02 (2)) | 86 x 36 x 3 | 2817 mm2 | 0 | solid stadium plate |
| `cap_a`, `cap_b` (Body_06) | 17 x 19 x 3 | 299 mm2 | 3 mm2 | small square caps, one hole each |

Every part sits on a large flat face (height over the square root of its contact area is under 1),
and the only overhangs are short bridges and 45 deg slopes: no supports, no raft.

## Changes

- `front_noled.stl`: the three LED windows filled (5.8 x 5.8 x 3.0 mm boxes unioned with
  manifold3d, the panel being 3.0 mm thick there), since this build has no LED strip
  (2026-11-16). Bottom-face holes 17 to 14, volume +259 mm3 against 253 for the three windows,
  still watertight.

## Hardware swap (pending)

The user's parts replace the ReSpeaker Lite and XIAO with INMP441 mics and an ESP32 board, and
use an ACEIRMC 4 ohm 5 W speaker. Speaker frame measured at 51.6 mm square (2026-11-16): the
front's speaker hole is 50.0 mm round, centred 34.6 mm from both edges, so the frame spans 8.8 to
60.4 mm and clears the magnet pockets (2.1 to 8.1 and 61.1 to 67.1) and the body's 69.3 mm inner
width. Four lobes at 45 deg reach r = 32.7 mm: screw slots for frame holes about 38 to 44 mm apart
(M3). The ESP32 mount waits on the board name.

## Print plan

- White PLA. The designer asks for supports on for the magnet pockets and dark accent parts
  against LED bleed; without LEDs, white is fine.
- `front` on the smooth PEI plate, for a glossy visible face (user's choice, 2026-11-16).
  Flashforge: Z offset +0.1 mm on smooth PEI. The plate failed its one earlier use.
- `body` on the textured plate.
