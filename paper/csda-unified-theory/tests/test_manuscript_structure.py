"""Source-only regression contract for the seven-section CSDA argument.

Checks presentation and dependencies, not statistical claims or speed.
The underlying numerical identities are checked by verify_theory.py
and the established numerical unit tests.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.tex"
SECTIONS = ROOT / "sections"

CORE_ORDER = [
    "introduction",
    "reading_guide",
    "model",
    "smoothness",
    "criteria",
    "algorithms",
    "complexity",
    "stability",
    "policy",
    "software",
    "conclusion",
]
APPENDIX_ORDER = ["appendix_likelihood_proofs", "algorithm_provenance"]


def _source(name: str) -> str:
    return (SECTIONS / f"{name}.tex").read_text(encoding="utf-8")


class ManuscriptArchitectureTests(unittest.TestCase):
    def test_integrated_core_order_and_appendix_order(self) -> None:
        main = MAIN.read_text(encoding="utf-8")
        self.assertEqual(
            re.findall(r"\\input\{sections/([A-Za-z_]+)\}", main),
            CORE_ORDER + APPENDIX_ORDER + ["declarations"],
        )
        before, after = main.split(r"\appendix", 1)
        self.assertEqual(
            [x for x in re.findall(r"\\input\{sections/([A-Za-z_]+)\}", before)],
            CORE_ORDER,
        )
        self.assertEqual(
            [x for x in re.findall(r"\\input\{sections/([A-Za-z_]+)\}", after)],
            APPENDIX_ORDER + ["declarations"],
        )
        for name in CORE_ORDER + APPENDIX_ORDER + ["declarations"]:
            self.assertTrue((SECTIONS / f"{name}.tex").is_file())

    def test_seven_main_sections_and_three_integrated_contributions(self) -> None:
        main = MAIN.read_text(encoding="utf-8")
        before = main.split(r"\appendix", 1)[0]
        count = len(re.findall(r"\\section\{", before))
        count += sum(len(re.findall(r"\\section\{", _source(name)))
                     for name in CORE_ORDER)
        self.assertEqual(count, 7)
        intro = _source("introduction")
        self.assertEqual(
            len(re.findall(r"\\item \\textbf\{\d\.", intro)), 0,
            "Use dynamic enumerate markers, not hard-coded list numbers",
        )
        self.assertEqual(intro.count(r"\item \textbf{"), 3)
        self.assertEqual(intro.count(r"\subsection{Contributions"), 1)

    def test_no_history_or_example_interrupts_theory(self) -> None:
        self.assertNotIn(r"\input{sections/third_difference_example}", _source("model"))
        self.assertNotIn(r"\input{sections/algorithm_provenance}", _source("algorithms"))
        self.assertIn(r"\input{sections/third_difference_example}", _source("software"))
        self.assertIn(r"\label{app:provenance}", _source("algorithm_provenance"))
        self.assertIn(r"\label{sec:gaussian-likelihood}", _source("gaussian_likelihood"))

    def test_gaussian_proofs_retained_in_appendix(self) -> None:
        source = _source("gaussian_likelihood")
        proofs = _source("appendix_likelihood_proofs")
        self.assertIn(r"\label{thm:reml}", source)
        self.assertIn(r"\label{prop:det}", source)
        self.assertIn(r"\label{app:likelihood-proofs}", proofs)
        self.assertIn(r"\begin{proof}[Proof of Theorem", proofs)
        self.assertIn(r"\begin{proof}[Proof of Proposition", proofs)
        self.assertEqual(proofs.count(r"\begin{proof}["), 2)
        self.assertEqual(proofs.count(r"\end{proof}"), 2)
        self.assertIn(r"\label{eq:logdet-spectral-proof}", proofs)
        self.assertIn(r"\label{eq:reml-profile-step}", proofs)

    def test_all_equations_preserved_and_distinct(self) -> None:
        sources = [MAIN.read_text(encoding="utf-8")]
        sources += [x.read_text(encoding="utf-8") for x in sorted(SECTIONS.glob("*.tex"))]
        s = "\n".join(sources)
        self.assertEqual(s.count(r"\begin{equation}"), 66)
        self.assertEqual(s.count(r"\end{equation}"), 66)
        labels = re.findall(r"\\label\{(eq:[^}]+)\}", s)
        self.assertEqual(len(labels), 66)
        self.assertEqual(len(labels), len(set(labels)))

    def test_submission_integrity(self) -> None:
        main = MAIN.read_text(encoding="utf-8")
        self.assertIn("orcid=0009-0009-1230-2931", main)
        self.assertIn("orcid=0000-0003-0893-6455", main)
        self.assertIn(r"\input{sections/declarations}", main)
        self.assertLess(main.index(r"\input{sections/declarations}"),
                        main.index(r"\bibliographystyle"))
        self.assertIn("OpenAI ChatGPT", _source("declarations"))


if __name__ == "__main__":
    unittest.main()
