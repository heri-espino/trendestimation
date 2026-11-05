"""Resume missing case/seed jobs into a NEW archive, preserving old outcomes."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
import hashlib
import os
from pathlib import Path
import subprocess
import additional_seeds as extra
import campaign


def remaining(report, design):
    raw = campaign.CASE_FILE.read_bytes()
    lf = raw.replace(b'\r\n', b'\n')
    accepted = {hashlib.sha256(value).hexdigest()
                for value in (raw, lf, lf.replace(b'\n', b'\r\n'))}
    if report.get('cases_sha256') not in accepted:
        raise ValueError('Case design differs from interrupted campaign')
    if not report.get('large_svd_opt_in'):
        raise ValueError('Expected the author-approved large-SVD campaign')
    work = extra.jobs(design)
    expected = {(i+3,c['id']):(i,seed,c,block) for i,seed,c,block in work}
    seen = set()
    for record in report['results']:
        key = (record['seed_index'],record['case'])
        if key in seen or key not in expected:
            raise ValueError('Duplicate or unknown completed job')
        job = expected[key]
        if record['seed'] != job[1] or record['block'] != job[3]:
            raise ValueError('Checkpoint seed or method-order block mismatch')
        seen.add(key)
    return [job for key,job in expected.items() if key not in seen]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous-report', type=Path, required=True)
    parser.add_argument('--run-tag', required=True)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if Path.cwd().resolve() != campaign.ROOT:
        raise ValueError('Run from repository root')
    if not campaign.VALID_TAGS.fullmatch(args.run_tag) or len(args.run_tag)>43:
        raise ValueError('Use a safe new tag at most 43 characters long')
    previous = json.loads(args.previous_report.read_text(encoding='utf8'))
    # New controller files may change; numerical/case source must match.
    subprocess.run(['git','diff','--exit-code',previous['source_commit'],'--',
                    'src/trendestimation','paper/benchmarks/experiment006',
                    'paper/benchmarks/experiment011/cases.json',
                    'paper/benchmarks/experiment011/campaign.py'], check=True)
    work = remaining(previous,campaign.load_design())
    print(f'Preserved {len(previous["results"])} jobs; remaining {len(work)}; workers=1',flush=True)
    if args.dry_run:
        return
    archive = campaign.HERE/'campaigns'/args.run_tag
    archive.mkdir(parents=True,exist_ok=False)
    for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS',
                'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
        os.environ[key] = '1'
    report = dict(previous_report=str(args.previous_report),
                  previous_report_sha256=campaign.sha256_file(args.previous_report),
                  preserved_jobs=len(previous['results']),planned_jobs=previous['planned_jobs'],
                  continuation_planned_jobs=len(work),
                  source_commit=campaign.git_sha(), workers=1,
                  mode='serial_continuation_of_concurrent_campaign',
                  large_svd_opt_in=True, cases_sha256=previous['cases_sha256'],
                  results=list(previous['results']), status='in_progress')
    def save():
        temp=archive/'report.tmp'
        temp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
        temp.replace(archive/'report.json')
    def publish(number):
        if not args.publish:
            return
        # Only this new continuation's output paths; no unrelated files.
        paths=[str(archive.relative_to(campaign.ROOT))]
        paths += [str(p.relative_to(campaign.ROOT))
                  for p in campaign.RUNS.glob(args.run_tag+'_s*')]
        subprocess.run(['git','add','-f','--',*paths],check=True)
        subprocess.run(['git','commit','-m',f'experiment011: continuation checkpoint {number}/{len(work)}'],check=True)
        subprocess.run(['git','push','-u','origin','HEAD'],check=True)
    save()
    for number,job in enumerate(work,1):
        result=extra.execute(job,args.run_tag,archive,large_svd=True)
        result['phase_workers']=1
        report['results'].append(result)
        save()
        print(f'[{number}/{len(work)}] seed={result["seed_index"]} {result["case"]} '
              f'exit={result["returncode"]} statuses={result["counts"]}',flush=True)
        publish(number)
    totals=defaultdict(Counter)
    for result in report['results']:
        for method,counts in result['counts'].items():
            totals[method].update(counts)
    report['status_counts_by_method']={k:dict(v) for k,v in totals.items()}
    report['status']='finished_pending_numerical_review'
    save()
    publish(len(work))
    print('Finished continuation; inspect numerical statuses separately from process completion.')


if __name__ == '__main__':
    main()
