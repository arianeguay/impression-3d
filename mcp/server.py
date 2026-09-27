"""MCP server for the Adventurer 5M: see the printer, send jobs, slice with Orca."""
import os
import sys
import tempfile

from mcp.server.mcpserver import Image, MCPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "skill", "scripts"))
import printer  # noqa: E402
import slice as slicer  # noqa: E402

server = MCPServer(
    "impression-3d",
    instructions=(
        "Flashforge Adventurer 5M on the LAN, sliced with OrcaSlicer. Read the 3d-print skill for the "
        "workflow and the lessons behind every default. Never start a print without first looking at "
        "printer_camera or having the user confirm the bed is empty."
    ),
)


@server.tool()
def printer_status() -> str:
    """Machine state, temperatures, layer progress and the file being printed."""
    return printer.status()


@server.tool()
def printer_files() -> list[str]:
    """Files stored on the printer. They cannot be deleted remotely, only on the touchscreen."""
    return printer.files()


@server.tool()
def printer_camera() -> Image:
    """One frame from the printer's camera: check the bed is empty before starting a job."""
    path = os.path.join(tempfile.gettempdir(), "ad5m-snapshot.jpg")
    return Image(path=printer.snapshot(path))


@server.tool()
def printer_upload(gcode_path: str, name: str) -> str:
    """Store a G-code file on the printer under `name` (short, ASCII, ends in .gcode). Does not print."""
    return printer.upload(gcode_path, name)


@server.tool()
def printer_clear_platform() -> str:
    """Acknowledge a finished job (BUILDING_COMPLETED -> READY). Only after the bed is seen empty."""
    return printer.clear_platform()


@server.tool()
def printer_start(name: str) -> str:
    """Start a stored file. Refuses unless the printer is READY. Only after the bed is seen empty."""
    return printer.start(name)


@server.tool()
def printer_job(action: str) -> str:
    """Pause, resume or cancel the current job. action: pause | resume | cancel."""
    return printer.job(action)


@server.tool()
def slice_models(
    out_dir: str,
    models: list[str],
    filament: str = slicer.orca_presets.DEFAULT_FILAMENT,
    profile: str | None = "figurine",
    overrides: list[str] | None = None,
    supported: list[str] | None = None,
) -> dict:
    """Slice STL files with Orca and return the G-code path, time, grams and support moves per object.

    out_dir and models must be under $HOME (the Flatpak cannot read /tmp). profile names a file in the
    repo's profiles/ folder. overrides are kind.key=value (e.g. process.layer_height=0.12). supported
    lists model stems that get supports and a 3-layer raft; every other model prints without.
    """
    return slicer.slice_models(out_dir, models, filament, overrides or [], supported or [], profile)


if __name__ == "__main__":
    server.run()
