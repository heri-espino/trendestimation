"""Check or explicitly refresh the canonical Paper C publication SHA-256 inventory.

Run from any directory:
    python paper/ngsim-jerk-case-study/check_publication_hashes.py --check
    python paper/ngsim-jerk-case-study/check_publication_hashes.py --write

This inventory tracks the committed manuscript PDFs, editable LaTeX sources,
publication-related figure provenance manifests. Frozen
experiment data and the old pilot-era publication inventory are not modified.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT / "publication_sha256.txt"

REQUIRED = (
    "main.pdf",
    "atlas_supplement.pdf",
    "main.tex",
    "atlas_supplement.tex",
    "references.bib",
    "render_paper.py",
    "awesomefigures_latex_manifest.json",
    "sections/introduction.tex",
    "sections/methods.tex",
    "sections/synthetic_case.tex",
    "sections/precision_calibration.tex",
    "sections/real_case.tex",
    "sections/discussion.tex",
    "generated/awesomefigures_atlas_manifest.json",
    "generated/exp008_methods_figure_manifest.json",
    "generated/visual_suite_manifest.json",
)


def publication_files() -> list[Path]:
    """Enumerate the canonical PDFs, source and figure manifests."""
    files = [ROOT / relative for relative in REQUIRED]
    missing = [relative for relative, path in zip(REQUIRED, files) if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing publication assets: " + ", ".join(missing))
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def generate_inventory() -> str:
    """Create sha256sum-compatible lines; never touch scientific data."""
    lines = []
    for path in publication_files():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Verify the committed inventory (default)")
    mode.add_argument("--write", action="store_true", help="Explicitly refresh the inventory after a reviewed build")
    args = parser.parse_args()
    expected = generate_inventory()

    if args.write:
        INVENTORY.write_text(expected, encoding="utf-8", newline="\n")
        print(f"Updated {INVENTORY} ({len(expected.splitlines())} files)")
        return 0

    if not INVENTORY.is_file():
        print(f"Missing inventory: {INVENTORY}")
        return 1
    actual = INVENTORY.read_text(encoding="utf-8")
    if actual != expected:
        print("Paper C publication checksum mismatch; do not silently rewrite the manifest.")
        print("".join(difflib.unified_diff(
            actual.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile="committed publication_sha256.txt",
            tofile="current working tree",
        )))
        return 1
    print(f"Verified Paper C publication inventory: {len(expected.splitlines())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
