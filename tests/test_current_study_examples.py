"""Regression tests for dated empirical sources, selection, and extrapolation."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
STUDY = REPO / "paper" / "computational-statistics-submission"


class CurrentExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        f=STUDY/"make_current_examples.py"
        spec=importlib.util.spec_from_file_location("current_examples",f)
        assert spec and spec.loader
        cls.mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=cls.mod
        spec.loader.exec_module(cls.mod)

    def test_pinned_noaa_snapshot(self):
        d,y=self.mod.load_series(
            STUDY/"data/noaa_mlo_monthly_1990_2026_09.csv",
            "average_ppm")
        self.assertEqual(len(y),441)
        self.assertEqual(d[0].isoformat(),"1990-01-01")
        self.assertEqual(d[-1].isoformat(),"2026-09-01")
        self.assertAlmostEqual(y[-1],426.07)

    def test_pinned_fred_snapshot_when_downloaded(self):
        source=STUDY/"data/fred_fedfunds_2010_2026_09.csv"
        if not source.is_file():
            self.skipTest("FRED snapshot produced by workflow")
        dates,y=self.mod.load_series(source,"value")
        self.assertEqual(len(y),201)
        self.assertEqual(dates[-1].isoformat(),"2026-09-01")
        self.assertAlmostEqual(y[-1],3.75)

    def test_local_polynomial_extension(self):
        t=np.arange(55,dtype=float)
        self.assertTrue(np.allclose(
            self.mod.extrapolate_tail(4+2*t,2,12),
            4+2*np.arange(55,67,dtype=float),atol=1e-10))
        const=self.mod.extrapolate_tail(t,1,12)
        self.assertTrue(np.allclose(const,t[-1]))
        q=1+0.5*t+0.01*t*t
        self.assertTrue(np.allclose(
            self.mod.extrapolate_tail(q,4,12),
            1+0.5*np.arange(55,67)+.01*np.arange(55,67)**2,
            atol=1e-9))

    def test_selection_same_lambda_candidates_across_criteria(self):
        y=np.sin(np.linspace(0,10,40))+np.linspace(0,1,40)
        smoother, results=self.mod.estimate_candidates(y,2)
        self.assertEqual(set(results),set(self.mod.METHODS))
        for name in self.mod.METHODS:
            x=results[name]
            self.assertAlmostEqual(
                smoother.smoothness(x["lambda"]),x["s"],places=7)
        self.assertAlmostEqual(results["controlled"]["s"],.86,places=7)
        self.assertTrue(all(
            results[name]["candidate_count"]==29
            for name in self.mod.METHODS[:4]))

    def test_manuscript_cites_guarded_extrapolation(self):
        main=(STUDY/"main.tex").read_text()
        section=(STUDY/"current_applications.tex").read_text()
        self.assertIn(r"\input{current_applications.tex}",main)
        self.assertIn("not a substitute",section)
        self.assertIn("Board of Governors",section)
        self.assertIn("2026",section)


if __name__=="__main__":
    unittest.main()
