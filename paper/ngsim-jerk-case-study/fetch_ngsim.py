"""Download and audit a small, *real* FHWA NGSIM vehicle-position subset.

Uses the authoritative USDOT Socrata source. No generated trajectories,
no smoothing before analysis, no data-dependent ranking by performance.
Source: https://data.transportation.gov/d/8ect-6jqj
DOI: 10.21949/1504477
License shown on dataset portal: CC BY-SA 3.0. Attribution preserved.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"data"
OUT.mkdir(parents=True,exist_ok=True)
BASE="https://data.transportation.gov/resource/8ect-6jqj.csv"
FIELDS="vehicle_id,frame_id,global_time,local_y,local_x,location"
QUERY={
    "$select":FIELDS,
    "$where":"location = 'us-101' AND vehicle_id >= 1 AND vehicle_id <= 120",
    "$order":"vehicle_id ASC, global_time ASC",
    "$limit":"70000",
}
URL=BASE+"?"+urllib.parse.urlencode(QUERY)
DT=0.1
MIN_LEN=200
N_TRACKS=5

def segments(rows):
    if not rows:return
    rows.sort(key=lambda x:x[1])
    series=[rows[0]]
    for row in rows[1:]:
        dt=(row[1]-series[-1][1])/1000.0
        if 0.095<=dt<=0.105:
            series.append(row)
        else:
            if len(series)>=MIN_LEN:yield series
            series=[row]
    if len(series)>=MIN_LEN:yield series

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"TrendEstimation-Research/1.0 (public cited dataset)","Accept":"text/csv"})
    with urllib.request.urlopen(req,timeout=120) as r:
        raw=r.read()
    if not raw or b"local_y" not in raw[:400]:
        raise RuntimeError("FHWA response lacks expected CSV fields")
    data=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(data)>=int(QUERY["$limit"]):
        raise RuntimeError("Source query hit row limit; result could be truncated; enlarge limit/paginate")
    groups=defaultdict(list)
    for row in data:
        try:
            vid=int(float(row["vehicle_id"]))
            t=int(float(row["global_time"]))
            y=float(row["local_y"])*0.3048
            x=float(row["local_x"])*0.3048
            frame=int(float(row["frame_id"]))
            if np.isfinite(y) and np.isfinite(x) and row["location"].lower()=="us-101":
                groups[vid].append((frame,t,y,x))
        except (ValueError,KeyError):continue
    eligible=[]
    for vid in sorted(groups):
        for seq in segments(groups[vid]):
            y=np.asarray([r[2] for r in seq])
            if y[-1]-y[0]<20:continue
            v=np.diff(y)/DT
            if np.mean(v>=-1)>0.87 and np.quantile(abs(v),.99)<65:
                eligible.append((vid,seq))
    if len(eligible)<N_TRACKS:
        raise RuntimeError(f"Only {len(eligible)} qualified real long tracks; no synthetic fallback.")
    chosen=eligible[:N_TRACKS]
    out=OUT/"ngsim_us101_selected_raw_positions.csv"
    with out.open("w",newline="",encoding="utf8") as f:
        wr=csv.writer(f)
        wr.writerow(["track_number","vehicle_id","frame_id","global_time_ms","t_s","longitudinal_m","lateral_m"])
        for no,(vid,seq) in enumerate(chosen,1):
            for i,(frame,t,y,x) in enumerate(seq):
                wr.writerow([no,vid,frame,t,f"{i*DT:.1f}",f"{y:.6f}",f"{x:.6f}"])
    manifest={
        "official_url":"https://data.transportation.gov/d/8ect-6jqj",
        "official_doi":"10.21949/1504477",
        "query_url":URL,
        "rows_from_query":len(data),
        "source_csv_sha256":hashlib.sha256(raw).hexdigest(),
        "selection_rule":"ascending vehicle_id, then start time; first five with >=200 contiguous 100-ms frames, >=20m positive displacement, >=87% differences >=-1m/s and 99th percentile absolute step speed <65m/s; never scored by forecast",
        "selected":[{"track_number":i+1,"vehicle_id":vid,"start_ms":seq[0][1],"frames":len(seq),"distance_m":round(seq[-1][2]-seq[0][2],3)}
                    for i,(vid,seq) in enumerate(chosen)],
        "subset_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "units":"raw FHWA Local_Y (feet) -> meters by exact 0.3048; t=0.1s; no artificial noise",
        "license":"CC BY-SA 3.0 per dataset metadata; attribute FHWA USDOT",
        "does_not_assert":"Source position is ground-truth jerk, or a safety-certified motion forecast",
    }
    (OUT/"provenance.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2),flush=True)

if __name__=="__main__":
    fetch()
