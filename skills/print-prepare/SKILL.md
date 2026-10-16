---
name: print-prepare
description: Slice parts into verified G-code for Ariane's Flashforge Adventurer 5M with the OrcaSlicer CLI, manage Orca filament presets and profiles, and calibrate a filament. Use when parts are ready to slice, the user asks to add or tune a filament, change print settings (layer height, supports, raft, speed), or run a calibration test (first layer, temperature, flow, pressure advance, retraction, fit coupon). Triggers - "slice", "ajoute ce filament", "change les settings", "calibration", "tour de température". Hands off to print-run.
---

# Preparing G-code

Read `~/dev/src/impression-3d/reference.md` first: setup, filaments, profiles.
This skill ends with a G-code file whose time, grams and support placement were read out of it.
Never hand over an unsliced file as if it were verified. Then use **print-run** to send it.

## Slicing from the command line

The Flatpak sandbox cannot read `/tmp` or the Claude scratchpad: keep every input and output under
`$HOME` (a working folder in `~/Téléchargements/` works).

```bash
S=~/dev/src/impression-3d/scripts
python3 $S/slice.py ~/Téléchargements/_slice head.stl torso.stl --profile lego_minifig \
  --supported head --supported hip --no-raft hip
```

It prints the G-code path, time, grams and support moves per object (the check that supports
landed only where intended). `--supported NAME` gives that part supports and a 3-layer raft,
`--no-raft NAME` drops the raft from a part that is also `--supported` (alone it gives that part no
supports at all, silently: the first Mazda slice came out with none), `--set kind.key=value`
overrides one setting.

What the CLI demands, each learned by a failure:

- **User presets as-is fail** ("unknown config type", then "process not compatible with printer").
  `orca_presets.py` merges the inherits chain, sets `type`, and puts both the machine name and its
  system parent in `compatible_printers`.
- **MakerWorld / Bambu Studio 3MFs fail** the version check (`File Version 2.6 not supported`), and
  patching the version makes it segfault. Slice the STLs print-design exported.
- **Per-object settings** (supports on some parts only, a raft under one part): run the CLI once with
  `--export-3mf base.3mf` instead of `--slice`, add `<metadata key="enable_support" value="1"/>`
  (or `support_type`, `raft_layers`) under that object in `Metadata/model_settings.config`, then
  `--arrange 1 --slice 0` on the edited 3MF. An Orca-written 3MF slices fine. `slice.py` does this.
- **"G-code conflicts detected"** means parts overlap once rafts/brims are added: slice with `--arrange 1`.
- `gcode_label_objects=1` is set by the script, so `; printing object <name>` and `;TYPE:` lines let
  you count support extrusions per object and prove supports landed only where intended.

## Settings that failed before

- **One part per job while tuning an assembly.** The user asked for it after three mixed plates
  failed: a 10-minute single-part test isolates the fix and wastes nothing. Only batch parts that
  already printed well.
- **A plate of several small parts prints by object, spread out.** `--set process.print_sequence="by object"`
  finishes one part before starting the next, and Orca spreads them over the bed. On v15 three of
  seven parts failed and none took another down, where the v14 plate (by layer, packed within
  85 x 45 mm) lost everything. It costs time: 1 h 40 against 1 h, since a lone tiny part waits on
  its minimum layer time. Add `process.reduce_crossing_wall=1` and `process.z_hop=0.6`. With the
  0.1 mm raft gap and 210 C, the v20 plate (arm on a raft, leg, torso) printed every part whole.
  **Only for parts under ~27 mm tall:** by object, Orca 2.4.2 silently left the 50 mm arm, the hand
  and the wrist off a jumbo-minifig plate and sliced the rest. Count `; printing object` per part.
- **Check every part has model extrusion on every layer.** A mesh with non-manifold edges slices
  without an error but with empty layers: the 500% skeleton head printed in two pieces, with no head
  layer from 8 to 12 mm, only its supports. Sum the non-`Support` extrusion per object per `;Z:` and
  flag any layer inside the part's height where it is zero.
- **PETG welds to supports at a 0.4 mm gap.** The skeleton legs' faces that sat on supports lost
  their skin with them. Use 0.6 mm (three 0.2 mm layers) top and bottom, 0.5 mm XY, for PETG.
- **Compare a failed G-code with one that printed, setting by setting, before guessing.** Diff the
  `; key = value` header lines of the two files: the v14 and v15 failures differed from the plate
  that printed Oogie whole by exactly three values, all from a calibration.
- **Orca 2.4.2 changed a default under the same profile**: `slowdown_for_curled_perimeters` went
  from 1 (Orca 2.0.0) to 0. `figurine` sets it back to 1, since small overhangs are where it matters.
  A slicer upgrade is a settings change: diff a G-code from each version.
- **Tree supports on tiny parts turn into spaghetti.** Branches under 1 mm get knocked over. Glue
  does not help, since the plate bond is not what breaks. Use normal (grid) supports, and support
  only the parts that need it (per-object settings).
- **Slim tree supports in PETG turn into spaghetti on a large part too.** The plague mask shell
  (2026-10-15, CR-PETG, `support_style = tree_slim`, `support_speed = 150`, retraction 0.8 mm)
  came out with the right shape but strings across every supported area, cut off by hand. Not yet
  separated: branches knocked over at speed, or PETG oozing on the travels between many thin
  branches. Never use `tree_slim` with PETG. Try `tree_strong` with `support_speed` at 60 or below,
  and check the strings on the camera at the first branches; if they come back, use grid supports
  and pay the time (the shell sliced to 6 h 37 in grid against 3 h 41 in trees).
- **The user wants supports released at a 0.3 mm gap minimum** (top, bottom and XY); 0.2 welded in PETG.
  At 0.2 mm layers the user asked for 0.4 (two whole layers) after the 500% arms (2026-10-01).
- **The raft contact gap is a different setting, and 0.1 is what holds a small part on its raft.**
  `raft_contact_distance` (now 0.1 in `figurine`) is the gap between the raft and the part, not the
  support gap. At 0.2 the Oogie head (upright on the ring around its neck socket) and an arm on
  its edge let go of the raft once they were 8 to 10 mm tall; at 0.1 the head printed whole in PLA.
  Cost: a rougher ring where the raft was, filed off, and hidden on the neck anyway.
- **Bridges**: `bridge_no_support=1` keeps supports out of blind cavities (torso bottom, head socket)
  that must stay clear for a mating part.

## Calibrating a filament

Order: first layer, temperature, flow, pressure advance, retraction, then the LEGO fit coupon last
(fits move with flow and pressure advance). Results go in `calibration/README.md`, values into the
filament preset in Orca. Each test is printed through print-run.

**A calibration on test pieces does not carry over to tiny parts by itself.** The Panchroma
calibration of 2026-09-27 (205 C, pressure advance 0.045, -0.02 mm z offset) read clean on a
temperature tower whose levels are 26 x 14 mm, and small figure parts on rafts failed with it on
three plates in a row. Before adopting a calibrated value for figurines, print one small raft part
(the Oogie head is the hardest) with it; until then keep the values that already printed the figure.

| Test | How | Reading it |
|---|---|---|
| First layer | `calibration/first_layer_ad5m.stl`, one 0.2 mm layer | peel a square, hold it to the light: one sheet with no gaps = right; gaps = raise squish (`machine.z_offset`, now -0.02 in `figurine`) |
| Temperature | `scripts/temp_tower.py`: 9 levels of 6 mm, 230 down to 190, M104 inserted per level | bridge and 45 degree overhang per level, then try to break the coolest levels by hand |
| Flow, pass 1 | Orca GUI (the user sends it) | the labels on the tabs are unreadable in photos: map from `calib/filament_flow/flowrate-test-pass1.3mf` vertex centroids, back row +20/+15/+10, middle +5/0/-5, front -20/-15/-10. A visible ring on the top = under-extrusion. Take the lowest smooth one |
| Pressure advance | Orca GUI project from the 2.4.2 `log/` folder, sliced by its CLI (the pattern is stored as custom G-code) | chevron order read from the G-code: 0 next to the placeholder cube, +0.005 per chevron. The user's reading in hand beats a photo (photo said 8, hand said 10) |
| Retraction | Orca GUI tower sliced by the 2.4.2 CLI, then `scripts/retraction_steps.py` | 0 below 1.4 mm, then +0.2 mm per mm of height; take the lowest clean band, but do not lower a working value on a test that cannot tell values apart |
| LEGO fits | `calibration/lego_fit_coupon.stl` | tested against real LEGO parts and the user's printed hip and torso |

GUI calibration projects land in the 2.4.2 `log/` folder, and the `com.orcaslicer.OrcaSlicer` CLI
slices them. When the user sends a GUI job straight from Orca, the file name on the printer is
Orca's (`<test>_PLA_<time>.gcode.3mf`), and it prints with whatever filament the GUI had selected:
check the nozzle temperature in `printer_status` against the preset before trusting the result.
