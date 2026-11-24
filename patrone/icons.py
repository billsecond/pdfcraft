#!/usr/bin/env python3
"""Render the PatroneOS edition's app icon into every file the app and its packages use.

The artwork is two vectors in assets/app-icon: pdfcraft.svg (the master) and pdfcraft-tiny.svg (the
same picture with less detail, drawn for 16-32 px). This writes the same files packaging/icons.sh
does, so builds and packages pick the new icon up with no other change:

    hicolor/<n>x<n>/apps/ai.storyteller.pdfcraft.png   16-512 px (tiny artwork up to 32 px)
    hicolor/scalable/apps/ai.storyteller.pdfcraft.svg  a copy of the master
    pdfcraft-small.svg                                 a copy of the master (README pictures)
    pdfcraft-1024.png                                  1024 px on Apple's icon grid
    pdfcraft.ico                                       Windows, 16-256 px
    pdfcraft.icns                                      macOS, 16-1024 px (written here, no iconutil)

The Windows PDF document icon (pdfcraft-document.*) is left as upstream draws it.

Needs resvg (on PATH, or its path in the RESVG environment variable) and Python 3, standard
library only. Afterwards, update the app-icon sha256 values in ATTRIBUTION.toml and run
`cargo xtask assets --write`.

    python patrone/icons.py
"""

import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "assets" / "app-icon"
MASTER = DIR / "pdfcraft.svg"
TINY = DIR / "pdfcraft-tiny.svg"
APP_ID = "ai.storyteller.pdfcraft"

# The tiny artwork stands in for the master up to this many pixels.
TINY_UP_TO = 32


def resvg_path() -> str:
    found = os.environ.get("RESVG") or shutil.which("resvg")
    if not found:
        sys.exit("error: resvg not found (cargo install resvg, or set RESVG to its path)")
    return found


def render(resvg: str, src: Path, size: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([resvg, "-w", str(size), "-h", str(size), str(src), str(out)], check=True, stdin=subprocess.DEVNULL)


def on_apple_grid(src: Path, out: Path) -> Path:
    """`src` as an 824 px body centred on a transparent 1024 px canvas (Apple's icon grid)."""
    text = src.read_text(encoding="utf-8")
    inner = re.sub(r"<svg\b[^>]*>", '<svg x="100" y="100" width="824" height="824" viewBox="0 0 512 512">', text, count=1)
    out.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">\n' + inner + "</svg>\n",
        encoding="utf-8",
    )
    return out


def artwork(size: int, master: Path, tiny: Path) -> Path:
    return tiny if size <= TINY_UP_TO else master


def write_ico(out: Path, pngs: list[Path]) -> None:
    blobs = [p.read_bytes() for p in pngs]
    head = struct.pack("<HHH", 0, 1, len(blobs))
    entries, data, offset = b"", b"", 6 + 16 * len(blobs)
    for blob in blobs:
        w, h = struct.unpack(">II", blob[16:24])  # IHDR
        entries += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(blob), offset)
        data += blob
        offset += len(blob)
    out.write_bytes(head + entries + data)


def write_icns(out: Path, entries: list[tuple[bytes, Path]]) -> None:
    body = b""
    for kind, png in entries:
        blob = png.read_bytes()
        body += kind + struct.pack(">I", 8 + len(blob)) + blob
    out.write_bytes(b"icns" + struct.pack(">I", 8 + len(body)) + body)


def main() -> None:
    resvg = resvg_path()
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        mac_master = on_apple_grid(MASTER, tmp / "mac-master.svg")
        mac_tiny = on_apple_grid(TINY, tmp / "mac-tiny.svg")

        # macOS runtime Dock icon.
        render(resvg, mac_master, 1024, DIR / "pdfcraft-1024.png")

        # Linux hicolor theme (hicolor/256x256 is also the runtime icon on Windows and Linux).
        for size in (16, 24, 32, 48, 64, 128, 256, 512):
            render(resvg, artwork(size, MASTER, TINY), size, DIR / "hicolor" / f"{size}x{size}" / "apps" / f"{APP_ID}.png")
        scalable = DIR / "hicolor" / "scalable" / "apps" / f"{APP_ID}.svg"
        scalable.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MASTER, scalable)
        shutil.copyfile(MASTER, DIR / "pdfcraft-small.svg")

        # Windows .ico.
        ico_pngs = []
        for size in (16, 20, 24, 32, 40, 48, 64, 128, 256):
            png = tmp / f"ico-{size}.png"
            render(resvg, artwork(size, MASTER, TINY), size, png)
            ico_pngs.append(png)
        write_ico(DIR / "pdfcraft.ico", ico_pngs)

        # macOS .icns, PNG entries: (type, pixel size, artwork).
        icns = []
        for kind, size in ((b"icp4", 16), (b"icp5", 32), (b"ic11", 32), (b"icp6", 64), (b"ic12", 64), (b"ic07", 128),
                           (b"ic08", 256), (b"ic13", 256), (b"ic09", 512), (b"ic14", 512), (b"ic10", 1024)):
            # ic11 is 16 pt at 2x: still a 16 pt icon on screen, so it takes the tiny artwork too.
            src = mac_tiny if size <= TINY_UP_TO else mac_master
            png = tmp / f"icns-{kind.decode()}.png"
            render(resvg, src, size, png)
            icns.append((kind, png))
        write_icns(DIR / "pdfcraft.icns", icns)

    print(f"icons written to {DIR}")


if __name__ == "__main__":
    main()
