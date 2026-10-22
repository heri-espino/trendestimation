"""Export publication-ready vector PDF figures using the AwesomeFigures Git library.

The manuscript stores numerical experiment data in *.dat and CSV files. This
script only renders those data: it never changes fitted trends or experiment
results. Its PDF graphics replace pgfplots/TikZ, which Scipedia does not support.

Run after generating the data:
    python paper/figures/render_awesomefigures.py
    python paper/figures/render_awesomefigures.py --figures-only
    python paper/figures/render_awesomefigures.py --benchmarks-only

Install the pinned Git revision:
    python -m pip install -r paper/requirements.txt
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # reproducible on headless GitHub runners

import matplotlib.pyplot as plt
import numpy as np

try:
    import awesomefigures as af
except ImportError as exc:
    raise SystemExit(
        "AwesomeFigures is required for the SMCCA figures. Install it using "
        "'python -m pip install -r paper/requirements.txt'."
    ) from exc

PAPER = Path(__file__).resolve().parents[1]
FIGURES = PAPER / "figures"
BENCHMARKS = PAPER / "benchmarks" / "results"
# The official SMCCA class has 2.5 cm margins on US letter paper:
# a width of ~6.4 inches avoids oversize artwork and unreadable legends.
WIDTH_IN = 6.3
COLORS = af.color_palette("okabe-ito", as_hex=True)

# All charts are vector PDF; only Matplotlib primitives styled by AwesomeFigures.
# Four-color plots also vary dashes and markers for grayscale legibility.
STYLES = ("-", "--", "-.", ":")
MARKERS = ("o", "s", "^", "D")


def _load(path: Path, columns: tuple[str, ...]):
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing experiment data: {path}. Run 'python paper/build.py --figures' "
            "to generate the required series, or --benchmarks for timing data."
        )
    arr = np.genfromtxt(path, names=True, dtype=float, encoding="utf-8")
    if arr.size == 0:
        return None
    arr = np.atleast_1d(arr)
    names = arr.dtype.names or ()
    if any(field not in names for field in columns):
        raise ValueError(f"Data {path} lacks columns {columns}; found {names}")
    for field in columns:
        if not np.all(np.isfinite(arr[field])):
            raise ValueError(f"Non-finite values in {path}, column {field}")
    return arr


def _axis(ylog=False):
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.2))
    ax.grid(which="major", alpha=0.17, linewidth=0.5)
    ax.grid(which="minor", alpha=0.08, linewidth=0.3)
    ax.set_axisbelow(True)
    if ylog:
        ax.set_yscale("log")
    return fig, ax


def _finish(fig, ax, path, *, ncol=2):
    ax.legend(
        ncol=ncol, loc="upper center",
        bbox_to_anchor=(0.5, -0.20), frameon=False,
        fontsize=8, columnspacing=1.5, handlelength=2.7,
    )
    fig.subplots_adjust(left=.105, right=.97, top=.96, bottom=.30)
    af.save_figure(
        fig, path, close=True,
        metadata={"Title": path.stem, "Creator": "AwesomeFigures / trendestimation SMCCA"},
    )
    print(f"[awesomefigures] {path.relative_to(PAPER)}")


def render_synthetic():
    arr = _load(FIGURES / "cortes_toto_synthetic.dat",
                ("t", "observed", "true", "gcv", "aicc"))
    fig, ax = _axis()
    ax.plot(arr["t"], arr["observed"], color="#8b8b8b", lw=.9,
            label="Observed", alpha=.8)
    ax.plot(arr["t"], arr["true"], color="#252525", ls="--", lw=1.65,
            label="True trend")
    ax.plot(arr["t"], arr["gcv"], color=COLORS[1], lw=1.65,
            label="GCV trend")
    ax.plot(arr["t"], arr["aicc"], color=COLORS[3], ls="-.", lw=1.5,
            label="AICc trend")
    ax.set(xlabel="Observation t", ylabel="Value")
    _finish(fig, ax, FIGURES / "cortes_toto_synthetic.pdf", ncol=4)


def render_co2():
    arr = _load(FIGURES / "mauna_loa_1990_1999.dat",
                ("year", "observed", "d2", "d3", "d4", "d5"))
    fig, ax = _axis()
    ax.plot(arr["year"], arr["observed"], lw=.7, color="#989898",
            label="Monthly observed")
    for idx, order in enumerate((2, 3, 4, 5)):
        ax.plot(arr["year"], arr[f"d{order}"], lw=1.55,
                color=COLORS[[1, 3, 2, 4][idx]],
                ls=STYLES[idx], label=f"d = {order}")
    ax.set(xlabel="Year", ylabel="CO$_2$ (ppm)")
    _finish(fig, ax, FIGURES / "mauna_loa_1990_1999.pdf", ncol=5)


def render_high_order():
    arr = _load(FIGURES / "high_order_numerics.dat", ("d", "condition"))
    if np.any(arr["condition"] <= 0):
        raise ValueError("High-order condition values must be positive for log axis")
    fig, ax = _axis(ylog=True)
    ax.plot(arr["d"], arr["condition"], ls="-", color=COLORS[1],
            lw=1.75, marker="o", markersize=4)
    ax.set_xticks(arr["d"])
    ax.set(xlabel="Difference order d",
           ylabel="Positive-spectrum condition ratio")
    fig.subplots_adjust(left=.13, right=.97, bottom=.20, top=.96)
    target = FIGURES / "high_order_numerics.pdf"
    af.save_figure(fig, target, close=True,
                   metadata={"Title": target.stem})
    print(f"[awesomefigures] {target.relative_to(PAPER)}")


def _render_benchmark(input_name, output_name, *, M, title, ylabel):
    source = BENCHMARKS / input_name
    # SMCCA author instructions require ALL included image files in figures/.
    target = FIGURES / output_name
    if not source.exists():
        # A default figure-only build must not create fictional runtime values.
        return
    arr = _load(source, ("n", "densefresh", "densecached", "spectral", "banded"))
    if arr is None or len(arr) < 2:
        # E.g. smoke preset omits M=64; avoid incorporating a stale old PDF.
        target.unlink(missing_ok=True)
        return
    fig, ax = _axis(ylog=True)
    for i, (field, name) in enumerate((
        ("densefresh", "Fresh dense"),
        ("densecached", "Cached dense"),
        ("spectral", "Spectral SVD" if M == 64 else "Spectral sum"),
        ("banded", "Banded"),
    )):
        if np.any(arr[field] <= 0):
            raise ValueError("Timing values must be strictly positive")
        ax.plot(arr["n"], arr[field], ls=STYLES[i],
                marker=MARKERS[i], markersize=4.1, lw=1.5,
                color=COLORS[[1, 3, 2, 4][i]], label=name)
    ax.set(xlabel=f"Series length n (d = 2, M = {M})", ylabel=ylabel)
    ax.set_title(title, fontsize=9)
    _finish(fig, ax, target, ncol=2)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--figures-only", action="store_true",
                       help="Render only the synthetic, real-data and high-order PDF plots")
    group.add_argument("--benchmarks-only", action="store_true",
                       help="Render timing PDFs from already measured CSV-derived data")
    args = parser.parse_args(argv)

    # Prevent global Matplotlib changes from leaking to other experiments.
    with af.style_context("elegante", font="DejaVu Sans",
                          palette="okabe-ito", use_tex=False):
        if not args.benchmarks_only:
            render_synthetic()
            render_co2()
            render_high_order()
        if not args.figures_only:
            _render_benchmark(
                "full_fit_at_M64.dat", "full_fit_at_M64.pdf",
                M=64, title="End-to-end full-trend fitting",
                ylabel="Median elapsed time (seconds)",
            )
            _render_benchmark(
                "trace_at_M32.dat", "trace_at_M32.pdf",
                M=32, title="Repeated EDF trace evaluation",
                ylabel="Median elapsed time (seconds)",
            )


if __name__ == "__main__":
    main()
