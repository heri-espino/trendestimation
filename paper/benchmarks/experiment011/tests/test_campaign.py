"""Fast, stdlib-only tests for Experiment011 planning and numerical audit.

No expensive PLS smoothing, no data download, no benchmark timings.
"""
from __future__ import annotations

import copy
from types import SimpleNamespace
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import campaign
import full_plan
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
        self.assertEqual(len(design["cases"]), 29)
        self.assertEqual(
            {case["stage"] for case in design["cases"]},
            {"smoke", "pilot", "confirm"},
        )
        self.assertTrue(all(c["repeats_per_block"] >= 1
                            for c in design["cases"]))
        self.assertTrue(all(c["conditional_data_mu"] == (c["mu"] == "data")
                            for c in design["cases"]))

    def test_targeted_d4_and_medium_large_size_extensions(self):
        design = campaign.load_design()
        cases = {c["id"]: c for c in design["cases"]}
        self.assertEqual(
            {(c["stage"], c["n"], c["d"], c["criterion"])
             for c in cases.values() if c["n"] in (2048, 4096)},
            {("confirm", n, 4, criterion)
             for n in (2048, 4096) for criterion in ("gcv", "cv")}
        )
        for n in (1024, 2048, 4096):
            for criterion in ("gcv", "cv"):
                name = f"confirm_{criterion}_n{n}_d4_m100"
                self.assertIn(name, cases)
                case = cases[name]
                self.assertEqual(case["stage"], "confirm")
                self.assertEqual(case["grid_denominator"], 100)
                self.assertIn("banded_cholesky", case["methods"])
                if n >= 2048:
                    self.assertEqual(case["methods"], ["banded_cholesky"])
                if n == 1024:
                    self.assertEqual(case["max_work"], 750_000_000)
                    self.assertIn("spectral_svd", case["methods"])
                    states = campaign.preflights(case,design)
                    self.assertEqual(
                        [x["preflight"] for x in states
                         if x["method"]=="spectral_svd"
                         and x["scenario"]=="grid_multiple_series"],
                        ["eligible"]
                    )
        for criterion in ("gcv", "cv"):
            self.assertIn(f"pilot_{criterion}_n256_d4_m100", cases)
        # No old case was renamed or removed.
        for name in ("smoke_gcv_n64_d1_m100",
                     "pilot_cv_n128_d3_m100",
                     "confirm_mle_n512_d3_m100"):
            self.assertIn(name, cases)

    def test_extended_n_is_temporary_and_old_factor_levels_unchanged(self):
        baseline = (64, 128, 256, 512, 1024, 16384, 131072)
        engine = SimpleNamespace(N_LEVELS=baseline)
        with campaign.approved_experiment011_size(engine, 4096):
            self.assertIn(4096, engine.N_LEVELS)
            self.assertEqual(engine.N_LEVELS[:-1], baseline)
        self.assertEqual(engine.N_LEVELS, baseline)
        with self.assertRaisesRegex(RuntimeError, "deliberate"):
            with campaign.approved_experiment011_size(engine, 2048):
                self.assertIn(2048, engine.N_LEVELS)
                raise RuntimeError("deliberate")
        self.assertEqual(engine.N_LEVELS, baseline)
        with self.assertRaises(ValueError):
            with campaign.approved_experiment011_size(engine, 8192):
                pass
        self.assertEqual(engine.N_LEVELS, baseline)

    def test_full_tensor_is_declared_without_running_a_solver(self):
        axes=full_plan.full_axes()
        self.assertEqual(axes["n"],
                         [64,128,256,512,1024,16384,131072])
        self.assertEqual(axes["d"],list(range(1,7)))
        self.assertEqual(axes["mu"],["0","data","0.15"])
        self.assertEqual(len(axes["method"]),10)
        self.assertEqual(axes["criterion"],
                         ["cv","gcv","bic","aicc","mle"])
        self.assertEqual(axes["grid_denominator"],
                         [100,1000,10000,100000])
        self.assertEqual(len(axes["workload"]),4)
        self.assertEqual(len(axes["coordinate"]),2)
        expected=(len(axes["n"])*len(axes["d"])*
                  len(axes["mu"])*len(axes["amplitude"])*
                  len(axes["criterion"])*len(axes["method"])*
                  len(axes["coordinate"])*
                  (2+2*len(axes["grid_denominator"])))
        self.assertEqual(expected,252_000)

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

    def test_single_banded_backend_keeps_valid_time_without_fake_parity(self):
        rows, manifest, env = fixture()
        rows = [r for r in rows if r["method"]=="banded_cholesky"]
        manifest["method_order"]=["banded_cholesky"]
        env["methods"]=["banded_cholesky"]
        qa=audit_rows(rows,manifest,env)
        self.assertEqual(qa["status_counts"],{"ok":8})
        self.assertEqual(qa["paired_method_comparisons"],[])
        self.assertEqual(
            qa["classification"],"single_backend_timing_only_no_parity_reference"
        )

    def test_wrong_git_commit_fails(self):
        rows, manifest, env = fixture()
        env["git_sha"] = "other"
        with self.assertRaisesRegex(ValueError, "source commit"):
            audit_rows(rows, manifest, env)


if __name__ == "__main__":
    unittest.main()
