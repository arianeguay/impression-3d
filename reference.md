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
| Power | Tuya Mini Smart Plug in Home Assistant (`hestia`), device "Imprimante 3D", entity `switch.bureau_imprimante_3d_socket_1` (was `switch.clim_salon_socket_1` until the hestia move; turning on a missing entity still answers 200 with `[]`, so read the state back). On/off only, no power reading. `HA_URL` and `HA_TOKEN` are in `printer.env`. Tested 2026-09-28: off drops the printer from the LAN, on brings it back `READY` in about 50 s |
| Camera | MJPEG on `http://<ip>:8080/?action=stream`; `printer.py snapshot` saves one frame. A USB lamp on top of the printer, powered by it, lights the whole plate (2026-09-29). It stays on through the printer's auto-shutdown but **not** through a power cut from the HA plug: after `turn_on` it has to be switched on by hand, or frames are near black. The printer cannot see it (`lightStatus` is the built-in LED) |
| Slicer | `com.orcaslicer.OrcaSlicer` 2.4.2 (Flatpak), the user's GUI and the scripts' CLI. The older `io.github.softfever.OrcaSlicer` 2.0.0 is no longer used: its AD5M start G-code heats the nozzle with `M104` and purges without waiting, where 2.4.2 waits with `M109`. Every Oogie part up to v14 was sliced by 2.0.0 |
| Orca config | `~/.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/` (`user/default/{machine,process,filament}`) |
| Machine preset | `Flashforge Adventurer 5M 0.4 Nozzle - custom` (inherits the system AD5M 0.4 preset) |
| Profiles | `profiles/lego_minifig.json` (extends figurine), `profiles/figurine.json`: 0.08 mm layers, slow walls, grid supports at 0.3 mm gap, 45 degree threshold |
| Projects | `projects/<name>/`: final oriented parts plus a README of every geometry change and its evidence |
| Standards | `standards/lego_minifig.json`: the tested value for every minifig joint on this printer |
| Calibration | `calibration/`: test models and `README.md`, the log of every calibration result |

Deliver files to `~/Téléchargements/`, versioned (`<model> - <filament> - v<N>.3mf/.gcode`).

## Filaments

Presets the user has (each inherits the Flashforge generic of its type):

- `Polymaker Panchroma Neon PLA`: 210 C (215 first layer), bed 50, flow 0.98, pressure advance 0.025,
  retraction 0.8 mm, `#00F263`, and the `figurine` profile has no z offset. Fluorescent under UV,
  does **not** glow in the dark. These are the values that printed the first Oogie whole
  (2026-09-27). The calibration of 2026-09-27 moved them to 205 C, pressure advance 0.045 and a
  -0.02 mm z offset (`calibration/README.md`); with exactly those three changes the v14, v15 and v16
  plates lost every small part on a raft, so the preset went back on 2026-09-28 (copy of the
  calibrated preset: `Polymaker Panchroma Neon PLA.json.bak-205` in Orca's filament folder).
  The revert alone was not enough: head v17 (210 C) printed clean up to the eyes, then its lower half
  came off the raft. Head v18 added a 0.1 mm raft contact gap and printed whole (2026-09-29).
- `IEMAI Glow PETG`: 250 C, 10 mm3/s. The bed actually runs at **85 C**: the AD5M plate is textured
  and the preset's `textured_plate_temp` (85, inherited from the Flashforge generic PETG) wins over its
  65 C `hot_plate_temp`; IEMAI says 60 to 70. The skeleton neck coupon fitted at 85. Dry it 8 to 10 h
  at 70 C (IEMAI). Supports need 0.6 mm gaps (see print-prepare). Glow pigment is abrasive.
- `Flashforge Duramic PLA`: 210 C.

A new filament preset: copy one of these JSONs in `user/default/filament/`,
change `name`, `filament_settings_id`, temps, colour, plus a matching `.info` (`base_id` = parent's
`setting_id`). Orca only reads presets at startup, so the user must fully quit and reopen it.

Tiny detailed figures: PLA over PETG. PETG strings between parts and bonds to supports.

The user also has a smooth PEI plate, without its handle, used once and failed. Flashforge: after
levelling on smooth PEI, set the Z offset to +0.1 mm (the textured plate's settings over-squish it).
No PETG directly on it (it can tear the PEI); a glue stick layer as release if needed.
