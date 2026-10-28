#!/usr/bin/env python3
r"""Reproducible 4x6 PLS dashboard: difference orders × selectors × reference means.

Run from repository root (Windows PowerShell):
    python paper\computational-statistics-submission\make_selection_dashboards.py

Frozen NOAA/FRED inputs, no downloads. Outputs go to figures/ and data/.
Every holdout model (mu, lambda and trend) uses ONLY its training prefix.
The dashed segments use a separately defined local-polynomial extrapolation;
PLS itself is a two-sided historical smoother, NOT a forecasting model.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from trendestimation import TrendSmoother, select_lambda
from contrast_theme import (
    apply as apply_contrast, METHODS as CONTRAST_METHODS,
    OBSERVED, INK, TREND, FUTURE, GRID, SERIES as CONTRAST_SERIES,
    ORDER_MARKERS,
)
apply_contrast()
from make_current_examples import (
    CONTROLLED_S, HORIZON, HOLDOUT, ORDERS, TARGET_S,
    extrapolate_tail, load_series,
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGURES = HERE / "figures"
SELECTORS = ("cv", "gcv", "aicc", "bic", "mle", "controlled")
MU_MODES = ("zero", "data")
SERIES = (
    ("co2_full", "Mauna Loa CO2 (ppm)",
     "noaa_mlo_monthly_1990_2026_09.csv", "average_ppm", None),
    ("co2_recent", "Mauna Loa CO2 — last 120 months (ppm)",
     "noaa_mlo_monthly_1990_2026_09.csv", "average_ppm", 120),
    ("fedfunds_full", "US effective federal funds rate (%)",
     "fred_fedfunds_2010_2026_09.csv", "value", None),
)
PALETTE = {"observed": OBSERVED, "training": INK,
           "trend": TREND, "future": FUTURE, "holdout": INK}
METHOD_COLORS = CONTRAST_METHODS
SHORT = {"cv":"CV", "gcv":"GCV", "aicc":"AICc", "bic":"BIC",
         "mle":"MLE", "controlled":f"Controlled S={CONTROLLED_S:.2f}"}


def month_after(last: date, months: int) -> list[date]:
    """Calendar-month boundaries, from the following month onward."""
    start = 12 * last.year + last.month - 1
    return [
        date((start + step)//12, (start + step)%12 + 1, 1)
        for step in range(1, months + 1)
    ]


def effective_mu(model: TrendSmoother, y: np.ndarray, mode: str) -> float:
    """Conditional reference difference mean, estimated on supplied window only."""
    if mode == "zero":
        return 0.0
    if mode == "data":
        return float(np.mean(model.D @ y))
    raise ValueError(f"Unknown mu mode: {mode}")


def fitted_selection(
    observations: np.ndarray, order: int, mode: str,
) -> dict:
    """Fit six options from identical S-grid candidate penalties.

    MLE with mode='data' explicitly uses the public MLE plug-in interface.
    CV/GCV/AICc/BIC use its NUMERIC value conditionally; this is not
    an exact re-estimated-mean LOOCV or joint MLE.
    """
    model = TrendSmoother(len(observations), order=order)
    mu = effective_mu(model, observations, mode)
    penalties = np.asarray(
        [model.lambda_for_smoothness(float(s)) for s in TARGET_S],
        dtype=float,
    )
    response: dict[str, dict] = {}
    for method in SELECTORS:
        if method == "controlled":
            lam = float(model.lambda_for_smoothness(CONTROLLED_S))
            score = None
            millis = None
        else:
            start = perf_counter()
            selection = select_lambda(
                model, observations, criterion=method,
                mu="data" if mode == "data" and method == "mle" else mu,
                search_space="lambda", grid=penalties, method="grid",
            )
            millis = float(1000.0 * (perf_counter() - start))
            lam, score = float(selection.lambda_), float(selection.score)
        fit = model.fit(observations, lambda_=lam, mu=mu)
        if not np.isfinite(fit.trend).all() or not (0 <= fit.smoothness <= 1):
            raise ArithmeticError(f"Nonfinite fit for {order}, {mode}, {method}")
        response[method] = {
            "d": order, "method": method, "mu_mode": mode, "mu": mu,
            "lambda": lam, "s": float(fit.smoothness),
            "score": score, "conditional_fit": np.asarray(fit.trend, dtype=float),
            "criterion_ms_reusing_svd_and_grid": millis,
            "candidate_count": len(penalties) if score is not None else 0,
        }
    return response


def analyze(dates: list[date], series: np.ndarray, mode: str) -> dict:
    """Train/test isolation: full-sample display and historical holdout."""
    if len(series) <= HOLDOUT + 36:
        raise ValueError("Insufficient observations for 12-month holdout")
    train = series[:-HOLDOUT]
    records: dict[tuple[int, str], dict] = {}
    for order in ORDERS:
        full = fitted_selection(series, order, mode)
        prefix = fitted_selection(train, order, mode)
        for method in SELECTORS:
            item, previous = full[method], prefix[method]
            holdout_prediction = extrapolate_tail(
                previous["conditional_fit"], order, HOLDOUT,
            )
            future_prediction = extrapolate_tail(
                item["conditional_fit"], order, HORIZON,
            )
            loss = holdout_prediction - series[-HOLDOUT:]
            item["holdout_mu"] = previous["mu"]
            item["holdout_lambda"] = previous["lambda"]
            item["holdout_s"] = previous["s"]
            item["holdout_fit"] = previous["conditional_fit"]
            item["holdout_prediction"] = holdout_prediction
            item["extrapolation"] = future_prediction
            item["rmse"] = float(np.sqrt(np.mean(loss * loss)))
            item["mae"] = float(np.mean(np.abs(loss)))
            if not (np.isfinite(item["rmse"]) and np.isfinite(item["mae"])):
                raise ArithmeticError("Nonfinite holdout performance")
            records[(order, method)] = item
    return {"mode": mode, "dates": dates, "y": series, "records": records}


def _save(fig: plt.Figure, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf", "svg", "png"):
        fig.savefig(FIGURES / f"{name}.{extension}", dpi=170,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_dashboard(data: dict, dataset: str, title: str, kind: str) -> str:
    """24 panels: rows=orders 1–4, columns=six methods."""
    records = data["records"]
    dates, observed = data["dates"], data["y"]
    mode = data["mode"]
    future = month_after(dates[-1], HORIZON)
    fig, axes = plt.subplots(
        4, 6, figsize=(23, 14.2), sharex="col",
        constrained_layout=True,
    )
    for i, order in enumerate(ORDERS):
        for j, method in enumerate(SELECTORS):
            ax = axes[i,j]
            row = records[(order, method)]
            if kind == "holdout":
                visible = 48
                origin = dates[-HOLDOUT-1]
                ax.plot(dates[-HOLDOUT-visible:-HOLDOUT],
                        observed[-HOLDOUT-visible:-HOLDOUT],
                        color=PALETTE["observed"], lw=1.08)
                ax.plot(dates[-HOLDOUT-visible:-HOLDOUT],
                        row["holdout_fit"][-visible:],
                        color=PALETTE["trend"], lw=1.5)
                ax.plot(dates[-HOLDOUT:], observed[-HOLDOUT:],
                        color=PALETTE["holdout"], lw=1.2,
                        marker="o", ms=2.4)
                ax.plot([origin, *dates[-HOLDOUT:]],
                        [row["holdout_fit"][-1], *row["holdout_prediction"]],
                        color=PALETTE["future"], ls="--", lw=1.7)
                ax.axvline(origin, color=GRID, ls=":", lw=1)
                note = f"RMSE {row['rmse']:.2f}  MAE {row['mae']:.2f}"
            elif kind == "future":
                visible = 60
                ax.plot(dates[-visible:], observed[-visible:],
                        color=PALETTE["observed"], lw=1.0)
                ax.plot(dates[-visible:], row["conditional_fit"][-visible:],
                        color=PALETTE["trend"], lw=1.55)
                ax.plot([dates[-1], *future],
                        [row["conditional_fit"][-1], *row["extrapolation"]],
                        color=PALETTE["future"], ls="--", lw=1.7)
                ax.axvline(dates[-1], color="#64748b", ls=":", lw=1)
                note = f"S={row['s']:.3f}; λ={row['lambda']:.3g}"
            else:
                raise ValueError(kind)
            if i == 0:
                ax.set_title(SHORT[method], size=12, fontweight="bold")
            if j == 0:
                ax.set_ylabel(f"d={order}", fontweight="bold", size=12)
            ax.text(.02,.95,note,ha="left",va="top",transform=ax.transAxes,
                    fontsize=8.4,color=INK,
                    bbox={"facecolor":"white","edgecolor":"none","alpha":.82})
            ax.grid(alpha=.16)
            if i != len(ORDERS)-1:
                ax.tick_params(labelbottom=False)
            else:
                ax.tick_params(axis="x",rotation=20,labelsize=8)
            ax.tick_params(axis="y",labelsize=8)
    mode_title = "μ = 0 (fixed)" if mode == "zero" else "μ = mean(D_d y) (training plug-in)"
    purpose = ("12-month single-origin historical holdout"
               if kind == "holdout" else
               "12-month future trend-only extrapolation (not forecast)")
    fig.suptitle(f"{title}\n{purpose}  |  {mode_title}",
                 fontsize=17, fontweight="bold")
    name = f"{dataset}_dashboard_{kind}_mu_{mode}"
    _save(fig, name)
    return name


def plot_summary(data: dict, dataset: str, title: str) -> str:
    records=data["records"]
    fig, axes=plt.subplots(2,2,figsize=(11.7,8.1), constrained_layout=True)
    specs=(
        ("lambda", "Selected penalty λ (log scale)"),
        ("s", "Normalized smoothness S(λ)"),
        ("rmse", "Historical 12-month RMSE"),
        ("mae", "Historical 12-month MAE"),
    )
    for ax, (field, label) in zip(axes.ravel(), specs):
        for method in SELECTORS:
            values=[records[(order,method)][field] for order in ORDERS]
            ax.plot(ORDERS, values, marker="o", lw=1.7,
                    color=METHOD_COLORS[method],label=SHORT[method],
                    ls={"cv":"-","gcv":"--","aicc":"-.","bic":":","mle":"-","controlled":"--"}[method])
        ax.set_title(label, fontsize=12)
        ax.set_xticks(ORDERS)
        ax.set_xlabel("Difference order d")
        if field == "lambda":
            ax.set_yscale("log")
        if field == "s":
            ax.set_ylim(-.02,1.02)
        ax.grid(alpha=.22)
    handles, labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncol=6,
               frameon=False, fontsize=9)
    title_mu="μ=0" if data["mode"]=="zero" else "data-derived μ by order"
    fig.suptitle(f"{title} — selection and holdout loss, {title_mu}",
                 fontsize=15, fontweight="bold")
    name=f"{dataset}_selection_summary_mu_{data['mode']}"
    _save(fig,name)
    return name


def plot_mu_sensitivity(zero: dict, data: dict, dataset: str,
                        title: str) -> str:
    fig,ax=plt.subplots(1,3,figsize=(14.0,4.6), constrained_layout=True)
    for method in SELECTORS:
        for label,series,style in (
            ("zero",zero,"-"),("data",data,"--"),
        ):
            records=series["records"]
            vals=[records[(order,method)]["rmse"] for order in ORDERS]
            ax[0].plot(ORDERS,vals,color=METHOD_COLORS[method],
                       ls=style,marker="o",ms=3,label=method+"-"+label)
    for j,field in ((1,"s"),(2,"lambda")):
        for method in SELECTORS:
            for vals,style in ((zero,"-"),(data,"--")):
                ax[j].plot(ORDERS, [vals["records"][(order,method)][field]
                                    for order in ORDERS],
                           color=METHOD_COLORS[method],ls=style,
                           marker="o",ms=3)
        if field=="lambda":
            ax[j].set_yscale("log")
    for axis,label in zip(ax,("Holdout RMSE","Selected S","Selected λ (log)")):
        axis.set(title=label,xlabel="Difference order d")
        axis.set_xticks(ORDERS)
        axis.grid(alpha=.22)
    fig.text(.5,.02,"Solid: fixed μ=0; dashed: μ estimated from each training window."
             " MLE with data mode is a conditional plug-in, not joint MLE.",
             ha="center",fontsize=10)
    fig.suptitle(title+" — sensitivity to the reference difference mean",
                 fontsize=14,fontweight="bold")
    name=f"{dataset}_mu_sensitivity"
    _save(fig,name)
    return name


def _record_for_json(row: dict) -> dict:
    return {
        key:(float(value) if isinstance(value,np.floating) else value)
        for key,value in row.items()
        if key not in {"conditional_fit","holdout_fit"}
        and not isinstance(value,np.ndarray)
    }


def _from_archived_selection(
    dates: list[date], observed: np.ndarray, mode: str, cached: dict,
) -> dict:
    """Reconstruct plots using FIXED archived parameters; never reselect.

    The stored JSON contains selected lambda, S, numeric mu and both
    holdout-origin parameters. We only evaluate the corresponding PLS
    curves and deterministic extrapolations. No search, likelihood,
    cross-validation, optimizer, timings or benchmarks are executed.
    """
    if cached.get("mu_modes") != list(MU_MODES):
        raise ValueError("Archived mu modes differ from the publication design")
    if cached.get("orders") != list(ORDERS) or cached.get("methods") != list(SELECTORS):
        raise ValueError("Archived selection method/order matrix is incomplete")
    if cached["dates"] != {"start":str(dates[0]),"end":str(dates[-1])}:
        raise ValueError("Archived dataset dates do not agree with frozen observations")
    found=cached["records"][mode]
    if len(found)!=len(ORDERS)*len(SELECTORS):
        raise ValueError("Missing archived criterion/order cases")
    train=observed[:-HOLDOUT]
    records={}
    for order in ORDERS:
        full_model=TrendSmoother(len(observed),order=order)
        train_model=TrendSmoother(len(train),order=order)
        for criterion in SELECTORS:
            key=f"d{order}_{criterion}"
            if key not in found:
                raise ValueError(f"Archived record missing: {mode}:{key}")
            row=dict(found[key])
            if not np.isfinite(float(row["lambda"])) or float(row["lambda"])<=0:
                raise ValueError(f"Invalid archived penalty for {mode}:{key}")
            if row["mu_mode"]!=mode or int(row["d"])!=order:
                raise ValueError(f"Invalid archived case identity: {mode}:{key}")
            full=full_model.fit(observed,lambda_=float(row["lambda"]),mu=float(row["mu"]))
            held=train_model.fit(train,lambda_=float(row["holdout_lambda"]),
                                 mu=float(row["holdout_mu"]))
            if not np.isclose(full.smoothness,float(row["s"]),atol=2e-7):
                raise ArithmeticError(f"Archived normalized S does not match: {key}")
            if not np.isclose(held.smoothness,float(row["holdout_s"]),atol=2e-7):
                raise ArithmeticError(f"Archived holdout S does not match: {key}")
            row["conditional_fit"]=np.asarray(full.trend)
            row["holdout_fit"]=np.asarray(held.trend)
            row["holdout_prediction"]=extrapolate_tail(held.trend,order,HOLDOUT)
            row["extrapolation"]=extrapolate_tail(full.trend,order,HORIZON)
            losses=row["holdout_prediction"]-observed[-HOLDOUT:]
            if not np.isclose(np.sqrt(np.mean(losses**2)),float(row["rmse"]),atol=1e-7):
                raise ArithmeticError(f"Holdout RMSE changed for {key}; source changed")
            if not np.isclose(np.mean(np.abs(losses)),float(row["mae"]),atol=1e-7):
                raise ArithmeticError(f"Holdout MAE changed for {key}; source changed")
            records[(order,criterion)]=row
    return {"mode":mode,"dates":dates,"y":observed,"records":records}


def generate(*, datasets: tuple[str,...] | None = None,
             render_only: bool = False) -> list[dict]:
    DATA.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for slug, title, filename, value_column, recent in SERIES:
        if datasets is not None and slug not in datasets:
            continue
        dates, observations=load_series(DATA/filename,value_column)
        if recent:
            dates, observations=dates[-recent:],observations[-recent:]
        modes={}
        figures=[]
        archived=None
        if render_only:
            existing=DATA/f"{slug}_dashboards.json"
            if not existing.is_file():
                raise FileNotFoundError(
                    f"Missing archived selections: {existing}. "
                    "Rendering never silently runs new optimization."
                )
            archived=json.loads(existing.read_text(encoding="utf-8"))
            if archived.get("dataset")!=slug or archived.get("source_file")!=filename:
                raise ValueError("Archived dataset identity does not match frozen CSV")
        for mode in MU_MODES:
            print(f"[dashboard] {slug}: mu={mode}, n={len(observations)}",
                  flush=True)
            values=(_from_archived_selection(dates,observations,mode,archived)
                    if render_only else analyze(dates,observations,mode))
            modes[mode]=values
            for kind in ("holdout","future"):
                figures.append(plot_dashboard(values,slug,title,kind))
            figures.append(plot_summary(values,slug,title))
        figures.append(plot_mu_sensitivity(modes["zero"],modes["data"],
                                           slug,title))
        if render_only:
            outputs.append(archived)
            continue
        json_result={
            "dataset":slug, "title":title,
            "source_file":filename,
            "dates":{"start":str(dates[0]),"end":str(dates[-1])},
            "orders":list(ORDERS), "methods":list(SELECTORS),
            "mu_modes":list(MU_MODES),
            "description":(
                "mu=data uses mean of order-d observed differences, "
                "computed within EACH training period only. CV/GCV/AICc/BIC "
                "condition on the resulting numeric mu; MLE uses the "
                "conditional mu=data plug-in, NOT joint mu/lambda MLE. "
                "Controlled S=0.86 is not a selected criterion. "
                "All six methods use the same 29-point candidate S grid "
                "where applicable, but MLE optimizes a distinct objective. "
                "Holdout uses one 12-month forecasting origin and anchored "
                "local-polynomial extrapolation, not a stochastic forecast model."
            ),
            "records":{
                mode:{
                    f"d{order}_{method}":_record_for_json(
                        values["records"][(order,method)]
                    ) for order in ORDERS for method in SELECTORS
                } for mode,values in modes.items()
            },
            "figures":[f"{filename}.pdf" for filename in figures],
        }
        (DATA/f"{slug}_dashboards.json").write_text(
            json.dumps(json_result,indent=2)+"\n",encoding="utf-8",
        )
        outputs.append(json_result)

    if not outputs:
        raise ValueError("No datasets selected")
    if not render_only:
        _write_selection_csv(outputs)
    _write_main_latex_table(outputs)
    print(f"[dashboard] {'Rendered archived' if render_only else 'Computed'} "
          f"{len(outputs)} scenarios using AwesomeFigures contrast colors",flush=True)
    return outputs


def _write_selection_csv(outputs: list[dict]) -> None:
    csv_path=DATA/"dashboard_selection_summary.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as fh:
        cols=("dataset","mu_mode","d","criterion","mu","lambda","s",
              "rmse","mae","score","criterion_ms_reusing_svd_and_grid",
              "candidate_count","holdout_mu","holdout_lambda","holdout_s")
        writer=csv.DictWriter(fh,fieldnames=cols)
        writer.writeheader()
        for dataset in outputs:
            for mode in MU_MODES:
                for order in ORDERS:
                    for method in SELECTORS:
                        record=dataset["records"][mode][f"d{order}_{method}"]
                        writer.writerow({
                            "dataset":dataset["dataset"],
                            "mu_mode":mode,"d":order,"criterion":method,
                            **{k:record[k] for k in cols[4:]},
                        })
def _write_main_latex_table(outputs: list[dict]) -> None:
    # Compact main-text comparison: NOAA full record, d=2, both mu modes.
    co2 = next((case for case in outputs if case["dataset"] == "co2_full"), None)
    if co2 is not None:
        latex_rows = [
            r"\begin{tabular}{llrrrrr}",
            r"\toprule",
            r"$\mu$ mode & Selector & $\mu$ & $\lambda$ & $S$ & RMSE & MAE \\",
            r"\midrule",
        ]
        for mode in MU_MODES:
            for method in SELECTORS:
                value = co2["records"][mode][f"d2_{method}"]
                desc = r"$0$ fixed" if mode == "zero" else "training plug-in"
                latex_rows.append(
                    f"{desc} & {SHORT[method].replace(' ', '~')} & "
                    f"{value['mu']:.3g} & {value['lambda']:.3g} & "
                    f"{value['s']:.3f} & {value['rmse']:.3f} & "
                    f"{value['mae']:.3f}" + r" \\"
                )
        latex_rows.extend([r"\bottomrule",r"\end{tabular}"])
        (HERE/"dashboard_summary_table.tex").write_text(
            "\n".join(latex_rows)+"\n", encoding="utf-8",
        )

 

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",choices=("all",)+tuple(x[0] for x in SERIES),
                        default="all",help="Subset of case studies for smoke tests")
    parser.add_argument(
        "--render-only",action="store_true",
        help="Restyle plots using saved selected lambda, S, mu, and losses. "
             "No criterion selection, objective optimization, or benchmark."
    )
    args=parser.parse_args()
    chosen=None if args.dataset=="all" else (args.dataset,)
    generate(datasets=chosen,render_only=args.render_only)


if __name__ == "__main__":
    main()
