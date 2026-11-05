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
