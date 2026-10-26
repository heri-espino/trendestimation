"""Execute documentation notebooks and record repeatable timing/provenance data.

Commands:
  python scripts/run_notebooks.py --list
  python scripts/run_notebooks.py --fast --all --in-place --fail-fast
  python scripts/run_notebooks.py --watts 80 --mxn-per-kwh 2.0
No costs are inferred unless BOTH wattage and tariff are specified.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "docs" / "notebooks"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("build/notebook-runs"))
    parser.add_argument("--all", action="store_true",
                        help="Execute all 14: three docs/examples plus eleven docs/notebooks.")
    parser.add_argument("--in-place", action="store_true",
                        help="Additionally save executed source notebooks for Sphinx.")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--fast", action="store_true",
                        help="Reduce benchmark sizes for documentation smoke builds.")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--only", nargs="*", help="Notebook names or stems")
    parser.add_argument("--watts", type=float, default=None,
                        help="Assumed whole-system active watts, not measured by this script.")
    parser.add_argument("--mxn-per-kwh", type=float, default=None,
                        help="Assumed electricity price in MXN/kWh.")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    paths = sorted(SOURCES.glob("*.ipynb"))
    if args.all:
        paths = sorted((SOURCES.parent / "examples").glob("*.ipynb")) + paths
    if args.only:
        wanted = {Path(s).stem for s in args.only}
        unexpected = wanted - {p.stem for p in paths}
        if unexpected:
            parser.error("Unknown notebooks: " + ", ".join(sorted(unexpected)))
        paths = [p for p in paths if p.stem in wanted]
    if not paths:
        parser.error("No notebooks matched the request.")
    if args.list:
        print("\n".join(str(p.relative_to(ROOT)) for p in paths))
        return 0
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if (args.watts is None) != (args.mxn_per_kwh is None):
        parser.error("Supply --watts and --mxn-per-kwh together.")
    if args.watts is not None and (args.watts <= 0 or args.mxn_per_kwh < 0):
        parser.error("Watts must be positive and tariff nonnegative.")

    output = (ROOT / args.output_dir).resolve()
    if output in (SOURCES.resolve(), (SOURCES.parent / "examples").resolve()) and not args.in_place:
        parser.error("Use --in-place when writing to the notebook source directory.")
    output.mkdir(parents=True, exist_ok=True)
    if args.fast:
        os.environ["TRENDESTIMATION_FAST"] = "1"

    versions = {}
    try:
        import numpy
        import scipy
        import matplotlib
        import nbclient
        versions = {"numpy": numpy.__version__, "scipy": scipy.__version__,
                    "matplotlib": matplotlib.__version__,
                    "nbclient": nbclient.__version__}
    except ImportError:
        pass

    meta = {
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unspecified",
        "cpu_count_logical": os.cpu_count(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "versions": versions,
        "fast_mode": bool(args.fast),
        "power_assumption_watts": args.watts,
        "tariff_assumption_mxn_per_kwh": args.mxn_per_kwh,
        "thread_environment": {
            key: os.getenv(key) for key in (
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"
            )
        },
    }
    rows = []
    for i, path in enumerate(paths, start=1):
        print(f"[{i}/{len(paths)}] Executing {path.name}", flush=True)
        nb = nbformat.read(path, as_version=4)
        tic = perf_counter()
        error = ""
        try:
            NotebookClient(
                nb, timeout=args.timeout, kernel_name="python3",
                allow_errors=False, record_timing=True,
                resources={"metadata": {"path": str(ROOT)}},
            ).execute()
        except Exception as exc:
            error = f"{type(exc).__name__}: {str(exc)[:1500]}"
        elapsed = perf_counter() - tic
        row = {
            "notebook": path.name,
            "status": "failed" if error else "ok",
            "wall_seconds": round(elapsed, 6),
            "error": error,
        }
        if args.watts is not None:
            kwh = args.watts / 1000 * elapsed / 3600
            row["estimated_kwh"] = kwh
            row["estimated_mxn"] = kwh * args.mxn_per_kwh
        rows.append(row)
        nbformat.write(nb, output / path.name)
        if args.in_place and not error:
            nbformat.write(nb, path)
        print(f"  {row['status']} in {elapsed:.3f}s" +
              (f": {error[:130]}" if error else ""), flush=True)
        if error and args.fail_fast:
            break

    meta["total_wall_seconds"] = round(sum(r["wall_seconds"] for r in rows), 6)
    meta["completed"] = len(rows)
    meta["failed"] = sum(r["status"] == "failed" for r in rows)
    (output / "manifest.json").write_text(
        json.dumps({"environment": meta, "notebooks": rows}, indent=2),
        encoding="utf-8",
    )
    with (output / "timings.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["notebook", "status", "wall_seconds", "error"]
        if args.watts is not None:
            fields.extend(["estimated_kwh", "estimated_mxn"])
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Completed {len(rows)} notebooks; failures={meta['failed']}")
    print(f"Reproducibility records at: {output}")
    return 1 if meta["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
