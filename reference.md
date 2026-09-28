# Printing setup, shared by the print-design, print-prepare and print-run skills

The user does not print often, and wants the whole job done through Claude: model in, G-code on the
printer, print started. Do the work; ask only for what needs eyes on the machine.

The three skills are one flow: **print-design** (model in, oriented parts out) then **print-prepare**
(parts in, verified G-code out) then **print-run** (G-code in, finished or cancelled print out).

## Where things are

Everything lives in the repo `~/dev/src/impression-3d`; each skill is a folder of `skills/`,
symlinked into `~/.claude/skills/`. Prefer the **`impression-3d` MCP tools** when they are loaded
(`printer_status`, `printer_camera`, `printer_files`, `printer_upload`, `printer_clear_platform`,
`printer_start`, `printer_job`, `slice_models`); the scripts in `scripts/` do the same from Bash.
The repo's `.venv` has `trimesh numpy scipy shapely manifold3d` for mesh work.

| Thing | Value |
|---|---|
| Printer | Flashforge Adventurer 5M, 0.4 nozzle, 220x220x220, firmware v5.1.8, **official enclosure kit fitted** |
| Printer IP, serial, LAN check code | `~/.config/impression-3d/printer.env` (never in git). The code is **lowercase** |
| Camera | MJPEG on `http://<ip>:8080/?action=stream`; `printer.py snapshot` saves one frame |
| Slicer | **Two Flatpaks.** The user's GUI is `com.orcaslicer.OrcaSlicer` 2.4.2 (config `~/.var/app/com.orcaslicer.OrcaSlicer/...`); the scripts still drive the older `io.github.softfever.OrcaSlicer`. A preset added to one is invisible to the other: copy it to both |
| Orca config | `~/.var/app/io.github.softfever.OrcaSlicer/config/OrcaSlicer/` (`user/default/{machine,process,filament}`) |
| Machine preset | `Flashforge Adventurer 5M 0.4 Nozzle - custom` (inherits the system AD5M 0.4 preset) |
| Profiles | `profiles/lego_minifig.json` (extends figurine), `profiles/figurine.json`: 0.08 mm layers, slow walls, grid supports at 0.3 mm gap, 45 degree threshold |
| Projects | `projects/<name>/`: final oriented parts plus a README of every geometry change and its evidence |
| Standards | `standards/lego_minifig.json`: the tested value for every minifig joint on this printer |
| Calibration | `calibration/`: test models and `README.md`, the log of every calibration result |

Deliver files to `~/Téléchargements/`, versioned (`<model> - <filament> - v<N>.3mf/.gcode`).

## Filaments

Presets the user has (each inherits the Flashforge generic of its type):

- `Polymaker Panchroma Neon PLA`: 205 C (215 first layer), bed 50, flow 0.98, pressure advance 0.045,
  retraction 0.8 mm, `#00F263`. All calibrated 2026-09-27, see `calibration/README.md`. Fluorescent
  under UV, does **not** glow in the dark.
- `IEMAI Glow PETG`: 250 C, bed 65, 10 mm3/s. Glow-in-the-dark pigment is abrasive.
- `Flashforge Duramic PLA`: 210 C.

A new filament preset: copy one of these JSONs in `user/default/filament/` of **both** Orca installs,
change `name`, `filament_settings_id`, temps, colour, plus a matching `.info` (`base_id` = parent's
`setting_id`). Orca only reads presets at startup, so the user must fully quit and reopen it.

Tiny detailed figures: PLA over PETG. PETG strings between parts and bonds to supports.
