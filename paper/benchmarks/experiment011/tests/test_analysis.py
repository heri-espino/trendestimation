"""Unit tests for the long-form measured-time tensor and paired baseline.

No numerical solver is executed; values below are synthetic TEST FIXTURES
and must never be described as observed benchmark timings.
"""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze import paired_naive, summaries, block_mean_ci


def measurements(block=0, run_tag="fakefixture", source="sha"):
    rows=[]
    for coord in ("direct_s","mapped_lambda"):
        for scenario in ("one_s_one_series","grid_one_series",
                         "one_s_multiple_series","grid_multiple_series"):
            for method,seconds in (
                ("spectral_svd",1.0),
                ("banded_cholesky",2.0),
                ("naive_inverse",4.0)
            ):
                rows.append(dict(
                    run_tag=run_tag,case_id="smoke_testonly_fixture",
                    block=block,block_seed=12345+block*10000,
                    repeat=0,coordinate=coord,workload=scenario,
                    environment_fingerprint="environment1",
                    experiment006_source_sha256=source,
                    method=method,status="ok",criterion="gcv",
                    selected_s=.5,selected_score=1.0,
                    total_cold_s=seconds,
                    n=64,d=1,mu=0,amplitude="low",
                    M=100 if scenario.startswith("grid") else 1,
                    R=2 if scenario.endswith("multiple_series") else 1,
                    host="fake_not_actual_hardware",
                    qa_classification="float64_parity_only_not_precision_certified"
                ))
    return rows


class TensorAnalysisTests(unittest.TestCase):
    def test_exact_paired_naive_speedup(self):
        pairs=paired_naive(measurements())
        self.assertEqual(len(pairs),16)
        bymethod={}
        for row in pairs:
            bymethod.setdefault(row["method"],set()).add(row["paired_naive_speedup"])
        self.assertEqual(bymethod,{"spectral_svd":{4.},"banded_cholesky":{2.}})

    def test_single_block_cannot_generate_ci(self):
        aggregated=summaries(measurements())
        self.assertEqual(len(aggregated),24)
        self.assertTrue(all(x["complete_independent_blocks"]==1
                            for x in aggregated))
        self.assertTrue(all(x["block_bootstrap_ci95_low_s"]==""
                            for x in aggregated))
        self.assertTrue(all(not x["ready_for_block_level_uncertainty"]
                            for x in aggregated))

    def test_three_distinct_seeds_allow_interval(self):
        rows=measurements(0)+measurements(1)+measurements(2)
        aggregate=summaries(rows)
        self.assertEqual(len(aggregate),24)
        self.assertTrue(all(x["complete_independent_blocks"]==3
                            for x in aggregate))
        self.assertTrue(all(x["block_bootstrap_ci95_low_s"]!=""
                            for x in aggregate))
        self.assertTrue(all(x["ready_for_block_level_uncertainty"]
                            for x in aggregate))

    def test_duplicate_seed_is_not_independent_replication(self):
        rows=measurements(0,"run_one")+measurements(0,"run_two")
        agg=summaries(rows)
        self.assertTrue(all(x["complete_independent_blocks"]==0 for x in agg))
        self.assertTrue(all(x["status"]=="incomplete_no_mean" for x in agg))

    def test_invalid_method_cannot_claim_naive_speedup(self):
        rows=measurements()
        for row in rows:
            if row["method"]=="spectral_svd":
                row["status"]="numerical_failed"
        pairs=paired_naive(rows)
        self.assertEqual(len(pairs),8)
        self.assertTrue(all(x["method"]=="banded_cholesky" for x in pairs))


if __name__=="__main__":
    unittest.main()
