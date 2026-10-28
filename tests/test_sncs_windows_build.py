"""Static safety checks for the Windows-only SNCS PDF builder."""
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
PAPER=HERE/"paper"/"computational-statistics-submission"


def test_sncs_build_requires_actual_pdf_and_reports_latex_logs():
    source=(PAPER/"build_sncs.ps1").read_text(encoding="utf-8")
    for marker in (
        "sncs_main.tex",
        "sncs_main.pdf",
        "sncs_main.log",
        "Check-PDF",
        "Test-Path -LiteralPath $pdf",
        "(Get-Item -LiteralPath $pdf).Length",
        "Get-Content -LiteralPath $log -Tail 55",
        "finally",
    ):
        assert marker in source


def test_sncs_build_avoids_repeating_numerical_experiments():
    source=(PAPER/"build_sncs.ps1").read_text(encoding="utf-8")
    assert "Invoke-Checked -executable $pdflatex" in source
    assert "Invoke-Checked -executable $bibtex" in source
    assert "if ($UseLatexmk)" in source
    for forbidden in (
        "run_final_vm_study.py",
        "make_selection_dashboards.py",
        "sncs_dashboard.py",
        "subprocess.run",
        "select_lambda(",
    ):
        assert forbidden not in source
