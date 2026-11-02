"""Experiment009: theory-constrained, separately calibrated solver cost surfaces.

One physical fitted trend (Experiment007) and one complete AICc score
(Experiment008) have different algebraic costs. Never combine their times.
All historical observations are frozen with an exact GitHub source path.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import nnls

HERE = Path(__file__).resolve().parent
N_GRID = (64, 128, 256, 512, 1024, 16384, 131072)
D_GRID = tuple(range(1, 7))
M_GRID = (1, 7, 100, 1000, 10000, 100000)


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(line for line in handle
                                   if line.strip() and not line.startswith("#")))


def as_valid(x):
    return str(x).lower() in ("true", "1", "yes")


def collect_fit():
    items=read_csv(HERE/"data/experiment007_fit_pair.csv")
    pairs=defaultdict(dict)
    for r in items:
        n=int(r["n"]);d=int(r["d"])
        workload=r["workload"]
        M=7 if workload.startswith("grid") else 1
        R=3 if "three_series" in workload else 1
        k=(n,d,r["scale"],r["mu_policy"],workload)
        pairs[k][r["method"]]=dict(
            valid=as_valid(r["complete_accuracy"]),
            t=float(r["median_cold_s"]),
            ref=r["numerical_certification"])
    result=[]
    for (n,d,scale,mean,work),v in sorted(pairs.items()):
        if "svd" not in v or "cholesky" not in v:
            raise ValueError("Incomplete fit-only pair")
        result.append(dict(mode="fit",n=n,d=d,M=7 if work.startswith("grid") else 1,
            R=3 if "three_series" in work else 1,scale=scale,mu=mean,
            criterion="full_trend",workload=work,svd=v["svd"],
            cholesky=v["cholesky"]))
    return result


def collect_aicc():
    paths=sorted((HERE/"data").glob("experiment008_aicc_data_n*.csv"))
    if len(paths)!=4:
        raise ValueError("Exactly four frozen independent n-level files are required")
    pairs=defaultdict(dict)
    for path in paths:
        for r in read_csv(path):
            if r["coordinate"]!="mapped_lambda":
                continue
            if r["criterion"]!="aicc" or r["mu"]!="data":
                raise ValueError("AICc source dimensions unexpectedly changed")
            k=(int(r["n"]),int(r["d"]),int(r["M"]),int(r["R"]),r["workload"])
            name="svd" if r["method"]=="spectral_svd" else "cholesky"
            if name in pairs[k]: raise ValueError(f"Duplicate AICc pair {k}")
            pairs[k][name]=dict(
                valid=as_valid(r["valid"]) and math.isfinite(float(r["mean_s"])),
                t=float(r["mean_s"]),ref="criterion_status_only")
    result=[]
    for (n,d,M,R,work),v in sorted(pairs.items()):
        if len(v)!=2: raise ValueError(f"Missing AICc method at {(n,d,M,R)}")
        result.append(dict(mode="aicc",n=n,d=d,M=M,R=R,scale="high",
            mu="data",criterion="aicc",workload=work,
            svd=v["svd"],cholesky=v["cholesky"]))
    return result


def basis(mode,method,n,d,M,R):
    """Explicit predicted operation categories, scaled dimensionlessly.

    Fit-only SVD: preprocessing n^3 + per-series n^2 projection
    + each full fitted curve n^2.
    Fit-only Cholesky: per-curve n*d^2 factor + n*d solve
    (Experiment007 does NOT cache Cholesky factors across series).

    AICc: global scalar score, per-candidate SVD spectral O(n).
    Experiment008 includes a common spectral S->lambda mapper when
    n<=512 even in the Cholesky method's measured cold setup;
    its n^3 term must be retained for fidelity. AICC inputs only
    cover these sizes. Mapped lambda coordinate, M=1 or 100.
    """
    x=n/128.; z=d/2.
    if mode=="fit":
        if method=="svd":
            return np.array([1.,x**3,R*x*x,(M*R/7.)*x*x])
        return np.array([1.,x*z,(M*R/7.)*x*z*z,(M*R/7.)*x*z])
    if mode=="aicc":
        if method=="svd":
            return np.array([1.,x**3,R*x*x,(M*R/100.)*x])
        return np.array([1.,x**3,x*z,(M/100.)*x*z*z,(M*R/100.)*x*z])
    raise ValueError(mode)


def fit_models(records,mode):
    # Strict out-of-length validation; never train on the held-out n.
    n_train=(64,128) if mode=="fit" else (64,128,256)
    heldout=256 if mode=="fit" else 512
    models={}
    for method in ("svd","cholesky"):
        rows=[r for r in records if r["n"] in n_train and
              r[method]["valid"] and math.isfinite(r[method]["t"]) and
              r[method]["t"]>0]
        A=np.vstack([basis(mode,method,**{k:r[k] for k in ("n","d","M","R")})
                      for r in rows])
        b=np.asarray([r[method]["t"] for r in rows])
        # The coefficients are NONNEGATIVE by construction. This estimates
        # machine-specific constants; it does not prove complexity exponents.
        coefficients,_=nnls(A,b)
        models[method]=coefficients
    return models, n_train, heldout


def predict(models,mode,method,n,d,M,R):
    return float(basis(mode,method,n,d,M,R)@models[method])


def compare(records,models,mode,heldout):
    rows=[]
    for r in records:
        ps=predict(models,mode,"svd",r["n"],r["d"],r["M"],r["R"])
        pc=predict(models,mode,"cholesky",r["n"],r["d"],r["M"],r["R"])
        valid=all(r[m]["valid"] for m in ("svd","cholesky"))
        times=[r[m]["t"] for m in ("svd","cholesky")]
        empirical=("svd" if times[0]<times[1] else "cholesky") if valid else "not_comparable"
        theoretical="svd" if ps<pc else "cholesky"
        rows.append(dict(mode=mode,n=r["n"],d=r["d"],M=r["M"],R=r["R"],
            criterion=r["criterion"],workload=r["workload"],mu=r["mu"],
            scale=r["scale"],set=("holdout" if r["n"]==heldout else "training"),
            measured_svd_s=r["svd"]["t"],measured_cholesky_s=r["cholesky"]["t"],
            svd_eligible=r["svd"]["valid"],cholesky_eligible=r["cholesky"]["valid"],
            pred_svd_s=ps,pred_cholesky_s=pc,
            empirical_winner=empirical,predicted_winner=theoretical,
            correct=(theoretical==empirical if valid else ""),
            relative_speed_prediction=pc/ps if ps>0 else float("nan"),
            accuracy_reference=r["cholesky"]["ref"]))
    valid_test=[x for x in rows if x["set"]=="holdout" and
                x["empirical_winner"]!="not_comparable"]
    outcome=dict(mode=mode,holdout_n=heldout,paired_comparable=len(valid_test),
                 predicted_correct=sum(x["correct"] is True for x in valid_test),
                 accuracy=(sum(x["correct"] is True for x in valid_test)/len(valid_test)
                           if valid_test else None))
    return rows,outcome


def theoretical_surface(models,mode):
    # A surface is conditional on (M,R,C); save EVERY requested M.
    values=[]
    R_values=(1,3) if mode=="fit" else (1,2)
    for n in N_GRID:
        for d in D_GRID:
            for M in M_GRID:
                for R in R_values:
                    ps=predict(models,mode,"svd",n,d,M,R)
                    pc=predict(models,mode,"cholesky",n,d,M,R)
                    # Reliability is a separate constraint. Dense SVD is
                    # gated at n>2048 or 5*n*n*8>2 GiB; unmeasured sizes
                    # are extrapolations, NEVER certified backend choices.
                    memory_ok=(n<=2048 and 40*n*n<=2*1024**3)
                    support=(n<=256 if mode=="fit" else n<=512)
                    values.append(dict(mode=mode,n=n,d=d,M=M,R=R,
                        predicted_svd_s=ps,predicted_cholesky_s=pc,
                        predicted_winner=("svd" if ps<pc else "cholesky"),
                        ratio_svd_over_cholesky=ps/pc if pc>0 else float("nan"),
                        svd_memory_runtime_gate=memory_ok,
                        within_measured_n_support=support,
                        status=("unverified_extrapolation" if not support
                                else "descriptive_prediction_not_reliability_certified")))
    return values


def save_csv(path,rows):
    if not rows: raise ValueError("Empty generated table")
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def make_plot(output,mode,models,M,R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ns=(64,128,256,512,1024) if mode=="aicc" else (64,128,256,512,1024)
    vals=np.array([[
        math.log10(predict(models,mode,"svd",n,d,M,R)/
                   predict(models,mode,"cholesky",n,d,M,R))
        for d in D_GRID] for n in ns])
    fig,ax=plt.subplots(figsize=(7.0,4.2))
    image=ax.imshow(vals.T,aspect="auto",origin="lower",
                    cmap="RdBu_r",vmin=-1.2,vmax=1.2)
    ax.set_xticks(range(len(ns)),ns)
    ax.set_yticks(range(len(D_GRID)),D_GRID)
    ax.set_xlabel("Series length n")
    ax.set_ylabel("Difference order d")
    ax.set_title(f"{'AICc selection' if mode=='aicc' else 'Full trend fits'}"
                 f" — M={M}, R={R}\nCalibrated cost model, not a reliability certificate")
    for i,n in enumerate(ns):
        for j,d in enumerate(D_GRID):
            label="S" if vals[i,j]<0 else "C"
            ax.text(i,j,label,ha="center",va="center",fontsize=10,
                    fontweight="bold",color="black")
    bar=fig.colorbar(image,ax=ax)
    bar.set_label(r"$\log_{10}(T_{\rm SVD}/T_{\rm Cholesky})$"
                  "\nNegative: predicted SVD advantage")
    fig.tight_layout()
    for ext in ("pdf","svg","png"):
        fig.savefig(output/f"surface_{mode}_M{M}_R{R}.{ext}",
                    dpi=180,bbox_inches="tight")
    plt.close(fig)


def run(output):
    if output.exists(): raise FileExistsError(f"Refusing overwrite: {output}")
    output.mkdir(parents=True)
    summaries=[]
    for mode,measurements in (("fit",collect_fit()),("aicc",collect_aicc())):
        models,train,heldout=fit_models(measurements,mode)
        validation,quality=compare(measurements,models,mode,heldout)
        surf=theoretical_surface(models,mode)
        save_csv(output/f"surface_{mode}.csv",surf)
        save_csv(output/f"comparison_{mode}.csv",validation)
        shape=("n^3 setup + R n^2 projection + MR n^2 full fits"
               if mode=="fit" else
               "AICc includes shared n^3 mapper preparation for n<=512")
        summaries.append(dict(mode=mode,coefficient_fit_ns=list(train),
            heldout_n=heldout,sample_records=len(measurements),
            training_examples={method:sum(
                r["n"] in train and r[method]["valid"] for r in measurements)
                for method in ("svd","cholesky")},
            coefficients={k:list(map(float,v)) for k,v in models.items()},
            theoretical_features=shape,validation=quality))
        if mode=="fit":
            for M,R in ((1,1),(7,3),(100,3)):
                make_plot(output,mode,models,M,R)
        else:
            for M,R in ((1,1),(100,2)):
                make_plot(output,mode,models,M,R)
    (output/"calibration.json").write_text(
        json.dumps(dict(
          source_fit="results/experiment007-selfhosted-41510943429",
          source_full="results/experiment008-41529113497-broad",
          important_limitations=(
            "All fitted constants are platform-specific and descriptive. "
            "Fit-only and AICc full-criterion are separate experiments. "
            "No SVD-proxy comparison is independent forward-error proof. "
            "The AICc benchmark includes common S->lambda mapper setup. "
            "Predictions for n beyond training/observed lengths are unvalidated. "
            "Numerical reliability must gate a production switch. "
            "Other criteria and mapping options need their own calibration."),
          models=summaries),indent=2)+"\n",encoding="utf-8")
    print(json.dumps([s["validation"] for s in summaries],indent=2))
    return summaries


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    run(a.output)
