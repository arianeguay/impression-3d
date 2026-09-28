---
name: print-run
description: Send G-code to Ariane's Flashforge Adventurer 5M over the LAN, start it on a bed seen empty, watch it through the camera, cancel it on failure, and diagnose a failed print. Use when a G-code is ready to print, the user asks to send, start, check, pause or cancel a print, clean up files on the printer, or reports a print that failed. Triggers - "envoie à l'imprimante", "part l'impression", "statut de l'impression", "check le print", "le print a fail", "plateau vide".
---

# Running a print

Read `~/dev/src/impression-3d/reference.md` first: printer, camera, credentials.
This skill ends with a print finished or cancelled, and the user told which. A failure caused by
geometry goes back to **print-design**, one caused by settings to **print-prepare**.

## Steps

1. **Send**: `printer_upload` (or `scripts/printer.py upload <file.gcode> <short_name.gcode>`).
2. **Start only on an empty bed you have seen.** Failed parts left on the plate are the normal state
   after a failure. Look through `printer_camera` (or the user confirms), then `printer_clear_platform`
   if the last job is `BUILDING_COMPLETED`, then `printer_start`, then `printer_status` to confirm
   `BUILDING_FROM_SD`. The camera sees most of the plate but not its front edge: say so if in doubt.
3. **Watch the job and cancel on the first spaghetti, without asking.** Check the camera every
   3 minutes for the first 15, then every 10: the v14 failure was already visible at 2 mm, on the
   first check. Loose strands or a part that stops rising is enough: `printer_job cancel` at once,
   then confirm with `printer_status` that the state left `BUILDING_FROM_SD`, then tell the user.
   On 2026-09-28 a full Oogie plate was flagged at 20 minutes and left running on a request for
   confirmation while the user was away; 40 minutes later nothing was recoverable.
4. **When it ends**, say so and ask for a photo of the parts before judging a fit or a surface.

## Diagnosing a failure

- **A whole plate that turns to spaghetti from the first layers is a dirty bed, not the file.** The
  final Oogie plate failed completely, with settings byte-identical to a plate that had just
  printed; a wipe with rubbing alcohol fixed it. Glue does not help adhesion here. Ask for a wipe
  before re-slicing anything.
- **Read the camera photos in order.** The first one that shows strands dates the failure: at 2 mm
  it is adhesion, a raft or supports; a part that grew then fell is a knock-over or a weak layer.
  Map photos to heights with `printProgress` (below), and parts to plate positions with the
  G-code's `; printing object` coordinates.
- A part that broke or toppled because of its shape, or a joint that does not fit: print-design.

## Power

The printer's plug is a Home Assistant switch (see `reference.md`):

```bash
set -a; . ~/.config/impression-3d/printer.env; set +a
curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  -d '{"entity_id":"switch.clim_salon_socket_1"}' "$HA_URL/api/services/switch/turn_off"   # or turn_on
```

Cut power only when `printer_status` is `READY` and the nozzle is under 50 C: the hotend fan must
run after a print, or heat creeps up the filament path. After `turn_on`, poll `printer_status` until
it answers (about 50 s). The plug used to run the office fan, and a wall button (`Switch bureau ②`)
still toggles it through an HA automation: pressing it mid-print cuts the print.

## Talking to the printer

`scripts/printer.py` speaks the legacy protocol on TCP 8899, the same one Orca's Flashforge host
uses: `~M601 S1` login, `~M28 <size> 0:/user/<name>` then raw bytes in 4096-byte chunks, `~M29`
save, `~M23 0:/user/<name>` start, `~M119` state, `~M105` temps, `~M27` progress, `~M661` file list.
No access code needed. Pause/resume/cancel are `~M25`/`~M24`/`~M26`.

- **After a job ends the printer sits in `BUILDING_COMPLETED`** until someone confirms on the
  touchscreen; `~M23` and `~M24` are acknowledged and ignored meanwhile, so `printer.py start`
  refuses unless READY.
- **Files cannot be deleted over the LAN:** `~M30` answers `ok` with any path form (`0:/user/`,
  `/data/`, bare name) and deletes nothing. The user deletes on the touchscreen; list what to delete
  with `printer_files`. The six files ending in `_PLA` are Flashforge's own: keep them.

The HTTP API on 8898 (serial + lowercase check code from `printer.env`) does two things 8899
cannot: `/detail` (status, layer, progress) and `/control` with `stateCtrl_cmd`/`setClearPlatform`,
the only remote way out of `BUILDING_COMPLETED`. `printer.py clear-platform` wraps it.

**`/detail`'s layer counter does not follow the G-code.** The v14 plate ended `BUILDING_COMPLETED`
at `printLayer` 217 of 298 with the whole file executed (`printProgress` 1.0); layer 217 of that
G-code is at 11.98 mm, not the 17.32 mm top. `printProgress` is the position in the file: to know the
height being printed, find the last `;Z:` line before that fraction of the file's bytes.
