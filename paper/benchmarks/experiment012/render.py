"""Render a source-backed, three-method amortization figure with AwesomeFigures.

Requires a completed 100-seed experiment012 output. Never draws hypothetical
timings, silently drops failed rows or substitutes estimates for measurements.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from statistics import median

METHODS = ("naive_inverse", "banded_cholesky", "spectral_svd")
NAMES = ("Naive explicit inverse", "Banded Cholesky", "Spectral SVD")


def load_complete(input_dir: Path, require_n: int = 100):
    meta = json.loads((input_dir / "metadata.json").read_text(encoding="utf8"))
    if meta["experiment"] != "experiment012" or meta["status"] != "complete_pending_publication_review":
        raise ValueError("No complete Experiment012 run")
    raw = (input_dir / "timings.csv").read_bytes()
    if hashlib.sha256(raw).hexdigest() != meta["timings_sha256"]:
        raise ValueError("Timing CSV SHA-256 mismatch")
    with (input_dir / "timings.csv").open(newline="", encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    observed = {int(row["seed_index"]) for row in rows}
    if meta["seeds"] != require_n or observed != set(range(require_n)):
        raise ValueError(f"Publication requires {require_n} actual independent seeds")
    expected = {(i, cp, method)
                for i in range(require_n) for cp in meta["checkpoints"]
                for method in METHODS}
    actual = {(int(r["seed_index"]), int(r["checkpoint"]), r["method"]) for r in rows}
    if actual != expected or len(rows) != len(expected):
        raise ValueError("Missing/duplicate method-seed-checkpoint records")
    for r in rows:
        if r["status"] == "ok":
            cp = int(r["checkpoint"])
            if int(r["completed"]) != cp or float(r["total_cold_s"]) <= 0:
                raise ValueError("False-success complete-criterion row")
            if abs(float(r["total_cold_s"]) -
                   (float(r["setup_s"]) + float(r["evaluation_s"]))) > 1e-7:
                raise ValueError("Cold time does not equal method setup + evaluation")
    return meta, rows


def summarize(rows, checkpoints):
    """Use matched valid seeds for fair three-way timing medians and ratios."""
    lookup = {(int(r["seed_index"]), int(r["checkpoint"]), r["method"]): r
              for r in rows}
    indices = sorted({int(r["seed_index"]) for r in rows})
    result = []
    for cp in checkpoints:
        matched = [i for i in indices if all(
            lookup[(i, cp, method)]["status"] == "ok" for method in METHODS)]
        for method in METHODS:
            observed = [float(lookup[(i, cp, method)]["total_cold_s"])
                        for i in matched]
            result.append({"checkpoint": cp, "method": method,
                           "paired_seeds": len(matched),
                           "median_cold_s": median(observed) if observed else None})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Figures are immutable per run: use a new --out directory")
    meta, rows = load_complete(args.input)
    summary = summarize(rows, meta["checkpoints"])
    if any(r["paired_seeds"] < 20 for r in summary):
        raise RuntimeError("Fewer than 20 fully matched seeds at one or more checkpoints")
    # Do not call the renderer until real timings have passed source validation.
    import awesomefigures as af
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    af.set_style("elegante", palette="okabe-ito", font="DejaVu Sans", use_tex=False)
    colors = af.color_palette("okabe-ito", as_hex=True)
    palette = {"naive_inverse": colors[2], "banded_cholesky": colors[0],
               "spectral_svd": colors[4]}
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    fig, ax = plt.subplots(figsize=(6.4, 3.55))
    for method, label in zip(METHODS, NAMES):
        data = [r for r in summary if r["method"] == method]
        ax.plot([r["checkpoint"] for r in data],
                [r["median_cold_s"] for r in data],
                marker="o", linewidth=1.7, label=label, color=palette[method])
    ax.set(xscale="log", yscale="log",
           xlabel="Distinct penalty candidates evaluated",
           ylabel="Median complete cold time (seconds)")
    ax.set_xticks(meta["checkpoints"],
                  [str(x) for x in meta["checkpoints"]])
    ax.legend(frameon=False, fontsize=7.6)
    ax.grid(True, alpha=.18)
    fig.tight_layout()
    figdir = out / "figures"
    figdir.mkdir()
    hashes = {}
    for ext in ("pdf", "svg", "png"):
        target = figdir / f"amortization_three_methods.{ext}"
        af.save_figure(fig, target, dpi=210)
        hashes[ext] = hashlib.sha256(target.read_bytes()).hexdigest()
    plt.close(fig)
    (out / "summary.json").write_text(json.dumps({
        "status": "observed_100_seed_three_method_comparison",
        "input_sha256": meta["timings_sha256"],
        "figures_sha256": hashes,
        "rows": summary,
        "method_scope": "Complete CV/GCV scores at distinct direct-lambda candidates",
        "timing_definition": "Cold = method initialization + all evaluations; "
                             "warm accounting omits initialization, not a new run",
        "limitations": [
            "The same candidate grid and synthetic series is used by every method",
            "All method medians are computed on the same valid seed intersections",
            "Naive baseline is an explicit dense inverse, not a dense solve",
            "These are single-host observations, not universal numerical-complexity constants",
            "Selection parity checked in numerical_audit.json; no independent accuracy certificate",
        ],
    }, indent=2) + "\n", encoding="utf8")
    print("Three-method, 100-seed figure built from measured and hash-checked rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
