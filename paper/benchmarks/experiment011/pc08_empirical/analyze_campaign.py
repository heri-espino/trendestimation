"""Reconcile the FINAL cumulative Experiment011 report and derive Springer evidence.

Never invokes a benchmark. No writes occur under --original or --backup.
Output is a SPARSE record tensor; failures, missingness and worker phases
remain explicit. Timings are conditional on numerical/coverage admissibility.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys

BASE = Path("paper/benchmarks/experiment011")
FINAL = BASE / "campaigns/PC08_resume12_20261108_200034/report.json"
INPUTS = ("experiment011_case.json", "experiment011_qa.json",
          "measurements/environment.json", "measurements/raw_times.csv")
TIMES = ("method_setup_s","s_to_lambda_s","candidate_evaluation_s",
         "total_cold_s","total_warm_s")
POLICIES = ("direct_s","mapped_lambda")
WORKLOADS = ("one_s_one_series","grid_one_series",
             "one_s_multiple_series","grid_multiple_series")
SCHEMA = ("seed_index","case_id","block","run_tag","phase_workers",
          "host","source_commit","source_file_sha256","environment_fingerprint",
          "n","d","mu","amplitude","criterion","grid_denominator",
          "method","coordinate","workload","repeat","R","M",
          "status","evaluations","selected_s","selected_score",*TIMES,
          "qa_classification","record_returncode","valid_full_search",
          "validity_reason","raw_sha256","comment")


def jload(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path, data, cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    op=gzip.open if path.suffix==".gz" else open
    with op(path,"wt",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def within(path, root):
    return path.resolve().is_relative_to(root.resolve())


def historical_chain(root):
    current=(root/FINAL).resolve()
    seen=set(); chain=[]
    while True:
        if current in seen:
            raise ValueError("Cyclic previous_report chain")
        seen.add(current)
        if not within(current,root):
            raise ValueError("Untrusted report escapes original checkout")
        obj=jload(current)
        chain.append((current,obj))
        prior=obj.get("previous_report")
        if not prior: break
        old=Path(prior)
        possibilities=([old] if old.is_absolute() else
                       [root/old,current.parent/old,root/BASE/"campaigns"/old])
        matches=[p.resolve() for p in possibilities if p.is_file()]
        if not matches:
            raise FileNotFoundError(f"Missing checkpoint lineage predecessor of {current}: {prior}")
        old=matches[0]
        if obj.get("previous_report_sha256") and sha(old).lower()!=obj["previous_report_sha256"].lower():
            raise ValueError("Previous checkpoint SHA-256 mismatch")
        current=old
    chain.reverse()
    result={}
    chain_meta=[]
    prev=[]
    for path,object_ in chain:
        records=object_.get("results",[])
        if len(records)<len(prev):
            raise ValueError("Decreasing checkpoint cumulative result length")
        if records[:len(prev)]!=prev:
            raise ValueError("Checkpoint changed inherited results; cannot resolve attempt lineage")
        stage=path.parent.name
        for item in records[len(prev):]:
            k=(item["seed_index"],item["case"])
            if k in result:raise ValueError("Duplicate finalized case-seed key")
            result[k]={"tag":stage,"record":item,"report":str(path.relative_to(root)).replace("\\","/")}
        chain_meta.append({"tag":stage,"report_sha256":sha(path),
                           "inherited":len(prev),"appended":len(records)-len(prev),
                           "cumulative":len(records)})
        prev=records
    if len(result)!=2813 or len(prev)!=2813:
        raise ValueError("Lineage has not preserved exactly 2813 unique jobs")
    return result,chain_meta,chain[-1][1]


def fp(env):
    fields=("host","python","numpy","scipy","blas_threads","threadpools","code_sha256")
    return hashlib.sha256(json.dumps({k:env.get(k) for k in fields},
                                      sort_keys=True).encode()).hexdigest()[:18]


def num(value):
    try:return float(value)
    except (TypeError,ValueError):return math.nan


def record_valid(row,qa,manifest,env,record):
    if record.get("returncode")!=0:return "process_nonzero_exit"
    if qa.get("issues"):return "qa_numerical_issues"
    if row.get("status")!="ok":return "status_"+str(row.get("status"))
    if row.get("coordinate") not in POLICIES or row.get("workload") not in WORKLOADS:
        return "invalid_axis"
    if row.get("method") not in manifest["method_order"]:return "unexpected_method"
    if int(row["M"])*int(row["R"])!=int(row["evaluations"]):return "incomplete_candidate_coverage"
    for field in TIMES:
        val=num(row.get(field))
        if not math.isfinite(val) or val<0:return "nonfinite_or_negative_"+field
    if num(row.get("total_cold_s"))<=0:return "zero_cold_time"
    s=num(row.get("selected_s"))
    if not math.isfinite(s) or not 0<=s<=1:return "invalid_selected_s"
    if not math.isfinite(num(row.get("selected_score"))):return "invalid_selected_score"
    if env["blas_threads"]!=1:return "blas_not_one_thread"
    if env.get("code_sha256")!=manifest.get("source_file_sha256"):
        return "source_hash_mismatch"
    if env.get("git_sha")!=manifest.get("source_commit"):
        return "source_commit_mismatch"
    return "complete_float64_status_only"


def safe_input(root, backup, path, inventory, problems, check_backup=False):
    rel=path.relative_to(root).as_posix()
    if not path.is_file():
        problems.append({"path":rel,"issue":"missing_input"})
        return False
    digest=sha(path)
    known=inventory.get(rel.casefold())
    if known and digest.lower()!=known.lower():
        problems.append({"path":rel,"issue":"inventory_original_hash_mismatch"})
        return False
    if not known:
        problems.append({"path":rel,"issue":"not_in_verified_inventory"})
    if check_backup:
        copy=backup/path.relative_to(root)
        if not copy.is_file() or sha(copy)!=digest:
            problems.append({"path":rel,"issue":"backup_mismatch"})
            return False
    return True


def ingress(root, backup):
    inventory_path=backup/"metadata/files_sha256.csv"
    inventory={}
    with inventory_path.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            inventory[r["path"].replace("\\","/").casefold()]=r["sha256"]
    accepted,chain,final=historical_chain(root)
    design=jload(root/BASE/"cases.json")
    design_keys={(idx,c["id"]) for idx in range(3,100) for c in design["cases"]}
    if set(accepted)!=design_keys:
        raise ValueError("Final report differs from 29x97 declared cases")
    if sha(root/BASE/"cases.json").lower()!=final["cases_sha256"].lower():
        raise ValueError("Design differs from final report")
    tensor=[]; files=[]; problems=[]; statuses=Counter(); qa_classes=Counter()
    paths_seen=set()
    for (idx,case_id),entry in sorted(accepted.items()):
        tag,record=entry["tag"],entry["record"]
        b=record["block"]
        path=root/BASE/"runs"/f"{tag}_s{idx:03d}"/case_id/f"block{b:03d}"
        if not within(path,root):raise ValueError("Unsafe accepted block")
        file_meta={"seed_index":idx,"case_id":case_id,"block":b,
                   "phase_workers":record.get("phase_workers"),
                   "run_tag":tag,"source_report":entry["report"],
                   "returncode":record.get("returncode"),
                   "qa_classification_in_report":record.get("qa_classification"),
                   "block_path":str(path.relative_to(root)).replace("\\","/")}
        valid_input=True
        for file_name in INPUTS:
            f=path/file_name
            ok=safe_input(root,backup,f,inventory,problems,check_backup=True)
            valid_input &= ok
            file_meta[file_name+"_sha256"]=sha(f) if f.is_file() else ""
        files.append(file_meta)
        if not valid_input:
            statuses["missing_or_changed_input"]+=1
            tensor.append({"seed_index":idx,"case_id":case_id,"block":b,"run_tag":tag,
                           "phase_workers":record.get("phase_workers"),"status":"missing_or_changed_input",
                           "valid_full_search":False,"validity_reason":"missing_or_changed_input",
                           "record_returncode":record.get("returncode")})
            continue
        try:
            manifest=jload(path/INPUTS[0]);qa=jload(path/INPUTS[1]);env=jload(path/INPUTS[2])
            with (path/INPUTS[3]).open(newline="",encoding="utf-8-sig") as stream:
                raw=list(csv.DictReader(stream))
            if (manifest.get("case",{}).get("id")!=case_id or manifest.get("block")!=b
                    or manifest.get("seed")!=record["seed"]):
                raise ValueError("Case/block/seed manifest mismatch")
            if qa.get("case_id")!=case_id or qa.get("block")!=b or qa.get("raw_rows")!=len(raw):
                raise ValueError("QA/case/raw-count mismatch")
            if manifest.get("raw_sha256")!=sha(path/INPUTS[3]):
                raise ValueError("Case manifest raw SHA-256 mismatch")
            if env.get("git_sha")!=manifest.get("source_commit"):
                raise ValueError("Execution revision mismatch")
            if env.get("code_sha256")!=manifest.get("source_file_sha256"):
                raise ValueError("Numerical executable SHA-256 mismatch")
            if manifest.get("case_design_sha256")!=final["cases_sha256"]:
                raise ValueError("Experiment design SHA-256 mismatch")
            qa_classes[qa.get("classification","unknown")]+=1
            if qa.get("classification")!=record.get("qa_classification"):
                problems.append({"path":file_meta["block_path"],"issue":"report_qa_classification_mismatch"})
            expected={(m,coord,w,rep) for m in manifest["method_order"]
                      for coord in POLICIES for w in WORKLOADS
                      for rep in range(manifest["case"]["repeats_per_block"])}
            present=set()
            for rawrow in raw:
                key=(rawrow["method"],rawrow["coordinate"],rawrow["workload"],int(rawrow["repeat"]))
                if key in present:raise ValueError("Duplicate measured method/coordinate/workload/repeat")
                present.add(key)
                reason=record_valid(rawrow,qa,manifest,env,record)
                row=dict(rawrow)
                row.update({"seed_index":idx,"case_id":case_id,"block":b,"run_tag":tag,
                            "phase_workers":record.get("phase_workers"),"host":env.get("host"),
                            "source_commit":manifest["source_commit"],
                            "source_file_sha256":manifest["source_file_sha256"],
                            "environment_fingerprint":fp(env),
                            "qa_classification":qa.get("classification"),
                            "record_returncode":record.get("returncode"),
                            "valid_full_search":reason=="complete_float64_status_only",
                            "validity_reason":reason,
                            "raw_sha256":file_meta["measurements/raw_times.csv_sha256"]})
                tensor.append(row)
                statuses[reason]+=1
            # Missing repeated cells are explicit, but normal resource-skipped cells use repeat=-1.
            if any(int(r["repeat"])==-1 for r in raw):
                for r in raw:
                    if int(r["repeat"])==-1:
                        for rep in range(manifest["case"]["repeats_per_block"]):
                            expected.discard((r["method"],r["coordinate"],r["workload"],rep))
            for method,coord,w,rep in sorted(expected-present):
                tensor.append({"seed_index":idx,"case_id":case_id,"block":b,"run_tag":tag,
                               "phase_workers":record.get("phase_workers"),"host":env.get("host"),
                               "source_commit":manifest.get("source_commit"),
                               "source_file_sha256":manifest.get("source_file_sha256"),
                               "environment_fingerprint":fp(env),
                               "n":manifest["case"]["n"],"d":manifest["case"]["d"],
                               "mu":manifest["case"]["mu"],"amplitude":manifest["case"]["amplitude"],
                               "criterion":manifest["case"]["criterion"],
                               "grid_denominator":manifest["case"]["grid_denominator"],
                               "method":method,"coordinate":coord,"workload":w,"repeat":rep,
                               "R":1 if w.endswith("one_series") else manifest["case"]["series_count"],
                               "M":1 if w.startswith("one_s") else manifest["case"]["grid_denominator"],
                               "status":"missing_repeat_row","valid_full_search":False,
                               "validity_reason":"missing_repeat_row",
                               "record_returncode":record.get("returncode"),
                               "qa_classification":qa.get("classification")})
                statuses["missing_repeat_row"]+=1
        except Exception as exc:
            problems.append({"path":file_meta["block_path"],"issue":"parse_or_integrity_failure",
                             "error":str(exc)[:300]})
            statuses["parse_or_integrity_failure"]+=1
            tensor.append({"seed_index":idx,"case_id":case_id,"block":b,"run_tag":tag,
                           "phase_workers":record.get("phase_workers"),"status":"parse_or_integrity_failure",
                           "valid_full_search":False,"validity_reason":"parse_or_integrity_failure",
                           "record_returncode":record.get("returncode")})
    return tensor,files,problems,chain,final,statuses,qa_classes


def fvalid(x):
    return x.get("valid_full_search") in (True,"True","true")


def pair_rows(rows):
    grouped=defaultdict(dict)
    for r in rows:
        if not fvalid(r):continue
        key=(r["seed_index"],r["case_id"],r["repeat"],r["coordinate"],r["workload"],
             r["phase_workers"],r["environment_fingerprint"],r["source_file_sha256"])
        grouped[key][r["method"]]=r
    pairs=[]
    for key,by_method in grouped.items():
        for baseline in ("banded_cholesky","naive_inverse"):
            base=by_method.get(baseline)
            if not base:continue
            for method,r in by_method.items():
                if method==baseline:continue
                a,b=num(base.get("total_cold_s")),num(r.get("total_cold_s"))
                if min(a,b)<=0:continue
                s_diff=abs(num(base["selected_s"])-num(r["selected_s"]))
                score_rel=(abs(num(base["selected_score"])-num(r["selected_score"]))/
                           max(1.,abs(num(base["selected_score"])))
                           if r["criterion"]!="mle" else 0.)
                is_pair=s_diff<=1e-10 and score_rel<=1e-7
                pairs.append({"seed_index":r["seed_index"],"case_id":r["case_id"],
                              "n":r["n"],"d":r["d"],"criterion":r["criterion"],
                              "mu":r["mu"],"amplitude":r["amplitude"],"M":r["M"],"R":r["R"],
                              "method":method,"baseline":baseline,"coordinate":r["coordinate"],
                              "workload":r["workload"],"repeat":r["repeat"],
                              "phase_workers":r["phase_workers"],
                              "float64_pair":is_pair,
                              "selected_s_diff":s_diff,
                              "score_rel_diff":score_rel if r["criterion"]!="mle" else "",
                              "ratio_baseline_over_method":a/b if is_pair else "",
                              "baseline_cold_s":a,"method_cold_s":b,
                              "pair_status":"matched_float64_only" if is_pair else "score_or_s_disagreement"})
    return pairs


def coord_pairs(rows):
    groups=defaultdict(dict)
    for r in rows:
        if not fvalid(r):continue
        key=(r["seed_index"],r["case_id"],r["repeat"],r["workload"],r["method"],
             r["phase_workers"],r["environment_fingerprint"],r["source_file_sha256"])
        groups[key][r["coordinate"]]=r
    pairs=[]
    for k,v in groups.items():
        if not all(p in v for p in POLICIES):continue
        a,b=v["direct_s"],v["mapped_lambda"]
        if (abs(num(a["selected_s"])-num(b["selected_s"]))>1e-10 or
            (a["criterion"]!="mle" and
            abs(num(a["selected_score"])-num(b["selected_score"]))>
            1e-7*max(1.,abs(num(a["selected_score"]))))):continue
        pairs.append({"seed_index":a["seed_index"],"case_id":a["case_id"],
                      "criterion":a["criterion"],"n":a["n"],"d":a["d"],"M":a["M"],
                      "method":a["method"],"workload":a["workload"],
                      "phase_workers":a["phase_workers"],"repeat":a["repeat"],
                      "mapped_over_direct_s":num(b["total_cold_s"])/num(a["total_cold_s"]),
                      "direct_s_cold_s":a["total_cold_s"],
                      "mapped_lambda_cold_s":b["total_cold_s"]})
    return pairs


def quantile(values,q):
    if not values:return None
    v=sorted(values)
    k=(len(v)-1)*q
    i=int(k)
    return v[i]*(1-(k-i))+v[min(i+1,len(v)-1)]*(k-i)


def logratio_ci(values, boot=700):
    # Repeated within-seed workload and method rows are reduced to one
    # cluster statistic BEFORE resampling independent seed trajectories.
    if not values:return ("","","")
    g=statistics.mean(values)
    if len(values)<3:return (math.exp(g),"","")
    rng=random.Random(20261109)
    scores=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(boot))
    return math.exp(g),math.exp(quantile(scores,.025)),math.exp(quantile(scores,.975))


def summarize_pair(pairs,ratio_key):
    g=defaultdict(lambda:defaultdict(list))
    for row in pairs:
        v=num(row.get(ratio_key))
        if not math.isfinite(v) or v<=0:continue
        if ratio_key=="ratio_baseline_over_method":
            key=(row["case_id"],row["n"],row["d"],row["criterion"],row["method"],row["baseline"],
                 row["coordinate"],row["workload"],row["M"],row["R"],row["phase_workers"])
        else:
            key=(row["case_id"],row["n"],row["d"],row["criterion"],row["method"],
                 row["workload"],row["M"],row["phase_workers"])
        g[key][row["seed_index"]].append(math.log(v))
    out=[]
    for key,seeds in sorted(g.items()):
        per_seed=[statistics.mean(v) for _,v in sorted(seeds.items())]
        geo,low,high=logratio_ci(per_seed)
        labels=(("case_id","n","d","criterion","method","baseline","coordinate",
                 "workload","M","R","phase_workers") if ratio_key=="ratio_baseline_over_method"
                else ("case_id","n","d","criterion","method","workload","M","phase_workers"))
        out.append({**dict(zip(labels,key)),"independent_seeds":len(per_seed),
                    "replicate_rows":sum(map(len,seeds.values())),
                    "geometric_ratio":geo,"bootstrap95_low":low,"bootstrap95_high":high,
                    "uncertainty_unit":"independent_seed_index_with_repeats_retained",
                    "precision":"float64_parity_only"})
    return out


def timing_summary(tensor):
    groups=defaultdict(list)
    for r in tensor:
        if not r.get("case_id") or not r.get("method"):continue
        k=(r.get("case_id"),r.get("n"),r.get("d"),r.get("criterion"),r.get("method"),
           r.get("coordinate"),r.get("workload"),r.get("M"),r.get("R"),r.get("phase_workers"))
        groups[k].append(r)
    out=[]
    names=("case_id","n","d","criterion","method","coordinate","workload","M","R","phase_workers")
    for key,group in sorted(groups.items(),key=lambda x:str(x[0])):
        good=[r for r in group if fvalid(r)]
        seeds={r["seed_index"] for r in good}
        entry=dict(zip(names,key))
        entry.update({"observed_and_missing_rows":len(group),
                      "valid_rows":len(good),"valid_seed_clusters":len(seeds),
                      "invalid_or_missing_rows":len(group)-len(good),
                      "valid_fraction":len(good)/len(group)})
        for field in TIMES:
            a=[num(x.get(field)) for x in good if math.isfinite(num(x.get(field)))]
            entry["median_"+field]=statistics.median(a) if a else ""
            entry["p10_"+field]=quantile(a,.1) if a else ""
            entry["p90_"+field]=quantile(a,.9) if a else ""
        out.append(entry)
    return out


def reliability(tensor):
    groups=defaultdict(list)
    for r in tensor:
        if not r.get("criterion") or not r.get("method"):continue
        k=(r["criterion"],r["method"],r["phase_workers"])
        groups[k].append(r)
    out=[]
    for (criterion,method,phase),rows in sorted(groups.items(),key=lambda x:str(x[0])):
        valid=[r for r in rows if fvalid(r)]
        counts=Counter(r.get("validity_reason","unclassified") for r in rows)
        out.append({"criterion":criterion,"method":method,"phase_workers":phase,
                    "total_attempted_or_masked_rows":len(rows),
                    "valid_complete_rows":len(valid),
                    "valid_rate":len(valid)/len(rows),
                    "independent_case_seed_clusters":len({(r["case_id"],r["seed_index"]) for r in rows}),
                    "excluded_reasons":json.dumps({k:v for k,v in counts.items()
                                                   if k!="complete_float64_status_only"},sort_keys=True)})
    return out


def figure_outputs(output,timing,pairs,coord,reliable):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({"font.family":"sans-serif","font.size":8,
                         "axes.spines.top":False,"axes.spines.right":False,
                         "pdf.fonttype":42,"figure.dpi":150})
    figs=output/"figures";figs.mkdir(exist_ok=True)
    desc=[]
    def save(fig,name,note):
        fig.tight_layout(pad=1.25)
        fig.savefig(figs/(name+".pdf"),bbox_inches="tight")
        fig.savefig(figs/(name+".png"),bbox_inches="tight",dpi=170)
        plt.close(fig)
        desc.append({"id":name,"pdf":"figures/"+name+".pdf",
                     "png":"figures/"+name+".png","description":note})
    # reliability proportions: no 0-second imputation of failures
    c=defaultdict(lambda:[0,0])
    for r in reliable:
        c[(r["criterion"],r["method"])][0]+=r["valid_complete_rows"]
        c[(r["criterion"],r["method"])][1]+=r["total_attempted_or_masked_rows"]
    items=sorted(c,key=lambda k:(k[0],k[1]))
    fig,ax=plt.subplots(figsize=(6.6,3.4))
    names=[crit.upper()+": "+m.replace("_"," ") for crit,m in items]
    valid=[c[k][0]/c[k][1] if c[k][1] else 0 for k in items]
    ax.barh(range(len(items)),valid,color="#326b9d")
    ax.set_yticks(range(len(items)),names,fontsize=6.5)
    ax.set_xlim(0,1);ax.set_xlabel("Fraction of complete, status-admissible timing rows")
    ax.invert_yaxis()
    save(fig,"fig01_reliability","All report-selected attempts, grouped by criterion/backend; invalid and missing cells retained in denominators")
    # Matched complete-grid forest plot: each point is a predeclared case
    # (not a pooled pseudo-scaling curve across mu, d or case families).
    sel=[r for r in pairs if r.get("baseline")=="banded_cholesky" and
         r.get("method")=="spectral_svd" and r.get("workload")=="grid_one_series" and
         r.get("coordinate")=="direct_s" and int(r.get("M") or 0)==100 and
         int(r.get("phase_workers") or 0)==24 and
         r.get("criterion") in ("cv","gcv") and r.get("bootstrap95_low")!=""]
    sel=sorted(sel,key=lambda r:(r["criterion"],int(r["n"]),int(r["d"]),r["case_id"]))
    fig,ax=plt.subplots(figsize=(6.7,3.95))
    colors={"cv":"#174a7a","gcv":"#58a2b7"}
    labels=[]
    for i,r in enumerate(sel):
        tag=r["case_id"]
        label=(
            "confirm-data" if tag.startswith("confirm_data") else
            "pilot-data" if tag.startswith("pilot_data") else
            "pilot-hybrid" if tag.startswith("pilot_hybrid") else
            tag.split("_")[0]
        )
        labels.append(f'{r["criterion"].upper()}: n={r["n"]}, d={r["d"]} ({label})')
        y=float(r["geometric_ratio"])
        lo=float(r["bootstrap95_low"])
        hi=float(r["bootstrap95_high"])
        ax.errorbar(y,i,xerr=[[y-lo],[hi-y]],fmt="o",markersize=4,
                    capsize=2.5,lw=1.2,color=colors[r["criterion"]])
    ax.set_yticks(range(len(sel)),labels,fontsize=7.5)
    ax.invert_yaxis()
    ax.axvline(1,color="black",lw=.8,ls="--")
    ax.set_xlabel("Banded Cholesky / spectral SVD cold time")
    if sel:
        ax.set_xlim(left=0,right=max(1.5,max(float(r["bootstrap95_high"]) for r in sel)*1.06))
        ax.set_ylim(len(sel)-.25,-.75)
    else:
        ax.text(.5,.5,"No numerically admissible matched grid comparisons",
                ha="center",va="center",transform=ax.transAxes)
    save(fig,"fig02_paired_cv_gcv","Ten observed CV/GCV 100-point complete-grid matched case slices; 24-worker phase, independent seed-cluster 95% bootstrap")
    # Direct S vs once mapped lambda, M>=100
    sel=[r for r in coord if r.get("workload")=="grid_multiple_series" and
         r.get("method") in ("banded_cholesky","spectral_svd") and
         r.get("bootstrap95_low")!="" and int(r["M"])>=100]
    fig,ax=plt.subplots(figsize=(6.3,3.25))
    for method,color in (("spectral_svd","#174a7a"),("banded_cholesky","#58a2b7")):
        ss=sorted([r for r in sel if r["method"]==method and r["phase_workers"]==24],
                  key=lambda r:(int(r["M"]),int(r["n"])))
        if not ss:continue
        xy=defaultdict(list)
        for r in ss:xy[int(r["M"])].append(float(r["geometric_ratio"]))
        x=sorted(xy)
        ax.plot(x,[statistics.median(xy[k]) for k in x],marker="o",ls="-",
                color=color,label=method.replace("_"," "))
    ax.axhline(1,color="black",ls="--",lw=.75)
    ax.set(xlabel="Candidate grid density M",ylabel="Mapped-lambda / direct-S cold time")
    ax.set_xscale("log")
    if ax.lines and len(ax.lines)>1:ax.legend(frameon=False,fontsize=7)
    if not sel:ax.text(.5,.5,"No eligible coordinate pairs",ha="center",va="center",transform=ax.transAxes)
    save(fig,"fig03_mapping_cost","Median of cell-level matched geometric ratios, 24-worker phase and grid/multiple-series workload; not a pooled isolated-latency claim")
    # Four-workload cost structure at one common pilot case and a phase
    sel=[r for r in timing if r.get("case_id")=="pilot_gcv_n64_d1_m100" and
         r.get("method") in ("banded_cholesky","spectral_svd") and
         r.get("coordinate")=="direct_s" and r.get("phase_workers")==24 and
         int(r.get("valid_rows") or 0)>0]
    fig,ax=plt.subplots(figsize=(6.4,3.3))
    x=list(range(4))
    for meth,off,c in (("spectral_svd",-.18,"#174a7a"),("banded_cholesky",.18,"#58a2b7")):
        yy=[]
        for w in WORKLOADS:
            v=[float(r["median_total_cold_s"]) for r in sel
               if r["method"]==meth and r["workload"]==w
               and r.get("median_total_cold_s")!=""]
            yy.append(statistics.median(v) if v else float("nan"))
        ax.bar([i+off for i in x],yy,.36,color=c,label=meth.replace("_"," "))
    ax.set_xticks(x,["1 S / 1 series","grid / 1 series","1 S / 3 series","grid / 3 series"],rotation=12,ha="right")
    ax.set_ylabel("Median complete-criterion cold time (s)")
    ax.set_yscale("log")
    ax.legend(frameon=False,fontsize=7)
    save(fig,"fig04_workloads","GCV n=64,d=1,M=100, 24-worker phase; cold end-to-end criterion evaluation includes setup and candidate search")
    (output/"figure_index.json").write_text(json.dumps(desc,indent=2)+"\n",encoding="utf-8")
    return desc


def tex_summary(output,summary,timing,paired):
    """Reproducible manuscript table: group names disclose mu/case variation."""
    tex=output/"empirical_results.tex"
    primary=[r for r in paired if r["method"]=="spectral_svd" and
             r["baseline"]=="banded_cholesky" and
             r["workload"]=="grid_one_series" and r["coordinate"]=="direct_s" and
             r["criterion"] in ("cv","gcv") and int(r["M"])==100 and
             int(r["phase_workers"])==24 and
             r["bootstrap95_low"]!=""]
    primary=sorted(primary,key=lambda r:(r["criterion"],int(r["n"]),r["case_id"]))
    lines=[r"\newcommand{\EmpiricalJobs}{"+str(summary["recorded_jobs"])+r"}",
           r"\newcommand{\EmpiricalRows}{"+str(summary["tensor_rows"])+r"}",
           r"\newcommand{\EmpiricalValidRows}{"+str(summary["valid_complete_rows"])+r"}",
           r"\newcommand{\EmpiricalFailedJobs}{"+str(summary["nonzero_process_jobs"])+r"}",
           r"\begin{table}[t]",
           r"\caption{Valid matched complete-search banded/SVD ratios for a 100-candidate, one-series grid in the 24-worker phase. Data denotes the conditional observed-difference mean, versus the default fixed zero mean. Hybrid labels refer to the broader comparison design, not the SVD/banded pairing itself. Confidence limits resample independent seed clusters; numerical agreement is float64 selected-score parity only.}",
           r"\label{tab:empirical-paired}",r"\centering\small",
           r"\begin{tabular}{llrrrrr}",r"\toprule",
           r"Criterion & Case design & $n$ & $d$ & seeds & ratio & 95\% CI\\",r"\midrule"]
    def case_group(name):
        if name.startswith("pilot_data"):return "pilot-data"
        if name.startswith("confirm_data"):return "confirm-data"
        if name.startswith("pilot_hybrid"):return "pilot-hybrid"
        return name.split("_")[0]
    for r in primary:
        lines.append(f'{r["criterion"].upper()} & {case_group(r["case_id"])} & {r["n"]} & {r["d"]} & {r["independent_seeds"]} & {r["geometric_ratio"]:.2f} & [{float(r["bootstrap95_low"]):.2f}, {float(r["bootstrap95_high"]):.2f}]'+r"\\")
    if not primary:
        lines.append(r"\multicolumn{7}{c}{No eligible matched full-grid comparisons}\\")
    lines += [r"\bottomrule",r"\end{tabular}",r"\end{table}"]
    tex.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--backup",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    if os.environ.get("RUNNER_NAME")!="PCAG103A-08":
        raise EnvironmentError("Require exact PCAG103A-08 runner")
    if a.out.exists():raise FileExistsError("Refuse to overwrite derived output")
    a.out.mkdir(parents=True)
    tensor,files,problems,chain,report,statuses,qa_classes=ingress(a.original,a.backup)
    pairs=pair_rows(tensor)
    coord=coord_pairs(tensor)
    pair_summary=summarize_pair(pairs,"ratio_baseline_over_method")
    coordinate_summary=summarize_pair(coord,"mapped_over_direct_s")
    timings=timing_summary(tensor)
    rel=reliability(tensor)
    valid=sum(1 for r in tensor if fvalid(r))
    summary={"experiment":"experiment011","evidence":"empirical_complete_criterion_sparse_not_full_factorial",
             "recorded_jobs":len(report["results"]),"tensor_rows":len(tensor),
             "valid_complete_rows":valid,"nonvalid_or_missing_rows":len(tensor)-valid,
             "nonzero_process_jobs":sum(r["returncode"]!=0 for r in report["results"]),
             "worker_phase_jobs":dict(Counter(str(r["phase_workers"]) for r in report["results"])),
             "selected_file_manifest":len(files),"input_integrity_problems":len(problems),
             "paired_baseline_rows":len(pairs),
             "valid_paired_baseline_rows":sum(r["float64_pair"] for r in pairs),
             "valid_coordinate_pairs":len(coord),
             "report_sha256":sha(a.original/FINAL),
             "design_sha256":sha(a.original/BASE/"cases.json"),
             "status_categories":dict(statuses),
             "qa_categories":dict(qa_classes),
             "lineage":chain,
             "warnings":["Timing is under varying concurrent process loads, not isolated latency.",
                         "Float64 selected-score parity is not a high-precision forward-error certificate.",
                         "Survivor bias: invalid/failed/infeasible complete searches cannot win timings.",
                         "Missing or ambiguous candidate rows are explicitly masked, not zero seconds."]}
    write_csv(a.out/"accepted_file_manifest.csv",files,list(files[0]) if files else [])
    write_csv(a.out/"timing_tensor.csv.gz",tensor,SCHEMA)
    write_csv(a.out/"paired_backend_rows.csv.gz",pairs,list(pairs[0]) if pairs else [])
    write_csv(a.out/"paired_coordinate_rows.csv.gz",coord,list(coord[0]) if coord else [])
    for name,data in (("timing_cell_summary.csv",timings),
                      ("paired_backend_seed_bootstrap.csv",pair_summary),
                      ("paired_coordinate_seed_bootstrap.csv",coordinate_summary),
                      ("criterion_backend_reliability.csv",rel)):
        write_csv(a.out/name,data,list(data[0]) if data else [])
    (a.out/"integrity_issues.json").write_text(json.dumps(problems,indent=2)+"\n",encoding="utf-8")
    (a.out/"analysis_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (a.out/"claim_to_data_ledger.json").write_text(json.dumps({
        "scheduling_completion":{"claim":"2813 distinct scheduled jobs","source":"analysis_summary.json:recorded_jobs; accepted_file_manifest.csv"},
        "numerical_reliability":{"claim":"Complete-search status admissibility, not independent precision","source":"criterion_backend_reliability.csv"},
        "backend_comparison":{"claim":"Only numerically matching, same-seed, same-phase method pairs","source":"paired_backend_seed_bootstrap.csv"},
        "coordinate_cost":{"claim":"Only same-seed complete-grid same-method matched coordinate pairs","source":"paired_coordinate_seed_bootstrap.csv"},
        "workloads":{"claim":"Observed median full criterion time by workload, no pooling worker phases","source":"timing_cell_summary.csv"},
        "lineage":{"claim":"Accepted final-report records only; origin reconstructed from cumulative report chain","source":"accepted_file_manifest.csv; analysis_summary.json:lineage"},
    },indent=2)+"\n",encoding="utf-8")
    fig=figure_outputs(a.out,timings,pair_summary,coordinate_summary,rel)
    tex_summary(a.out,summary,timings,pair_summary)
    print(json.dumps({**{k:summary[k] for k in ("recorded_jobs","tensor_rows","valid_complete_rows","nonzero_process_jobs","input_integrity_problems","valid_paired_baseline_rows","valid_coordinate_pairs")},
                      "lineage":chain,"figures":[x["id"] for x in fig],
                      "output":str(a.out)},indent=2))
    if problems:
        print("Input integrity issues and exclusions are in integrity_issues.json; do not rank those rows.")


if __name__=="__main__":
    main()
