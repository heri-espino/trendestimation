"""Consistent, readable typography for Sphinx notebook figures.

This opt-in helper is applied after the AwesomeFigures elegante style,
retaining the Okabe-Ito palette and vector output. Numerical estimators
never change global plotting settings.
"""

from __future__ import annotations


def apply_documentation_figure_style() -> None:
    """Match notebook figures to the documentation's DejaVu Sans face.

    Call after awesomefigures.set_style so its other theme settings are
    retained. SVG fonttype='path' outlines glyphs from Matplotlib's bundled
    DejaVu Sans: a standalone SVG loaded via <img> cannot inherit the page's
    webfont CSS and otherwise falls back to a different system font.

    SVG text is therefore visually reproducible but no longer selectable.
    Point sizes: body 11, titles 13, axes 11, ticks 10, legends 10,
    figure titles 14. Major grids use both axes; ordinary line markers
    are disabled unless they convey actual individual observations. This changes rendering only, never statistical data.
    """
    import matplotlib as mpl

    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11.0,
        "axes.titlesize": 13.0,
        "axes.labelsize": 11.0,
        "axes.titlepad": 9.0,
        "xtick.labelsize": 10.0,
        "ytick.labelsize": 10.0,
        "legend.fontsize": 10.0,
        "legend.title_fontsize": 10.0,
        "figure.titlesize": 14.0,
        "figure.titleweight": "semibold",
        "lines.marker": "None",
        "lines.markersize": 0.0,
        "axes.grid": True,
        "axes.grid.axis": "both",
        "axes.grid.which": "major",
        "axes.axisbelow": True,
        "grid.color": "#CFDCE7",
        "grid.linewidth": 0.65,
        "grid.alpha": 0.6,
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "savefig.bbox": "tight",
    })
