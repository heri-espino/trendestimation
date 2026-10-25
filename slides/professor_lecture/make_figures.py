#!/usr/bin/env python3
"""Build reproducible SVG figures for the professor's Marp research lecture.

Usage from repository root:
    python slides/professor_lecture/make_figures.py
    python slides/professor_lecture/make_figures.py --smoke

Source-specific figures are either regenerated using trendestimation or
read from host benchmark CSVs. Never invent runtime observations.
No external network calls and no modification to paper/results or src/.
"""
from __future__ import annotations

import argparse
import csv
import json
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import binom

from trendestimation import TrendSmoother, score_lambda, select_lambda

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "figures"
BENCH = ROOT / "paper" / "benchmarks" / "results"
NAVY, BLUE, SKY, TEAL = "#122747", "#205fd4", "#61a5ff", "#138b94"
AMBER, RED, INK, GRID = "#db9a31", "#bf5268", "#334a67", "#e1eaf3"
PALETTE = [BLUE, TEAL, AMBER, RED, "#8064c9", "#617791"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.titlesize": 17, "axes.titleweight": "bold",
    "axes.labelcolor": INK, "axes.edgecolor": "#bbcadb",
    "axes.spines.top": False, "axes.spines.right": False,
    "text.color": NAVY, "xtick.color": INK, "ytick.color": INK,
    "grid.color": GRID, "grid.alpha": 0.85, "axes.grid": True,
    "svg.fonttype": "none", "figure.facecolor": "white",
    "axes.facecolor": "white", "savefig.facecolor": "white",
})
FIGURES = []


def axes(title, xlabel="time", ylabel="value", *, size=(10, 4.6)):
    fig, ax = plt.subplots(figsize=size)
    ax.set_title(title, loc="left", pad=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.7)
    return fig, ax


def save(name, fig, kind="deterministic", source="computed from seeded synthetic data"):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    FIGURES.append(dict(file=f"figures/{name}.svg", kind=kind, source=source))


def message(name, title, text):
    fig, ax = axes(title, "", "")
    ax.axis("off")
    ax.text(.5, .63, text, ha="center", va="center", transform=ax.transAxes,
            color=NAVY, fontsize=16, linespacing=1.7)
    ax.text(.5, .15, "No timings have been invented.", ha="center",
            transform=ax.transAxes, color=RED, fontsize=12)
    save(name, fig, kind="missing", source="no host benchmark CSV present")


def setup():
    t = np.arange(96, dtype=float)
    truth = .028 * t + 1.1 * np.sin(t / 11) + .38 * np.cos(t / 5.5)
    y = truth + np.random.default_rng(24021).normal(0, .43, len(t))
    models = {d: TrendSmoother(len(t), order=d) for d in (1, 2, 3, 4, 5)}
    return t, truth, y, models


def plot_signal(t, truth, y, models):
    fig, ax = axes("A latent trend is obscured by observation noise")
    ax.plot(t, y, "o", ms=3.6, alpha=.55, color=SKY, label="observations")
    ax.plot(t, truth, lw=3, color=NAVY, label="known synthetic signal")
    ax.legend(frameon=False, ncol=2); save("01_signal", fig)
    sm = models[2]
    fig, ax = axes("Fidelity term: fitted curve should explain observations")
    fit = sm.fit(y, lambda_=30).trend
    ax.plot(t, y, "o", ms=3, color=SKY, alpha=.35)
    ax.plot(t, fit, lw=3, color=BLUE)
    for k in range(0, 96, 8):
        ax.vlines(t[k], min(y[k], fit[k]), max(y[k], fit[k]), color=RED, lw=1.4)
    save("02_fidelity", fig)
    fig, ax = axes("Penalty term: differences should remain controlled", ylabel="second difference")
    for lam, color in [(0, SKY), (1, AMBER), (50, BLUE), (5000, TEAL)]:
        fit = sm.fit(y, lambda_=lam).trend
        ax.plot(t[:-2], np.diff(fit, n=2), color=color, lw=2,
                label=rf"$\lambda={lam:g}$")
    ax.axhline(0, color=INK, lw=.8); ax.legend(frameon=False, ncol=4)
    save("03_penalty", fig)
    fig, ax = axes("Same data, different penalty strengths")
    ax.scatter(t, y, s=10, color=SKY, alpha=.38)
    for lam, color in [(0.4, AMBER), (10, BLUE), (250, TEAL), (1e5, NAVY)]:
        ax.plot(t, sm.fit(y, lambda_=lam).trend, lw=2.7, color=color,
                label=rf"$\lambda={lam:g}$")
    ax.legend(frameon=False, ncol=4, fontsize=10); save("04_lambda_sweep", fig)
    fig, ax = axes("Equal S does not mean identical trend geometry")
    for d, color in zip((1, 2, 3, 4, 5), PALETTE):
        sm = models[d]
        lam = sm.lambda_for_smoothness(.78)
        ax.plot(t, sm.fit(y, lambda_=lam).trend, lw=2.3, color=color,
                label=f"d={d}, lambda={lam:.2g}")
    ax.legend(frameon=False, ncol=3, fontsize=10); save("05_order_comparison", fig)
    fig, ax = axes("Nonzero reference differences change the affine fit")
    for mu, color in [(-.03, AMBER), (0, BLUE), (.03, TEAL)]:
        ax.plot(t, sm.fit(y, lambda_=sm.lambda_for_smoothness(.83), mu=mu).trend,
                color=color, lw=2.8, label=f"mu={mu:+.2f}")
    ax.legend(frameon=False, ncol=3); save("06_mu_sweep", fig)
    fig, ax = axes("At infinite penalty: degree d vs. degree d-1")
    for d, color in [(1, AMBER), (2, BLUE), (3, TEAL)]:
        trend = models[d].fit(y, lambda_=np.inf, mu=.0015).trend
        ax.plot(t, trend, lw=2.7, color=color, label=f"d={d}, mu=0.0015")
    ax.legend(frameon=False); save("07_affine_limit", fig)
    fit = sm.fit(y, lambda_=sm.lambda_for_smoothness(.82)).trend
    fig, ax = axes("Residuals are not automatically independent noise", ylabel="residual")
    ax.axhline(0, color=NAVY, lw=1)
    ax.plot(t, y-fit, color=SKY, lw=1.5, marker="o", ms=3)
    save("08_residuals", fig)


def plot_differences(t, truth, y, models):
    for d in (1, 2, 3):
        fig, ax = axes(f"Order d={d}: the finite-difference stencil",
                       xlabel="index", ylabel=f"Delta^{d} y")
        ax.plot(np.arange(len(y)-d), np.diff(y, n=d),
                color=PALETTE[d-1], lw=1.8)
        ax.axhline(0, lw=.8, color=INK)
        save(f"09_diff_d{d}", fig)
    fig, ax = axes("The difference operator is sparse and banded",
                   xlabel="time index", ylabel="difference row", size=(8.3, 4.9))
    D = models[3].D
    ax.grid(False)
    ax.imshow(D[:18, :22], cmap="coolwarm", aspect="auto",
              vmin=-max(abs(D.flat)), vmax=max(abs(D.flat)))
    save("12_matrix_D", fig)
    fig, ax = axes("Binomial stencil coefficients", "position in stencil", "coefficient")
    for d in (1, 2, 3, 4, 5):
        ax.plot(np.arange(d+1), [(-1)**(d-k)*comb(d,k) for k in range(d+1)],
                marker="o", lw=1.6, label=f"d={d}")
    ax.axhline(0, color=INK, lw=.8);ax.legend(frameon=False, ncol=5)
    save("13_stencils", fig)
    fig, ax = axes("Unpenalized polynomial directions: ker(D_d)", "time", "scaled basis value")
    x = np.linspace(-1,1,96)
    for d, color in zip(range(4), PALETTE):
        ax.plot(t, x**d, color=color, lw=2.4,
                label=rf"t^{d}")
    ax.legend(frameon=False, ncol=4)
    save("14_kernel", fig)
    fig, ax = axes("As lambda grows, d=1 / 2 / 3 approach distinct nullspaces")
    ax.scatter(t, y, s=8, color=GRID)
    for d, color in [(1, AMBER), (2, BLUE), (3, TEAL)]:
        ax.plot(t, models[d].fit(y, lambda_=np.inf, mu=0).trend,
                color=color, lw=3, label=f"d={d}; degree <= {d-1}")
    ax.legend(frameon=False)
    save("15_polynomial_limit", fig)
    fig, ax = axes("Penalty energy decreases when smoothing increases", "lambda", "||D2 trend|| squared")
    lam = np.geomspace(1e-3, 1e6, 65)
    energy = [np.linalg.norm(models[2].D @ models[2].fit(y,lambda_=float(v)).trend)**2
              for v in lam]
    ax.semilogx(lam, energy, color=BLUE, lw=3)
    save("16_penalty_energy", fig)


def plot_spectral(t, truth, y, models):
    sm = models[2]
    vals = sm.eigenvalues[:sm.n-sm.order]
    fig, ax = axes("Positive eigenvalues of the penalty", "penalized mode", "eigenvalue")
    ax.semilogy(np.arange(1,len(vals)+1), vals, color=BLUE, lw=2.5)
    save("17_eigen_spectrum",fig)
    fig, ax=axes("Smoothing is mode-by-mode spectral attenuation",
                 "mode", "attenuation 1/(1+lambda delta)")
    for lam,color in [(0.1,AMBER),(10,BLUE),(1e3,TEAL),(1e5,NAVY)]:
        ax.plot(np.arange(1,len(vals)+1),1/(1+lam*vals),lw=2.3,
                color=color,label=f"lambda={lam:g}")
    ax.legend(frameon=False,ncol=4,fontsize=10)
    save("18_attenuation",fig)
    for lam,name in [(0.5,"19_hat_weak"),(500,"20_hat_strong")]:
        fig,ax=axes(f"Hat matrix: lambda={lam:g} (illustrative 36-point problem)",
                     "column","row",size=(7.2,4.8))
        tiny=TrendSmoother(36,2)
        Q=tiny.D.T@tiny.D
        H=np.linalg.inv(np.eye(36)+lam*Q)
        ax.imshow(H,cmap="Blues",aspect="auto")
        ax.grid(False);save(name,fig)
    lam=np.geomspace(1e-5,1e8,125)
    fig,ax=axes("Effective degrees of freedom decrease with lambda",
                "lambda","EDF = trace(H)")
    ax.semilogx(lam,[sm.degrees_of_freedom(float(l)) for l in lam],
                color=BLUE,lw=3)
    ax.axhline(2,color=TEAL,ls="--",label="d=2 limit")
    ax.legend(frameon=False);save("21_edf",fig)
    fig,ax=axes("Normalized smoothness increases from 0 to 1",
                "lambda","S(lambda)")
    ax.semilogx(lam,[sm.smoothness(float(l)) for l in lam],lw=3,color=BLUE)
    ax.axhline(.8,color=AMBER,ls="--",label="target S=0.8")
    ax.legend(frameon=False);save("22_smoothness",fig)
    fig,ax=axes("Guerrero's original S_G and normalized S differ",
                "lambda","smoothness")
    ax.semilogx(lam,[sm.smoothness(float(l)) for l in lam],color=BLUE,lw=2.7,label="S normalized")
    ax.semilogx(lam,[sm.smoothness(float(l),normalized=False) for l in lam],
                color=TEAL,lw=2.7,label="S_G, denominator n")
    ax.legend(frameon=False);save("23_two_s_indices",fig)
    fig,ax=axes("Normalized S by differencing order", "lambda","S(lambda)")
    for d,color in zip((1,2,3,4,5),PALETTE):
        ax.semilogx(lam,[models[d].smoothness(float(l)) for l in lam],
                    lw=2.3,color=color,label=f"d={d}")
    ax.legend(frameon=False,ncol=5);save("24_s_by_order",fig)
    fig,ax=axes("Derivative S'(lambda) is strictly positive",
                "lambda","S'(lambda)")
    derivative=[np.mean(vals/(1+l*vals)**2) for l in lam]
    ax.loglog(lam, derivative, color=BLUE,lw=2.7);save("25_s_derivative",fig)
    fig,ax=axes("Derivative with respect to log(lambda) vanishes in both tails",
                "lambda","dS / dlog(lambda)")
    slope=np.asarray(lam)*np.asarray(derivative)
    ax.semilogx(lam,slope,color=TEAL,lw=2.7);save("26_log_s_derivative",fig)
    s_grid=np.linspace(.02,.98,90)
    inverse=np.asarray([sm.lambda_for_smoothness(float(s)) for s in s_grid])
    fig,ax=axes("The inverse lambda(s) spans many orders of magnitude",
                "normalized s","lambda(s)")
    ax.semilogy(s_grid,inverse,color=BLUE,lw=3);save("27_inverse",fig)
    fig,ax=axes("Equal steps in S are unequal steps in log(lambda)",
                "lambda","S(lambda)")
    ax.semilogx(lam,[sm.smoothness(float(l)) for l in lam],lw=2.2,color=SKY)
    for s in np.linspace(.1,.9,9):
        x=sm.lambda_for_smoothness(float(s))
        ax.scatter([x],[s],color=BLUE,s=38)
        ax.vlines(x,0,s,color=GRID,linewidth=1)
    save("28_s_grid",fig)
    fig,ax=axes("Spectral residual energy and trace are scalar sums",
                "lambda","normalized value")
    energy=[np.sum((l*vals/(1+l*vals))**2 * (sm._prepare(y,0.)[3][:len(vals)]**2))
            for l in lam]
    ax.semilogx(lam,np.asarray(energy)/max(energy),color=BLUE,lw=2.7,label="relative RSS")
    ax.semilogx(lam,[sm.degrees_of_freedom(float(l))/sm.n for l in lam],
                color=TEAL,lw=2.7,label="EDF/n")
    ax.legend(frameon=False);save("29_rss_edf",fig)


def plot_selection(t, truth, y, models):
    sm=models[2]
    lam=np.geomspace(1e-5,1e7,140)
    cv=np.asarray([score_lambda(sm,y,lambda_=float(l),criterion="cv",mu=0.0) for l in lam])
    s=np.asarray([sm.smoothness(float(l)) for l in lam])
    fig,ax=axes("Ordinary LOOCV as a function of log-penalty","lambda","CV")
    ax.semilogx(lam,cv,color=BLUE,lw=2.7);save("30_cv_lambda",fig)
    fig,ax=axes("Exactly the same CV score as a function of normalized S","s","CV")
    ax.plot(s,cv,color=TEAL,lw=2.7);save("31_cv_s",fig)
    fig,ax=axes("CV minima in two coordinates represent the same model",
                "s","CV (score value)")
    ax.plot(s,cv,color=BLUE,lw=2.6)
    k=int(np.nanargmin(cv));ax.scatter([s[k]],[cv[k]],s=90,color=AMBER,zorder=3,label="same candidate")
    ax.legend(frameon=False);save("32_cv_minimum",fig)
    fig,ax=axes("Criterion profiles: scores have different units",
                "lambda","score centered and scaled (display only)")
    for c,color in zip(("cv","gcv","aicc","bic"),PALETTE):
        values=np.array([score_lambda(sm,y,lambda_=float(l),criterion=c,mu=0.0) for l in lam])
        ok=np.isfinite(values)
        if ok.sum()>3:
            low=np.nanmin(values[ok]); scale=np.nanpercentile(values[ok],90)-low
            if scale==0:scale=1
            ax.semilogx(lam,(values-low)/scale,color=color,lw=2.2,label=c.upper())
    ax.set_ylim(-.08,2.5);ax.legend(frameon=False,ncol=4)
    save("33_criteria",fig)
    fig,ax=axes("Four selection rules, one synthetic series")
    ax.scatter(t,y,s=10,color=SKY,alpha=.38,label="observations")
    ax.plot(t,truth,color=NAVY,ls="--",lw=2,label="known true signal")
    for c,color in zip(("cv","gcv","aicc","bic"),PALETTE):
        selected=select_lambda(sm,y,criterion=c,mu=0.0)
        fit=sm.fit(y,lambda_=selected.lambda_).trend
        ax.plot(t,fit,lw=2.15,color=color,label=c.upper())
    ax.legend(frameon=False,ncol=3,fontsize=10)
    save("34_selected_trends",fig)
    tiny=TrendSmoother(38,2)
    lamb=16.
    H=np.linalg.inv(np.eye(38)+lamb*(tiny.D.T@tiny.D))
    fig,ax=axes("LOOCV uses pointwise leverage 1-H[i,i]",
                 "observation index","hat diagonal")
    ax.bar(np.arange(38),np.diag(H),color=BLUE,width=.75)
    ax.axhline(np.trace(H)/38,color=AMBER,ls="--",label="mean leverage (GCV)")
    ax.legend(frameon=False);save("35_leverage",fig)
    fig,ax=axes("Training residual vs. leave-one-out residual",
                 "observation index","residual")
    yy=y[:38]
    # This is a distinct short-sample demonstration with its own fit.
    shortfit=tiny.fit(yy,lambda_=lamb,mu=0).trend
    r=yy-shortfit
    ax.plot(r,lw=2,color=BLUE,label="training residual")
    ax.plot(r/(1-np.diag(H)),lw=2,color=AMBER,label="LOO residual")
    ax.legend(frameon=False);save("36_loo_residuals",fig)
    fig,ax=axes("Chronological holdout is a different question",
                 "time index","observed value")
    ax.plot(t,y,color=SKY,lw=1.7)
    ax.axvspan(0,66,facecolor=BLUE,alpha=.09,label="train history")
    ax.axvspan(67,95,facecolor=AMBER,alpha=.12,label="future holdout")
    ax.axvline(67,color=RED,ls="--")
    ax.legend(frameon=False);save("37_chronological_split",fig)
    mle=np.asarray([score_lambda(sm,y,lambda_=float(l),criterion="mle",mu=0.0)
                    for l in lam])
    fig,ax=axes("Conditional Gaussian marginal-likelihood score",
                 "lambda","negative profile log-likelihood")
    ax.semilogx(lam,mle,color=BLUE,lw=3);save("38_mle_profile",fig)
    eig,basis=np.linalg.eigh(sm.D.T@sm.D)
    positive=eig>1e-9
    ev=eig[positive];V=basis[:,positive]
    p=binom(np.arange(len(y)),2)
    z=V.T@y;b=V.T@p
    muhat=[]
    for l in lam:
        w=l*ev/(1+l*ev)
        muhat.append(float(np.sum(w*b*z)/np.sum(w*b*b)))
    fig,ax=axes("Deferred research: conditional closed-form mu-hat(lambda)",
                "lambda","mu-hat(lambda)")
    ax.semilogx(lam,muhat,color=TEAL,lw=3)
    save("39_mu_profile",fig,kind="analytical illustration",
         source="profile formula only; no released joint optimizer")
    mu_scan=np.linspace(-.025,.025,90)
    l_scan=np.geomspace(.005,5e3,100)
    surface=np.empty((len(mu_scan),len(l_scan)))
    for i,mu in enumerate(mu_scan):
        for j,l in enumerate(l_scan):
            w=l*ev/(1+l*ev)
            T=np.sum(w*(z-b*mu)**2)/len(ev)
            surface[i,j]=len(ev)*np.log(max(T,1e-300))-np.log(w).sum()
    fig,ax=axes("Future joint-profile surface: analytical illustration",
                 "log10(lambda)","mu",size=(9,4.7))
    ax.grid(False)
    ax.contourf(np.log10(l_scan),mu_scan,surface,levels=24,cmap="Blues_r")
    save("40_joint_mle_surface",fig,kind="analytical illustration",
         source="analytical likelihood surface; not a tested joint estimator")
    fig,ax=axes("Analytical inversion strategies seek the same target",
                 "iteration (conceptual)","log(lambda)")
    xstar=np.log(sm.lambda_for_smoothness(.75))
    for i,(name,col) in enumerate([("bracketed bisection",BLUE),("safeguarded Newton",TEAL),
                                    ("safeguarded secant",AMBER)]):
        x=xstar+(4.0/(np.arange(1,12)**(1.2+i*.5)))*(-1)**np.arange(1,12)
        ax.plot(np.arange(len(x)),x,color=col,marker="o",lw=1.9,label=name)
    ax.axhline(xstar,color=NAVY,ls="--",label="unique root")
    ax.legend(frameon=False,ncol=2,fontsize=10)
    save("41_root_methods",fig,kind="schematic",
         source="illustrative trajectories, not observed iteration logs")


def plot_computation(t, truth, y, models):
    ns=np.linspace(20,300,120)
    fig,ax=axes("Leading-order arithmetic models, not timed observations",
                "n","relative operations (log scale)")
    ax.loglog(ns,ns**3,color=RED,label="repeated dense, one fit")
    ax.loglog(ns,ns**2*30,color=BLUE,label="spectral, M=30 reconstruction")
    ax.loglog(ns,ns*2**2*30,color=TEAL,label="banded, d=2, M=30")
    ax.legend(frameon=False,fontsize=10)
    save("42_arithmetic_costs",fig,kind="complexity schematic",
         source="Big-O models only; arbitrary multiplicative constants")
    Ms=np.arange(1,130)
    fig,ax=axes("Why preprocessing changes the cost crossover",
                "number of fitted trends M","arbitrary operation units")
    ax.plot(Ms,100+Ms*2.5,color=BLUE,lw=3,label="SVD setup + repeated curves")
    ax.plot(Ms,Ms*11,color=RED,lw=3,label="repeated dense solves")
    ax.plot(Ms,20+Ms*1.9,color=TEAL,lw=3,label="banded solve model")
    ax.legend(frameon=False,fontsize=10)
    save("43_crossover_schematic",fig,kind="complexity schematic",
         source="illustrative cost model, not measured performance")
    Ms=np.arange(1,130)
    fig,ax=axes("Scalar trace vs reconstructed trends after SVD",
                "candidate count M","model operations, normalized")
    ax.plot(Ms,Ms*96,color=TEAL,lw=3,label="trace O(Mn)")
    ax.plot(Ms,Ms*96**2,color=BLUE,lw=3,label="full fits O(M n²)")
    ax.set_yscale("log");ax.legend(frameon=False)
    save("44_trace_vs_fit",fig,kind="complexity schematic",
         source="operation growth only, no observed wall times")
    dorders=range(1,11);ratios=[]
    for d in dorders:
        check=TrendSmoother(50,d)
        ev=check.eigenvalues[:50-d]
        ratios.append(float(np.max(ev)/np.min(ev)))
    fig,ax=axes("Higher differencing orders worsen conditioning",
                "difference order d","positive-spectrum condition ratio")
    ax.semilogy(list(dorders),ratios,color=BLUE,marker="o",lw=2.7)
    save("45_conditioning",fig,source="n=50; eigenvalue condition ratio from SVD")
    fig,ax=axes("Spectral vs direct equations: a numerical diagnostic",
                "d (difference order)","maximum absolute fit discrepancy")
    differences=[]
    z=np.random.default_rng(24021).normal(size=50)
    for d in dorders:
        obj=TrendSmoother(50,d)
        l=obj.lambda_for_smoothness(.86)
        out=obj.fit(z,lambda_=l,mu=0).trend
        direct=np.linalg.solve(np.eye(50)+l*(obj.D.T@obj.D),z)
        differences.append(max(float(np.max(np.abs(out-direct))),1e-17))
    ax.semilogy(list(dorders),differences,color=AMBER,marker="o",lw=2.7)
    save("46_numeric_discrepancy",fig,source="n=50 seed=24021 S=.86; direct normal-equation comparator")


def plot_host_timings():
    for name,filename,short in (
        ("47_measured_full","full_fit_timings.csv","full-fit trends"),
        ("48_measured_trace","trace_timings.csv","EDF/trace profiles"),
    ):
        path=BENCH/filename
        if not path.exists():
            message(name,f"Host measurements: {short}",
                    "Benchmark CSV not found on this machine.\n"
                    "Run the repository's paper benchmark suite,\n"
                    "then regenerate these slide figures.")
            continue
        with path.open(encoding="utf-8",newline="") as handle:
            rows=list(csv.DictReader(handle))
        if not rows:
            message(name,f"Host measurements: {short}","CSV is empty; no comparison plotted.")
            continue
        preferred=64 if "full" in name else 32
        candidates=[r for r in rows if int(r.get("M",0))==preferred and int(r.get("d",2))==2]
        if "full" in name:
            candidates=[r for r in candidates if abs(float(r.get("mu",0)))<1e-12]
        if not candidates:
            message(name,f"Host measurements: {short}",
                    f"CSV present but M={preferred}, d=2 case not available.\n"
                    "Rerun with the quick/full preset.")
            continue
        names=sorted({r["method"] for r in candidates})
        nvalues=sorted({int(r["n"]) for r in candidates})
        fig,ax=axes(f"Measured host timing: {short} (M={preferred})",
                    "n","end-to-end milliseconds",size=(10,4.8))
        for method,color in zip(names,PALETTE):
            series=[]
            for n in nvalues:
                found=[r for r in candidates if int(r["n"])==n and r["method"]==method]
                series.append(float(found[0]["total_median_s"])*1e3 if found else np.nan)
            ax.plot(nvalues,series,marker="o",lw=2,color=color,
                    label=method.replace("_"," "))
        ax.set_yscale("log");ax.legend(frameon=False,ncol=2,fontsize=10)
        save(name,fig,kind="host measured",
             source=f"{path.relative_to(ROOT)}; local CSV, includes setup")


def plot_real_data():
    try:
        import pandas as pd
        import statsmodels.api as sm
        raw=sm.datasets.co2.load_pandas().data["co2"].dropna()
        monthly=raw.loc["1990":"1999"].resample("MS").mean().interpolate()
        if len(monthly)!=120:
            raise ValueError(f"expected 120 monthly values, got {len(monthly)}")
        y=monthly.to_numpy()
        t=np.arange(len(y))
        fig,ax=axes("Mauna Loa: historical monthly CO2, 1990–1999",
                    "month index","CO2 (ppm)")
        ax.plot(t,y,color=SKY,lw=1.5,label="observed monthly concentration")
        colors=[BLUE,TEAL,AMBER,RED]
        for d,color in zip((2,3,4,5),colors):
            solver=TrendSmoother(len(y),d)
            lam=solver.lambda_for_smoothness(.86)
            fit=solver.fit(y,lambda_=lam,mu=0.0).trend
            ax.plot(t,fit,color=color,lw=2.6,label=f"d={d}, S=0.86")
        ax.legend(frameon=False,ncol=2,fontsize=10)
        save("49_mauna_loa",fig,kind="observed data",
             source="statsmodels.datasets.co2 weekly observations aggregated to monthly means")
    except (ImportError,ValueError,KeyError) as exc:
        message("49_mauna_loa","Real observations: Mauna Loa",
                "Optional statsmodels CO2 dataset unavailable.\n"
                "Install statsmodels to render the observed-data figure.\n"
                f"Reason: {type(exc).__name__}")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke",action="store_true",
                        help="generate a minimal pair for CI")
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    t,truth,y,models=setup()
    if args.smoke:
        fig,ax=axes("Reproducible smoke figure")
        ax.plot(t,y,color=BLUE)
        save("00_smoke",fig)
    else:
        plot_signal(t,truth,y,models)
        plot_differences(t,truth,y,models)
        plot_spectral(t,truth,y,models)
        plot_selection(t,truth,y,models)
        plot_computation(t,truth,y,models)
        plot_host_timings()
        plot_real_data()
    manifest={
        "generator":"slides/professor_lecture/make_figures.py",
        "reproducibility_seed":24021,
        "count":len(FIGURES),
        "figures":FIGURES,
        "warning":"Complexity and root-method schematics are not measured runtimes.",
    }
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",
                                       encoding="utf-8")
    print(f"Generated {len(FIGURES)} SVGs in {OUT}")
    missing=[r["file"] for r in FIGURES if not (OUT/r["file"].removeprefix("figures/")).exists()]
    if missing:
        raise RuntimeError(f"Missing outputs: {missing}")


if __name__=="__main__":
    main()
