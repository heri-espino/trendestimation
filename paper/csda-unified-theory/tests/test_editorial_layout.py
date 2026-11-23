"""Source-only regression checks for CSDA layout and disclosure integrity."""
from __future__ import annotations

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
            r"\usepackage{xcolor,listings,microtype}",
            r"\lstdefinestyle{vscodeLightPython}",
            r"linewidth=\linewidth",
            r"breaklines=true",
            r"\setlength{\emergencystretch}{2.5em}",
        ):
            self.assertIn(piece, tex)
        self.assertIn(r"\begin{lstlisting}[style=vscodeLightPython]", listing)
        self.assertNotIn(r"\begin{verbatim}", listing)

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
