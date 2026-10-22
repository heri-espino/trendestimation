"""Regressions for table/figure float compatibility with official sn-jnl.cls.

The Springer class does not accept legacy float [H] placement; and TeX
cannot reliably process a full tabular read via \input within \resizebox
as used in the earlier SMCCA manuscript. Both triggered fatal errors
after the bibliography transition. Tests do not run numerical benchmarks.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
SECTIONS = (
    PAPER / "sections" / "timing_experiments.tex",
    PAPER / "sections" / "mauna_loa.tex",
    PAPER / "sections" / "high_order_numerics.tex",
)


class SpringerSourceFloatTest(unittest.TestCase):
    def test_sections_never_force_h_placement(self):
        for path in SECTIONS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn(r"\begin{table}[H]", content)
                self.assertNotIn(r"\begin{figure}[H]", content)

    def test_timing_tables_are_unscaled_standalone_inputs(self):
        content = SECTIONS[0].read_text(encoding="utf-8")
        self.assertNotIn(r"\resizebox", content)
        self.assertIn(
            r"\input{benchmarks/results/full_fit_table.tex}", content
        )
        self.assertIn(
            r"\input{benchmarks/results/trace_table.tex}", content
        )
        self.assertIn(r"\begin{table}[tbp]", content)

    @unittest.skipUnless(shutil.which("pdflatex"), "pdflatex is not installed")
    def test_generated_tabular_inside_conditioned_springer_float(self):
        # Test the actual supplied Springer class, not article.cls.
        # Runs one minimal TeX process if the host already has TeX; ordinary
        # PR CI without LaTeX still executes the source-level regressions.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copyfile(PAPER / "sn-jnl.cls", root / "sn-jnl.cls")
            (root / "timings.tex").write_text(
                "\\begin{tabular}{rrrrrrr}\n"
                "\\toprule\n"
                "$n$ & $M$ & Fresh & Cached & Spectral & Banded & $R$ \\\\\n"
                "\\midrule\n"
                "40 & 1 & 0.020 & 0.015 & 0.040 & 0.010 & 0.50 \\\\\n"
                "\\bottomrule\n"
                "\\end{tabular}\n",
                encoding="utf-8",
            )
            source = (
                "\\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}\n"
                "\\usepackage{amsmath,amssymb,graphicx,booktabs,float}\n"
                "\\begin{document}\n"
                "\\title{Example}\n"
                "\\author[1]{\\fnm{First} \\sur{Last}}\n"
                "\\affil[1]{\\orgname{Example}}\n"
                "\\abstract{Short test abstract.}\n"
                "\\keywords{first, second}\n"
                "\\maketitle\n"
                "\\IfFileExists{timings.tex}{%\n"
                "\\begin{table}[tbp]\n"
                "\\centering\n"
                "\\caption{Generated full-fit measurements.}\n"
                "\\label{tab:test}\n"
                "\\input{timings.tex}\n"
                "\\end{table}\n"
                "}{}\n"
                "\\end{document}\n"
            )
            (root / "main.tex").write_text(source, encoding="utf-8")
            result = subprocess.run(
                [
                    "pdflatex", "-no-shell-escape", "-interaction=nonstopmode",
                    "-halt-on-error", "-file-line-error", "main.tex",
                ],
                cwd=root, capture_output=True, text=True,
                check=False, timeout=60,
            )
            self.assertEqual(
                result.returncode, 0,
                msg="LaTeX did not accept generated Springer float:\n"
                + (result.stdout or "")[-2800:],
            )
            self.assertTrue((root / "main.pdf").is_file())


if __name__ == "__main__":
    unittest.main()
