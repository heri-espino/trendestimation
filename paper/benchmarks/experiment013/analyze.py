"""Audit Experiment013 execution and calculate *paired* real-time contrasts.

This module never executes the numerical experiment, never fabricates
infeasible timing rows, and never pools 100 correlated seed observations
as if 100,000 independent criterion evaluations.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import median

from run import CRITERIA, METHODS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_data(output: Path):
    config=json.loads((output/"metadata.json").read_text(encoding="utf8"))
    with (output/"timings.csv").open(newline="",encoding="utf8") as stream:
        rows=list(csv.DictReader(stream))
    expected=(len(config["n"])*len(config["d"])*len(config["criteria"])*
              config["seeds"]*len(METHODS)*len(config["checkpoints"]))
    if len(rows)!=expected:
        raise ValueError(f"Expected {expected} raw rows, found {len(rows)}")
    keys=set()
    for row in rows:
        key=(int(row["n"]),int(row["d"]),row["criterion"],row["method"],
             int(row["seed_index"]),int(row["M"]))
        if key in keys:
            raise ValueError("Duplicate method–seed–checkpoint observation")
        keys.add(key)
        if row["source_commit"]!=config["source_commit"]:
            raise ValueError("Source SHA mismatch")
        if row["status"]=="ok":
            if int(row["completed"]) != int(row["M"]):
                raise ValueError("False full-coverage claim")
            if any(not row[name] for name in (
                "method_setup_s","first_evaluation_s",
                "cumulative_evaluation_s","total_cold_s",
                "selected_lambda","selected_score")):
                raise ValueError("Missing successful criterion evidence")
            setup=float(row["method_setup_s"])
            evaluation=float(row["cumulative_evaluation_s"])
            cold=float(row["total_cold_s"])
            if (not math.isfinite(cold) or cold<=0 or
                abs(setup+evaluation-cold)>1e-6*max(1,cold)):
                raise ValueError("Inconsistent complete cold-time accounting")
    if (output/"completion.json").exists():
        completion=json.loads((output/"completion.json").read_text(encoding="utf8"))
        if completion["timings_sha256"]!=digest(output/"timings.csv"):
            raise ValueError("Frozen timing SHA-256 mismatch")
    return config,rows


def paired_contrasts(rows, *, bootstraps=400, seed=13013):
    import numpy as np
    baseline_pairs=(
        ("naive_inverse","banded_cholesky"),
        ("naive_inverse","spectral_svd"),
        ("banded_cholesky","spectral_svd"),
    )
    indices=defaultdict(dict)
    for r in rows:
        k=(int(r["n"]),int(r["d"]),r["criterion"],int(r["M"]),
           int(r["seed_index"]))
        indices[k][r["method"]]=r
    paired=defaultdict(list)
    mismatch=[]
    for (n,d,criterion,m,seed_idx),available in indices.items():
        for baseline,method in baseline_pairs:
            a,b=available[baseline],available[method]
            if a["status"]!="ok" or b["status"]!="ok":
                continue
            la,lb=float(a["selected_lambda"]),float(b["selected_lambda"])
            sa,sb=float(a["selected_score"]),float(b["selected_score"])
            parity_lambda=abs(la-lb)<=1e-9*max(1.,abs(la),abs(lb))
            parity_score=(criterion=="mle" or
                          abs(sa-sb)<=1e-6*max(1.,abs(sa),abs(sb)))
            if not parity_lambda or not parity_score:
                mismatch.append(dict(n=n,d=d,criterion=criterion,M=m,seed=seed_idx,
                                     baseline=baseline,method=method,
                                     lambda_a=la,lambda_b=lb,score_a=sa,score_b=sb))
                continue
            ratio=float(a["total_cold_s"])/float(b["total_cold_s"])
            if ratio>0 and math.isfinite(ratio):
                paired[(n,d,criterion,m,baseline,method)].append((seed_idx,math.log(ratio)))
    rng=np.random.default_rng(seed)
    output=[]
    for (n,d,c,m,baseline,method),items in sorted(paired.items()):
        seeds=set(idx for idx,_ in items)
        if len(seeds)!=len(items):
            raise ValueError("Duplicate seed in matched contrast")
        log_ratios=np.array([x for _,x in items])
        nseeds=len(log_ratios)
        observed=math.exp(float(np.mean(log_ratios)))
        low=high=""
        if nseeds>=5:
            chosen=rng.integers(0,nseeds,size=(bootstraps,nseeds))
            boots=np.exp(np.mean(log_ratios[chosen],axis=1))
            low=float(np.quantile(boots,.025))
            high=float(np.quantile(boots,.975))
        output.append(dict(n=n,d=d,criterion=c,M=m,baseline=baseline,
                           method=method,paired_seeds=nseeds,
                           geometric_speedup=observed,ci_low=low,ci_high=high))
    return output,mismatch


def save_rows(path,rows,fields):
    with path.open("w",newline="",encoding="utf8") as handle:
        wr=csv.DictWriter(handle,fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)


def analyze(output: Path, *, bootstrap=400):
    config,rows=parse_data(output)
    counts=Counter((int(r["n"]),int(r["d"]),r["criterion"],
                    r["method"],int(r["M"]),r["status"]) for r in rows)
    statuses=[dict(n=n,d=d,criterion=c,method=method,M=m,status=status,
                   seed_rows=v)
              for (n,d,c,method,m,status),v in sorted(counts.items())]
    pairs,mismatches=paired_contrasts(rows,bootstraps=bootstrap)
    save_rows(output/"status_counts.csv",statuses,
              ("n","d","criterion","method","M","status","seed_rows"))
    save_rows(output/"paired_speedups.csv",pairs,
              ("n","d","criterion","M","baseline","method","paired_seeds",
               "geometric_speedup","ci_low","ci_high"))
    save_rows(output/"numerical_disagreements.csv",mismatches,
              ("n","d","criterion","M","seed","baseline","method",
               "lambda_a","lambda_b","score_a","score_b"))
    summary={
        "experiment":"experiment013","source_commit":config["source_commit"],
        "seed_count_scheduled_per_case":config["seeds"],
        "raw_rows":len(rows),
        "status_counts":dict(Counter(r["status"] for r in rows)),
        "paired_contrasts":len(pairs),
        "selected_parameter_disagreements":len(mismatches),
        "source_timings_sha256":digest(output/"timings.csv"),
        "bootstrap":{"resamples":bootstrap,"unit":"independent seed",
                     "seed":13013},
        "interpretation":"Only full, status-ok and numerically paired method times enter speedups. "
                         "Noncompletion and resource masks retain their denominators.",
    }
    (output/"analysis_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf8")
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--bootstraps",type=int,default=400)
    args=parser.parse_args()
    if args.bootstraps<1 or args.bootstraps>10000:
        parser.error("Bootstrap count outside 1..10000")
    print(json.dumps(analyze(args.input,bootstrap=args.bootstraps),indent=2))


if __name__=="__main__":
    main()
