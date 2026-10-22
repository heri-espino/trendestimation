"""Consistent, readable typography for Sphinx notebook figures.

This opt-in helper is applied after the AwesomeFigures elegante style,
retaining the Okabe-Ito palette and vector output. Numerical estimators
never change global plotting settings.
"""

from __future__ import annotations


def apply_documentation_figure_style() -> None:
    """Enlarge SVG figure text to match the website's DejaVu Sans font.

    Execute this function after awesomefigures.set_style in notebooks.
    DejaVu Sans ships with Matplotlib, and svg.fonttype='none' preserves
    editable vector text. Sizes: body 16, axis titles 19, axis labels 17,
    tick labels 14, legends 15, and figure titles 21 points.

    Only plotting presentation changes; model outputs stay unchanged.
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
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "savefig.bbox": "tight",
    })
