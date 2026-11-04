"""No expensive numerical computation: parallel throughput contract tests."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from parallel_series import audit_parallel, run_parallel


def fake_rows(methods=("spectral_svd","banded_cholesky"),R=3,repeats=1):
    rows=[]
    for method in methods:
        for repeat in range(repeats):
            for j in range(R):
                for workload,M in (("one_s_multiple_series",1),
                                   ("grid_multiple_series",100)):
                    for coordinate in ("direct_s","mapped_lambda"):
                        rows.append(dict(
                            method=method, repeat=repeat, series_index=j,
                            coordinate=coordinate,workload=workload,
                            criterion="gcv",
                            status="ok",selected_s=.5,selected_score=2.,
                            attributed_total_s=.02,evaluations=M,M=M,
                        ))
    return rows


class ParallelSeriesTests(unittest.TestCase):
    def test_coverage_is_per_series_not_fake_aggregated_s(self):
        rows=fake_rows()
        qa=audit_parallel(rows,["spectral_svd","banded_cholesky"],3,1)
        self.assertEqual(qa["actual_rows"],24)
        self.assertEqual(qa["paired_method_comparisons"],12)
        self.assertEqual(qa["classification"],
                         "float64_parity_only_not_precision_certified")

    def test_invalid_grid_coverage_is_rejected(self):
        rows=fake_rows()
        rows[2]["evaluations"]=70
        with self.assertRaisesRegex(ValueError,"Partial grid"):
            audit_parallel(rows,["spectral_svd","banded_cholesky"],3,1)

    def test_numerical_divergence_is_recorded_not_masked(self):
        rows=fake_rows()
        rows[0]["selected_s"]=.7
        qa=audit_parallel(rows,["spectral_svd","banded_cholesky"],3,1)
        self.assertEqual(qa["classification"],
                         "needs_independent_numerical_review")
        self.assertTrue(qa["issues"])

    def test_safeguards_for_small_cases_and_worker_count(self):
        cfg=dict(
            id="smoke_only",stage="smoke",n=64,d=1,
            grid_denominator=100,criterion="gcv",mu="0",
            amplitude="low",methods=["spectral_svd","banded_cholesky"],
            repeats_per_block=1,planned_blocks=1,series_count=3,
        )
        kwargs=dict(run_tag="dry_001",block=0,series_count=3,
                    series_workers=2,max_work=5e8,
                    max_dense_bytes=2*1024**3,
                    seed_base=20261103,source_commit="testfixture",
                    source_hashes={"experiment006":"testfixture"},
                    dry_run=True)
        result=run_parallel(cfg,**kwargs)
        self.assertTrue(result["metadata"]["not_comparable_to_serial_r_cache_latency"])
        self.assertEqual(result["metadata"]["series_workers"],2)
        with self.assertRaisesRegex(ValueError,"small n"):
            run_parallel({**cfg,"n":1024},**kwargs)
        with self.assertRaisesRegex(ValueError,"series_workers"):
            run_parallel(cfg,**{**kwargs,"series_workers":4})
        with self.assertRaisesRegex(ValueError,"series_count"):
            run_parallel(cfg,**{**kwargs,"series_count":33})

    def test_parallel_copy_of_existing_serial_archive_never_occurs(self):
        cfg=dict(
            id="smoke_only",stage="smoke",n=64,d=1,
            grid_denominator=100,criterion="gcv",mu="0",
            amplitude="low",methods=["spectral_svd","banded_cholesky"],
            repeats_per_block=1,planned_blocks=1,series_count=3,
        )
        dry=run_parallel(
            cfg,run_tag="test_001",block=0,series_count=3,
            series_workers=3,max_work=5e8,
            max_dense_bytes=2*1024**3,seed_base=20261103,
            source_commit="fixture",source_hashes={},dry_run=True
        )
        self.assertIn("runs_parallel",dry["output"])
        self.assertNotIn("/runs/",dry["output"].replace("\\","/"))


if __name__=="__main__":
    unittest.main()
