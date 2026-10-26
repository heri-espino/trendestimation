#!/usr/bin/env python3
"""Reproducible solver x criterion x coordinate study for fixed-mu PLS.

Run from the repository root:
  python benchmarks/criterion_coordinate_matrix.py --preset smoke
  python benchmarks/criterion_coordinate_matrix.py --preset quick --seeds 3 --repeats 4
  python benchmarks/criterion_coordinate_matrix.py --preset full --seeds 10 --repeats 7

Each cell measures an ACTUAL optimizer-free finite grid search with:
  solver: SVD, symmetric eigendecomposition Q=D.T@D, banded Cholesky
  criterion: CV, GCV, AICc, BIC (same formulas; fixed numeric mu)
  coordinate: log-lambda, S on a mapped grid, S on a uniform native grid.

Banded Cholesky computes EDF/leverage by solving for all columns of H,
not by borrowing the SVD eigenvalues. Inverting S for Cholesky also
uses Cholesky trace solves; these are part of its timed work.
No claim is made about the default library's auto/derivative optimizer;
that is a DIFFERENT workload with a different number of evaluations.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from math import comb
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import scipy
from scipy.linalg import cho_solve_banded, cholesky_banded, eigh, svd
from scipy.optimize import brentq
from scipy.special import binom
from threadpoolctl import threadpool_info, threadpool_limits

from trendestimation.core import difference_matrix
from trendestimation.solvers import _penalty_lower_bands

METHODS = ("svd", "eigh", "cholesky")
CRITERIA = ("cv", "gcv", "aicc", "bic")
COORDINATES = ("lambda", "s_mapped", "s_uniform")
FIELDS = ("preset", "n", "d", "mu", "case", "seed", "block", "criterion",
          "solver", "coordinate", "candidates", "setup_ns", "inversion_ns",
          "score_ns", "postmap_ns", "end_to_end_ns", "score_calls",
          "inverse_calls", "trace_calls", "selected_lambda",
          "selected_s", "selected_score", "lambda_roundtrip_max_log_error")
DEFAULT_OUTPUT = Path("build/criterion-coordinate-study")


def workload(preset: str) -> tuple[list[tuple[int, int, float]], int]:
    if preset == "smoke":
        return [(28, 2, 0.0)], 7
    if preset == "quick":
        return [(40, 1, 0.0), (40, 2, 0.0),
                (64, 2, 0.1), (64, 3, 0.0)], 13
    return [(40, 1, 0.0), (40, 2, 0.0), (64, 2, 0.1),
            (64, 3, 0.0), (96, 2, 0.0), (96, 3, 0.1),
            (128, 2, 0.0), (128, 4, 0.0)], 21


def sample_data(n: int, d: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(np.random.SeedSequence([seed, n, d]))
    x = np.linspace(0.0, 1.0, n)
    return (0.5 * np.sin(9*x) + 0.3 * np.cos(17*x)
            + 0.4*x + rng.normal(0.0, 0.25, n))


class Scorer:
    """One prepared PLS backend; scores are conditional on fixed mu."""

    def __init__(self, n: int, d: int, y: np.ndarray,
                 mu: float, method: str):
        self.n, self.d, self.method = n, d, method
        self.y = np.asarray(y, dtype=float)
        self.ref = mu * binom(np.arange(n, dtype=float), d)
        self.centered = self.y - self.ref
        self.trace_calls = 0
        self.score_calls = 0
        self.identity = None
        self.band = None
        self.values = None
        self.vectors = None
        self.coordinates = None
        self.squares = None

        if method == "cholesky":
            self.band = _penalty_lower_bands(n, d)
            self.identity = np.eye(n)
        else:
            D = difference_matrix(n, d)
            if method == "svd":
                _, sigma, vt = svd(D, full_matrices=True,
                                   check_finite=True)
                values = np.r_[sigma*sigma, np.zeros(d)]
                vectors = vt.T
            elif method == "eigh":
                values, vectors = eigh(D.T @ D, check_finite=True)
                # Nullspace is known algebraically: correct the d smallest
                # numerically perturbed eigenvalues, without pretending
                # that an eig(Q) solve has the same stability as svd(D).
                values[:d] = 0.0
                if np.any(values[d:] <= 0):
                    raise ArithmeticError("eigh did not resolve Q's positive spectrum")
            else:
                raise ValueError(method)
            self.values = values
            self.vectors = vectors
            self.coordinates = vectors.T @ self.centered
            self.squares = vectors*vectors

    def _h_cholesky(self, lam: float) -> np.ndarray:
        assert self.band is not None and self.identity is not None
        ab = self.band * lam
        ab[0] += 1.0
        lower = cholesky_banded(ab, lower=True,
                                check_finite=False, overwrite_ab=True)
        return cho_solve_banded((lower, True), self.identity,
                                check_finite=False)

    def smoothness(self, lam: float) -> float:
        self.trace_calls += 1
        if lam == 0:
            return 0.0
        if self.method == "cholesky":
            trace = float(np.trace(self._h_cholesky(lam)))
            # Clip only rounding-level deviations, not data-dependent
            # discrepancies; never conflate this with Guerrero's index.
            value = (self.n - trace)/(self.n - self.d)
            return float(np.clip(value, 0.0, 1.0))
        assert self.values is not None
        z = lam * self.values
        return float(np.mean((z/(1.0+z))[self.values > 0]))

    def inverse_s(self, target: float) -> float:
        if not 0.0 < target < 1.0:
            raise ValueError("interior target S is required")
        # The brackets are deliberately common to all backends. A case
        # that cannot be bracketed is reported, never silently clipped.
        lo, hi = -34.0, 34.0
        f = lambda x: self.smoothness(float(np.exp(x))) - target
        if f(lo) > 0 or f(hi) < 0:
            raise ArithmeticError("S inversion out of finite search bracket")
        return float(np.exp(brentq(f, lo, hi, xtol=1e-10, maxiter=120)))

    def score(self, lam: float, criterion: str) -> float:
        self.score_calls += 1
        n = self.n
        if self.method == "cholesky":
            H = self._h_cholesky(lam)
            residual = self.centered - H @ self.centered
            rss = float(residual@residual)
            edf = float(np.trace(H))
            if criterion == "cv":
                denom = 1.0 - np.diag(H)
                if np.min(denom) <= 1e-12:
                    return float("inf")
                q = residual / denom
                return float(np.mean(q*q))
        else:
            assert self.values is not None and self.vectors is not None
            assert self.coordinates is not None and self.squares is not None
            alpha = 1.0/(1.0 + lam*self.values)
            w = 1.0-alpha
            residual_coeffs = w * self.coordinates
            rss = float(residual_coeffs@residual_coeffs)
            edf = float(np.sum(alpha))
            if criterion == "cv":
                residual = self.vectors @ residual_coeffs
                denom = self.squares @ w
                if np.min(denom) <= 1e-12:
                    return float("inf")
                q = residual/denom
                return float(np.mean(q*q))
        if criterion == "gcv":
            denom = 1.0-edf/n
            return float((rss/n)/denom**2) if denom > 1e-10 else float("inf")
        if rss <= np.finfo(float).eps * max(1.0, float(self.centered@self.centered)):
            return float("inf")
        log_rss = float(np.log(rss/n))
        if criterion == "bic":
            return log_rss + edf*np.log(n)/n
        if criterion == "aicc":
            denom = n-edf-2
            return log_rss+(2*edf+1)/denom if denom > 0 else float("inf")
        raise ValueError(criterion)


def run_cell(*, n: int, d: int, mu: float, y: np.ndarray,
             criterion: str, solver: str, coordinate: str,
             candidates: np.ndarray, s_mapped: np.ndarray,
             seed: int, case: int, block: int, preset: str) -> dict:
    t0 = perf_counter_ns()
    backend = Scorer(n, d, y, mu, solver)
    t1 = perf_counter_ns()
    inversion_calls = 0
    error = 0.0
    if coordinate == "lambda":
        penalties = candidates
    else:
        target = s_mapped if coordinate == "s_mapped" else np.linspace(
            0.025, 0.975, len(candidates))
        penalties_list = []
        for s in target:
            lam = backend.inverse_s(float(s))
            penalties_list.append(lam)
            inversion_calls += 1
        penalties = np.asarray(penalties_list, dtype=float)
        if coordinate == "s_mapped":
            error = float(max(abs(np.log(a/b))
                              for a, b in zip(penalties, candidates)))
    t2 = perf_counter_ns()
    scores = np.asarray([backend.score(float(lam), criterion)
                         for lam in penalties])
    t3 = perf_counter_ns()
    good = np.isfinite(scores)
    if not np.any(good):
        raise ArithmeticError("No finite score in candidate search")
    winner = int(np.argmin(np.where(good, scores, np.inf)))
    lam_selected = float(penalties[winner])
    s_selected = backend.smoothness(lam_selected)
    t4 = perf_counter_ns()
    return dict(preset=preset, n=n, d=d, mu=mu, case=case, seed=seed,
                block=block, criterion=criterion, solver=solver,
                coordinate=coordinate, candidates=len(penalties),
                setup_ns=t1-t0, inversion_ns=t2-t1,
                score_ns=t3-t2, postmap_ns=t4-t3,
                end_to_end_ns=t4-t0, score_calls=backend.score_calls,
                inverse_calls=inversion_calls, trace_calls=backend.trace_calls,
                selected_lambda=lam_selected, selected_s=s_selected,
                selected_score=float(scores[winner]),
                lambda_roundtrip_max_log_error=error)


def check_backend_agreement(n: int, d: int, y: np.ndarray, mu: float,
                            penalties: np.ndarray) -> None:
    models = {m: Scorer(n, d, y, mu, m) for m in METHODS}
    for lam in (float(penalties[1]), float(penalties[-2])):
        for criterion in CRITERIA:
            scores = {m: mod.score(lam, criterion)
                      for m, mod in models.items()}
            baseline = scores["svd"]
            for method, result in scores.items():
                if not np.isfinite(result) or not np.isclose(
                    result, baseline, rtol=3e-4, atol=3e-6,
                ):
                    raise AssertionError(
                        f"score mismatch n={n},d={d},mu={mu},lambda={lam},"
                        f"{criterion},{method}: {result} vs {baseline}")
        for method, model in models.items():
            s0 = models["svd"].smoothness(lam)
            s1 = model.smoothness(lam)
            if not np.isclose(s0, s1, atol=5e-7, rtol=5e-7):
                raise AssertionError(
                    f"smoothness mismatch: {method} {s1} vs {s0}")


def collect(preset: str, seeds: int, repeats: int, base_seed: int) -> list[dict]:
    cases, count = workload(preset)
    results = []
    for case_id, (n, d, mu) in enumerate(cases):
        penalties = np.geomspace(0.015, 3500.0, count)
        for seed_index in range(seeds):
            data_seed = base_seed + seed_index
            y = sample_data(n, d, data_seed)
            check_backend_agreement(n, d, y, mu, penalties)
            # Experimental controls only: a fixed canonical SVD map
            # defines the S values corresponding to identical lambda
            # candidates. Its cost is excluded from every timed cell;
            # this mapped experiment isolates per-method inverse overhead.
            canonical = Scorer(n, d, y, mu, "svd")
            mapped = np.asarray([canonical.smoothness(float(lam))
                                 for lam in penalties])
            jobs = [(criterion, solver, coordinate)
                    for criterion in CRITERIA for solver in METHODS
                    for coordinate in COORDINATES]
            for block in range(repeats):
                rng = np.random.default_rng(
                    np.random.SeedSequence([base_seed, case_id, seed_index, block]))
                order = rng.permutation(len(jobs))
                for pos in order:
                    criterion, solver, coordinate = jobs[int(pos)]
                    results.append(run_cell(
                        n=n, d=d, mu=mu, y=y, criterion=criterion,
                        solver=solver, coordinate=coordinate,
                        candidates=penalties, s_mapped=mapped,
                        seed=data_seed, case=case_id, block=block, preset=preset))
        print(f"[coordinate-study] case {case_id+1}/{len(cases)}"
              f" n={n} d={d} mu={mu} rows={len(results)}", flush=True)
    return results


def summarize(rows: list[dict]) -> list[dict]:
    buckets = defaultdict(list)
    for row in rows:
        key = (row["n"], row["d"], row["mu"], row["criterion"],
               row["solver"], row["coordinate"])
        buckets[key].append(row)
    out = []
    for key, group in sorted(buckets.items()):
        values = np.asarray([v["end_to_end_ns"]/1e6 for v in group])
        times = np.asarray([v["inversion_ns"]/1e6 for v in group])
        scores = np.asarray([v["selected_score"] for v in group])
        reference = {(v["seed"], v["block"]): v["selected_score"]
                     for v in rows if (v["n"], v["d"], v["mu"],
                     v["criterion"], v["solver"], v["coordinate"]) ==
                     (*key[:5], "lambda")}
        losses = [v["selected_score"]-reference[(v["seed"], v["block"])]
                  for v in group]
        out.append(dict(
            zip(("n", "d", "mu", "criterion", "solver", "coordinate"), key),
            trials=len(group),
            median_ms=float(np.median(values)),
            mad_ms=float(np.median(np.abs(values-np.median(values)))),
            median_inversion_ms=float(np.median(times)),
            median_score_difference_vs_lambda=float(np.median(losses)),
            max_roundtrip_log_error=float(max(v["lambda_roundtrip_max_log_error"]
                                             for v in group)),
        ))
    return out


def git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
            timeout=3, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("smoke", "quick", "full"),
                        default="smoke")
    parser.add_argument("--seeds", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261025)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if min(args.seeds, args.repeats, args.threads) < 1:
        parser.error("--seeds, --repeats and --threads must all be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with threadpool_limits(limits=args.threads):
        rows = collect(args.preset, args.seeds, args.repeats, args.seed)
        summary = summarize(rows)
        settings = dict(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            python=sys.version, platform=platform.platform(),
            numpy=np.__version__, scipy=scipy.__version__,
            blas_thread_limit=args.threads,
            threadpool_info=threadpool_info(),
            git_revision=git_head(), preset=args.preset, seeds=args.seeds,
            repeats=args.repeats, random_seed=args.seed, methods=METHODS,
            criteria=CRITERIA, coordinates=COORDINATES,
            outcome="grid-search minimum of identical PLS criteria",
            note="S_mapped canonical candidate preparation excluded from timed cells;"
                 " all backend-specific S inversions, score evaluations and"
                 " winner-to-S conversions included; no timings fabricated.",
        )
    with (args.output_dir/"raw_trials.csv").open(
        "w", encoding="utf-8", newline="",
    ) as handle:
        writer = csv.DictWriter(handle, FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with (args.output_dir/"summary.csv").open(
        "w", encoding="utf-8", newline="",
    ) as handle:
        writer = csv.DictWriter(handle, list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    (args.output_dir/"environment.json").write_text(
        json.dumps(settings, indent=2, default=str)+"\n", encoding="utf-8")
    print(f"Saved {len(rows)} trials to {args.output_dir}")


if __name__ == "__main__":
    main()
