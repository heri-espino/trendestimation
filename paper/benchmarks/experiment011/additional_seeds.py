"""Additional seeded trials; preserve failures and concurrent-load provenance."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import campaign


def jobs(design):
    # Separate repeat/series streams from the original three blocks and
    # from one another (the engine adds 100000*repeat + 23*k + 29*n + 7*d).
    return [(i, 1_000_000_000 + 1_000_000*i, c,
             i % c['planned_blocks'])
            for i in range(97) for c in design['cases']]


def execute(job, tag, archive):
    index, seed, case, block = job
    seed_tag = f'{tag}_s{index+3:03d}'
    cmd = [sys.executable, str(campaign.HERE/'campaign.py'), 'run',
           '--case', case['id'], '--run-tag', seed_tag, '--block', str(block),
           '--seed', str(seed), '--allow-confirm']
    started = time.perf_counter()
    log = archive/f"s{index+3:03d}_{case['id']}.log"
    with log.open('w', encoding='utf8') as handle:
        proc = subprocess.run(cmd, cwd=campaign.ROOT, stdout=handle,
                              stderr=subprocess.STDOUT, check=False)
    folder = campaign.RUNS/seed_tag/case['id']/f'block{block:03d}'
    raw = folder/'measurements/raw_times.csv'
    counts = defaultdict(Counter)
    if raw.exists():
        with raw.open(newline='', encoding='utf8') as handle:
            for row in csv.DictReader(handle):
                status = row['status']
                if status == 'ok' and int(row['evaluations']) != int(row['M'])*int(row['R']):
                    status = 'incomplete_coverage'
                counts[row['method']][status] += 1
    qa_file = folder/'experiment011_qa.json'
    qa = json.loads(qa_file.read_text()) if qa_file.exists() else {}
    return dict(seed_index=index+3, seed=seed, case=case['id'], block=block,
                returncode=proc.returncode, wall_s=time.perf_counter()-started,
                counts={k:dict(v) for k,v in counts.items()},
                qa_classification=qa.get('classification', 'missing_qa'),
                qa_issues=qa.get('issues', []), log=log.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-tag', required=True)
    parser.add_argument('--workers', type=int, default=24)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not campaign.VALID_TAGS.fullmatch(args.run_tag) or len(args.run_tag)>43:
        raise ValueError('Use a safe run tag at most 43 characters long')
    if not 1 <= args.workers <= 24:
        raise ValueError('workers must be between 1 and 24')
    if Path.cwd().resolve() != campaign.ROOT:
        raise ValueError('Run from repository root')
    design = campaign.load_design()
    work = jobs(design)
    print(f'97 additional base seeds; {len(design["cases"])} cases; {len(work)} jobs', flush=True)
    if args.dry_run:
        print('PLAN ONLY; no observations generated')
        return
    archive = campaign.HERE/'campaigns'/args.run_tag
    archive.mkdir(parents=True, exist_ok=False)
    for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS',
                'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
        os.environ[key] = '1'
    report = dict(mode='concurrent_case_blocks_not_isolated_latency',
                  source_commit=campaign.git_sha(), workers=args.workers,
                  blas_threads_per_job=1, cases_sha256=campaign.sha256_file(campaign.CASE_FILE),
                  planned_jobs=len(work), additional_base_seeds=97, results=[])
    def save():
        temp = archive/'report.tmp'
        temp.write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
        temp.replace(archive/'report.json')
    save()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = [pool.submit(execute, job, args.run_tag, archive) for job in work]
        for number, future in enumerate(as_completed(pending), 1):
            result = future.result()
            report['results'].append(result)
            save()
            non_ok = sum(v for counts in result['counts'].values()
                         for status,v in counts.items() if status != 'ok')
            print(f'[{number}/{len(work)}] seed={result["seed_index"]} '
                  f'{result["case"]} exit={result["returncode"]} '
                  f'non_ok_rows={non_ok} QA={result["qa_classification"]}', flush=True)
    totals = defaultdict(Counter)
    for result in report['results']:
        for method, counts in result['counts'].items():
            totals[method].update(counts)
    report['status_counts_by_method'] = {k:dict(v) for k,v in totals.items()}
    report['status'] = 'finished_pending_numerical_review'
    save()
    print(json.dumps(report['status_counts_by_method'], indent=2))
    # Resource skips remain distinct from numerical or infrastructure failures.
    bad = any(r['returncode'] or r['qa_issues'] or r['qa_classification']=='missing_qa'
              for r in report['results'])
    bad |= any(v for counts in totals.values() for status,v in counts.items()
               if status != 'ok' and status != 'budget_exceeded' and not status.startswith('infeasible_'))
    sys.exit(2 if bad else 0)


if __name__ == '__main__':
    main()
