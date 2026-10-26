"""Regenerate journal vector PDF + web SVG for the full-S backend factorial.

Use the actual archived raw CSV tables, not hardcoded timing measurements.
All plots use pinned AwesomeFigures and the exact Springer publication_context
already validated in render_awesomefigures.py.

python paper/figures/render_full_s_factorial.py
"""
from __future__ import annotations

import csv
from pathlib import Path
from runpy import run_path
import matplotlib.pyplot as plt
import numpy as np

PAPER=Path(__file__).resolve().parents[1]
DIR=PAPER/"figures"
DATA=PAPER/"benchmarks"/"full_s_reference"
CRITERIA=("cv","gcv","aicc","bic","mle")
METHODS=("dense_fresh","dense_cached","general_banded",
         "dense_cholesky","banded_cholesky","eigh","svd")
LABELS=("Dense fresh","Dense cached","General banded",
        "Dense Cholesky","Banded Cholesky","Eigendecomp.","SVD")


def csv_rows(name):
    source=DATA/name
    if not source.is_file():
        raise FileNotFoundError(
            f"Missing real study {source}. Run the full-S benchmark first.")
    with source.open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))


def save(pub,fig,target,original_save):
    DIR.mkdir(parents=True,exist_ok=True)
    with plt.rc_context({"svg.fonttype":"none"}):
        fig.savefig(DIR/(target+".svg"),format="svg")
    original_save(pub,fig,DIR/(target+".pdf"))
    print("[full-S AwesomeFigures]",target,"PDF/SVG")


def make_figures():
    style=run_path(str(DIR/"render_awesomefigures.py"))
    rows=csv_rows("full_grid_summary.csv")
    detailed=csv_rows("candidate_scores_and_times.csv")
    grid=csv_rows("s_lambda_grid.csv")
    palette=style["COLORS"]
    with style["publication_context"]() as pub:
        axis=style["_axis"]
        original_save=style["_save"]
        for criterion in CRITERIA:
            # Strict full-grid comparison: exclude a backend if ANY of its
            # 15 finite interior targets is inaccurate or undefined.
            fig,ax=axis(pub,ylog=True)
            for i,(method,label) in enumerate(zip(METHODS,LABELS)):
                subset={int(r["d"]):r for r in rows
                        if r["criterion"]==criterion and r["method"]==method
                        and int(r["n"])==24 and float(r["mu"])==0
                        and int(r["seed"])==20261026}
                xs=[];times=[]
                for d in range(6):
                    r=subset.get(d)
                    xs.append(d)
                    times.append(
                        1000*(float(r["setup_s"])+float(r["total_finite_eval_s"]))
                        if r and r["all_interior_valid"]=="True" else np.nan)
                ax.plot(xs,times,marker=("o","s","^","D")[i%4],
                        ls=("-","--","-.",":")[i%4],
                        markersize=3,lw=1.35,
                        color=palette[i%len(palette)],label=label)
            ax.set_xticks(range(6))
            ax.set(xlabel="Difference order d (full 0 < S < 1 grid)",
                   ylabel="Median total valid-grid runtime (ms)")
            ax.set_title(f"{criterion.upper()}: seven backend implementations")
            ax.legend(ncol=3,fontsize=7.0,frameon=False,
                      loc="upper center",bbox_to_anchor=(.5,-.23))
            fig.subplots_adjust(left=.12,right=.97,top=.92,bottom=.36)
            save(pub,fig,f"full_s_time_{criterion}",original_save)

        # Fraction valid across ALL 15 positive finite S candidates for
        # fixed mu=0, observed d=0..5, each criterion. MLE d0 is N/A.
        for criterion in ("gcv","mle"):
            vals=np.full((len(METHODS),6),np.nan)
            for i,method in enumerate(METHODS):
                for d in range(6):
                    row=next((r for r in rows
                              if int(r["n"])==24 and int(r["seed"])==20261026
                              and r["method"]==method and r["criterion"]==criterion
                              and float(r["mu"])==0 and int(r["d"])==d),None)
                    if row:
                        vals[i,d]=int(row["valid_points"])/15
            fig,ax=axis(pub)
            im=ax.imshow(vals,aspect="auto",vmin=0,vmax=1,cmap="Blues")
            ax.set_xticks(range(6),range(6))
            ax.set_yticks(range(7),LABELS)
            ax.set(xlabel="Difference order d",
                   title=f"{criterion.upper()}: numerically agreeing finite-S points")
            for i in range(7):
                for d in range(6):
                    if np.isfinite(vals[i,d]):
                        ax.text(d,i,f"{int(round(15*vals[i,d]))}/15",
                                ha="center",va="center",fontsize=7,
                                color="white" if vals[i,d]>.65 else "black")
                    else:
                        ax.text(d,i,"N/A",ha="center",va="center",fontsize=7)
            fig.colorbar(im,ax=ax,shrink=.78,label="Fraction of validated grid")
            fig.subplots_adjust(left=.28,right=.94,top=.91,bottom=.19)
            save(pub,fig,f"full_s_validity_{criterion}",original_save)

        for mu,suffix in ((0.,"mu0"),(.15,"mu015")):
            fig,ax=axis(pub)
            for i,criterion in enumerate(CRITERIA):
                selections=[]
                for d in range(6):
                    r=next((r for r in rows if int(r["n"])==24
                            and int(r["seed"])==20261026
                            and int(r["d"])==d and float(r["mu"])==mu
                            and r["method"]=="svd"
                            and r["criterion"]==criterion),None)
                    selections.append(float(r["selected_S"]) if r else np.nan)
                ax.plot(range(6),selections,marker=("o","s","^","D")[i%4],
                        markersize=4,lw=1.45,ls=("-","--","-.",":")[i%4],
                        color=palette[i%len(palette)],label=criterion.upper())
            ax.set_ylim(-.03,1.03)
            ax.set_xticks(range(6))
            ax.set(xlabel="Difference order d",
                   ylabel="Selected normalized smoothness S")
            ax.set_title(f"Full 17-candidate grid; fixed mu={mu:g}")
            ax.legend(ncol=3,frameon=False,
                      loc="upper center",bbox_to_anchor=(.5,-.2))
            fig.subplots_adjust(left=.12,right=.97,top=.94,bottom=.32)
            save(pub,fig,"full_s_selected_"+suffix,original_save)

        # This chart shows the price of seeking a S extremely close to 1,
        # including the special *exact* S=1 limit as a textual note.
        fig,ax=axis(pub,ylog=True)
        for d in range(6):
            series=sorted((float(r["S"]),float(r["lambda_"]))
                          for r in grid if int(r["n"])==24
                          and int(r["d"])==d
                          and not r["is_endpoint"]=="True")
            # A linear S axis collapses 0.9999 and 0.999999999999
            # into the same pixel. Plot -log10(1-S) to resolve the tail.
            ax.plot([-np.log10(1-s) for s,lam in series],
                    [lam for s,lam in series],
                    marker="o",markersize=2.4,lw=1.25,
                    color=palette[d%len(palette)],label=f"d={d}")
        ax.set_xlim(0,12.4)
        ax.set_xticks([0,1,2,3,4,6,12],
                      ["0","0.9","0.99","0.999","0.9999","0.999999","1-1e-12"])
        ax.tick_params(axis="x",labelsize=7)
        ax.set(xlabel="S targets (tail-expanded -log10(1-S) axis)",
               ylabel="Mapped finite penalty lambda (log scale)")
        ax.legend(ncol=3,loc="upper center",bbox_to_anchor=(.5,-.2),
                  frameon=False)
        ax.text(.98,.98,"Exact S=1: lambda=infinity (not on log axis)",
                ha="right",va="top",transform=ax.transAxes,fontsize=7)
        fig.subplots_adjust(left=.14,right=.97,top=.95,bottom=.34)
        save(pub,fig,"full_s_lambda_tail",original_save)

    print("[full-S AwesomeFigures] from",len(detailed),"actual measured candidates")


if __name__=="__main__":
    make_figures()
