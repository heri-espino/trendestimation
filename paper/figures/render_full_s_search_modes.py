"""AwesomeFigures charts of 1 versus 17 versus repeated full-S evaluations.

These plots read only the source-of-truth measured search_mode_timings.csv,
not invented timing estimates. They are separate from the seven backend
per-candidate validation figures in render_full_s_factorial.py.
"""
from __future__ import annotations

import csv
from pathlib import Path
from runpy import run_path

import matplotlib.pyplot as plt
import numpy as np

PAPER=Path(__file__).resolve().parents[1]
OUTPUT=PAPER/"figures"
DATA=PAPER/"benchmarks/full_s_search_reference"
METHODS=("dense_fresh","dense_cached","general_banded","dense_cholesky",
         "banded_cholesky","eigh","svd")
METHOD_NAMES=("Fresh dense","Cached dense","General banded","Dense Cholesky",
              "Banded Cholesky","Eigendecomposition","SVD")
CRITERIA=("cv","gcv","aicc","bic","mle")


def rows():
    file=DATA/"search_mode_timings.csv"
    if not file.is_file():
        raise FileNotFoundError(
            f"No measured coordinate search results: {file}. "
            "Run paper/benchmarks/full_s_search_modes.py first.")
    with file.open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))


def source_row(data, *, n=24,d=2,mu=0.,criterion="gcv",method="svd",
               R=1,reuse_mode="shared",policy="mapped_s_lambda"):
    found=[r for r in data if int(r["n"])==n and int(r["d"])==d
           and float(r["mu"])==mu and r["criterion"]==criterion
           and r["method"]==method and int(r["R"])==R
           and r["reuse_mode"]==reuse_mode and r["policy"]==policy]
    if len(found)!=1:
        raise ValueError(f"Missing unique measured cell: {d=} {mu=} "
                         f"{criterion=} {method=} {R=} {reuse_mode=} "
                         f"{policy=}")
    return found[0]


def ms(row,*,include_map=False):
    key="total_standalone_s" if include_map else "total_backend_only_s"
    return 1000*float(row[key])


def save(pub,fig,name,save_pdf):
    OUTPUT.mkdir(exist_ok=True,parents=True)
    with plt.rc_context({"svg.fonttype":"none"}):
        fig.savefig(OUTPUT/(name+".svg"),format="svg")
    save_pdf(pub,fig,OUTPUT/(name+".pdf"))
    print("[search AwesomeFigures]",name,"PDF+SVG")


def make_figures():
    records=rows()
    style=run_path(str(OUTPUT/"render_awesomefigures.py"))
    COLORS=style["COLORS"]
    axis=style["_axis"]
    with style["publication_context"]() as pub:
        save_pdf=style["_save"]
        # 1 score versus 17-point search versus three repeated 17-point
        # searches: all at matched n,d,mu,criterion.
        fig,ax=axis(pub,ylog=True)
        x=[0,1,2]
        for i,(method,label) in enumerate(zip(METHODS,METHOD_NAMES)):
            entries=[
                source_row(records,d=1,method=method,R=1,
                           policy="single_mapped_s_lambda"),
                source_row(records,d=1,method=method,R=1,
                           policy="mapped_s_lambda"),
                source_row(records,d=1,method=method,R=3,
                           policy="mapped_s_lambda"),
            ]
            # A direct result cannot claim full-grid speed if it failed.
            t=[ms(r,include_map=True) if r["success"]=="True"
               else float("nan") for r in entries]
            ax.plot(x,t,marker=("o","s","^","D")[i%4],
                    linestyle=("-","--","-.",":")[i%4],
                    lw=1.3,markersize=3,color=COLORS[i%len(COLORS)],
                    label=label)
        ax.set_xticks(x,("One S=.5 score","17-point grid","3 × 17-point grid"))
        ax.tick_params(axis="x",labelsize=7)
        ax.set(ylabel="Standalone median total (ms, log scale)",
               xlabel="GCV workload (n=24, d=1, fixed mu=0)")
        ax.legend(ncol=3,loc="upper center",bbox_to_anchor=(.5,-.23),
                  fontsize=7,frameon=False)
        fig.subplots_adjust(left=.13,right=.98,bottom=.36,top=.94)
        save(pub,fig,"full_s_single_grid_repeated",save_pdf)

        # Discrete grid policies only: 17 candidates, all criteria,
        # spectral backend, fixed d and mu. The log grid can select
        # different candidates; native S and mapped lambda are identical.
        fig,ax=axis(pub,ylog=True)
        policies=("native_s","mapped_s_lambda","native_log_lambda")
        captions=("Direct S (invert each)","Map S once -> lambda",
                  "Independent log-lambda")
        for k,(policy,label) in enumerate(zip(policies,captions)):
            value=[]
            for criterion in CRITERIA:
                r=source_row(records,d=2,criterion=criterion,policy=policy)
                value.append(ms(r,include_map=True)
                             if r["success"]=="True" else float("nan"))
            ax.bar(np.arange(5)+(k-1)*.24,value,width=.24,
                   color=COLORS[(k*2)%len(COLORS)],label=label)
        ax.set_xticks(np.arange(5),[name.upper() for name in CRITERIA])
        ax.set(xlabel="Criterion (17 candidate points; spectral solver)",
               ylabel="Standalone full-grid search time (ms, log scale)")
        ax.legend(ncol=2,loc="upper center",bbox_to_anchor=(.5,-.23),
                  frameon=False,fontsize=7)
        fig.subplots_adjust(left=.13,right=.98,bottom=.36,top=.94)
        save(pub,fig,"full_s_grid_coordinate_times",save_pdf)

        # Bounded *local* optimization, deliberately not conflated with
        # full 17-point discrete grid search. Both compare candidate
        # endpoint evaluations but have variable function-eval counts.
        fig,ax=axis(pub,ylog=True)
        for k,(policy,label) in enumerate((
            ("continuous_s","Bounded S search"),
            ("continuous_log_lambda","Bounded log-lambda search"),
        )):
            vals=[]
            for criterion in CRITERIA:
                r=source_row(records,d=2,criterion=criterion,policy=policy)
                vals.append(ms(r) if r["success"]=="True" else float("nan"))
            ax.bar(np.arange(5)+(k-.5)*.34,vals,width=.34,
                   color=COLORS[(k*3+1)%len(COLORS)],label=label)
        ax.set_xticks(np.arange(5),[name.upper() for name in CRITERIA])
        ax.set(xlabel="Criterion (bounded local search, not global)",
               ylabel="Search time (ms, log scale)")
        ax.legend(ncol=2,loc="upper center",bbox_to_anchor=(.5,-.21),
                  frameon=False,fontsize=7)
        fig.subplots_adjust(left=.13,right=.98,bottom=.34,top=.94)
        save(pub,fig,"full_s_continuous_coordinate_times",save_pdf)

        # Cold versus amortized backend preparation for repeated
        # evaluations of the SAME mapped grid on three independent y.
        fig,ax=axis(pub)
        ratios=[]
        for method in METHODS:
            cold=source_row(records,d=1,criterion="gcv",method=method,
                            R=3,reuse_mode="cold",policy="mapped_s_lambda")
            warm=source_row(records,d=1,criterion="gcv",method=method,
                            R=3,reuse_mode="shared",policy="mapped_s_lambda")
            valid=cold["success"]=="True" and warm["success"]=="True"
            ratio=ms(cold)/ms(warm) if valid and ms(warm)>0 else np.nan
            ratios.append(ratio)
        for i,val in enumerate(ratios):
            ax.bar(i,val,color=COLORS[i%len(COLORS)],width=.7)
        ax.axhline(1.0,color="#777777",lw=.9,linestyle="--")
        ax.set_xticks(np.arange(7),
                      ("Fresh","Cached","Banded","Dense Ch.","Band Ch.","Eigh","SVD"))
        ax.tick_params(axis="x",labelsize=7)
        ax.set(xlabel="GCV backend, 3 independent series",
               ylabel="Cold / shared preprocessing time")
        fig.subplots_adjust(left=.13,right=.98,bottom=.25,top=.94)
        save(pub,fig,"full_s_search_reuse_speedup",save_pdf)

        # Source-supplied selected smoothness levels; different grids
        # and bounded local optimizers can select different values.
        fig,ax=axis(pub)
        policies=("native_s","mapped_s_lambda","native_log_lambda",
                  "continuous_s","continuous_log_lambda")
        labels=("S grid","Same grid as lambda","Log-lambda grid",
                "Bounded S optimizer","Bounded log-lambda optimizer")
        for k,(policy,label) in enumerate(zip(policies,labels)):
            selected=[]
            for name in CRITERIA:
                r=source_row(records,d=2,criterion=name,policy=policy)
                selected.append(float(r["selected_s"])
                                if r["success"]=="True" else np.nan)
            ax.plot(range(5),selected,marker=("o","s","^","D")[k%4],
                    linewidth=1.4,markersize=4,
                    color=COLORS[k%len(COLORS)],label=label)
        ax.set_xticks(range(5),[x.upper() for x in CRITERIA])
        ax.set_ylim(-.03,1.03)
        ax.set(xlabel="Selection criterion (fixed mu=0, d=2)",
               ylabel="Selected normalized smoothness S")
        ax.legend(ncol=2,loc="upper center",bbox_to_anchor=(.5,-.22),
                  frameon=False,fontsize=7)
        fig.subplots_adjust(left=.13,right=.98,bottom=.34,top=.94)
        save(pub,fig,"full_s_coordinate_selected_s",save_pdf)


if __name__=="__main__":
    make_figures()
