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
  --supported head --no-raft hip
```

It prints the G-code path, time, grams and support moves per object (the check that supports
landed only where intended). `--supported NAME` gives that part supports and a 3-layer raft,
`--no-raft NAME` supports only, `--set kind.key=value` overrides one setting.

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
- **Mixed plates of small parts failed where single parts did not.** The v14 plate (seven parts,
  1 h, packed within 85 x 45 mm) went to spaghetti around the supported parts by 2 mm of height,
  while each part had printed clean alone on a bed wiped the same way. Unresolved: a bed re-level
  was started afterwards, and printing by object (`print_sequence`) with the parts spread out is
  the untested next step. Until a mixed plate prints clean, print small parts one per job.
- **Tree supports on tiny parts turn into spaghetti.** Branches under 1 mm get knocked over. Glue
  does not help, since the plate bond is not what breaks. Use normal (grid) supports, and support
  only the parts that need it (per-object settings).
- **The user wants supports released at a 0.3 mm gap minimum** (top, bottom and XY); 0.2 welded in PETG.
- **Bridges**: `bridge_no_support=1` keeps supports out of blind cavities (torso bottom, head socket)
  that must stay clear for a mating part.

## Calibrating a filament

Order: first layer, temperature, flow, pressure advance, retraction, then the LEGO fit coupon last
(fits move with flow and pressure advance). Results go in `calibration/README.md`, values into the
filament preset of **both** Orca installs. Each test is printed through print-run.

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
