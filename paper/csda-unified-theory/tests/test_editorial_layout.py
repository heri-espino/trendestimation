"""Source-only regression checks for CSDA layout and disclosure integrity."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verify_layout import check  # noqa: E402


class JournalLayoutChecks(unittest.TestCase):
    def test_code_theme_fits_column(self) -> None:
        tex = (ROOT / "main.tex").read_text()
        listing = (ROOT / "sections" / "software.tex").read_text()
        for piece in (
            r"\usepackage{xcolor,listings}",
            r"\usepackage[expansion=false]{microtype}",
            r"\lstdefinestyle{vscodeLightPython}",
            r"linewidth=\linewidth",
            r"breaklines=true",
            r"\setlength{\emergencystretch}{2.5em}",
        ):
            self.assertIn(piece, tex)
        self.assertIn(r"\begin{lstlisting}[style=vscodeLightPython]", listing)
        self.assertNotIn(r"\begin{verbatim}", listing)
        self.assertIn("frame=none", tex)
        self.assertNotIn("frame=single", tex)

    def test_authors_and_correspondence(self) -> None:
        tex = (ROOT / "main.tex").read_text()
        for token in (
            r"\author[1]{Heriberto Espino-Montelongo}[orcid=0009-0009-1230-2931]",
            r"\cormark[1]",
            r"\ead{heriberto.espinomo@udlap.mx}",
            r"\author[2]{Daniela Cort\'es-Toto}[orcid=0000-0003-0893-6455]",
            r"\ead{daniela.cortes@udlap.mx}",
            r"\cortext[cor1]{Corresponding author}",
            r"Departamento de Actuar\'ia, F\'isica y Matem\'aticas",
            "postcode={72810}",
        ):
            self.assertIn(token, tex)

    def test_every_display_is_numbered_and_no_boxes(self) -> None:
        sections = ROOT / "sections"
        parts = [ROOT / "main.tex", *sorted(sections.glob("*.tex"))]
        all_source = "\n".join(p.read_text(encoding="utf-8") for p in parts)
        for forbidden in (
            r"\[", r"\]", "$$",
            r"\begin{equation*}", r"\begin{align*}",
            r"\begin{gather*}", r"\begin{displaymath}",
            r"\boxed{", r"\fbox{", r"\framebox{",
        ):
            self.assertNotIn(forbidden, all_source)
        self.assertEqual(
            all_source.count(r"\begin{equation}"),
            all_source.count(r"\end{equation}"),
        )
        self.assertGreaterEqual(all_source.count(r"\begin{equation}"), 40)
        labels = re.findall(r"\\label\{(eq:[^}]+)\}", all_source)
        self.assertEqual(len(labels), len(set(labels)))
        for target in (
            "eq:third-order-matrices",
            "eq:difference-derivative-approximation",
            "eq:reml-profile-step",
            "eq:affine-workload-times",
        ):
            self.assertIn(target, labels)

    def test_official_cas_font_pipeline(self) -> None:
        cas = ROOT.parent / "els-cas-templates" / "cas-dc.cls"
        workflow = ROOT.parent.parent / ".github" / "workflows" / "csda-unified-theory.yml"
        self.assertIn(r"\RequirePackage{charis}", cas.read_text())
        self.assertIn(r"\usepackage{charissil}", (ROOT / "main.tex").read_text())
        self.assertIn(r"\RequirePackage[notext]{stix}", cas.read_text())
        run = workflow.read_text()
        self.assertIn("texlive-fonts-extra", run)
        self.assertIn("kpsewhich charissil.sty", run)
        self.assertIn("kpsewhich stix.sty", run)

    def test_submissions_are_explicit_but_not_fabricated(self) -> None:
        tex = (ROOT / "main.tex").read_text()
        disclosures = (ROOT / "sections" / "declarations.tex").read_text()
        self.assertIn(r"\input{sections/declarations}", tex)
        for phrase in (
            "Data and code availability",
            "Funding",
            "CRediT authorship contribution statement",
            "Declaration of competing interests",
            "Ethics statement",
            "Declaration of generative AI and AI-assisted technologies",
        ):
            self.assertIn(phrase, disclosures)
        self.assertIn("OpenAI ChatGPT", disclosures)
        self.assertIn("pending confirmation", disclosures)
        self.assertNotIn("The authors declare that they have no known", disclosures)

    def test_margin_log_parser(self) -> None:
        sample = r"Overfull \hbox (7.38368pt too wide) in paragraph at lines 9--28"
        self.assertEqual(len(check(sample)), 1)
        self.assertEqual(check(r"Overfull \hbox (123.6pt too wide) detected at line 115"), [])
        self.assertEqual(check(r"Overfull \hbox (0.2pt too wide) in paragraph at lines 2--3"), [])


if __name__ == "__main__":
    unittest.main()
