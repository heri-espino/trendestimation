# Experiment006 — aggregate measured computational complexity by matched factor

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

KEYS=('method','coordinate','workload','mu','amplitude','criterion','grid_denominator','d','R','M')

def load(root):
    rows=[]
    for path in sorted(Path(root).rglob('raw_times.csv')):
        with path.open(encoding='utf-8',newline='') as stream:
            for record in csv.DictReader(stream):
                record['source_dir']=str(path.parent)
                rows.append(record)
    return rows

def aggregate(root,output):
    records=load(root)
    if not records:
        raise ValueError('No measured raw_times.csv under the requested root')
    groups=defaultdict(list)
    for row in records:
        key=(row['source_dir'],)+tuple(row[k] for k in KEYS)+ (row['n'],)
        groups[key].append(row)
    summaries=[]
    for key,group in groups.items():
        good=[r for r in group if r['status']=='ok']
        complete=len(good)==len(group) and len(good)>=1
        time=np.array([float(r['total_cold_s']) for r in good])
        rng=np.random.default_rng(6006)
        boot=(np.mean(time[rng.integers(0,len(time),(2000,len(time)))],axis=1)
              if len(time)>=2 and complete else None)
        summaries.append(dict(
            source_dir=key[0],
            **dict(zip(KEYS,key[1:1+len(KEYS)])),
            n=key[-1],repeats=len(group),valid_repeats=len(good),
            complete=complete,
            mean_s=float(time.mean()) if complete else float('nan'),
            median_s=float(np.median(time)) if complete else float('nan'),
            sd_s=float(np.std(time,ddof=1)) if complete and len(time)>1 else float('nan'),
            ci95_low_s=float(np.quantile(boot,.025)) if boot is not None else float('nan'),
            ci95_high_s=float(np.quantile(boot,.975)) if boot is not None else float('nan'),
        ))
    output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f'Refusing to overwrite prior analysis: {output}')
    output.mkdir(parents=True,exist_ok=True)
    with (output/'timing_aggregates.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(summaries[0]))
        writer.writeheader(); writer.writerows(summaries)
    # A power-law slope is meaningful only within a fixed workload,
    # grid, difference order, mu, scale, criterion, coordinate and method.
    slopes=defaultdict(list)
    for record in summaries:
        if not record['complete'] or record['mean_s']<=0:continue
        key=tuple(record[k] for k in KEYS)
        slopes[key].append(record)
    estimates=[]
    for key,group in slopes.items():
        ns={int(r['n']) for r in group}
        if len(ns)<3:continue
        # Multiple runs for same n are combined by their measured mean
        # before fitting log(T) = intercept + slope*log(n).
        by_n=defaultdict(list)
        for r in group:by_n[int(r['n'])].append(r['mean_s'])
        xx=np.array(sorted(by_n),float)
        yy=np.array([np.mean(by_n[int(n)]) for n in xx],float)
        slope,intercept=np.polyfit(np.log(xx),np.log(yy),1)
        prediction=intercept+slope*np.log(xx)
        sst=float(np.sum((np.log(yy)-np.mean(np.log(yy)))**2))
        r2=(1-float(np.sum((np.log(yy)-prediction)**2))/sst
            if sst>0 else float('nan'))
        estimates.append(dict(
            **dict(zip(KEYS,key)),n_values=';'.join(map(str,map(int,xx))),
            exponent=float(slope),log_intercept=float(intercept),r2_log=float(r2),
            n_distinct=len(xx),
            note='Empirical composite exponent; not an algorithmic proof or causal estimate',
        ))
    with (output/'empirical_complexity_exponents.csv').open('w',encoding='utf-8',newline='') as stream:
        fieldnames=(list(estimates[0]) if estimates else
                    list(KEYS)+['n_values','exponent','log_intercept','r2_log','n_distinct','note'])
        writer=csv.DictWriter(stream,fieldnames=fieldnames)
        writer.writeheader();writer.writerows(estimates)
    print(f'Aggregated {len(records)} raw timing rows, {len(summaries)} cells, {len(estimates)} empirical exponents.')
    return summaries,estimates

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    aggregate(a.runs,a.output)
