"""Analyze the author's measured 80,640-cell Windows experiment.

Input is the ORIGINAL CSV committed in
paper/benchmarks/results/full_s_search_modes. The GitHub-Linux reference
remains unchanged. Two actual seeds per full factorial cell are aggregated
by their median. Invalid numerical methods cannot win on elapsed time.

Outputs:
  paper/benchmarks/windows_full_s_analysis/*.csv and validation.json
  paper/sections/windows_full_s_generated.tex (measured results table)
  docs/windows_full_s_generated.rst (measured documentation table)
  five corresponding AwesomeFigures PDF+SVG pairs.

Run: python paper/benchmarks/report_windows_full_s.py
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
SOURCE = PAPER / "benchmarks/results/full_s_search_modes"
DEST = PAPER / "benchmarks/windows_full_s_analysis"
METHODS = ("dense_fresh", "dense_cached", "general_banded",
           "dense_cholesky", "banded_cholesky", "eigh", "svd")
METHOD_LABELS = ("Dense fresh", "Dense cached", "General banded",
                 "Dense Cholesky", "Banded Cholesky", "Eigen", "SVD")
CRITERIA = ("cv", "gcv", "aicc", "bic", "mle")
POLICIES = ("single_native_s", "single_lambda", "single_mapped_s_lambda",
            "native_s", "mapped_s_lambda", "native_log_lambda",
            "continuous_s", "continuous_log_lambda")
KEYS = ("n", "d", "mu", "criterion", "method", "R", "reuse_mode", "policy")
TIMES = ("setup_s", "evaluate_s", "mapping_once_s",
         "total_standalone_s", "total_backend_only_s", "selected_s",
         "mean_score", "candidate_evaluations")


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)


def med(values):
    finite = [float(v) for v in values if math.isfinite(float(v))]
    return statistics.median(finite) if finite else float("nan")


def value_ms(row, field="total_standalone_s"):
    return 1000 * float(row[field])


def load():
    raw = read_csv(SOURCE / "search_mode_timings.csv")
    prep = read_csv(SOURCE / "search_grid_preparation.csv")
    env = json.loads((SOURCE / "environment.json").read_text(encoding="utf-8"))
    if len(raw) != 80640:
        raise RuntimeError("Expected exactly 80,640 original Windows records")
    axes = {
        "n": {24, 48}, "d": set(range(6)), "mu": {0., .15},
        "R": {1, 3, 8}, "criterion": set(CRITERIA),
        "method": set(METHODS), "policy": set(POLICIES),
        "reuse_mode": {"shared", "cold"},
    }
    for key, expected in axes.items():
        cast = float if key == "mu" else (
            int if key in ("n", "d", "R") else str
        )
        found = {cast(row[key]) for row in raw}
        if found != expected:
            raise RuntimeError("Missing or unexpected axis: "+key)
    if any(int(r["shared_grid_size"]) != 17 for r in raw):
        raise RuntimeError("Not the 17-point complete S grid")
    if any(r["status"] != "not_applicable_d0_mle"
           for r in raw if r["criterion"] == "mle" and r["d"] == "0"):
        raise RuntimeError("Cannot infer MLE for d=0")
    if len(prep) != 12:
        raise RuntimeError("Expected 12 n/d grid mapping records")
    if not env["platform"].startswith("Windows") or (
        env["preset"], env["repeats"], env["blas_threads"]
    ) != ("full", 7, 1):
        raise RuntimeError("Incorrect machine or experiment provenance")
    if sorted(env["seeds"]) != [20261026, 20261027]:
        raise RuntimeError("Missing expected recorded seed pair")
    return raw, prep, env


def summarize(raw):
    buckets = defaultdict(list)
    for r in raw:
        buckets[tuple(r[k] for k in KEYS)].append(r)
    if len(buckets) != 40320 or any(len(v) != 2 for v in buckets.values()):
        raise RuntimeError("Expected 40,320 full factorial cells and two seeds")
    out = []
    for key, values in sorted(buckets.items()):
        x = dict(zip(KEYS, key))
        x["seed_count"] = 2
        x["valid_seed_count"] = sum(v["success"] == "True" for v in values)
        x["both_valid"] = x["valid_seed_count"] == 2
        x["n_a_seed_count"] = sum(
            v["status"] == "not_applicable_d0_mle" for v in values
        )
        for field in TIMES:
            x[field] = med(v[field] for v in values)
        out.append(x)
    return out, buckets


def pick(index, n=48, d=2, mu=0., criterion="gcv",
         method="svd", R=1, reuse_mode="shared",
         policy="mapped_s_lambda"):
    key = (str(n), str(d), str(float(mu)), criterion, method,
           str(R), reuse_mode, policy)
    if key not in index:
        raise KeyError("Missing cell "+repr(key))
    return index[key]


def check_parity(buckets):
    count = 0
    max_s_difference = 0.
    max_score_difference = 0.
    for key, s_rows in buckets.items():
        if key[-1] != "native_s":
            continue
        companion = buckets.get(key[:-1] + ("mapped_s_lambda",))
        if companion is None:
            raise RuntimeError("Paired converted grid is missing")
        for left, right in zip(s_rows, companion):
            if left["success"] != "True" or right["success"] != "True":
                continue
            count += 1
            a, b = float(left["selected_s"]), float(right["selected_s"])
            if math.isfinite(a) and math.isfinite(b):
                max_s_difference = max(max_s_difference, abs(a-b))
            a, b = float(left["mean_score"]), float(right["mean_score"])
            if math.isfinite(a) and math.isfinite(b):
                max_score_difference = max(max_score_difference, abs(a-b))
    if not count or max_s_difference > 1e-6:
        raise RuntimeError("The identical S/lambda mapped grids lost score parity")
    return {
        "matched_valid_seed_pairs":count,
        "maximum_selected_s_disagreement":max_s_difference,
        "maximum_absolute_score_disagreement":max_score_difference,
    }


def selected_rows(index):
    out = []
    for mu in (0.,.15):
        for crit in CRITERIA:
            x = {"n":48,"d":2,"mu":mu,"criterion":crit}
            for policy in ("native_s","mapped_s_lambda","native_log_lambda",
                           "continuous_s","continuous_log_lambda"):
                r = pick(index,mu=mu,criterion=crit,policy=policy)
                x[policy+"_S"] = r["selected_s"] if r["both_valid"] else "NA"
                x[policy+"_ms"] = (
                    value_ms(r) if r["both_valid"] else "NA")
            out.append(x)
    return out


def comparative_rows(index, prep):
    map_cost = {
        (int(r["n"]),int(r["d"])):value_ms(r,"map_once_s")
        for r in prep
    }
    results = []
    for n in (24,48):
        for d in range(6):
            for mu in (0.,.15):
                for crit in CRITERIA:
                    for method in METHODS:
                        for R in (1,3,8):
                            native = pick(index,n,d,mu,crit,method,R,policy="native_s")
                            mapped = pick(index,n,d,mu,crit,method,R,
                                          policy="mapped_s_lambda")
                            log = pick(index,n,d,mu,crit,method,R,
                                       policy="native_log_lambda")
                            results.append({
                                "n":n,"d":d,"mu":mu,"criterion":crit,
                                "method":method,"R":R,
                                "native_s_ms":value_ms(native),
                                "mapped_s_ms":value_ms(mapped),
                                "log_lambda_ms":value_ms(log),
                                "once_mapping_ms":map_cost[(n,d)],
                                "valid_native_seeds":native["valid_seed_count"],
                                "valid_mapped_seeds":mapped["valid_seed_count"],
                                "valid_log_seeds":log["valid_seed_count"],
                                "selected_native_S":native["selected_s"],
                                "selected_mapped_S":mapped["selected_s"],
                            })
    return results


def number(x):
    v = float(x)
    return f"{v:.3f}" if math.isfinite(v) else "--"


def manuscript(index, prep):
    header = [
        "% AUTO-GENERATED FROM TWO RECORDED WINDOWS SEEDS; DO NOT EDIT VALUES",
        r"\begin{table}[tbp]",
        r"\centering",
        r"\caption{Author's Windows full-run median complete 17-point grid",
        r"selection times (milliseconds) for two independent recorded seeds,",
        r"$n=48$, $d=2$, fixed $\mu=0$, $R=1$, spectral SVD,",
        r"one BLAS thread and seven timing repetitions.",
        r"Premapped $S\to\lambda$ includes one complete grid conversion.",
        r"Independent log-$\lambda$ has different interior nodes.",
        r"Cells are shown only where both seeds are numerically valid.}",
        r"\label{tab:windows-full-search}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Criterion & Native $S$ & Premapped $\lambda$ & Log-$\lambda$ \\",
        r"\midrule",
    ]
    for criterion in CRITERIA:
        costs = []
        for policy in ("native_s","mapped_s_lambda","native_log_lambda"):
            r=pick(index,criterion=criterion,policy=policy)
            costs.append(number(value_ms(r)) if r["both_valid"] else "--")
        header.append(("AICc" if criterion == "aicc" else criterion.upper())+" & "+" & ".join(costs)+r" \\")
    header += [r"\bottomrule",r"\end{tabular}",r"\end{table}",""]
    ref = [pick(index,criterion=c,policy="native_s") for c in CRITERIA]
    mapped = [pick(index,criterion=c,policy="mapped_s_lambda") for c in CRITERIA]
    if all(r["both_valid"] for r in ref+mapped):
        sum_native = sum(value_ms(r) for r in ref)
        mapping = next(value_ms(r,"map_once_s") for r in prep
                       if int(r["n"])==48 and int(r["d"])==2)
        sum_mapped = mapping + sum(
            value_ms(r,"total_backend_only_s") for r in mapped
        )
        header.append(
            "When reusing exactly one pretranslated candidate grid "
            "across all five criteria, the measured native-$S$ total "
            "was "+number(sum_native)+r"\,ms and the shared "
            r"$S\to\lambda$ mapping plus five backend-only searches "
            "took "+number(sum_mapped)+r"\,ms (descriptive ratio "
            +number(sum_native/sum_mapped)+"). "
            "This accounting charges grid inversion exactly once, "
            "not once per statistical criterion."
        )
    header += [
        "",
        r"The $80\,640$ original author-host measurements and machine",
        r"metadata are preserved under",
        r"\texttt{paper/benchmarks/results/full\_s\_search\_modes/}.",
        r"The Windows study covers $n=24,48$, $d=0,\ldots,5$,",
        r"$\mu=0,0.15$, $R=1,3,8$, seven backends, five criteria,",
        r"and cold versus shared backend preparation.",
        r"MLE at $d=0$ remains not applicable. At $S=1$",
        r"the $\lambda=\infty$ limit is evaluated analytically.",
        "",
    ]
    path=PAPER/"sections/windows_full_s_generated.tex"
    path.write_text("\n".join(header),encoding="utf-8")


def docs(index, parity):
    lines = [
        ".. This table is generated solely from uploaded Windows CSV evidence.",
        "",
        "Measured full Windows study",
        "---------------------------",
        "",
        "The source contains **80,640 real Windows search records**, with",
        "two experimental seeds, seven timing repetitions and one BLAS thread.",
        "For :math:`n=48, d=2, \\mu=0, R=1`, spectral SVD, the following",
        "millisecond values are medians of the two recorded seeds:",
        "",
        ".. list-table:: Seventeen-point grid timings",
        "   :header-rows: 1",
        "   :widths: 25 25 25 25",
        "",
        "   * - Criterion",
        "     - Native S",
        "     - Premapped S to lambda",
        "     - Independent log-lambda",
    ]
    for criterion in CRITERIA:
        vals = []
        for policy in ("native_s","mapped_s_lambda","native_log_lambda"):
            row=pick(index,criterion=criterion,policy=policy)
            vals.append(number(value_ms(row))+" ms"
                        if row["both_valid"] else "N/A")
        lines += [
            "   * - "+("AICc" if criterion == "aicc" else criterion.upper()),
            "     - "+vals[0],
            "     - "+vals[1],
            "     - "+vals[2],
        ]
    lines += [
        "",
        "Native S and pretranslated S-to-lambda use the **same candidate",
        "penalties**; independent log-lambda uses different interior points.",
        "The source audit verified **"+str(parity["matched_valid_seed_pairs"])+
        "** numerically valid matched-coordinate seed pairs.",
        "Unstable numerical backends are excluded from full-grid winner",
        "comparisons, not credited for completing only part of a search.",
        "The exact S=1 / lambda=infinity endpoint is analytical.",
        "The Gaussian MLE model is not applicable for d=0.",
        "",
    ]
    (ROOT/"docs/windows_full_s_generated.rst").write_text(
        "\n".join(lines),encoding="utf-8"
    )


def images(index):
    import matplotlib.pyplot as plt
    import numpy as np
    style=run_path(str(PAPER/"figures/render_awesomefigures.py"))
    palette=style["COLORS"]
    output=PAPER/"figures"
    fig_names = []

    def timed(**kwargs):
        r=pick(index,**kwargs)
        return value_ms(r) if r["both_valid"] else np.nan

    def save(pub, fig, name):
        # In SNCS publication mode, these figures must be re-exported at
        # their *actual* .48 of the line width (or full-width) manuscript size.
        # The older general manuscript figures have different dimensions.
        import os
        if os.environ.get("TRENDESTIMATION_TEX_FIGURES") == "1":
            import sys
            theme_dir = PAPER / "computational-statistics-submission"
            if str(theme_dir) not in sys.path:
                sys.path.insert(0, str(theme_dir))
            from contrast_theme import save_figure
            target = theme_dir / "figures"
            target.mkdir(parents=True, exist_ok=True)
            save_figure(fig, target / (name + ".pdf"), dpi=180, strict=True)
            save_figure(fig, target / (name + ".svg"), dpi=180, strict=True)
            plt.close(fig)
        else:
            with plt.rc_context({"svg.fonttype":"none"}):
                fig.savefig(output/(name+".svg"), format="svg")
            style["_save"](pub,fig,output/(name+".pdf"))
        fig_names.append(name)

    with style["publication_context"]() as pub:
        axis=style["_axis"]
        fig,ax=axis(pub,ylog=True)
        for i,(method,label) in enumerate(zip(METHODS,METHOD_LABELS)):
            yy=[
                timed(d=1,method=method,criterion="gcv",R=1,
                      policy="single_mapped_s_lambda"),
                timed(d=1,method=method,criterion="gcv",R=1,
                      policy="mapped_s_lambda"),
                timed(d=1,method=method,criterion="gcv",R=8,
                      policy="mapped_s_lambda"),
            ]
            ax.plot(range(3),yy,color=palette[i%len(palette)],
                    linewidth=1.3,marker=("o","s","^","D")[i%4],
                    linestyle=("-","--","-.",":")[i%4],
                    markersize=3,label=label)
        ax.set_xticks(range(3),
                      ("One S=0.5","One 17-point grid","Eight full grids"))
        ax.tick_params(axis="x",labelsize=7)
        ax.set(xlabel="GCV workload, n=48, d=1, fixed mu=0",
               ylabel="Time (ms, logarithmic)")
        ax.legend(ncol=3,fontsize=7,frameon=False,
                  loc="upper center",bbox_to_anchor=(.5,-.22))
        fig.subplots_adjust(left=.13,right=.97,bottom=.35,top=.95)
        save(pub,fig,"windows_full_s_workloads")

        fig,ax=axis(pub,ylog=True)
        for j,(policy,label) in enumerate(zip(
            ("native_s","mapped_s_lambda","native_log_lambda"),
            ("Native S","Map S once","Different log-lambda grid"),
        )):
            yy=[timed(criterion=c,policy=policy) for c in CRITERIA]
            ax.bar(np.arange(5)+.23*(j-1),yy,width=.23,
                   color=palette[(2*j+1)%len(palette)],label=label)
        ax.set_xticks(range(5),[c.upper() for c in CRITERIA])
        ax.set(xlabel="17-point grid, n=48, d=2, mu=0, SVD",
               ylabel="Standalone time (ms, logarithmic)")
        ax.legend(ncol=2,fontsize=7,frameon=False,
                  loc="upper center",bbox_to_anchor=(.5,-.2))
        fig.subplots_adjust(left=.13,right=.97,bottom=.33,top=.95)
        save(pub,fig,"windows_full_s_grid_coordinates")

        fig,ax=axis(pub)
        for i,c in enumerate(CRITERIA):
            yy=[]
            for d in range(6):
                shared=pick(index,d=d,R=8,criterion=c)
                cold=pick(index,d=d,R=8,criterion=c,reuse_mode="cold")
                if shared["both_valid"] and cold["both_valid"] and (
                    float(shared["total_backend_only_s"])>0
                ):
                    yy.append(float(cold["total_backend_only_s"])/
                              float(shared["total_backend_only_s"]))
                else:
                    yy.append(np.nan)
            ax.plot(range(6),yy,marker=("o","s","^","D")[i%4],
                    linewidth=1.3,markersize=3,
                    linestyle=("-","--","-.",":")[i%4],
                    color=palette[i%len(palette)],label=c.upper())
        ax.axhline(1.0,color="#777777",linestyle="--",linewidth=.8)
        ax.set_xticks(range(6))
        ax.set(xlabel="Difference order d; 8 series, n=48, SVD, mu=0",
               ylabel="Cold/shared backend time")
        ax.legend(ncol=3,fontsize=7,frameon=False,
                  loc="upper center",bbox_to_anchor=(.5,-.2))
        fig.subplots_adjust(left=.13,right=.97,bottom=.32,top=.95)
        save(pub,fig,"windows_full_s_reuse_d")

        fig,ax=axis(pub,ylog=True)
        for j,(policy,label) in enumerate(zip(
            ("continuous_s","continuous_log_lambda"),
            ("Bounded S","Bounded log-lambda"),
        )):
            vals=[timed(criterion=c,policy=policy) for c in CRITERIA]
            ax.bar(np.arange(5)+.17*(2*j-1),vals,width=.34,
                   color=palette[(j*3+2)%len(palette)],label=label)
        ax.set_xticks(range(5),[c.upper() for c in CRITERIA])
        ax.set(xlabel="Bounded local optimizer, n=48, d=2, mu=0",
               ylabel="Time (ms, logarithmic)")
        ax.legend(ncol=2,fontsize=7,frameon=False,
                  loc="upper center",bbox_to_anchor=(.5,-.2))
        fig.subplots_adjust(left=.13,right=.97,bottom=.32,top=.95)
        save(pub,fig,"windows_full_s_bounded")

        fig,ax=axis(pub)
        for i,mu in enumerate((0.,.15)):
            vals=[]
            for c in CRITERIA:
                r=pick(index,mu=mu,criterion=c)
                vals.append(r["selected_s"] if r["both_valid"] else np.nan)
            ax.plot(range(5),vals,color=palette[2*i],
                    marker=("o","s")[i],markersize=4,
                    linestyle=("-","--")[i],linewidth=1.4,
                    label="mu="+str(mu))
        ax.set_xticks(range(5),[c.upper() for c in CRITERIA])
        ax.set_ylim(-.03,1.03)
        ax.set(xlabel="Criterion, full S grid, n=48, d=2",
               ylabel="Median selected S (two seeds)")
        ax.legend(ncol=2,fontsize=7,frameon=False,
                  loc="upper center",bbox_to_anchor=(.5,-.19))
        fig.subplots_adjust(left=.13,right=.97,bottom=.30,top=.95)
        save(pub,fig,"windows_full_s_means")
    return fig_names


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summaries-only",action="store_true")
    args=parser.parse_args()
    raw,prep,env=load()
    rows,buckets=summarize(raw)
    index={tuple(r[k] for k in KEYS):r for r in rows}
    parity=check_parity(buckets)
    DEST.mkdir(parents=True,exist_ok=True)
    write_csv(DEST/"two_seed_aggregates.csv",rows)
    write_csv(DEST/"paired_grid_costs.csv",comparative_rows(index,prep))
    write_csv(DEST/"selected_s.csv",selected_rows(index))
    provenance={
        "origin":"author Windows full experimental run",
        "source_csv":"paper/benchmarks/results/full_s_search_modes/search_mode_timings.csv",
        "raw_rows":len(raw),"two_seed_design_cells":len(rows),
        "platform":env["platform"],"preset":env["preset"],
        "seeds":env["seeds"],"n":env["n"],"d":env["d"],
        "mu":env["reference_means"],"R":env["R"],
        "criteria":env["criteria"],"backends":env["backends"],
        "repeats":env["repeats"],"blas_threads":env["blas_threads"],
        **parity,
    }
    (DEST/"validation.json").write_text(
        json.dumps(provenance,indent=2,allow_nan=False),encoding="utf-8"
    )
    manuscript(index,prep)
    docs(index,parity)
    names=[] if args.summaries_only else images(index)
    print(json.dumps({"rows":len(raw),"two_seed_cells":len(rows),
                      "figures":names,"parity":parity},indent=2),flush=True)


if __name__=="__main__":
    main()
