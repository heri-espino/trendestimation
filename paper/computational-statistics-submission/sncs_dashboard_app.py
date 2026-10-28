#!/usr/bin/env python3
"""Interactive SN Computer Science supplementary dashboard (archived data only).

    python -m pip install streamlit
    streamlit run paper/computational-statistics-submission/sncs_dashboard_app.py

The app never reoptimizes CV/GCV/AICc/BIC/MLE, retimes numerical solvers,
or fetches new series. It performs ONLY deterministic fits for one selected
archived lambda and mu, then draws the historical holdout or future
trend extension. Saved metrics and chosen penalties are not mutated.
"""
from __future__ import annotations

import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from contrast_theme import apply, OBSERVED, INK, TREND, FUTURE, GRID
from make_current_examples import load_series, extrapolate_tail, HOLDOUT, HORIZON
from make_selection_dashboards import month_after
from sncs_dashboard import INPUTS, METHODS, ORDERS, VERSIONS, read_results
from trendestimation import TrendSmoother

HERE=Path(__file__).resolve().parent
DATA=HERE/"data"
SOURCES={
    "co2_full":("noaa_mlo_monthly_1990_2026_09.csv","average_ppm",None),
    "co2_recent":("noaa_mlo_monthly_1990_2026_09.csv","average_ppm",120),
    "fedfunds_full":("fred_fedfunds_2010_2026_09.csv","value",None),
}
DISPLAY={"cv":"CV","gcv":"GCV","aicc":"AICc",
         "bic":"BIC","mle":"MLE","controlled":"Controlled S=0.86"}


def fit_saved_case(dataset:str, mode:str, d:int, method:str,kind:str):
    """Return plot primitives for exactly ONE archived case, never optimize."""
    from sncs_dashboard import read_results
    if dataset not in SOURCES or mode not in VERSIONS or d not in ORDERS or method not in METHODS:
        raise ValueError("Unrecognized archived analysis configuration")
    if kind not in ("holdout","future"):
        raise ValueError("Unknown time origin")
    results,_=read_results(dataset)
    row=results["records"][mode][f"d{d}_{method}"]
    source,column,recent=SOURCES[dataset]
    dates,y=load_series(DATA/source,column)
    if recent:
        dates,y=dates[-recent:],y[-recent:]
    if kind=="holdout":
        train=y[:-HOLDOUT]
        fit=TrendSmoother(len(train),order=d).fit(
            train,lambda_=float(row["holdout_lambda"]),
            mu=float(row["holdout_mu"]),
        ).trend
        ext=extrapolate_tail(fit,d,HOLDOUT)
        return dates,y,fit,ext,row
    fit=TrendSmoother(len(y),order=d).fit(
        y,lambda_=float(row["lambda"]),mu=float(row["mu"]),
    ).trend
    ext=extrapolate_tail(fit,d,HORIZON)
    return dates,y,fit,ext,row


def draw(dataset:str,mode:str,d:int,method:str,kind:str):
    dates,y,fit,ext,row=fit_saved_case(dataset,mode,d,method,kind)
    apply()
    fig,ax=plt.subplots(figsize=(10.4,4.5),layout="constrained")
    if kind=="holdout":
        cutoff=len(y)-HOLDOUT
        start=max(0,cutoff-60)
        ax.plot(dates[start:cutoff],y[start:cutoff],color=OBSERVED,lw=1.1,label="Training observations")
        ax.plot(dates[start:cutoff],fit[start:cutoff],color=TREND,lw=1.8,label="Archived-parameter PLS trend")
        ax.plot(dates[cutoff:],y[cutoff:],color=INK,lw=1.2,
                marker="o",ms=4,label="Held-out observations")
        ax.plot([dates[cutoff-1],*dates[cutoff:]],
                [fit[-1],*ext],color=FUTURE,lw=2,ls="--",
                label="Anchored trend extension")
        ax.axvline(dates[cutoff-1],color=GRID,ls=":")
        ax.set_title(f"Historical holdout — RMSE={row['rmse']:.3f}, MAE={row['mae']:.3f}")
    else:
        future=month_after(dates[-1],HORIZON)
        start=max(0,len(y)-60)
        ax.plot(dates[start:],y[start:],color=OBSERVED,lw=1.2,label="Observed")
        ax.plot(dates[start:],fit[start:],color=TREND,lw=1.8,label="Archived-parameter PLS trend")
        ax.plot([dates[-1],*future],[fit[-1],*ext],color=FUTURE,lw=2,ls="--",
                label="Deterministic trend extrapolation")
        ax.axvline(dates[-1],color=GRID,ls=":")
        ax.set_title("Future trend extension — not a probabilistic forecast")
    ax.set_ylabel("Observed units")
    ax.grid(alpha=.19)
    ax.legend(loc="best",fontsize=9)
    fig.autofmt_xdate()
    return fig,row


def main():
    import streamlit as st
    import pandas as pd
    st.set_page_config(page_title="Trendestimation | archived studies",
                       page_icon=None,layout="wide")
    st.title("Penalized trend estimation")
    st.caption("Supplementary dashboard for SN Computer Science · archived experiments only")
    with st.sidebar:
        dataset=st.selectbox("Series",tuple(INPUTS),format_func=lambda k:INPUTS[k])
        mode=st.radio("Reference difference mean",tuple(VERSIONS),
                      format_func=lambda x:"Fixed μ=0" if x=="zero"
                                  else "Training-derived μ",horizontal=False)
        d=st.select_slider("Difference order",options=ORDERS,value=2)
        method=st.selectbox("Selection method",METHODS,
                            format_func=lambda x:DISPLAY[x])
        kind=st.radio("Time origin",("holdout","future"),
                      format_func=lambda k:"Historical holdout" if k=="holdout"
                                  else "Future extension")
    saved,_=read_results(dataset)
    row=saved["records"][mode][f"d{d}_{method}"]
    a,b,c,d_col=st.columns(4)
    a.metric("Archived λ",f"{row['lambda']:.4g}")
    b.metric("Archived S",f"{row['s']:.3f}")
    c.metric("Reference μ",f"{row['mu']:.4g}")
    d_col.metric("Holdout RMSE",f"{row['rmse']:.3f}")
    fig,_=draw(dataset,mode,d,method,kind)
    st.pyplot(fig,use_container_width=True)
    png=io.BytesIO()
    fig.savefig(png,format="png",dpi=175,bbox_inches="tight")
    plt.close(fig)
    st.download_button("Download current figure (PNG)",png.getvalue(),
                       file_name=f"{dataset}_{mode}_d{d}_{method}_{kind}.png",
                       mime="image/png")
    st.subheader("All archived comparisons")
    records=[
        {"d":order,"Method":DISPLAY[selector],
         "μ":float(saved["records"][mode][f"d{order}_{selector}"]["mu"]),
         "λ":float(saved["records"][mode][f"d{order}_{selector}"]["lambda"]),
         "S":float(saved["records"][mode][f"d{order}_{selector}"]["s"]),
         "RMSE":float(saved["records"][mode][f"d{order}_{selector}"]["rmse"]),
         "MAE":float(saved["records"][mode][f"d{order}_{selector}"]["mae"])}
        for order in ORDERS for selector in METHODS
    ]
    table=pd.DataFrame(records)
    st.dataframe(table,use_container_width=True,hide_index=True)
    st.download_button("Download archived comparison (CSV)",
                       table.to_csv(index=False).encode("utf-8"),
                       file_name=f"{dataset}_{mode}_sncs_comparison.csv",
                       mime="text/csv")
    st.caption(
        "All penalty selections and recorded losses were obtained earlier. "
        "The curve shown here is recomputed deterministically at the saved "
        "λ and μ; no root search, criterion optimization, numerical benchmark "
        "or fresh data download takes place. CV/GCV/AICc/BIC and MLE use a "
        "conditional plug-in μ when requested. The single-origin holdout "
        "does not establish predictive superiority."
    )


if __name__=="__main__":
    main()
