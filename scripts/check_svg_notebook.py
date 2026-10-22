"""Run one short notebook and verify SVG-only inline figure MIME output."""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    notebook = nbformat.read(ROOT / "docs/examples/01_first_trend.ipynb", as_version=4)
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
        raise AssertionError("Executed notebook did not emit SVG MIME output")
    if any("image/png" in d for d in data):
        raise AssertionError("Notebook emitted unwanted PNG MIME output")
    if not any("<svg" in (v if isinstance(v, str) else "".join(v)) for v in svg):
        raise AssertionError("SVG output contains no SVG element")
    print(f"SVG notebook smoke passed: {len(svg)} inline figure(s)")


if __name__ == "__main__":
    main()
