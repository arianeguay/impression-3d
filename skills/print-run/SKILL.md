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
   **On a by-object plate**, one failed part does not take the others down, so let it finish and
   reprint it alone. Cancel anyway when spaghetti piles up next to the nozzle for more than a few
   minutes (a blob can set around the hotend), as the v15 head did.
   `scripts/where.py <local.gcode>` gives the part being printed, its height and the minutes left.
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
- **Reading a camera frame:** compare each part's visible height to the height `where.py` gives;
  a part clearly shorter than that has failed even with no strands in sight (v15 arm at "7.8 mm"
  was a low mess). A green bit away from every part is debris from a broken part, not ooze. A
  part lying on its side has toppled: parts are printed in their final orientation. The printhead
  hides whatever is between it and the camera; say what could not be seen. A dark frame after a
  power cut means the USB lamp is off (see `reference.md`): ask for it to be switched on.
- A part that broke or toppled because of its shape, or a joint that does not fit: print-design.
- **A long thin strand across the plate at the start** (seen on head v16 and v18) is filament that
  oozed while the nozzle waited to reach temperature, dragged away when printing began. It is not
  the part failing: pull it off by the end away from the nozzle, and do not cancel for it.
- **A new resonance or whoosh at the end of moves** after an interrupted calibration is the
  vibration compensation missing: run it alone from the printer's settings (a few minutes). It
  cleared the noise on 2026-09-29.
- **A calibration that shows 0:00 and stops moving** (status `calibrate_doing`, nozzle held at
  120 C) is stuck: after 15 more minutes, power it off and on (see Power). That aborts the bed
  levelling, so the previous mesh stays in use.

## Long prints: watch from apollon

The laptop cannot stay up for an 8 h print, so `scripts/watch.py` runs on `apollon` (copies of
`printer.py`, `where.py`, `watch.py` in `~/impression-3d/scripts/`, `printer.env` in
`~/.config/impression-3d/`, `claude` in `~/.local/bin`). Copy the uploaded G-code there and start it
detached once the print is running:

```bash
ssh apollon 'export PATH=$HOME/.local/bin:$PATH; nohup python3 ~/impression-3d/scripts/watch.py \
  ~/impression-3d/gcode/<file>.gcode --notify /home/ariane/ops/scripts/pushover-notify.sh \
  > ~/impression-3d/watch.log 2>&1 < /dev/null & disown'
```

It reads supports failing inside a hollow part as "stringing": on the plague mask shell it logged
strings piling up inside the shell from 68 mm and judged "ok" every time but once, while the tree
supports there were going to spaghetti. Check such a part yourself.

Start a new watcher for every print: each one exits when its print ends, so a plate started later
runs unwatched (brick plate B did). Do not `pkill -f watch.py` over ssh: the pattern matches the ssh
command's own shell and kills it before the watcher starts.

A failure verdict is re-checked on a second frame a minute later before cancelling. Dry run on an
empty plate (2026-09-30): the judge answered `unsure`, not `failure`, for a part it could not see.

## Power

The printer's plug is a Home Assistant switch (see `reference.md`):

```bash
op run --env-file ~/.config/impression-3d/printer.env -- sh -c '
curl -s -X POST -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" \
  -d "{\"entity_id\":\"switch.bureau_imprimante_3d_socket_1\"}" "$HA_URL/api/services/switch/turn_off"'   # or turn_on
```

On a host whose `printer.env` holds plain values instead of `op://` references, source it
(`set -a; . ~/.config/impression-3d/printer.env; set +a`) and run the `curl` directly.

Cut power only when `printer_status` is `READY` and the nozzle is under 50 C: the hotend fan must
run after a print, or heat creeps up the filament path. After `turn_on`, poll `printer_status` until
it answers (about 50 s). The plug used to run the office fan; its three fan automations (wall
button ② and two temperature triggers) were deleted on 2026-09-28, so nothing in HA switches it but
the Bureau dashboard tile.

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
