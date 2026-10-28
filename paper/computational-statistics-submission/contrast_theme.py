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
from functools import lru_cache
import json
import os
import shutil
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



# The Springer .tex file is the source of truth for physical sizes and font.
PAPER_TEX = Path(__file__).resolve().parent / "sncs_main.tex"
WIDTH_FRACTIONS = {
    "windows_full_s_workloads": 0.48,
    "windows_full_s_reuse_d": 0.48,
    "windows_full_s_means": 0.48,
    "windows_full_s_bounded": 0.48,
    "final_solver_inference": 0.86,
    "final_inversion_speed": 0.86,
}
PGF_PREAMBLE = r"\usepackage{amsmath,amssymb}"


@lru_cache(maxsize=1)
def latex_layout():
    """Measure the actual Springer manuscript via AwesomeFigures/TeX."""
    require_awesomefigures()
    if shutil.which("pdflatex") is None:
        raise RuntimeError(
            "Exact Springer Nature fonts require pdflatex on PATH. "
            "Install user-scope MiKTeX/TeX Live before regenerating figures."
        )
    return af.inspect_latex(PAPER_TEX, engine="pdflatex", timeout=90)


def _tex_safe_labels(fig):
    """Render Unicode Greek/arrow labels as TeX math, preserving math regions."""
    from matplotlib.text import Text
    translations = {
        "λ": r"\lambda", "μ": r"\mu", "τ": r"\tau",
        "δ": r"\delta", "α": r"\alpha", "σ": r"\sigma",
        "θ": r"\theta", "ρ": r"\rho", "π": r"\pi",
        "→": r"\rightarrow", "↔": r"\leftrightarrow",
        "≤": r"\leq", "≥": r"\geq", "∞": r"\infty",
        "±": r"\pm", "×": r"\times",
    }
    for item in fig.findobj(match=Text):
        item.set_fontfamily("serif")
        label = item.get_text()
        if not label:
            continue
        parts = label.split("$")
        for i, part in enumerate(parts):
            for symbol, command in translations.items():
                part = part.replace(symbol, command if i % 2 else "$" + command + "$")
            if i % 2 == 0:
                part = part.replace("–", "--").replace("—", "---").replace("−", "-")
            parts[i] = part
        adjusted = "$".join(parts)
        if adjusted != label:
            item.set_text(adjusted)


def _save_with_latex(fig, target: Path, *, dpi: int) -> Path:
    """Exact physical sizes and TeX glyphs for manuscript-ready vector PDFs.

    The PDF uses the TeX PGF backend; PNG/SVG are previews with the same size
    and point hierarchy but their font outlines are not necessarily identical.
    """
    layout = latex_layout()
    fraction = WIDTH_FRACTIONS.get(target.stem, 1.0)
    width_inches = layout.width_inches("column") * fraction
    with af.latex_style(
        layout, width=width_inches, engine="pdflatex",
        font="auto", minimum_text_pt=7.0, rasterize=True,
    ) as pub:
        if not getattr(fig, "_sncs_latex_layout_prepared", False):
            _tex_safe_labels(fig)
            pub.fit(fig, reference_fontsize_pt=10.0)
            fig._sncs_latex_layout_prepared = True
        audit = pub.audit(fig)
        if abs(audit.output_width_pt - audit.expected_width_pt) > 0.5:
            raise RuntimeError(f"Publication width mismatch: {audit.warnings}")
        if audit.smallest_text_pt is not None and audit.smallest_text_pt < 6.8:
            raise RuntimeError(f"Unreadable text at printed size: {audit.warnings}")
        if target.suffix.lower() == ".pdf":
            with mpl.rc_context({
                "pgf.texsystem": "pdflatex", "pgf.rcfonts": False,
                "pgf.preamble": PGF_PREAMBLE,
                "savefig.bbox": None, "savefig.pad_inches": 0,
                "text.usetex": False,
            }):
                pub.savefig(fig, target, dpi=dpi, backend="pgf", audit=True)
            details = {
                "figure": target.name, "manuscript": PAPER_TEX.name,
                "textwidth_pt": layout.textwidth_pt,
                "columnwidth_pt": layout.columnwidth_pt,
                "body_font_pt": layout.fontsize_pt,
                "font_family": layout.font_family, "font_name": layout.font_name,
                "inclusion_fraction": fraction,
                "export_width_pt": audit.output_width_pt,
                "minimum_text_pt": audit.smallest_text_pt,
                "audit_warnings": list(audit.warnings),
                "font_backend": "pdfLaTeX PGF-generated vector PDF",
                "awesomefigures_apis": [
                    "inspect_latex", "latex_style", "PublicationStyle.fit",
                    "PublicationStyle.audit", "PublicationStyle.savefig",
                ],
            }
            target.with_suffix(".typography.json").write_text(
                json.dumps(details, indent=2) + "\n", encoding="utf-8"
            )
        else:
            pub.savefig(fig, target, dpi=dpi, audit=False)
    return target


def save_figure(fig, path: str | Path, *, dpi: int = 180, strict: bool = False):
    """TeX-aware paper export; plain library preview without an installed TeX."""
    if strict:
        require_awesomefigures()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if os.environ.get("TRENDESTIMATION_TEX_FIGURES") == "1":
        require_awesomefigures()
        return _save_with_latex(fig, target, dpi=dpi)
    if af is not None:
        return af.save_figure(fig, target, dpi=dpi)
    fig.savefig(target, dpi=dpi, bbox_inches="tight", facecolor="white")
    return target


def provenance(*, strict: bool = False) -> dict:
    """Report the plotting backend; publication builds require AwesomeFigures."""
    if strict:
        require_awesomefigures()
    if af is None:
        return {"library": "matplotlib-preview-only", "paper_extras_installed": False}
    return {
        "library": "awesomefigures",
        "library_version": af.__version__,
        "source": "https://github.com/awesomefigures/awesomefigures",
        "source_commit": "54c8bf2374551fa39428f47f69580b4822d4b938",
        "style": STYLE,
        "palette": PALETTE,
        "preview_font": FONT,
        "publication_pdf_font": "measured TeX manuscript font, embedded via PGF/PDF",
        "typography": "af.inspect_latex + af.latex_style + PublicationStyle.fit/audit",
        "apis": [
            "awesomefigures.set_style",
            "awesomefigures.plot_scheme",
            "awesomefigures.named_colormap",
            "awesomefigures.save_figure",
        ],
    }
