"""Stage measured Windows full-preset AwesomeFigures in the Marp figure folder.

No benchmark is rerun. Five already-published, vector-only SVGs are copied
from the paper's actual AwesomeFigures outputs so the Marp HTML/PDF deck
is self-contained under figures/ (Marp's --allow-local-files).

The manifest records the original study and SHA256 of each source SVG.
The Windows measurements come from the author's 80,640-cell full run,
not the hosted Linux quick experiment or old unrun slide studies.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "paper" / "figures"
DEST = Path(__file__).resolve().parent / "figures"

WINDOWS_VECTOR_FIGURES = {
    "60_windows_workloads": "windows_full_s_workloads",
    "61_windows_grid_coordinates": "windows_full_s_grid_coordinates",
    "62_windows_reuse_eight": "windows_full_s_reuse_d",
    "63_windows_bounded_search": "windows_full_s_bounded",
    "64_windows_fixed_mu": "windows_full_s_means",
}


def stage_windows_figures(register):
    """Copy every validated original SVG and add an auditable manifest entry."""
    DEST.mkdir(parents=True, exist_ok=True)
    for target, origin in WINDOWS_VECTOR_FIGURES.items():
        src = SOURCES / f"{origin}.svg"
        if not src.is_file():
            raise FileNotFoundError(
                f"Measured Windows figure is missing: {src}. "
                "Regenerate with python paper/benchmarks/report_windows_full_s.py "
                "after the pinned AwesomeFigures dependencies are installed."
            )
        data = src.read_bytes()
        if not data or b"<svg" not in data[:2000]:
            raise ValueError(f"Not a valid published SVG: {src}")
        shutil.copyfile(src, DEST / f"{target}.svg")
        register.append(
            {
                "file": f"figures/{target}.svg",
                "kind": "host measured: Windows full",
                "source": src.relative_to(ROOT).as_posix(),
                "source_sha256": hashlib.sha256(data).hexdigest(),
                "original_measurements":
                    "paper/benchmarks/results/full_s_search_modes/"
                    "search_mode_timings.csv",
                "provenance": "Windows full; 80640 rows, 2 seeds, 7 repeats",
            }
        )
