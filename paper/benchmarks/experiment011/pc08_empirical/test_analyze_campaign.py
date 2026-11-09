"""Source-only regression tests. No raw Windows dataset and no benchmarks needed."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze_campaign as a


def row(method,seed=3,phase=24,coord="direct_s",status="ok",evaluations=100,
        M=100,R=1,time=1.0,selected=0.5,score=0.4):
    return {
        "seed_index":seed,"case_id":"test_case","repeat":0,"coordinate":coord,
        "workload":"grid_one_series","phase_workers":phase,
        "environment_fingerprint":"fixture_env","source_file_sha256":"fixture_engine",
        "method":method,"n":64,"d":1,"criterion":"gcv","mu":"0","amplitude":"low",
        "M":M,"R":R,"status":status,"selected_s":selected,"selected_score":score,
        "total_cold_s":time,"valid_full_search":True,"grid_denominator":100,
        "method_setup_s":0.1,"candidate_evaluation_s":0.7,
        "s_to_lambda_s":0.1,"total_warm_s":0.8,"evaluations":evaluations
    }


class IngestionRules(unittest.TestCase):
    def test_candidate_coverage_is_required(self):
        manifest={"method_order":["spectral_svd"],"source_file_sha256":"hash"}
        env={"blas_threads":1,"git_sha":"commit","code_sha256":"hash"}
        manifest["source_commit"]="commit"
        job={"returncode":0}
        qa={"issues":[]}
        candidate=row("spectral_svd",evaluations=95)
        self.assertEqual(a.record_valid(candidate,qa,manifest,env,job),
                         "incomplete_candidate_coverage")
        candidate["evaluations"]=100
        self.assertEqual(a.record_valid(candidate,qa,manifest,env,job),
                         "complete_float64_status_only")
        job["returncode"]=1
        self.assertEqual(a.record_valid(candidate,qa,manifest,env,job),
                         "process_nonzero_exit")

    def test_pairing_rejects_unequal_sources_and_worker_strata(self):
        r1=row("banded_cholesky",time=2)
        r2=row("spectral_svd",time=1)
        self.assertEqual(len(a.pair_rows([r1,r2])),1)  # only banded baseline is present
        r2["phase_workers"]=12
        self.assertEqual(a.pair_rows([r1,r2]),[])
        r2["phase_workers"]=24
        r2["source_file_sha256"]="different"
        self.assertEqual(a.pair_rows([r1,r2]),[])

    def test_invalid_method_cannot_win(self):
        fast=row("spectral_svd",time=0.001)
        fast["valid_full_search"]=False
        slow=row("banded_cholesky",time=2)
        self.assertEqual(a.pair_rows([fast,slow]),[])

    def test_selected_score_parity_gate(self):
        r1=row("banded_cholesky",time=2)
        r2=row("spectral_svd",time=1,selected=0.8)
        pairs=a.pair_rows([r1,r2])
        self.assertEqual(len(pairs),1)
        self.assertFalse(any(p["float64_pair"] for p in pairs))
        self.assertTrue(all(p["pair_status"]=="score_or_s_disagreement" for p in pairs))

    def test_coordinate_comparison_only_same_seed_and_method(self):
        r1=row("spectral_svd",coord="direct_s",time=2)
        r2=row("spectral_svd",coord="mapped_lambda",time=1)
        self.assertEqual(len(a.coord_pairs([r1,r2])),1)
        r2["seed_index"]=4
        self.assertEqual(len(a.coord_pairs([r1,r2])),0)

    def test_uncertainty_needs_independent_clusters(self):
        mean,low,high=a.logratio_ci([math.log(2)]*2)
        self.assertAlmostEqual(mean,2)
        self.assertEqual(low,"")
        self.assertEqual(high,"")
        mean,low,high=a.logratio_ci([math.log(2)]*10)
        self.assertAlmostEqual(mean,2)
        self.assertAlmostEqual(low,2)
        self.assertAlmostEqual(high,2)

    def test_reliability_preserves_execution_phases(self):
        p=row("spectral_svd",phase=24)
        q=row("spectral_svd",phase=12)
        q["valid_full_search"]=False
        rows=a.reliability([p,q])
        self.assertEqual(len(rows),2)
        results={int(r["phase_workers"]):r for r in rows}
        self.assertEqual(results[24]["valid_rate"],1)
        self.assertEqual(results[12]["valid_rate"],0)


if __name__=="__main__":
    unittest.main()
