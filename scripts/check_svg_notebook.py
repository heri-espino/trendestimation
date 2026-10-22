"""Execute small tutorial notebooks and validate inline SVG MIME output.

Use --save-intro-outputs only in the ephemeral Sphinx PR preview workspace:
this writes SVG outputs to three introductory notebooks without committing them.
It does NOT execute the full research gallery.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "docs/examples"


def execute_and_check(path: Path, *, save: bool) -> int:
    notebook = nbformat.read(path, as_version=4)
    NotebookClient(
        notebook, timeout=120, kernel_name="python3", allow_errors=False,
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()
    data = [
        output.get("data", {})
        for cell in notebook.cells for output in cell.get("outputs", [])
        if output.get("output_type") in {"display_data", "execute_result"}
    ]
    svg = [d["image/svg+xml"] for d in data if "image/svg+xml" in d]
    if not svg:
        raise AssertionError(f"{path.name} did not emit SVG MIME output")
    if any("image/png" in d for d in data):
        raise AssertionError(f"{path.name} emitted unwanted PNG MIME output")
    if not any("<svg" in (v if isinstance(v, str) else "".join(v)) for v in svg):
        raise AssertionError(f"{path.name} SVG MIME output contains no SVG element")
    if save:
        nbformat.write(notebook, path)
    print(f"SVG smoke passed: {path.name}: {len(svg)} vector figure(s)")
    return len(svg)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--save-intro-outputs", action="store_true",
        help="Execute all three small intros and embed SVG in preview checkout",
    )
    args = parser.parse_args()
    paths = (
        sorted(INTRO.glob("*.ipynb")) if args.save_intro_outputs
        else [INTRO / "01_first_trend.ipynb"]
    )
    if not paths or (args.save_intro_outputs and len(paths) != 3):
        raise RuntimeError("Expected three introductory SVG notebooks")
    total = sum(execute_and_check(path, save=args.save_intro_outputs) for path in paths)
    print(f"Verified {total} SVG notebook figure(s) across {len(paths)} tutorial(s)")


if __name__ == "__main__":
    main()
