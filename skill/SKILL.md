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
| Printer | Flashforge Adventurer 5M, 0.4 nozzle, 220x220x220, firmware v5.1.8 |
| Printer IP, serial, LAN check code | `~/.config/impression-3d/printer.env` (never in git). The code is **lowercase** |
| Camera | MJPEG on `http://<ip>:8080/?action=stream`; `printer.py snapshot` saves one frame |
| Slicer | OrcaSlicer 2.3.1, Flatpak `io.github.softfever.OrcaSlicer` |
| Orca config | `~/.var/app/io.github.softfever.OrcaSlicer/config/OrcaSlicer/` (`user/default/{machine,process,filament}`) |
| Machine preset | `Flashforge Adventurer 5M 0.4 Nozzle - custom` (inherits the system AD5M 0.4 preset) |
| Profiles | `profiles/lego_minifig.json` (extends figurine), `profiles/figurine.json`: 0.08 mm layers, slow walls, grid supports at 0.3 mm gap, 45 degree threshold |
| Projects | `projects/<name>/`: final oriented parts plus a README of every geometry change and its evidence |

Filament presets the user has (both inherit the Flashforge generic of their type):

- `Polymaker Panchroma Neon PLA`: 210 C (215 first layer), bed 50, `#00F263`. Fluorescent under UV, does **not** glow in the dark.
- `IEMAI Glow PETG`: 250 C, bed 65, 10 mm3/s. Glow-in-the-dark pigment is abrasive.
- `Flashforge Duramic PLA`: 210 C.

A new filament preset: copy one of these JSONs in `user/default/filament/`, change `name`,
`filament_settings_id`, temps, colour, plus a matching `.info` (`base_id` = parent's `setting_id`).
Orca only reads presets at startup, so the user must fully quit and reopen it.

## Workflow

1. **Inspect the model before touching settings.** Unzip the 3MF with Python `zipfile`, read the
   designer description (`3D/3dmodel.model` metadata), `Metadata/project_settings.config` and
   `model_settings.config`. Measure parts with trimesh (scratch venv: `trimesh numpy shapely
   networkx scipy rtree`): bounding boxes, and `mesh.section()` slices to find studs, holes and pins.
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
7. **Record the project** in `projects/<name>/`: final parts and what changed, with the measurement
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
form (`0:/user/`, `/data/`, bare name) and deletes nothing. Deleting is done on the touchscreen. Pause/resume/cancel (`~M25`/`~M24`/`~M26`) are written but untested.

The HTTP API on 8898 (serial + lowercase check code from `printer.env`) does two things 8899
cannot: `/detail` (status, layer, ETA) and `/control` with `stateCtrl_cmd`/`setClearPlatform`, the only
remote way out of `BUILDING_COMPLETED`. `printer.py clear-platform` wraps it.

## What failed before, and the fix that worked

Measured on the Oogie Boogie Lego figure (MakerWorld, designed at 500%, printed at 20%):

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
- **A pocket whose ceiling overhangs gets filled with support, and its inside comes out rough.**
  Try rotations and pick the one that minimizes supported overhang (faces steeper than ~55 degrees
  down) while keeping the pocket walls vertical. Oogie's flipper arms went from 101 to 19 mm2 of
  supported surface standing on their thin tip, peg up, on a raft.
- **The user wants supports released at a 0.3 mm gap minimum** (top, bottom and XY); 0.2 welded in PETG.
- **Designers often model press fits at zero clearance.** Head socket = neck stud diameter, leg hole
  0.07 mm bigger than the pin. Scaling down shrinks the gap to nothing. Target **0.30 mm diametral
  clearance** by moving the hole's vertices radially, keeping the part itself at scale.
- **Every part of an assembly at one scale.** Different scales per part broke every joint.
- **Hollow studs with sub-mm walls snap off.** Real LEGO studs flex, printed ones shear at the base.
  Fill the hollow and slim the stud 0.1 mm. Print studs pointing up, never on the plate: the first
  layer's elephant foot makes the tip oversize, and the weak root ends up on supports.
- **Printed studs come out thinner than modeled.** A neck stud had to be modeled at 4.9 mm to grip a
  real LEGO head (official 4.8).
- **Tiny detailed figures: PLA over PETG.** PETG strings between parts and bonds to supports.
- **Bridges**: `bridge_no_support=1` keeps supports out of blind cavities (torso bottom, head socket)
  that must stay clear for a mating part.

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
5.0 x 5.0 and 1.9 deep. Keep at least 0.78 mm of wall; widen toward the thick side if the hole is
off-center.

A snap lip cannot work on a solid printed torso and a split 4 mm pin breaks when printed: use a
plain friction cylinder instead (3.85 mm peg in a 4.0 mm hole). A ball resting on a hole's rim holds
nothing at minifig scale.

A figure advertised "500%" is 5x a minifig: 20% brings it back, and the torso width confirms it.
