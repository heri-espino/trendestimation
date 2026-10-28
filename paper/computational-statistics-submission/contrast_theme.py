"""High-contrast, colorblind-aware AwesomeFigures styling for scientific plots.

The palette is the same pinned AwesomeFigures Okabe–Ito palette used in the
Springer renderer. Styling is independent of data acquisition, fitting,
model selection, or benchmarking. Always regenerate figures from stored
research artifacts; colors must never change reported numeric values.
"""
from __future__ import annotations

from cycler import cycler
import matplotlib as mpl

# AwesomeFigures is an optional *paper-only* extra: core CI tests and
# the main Python package must remain importable without installing it.
# When installed, use the exact pinned AwesomeFigures palette. Otherwise
# use the public standard Okabe-Ito hex values for consistent previews.
STANDARD_OKABE_ITO = (
    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
    "#0072B2", "#D55E00", "#CC79A7", "#000000",
)
try:
    import awesomefigures as af
except ImportError:
    af = None

CONTRAST = tuple(af.color_palette("okabe-ito", as_hex=True)) if af else STANDARD_OKABE_ITO
if len(CONTRAST) < 8:
    raise RuntimeError("AwesomeFigures Okabe–Ito palette unexpectedly short")

# Match the existing awesomefigures Springer palette; use contrasting
# dash/marker patterns as a second cue, including in grayscale exports.
ORDER = (0, 1, 2, 4, 5, 6, 7, 3)
SERIES = tuple(CONTRAST[i] for i in ORDER)
METHODS = {
    "cv": SERIES[0],
    "gcv": SERIES[1],
    "aicc": SERIES[2],
    "bic": SERIES[3],
    "mle": SERIES[4],
    "controlled": SERIES[5],
}
METHOD_LINESTYLE = {
    "cv":"-", "gcv":"--", "aicc":"-.", "bic":":",
    "mle":"-", "controlled":"--",
}
ORDER_COLORS = {d: SERIES[d-1] for d in (1,2,3,4)}
ORDER_MARKERS = {1:"o", 2:"s", 3:"^", 4:"D"}
INK="#1B2533"
MUTED="#7C8899"
GRID="#C9D2DE"
FUTURE=SERIES[1]
TREND=SERIES[4]
OBSERVED=MUTED


def apply() -> None:
    """Set high-contrast publication defaults without modifying any results."""
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.prop_cycle": cycler("color", SERIES),
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Liberation Sans"],
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": GRID,
        "xtick.color": INK,
        "ytick.color": INK,
        "grid.color": GRID,
        "grid.alpha": .35,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "legend.frameon": False,
    })
