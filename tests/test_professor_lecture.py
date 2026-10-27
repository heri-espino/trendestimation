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

    def test_bounded_smoothness_is_explained_before_technical_sections(self):
        """Core formulas, numerical interpretation and code must stay visible."""
        deck = self.deck
        opening = deck.split("# I. Why estimate a trend?")[0]
        self.assertIn("The central question in three formulas", opening)
        self.assertIn(r"s=S(\lambda)", opening)
        self.assertIn(r"S^{-1}(\widehat s)", opening)
        self.assertIn("Interpret a smoothness target S = 0.8", deck)
        self.assertIn(r"\nu(\lambda)=n-(n-d)S(\lambda)", deck)
        self.assertIn("$21.6$", deck)
        self.assertIn("not 80% of the noise", deck)
        self.assertIn("Two search coordinates: what changes?", deck)
        self.assertIn('search_space="lambda"', deck)
        self.assertIn('search_space="smoothness"', deck)
        self.assertIn("np.testing.assert_allclose(from_lam.scores, from_s.scores", deck)
        self.assertIn("solver.lambda_for_smoothness(target_s)", deck)
        self.assertIn("not automatically faster", deck)
        self.assertIn("docs/smoothness_coordinate.rst", deck)
        self.assertIn("manual GitHub Pages deployment", deck)
        self.assertIn("end-to-end optimization", deck)

    def test_every_figure_reference_has_a_reproducible_recipe(self):
        names=set(re.findall(r"figures/([a-zA-Z0-9_]+\.svg)", self.deck))
        self.assertGreaterEqual(len(names), 40)
        dynamic={
            "09_diff_d1.svg", "10_diff_d2.svg", "11_diff_d3.svg",
            "19_hat_weak.svg", "20_hat_strong.svg",
            "47_measured_full.svg", "48_measured_trace.svg",
            "49_mauna_loa.svg",
            "50_cv_coordinate_pair.svg", "51_gcv_coordinate_pair.svg",
            "52_aicc_coordinate_pair.svg", "53_bic_coordinate_pair.svg",
            "54_coordinate_factorial.svg", "55_s_vs_lambda_ratio.svg",
            "56_phase_breakdown.svg", "57_optimum_quality.svg",
            "58_public_coordinate_runtime.svg",
            "59_public_candidate_quality.svg",
            "60_windows_workloads.svg", "61_windows_grid_coordinates.svg",
            "62_windows_reuse_eight.svg", "63_windows_bounded_search.svg",
            "64_windows_fixed_mu.svg",
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
        windows=(LECTURE/"build.ps1").read_text(encoding="utf-8")
        self.assertIn('Join-Path $RepositoryRoot "src"', windows)
        self.assertIn('$env:PYTHONPATH=$SourceDirectory', windows)
        self.assertIn('[IO.Path]::PathSeparator', windows)
        self.assertIn('Remove-Item Env:PYTHONPATH', windows)
        for fname in ("build.ps1", "build.sh"):
            script=(LECTURE/fname).read_text(encoding="utf-8")
            self.assertIn("--theme", script)
            self.assertIn("--html", script)
            self.assertIn("--allow-local-files", script)
            self.assertIn("make_figures.py", script)
        self.assertTrue((LECTURE / "coordinate_experiment_figures.py").is_file())
        self.assertIn("paired_score_figures", self.script)
        self.assertIn("measured_figures", self.script)
        self.assertIn("public_selector_figures", self.script)
        self.assertIn("full_fit_timings.csv", self.script)
        self.assertIn("trace_timings.csv", self.script)
        self.assertIn("no host benchmark CSV present", self.script)

    def test_windows_full_preset_slides_use_actual_published_sources(self):
        windows=LECTURE/"windows_full_results.py"
        self.assertTrue(windows.is_file())
        content=windows.read_text(encoding="utf-8")
        self.assertIn("source_sha256",content)
        self.assertIn("stage_windows_figures",content)
        self.assertIn("80640",content)
        for key in ("60_windows_workloads","61_windows_grid_coordinates",
                    "62_windows_reuse_eight","63_windows_bounded_search",
                    "64_windows_fixed_mu"):
            self.assertIn(f"figures/{key}.svg",self.deck)
        for key in ("windows_full_s_workloads","windows_full_s_grid_coordinates",
                    "windows_full_s_reuse_d","windows_full_s_bounded",
                    "windows_full_s_means"):
            self.assertTrue((ROOT/"paper"/"figures"/f"{key}.svg").is_file())
        self.assertIn("80,640 actual measurements",self.deck)
        self.assertIn("11.234 ms",self.deck)
        self.assertIn("3.980 ms",self.deck)
        self.assertIn("4,484 valid matched-coordinate seed pairs",self.deck)
        self.assertIn("bounded local",self.deck)
        self.assertIn("report_windows_full_s.py",self.deck)

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
