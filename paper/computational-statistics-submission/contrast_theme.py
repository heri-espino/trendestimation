"""AwesomeFigures publication theme for every trendestimation paper plot.

This module is the single plotting configuration used by archived-data
renderers. The publication pipeline requires the pinned AwesomeFigures
revision in paper/requirements.txt; the core Python package and its tests may
still run without that optional, paper-only dependency.

Styles and schemes are furnished by the AwesomeFigures public APIs rather
than copying its color values or implementing another Matplotlib theme.
None of these functions fits a model or runs an experiment.
"""
from __future__ import annotations

from pathlib import Path
import matplotlib as mpl

try:
    import awesomefigures as af
except ImportError:
    af = None

PALETTE = "okabe-ito"
STYLE = "elegante"
FONT = "DejaVu Sans"
STANDARD_OKABE_ITO = (
    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
    "#0072B2", "#D55E00", "#CC79A7", "#000000",
)
CONTRAST = tuple(af.color_palette(PALETTE, as_hex=True)) if af else STANDARD_OKABE_ITO
if len(CONTRAST) != 8:
    raise RuntimeError("Expected pinned AwesomeFigures eight-color Okabe-Ito palette")

# Preserve method color assignments across the archival and SNCS manuscripts.
ORDER = (0, 1, 2, 4, 5, 6, 7, 3)
SERIES = tuple(CONTRAST[i] for i in ORDER)
MARKERS = ("o", "s", "^", "D", "v", "P", "X", "*")
LINESTYLES = ("-", "--", "-.", ":", "-", "--", "-.", ":")
SCHEME = (
    tuple(af.plot_scheme(PALETTE, markers=MARKERS, linestyles=LINESTYLES))
    if af else tuple(
        {"color": color, "marker": MARKERS[i], "linestyle": LINESTYLES[i]}
        for i, color in enumerate(CONTRAST)
    )
)
METHODS = {
    "cv": SERIES[0], "gcv": SERIES[1], "aicc": SERIES[2],
    "bic": SERIES[3], "mle": SERIES[4], "controlled": SERIES[5],
}
METHOD_LINESTYLE = {
    "cv": "-", "gcv": "--", "aicc": "-.", "bic": ":",
    "mle": "-", "controlled": "--",
}
ORDER_COLORS = {d: SERIES[d - 1] for d in (1, 2, 3, 4)}
ORDER_MARKERS = {1: "o", 2: "s", 3: "^", 4: "D"}
INK = "#1B2533"
MUTED = "#7C8899"
GRID = "#C9D2DE"
FUTURE = SERIES[1]
TREND = SERIES[4]
OBSERVED = MUTED


def require_awesomefigures() -> None:
    """Fail if a publication build lacks the pinned plotting dependency."""
    if af is None:
        raise RuntimeError(
            "Publication figures require AwesomeFigures. Install the pinned "
            "revision with: python -m pip install -r paper/requirements.txt"
        )


def apply(*, strict: bool = False) -> None:
    """Apply AwesomeFigures elegante style, not a local imitation.

    strict=True is required in publication builds. strict=False preserves
    lightweight core-unit-test imports without paper extras.
    """
    if strict:
        require_awesomefigures()
    if af is not None:
        af.set_style(STYLE, palette=PALETTE, font=FONT, use_tex=False, rasterize=True)
    else:
        # Optional nonpublication preview when paper extras are not installed.
        mpl.rcParams.update({"font.family": "sans-serif", "figure.facecolor": "white"})
    mpl.rcParams.update({
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "legend.frameon": False,
    })


def named_colormap(name: str):
    """Expose AwesomeFigures named scientific colormaps."""
    return af.named_colormap(name) if af is not None else mpl.colormaps[name]


def save_figure(fig, path: str | Path, *, dpi: int = 180, strict: bool = False):
    """Use AwesomeFigures vector/hybrid publication exporter."""
    if strict:
        require_awesomefigures()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if af is not None:
        return af.save_figure(fig, target, dpi=dpi)
    fig.savefig(target, dpi=dpi, bbox_inches="tight", facecolor="white")
    return target


def provenance() -> dict:
    """Report the exact reproducibility contract for a figure manifest."""
    require_awesomefigures()
    return {
        "library": "awesomefigures",
        "library_version": af.__version__,
        "source": "https://github.com/awesomefigures/awesomefigures",
        "source_commit": "54c8bf2374551fa39428f47f69580b4822d4b938",
        "style": STYLE,
        "palette": PALETTE,
        "font": FONT,
        "apis": [
            "awesomefigures.set_style",
            "awesomefigures.plot_scheme",
            "awesomefigures.named_colormap",
            "awesomefigures.save_figure",
        ],
    }
