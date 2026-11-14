"""Experiment011 robustness figures, derived from the frozen empirical tensor only.

No solver calls, no campaign launch, no input modification. All denominators
are observed method/workload timing rows; repeated rows are NOT independent
Bernoulli experiments. Paired speedup uncertainty was computed previously
over independent seed clusters and is read from the frozen bootstrap CSV.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
FROZEN = ROOT / "paper/benchmarks/experiment011/pc08_empirical/derived/42636962129"
OUTPUT = Path(__file__).resolve().parent
METHODS = ("banded_cholesky", "spectral_svd")
BLU = "#155989"
PALE = "#61a1c6"
RED = "#bb5360"
GOLD = "#d39a48"
INK = "#253a4c"
GRID = "#dce5ed"
KKT_RE = re.compile(r"PLS KKT failed: backward_error=([0-9.eE+-]+)")


def sha(file: Path):
    digest=hashlib.sha256()
    with file.open("rb") as stream:
        for part in iter(lambda:stream.read(1048576),b""):
            digest.update(part)
    return digest.hexdigest()


def save(fig, name, description, folder, manifest):
    folder.mkdir(parents=True,exist_ok=True)
    fig.savefig(folder/(name+".pdf"),bbox_inches="tight",pad_inches=.12)
    fig.savefig(folder/(name+".png"),bbox_inches="tight",pad_inches=.12,dpi=185)
    plt.close(fig)
    manifest.append({"id":name,"pdf":"figures/"+name+".pdf",
                     "png":"figures/"+name+".png","description":description})


def oneplot(df,sel_pairs,out,meta):
    cases=meta["robust_cases"]
    m=df[df.case_id.isin(cases)&df.method.isin(METHODS)].copy()
    m["scope"]=np.where(m.workload.str.startswith("grid"),"grid","one")
    tab=m.groupby(["case_id","method","scope"],observed=True).agg(
        successes=("status",lambda s:(s=="ok").sum()),
        attempts=("status","size"),
        seed_clusters=("seed_index","nunique")
    )
    for c in cases:
        for meth in METHODS:
            for w in ("one","grid"):
                assert (c,meth,w) in tab.index, (c,meth,w)
    matrix=np.array([
        [tab.loc[(c,"banded_cholesky","one"),"successes"]/tab.loc[(c,"banded_cholesky","one"),"attempts"],
         tab.loc[(c,"spectral_svd","one"),"successes"]/tab.loc[(c,"spectral_svd","one"),"attempts"],
         tab.loc[(c,"banded_cholesky","grid"),"successes"]/tab.loc[(c,"banded_cholesky","grid"),"attempts"],
         tab.loc[(c,"spectral_svd","grid"),"successes"]/tab.loc[(c,"spectral_svd","grid"),"attempts"]]
        for c in cases])
    assert np.array_equal(matrix,np.tile([1.,1.,0.,1.],(len(cases),1))),"Unexpected failure pattern"
    fig,ax=plt.subplots(figsize=(6.8,4.4))
    im=ax.imshow(matrix,cmap=ListedColormap([RED,BLU]),vmin=0,vmax=1,aspect="auto")
    ids=[]
    for c in cases:
        r=m[m.case_id==c].iloc[0]
        mu="data" if "data" in c else "zero"
        ids.append(f'{r.criterion.upper():<4}  n={int(r.n):<4} d={int(r.d)}  M={int(r.grid_denominator):<5}')
    ax.set_yticks(np.arange(len(cases)),ids,fontsize=8)
    ax.set_xticks(range(4),["Banded\n1 candidate","SVD\n1 candidate",
                            "Banded\nfull grid","SVD\nfull grid"],fontsize=8)
    ax.set_xticks(np.arange(-.5,4,1),minor=True)
    ax.set_yticks(np.arange(-.5,len(cases),1),minor=True)
    ax.grid(which="minor",color="white",linewidth=2)
    ax.tick_params(axis="both",which="both",length=0)
    for i in range(len(cases)):
        for j in range(4):
            ax.text(j,i,f"{matrix[i,j]:.0%}",va="center",ha="center",
                    color="white",fontweight="bold",fontsize=9)
    ax.set_title("Nine reproducible Cholesky complete-grid failure regimes",
                 fontsize=11,weight="bold",color=INK,pad=11)
    fig.text(.50,.01,"97 independent seeds per case; repeated workload/coordinate rows are correlated",
             ha="center",fontsize=7.5,color=INK)
    fig.subplots_adjust(bottom=.17,left=.30,right=.98,top=.89)
    save(fig,"fig05_complete_grid_failure",
         "Nine case families: one candidate succeeds for both; full grid fails the banded KKT gate but passes SVD",
         out/"figures",meta["figures"])
    return tab.reset_index()


def failure_mechanisms(df,out,meta):
    subset=df[(df.d==4)&df.n.isin([256,1024,2048,4096])&
              df.method.isin(METHODS)].copy()
    # Each component is a row status, not a Bernoulli trial/seed.
    subset["mechanism"]=np.select([
        subset.status.eq("ok"),
        subset.comment.fillna("").str.contains("PLS KKT failed",regex=False),
        subset.comment.fillna("").str.contains("Inaccurate S inversion",regex=False),
        subset.status.eq("budget_exceeded")
    ],["complete","KKT gate","S inversion","resource gate"],default="other")
    by=(subset.groupby(["n","method","mechanism"],observed=True)
        .size().unstack(fill_value=0))
    order=[(float(n),m) for n in [256,1024,2048,4096] for m in METHODS]
    by=by.reindex(order,fill_value=0)
    nrows=by.sum(axis=1)
    fig,ax=plt.subplots(figsize=(6.8,3.7))
    y=np.arange(len(order))
    left=np.zeros(len(order))
    colors={"complete":BLU,"KKT gate":RED,"S inversion":GOLD,
            "resource gate":"#8789a3","other":"#a0a0a0"}
    for category in colors:
        vals=by.get(category,pd.Series(0,index=by.index)).to_numpy()/nrows.to_numpy()
        if any(vals):
            ax.barh(y,vals,left=left,height=.7,label=category,
                    color=colors[category])
            left+=vals
    ax.invert_yaxis()
    ax.set_yticks(y,[f'n={int(n):,}   {("banded" if meth=="banded_cholesky" else "SVD")}'
                    for n,meth in order],fontsize=8)
    ax.set_xticks(np.linspace(0,1,6),[f"{j:.0%}" for j in np.linspace(0,1,6)])
    ax.set_xlim(0,1)
    ax.set_xlabel("Fraction of available method-level timing rows",fontsize=9)
    ax.set_title("Fourth-order case: two distinct mechanisms",
                 fontsize=11,weight="bold",color=INK,pad=9)
    ax.legend(ncol=3,loc="upper center",bbox_to_anchor=(.5,-.15),
              frameon=False,fontsize=8)
    ax.grid(axis="x",alpha=.25)
    fig.tight_layout(pad=1.15)
    save(fig,"fig06_fourth_order_failure_modes",
         "Recorded n=256 to 4096, d=4 rows by solver and status; the two methods both encounter mapping failures at large n",
         out/"figures",meta["figures"])
    tab=by.copy()
    tab["available_rows"]=nrows
    tab.reset_index().rename(columns={"level_0":"n","level_1":"method"}).to_csv(
        out/"fourth_order_failure_mechanisms.csv",index=False)
    return subset


def crossover(pairs,out,meta):
    cases=["pilot_gcv_n64_d1_m100","pilot_cv_n128_d3_m100",
           "confirm_data_cv_n256_d3_m100"]
    df=pairs[(pairs.case_id.isin(cases))&
             (pairs.baseline=="banded_cholesky")&
             (pairs.method=="spectral_svd")&
             (pairs.coordinate=="direct_s")&
             (pairs.phase_workers==24)&
             (pairs.workload.isin(["one_s_one_series","grid_one_series"]))].copy()
    assert len(df)==6,df.shape
    fig,ax=plt.subplots(figsize=(6.8,3.6))
    label={"pilot_gcv_n64_d1_m100":"GCV, n=64, d=1, fixed mean",
           "pilot_cv_n128_d3_m100":"CV, n=128, d=3, fixed mean",
           "confirm_data_cv_n256_d3_m100":"CV, n=256, d=3, plug-in mean"}
    for i,c in enumerate(cases):
        for j,(wl,off,color,mark) in enumerate([
            ("one_s_one_series",-.13,PALE,"s"),
            ("grid_one_series",+.13,BLU,"o")
        ]):
            r=df[(df.case_id==c)&(df.workload==wl)].iloc[0]
            est=float(r.geometric_ratio)
            lo=float(r.bootstrap95_low)
            hi=float(r.bootstrap95_high)
            ax.errorbar(est,i+off,xerr=[[est-lo],[hi-est]],fmt=mark,capsize=2.5,
                        markersize=6,lw=1.3,color=color,zorder=3)
    ax.set_yticks(range(3),[label[c] for c in cases],fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(.4,7.0)
    ax.axvline(1,lw=1,ls="--",color="#525c66")
    ax.grid(axis="x",alpha=.25)
    ax.set_xlabel("Banded Cholesky / SVD total cold time (log scale)",fontsize=9)
    ax.set_title("A single candidate can favor banded; the grid favors SVD",
                 fontsize=11,weight="bold",pad=10)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0],[0],marker="s",lw=0,color=PALE,label="One candidate"),
                       Line2D([0],[0],marker="o",lw=0,color=BLU,label="100-candidate grid")],
              frameon=False,fontsize=8,loc="upper right")
    fig.tight_layout()
    save(fig,"fig07_single_vs_grid_speedups",
         "Same valid paired cases within 24-worker phase: seed-cluster 95% CIs, banded/SVD ratio; one vs 100 candidates",
         out/"figures",meta["figures"])
    df.to_csv(out/"representative_paired_speedups.csv",index=False)


def memory(out,meta):
    # Source policy: experiment006/run.py: memory_budget_status.
    # These are formula-based allowances / storage scales, NOT observed RSS.
    ns=np.array([64,128,256,512,1024,2048,4096,8192,16384,32768],dtype=float)
    d=4
    mib=1024.**2
    data=pd.DataFrame({"n":ns.astype(int),
         "spectral_policy_5_dense_matrices_MiB":(5*8*ns**2)/mib,
         "naive_policy_7_dense_matrices_MiB":(7*8*ns**2)/mib,
         "banded_two_arrays_d4_MiB":(2*8*ns*(d+1))/mib})
    data["policy_dense_cap_MiB"]=2048.
    data["spectral_policy_under_2GiB"]=data["spectral_policy_5_dense_matrices_MiB"]<=2048
    data.to_csv(out/"memory_policy_model.csv",index=False,float_format="%.9g")
    fig,ax=plt.subplots(figsize=(6.7,3.85))
    ax.plot(ns,data["spectral_policy_5_dense_matrices_MiB"],"o-",color=BLU,lw=2,
            label="SVD policy: 5 full float64 matrices")
    ax.plot(ns,data["naive_policy_7_dense_matrices_MiB"],"s--",color="#728fa7",lw=1.5,
            label="Naive inverse policy: 7 full matrices")
    ax.plot(ns,data["banded_two_arrays_d4_MiB"],"^-",color=RED,lw=1.8,
            label="Banded factor + selected inverse (d=4)")
    ax.axhline(2048,color=GOLD,ls=(0,(5,3)),lw=1.5,label="Dense allocation limit (2 GiB)")
    ax.axvspan(64,4096,color="#dde8f0",alpha=.23)
    ax.set(xscale="log",yscale="log")
    ax.set_xticks(ns)
    ax.set_xticklabels([f'{int(n):,}' for n in ns],rotation=35,ha="right",fontsize=7)
    ax.set_xlabel("Series length n (shaded: evaluated sample-size range)",fontsize=9)
    ax.set_ylabel("Storage scale or admission allowance (MiB; log axis)",fontsize=9)
    ax.set_title("Why dense spectral reuse trades speed for quadratic memory",
                 fontsize=10.5,weight="bold",pad=9)
    ax.grid(which="both",alpha=.18)
    ax.legend(frameon=False,fontsize=7.5,loc="upper left")
    fig.tight_layout()
    save(fig,"fig08_memory_policy",
         "Code-policy model (not measured peak RAM): spectral 40n² bytes, naive 56n², banded two arrays 16n(d+1) bytes, 2 GiB dense cap",
         out/"figures",meta["figures"])


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,default=FROZEN)
    p.add_argument("--output",type=Path,default=OUTPUT)
    a=p.parse_args()
    a.output.mkdir(exist_ok=True,parents=True)
    plt.rcParams.update({
        "font.family":"sans-serif","font.size":8.5,
        "pdf.fonttype":42,"ps.fonttype":42,
        "axes.spines.top":False,"axes.spines.right":False,
        "axes.edgecolor":"#899ba9","axes.labelcolor":INK,
        "xtick.color":INK,"ytick.color":INK,
        "savefig.facecolor":"white","figure.facecolor":"white"
    })
    tensor=a.frozen/"timing_tensor.csv.gz"
    pair_file=a.frozen/"paired_backend_seed_bootstrap.csv"
    summary=json.loads((a.frozen/"analysis_summary.json").read_text(encoding="utf-8"))
    assert (summary["recorded_jobs"],summary["tensor_rows"],summary["valid_complete_rows"])==(2813,92679,76220)
    data=pd.read_csv(tensor,low_memory=False)
    pairs=pd.read_csv(pair_file,low_memory=False)
    assert len(data)==92679
    comments=data.comment.fillna("")
    kkt=data[(data.method=="banded_cholesky")&
             comments.str.startswith("ArithmeticError: PLS KKT failed")]
    inv=data[comments.str.contains("Inaccurate S inversion",regex=False)]
    assert (len(kkt),len(inv))==(9096,6336),(len(kkt),len(inv))
    kkt_errors=kkt.comment.str.extract(KKT_RE,expand=False).astype(float)
    assert (kkt_errors>1e-7).all()
    other=data[data.status.eq("budget_exceeded")].method.value_counts().to_dict()
    assert other=={"naive_inverse":776,"spectral_svd":194},other
    m=data[data.method.isin(METHODS)].copy()
    m["scope"]=np.where(m.workload.str.startswith("grid"),"grid","one")
    g=(m.groupby(["case_id","method","scope"],observed=True)
       .status.agg(lambda s:float((s=="ok").mean())).unstack(["method","scope"]))
    robust=[c for c, r in g.iterrows() if all(
        r.get((meth,wl))==(0. if meth=="banded_cholesky" and wl=="grid" else 1.)
        for meth in METHODS for wl in ("one","grid")
    )]
    robust=sorted(robust,key=lambda c:(c.split("_")[1],c))
    assert len(robust)==9,robust
    meta={"experiment":"experiment011","supplement":"robustness001",
          "original_tensor_sha256":sha(tensor),
          "original_pairs_sha256":sha(pair_file),
          "original_report_sha256":summary["report_sha256"],
          "recorded_jobs":2813,
          "rows":len(data),
          "kkt_failure_rows":len(kkt),
          "kkt_threshold":1e-7,
          "kkt_error_min":float(kkt_errors.min()),
          "kkt_error_median":float(kkt_errors.median()),
          "kkt_error_max":float(kkt_errors.max()),
          "inversion_error_rows_by_method":inv.groupby("method").size().to_dict(),
          "resource_exclusion_rows_by_method":other,
          "robust_cases":robust,
          "figures":[],
          "caveat":"SVD does not undergo identical banded implementation KKT gate; recorded status success is not independent high-precision evidence.",
          "memory_note":"All plotted memory curves are code-policy scaling formulae, not measured allocations or peak RSS.",
          "sampling_note":"Timing rows and repeated workloads are correlated within independent seeds."}
    cases=[]
    for c in robust:
        slice_=m[m.case_id==c]
        for meth in METHODS:
            for scope in ("one","grid"):
                sub=slice_[(slice_.method==meth)&(slice_.scope==scope)]
                cases.append({"case_id":c,"n":int(sub.n.iloc[0]),"d":int(sub.d.iloc[0]),
                              "criterion":sub.criterion.iloc[0],
                              "candidate_grid_M":int(sub.grid_denominator.iloc[0]),
                              "method":meth,"workload_scope":scope,
                              "valid_rows":int(sub.status.eq("ok").sum()),
                              "recorded_method_rows":len(sub),
                              "independent_seed_clusters":int(sub.seed_index.nunique()),
                              "failure_type":("PLS KKT backward-error" if meth=="banded_cholesky" and scope=="grid" else "none")})
    pd.DataFrame(cases).to_csv(a.output/"nine_failure_cases.csv",index=False)
    oneplot(data,pairs,a.output,meta)
    failure_mechanisms(data,a.output,meta)
    crossover(pairs,a.output,meta)
    memory(a.output,meta)
    # Count by stage exactly; 57 failed process jobs lack method-level rows.
    counts=data.groupby(["method","status"],dropna=False).size().unstack(fill_value=0)
    counts.to_csv(a.output/"all_method_statuses.csv")
    ledger={
        "nine_cases":{"table":"nine_failure_cases.csv","source":"timing_tensor.csv.gz", "checks":"9 x 97 independent seeds, 100% single for both, 0% banded grid, 100% SVD grid"},
        "kkt":{"count":len(kkt),"source":"timing_tensor.csv.gz:comment","mechanism":"selected_inverse.py:BandedTrace.score, after cholesky_banded and cho_solve_banded, backward_error>1e-7"},
        "inversion":{"counts":meta["inversion_error_rows_by_method"],"source":"timing_tensor.csv.gz:comment", "caveat":"both backends can fail mapping; high-n fourth order"},
        "speedups":{"source":"paired_backend_seed_bootstrap.csv","filters":"same source/seed/case/phase=24, direct S, R=1, one-vs-M=100","file":"representative_paired_speedups.csv"},
        "memory":{"source":"experiment006/run.py:memory_budget_status; experiment011/cases.json:max_dense_bytes", "file":"memory_policy_model.csv",
                  "measured_peak_RAM":False,"budget_exceeded_causes":"Work gate; no observed infeasible_dense_memory status in selected tensor"}
    }
    (a.output/"claim_to_data_ledger.json").write_text(json.dumps(ledger,indent=2)+"\n",encoding="utf-8")
    (a.output/"figure_index.json").write_text(json.dumps(meta["figures"],indent=2)+"\n",encoding="utf-8")
    (a.output/"summary.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in meta.items() if k not in ("figures",)},indent=2))
    print("Saved",len(meta["figures"]),"new vector/raster figure pairs; NO numerical experiments rerun.")


if __name__=="__main__":
    main()
