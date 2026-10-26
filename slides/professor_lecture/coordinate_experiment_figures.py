"""Add paired objective plots and host-measured factorial timings to Marp slides.

These figures are invoked by make_figures.py. Every runtime plot comes
from CSV measurements; absent data produce explicit missing-data panels.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from trendestimation import score_lambda

METHODS = ("svd", "eigh", "cholesky")
CRITERIA = ("cv", "gcv", "aicc", "bic")
COORDINATES = ("lambda", "s_mapped", "s_uniform")
LABELS = {"lambda": "log-lambda grid + post-map",
          "s_mapped": "same candidates via inverse S",
          "s_uniform": "uniform S grid"}
COLORS = {"lambda": "#205fd4", "s_mapped": "#138b94",
          "s_uniform": "#db9a31"}
STUDY = Path(__file__).resolve().parents[2] / "build" / "criterion-coordinate-study"


def paired_score_figures(model, y, save):
    lam = np.geomspace(1e-3, 3500, 260)
    s = np.asarray([model.smoothness(float(x)) for x in lam])
    for count, name in enumerate(CRITERIA, start=50):
        scores = np.asarray([
            score_lambda(model, y, lambda_=float(x), criterion=name, mu=0.0)
            for x in lam
        ])
        finite = np.isfinite(scores)
        if not np.any(finite):
            raise ArithmeticError(f"No finite candidate score for {name}")
        best = int(np.argmin(np.where(finite, scores, np.inf)))
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.6),
                                sharey=True, layout="constrained")
        fig.suptitle(f"{name.upper()}: the same objective, two coordinates",
                     fontsize=17, weight="bold")
        axs[0].semilogx(lam[finite], scores[finite],
                         color="#205fd4", lw=2.6)
        axs[1].plot(s[finite], scores[finite],
                    color="#138b94", lw=2.6)
        for axis, pos in zip(axs, (lam[best], s[best])):
            axis.scatter([pos], [scores[best]], s=55,
                         color="#bf5268", zorder=5,
                         label="lowest score on mapped candidates")
            axis.grid(alpha=0.35)
        axs[0].set_xlabel("Penalty λ (log scale)")
        axs[1].set_xlabel("Normalized smoothness S(λ)")
        axs[0].set_ylabel(f"{name.upper()} score, lower is better")
        axs[1].set_xlim(0, 1)
        axs[1].legend(frameon=False, loc="best", fontsize=9)
        save(f"{count}_{name}_coordinate_pair", fig, kind="deterministic",
             source="n=96, d=2, mu=0, seed=24021; identical 260 lambda candidates")


def _selected_rows(rows):
    """Prefer (64,2,*) if present, otherwise first available (n,d,mu)."""
    keys = sorted({(int(row["n"]), int(row["d"]), float(row["mu"]))
                   for row in rows})
    desired = next((k for k in keys if k[0] == 64 and k[1] == 2), keys[0])
    return [r for r in rows if (int(r["n"]), int(r["d"]),
                                float(r["mu"])) == desired], desired


def _read_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def measured_figures(save, axes, message):
    summary = _read_csv(STUDY/"summary.csv")
    raw = _read_csv(STUDY/"raw_trials.csv")
    planned = (
        ("54_coordinate_factorial", "Measured 3 × 4 × 3 runtime matrix"),
        ("55_s_vs_lambda_ratio", "Measured S-versus-lambda runtime ratios"),
        ("56_phase_breakdown", "Measured setup, inversion and score work"),
        ("57_optimum_quality", "Score differences from lambda grid search"),
    )
    if not summary or not raw:
        for name, title in planned:
            message(name, title, "Factorial study CSV is not present.\n"
                    "Run: python benchmarks/criterion_coordinate_matrix.py\n"
                    "  --preset quick --seeds 3 --repeats 4\n"
                    "Then regenerate the lecture figures.")
        return
    values, desc = _selected_rows(summary)
    dlabel = f"n={desc[0]}, d={desc[1]}, mu={desc[2]:g}"
    index = {(r["solver"], r["criterion"], r["coordinate"]): r for r in values}

    # 54: 4 panels with complete solver × coordinate timings.
    fig, axs = plt.subplots(2, 2, figsize=(12, 7.0), layout="constrained")
    for ax, crit in zip(axs.ravel(), CRITERIA):
        xx = np.arange(len(METHODS), dtype=float)
        for k, coordinate in enumerate(COORDINATES):
            yy = [float(index[(solver, crit, coordinate)]["median_ms"])
                  if (solver, crit, coordinate) in index else np.nan
                  for solver in METHODS]
            ax.bar(xx+(k-1)*0.24, yy, width=0.23,
                   label=LABELS[coordinate], color=COLORS[coordinate])
        ax.set_xticks(xx, [x.upper() for x in METHODS])
        ax.set_title(crit.upper(), fontweight="bold")
        ax.set_ylabel("Median end-to-end time (ms)")
        ax.set_yscale("log")
        ax.grid(alpha=0.27, axis="y")
    axs[0, 0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle(f"Host-measured full criterion selection | {dlabel}",
                 fontsize=17, fontweight="bold")
    save("54_coordinate_factorial", fig, kind="host measured",
         source=f"{STUDY/'summary.csv'}; medians, setup and inverse included")

    # 55: heatmap ratios for native-uniform S versus direct lambda.
    ratios = np.full((len(METHODS), len(CRITERIA)), np.nan)
    for i, solver in enumerate(METHODS):
        for j, criterion in enumerate(CRITERIA):
            num = index.get((solver, criterion, "s_uniform"))
            den = index.get((solver, criterion, "lambda"))
            if num and den and float(den["median_ms"]) > 0:
                ratios[i, j] = float(num["median_ms"])/float(den["median_ms"])
    fig, ax = plt.subplots(figsize=(10, 4.2), layout="constrained")
    image = ax.imshow(ratios, cmap="Blues", aspect="auto", vmin=0)
    ax.set(xticks=range(len(CRITERIA)), xticklabels=[c.upper() for c in CRITERIA],
           yticks=range(len(METHODS)), yticklabels=[m.upper() for m in METHODS],
           title=f"End-to-end ratio = native S search / lambda search | {dlabel}")
    for i in range(len(METHODS)):
        for j in range(len(CRITERIA)):
            if np.isfinite(ratios[i, j]):
                ax.text(j, i, f"{ratios[i,j]:.2f}x", ha="center", va="center",
                        color="#102844", fontsize=13, fontweight="bold")
    fig.colorbar(image, ax=ax, label="Ratio above 1: S search slower")
    save("55_s_vs_lambda_ratio", fig, kind="host measured",
         source=f"{STUDY/'summary.csv'}; median time ratios")

    # 56: disaggregate phases, using medians of each measured component.
    native = [r for r in raw if (int(r["n"]), int(r["d"]),
               float(r["mu"]), r["criterion"]) == (*desc, "cv")]
    groups = defaultdict(list)
    for row in native:
        groups[(row["solver"], row["coordinate"])].append(row)
    targets = [(method, coord) for method in METHODS for coord in COORDINATES]
    fig, ax = plt.subplots(figsize=(11, 5.5), layout="constrained")
    bottom = np.zeros(len(targets))
    for col, field in (("#205fd4", "setup_ns"),
                       ("#138b94", "inversion_ns"),
                       ("#db9a31", "score_ns"),
                       ("#7b88aa", "postmap_ns")):
        yparts = [float(np.median([float(r[field])/1e6 for r in groups[key]]))
                  if groups[key] else 0.0 for key in targets]
        ax.bar(np.arange(len(targets)), yparts, bottom=bottom, color=col,
               label=field.removesuffix("_ns"))
        bottom += np.asarray(yparts)
    ax.set_xticks(np.arange(len(targets)),
                  [f"{m}\n{c}" for m, c in targets], fontsize=9)
    ax.set_ylabel("Median phase time (ms)")
    ax.set_title(f"CV: measured time by phase | {dlabel}", fontsize=16)
    ax.legend(ncol=4, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    save("56_phase_breakdown", fig, kind="host measured",
         source=f"{STUDY/'raw_trials.csv'}; phase medians per cell")

    # 57: score quality, not just speed; mapped S should agree.
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    for ax, coord in zip(axs, ("s_mapped", "s_uniform")):
        for k, solver in enumerate(METHODS):
            yy = [float(index[(solver, criterion, coord)][
                  "median_score_difference_vs_lambda"])
                  if (solver, criterion, coord) in index else np.nan
                  for criterion in CRITERIA]
            ax.plot(np.arange(4), yy, marker="o", lw=2.5,
                    color=("#205fd4", "#138b94", "#db9a31")[k],
                    label=solver)
        ax.axhline(0, color="#71829c", lw=1)
        ax.set_xticks(range(4), [c.upper() for c in CRITERIA])
        ax.set_title("Mapped S: same candidates" if coord == "s_mapped"
                     else "Native S: different candidates")
        ax.set_ylabel("Median selected score - λ-grid score")
        ax.grid(alpha=0.25)
    axs[0].legend(frameon=False)
    fig.suptitle(f"Selection quality is independent of runtime | {dlabel}",
                 fontsize=17, fontweight="bold")
    save("57_optimum_quality", fig, kind="host measured",
         source=f"{STUDY/'summary.csv'}; score differences")
