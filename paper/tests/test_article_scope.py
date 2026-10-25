"""Fast static checks that the journal manuscript stays within validated scope.

The long-term joint (lambda, mu) marginal MLE project is deliberately
not imported into this computational comparison. No TeX or benchmarks
are required; the author still compiles and visually reviews the PDF.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]


class ArticleScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (PAPER / "main.tex").read_text(encoding="utf-8")
        cls.real = (PAPER / "sections" / "mauna_loa.tex").read_text(
            encoding="utf-8"
        )

    def test_uses_verified_springer_author_year_class(self):
        self.assertIn(
            r"\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}",
            self.main,
        )

    def test_abstract_and_keywords_have_journal_lengths(self):
        abstract = re.search(r"\\abstract\{([^}]*)\}", self.main, re.DOTALL)
        keywords = re.search(r"\\keywords\{([^}]*)\}", self.main, re.DOTALL)
        self.assertIsNotNone(abstract)
        self.assertIsNotNone(keywords)
        words = re.findall(r"\b[\w-]+\b", abstract.group(1))
        self.assertGreaterEqual(len(words), 150)
        self.assertLessEqual(len(words), 250)
        keys = [term.strip() for term in keywords.group(1).split(",")]
        self.assertGreaterEqual(len(keys), 4)
        self.assertLessEqual(len(keys), 6)

    def test_core_equations_remain_visible(self):
        for equation in (
            "objective", "affine", "smoothness",
            "likelihood-profile", "mu-profile-mle", "lambda-profile-mle",
        ):
            with self.subTest(equation=equation):
                self.assertIn(r"\label{eq:" + equation + "}", self.main)
        self.assertIn(r"\arg\min_{\tau\in\R^n}", self.main)
        self.assertIn(r"\|D_d\tau-\mu\mathbf1\|_2^2", self.main)
        self.assertIn(
            r"\arg\min_{\lambda>0}", self.main,
        )

    def test_joint_mle_is_theoretical_outlook_not_empirical_result(self):
        self.assertNotIn(r"\input{sections/likelihood_mu}", self.main)
        self.assertTrue((PAPER / "sections" / "likelihood_mu.tex").is_file())
        self.assertIn("a deferred extension", self.main)
        self.assertIn(r"\emph{not} a tested", self.main)
        self.assertIn("outside the scope", self.main)
        self.assertNotIn(r"\eqref{eq:lambda-profile-mle}", self.real)
        self.assertNotIn(r"\eqref{eq:mu-profile-mle}", self.real)

    def test_smoothness_coordinate_math_and_implementation_scope(self):
        section_path = PAPER / "sections" / "smoothness_coordinate_search.tex"
        self.assertTrue(section_path.is_file())
        content = section_path.read_text(encoding="utf-8")
        self.assertIn(r"\input{sections/smoothness_coordinate_search}", self.main)
        for label in (
            "inverse-s-coordinate", "s-coordinate-derivative",
            "criterion-s-coordinate", "score-s-chain",
            "future-joint-s-profile",
        ):
            with self.subTest(label=label):
                self.assertIn(r"\label{eq:" + label + "}", content)
        self.assertIn(r"\texttt{search\_space=", content)
        self.assertIn("search\\_grid", content)
        self.assertIn("additional scalar inversion", content)
        self.assertIn(r"\emph{unimplemented research extension}", content)
        self.assertIn("The central question of this computational study", self.main)
        self.assertIn("Direct end-to-end timing comparisons", self.main)
        self.assertIn("rather than an automatic speed improvement", self.main)

    def test_smoothness_is_the_primary_manuscript_coordinate(self):
        self.assertIn(
            r"\title[Normalized smoothness for trend estimation]",
            self.main,
        )
        self.assertIn(r"$s=S(\lambda)\in[0,1]$", self.main)
        self.assertIn(
            "mapped-grid equivalence checks and numerical validation",
            self.main,
        )
        self.assertIn("not a new smoothing criterion", self.main)
        self.assertIn(r"\emph{not} a head-to-head timing comparison", self.main)

    def test_existing_numeric_evidence_remains_included(self):
        for dependency in (
            "sections/kernel_derivatives",
            "sections/smoothness_speed",
            "sections/timing_experiments",
            "sections/high_order_numerics",
            "sections/mauna_loa",
        ):
            with self.subTest(dependency=dependency):
                self.assertIn(r"\input{" + dependency + "}", self.main)
        self.assertIn(r"\input{criteria_table.tex}", self.main)
        self.assertIn("fresh", (PAPER / "sections" / "timing_experiments.tex").read_text())

    def test_observed_example_is_fixed_mean_and_descriptive(self):
        self.assertIn(r"$\mu=0$", self.real)
        self.assertIn("does not estimate", self.real)
        self.assertIn("not forecasts", self.real)


if __name__ == "__main__":
    unittest.main()
