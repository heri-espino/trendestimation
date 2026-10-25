"""Scientific lecture source smoke checks; no measurements or PDF needed."""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LECTURE=ROOT/"slides"/"professor_lecture"


class MarpResearchLecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deck=(LECTURE/"main.md").read_text(encoding="utf-8")
        cls.script=(LECTURE/"make_figures.py").read_text(encoding="utf-8")

    def test_marptheme_and_full_research_scope(self):
        self.assertIn("marp: true", self.deck)
        self.assertIn("theme: trend-lecture", self.deck)
        self.assertIn("math: mathjax", self.deck)
        self.assertIn("html: true", self.deck)
        self.assertGreaterEqual(self.deck.count("\n---\n"), 80)
        for phrase in (
            "Whittaker", "Guerrero", "Cortés-Toto",
            "Normal", "likelihood", "CV", "GCV", "AICc", "BIC",
            "lambda", "smoothness", "banded", "nullspace",
            "profil", "Mauna Loa", "conditioning",
            "not yet", "future", "reproducib",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.deck.lower())

    def test_every_figure_reference_has_a_reproducible_recipe(self):
        names=set(re.findall(r"figures/([a-zA-Z0-9_]+\.svg)", self.deck))
        self.assertGreaterEqual(len(names), 40)
        dynamic={
            "09_diff_d1.svg", "10_diff_d2.svg", "11_diff_d3.svg",
            "19_hat_weak.svg", "20_hat_strong.svg",
            "47_measured_full.svg", "48_measured_trace.svg",
            "49_mauna_loa.svg",
        }
        static={m+".svg" for m in re.findall(
            r'save\("([0-9][a-zA-Z0-9_]+)"', self.script,
        )}
        static.discard("00_smoke.svg")  # generated only by --smoke
        self.assertEqual(names, static | dynamic)
        self.assertFalse((LECTURE/"main.md").read_text().count("TODO"))

    def test_project_sources_and_reproducible_vm_exports(self):
        for fname in ("theme.css", "build.ps1", "build.sh", "README.md"):
            with self.subTest(fname=fname):
                self.assertTrue((LECTURE/fname).is_file())
        for fname in ("build.ps1", "build.sh"):
            script=(LECTURE/fname).read_text(encoding="utf-8")
            self.assertIn("--theme-set", script)
            self.assertIn("--html", script)
            self.assertIn("--allow-local-files", script)
            self.assertIn("make_figures.py", script)
        self.assertIn("full_fit_timings.csv", self.script)
        self.assertIn("trace_timings.csv", self.script)
        self.assertIn("no host benchmark CSV present", self.script)

    def test_smoke_svg_generator(self):
        result=subprocess.run(
            [sys.executable, str(LECTURE/"make_figures.py"), "--smoke"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(
            result.returncode, 0,
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertTrue((LECTURE/"figures"/"00_smoke.svg").is_file())
        self.assertTrue((LECTURE/"figures"/"manifest.json").is_file())


if __name__=="__main__":
    unittest.main()
