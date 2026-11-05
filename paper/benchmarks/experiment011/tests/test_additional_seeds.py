"""Independent seed-stream and metadata checks; no timings."""
import contextlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import additional_seeds as extra  # noqa: E402
import campaign  # noqa: E402


class SeedTests(unittest.TestCase):
    def test_all_cases_and_nonoverlapping_repeat_series_streams(self):
        design = campaign.load_design()
        work = extra.jobs(design)
        self.assertEqual(len(work), 97*29)
        for case in design['cases']:
            seen = set()
            seeds = [design['seed_base']+10000*b for b in range(case['planned_blocks'])]
            seeds += [seed for _,seed,c,_ in work if c['id']==case['id']]
            for seed in seeds:
                for repeat in range(case['repeats_per_block']):
                    for k in range(case['series_count']):
                        actual = seed+100000*repeat+23*k+29*case['n']+7*case['d']
                        self.assertNotIn(actual, seen)
                        seen.add(actual)

    def test_explicit_seed_is_written_to_dry_run_metadata(self):
        args = SimpleNamespace(case='smoke_gcv_n64_d1_m100', seed=1000000000,
                               run_tag='seed_test', block=0, allow_confirm=False,
                               dry_run=True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            campaign.run_one(args)
        self.assertEqual(json.loads(out.getvalue())['config']['seed'], args.seed)

    def test_negative_seed_rejected(self):
        with self.assertRaises(ValueError):
            campaign.run_one(SimpleNamespace(case='smoke_gcv_n64_d1_m100',
                              seed=-1, run_tag='seed_test', block=0))

    def test_large_svd_preflight_explicit_opt_in(self):
        before = campaign.CASE_FILE.read_bytes()
        args = SimpleNamespace(case='confirm_gcv_n4096_d4_m100', seed=1000000000,
                               run_tag='large_seed_test', block=0, allow_confirm=True,
                               dry_run=True, large_svd=True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            campaign.run_one(args)
        config = json.loads(out.getvalue())['config']
        self.assertEqual(config['method_order'], ['spectral_svd', 'banded_cholesky'])
        self.assertTrue(config['large_svd_opt_in'])
        self.assertTrue(all(p['preflight']=='eligible' for p in config['preflights']))
        self.assertEqual(before, campaign.CASE_FILE.read_bytes())

    def test_large_svd_rejects_unintended_sizes(self):
        args = SimpleNamespace(case='smoke_gcv_n64_d1_m100', seed=1000000000,
                               run_tag='large_seed_test', block=0, allow_confirm=True,
                               dry_run=True, large_svd=True)
        with self.assertRaises(ValueError):
            campaign.run_one(args)

    def test_resume_preserves_numerical_failures_and_only_schedules_missing(self):
        import resume_seeds
        design=campaign.load_design()
        work=extra.jobs(design)
        done=[]
        for i,seed,case,block in work[:5]:
            done.append(dict(seed_index=i+3, seed=seed,case=case['id'],
                             block=block,returncode=0,
                             counts={'spectral_svd':{'numerical_failed':4}}))
        report=dict(cases_sha256=campaign.sha256_file(campaign.CASE_FILE),
                    large_svd_opt_in=True,results=done)
        self.assertEqual(resume_seeds.remaining(report,design),work[5:])
        report['results'].append(done[0])
        with self.assertRaises(ValueError):
            resume_seeds.remaining(report,design)
