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

    def test_deferred_joint_mle_not_in_submission(self):
        self.assertNotIn(r"\input{sections/likelihood_mu}", self.main)
        self.assertTrue((PAPER / "sections" / "likelihood_mu.tex").is_file())
        for text in (self.main, self.real):
            self.assertNotIn(r"\eqref{eq:mu-profile-mle}", text)
            self.assertNotIn(r"\eqref{eq:likelihood-profile}", text)
        self.assertIn("outside the scope", self.main)

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
