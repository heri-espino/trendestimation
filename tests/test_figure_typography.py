"""Figure typography and notebook presentation regressions."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import nbformat

from trendestimation._docs_style import apply_documentation_figure_style

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_figure_font_scale_and_portable_svg():
    """The documentation style must override tiny AwesomeFigures defaults."""
    with mpl.rc_context():
        apply_documentation_figure_style()
        settings = {
            "font.family": ["DejaVu Sans"],
            "font.size": 16.0,
            "axes.titlesize": 19.0,
            "axes.labelsize": 17.0,
            "xtick.labelsize": 14.0,
            "ytick.labelsize": 14.0,
            "legend.fontsize": 15.0,
            "figure.titlesize": 21.0,
            "svg.fonttype": "path",
        }
        for name, expected in settings.items():
            assert mpl.rcParams[name] == expected, name

        fig, ax = plt.subplots()
        ax.plot([0, 1, 2], [0, 1, 0], label="A fitted trend")
        ax.set(xlabel="Time", title="Example")
        ax.legend()
        output = StringIO()
        fig.savefig(output, format="svg")
        svg = output.getvalue()
        plt.close(fig)
        assert "<path" in svg
        assert "<text" not in svg
        assert "DejaVuSans" in svg  # Path glyph IDs carry the font family.


def test_all_notebooks_activate_large_figure_style_after_awesomefigures():
    paths = sorted(DOCS.glob("**/*.ipynb"))
    assert len(paths) == 13
    for path in paths:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        code = next(cell.source for cell in nb.cells if cell.cell_type == "code")
        assert "font=\"DejaVu Sans\"" in code, path
        assert "apply_documentation_figure_style()" in code, path
        assert "set_matplotlib_formats(\"svg\")" in code, path
        assert code.index('af.set_style("elegante"') < code.index(
            "apply_documentation_figure_style()"
        ), path


def test_notebook_code_has_no_gray_frame_and_main_article_receives_transition():
    css = (DOCS / "_static/css/custom.css").read_text(encoding="utf-8")
    assert '--te-font: "DejaVu Sans"' in css
    assert "#furo-main-content" in css
    assert "animation: te-document-enter 1.15s" in css
    assert ".sidebar-tree {\n    animation: none !important;" in css
    assert "prefers-reduced-motion: reduce" in css
    assert ".cell_input .highlight pre" in css
    assert "div.cell_input div.highlight" in css
    assert "border: none !important;" in css
