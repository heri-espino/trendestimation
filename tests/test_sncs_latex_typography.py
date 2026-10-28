"""Paper font/size regression using the real AwesomeFigures publication API.

Only saved-data plotting is touched. Requires MiKTeX/TeX Live and optional
paper dependencies in the dedicated publication workflow; core CI can skip.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

HERE = Path(__file__).resolve().parents[1] / "paper" / "computational-statistics-submission"
sys.path.insert(0, str(HERE))


def test_pgf_pdf_width_and_font_match_the_springer_tex(monkeypatch, tmp_path):
    pytest.importorskip("awesomefigures")
    pypdf = pytest.importorskip("pypdf")
    if shutil.which("pdflatex") is None:
        pytest.skip("Publication TeX not installed; the separate journal workflow requires it.")

    from contrast_theme import apply, latex_layout, save_figure
    apply(strict=True)
    layout = latex_layout()
    assert layout.textwidth_pt > 200
    assert layout.fontsize_pt >= 9
    assert layout.font_family not in ("", "unknown")

    monkeypatch.setenv("TRENDESTIMATION_TEX_FIGURES", "1")
    for name, fraction in (("sncs_observed_trends", 1.0),
                           ("windows_full_s_workloads", 0.48)):
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot([0.0, 1.0], [1.0, 0.0], lw=1.3, label="sample")
        ax.set_title("Indexed smoothness: μ → λ")
        ax.set(xlabel="Time", ylabel="Value")
        ax.legend()
        target = tmp_path / (name + ".pdf")
        save_figure(fig, target, strict=True)
        plt.close(fig)

        assert target.is_file() and target.stat().st_size > 1000
        report = json.loads(target.with_suffix(".typography.json").read_text())
        assert report["font_backend"] == "pdfLaTeX PGF-generated vector PDF"
        assert report["font_family"] == layout.font_family
        assert report["body_font_pt"] == layout.fontsize_pt
        assert report["inclusion_fraction"] == fraction
        assert report["minimum_text_pt"] >= 6.8
        # AF uses TeX pt (72.27/in). PDF pages use PostScript pt (72/in).
        expected_pdf_pt = layout.columnwidth_pt * fraction * 72.0 / 72.27
        actual_pdf_pt = float(pypdf.PdfReader(str(target)).pages[0].mediabox.width)
        assert actual_pdf_pt == pytest.approx(expected_pdf_pt, abs=1.0)
        assert report["export_width_pt"] == pytest.approx(
            layout.columnwidth_pt * fraction, abs=0.6
        )


def test_master_renderer_checks_each_cited_figures_tex_font():
    source = (HERE/"rerender_awesomefigures.py").read_text(encoding="utf-8")
    assert 'TRENDESTIMATION_TEX_FIGURES' in source
    assert '"publication_typography"' in source
    assert "manuscript cites PDFs not exported" not in source.lower() or (
        "not exported with measured TeX fonts" in source
    )
    theme = (HERE/"contrast_theme.py").read_text(encoding="utf-8")
    assert "af.inspect_latex(" in theme
    assert "af.latex_style(" in theme
    assert 'backend="pgf"' in theme
    assert "pub.fit(fig," in theme
    assert "pub.audit(fig)" in theme
    assert "savefig.bbox" in theme
    assert "sncs_main.tex" in theme
