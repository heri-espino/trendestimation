"""Fast, stdlib-only tests for Experiment011 planning and numerical audit.

No expensive PLS smoothing, no data download, no benchmark timings.
"""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import campaign
from verify import audit_rows, SCENARIOS, POLICIES


def fixture(criterion: str = "gcv"):
    case = dict(
        id="synthetic_validation_only", n=64, d=2, criterion=criterion,
        grid_denominator=100, series_count=2, repeats_per_block=1,
        methods=["spectral_svd", "banded_cholesky", "naive_inverse"],
    )
    methods = list(case["methods"])
    manifest = dict(case=case, method_order=methods, block=0,
                    source_commit="deadbeef")
    env = dict(n=64, d=2, criterion=criterion, denominator=100,
               R=2, repeats=1, blas_threads=1,
               methods=methods, git_sha="deadbeef")
    rows = []
    for method in methods:
        for policy in POLICIES:
            for workload in SCENARIOS:
                r = 1 if workload.endswith("one_series") else 2
                m = 1 if workload.startswith("one_s") else 100
                rows.append(dict(
                    n="64", d="2", criterion=criterion,
                    grid_denominator="100", method=method,
                    coordinate=policy, workload=workload, repeat="0",
                    R=str(r), M=str(m), status="ok",
                    selected_s="0.5",
                    selected_score=("3.0" if criterion != "mle"
                                    else "40.0" if method == "banded_cholesky"
                                    else "3.0"),
                    total_cold_s="0.5", total_warm_s="0.25",
                ))
    return rows, manifest, env


class Experiment011PlanningTests(unittest.TestCase):
    def test_declared_design_and_safe_cases(self):
        design = campaign.load_design()
        self.assertEqual(design["experiment"], "experiment011")
        self.assertGreaterEqual(len(design["cases"]), 15)
        self.assertEqual(
            {case["stage"] for case in design["cases"]},
            {"smoke", "pilot", "confirm"},
        )
        self.assertTrue(all(c["repeats_per_block"] >= 1
                            for c in design["cases"]))
        self.assertTrue(all(c["conditional_data_mu"] == (c["mu"] == "data")
                            for c in design["cases"]))

    def test_rotation_logic_preserves_method_set(self):
        methods = ("spectral_svd", "banded_cholesky", "naive_inverse")
        for k in range(3):
            rotation = methods[k:] + methods[:k]
            self.assertEqual(set(rotation), set(methods))
            self.assertEqual(len(rotation), 3)


class Experiment011AuditTests(unittest.TestCase):
    def test_complete_valid_parity_is_not_precision_certification(self):
        rows, manifest, env = fixture()
        result = audit_rows(rows, manifest, env)
        self.assertEqual(result["raw_rows"], 24)
        self.assertEqual(result["status_counts"], {"ok": 24})
        self.assertEqual(
            result["classification"],
            "float64_parity_only_not_precision_certified"
        )
        self.assertEqual(len(result["paired_method_comparisons"]), 16)

    def test_marginal_mle_score_offset_not_comparable(self):
        rows, manifest, env = fixture("mle")
        result = audit_rows(rows, manifest, env)
        self.assertEqual(
            result["classification"],
            "float64_parity_only_not_precision_certified"
        )
        self.assertTrue(all(
            x["relative_score_difference"] is None
            for x in result["paired_method_comparisons"]
        ))

    def test_deviating_selected_s_requests_numerical_review(self):
        rows, manifest, env = fixture()
        rows[1]["selected_s"] = "0.7"
        result = audit_rows(rows, manifest, env)
        self.assertEqual(
            result["classification"], "needs_independent_numerical_review"
        )
        self.assertTrue(result["issues"])

    def test_resource_skips_are_not_silent_successes(self):
        rows, manifest, env = fixture()
        subset = [r for r in rows if
                  not (r["method"] == "naive_inverse"
                       and r["coordinate"] == "direct_s"
                       and r["workload"] == "grid_multiple_series")]
        exemplar = copy.deepcopy(rows[-1])
        exemplar.update(
            method="naive_inverse", coordinate="direct_s",
            workload="grid_multiple_series", repeat="-1",
            status="budget_exceeded",
            selected_s="nan", selected_score="nan",
        )
        subset.append(exemplar)
        result = audit_rows(subset, manifest, env)
        self.assertEqual(result["classification"],
                         "partial_success_with_skips_or_failures")
        self.assertEqual(result["status_counts"]["budget_exceeded"], 1)

    def test_missing_expected_cell_fails(self):
        rows, manifest, env = fixture()
        with self.assertRaisesRegex(ValueError, "Missing complete"):
            audit_rows(rows[:-1], manifest, env)

    def test_wrong_git_commit_fails(self):
        rows, manifest, env = fixture()
        env["git_sha"] = "other"
        with self.assertRaisesRegex(ValueError, "source commit"):
            audit_rows(rows, manifest, env)


if __name__ == "__main__":
    unittest.main()
