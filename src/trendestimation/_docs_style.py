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
    Point sizes: body 16, titles 19, axes 17, ticks 14, legends 15,
    figure titles 21. This changes rendering only, never statistical data.
    """
    import matplotlib as mpl

    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 16.0,
        "axes.titlesize": 19.0,
        "axes.labelsize": 17.0,
        "axes.titlepad": 13.0,
        "xtick.labelsize": 14.0,
        "ytick.labelsize": 14.0,
        "legend.fontsize": 15.0,
        "legend.title_fontsize": 15.0,
        "figure.titlesize": 21.0,
        "figure.titleweight": "semibold",
        "svg.fonttype": "path",
        "pdf.fonttype": 42,
        "savefig.bbox": "tight",
    })
