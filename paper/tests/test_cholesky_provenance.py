"""Guard the attribution of numerical methods in the Springer paper.

These are static provenance checks; they do not time numerical solvers.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"


class CholeskyProvenanceTests(unittest.TestCase):
    def test_weinert_2012_book_and_2007_article_are_distinct(self):
        bib = (PAPER / "bibliografia.bib").read_text(encoding="utf-8")
        self.assertIn("@book{weinert2012fast,", bib)
        self.assertIn("Fast Compact Algorithms and Software for Spline Smoothing", bib)
        self.assertIn("10.1007/978-1-4614-5496-0", bib)
        self.assertIn("@article{weinert2007wh,", bib)

    def test_manuscript_attributes_cholesky_prior_art_correctly(self):
        main = (PAPER / "main.tex").read_text(encoding="utf-8")
        timing = (PAPER / "sections" / "timing_experiments.tex").read_text(
            encoding="utf-8"
        )
        self.assertIn(r"\cite{weinert2012fast}", main)
        self.assertIn("simulation implementation in R", main)
        self.assertIn("does not establish", main)
        self.assertIn(r"\texttt{scipy.linalg.solve\_banded}", timing)
        self.assertIn(r"\texttt{scipy.linalg.cholesky\_banded}", timing)
        self.assertIn("not} measured Cholesky timings", timing)
        self.assertIn("no measured Cholesky-specific speed", timing)

    def test_backend_and_benchmark_are_not_conflated(self):
        paper_baseline = (PAPER / "benchmarks" / "run_benchmarks.py").read_text(
            encoding="utf-8"
        )
        backend = (ROOT / "src" / "trendestimation" / "solvers.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from scipy.linalg import solve_banded", paper_baseline)
        self.assertIn("return solve_banded(", paper_baseline)
        self.assertNotIn("cholesky_banded", paper_baseline)
        self.assertIn("cholesky_banded", backend)
        self.assertIn("cho_solve_banded", backend)


if __name__ == "__main__":
    unittest.main()
