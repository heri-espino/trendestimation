"""Editorial contract: SVD example, typography, notation and float mentions.

This test only inspects the canonical CSDA manuscript. No experimental
results, other paper sources or numerical algorithms are changed.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ROOT / "sections"


class CaptionAndNotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = (ROOT / "main.tex").read_text(encoding="utf-8")
        cls.contents = {
            p.name: p.read_text(encoding="utf-8")
            for p in SECTIONS.glob("*.tex")
        }
        cls.all_source = cls.main + "\n" + "\n".join(cls.contents.values())

    def test_mathds_and_H_first(self):
        self.assertIn(r"\usepackage{dsfont}", self.main)
        self.assertIn(r"\newcommand{\R}{\mathds{R}}", self.main)
        self.assertIn(r"\usepackage[scaled=0.95]{helvet}", self.main)
        guide = self.contents["reading_guide.tex"]
        model = self.contents["model.tex"]
        self.assertLess(
            guide.index(r"H_\lambda=(I+\lambda D_d^\top D_d)^{-1}"),
            guide.index(r"A_\lambda=I+\lambda Q_d"),
        )
        self.assertLess(
            model.index(r"H_\lambda=(I+\lambda D_d^\top D_d)^{-1}"),
            model.index(r"A_\lambda=I+\lambda Q_d"),
        )
        self.assertIn(r"\operatorname*{arg\,min}_{\tau\in\R^n}", model)

    def test_nabla_and_spectral_rho_not_delta(self):
        self.assertNotIn(r"\Delta", self.all_source)
        self.assertNotIn(r"\delta", self.all_source)
        self.assertNotIn(r"\mathbb{R}", self.all_source)
        self.assertNotIn(r"\mathbb R", self.all_source)
        self.assertIn(r"\nabla^d x(t+dh)", self.contents["order_interpretation.tex"])
        self.assertIn(r"\nabla^3 x_{t+3}", self.contents["third_difference_example.tex"])
        self.assertIn(r"\rho_j=\sigma_j^2", self.contents["model.tex"])

    def test_each_figure_and_table_is_referenced(self):
        labels = re.findall(
            r"\\label\{((?:fig|tab):[^}]+)\}", self.all_source,
        )
        self.assertEqual(len(labels), 5)
        self.assertEqual(len(set(labels)), 5)
        for label in labels:
            with self.subTest(label=label):
                self.assertRegex(
                    self.all_source, r"\\(?:auto|c|C)?ref\{" + re.escape(label) + r"\}",
                )

    def test_caption_fonts_are_consistently_defined(self):
        example = self.contents["third_difference_example.tex"]
        software = self.contents["software.tex"]
        algorithms = self.contents["algorithms.tex"]
        provenance = self.contents["algorithm_provenance.tex"]
        policy = self.contents["policy.tex"]
        self.assertIn(r"\begin{figure*}", example)
        self.assertIn(r"\caption{Reduced singular-value decomposition", example)
        self.assertIn(r"{\sffamily\footnotesize", software)
        self.assertIn(r"{\sffamily\footnotesize \caption{", algorithms)
        self.assertIn(r"{\sffamily\footnotesize \caption{", provenance)
        self.assertIn(r"\begin{table*}", policy)
        # The CAS figure*/table* environments apply \sffamily\small;
        # Helvetica is the common scalable sans family for all captions.

    def test_numeric_example_equations_and_reproducibility(self):
        example = self.contents["third_difference_example.tex"]
        for label in (
            "eq:third-order-matrices",
            "eq:d3-numerical-svd",
            "eq:d3-numerical-h",
            "eq:third-order-distant-leverage",
            "eq:d3-nonzero-affine-check",
        ):
            self.assertIn(r"\label{" + label + "}", example)
        self.assertIn("tests/test\\_d3\\_numeric\\_svd.py", example)
        self.assertIn("195", example)
        self.assertTrue((ROOT / "tests" / "test_d3_numeric_svd.py").is_file())


if __name__ == "__main__":
    unittest.main()
