"""Regression checks for the finite-grid solver x criterion x coordinate study.

The user-facing PDF/HTML presentation does not need to be generated for
these tests, and no timing observation is asserted as a reference truth.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
SLIDES = ROOT / "slides" / "professor_lecture"


class CoordinateMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(BENCH))
        path = BENCH / "criterion_coordinate_matrix.py"
        spec = importlib.util.spec_from_file_location(
            "criterion_coordinate_matrix", path)
        assert spec and spec.loader
        cls.study = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.study)

    def test_all_36_criterion_solver_coordinate_cells(self):
        m = self.study
        self.assertEqual(len(m.METHODS)*len(m.CRITERIA)*
                         len(m.COORDINATES), 36)
        self.assertEqual(m.METHODS, ("svd", "eigh", "cholesky"))
        self.assertEqual(m.CRITERIA, ("cv", "gcv", "aicc", "bic"))
        self.assertEqual(m.COORDINATES, ("lambda", "s_mapped", "s_uniform"))

    def test_scorers_and_backend_native_inverse_agree(self):
        m = self.study
        n, d, mu = 24, 2, .1
        y = m.sample_data(n, d, 20261025)
        penalty = 10.0
        models = {s: m.Scorer(n, d, y, mu, s) for s in m.METHODS}
        s_reference = models["svd"].smoothness(penalty)
        self.assertTrue(0 < s_reference < 1)
        for solver, backend in models.items():
            with self.subTest(solver=solver):
                self.assertAlmostEqual(
                    backend.smoothness(penalty), s_reference, places=7)
                inversion = backend.inverse_s(s_reference)
                self.assertAlmostEqual(inversion/penalty, 1, places=6)
                for criterion in m.CRITERIA:
                    first = backend.score(penalty, criterion)
                    second = models["svd"].score(penalty, criterion)
                    self.assertTrue(np.isclose(first, second,
                                               rtol=2e-5, atol=2e-6),
                                    msg=f"{solver}, {criterion}: {first} vs {second}")

    def test_mapped_grid_same_candidate_and_score(self):
        m = self.study
        n, d, mu = 24, 2, 0.0
        y = m.sample_data(n, d, 123)
        penalty = np.geomspace(.05, 100.0, 5)
        svd = m.Scorer(n, d, y, mu, "svd")
        matched = np.asarray([svd.smoothness(float(x)) for x in penalty])
        for solver in m.METHODS:
            for criterion in m.CRITERIA:
                lhs = m.run_cell(
                    n=n, d=d, mu=mu, y=y, criterion=criterion, solver=solver,
                    coordinate="lambda", candidates=penalty, s_mapped=matched,
                    seed=123, case=0, block=0, preset="test")
                rhs = m.run_cell(
                    n=n, d=d, mu=mu, y=y, criterion=criterion, solver=solver,
                    coordinate="s_mapped", candidates=penalty, s_mapped=matched,
                    seed=123, case=0, block=0, preset="test")
                self.assertTrue(np.isclose(
                    lhs["selected_score"], rhs["selected_score"],
                    rtol=2e-6, atol=2e-7), msg=f"{solver}/{criterion}")
                self.assertLess(rhs["lambda_roundtrip_max_log_error"], 2e-5)
                self.assertEqual(rhs["inverse_calls"], len(penalty))
                self.assertEqual(lhs["inverse_calls"], 0)

    def test_sources_of_measured_figures_and_protocol(self):
        script = (SLIDES / "coordinate_experiment_figures.py").read_text()
        main = (SLIDES / "main.md").read_text()
        for basename in (
            "50_cv_coordinate_pair", "51_gcv_coordinate_pair",
            "52_aicc_coordinate_pair", "53_bic_coordinate_pair",
            "54_coordinate_factorial", "55_s_vs_lambda_ratio",
            "56_phase_breakdown", "57_optimum_quality",
            "58_public_coordinate_runtime", "59_public_candidate_quality",
        ):
            self.assertIn("figures/"+basename+".svg", main)
        self.assertIn("STUDY/\"summary.csv\"", script)
        self.assertIn("STUDY/\"public_summary.csv\"", script)
        self.assertIn("missing-data panels", script)


if __name__ == "__main__":
    unittest.main()
