---
name: 3d-print
description: Prepare, slice and send 3D prints to Ariane's Flashforge Adventurer 5M through OrcaSlicer, end to end. Use when the user shares a model (.3mf, .stl, MakerWorld/Printables link), asks to scale or fix a model, add a filament, tune print settings, slice, send a job to the printer, start/check/pause a print, or diagnose a failed print. Triggers - "imprime", "print this", "prépare le fichier", "envoie à l'imprimante", "statut de l'impression", "le print a fail".
---

# 3D printing on the Adventurer 5M

The user does not print often, and wants the whole job done through Claude: model in, G-code on the
printer, print started. Do the work; ask only for what needs eyes on the machine.

## The setup

Everything lives in the repo `~/dev/src/impression-3d` (this skill is its `skill/` folder, symlinked).
Prefer the **`impression-3d` MCP tools** when they are loaded (`printer_status`, `printer_camera`,
`printer_files`, `printer_upload`, `printer_clear_platform`, `printer_start`, `printer_job`,
`slice_models`); the scripts in `skill/scripts/` do the same from Bash.

| Thing | Value |
|---|---|
| Printer | Flashforge Adventurer 5M, 0.4 nozzle, 220x220x220, firmware v5.1.8, **official enclosure kit fitted** |
| Printer IP, serial, LAN check code | `~/.config/impression-3d/printer.env` (never in git). The code is **lowercase** |
| Camera | MJPEG on `http://<ip>:8080/?action=stream`; `printer.py snapshot` saves one frame |
| Slicer | **Two Flatpaks.** The user's GUI is `com.orcaslicer.OrcaSlicer` 2.4.2 (config `~/.var/app/com.orcaslicer.OrcaSlicer/...`); the scripts still drive the older `io.github.softfever.OrcaSlicer`. A preset added to one is invisible to the other: copy it to both. GUI calibration projects land in the 2.4.2 `log/` folder; `com.orcaslicer.OrcaSlicer` CLI slices them (the PA pattern is stored as custom G-code), and `retraction_steps.py` adds the per-mm retraction the CLI leaves out |
| Orca config | `~/.var/app/io.github.softfever.OrcaSlicer/config/OrcaSlicer/` (`user/default/{machine,process,filament}`) |
| Machine preset | `Flashforge Adventurer 5M 0.4 Nozzle - custom` (inherits the system AD5M 0.4 preset) |
| Profiles | `profiles/lego_minifig.json` (extends figurine), `profiles/figurine.json`: 0.08 mm layers, slow walls, grid supports at 0.3 mm gap, 45 degree threshold |
| Projects | `projects/<name>/`: final oriented parts plus a README of every geometry change and its evidence |

Filament presets the user has (both inherit the Flashforge generic of their type):

- `Polymaker Panchroma Neon PLA`: 205 C (215 first layer), bed 50, flow 0.98, pressure advance 0.045,
  retraction 0.8 mm, `#00F263`. All calibrated 2026-09-27, see `calibration/README.md`. Fluorescent
  under UV, does **not** glow in the dark.
- `IEMAI Glow PETG`: 250 C, bed 65, 10 mm3/s. Glow-in-the-dark pigment is abrasive.
- `Flashforge Duramic PLA`: 210 C.

A new filament preset: copy one of these JSONs in `user/default/filament/`, change `name`,
`filament_settings_id`, temps, colour, plus a matching `.info` (`base_id` = parent's `setting_id`).
Orca only reads presets at startup, so the user must fully quit and reopen it.

## Workflow

1. **Inspect the model before touching settings.** Unzip the 3MF with Python `zipfile`, read the
   designer description (`3D/3dmodel.model` metadata), `Metadata/project_settings.config` and
   `model_settings.config`. Measure parts with trimesh (the repo's `.venv` has `trimesh numpy scipy shapely
   manifold3d`): bounding boxes, and `mesh.section()` slices to find studs, holes and pins.
2. **Fix geometry by editing vertices**, not by scaling a part up or down to cheat a fit (see Fits).
3. **Slice with the Orca CLI** (recipe below) and read time, grams and per-object support placement
   out of the G-code. Never hand over an unsliced file as if it were verified.
4. **Send**: `scripts/printer.py upload <file.gcode> <short_name.gcode>`.
5. **One part per job while tuning an assembly.** The user asked for it after three mixed plates failed:
   a 10-minute single-part test isolates the fix and wastes nothing. Only batch parts that already printed well.
6. **Start only on an empty bed you have seen.** Failed parts left on the plate are the normal state
   after a failure. Look through `printer_camera` (or the user confirms), then `printer_clear_platform`
   if the last job is `BUILDING_COMPLETED`, then `printer_start`, then `printer_status` to confirm
   `BUILDING_FROM_SD`. The camera sees most of the plate but not its front edge: say so if in doubt.
7. **Watch the job and cancel on the first spaghetti, without asking.** When checking a running
   print, check the camera every 3 minutes for the first 15, then every 10: the v14 failure was
   already visible at 2 mm, on the first check. Loose strands or a part that stops rising is enough: `printer_job cancel` at once, then
   tell the user. On 2026-09-28 a full Oogie plate was flagged at 20 minutes and left running on a
   request for confirmation while the user was away; 40 minutes later nothing was recoverable.
8. **Record the project** in `projects/<name>/`: final parts and what changed, with the measurement
   that justified it, then commit.

Deliver files to `~/Téléchargements/`, versioned (`<model> - <filament> - v<N>.3mf/.gcode`).

## Slicing from the command line

The Flatpak sandbox cannot read `/tmp` or the Claude scratchpad: keep every input and output under
`$HOME` (a working folder in `~/Téléchargements/` works).

```bash
S=~/dev/src/impression-3d/skill/scripts
python3 $S/slice.py ~/Téléchargements/_slice head.stl torso.stl --profile figurine \
  --supported head --set process.support_top_z_distance=0.3
```

It prints the G-code path, time, grams and support moves per object (the check that supports
landed only where intended). `--supported` does the per-object 3MF edit described below.

What the CLI demands, each learned by a failure:

- **User presets as-is fail** ("unknown config type", then "process not compatible with printer").
  `orca_presets.py` merges the inherits chain, sets `type`, and puts both the machine name and its
  system parent in `compatible_printers`.
- **MakerWorld / Bambu Studio 3MFs fail** the version check (`File Version 2.6 not supported`), and
  patching the version makes it segfault. Export each object to STL with its build transform applied
  (flip triangle winding when the transform's determinant is negative), then slice the STLs.
- **Per-object settings** (supports on some parts only, a raft under one part): run the CLI once with
  `--export-3mf base.3mf` instead of `--slice`, add `<metadata key="enable_support" value="1"/>`
  (or `support_type`, `raft_layers`) under that object in `Metadata/model_settings.config`, then
  `--arrange 1 --slice 0` on the edited 3MF. An Orca-written 3MF slices fine.
- **"G-code conflicts detected"** means parts overlap once rafts/brims are added: slice with `--arrange 1`.
- `gcode_label_objects=1` is set by the script, so `; printing object <name>` and `;TYPE:` lines let
  you count support extrusions per object and prove supports landed only where intended.

## Talking to the printer

`scripts/printer.py` speaks the legacy protocol on TCP 8899, the same one Orca's Flashforge host
uses: `~M601 S1` login, `~M28 <size> 0:/user/<name>` then raw bytes in 4096-byte chunks, `~M29`
save, `~M23 0:/user/<name>` start, `~M119` state, `~M105` temps, `~M27` progress, `~M661` file list.
No access code needed. **After a job ends the printer sits in `BUILDING_COMPLETED`** until someone confirms on the touchscreen;
`~M23` and `~M24` are acknowledged and ignored meanwhile, so `printer.py start` refuses unless READY.
**Files cannot be deleted over the LAN:** `~M30` answers `ok` with any path
form (`0:/user/`, `/data/`, bare name) and deletes nothing. Deleting is done on the touchscreen. Pause/resume/cancel (`~M25`/`~M24`/`~M26`) are written but untested: after a cancel, confirm with `printer_status` that the state left `BUILDING_FROM_SD`.

The HTTP API on 8898 (serial + lowercase check code from `printer.env`) does two things 8899
cannot: `/detail` (status, layer, ETA) and `/control` with `stateCtrl_cmd`/`setClearPlatform`, the only
remote way out of `BUILDING_COMPLETED`. `printer.py clear-platform` wraps it.
**`/detail`'s layer counter does not follow the G-code.** The v14 plate ended `BUILDING_COMPLETED`
at `printLayer` 217 of 298 with the whole file executed (`printProgress` 1.0); layer 217 of that
G-code is at 11.98 mm, not the 17.32 mm top. `printProgress` is the position in the file: to know the
height being printed, find the last `;Z:` line before that fraction of the file's bytes.

## What failed before, and the fix that worked

Measured on the Oogie Boogie Lego figure (MakerWorld, designed at 500%, printed at 20%):

- **A whole plate that turns to spaghetti from the first layers is a dirty bed, not the file.** The
  final Oogie plate failed completely, with settings byte-identical to a plate that had just
  printed; a wipe with rubbing alcohol fixed it. Glue does not help adhesion here. Ask for a wipe
  before re-slicing anything.
- **Mixed plates of small parts failed where single parts did not.** The v14 plate (seven parts,
  1 h) went to spaghetti around the supported parts while each part had printed clean alone on a
  bed wiped the same way. Unresolved: a bed re-level was started afterwards. Until a mixed plate
  prints clean, print small parts one per job.
- **Tree supports on tiny parts turn into spaghetti.** Branches under 1 mm get knocked over. Glue
  does not help, since the plate bond is not what breaks. Use normal (grid) supports, plus a 3-layer
  raft on parts that sit on a point, and support only the parts that need it (per-object settings).
- **Measure every part's bed contact before deciding supports.** Section the mesh 0.1 mm above its
  lowest point and compare the area to the height. A part whose height over the square root of its
  contact area is above ~5 topples at small scale, even when its overhangs would print unsupported
  at full size: give it a raft and normal supports too. Measured: a 16.4 mm head on 2.4 mm2 and a
  12.8 mm hip on 2.3 mm2 both went to spaghetti without them, while a torso on 42 mm2 and legs on
  29 mm2 printed clean with none.
- **Start from the designer's orientation and the user's, not a clever one.** Flipping Oogie's hip
  studs-up put it on a raft and supports, and it split in two coming off them. Studs on the plate,
  as designed and as the user had said, needs no support at all: the block bridges between the studs.
  When the user names an orientation, restate it in geometric terms (which face touches the plate)
  before slicing.
- **Pegs and studs break across layers.** A vertical stud is a stack of discs and snaps at its root.
  Lay the part so its studs are horizontal: Oogie's hip studs fit a real torso but one snapped when
  printed vertical; lying on its front face they print along their length (33 mm2 contact, 7.7 mm tall).
- **Check the weakest layer before choosing an orientation.** Section the part every ~0.4 mm and take
  the smallest cross-section: Oogie's arm standing on its tip had a 2.3 mm2 layer and snapped there,
  on its edge the weakest is 17.7 mm2. Score candidates on weakest layer, supported area inside
  cavities (faces >0.4 mm inside the convex hull) and supported area on the visible outside, then pick.
- **A pocket whose ceiling overhangs gets filled with support, and its inside comes out rough.**
  Minimizing supported overhang alone is not enough: Oogie's flipper arm standing on its thin tip
  had the least support (19 mm2) and the cleanest pocket, and snapped at its 2.3 mm2 weakest layer.
  On its edge (weakest layer 17.7 mm2, supports split between pocket and outside) it printed whole.
- **The user wants supports released at a 0.3 mm gap minimum** (top, bottom and XY); 0.2 welded in PETG.
- **Designers often model press fits at zero clearance.** Head socket = neck stud diameter, leg hole
  0.07 mm bigger than the pin. Scaling down shrinks the gap to nothing. Fix it by moving the hole's
  vertices radially, keeping the part itself at scale. **Target ~0.15 mm on the diameter for a joint
  that must turn and stay on** (leg on hip pin: 0.07 seized, 0.30 slid off, 0.15 clips); the head
  socket sits at 0.16 over its stud. `standards/lego_minifig.json` holds the tested value per joint.
- **Every part of an assembly at one scale.** Different scales per part broke every joint.
- **Hollow studs with sub-mm walls snap off.** Real LEGO studs flex, printed ones shear at the base.
  Fill the hollow and slim the stud 0.1 mm, and print the part so the studs lie horizontal (see the
  layers bullet above); never with the stud tips on the plate, where the first layer's squish makes
  them oversize.
- **Printed studs come out thinner than modeled, and the material moves the number.** A neck stud
  modeled at 4.9 gripped a real LEGO head in PETG and was loose in PLA; 5.0 is the PLA value under test.
- **Tiny detailed figures: PLA over PETG.** PETG strings between parts and bonds to supports.
- **Bridges**: `bridge_no_support=1` keeps supports out of blind cavities (torso bottom, head socket)
  that must stay clear for a mating part.

## Calibrating a filament

Order: first layer, temperature, flow, pressure advance, retraction, then the LEGO fit coupon last
(fits move with flow and pressure advance). Results go in `calibration/README.md`, values into the
filament preset of **both** Orca installs.

| Test | How | Reading it |
|---|---|---|
| First layer | `calibration/first_layer_ad5m.stl`, one 0.2 mm layer | peel a square, hold it to the light: one sheet with no gaps = right; gaps = raise squish (`machine.z_offset`, now -0.02 in `figurine`) |
| Temperature | `scripts/temp_tower.py`: 9 levels of 6 mm, 230 down to 190, M104 inserted per level | bridge and 45 degree overhang per level, then try to break the coolest levels by hand |
| Flow, pass 1 | Orca GUI (the user sends it) | the labels on the tabs are unreadable in photos: map from `calib/filament_flow/flowrate-test-pass1.3mf` vertex centroids, back row +20/+15/+10, middle +5/0/-5, front -20/-15/-10. A visible ring on the top = under-extrusion. Take the lowest smooth one |
| Pressure advance | Orca GUI project from the 2.4.2 `log/` folder, sliced by its CLI (the pattern is stored as custom G-code) | chevron order read from the G-code: 0 next to the placeholder cube, +0.005 per chevron. The user's reading in hand beats a photo (photo said 8, hand said 10) |
| Retraction | Orca GUI tower sliced by the 2.4.2 CLI, then `retraction_steps.py` | 0 below 1.4 mm, then +0.2 mm per mm of height; take the lowest clean band, but do not lower a working value on a test that cannot tell values apart |
| LEGO fits | `calibration/lego_fit_coupon.stl` | tested against real LEGO parts and the user's printed hip and torso |

When the user sends a GUI job straight from Orca, the file name on the printer is Orca's
(`<test>_PLA_<time>.gcode.3mf`), and it prints with whatever filament the GUI had selected: check the
nozzle temperature in `printer_status` against the preset before trusting the result.

## LEGO minifigure reference

The machine-readable version, with what to **model** for each joint on this printer and the test
behind it, is `standards/lego_minifig.json`; slice minifig parts with `--profile lego_minifig`.
Update that file (and its evidence) whenever a fit is tested.

Official LDraw geometry (1 LDU = 0.4 mm; parts at `library.ldraw.org/library/official/parts/`, the
real shapes live in the `s/` subfiles, the patterned `.dat` only carry decals):

| Feature | mm |
|---|---|
| Torso bottom width x height x depth | 15.2 x 12.8 x 8.0 |
| Neck stud | 4.8 diameter, 4.8 tall above the torso |
| Hips width | 14.4 |
| Leg width | 7.2 |
| Hip top to sole | 16.0 |
| Shoulder hole | 4.0 diameter through a 0.8 mm wall (hollow torso) |
| Arm pin (`knob1.dat`) | 4.0 x 0.8 neck, then a 4.4 snap lip, split and hollow |
| Leg bottom hole (grips a plate stud) | 4.8 x 4.8 square, 1.6 deep |
| Plate stud | 4.8 diameter, 1.7 tall |

Printed holes come out about 0.15 mm small plus first-layer squish: model a stud-receiving hole at
5.1 x 5.1 and 1.9 deep (5.0 fit a baseplate only just, 5.1 fits). Keep at least 0.78 mm of wall; widen toward the thick side if the hole is
off-center.

A snap lip cannot work on a solid printed torso and a split 4 mm pin breaks when printed: use a
plain friction cylinder instead. 3.85 in the 4.0 hole was accepted but loose; the fit coupon tests
3.90/3.95/4.00. If friction is not enough, the next step is an acorn peg, which needs a deeper
shoulder hole with a groove, so a new torso. A ball resting on a hole's rim holds
nothing at minifig scale.

A figure advertised "500%" is 5x a minifig: 20% brings it back, and the torso width confirms it.
