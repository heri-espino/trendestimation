"""Reproducible notebook illustrations of lambda and normalized smoothness S.

A bounded S-grid is converted to penalties ONCE and reused for all classical
criteria. Exact S=0/1 map to lambda=0/infinity; no artificial clipping.
Timing illustrations are not controlled backend or publication benchmarks.
"""
from __future__ import annotations

from time import perf_counter

import numpy as np

from .core import TrendSmoother
from .criteria import select_lambda


def notebook_s_grid(*, high_tail=True):
    """Return eleven deciles from 0 through 1, optionally enriched near 1.

    Endpoints are exact, while 0.999999 is a genuine finite-penalty point.
    """
    points = np.linspace(0.0, 1.0, 11)
    if high_tail:
        points = np.r_[points, [0.95, 0.99, 0.999, 0.9999, 0.999999]]
    return np.unique(points)


def show_dual_coordinate_gallery(series=None, *, order=2, mu=0.0, max_points=60):
    """Plot full S range and CV/GCV/AICc/BIC scores on identical penalty grids.

    Lambda=0 and +infinity are in the evaluated grid. The left log-lambda
    panels cannot display either endpoint; the right S panels display both.
    """
    import matplotlib.pyplot as plt

    x = np.linspace(0, 1, max_points)
    fallback = (0.65*np.sin(9*x) + 0.4*x +
                np.random.default_rng(2026).normal(0, 0.24, max_points))
    context = "independent seeded synthetic series"
    if series is None:
        y = fallback
    else:
        try:
            raw = np.asarray(series, dtype=float).reshape(-1)
            if raw.size < 12 or not np.all(np.isfinite(raw)):
                raise ValueError("invalid data for plotting")
            y = raw[-max_points:]
            context = ("same series" if raw.size <= max_points else
                       f"last {max_points} observations of the notebook series")
        except (ValueError, TypeError):
            y = fallback
            context = "seeded fallback for nonnumeric notebook input"

    d = min(int(order), len(y) - 2)
    if d < 1:
        raise ValueError("difference order must be positive")
    smoother = TrendSmoother(len(y), order=d)
    targets = notebook_s_grid()
    penalties = np.asarray([
        smoother.lambda_for_smoothness(float(s)) for s in targets
    ])
    recovered = np.asarray([smoother.smoothness(float(lam)) for lam in penalties])
    np.testing.assert_allclose(recovered, targets, atol=1e-10, rtol=0)
    assert penalties[0] == 0 and np.isposinf(penalties[-1])
    print(f"Paired coordinates: {context}; n={len(y)}, d={d}, mu={mu:g}")
    print(f"Normalized S grid: {np.array2string(targets, precision=6)}")
    print("S=0 maps to lambda=0; S=1 maps to lambda=+infinity.")
    print("Near-1 targets: " + ", ".join(
        f"S={s:.6f} -> lambda={lam:.6g}" for s, lam in zip(targets[-6:-1], penalties[-6:-1])
    ))
    print(f"Maximum inversion / round-trip error: {np.max(np.abs(targets-recovered)):.3g}")

    interior = (penalties > 0) & np.isfinite(penalties)
    fig, axs = plt.subplots(1, 2, figsize=(12.3, 3.9), layout="constrained")
    axs[0].semilogx(penalties[interior], targets[interior], "o-",
                    color="#205fd4", lw=2, ms=4)
    axs[0].set(xlabel="Penalty lambda (log scale)", ylabel="Normalized S",
               title="Construct a full [0, 1] S-grid, invert once")
    axs[1].plot(targets[interior], penalties[interior], "o-",
                color="#138b94", lw=2, ms=4)
    axs[1].set_yscale("log")
    axs[1].set(xlabel="Normalized S", ylabel="Mapped penalty lambda (log scale)",
               title="Extra samples resolve the S -> 1 tail")
    axs[1].set_xlim(0, 1)
    for ax in axs:
        ax.grid(alpha=.22)
    fig.suptitle("Exact endpoints S=0 (lambda=0) and S=1 (lambda=inf) are scored below",
                 fontsize=10)
    plt.show()

    # Reuse this single converted penalty grid for all four criterion searches.
    names = ("cv", "gcv", "aicc", "bic")
    fig, axes = plt.subplots(4, 2, figsize=(12, 14.6), layout="constrained")
    for row, criterion in enumerate(names):
        result = select_lambda(smoother, y, criterion=criterion, mu=mu,
                               grid=penalties, search_space="lambda")
        scores = result.scores
        finite = np.isfinite(scores)
        left = finite & interior
        right = finite
        for ax, xx, mask, col in (
            (axes[row, 0], penalties, left, "#205fd4"),
            (axes[row, 1], recovered, right, "#138b94"),
        ):
            ax.plot(xx[mask], scores[mask], marker="o", color=col, ms=3.7, lw=2)
            ax.grid(alpha=.22)
            ax.set(ylabel=f"{criterion.upper()} (smaller is better)",
                   title=f"{criterion.upper()} — identical penalty candidates")
        axes[row, 0].set(xlabel="Penalty lambda (log scale)")
        axes[row, 0].set_xscale("log")
        axes[row, 1].set(xlabel="Normalized S, including endpoints", xlim=(-.02, 1.02))
        optimum = int(np.argmin(np.where(finite, scores, np.inf)))
        axes[row, 1].scatter([recovered[optimum]], [scores[optimum]],
                             color="#bf5268", zorder=6, s=48)
        if interior[optimum]:
            axes[row, 0].scatter([penalties[optimum]], [scores[optimum]],
                                 color="#bf5268", zorder=6, s=48)
        else:
            axes[row, 0].text(.03, .93, "Best at endpoint (0 or inf)",
                              transform=axes[row, 0].transAxes, va="top", fontsize=9)
        print(f"{criterion.upper():>4}: lambda={result.lambda_:11.6g}, "
              f"S={result.smoothness:.6g}, score={result.score:.6g}")
    plt.show()
    print("Left log-lambda plots omit 0 and infinity as coordinates, NOT as "
          "evaluated candidates. Right S plots include those endpoints. "
          "CV can be infinite at S=0 because unregularized LOOCV is undefined.")

    # Same S candidates, exactly the same lambda points and score definitions.
    # One workflow performs S inversion ONCE per full 4-criterion sweep;
    # the alternative public S-selector repeats inversion for EACH criterion.
    def mapped_penalty_sweep():
        grid = np.asarray([
            smoother.lambda_for_smoothness(float(s)) for s in targets])
        return [select_lambda(smoother, y, criterion=c, mu=mu,
                              search_space="lambda", grid=grid) for c in names]

    def direct_s_sweep():
        return [select_lambda(smoother, y, criterion=c, mu=mu,
                              search_space="smoothness", grid=targets) for c in names]

    paired = (mapped_penalty_sweep(), direct_s_sweep())
    for left_result, right_result in zip(*paired):
        np.testing.assert_allclose(left_result.scores, right_result.scores,
                                   atol=1e-8, rtol=1e-8)
    times = []
    for func in (mapped_penalty_sweep, direct_s_sweep):
        func()  # warm up
        trials = []
        for _ in range(5):
            start = perf_counter()
            func()
            trials.append((perf_counter()-start)*1e3)
        times.append(float(np.median(trials)))
    fig, ax = plt.subplots(figsize=(10.0, 3.7), layout="constrained")
    ax.bar(["Map S -> lambda once,\nthen score four criteria",
            "Repeat S inversion in\neach of four selectors"], times,
           color=["#205fd4", "#138b94"])
    ax.set(ylabel="Milliseconds, median of 5 local repetitions",
           title="Exactly matched points: reuse mapped lambda grid")
    ax.grid(axis="y", alpha=.2)
    plt.show()
    print(f"Four-criterion sweep, lambda-map-once: {times[0]:.3f} ms; "
          f"direct S selector (repeated mapping): {times[1]:.3f} ms.")
    print("Both evaluate the same 16 penalties. This small, single-session "
          "measurement isolates a reusable-grid workflow, not the general "
          "speed of every optimization method or back end.")
