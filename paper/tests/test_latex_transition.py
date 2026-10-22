"""Regression tests for switching from SMCCA numeric to Springer author-year.

These tests do not require LaTeX to run and preserve ignored numerical data.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("springer_latex_builder", PAPER / "build.py")
builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(builder)


class SpringerTemplateTransitionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.paper = Path(self.tmp.name)
        self.source = self.paper / "main.tex"
        self.source.write_text(
            "% Springer manuscript\n"
            r"\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}" + "\n"
            r"\bibliography{bibliografia}" + "\n",
            encoding="utf-8",
        )

    def test_current_repository_is_springer_author_year(self):
        identity = builder._latex_source_identity(
            (PAPER / "main.tex").read_text(encoding="utf-8")
        )
        self.assertEqual(identity["document_class"], "sn-jnl")
        self.assertEqual(identity["bib_style"], "sn-mathphys-ay")

    def test_cleans_stale_smcca_aux_but_preserves_measured_data_and_pdf(self):
        self.paper.joinpath("main.aux").write_text(
            "\\relax\n\\bibstyle{abbrv}\n\\NAT@force@numbers{}\n",
            encoding="utf-8",
        )
        for suffix in (".bbl", ".blg", ".fdb_latexmk", ".fls", ".log"):
            self.paper.joinpath("main" + suffix).write_text("outdated", encoding="utf-8")
        self.paper.joinpath("main.pdf").write_bytes(b"%PDF-1.4 previous draft")
        figure = self.paper / "figures" / "syn.pdf"
        figure.parent.mkdir()
        figure.write_bytes(b"vector illustration")
        measurement = self.paper / "benchmarks" / "results" / "full_fit_timings.csv"
        measurement.parent.mkdir(parents=True)
        measurement.write_text("n,timing\n100,0.04\n")

        removed = builder._prepare_latex_transition(self.paper)
        self.assertIn("main.aux", removed)
        self.assertIn("main.bbl", removed)
        for suffix in (".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log"):
            self.assertFalse(self.paper.joinpath("main" + suffix).exists())
        self.assertTrue(self.paper.joinpath("main.pdf").is_file())
        self.assertEqual(figure.read_bytes(), b"vector illustration")
        self.assertEqual(measurement.read_text(), "n,timing\n100,0.04\n")

    def test_keeps_valid_author_year_cache(self):
        self.paper.joinpath("main.aux").write_text(
            "\\relax\n\\bibstyle{sn-mathphys-ay}\n", encoding="utf-8"
        )
        self.paper.joinpath("main.bbl").write_text("valid bibliography\n")
        self.assertEqual(builder._prepare_latex_transition(self.paper), [])
        self.assertTrue((self.paper / "main.aux").exists())
        self.assertTrue((self.paper / "main.bbl").exists())

    def test_recovers_from_changed_identity_stamp(self):
        state = self.paper / ".latex_build_identity.json"
        state.write_text(json.dumps({
            "document_class": "smcca", "bib_style": "abbrv",
        }))
        self.paper.joinpath("main.aux").write_text("old")
        removed = builder._prepare_latex_transition(self.paper)
        self.assertIn("main.aux", removed)
        builder._save_latex_identity(self.paper)
        self.assertEqual(
            json.loads(state.read_text())["bib_style"], "sn-mathphys-ay"
        )
        self.paper.joinpath("main.aux").write_text(
            r"\bibstyle{sn-mathphys-ay}" + "\n",
        )
        self.assertEqual(builder._prepare_latex_transition(self.paper), [])

    def test_rejects_old_class_before_running_experiments(self):
        self.source.write_text(
            r"\documentclass[english]{smcca}" + "\n"
            r"\bibliographystyle{abbrv}" + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "Pull the latest main branch"):
            builder._prepare_latex_transition(self.paper)

    def test_rejects_unexpected_springer_citation_style(self):
        self.source.write_text(
            r"\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}" + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "sn-mathphys-ay"):
            builder._prepare_latex_transition(self.paper)


if __name__ == "__main__":
    unittest.main()
