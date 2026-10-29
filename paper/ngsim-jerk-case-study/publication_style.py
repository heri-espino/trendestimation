"""TeX-native AwesomeFigures export for the computational CAS two-column paper.

PDFs are rendered with the pdfLaTeX PGF backend, using the fonts
measured from the exact manuscript. Native PGF sources are also saved
for editable LaTeX reuse; SVGs are preview-only.

This module never simulates or alters the Experiment004 numerical data.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

try:
    import awesomefigures as af
except ImportError as exc:
    raise RuntimeError(
        "CSDA publication requires pinned AwesomeFigures. "
        "Install paper/requirements.txt."
    ) from exc

_LAYOUT = None
_PAPER = None
_COLUMN_INCHES = None
_MANIFEST = []
WIDE = frozenset({"heldout_forecast", "jerk_comparison", "criterion_heatmap", "forecast_horizons", "backend_comparison"})


def configure_publication(paper: Path):
    global _LAYOUT, _PAPER, _COLUMN_INCHES
    if shutil.which("pdflatex") is None:
        raise RuntimeError("Full TeX-backed figure rendering requires pdflatex.")
    _PAPER = Path(paper)
    af.set_style(
        "elegante", palette="okabe-ito", font="DejaVu Sans",
        use_tex=False, rasterize=True,
    )
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })
    _MANIFEST.clear()
    _LAYOUT = af.inspect_latex(
        _PAPER / "main.tex", engine="pdflatex", timeout=150
    )
    if _LAYOUT.textwidth_pt < 350:
        raise RuntimeError("CAS LaTeX body textwidth measurement failed.")
    # The CAS front-matter is a full-width title before \maketitle
    # switches the BODY into two columns. af.inspect_latex(main.tex) may
    # therefore report columnwidth=textwidth (title-page width).
    # Read the actual columnsep directly from the supplied CAS class,
    # then use the LaTeX two-column identity rather than guessing.
    cls = (_PAPER.parent / "els-cas-templates" / "cas-dc.cls").read_text()
    match = re.search(r"\bcolumnsep\s*=\s*([0-9.]+)\s*pt\b", cls)
    if match is None:
        raise RuntimeError("Cannot locate columnsep in supplied CAS class")
    gap_pt = float(match.group(1))
    body_column_pt = (_LAYOUT.textwidth_pt - gap_pt) / 2.0
    if not 150 < body_column_pt < 300:
        raise RuntimeError("Measured CAS body column width is implausible.")
    _COLUMN_INCHES = body_column_pt / 72.27
    print(
        "AwesomeFigures from CAS manuscript: "
        "column={:.2f}pt, text={:.2f}pt, font={}".format(
            (_COLUMN_INCHES * 72.27), _LAYOUT.textwidth_pt,
            _LAYOUT.font_name,
        ), flush=True,
    )


def publication_export(fig, name: str, figures_dir: Path):
    if _LAYOUT is None:
        raise RuntimeError("Call configure_publication before exporting.")
    target = Path(figures_dir)
    target.mkdir(parents=True, exist_ok=True)
    mode = "text" if name in WIDE else "column"
    width = (_COLUMN_INCHES if mode == "column"
             else _LAYOUT.width_inches("text"))
    with af.latex_style(
        _LAYOUT, width=width, engine="pdflatex",
        font="auto", minimum_text_pt=7.0, rasterize=True,
    ) as publication:
        publication.fit(fig, reference_fontsize_pt=9.0)
        audit = publication.audit(fig)
        if abs(audit.output_width_pt - audit.expected_width_pt) > .75:
            raise RuntimeError("Mismatch of PDF figure width for " + name)
        # CAS font and math glyphs are rendered by the same pdflatex
        # engine as the document; ordinary Matplotlib PDF is NOT used.
        with mpl.rc_context({
            "pgf.texsystem": "pdflatex",
            "pgf.rcfonts": False,
            "pgf.preamble": r"\usepackage{amsmath,amssymb}",
            "savefig.bbox": None,
            "savefig.pad_inches": 0,
            "text.usetex": False,
        }):
            publication.savefig(
                fig, target / (name + ".pdf"), backend="pgf",
                audit=True,
            )
            fig.savefig(
                target / (name + ".pgf"), backend="pgf",
                bbox_inches=None, pad_inches=0,
            )
        # SVG preserves geometric vectors as a preview. Its glyphs are
        # not used in the submitted PDF (TeX PDF is authoritative).
        publication.savefig(fig, target / (name + ".svg"), audit=False)
        _MANIFEST.append({
            "figure": name,
            "layout": mode,
            "document": "main.tex",
            "document_class": "cas-dc (user supplied CAS 2.4)",
            "engine": "pdflatex",
            "pdf_backend": "PGF (genuine TeX text and mathematics)",
            "pgf_source": True,
            "awesomefigures_api": [
                "set_style", "inspect_latex", "latex_style",
                "PublicationStyle.fit", "PublicationStyle.audit",
                "PublicationStyle.savefig",
            ],
            "body_column_width_pt": _COLUMN_INCHES * 72.27,
            "body_text_width_pt": _LAYOUT.textwidth_pt,
            "columnsep_pt": _LAYOUT.textwidth_pt - 2.0 * _COLUMN_INCHES * 72.27,
            "output_width_pt": audit.output_width_pt,
            "expected_width_pt": audit.expected_width_pt,
            "smallest_text_pt": audit.smallest_text_pt,
            "font_family": _LAYOUT.font_family,
            "font_name": _LAYOUT.font_name,
            "audit_warnings": list(audit.warnings),
        })
    plt.close(fig)
    print("TeX/PGF AwesomeFigures export complete:", name, flush=True)


def finish_manifest(paper: Path, figures_dir: Path):
    target = Path(figures_dir)
    names = (
        "heldout_forecast", "jerk_comparison", "criterion_heatmap",
        "forecast_horizons", "backend_comparison",
    )
    if {row["figure"] for row in _MANIFEST} != set(names):
        raise RuntimeError("An expected figure has not been exported.")
    for row in _MANIFEST:
        name = row["figure"]
        row["outputs_sha256"] = {}
        for ext in ("pdf", "pgf", "svg"):
            file = target / (name + "." + ext)
            if not file.is_file() or file.stat().st_size <= 1000:
                raise RuntimeError("Missing vector asset " + str(file))
            row["outputs_sha256"][ext] = hashlib.sha256(
                file.read_bytes()
            ).hexdigest()
    (Path(paper) / "awesomefigures_latex_manifest.json").write_text(
        json.dumps({
            "manuscript": "Elsevier CAS v2.4 / cas-dc",
            "awesomefigures_version": getattr(af, "__version__", "unknown"),
            "source_data": "official FHWA NGSIM raw US101 positions, selected deterministic subset",
            "figures": _MANIFEST,
        }, indent=2) + "\n", encoding="utf8",
    )
