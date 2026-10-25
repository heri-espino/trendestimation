"""Formal paired timing analysis of raw PLS backend measurements.

Run:
  python benchmarks/analyze_formal_solver_study.py --input-dir build/solver-study
  python benchmarks/analyze_formal_solver_study.py --input-dir build/solver-study --bootstrap 10000

The inferential unit is one independently generated data seed per workload,
with the median of all within-seed timing blocks. Repetitions and penalties
are NOT counted as independent samples. Two-sided paired sign-flip tests
compare the mean log time ratio (geometric mean speedup), with Holm
family-wise correction over ALL pre-specified primary hypotheses.
Secondary timing metrics are descriptive, not separately tested.
Percentile bootstrap confidence intervals are *pointwise, unadjusted*.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

import numpy as np

METHODS = ("svd", "eigh", "cholesky")
PAIRS = tuple(itertools.combinations(METHODS, 2))
PRIMARY = "end_to_end_ns"
METRICS = ("end_to_end_ns", "setup_ns", "batch_ns", "single_amortized_ns")


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to export to {path}")
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate_and_aggregate(rows: list[dict], metadata: dict):
    """Return paired per-seed median timings, checking complete matched blocks."""
    if metadata.get("protocol_version") != "paired_solver_study_v1":
        raise ValueError("Unsupported or missing timing protocol")
    seen: set[tuple[int, int, int, str]] = set()
    blocks: dict[tuple[int, int, int], set[str]] = defaultdict(set)
    grouped: dict[tuple[int, int, str], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        case = int(row["case_id"])
        seed = int(row["seed_index"])
        block = int(row["block"])
        method = row["method"]
        if method not in METHODS:
            raise ValueError(f"Unexpected method: {method}")
        identity = (case, seed, block, method)
        if identity in seen:
            raise ValueError(f"Duplicate paired observation: {identity}")
        seen.add(identity)
        blocks[(case, seed, block)].add(method)
        for metric in METRICS:
            value = float(row[metric])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"Nonpositive or invalid time for {identity}: {metric}")
            grouped[(case, seed, method)][metric].append(value)

    if any(observed != set(METHODS) for observed in blocks.values()):
        raise ValueError("Incomplete matched timing blocks; do not discard missing methods")
    expected_cases = {int(x["case_id"]) for x in metadata["workload_cases"]}
    if set(case for case, _, _ in blocks) != expected_cases:
        raise ValueError("Raw data do not cover every declared workload")
    for case in expected_cases:
        seeds = {seed for c, seed, _ in blocks if c == case}
        if seeds != set(range(int(metadata["independent_seeds"]))):
            raise ValueError(f"Incomplete set of data seeds in case {case}")
        for seed in seeds:
            timings = [block for c, s, block in blocks if (c, s) == (case, seed)]
            if set(timings) != set(range(int(metadata["timing_blocks_per_seed"]))):
                raise ValueError(f"Incomplete matched repeats in case {case}, seed {seed}")

    aggregation = {}
    for key, values in grouped.items():
        aggregation[key] = {metric: float(median(values[metric])) for metric in METRICS}
    return aggregation


def signflip_pvalue(
    differences: np.ndarray, rng: np.random.Generator, permutations: int,
) -> tuple[float, str]:
    """Two-sided paired randomization/sign-flip p-value for mean log ratio.

    Exact enumeration for <=16 independent seeds; Monte Carlo with plus-one
    correction otherwise. Symmetric/exchangeable log differences are an
    assumption, not a consequence of measuring fast code.
    """
    arr = np.asarray(differences, dtype=float)
    if arr.ndim != 1 or len(arr) == 0 or not np.all(np.isfinite(arr)):
        raise ValueError("Differences must be one finite nonempty vector")
    n = len(arr)
    observed = abs(float(np.mean(arr)))
    if n <= 16:
        count = 0
        extreme = 0
        for bits in itertools.product((-1., 1.), repeat=n):
            candidate = abs(float(np.mean(arr * bits)))
            extreme += candidate >= observed - 1e-14
            count += 1
        return float(extreme / count), "exact_signflip"
    extreme = 0
    total = 0
    chunk_size = 1024
    for start in range(0, permutations, chunk_size):
        amount = min(chunk_size, permutations - start)
        signs = rng.choice(np.array([-1., 1.]), size=(amount, n))
        means = np.abs(np.mean(signs * arr, axis=1))
        extreme += int(np.count_nonzero(means >= observed - 1e-14))
        total += amount
    return float((extreme + 1) / (total + 1)), "monte_carlo_signflip"


def bootstrap_log_ratio_ci(
    log_ratio: np.ndarray, rng: np.random.Generator,
    bootstrap: int, alpha: float,
) -> tuple[float, float]:
    """Pointwise percentile bootstrap over independent data seeds."""
    arr = np.asarray(log_ratio, dtype=float)
    picks = rng.integers(0, len(arr), size=(bootstrap, len(arr)))
    draws = np.mean(arr[picks], axis=1)
    low, high = np.quantile(draws, [alpha / 2, 1 - alpha / 2])
    return float(np.exp(low)), float(np.exp(high))


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, preserving original order."""
    if not p_values:
        return []
    values = np.asarray(p_values, dtype=float)
    if not np.all(np.isfinite(values)) or np.any((values < 0) | (values > 1)):
        raise ValueError("Invalid p-values")
    count = len(values)
    indices = np.argsort(values, kind="stable")
    adjusted = np.empty(count, dtype=float)
    previous = 0.
    for rank, index in enumerate(indices):
        previous = max(previous, (count - rank) * float(values[index]))
        adjusted[index] = min(1., previous)
    return adjusted.tolist()


def summarize(
    aggregated: dict, metadata: dict, *, seed: int = 42,
    bootstrap: int = 4000, permutations: int = 20000,
    alpha: float = .05, min_inferential_seeds: int = 5,
) -> tuple[list[dict], list[dict]]:
    """Summarize paired speedups and seed-level method timings."""
    timing_rows, comparisons = [], []
    master_rng = np.random.default_rng(seed)
    cases = metadata["workload_cases"]
    for case in cases:
        case_id = int(case["case_id"])
        seed_ids = sorted({
            seed_no for (c, seed_no, method) in aggregated if c == case_id
        })
        info = {
            "case_id": case_id, "n": int(case["n"]),
            "order": int(case["order"]), "evaluations": int(case["evaluations"]),
            "mu": float(case["mu"]), "independent_seeds": len(seed_ids),
        }
        for method in METHODS:
            for metric in METRICS:
                values_ms = np.array([
                    aggregated[(case_id, seed_no, method)][metric] / 1e6
                    for seed_no in seed_ids
                ])
                timing_rows.append({
                    **info, "method": method, "metric": metric,
                    "median_ms": float(np.median(values_ms)),
                    "iqr_low_ms": float(np.quantile(values_ms, .25)),
                    "iqr_high_ms": float(np.quantile(values_ms, .75)),
                    "mean_ms": float(np.mean(values_ms)),
                })
        for first, second in PAIRS:
            a = np.array([
                aggregated[(case_id, seed_no, first)][PRIMARY]
                for seed_no in seed_ids
            ])
            b = np.array([
                aggregated[(case_id, seed_no, second)][PRIMARY]
                for seed_no in seed_ids
            ])
            # first/second: >1 => second is faster.
            log_ratio = np.log(a) - np.log(b)
            effect = float(np.exp(np.mean(log_ratio)))
            ci_low, ci_high = bootstrap_log_ratio_ci(
                log_ratio, master_rng, bootstrap, alpha,
            )
            if len(seed_ids) >= min_inferential_seeds:
                p, test_kind = signflip_pvalue(
                    log_ratio, master_rng, permutations,
                )
            else:
                p, test_kind = None, "not_tested_insufficient_seeds"
            comparisons.append({
                **info, "method_a": first, "method_b": second,
                "speedup_a_over_b": effect,
                "ci95_low": ci_low, "ci95_high": ci_high,
                "median_paired_difference_ms": float(np.median((a - b) / 1e6)),
                "fraction_seeds_b_faster": float(np.mean(b < a)),
                "p_two_sided_unadjusted": p,
                "p_holm_familywise": None, "significant_holm": None,
                "test_kind": test_kind,
            })
    eligible = [i for i, row in enumerate(comparisons)
                if row["p_two_sided_unadjusted"] is not None]
    adjusted = holm_adjust([
        comparisons[i]["p_two_sided_unadjusted"] for i in eligible
    ])
    for index, p in zip(eligible, adjusted):
        comparisons[index]["p_holm_familywise"] = p
        comparisons[index]["significant_holm"] = p < alpha
    return timing_rows, comparisons


def scientific_report(metadata: dict, comparisons: list[dict], alpha: float) -> str:
    tested = [r for r in comparisons if r["p_holm_familywise"] is not None]
    significant = [r for r in tested if r["significant_holm"]]
    lines = [
        "# PLS solver backend study — machine-generated analysis",
        "",
        "**Interpretation:** findings apply to the sampled series and recorded "
        "computing environment, not all machines or problem sizes.",
        "",
        "## Pre-specified statistical design",
        "",
        "- Methods: SVD of D, symmetric eigendecomposition of D.T @ D, "
        "and direct banded Cholesky for exactly the same full PLS trends.",
        "- Primary outcome: wall-clock **setup plus M full fitted trends**, "
        "one measurement for each method within the same randomized block.",
        "- Independent inferential unit: data seed. Repeated measurements "
        "for the same seed are summarized by their median; neither "
        "repeated time blocks nor the M individual penalties are "
        "treated as independent observations.",
        "- Pairwise comparisons, for every pre-specified workload: "
        "SVD vs eigh, SVD vs Cholesky, eigh vs Cholesky.",
        "- Effect: geometric mean of the per-seed **time(A)/time(B)** ratios. "
        "Values >1 indicate that method B is faster; values <1 indicate A "
        "is faster. Confidence intervals are seed-level paired percentile "
        "bootstrap intervals and are **pointwise, not family-wise adjusted**.",
        "- Hypothesis H0: mean paired log time ratio equals zero. "
        "Two-sided paired sign-flip randomization test: exact for <=16 "
        "seeds, Monte Carlo otherwise (with plus-one p correction). "
        "It assumes exchangeable/symmetric paired log differences.",
        f"- Pre-specified family-wise level alpha={alpha:g}; "
        "Holm adjustment across **every pair in every workload** for "
        "the primary outcome. Secondary timing metrics are descriptive.",
        "- Missing blocks, failed numerical agreement, nonpositive times "
        "or incomplete data cause analysis to fail rather than quietly "
        "dropping observations.",
        "- Statistical significance is not practical importance; "
        "small runtime differences may be irrelevant despite small p-values. "
        "Multiple machines, sessions, software versions and independent "
        "confirmation are needed for generalizable performance claims.",
        "",
        "## Run characteristics",
        "",
        f"- Git revision: \`{metadata.get('git_revision')}\`",
        f"- Preset: \`{metadata['preset']}\`",
        f"- Data seeds: **{metadata['independent_seeds']}** per workload",
        f"- Timing blocks per seed: **{metadata['timing_blocks_per_seed']}**",
        f"- BLAS threads requested: **{metadata['environment']['blas_threads_requested']}**",
        f"- Python: \`{metadata['environment']['python']}\`, "
        f"NumPy: \`{metadata['environment']['numpy']}\`, "
        f"SciPy: \`{metadata['environment']['scipy']}\`",
        "",
        "## Inferential results",
        "",
        f"Adjusted tests: **{len(tested)}**; Holm-significant: "
        f"**{len(significant)}**. "
        "A low p-value describes evidence for these measured workloads, "
        "not a universal fastest default.",
        "",
        "| n | d | M | mu | Comparison A / B | G-mean time ratio A/B | "
        "95% CI (pointwise) | Holm p |",
        "|---:|---:|---:|---:|---|---:|---|---:|",
    ]
    for r in comparisons:
        p = r["p_holm_familywise"]
        formatted = "NA (insufficient seeds)" if p is None else f"{p:.4g}"
        lines.append(
            f"| {r['n']} | {r['order']} | {r['evaluations']} "
            f"| {r['mu']:g} | {r['method_a']} / {r['method_b']} "
            f"| {r['speedup_a_over_b']:.3f} "
            f"| [{r['ci95_low']:.3f}, {r['ci95_high']:.3f}] "
            f"| {formatted} |"
        )
    lines += [
        "", "## Publication cautions", "",
        "The unadjusted bootstrap intervals are provided as descriptive "
        "uncertainty summaries; **do not infer multiple-comparison-adjusted "
        "significance from whether they cover 1**. The predeclared "
        "Holm-adjusted p-values apply only to the primary total-time metric.",
        "The comparisons use identical generated datasets but all timing "
        "trials ran on the same machine/session. The randomization test "
        "is model-dependent evidence, not a causal guarantee or "
        "cross-hardware generalization.",
        "SVD currently remains the default for the original "
        "TrendSmoother/criterion-selection API. Backend choice and criterion "
        "selection are different computational problems.",
        "",
    ]
    return "\n".join(lines)


def tex_escape(value) -> str:
    return str(value).replace("_", r"\_")


def create_latex_tables(
    directory: Path, timing: list[dict], comparisons: list[dict],
) -> None:
    chosen_time = [r for r in timing if r["metric"] == PRIMARY]
    output = [r"\begin{tabular}{rrrrlrr}",
              r"\hline",
              r"$n$ & $d$ & $M$ & $\mu$ & Backend & Median (ms) & IQR (ms) \\",
              r"\hline"]
    for r in chosen_time:
        output.append(
            f"{r['n']} & {r['order']} & {r['evaluations']} & "
            f"{r['mu']:g} & {tex_escape(r['method'])} & "
            f"{r['median_ms']:.4f} & "
            f"[{r['iqr_low_ms']:.4f}, {r['iqr_high_ms']:.4f}] "
            + r"\\"
        )
    output += [r"\hline", r"\end{tabular}", ""]
    (directory / "paper_solver_timings.tex").write_text(
        "\n".join(output), encoding="utf-8",
    )
    output = [r"\begin{tabular}{rrrrlrr}",
              r"\hline",
              r"$n$ & $d$ & $M$ & $\mu$ & Comparison & Speedup & Holm $p$ \\",
              r"\hline"]
    for r in comparisons:
        p = r["p_holm_familywise"]
        output.append(
            f"{r['n']} & {r['order']} & {r['evaluations']} & "
            f"{r['mu']:g} & {tex_escape(r['method_a'])}/"
            f"{tex_escape(r['method_b'])} & "
            f"{r['speedup_a_over_b']:.3f} & "
            + (f"{p:.3g}" if p is not None else "NA") + " " + r"\\"
        )
    output += [r"\hline", r"\end{tabular}", ""]
    (directory / "paper_solver_speedups.tex").write_text(
        "\n".join(output), encoding="utf-8",
    )


def export_figures(directory: Path, timing: list[dict]) -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cases = sorted({(r["order"], r["evaluations"], r["mu"])
                    for r in timing if r["metric"] == PRIMARY})
    relevant = [
        c for c in cases if c[0] == 2 and c[2] == 0.0
    ] or cases
    palette = {"svd": "#2863AA", "eigh": "#D5973C", "cholesky": "#13877A"}
    generated = 0
    for d, m, mu in relevant:
        candidates = [
            r for r in timing
            if r["order"] == d and r["evaluations"] == m
            and r["mu"] == mu and r["metric"] == PRIMARY
        ]
        n_sizes = sorted({r["n"] for r in candidates})
        if len(n_sizes) < 2:
            continue
        fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
        for method in METHODS:
            sampled = sorted(
                (r for r in candidates if r["method"] == method),
                key=lambda r: r["n"],
            )
            ax.plot(
                [r["n"] for r in sampled],
                [r["median_ms"] for r in sampled],
                label=method, color=palette[method],
                linewidth=2, marker="o",
            )
        ax.set(
            xlabel="Series length n",
            ylabel="Setup + M full trends, median (ms, log scale)",
            title=f"Matched solver benchmark: d={d}, M={m}, mu={mu:g}",
        )
        ax.set_yscale("log")
        ax.grid(alpha=.25, axis="y")
        ax.legend(frameon=False, ncol=3)
        filename = f"full_fit_n_d{d}_M{m}_mu{mu:g}"
        for ext in ("svg", "png", "pdf"):
            fig.savefig(directory / (filename + "." + ext), dpi=170)
        plt.close(fig)
        generated += 1
        if generated >= 4:
            break
    return generated


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--bootstrap", type=int, default=4000)
    parser.add_argument("--permutations", type=int, default=20000)
    parser.add_argument("--alpha", type=float, default=.05)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)
    if args.bootstrap < 100 or args.permutations < 100 or not 0 < args.alpha < 1:
        parser.error("Require bootstrap/permutations >=100, 0<alpha<1.")
    output = args.output_dir or (args.input_dir / "analysis")
    output.mkdir(parents=True, exist_ok=True)
    raw_file = args.input_dir / "raw_measurements.csv"
    metadata_file = args.input_dir / "study_metadata.json"
    raw = load_csv(raw_file)
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    aggregated = validate_and_aggregate(raw, metadata)
    timing, comparisons = summarize(
        aggregated, metadata, seed=args.seed, bootstrap=args.bootstrap,
        permutations=args.permutations, alpha=args.alpha,
    )
    write_csv(output / "timing_summary.csv", timing)
    write_csv(output / "paired_comparisons.csv", comparisons)
    (output / "results.md").write_text(
        scientific_report(metadata, comparisons, args.alpha),
        encoding="utf-8",
    )
    create_latex_tables(output, timing, comparisons)
    images = 0 if args.no_plots else export_figures(output, timing)
    manifest = {
        "analysis_protocol": "paired_signflip_holm_v1",
        "raw_sha256": hashlib.sha256(raw_file.read_bytes()).hexdigest(),
        "metadata_sha256": hashlib.sha256(metadata_file.read_bytes()).hexdigest(),
        "alpha": args.alpha, "bootstrap": args.bootstrap,
        "signflip_permutations": args.permutations, "analysis_seed": args.seed,
        "primary_metric": PRIMARY, "methods": list(METHODS),
        "all_primary_comparisons_holm_adjusted": True,
        "pointwise_ci_not_multiplicity_adjusted": True,
        "figures_exported": images,
    }
    (output / "analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(
        f"Analyzed {len(metadata['workload_cases'])} matched workloads, "
        f"wrote {len(comparisons)} paired comparisons, "
        f"{images} figures (SVG/PNG/PDF), LaTeX tables and results.md to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
