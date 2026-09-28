# impression-3d

Everything needed to print on the Flashforge Adventurer 5M through Claude: model in, G-code on the
printer, job started.

| Path | What |
|---|---|
| `skills/` | Three Claude skills, each symlinked into `~/.claude/skills/`: `print-design` (model to oriented parts), `print-prepare` (parts to verified G-code, calibration), `print-run` (send, watch, cancel, diagnose) |
| `reference.md` | Setup shared by the three skills: printer, slicers, filaments, where files go |
| `scripts/printer.py` | Printer over the LAN: status, files, upload, start, pause/resume/cancel, clear-platform, camera snapshot |
| `scripts/slice.py` | OrcaSlicer CLI wrapper: presets flattened, per-object supports, summary of time/grams/supports |
| `scripts/orca_presets.py` | Turns Orca user presets into files the CLI accepts |
| `profiles/` | Named override sets for `slice.py --profile` (`figurine`: the settings that printed Oogie; `lego_minifig` extends it via `_extends`) |
| `standards/` | Dimension standards with the values that print and fit here (`lego_minifig.json`) |
| `mcp/server.py` | MCP server exposing the same tools to Claude Code |
| `projects/<name>/` | One folder per print project: final parts and the notes behind every change |

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
for s in skills/*/; do ln -s "$PWD/$s" ~/.claude/skills/; done
claude mcp add --scope user impression-3d -- "$PWD/.venv/bin/python" "$PWD/mcp/server.py"
```

Printer credentials stay out of git, in `~/.config/impression-3d/printer.env`:

```
AD5M_HOST=192.168.0.199
AD5M_SERIAL=<serial from printer.py status / M115>
AD5M_CHECK_CODE=<LAN-mode code from the touchscreen, lowercase>
```

## Not done yet

The MCP server runs over stdio, so it serves Claude Code on this laptop only. Reaching it from
claude.ai (a phone at the store) needs it served over HTTP behind authentication and a tunnel, since
the printer is only on the home LAN.
