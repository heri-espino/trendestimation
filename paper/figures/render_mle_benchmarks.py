"""AwesomeFigures-rendered, source-traceable Springer PDF and website SVG.

Uses the EXACT same publication_context as render_awesomefigures.py, hence
the journal's measured physical width and LaTeX fonts. Never invent data.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CRITERIA=("cv","gcv","aicc","bic","mle")
METHODS=("dense_fresh","dense_cached","spectral","banded",
         "dense_cholesky","banded_cholesky")
NAMES=("Dense fresh","Dense cached","Spectral SVD",
       "General banded","Dense Cholesky","Banded Cholesky")
STYLES=("-","--","-.",":")
MARKERS=("o","s","^","D")


def _read(path, fields):
    if not path.exists():
        print(f"[awesomefigures] Missing real CSV: {path}; figure skipped")
        return None
    with path.open(encoding="utf-8",newline="") as f:
        data=list(csv.DictReader(f))
    if not data or not set(fields).issubset(data[0]):
        raise ValueError(f"Expected nonempty {fields} from {path}")
    return data


def _save(pub, fig, target, save_pdf):
    target.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"svg.fonttype":"none"}):
        fig.savefig(target.with_suffix(".svg"),format="svg")
    save_pdf(pub,fig,target)
    print("[awesomefigures] PDF + SVG:",target)


def render_all(pub,paper,colors,axis_factory,save_pdf):
    figure_dir=paper/"figures"
    gcv=_read(paper/"benchmarks/grid_reuse_reference/gcv_grid_timings.csv",
              ("n","d","M","R","mu","method","reuse","grid_policy","total_median_s"))
    if gcv:
        fig,ax=axis_factory(pub,ylog=True)
        for i,(method,label) in enumerate(zip(METHODS,NAMES)):
            values=sorted(
                (int(r["d"]),1000*float(r["total_median_s"])) for r in gcv
                if r["method"]==method and r["grid_policy"]=="log_lambda"
                and r["reuse"]=="warm" and int(r["n"])==48
                and int(r["M"])==11 and int(r["R"])==1
                and float(r["mu"])==0.0)
            if len(values)!=4:
                raise ValueError(f"Missing four difference-order GCV timings: {method}")
            ax.plot([v[0] for v in values],[v[1] for v in values],
                    color=colors[i],ls=STYLES[i%4],
                    marker=MARKERS[i%4],markersize=3.2,lw=1.3,label=label)
        ax.set_xticks((1,2,3,4))
        ax.set(xlabel="Difference order $d$ ($n=48$, 11 penalties)",
               ylabel="Total GCV search time (ms)")
        ax.legend(ncol=3,frameon=False,fontsize=7,loc="upper center",
                  bbox_to_anchor=(.5,-.20))
        fig.subplots_adjust(left=.13,right=.97,top=.95,bottom=.33)
        _save(pub,fig,figure_dir/"gcv_solver_by_order.pdf",save_pdf)

        vals=[]
        for method in METHODS:
            entries={r["reuse"]:float(r["total_median_s"]) for r in gcv
                     if r["method"]==method and r["grid_policy"]=="log_lambda"
                     and int(r["n"])==48 and int(r["d"])==2
                     and int(r["M"])==11 and int(r["R"])==4
                     and float(r["mu"])==0.0}
            if set(entries)!={"cold","warm"}:
                raise ValueError(f"Missing repeat benchmark {method}")
            vals.append(entries["cold"]/entries["warm"])
        fig,ax=axis_factory(pub)
        ax.bar(range(6),vals,color=colors[:6],width=.72)
        ax.axhline(1,color="#777777",lw=.8,ls="--")
        ax.set_xticks(range(6),
                      ["Fresh","Cached","SVD","Banded","Dense Chol.","Banded Chol."])
        ax.tick_params(axis="x",labelsize=7)
        ax.set(xlabel="Six GCV solvers (four independent series)",
               ylabel="Cold/warm total time")
        fig.subplots_adjust(left=.12,right=.97,top=.95,bottom=.25)
        _save(pub,fig,figure_dir/"gcv_repeated_search.pdf",save_pdf)

    sel=paper/"benchmarks/selection_coordinate_reference"
    paths=_read(sel/"criterion_score_paths.csv",
                ("n","d","mu","criterion","S","score","finite"))
    times=_read(sel/"selector_timings.csv",
                ("n","d","mu","criterion","policy","selection_median_s"))
    if paths:
        fig,ax=axis_factory(pub)
        for i,criterion in enumerate(CRITERIA):
            part=sorted((float(r["S"]),float(r["score"])) for r in paths
                        if int(r["n"])==60 and int(r["d"])==2
                        and float(r["mu"])==0 and r["criterion"]==criterion
                        and r["finite"].lower()=="true")
            if len(part)<5:
                raise ValueError(f"No full smoothness path for {criterion}")
            s=np.array([p[0] for p in part]); z=np.array([p[1] for p in part])
            # Never plot incomparable MLE, squared-error and information
            # criteria on a shared *raw* score axis.
            z=z-z.min()
            if z.max()>0: z/=z.max()
            ax.plot(s,z,color=colors[i],marker=MARKERS[i%4],
                    markersize=3.0,ls=STYLES[i%4],lw=1.3,
                    label=criterion.upper())
            ax.scatter([s[np.argmin(z)]],[0],s=19,color=colors[i],zorder=5)
        ax.set_xlim(-.01,1.01)
        ax.set(xlabel="Normalized smoothness S, including exact 1",
               ylabel="Score rescaled WITHIN criterion (0=minimum)")
        ax.legend(ncol=3,loc="upper center",bbox_to_anchor=(.5,-.20),
                  frameon=False)
        fig.subplots_adjust(left=.12,right=.97,top=.95,bottom=.32)
        _save(pub,fig,figure_dir/"criteria_with_mle_s_paths.pdf",save_pdf)

    if paths:
        # The corresponding *same 16 candidates* in log-penalty coordinates.
        # Exact endpoints 0 and infinity were SCORED above but are not
        # plottable on a finite logarithmic horizontal axis.
        fig,ax=axis_factory(pub)
        for i,criterion in enumerate(CRITERIA):
            complete=sorted(
                [(float(r["lambda"]),float(r["score"])) for r in paths
                 if int(r["n"])==60 and int(r["d"])==2
                 and float(r["mu"])==0 and r["criterion"]==criterion
                 and r["finite"].lower()=="true"],
                key=lambda item:item[0])
            finite=np.asarray([p[1] for p in complete])
            scale=float(finite.max()-finite.min())
            part=[(lam,(value-finite.min())/scale if scale else 0.)
                  for lam,value in complete if 0<lam<np.inf]
            ax.plot([p[0] for p in part],[p[1] for p in part],
                    color=colors[i],marker=MARKERS[i%4],
                    markersize=3.0,ls=STYLES[i%4],lw=1.3,
                    label=criterion.upper())
        ax.set_xscale("log")
        ax.set(xlabel=r"Penalty $\lambda$ (log scale; endpoints scored, not plotted)",
               ylabel="Score rescaled WITHIN criterion (0=minimum)")
        ax.legend(ncol=3,loc="upper center",bbox_to_anchor=(.5,-.20),
                  frameon=False)
        fig.subplots_adjust(left=.12,right=.97,top=.95,bottom=.32)
        _save(pub,fig,figure_dir/"criteria_with_mle_lambda_paths.pdf",save_pdf)

    if times:
        fig,ax=axis_factory(pub,ylog=True)
        policies=(("matched_lambda","Mapped penalty (reuse)"),
                  ("native_s","Native S (inversion)"),
                  ("log_lambda","Independent log penalty"))
        for k,(policy,label) in enumerate(policies):
            y=[]
            for criterion in CRITERIA:
                hits=[float(r["selection_median_s"])*1000 for r in times
                      if int(r["n"])==60 and int(r["d"])==2
                      and float(r["mu"])==0 and r["criterion"]==criterion
                      and r["policy"]==policy]
                if len(hits)!=1:
                    raise ValueError(f"Missing search timing {policy}/{criterion}")
                y.append(hits[0])
            ax.bar(np.arange(5)+.24*(k-1),y,width=.24,
                   color=colors[[1,3,5][k]],label=label)
        ax.set_xticks(range(5),[name.upper() for name in CRITERIA])
        ax.set(xlabel="Selection criterion (16 candidate penalties)",
               ylabel="Median selector time (ms)")
        ax.legend(ncol=2,frameon=False,fontsize=7,
                  loc="upper center",bbox_to_anchor=(.5,-.20))
        fig.subplots_adjust(left=.12,right=.97,top=.95,bottom=.32)
        _save(pub,fig,figure_dir/"criteria_with_mle_search_time.pdf",save_pdf)
