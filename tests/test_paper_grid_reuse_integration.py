"""Check paper/website benchmark claims against archived measured CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from trendestimation import PreparedPLSSolver, TrendSmoother, fit_penalized, select_lambda

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "paper/benchmarks/grid_reuse_reference/gcv_grid_timings.csv"


def read_rows():
    with BENCH.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def row(rows, d, mu, R, method, reuse, M=11):
    hits = [
        r for r in rows
        if int(r["n"]) == 48 and int(r["d"]) == d and int(r["M"]) == M
        and int(r["R"]) == R and float(r["mu"]) == mu
        and r["grid_policy"] == "log_lambda"
        and r["reuse"] == reuse and r["method"] == method
    ]
    assert len(hits) == 1
    return float(hits[0]["total_median_s"])


def test_reported_paper_d_and_mu_results_are_grounded():
    records = read_rows()
    paper = (ROOT / "paper/sections/gcv_grid_reuse.tex").read_text(encoding="utf-8")
    for d in range(1, 5):
        for mu in (0.0, 0.15):
            svd = row(records, d, mu, 1, "spectral", "warm")
            chol = row(records, d, mu, 1, "banded_cholesky", "warm")
            expected = (
                f"{d} & {mu:.2f} & {svd*1000:.3f} & "
                f"{chol*1000:.3f} & {svd/chol:.2f}"
            )
            assert expected in paper, expected
            # Only an observed benchmark result, not a solver contract.
            assert svd > 0 and chol > 0
    assert "Windows-VM" in paper
    assert "GitHub-hosted Linux runner" in paper


def test_paper_reuse_table_from_real_measurements():
    records = read_rows()
    paper = (ROOT / "paper/sections/gcv_grid_reuse.tex").read_text(encoding="utf-8")
    for method, label in (
        ("spectral", "SVD"),
        ("banded_cholesky", "Banded Cholesky"),
        ("banded", "General banded"),
        ("dense_cholesky", "Dense Cholesky"),
    ):
        cold = row(records, 2, 0., 4, method, "cold")
        warm = row(records, 2, 0., 4, method, "warm")
        expected = (
            f"{label} & {cold*1000:.3f} & "
            f"{warm*1000:.3f} & {cold/warm:.2f}"
        )
        assert expected in paper, expected


def test_paper_and_website_register_benchmarks():
    source = (ROOT / "paper/main.tex").read_text(encoding="utf-8")
    index = (ROOT / "docs/index.rst").read_text(encoding="utf-8")
    assert r"\input{sections/gcv_grid_reuse}" in source
    assert "grid_reuse_selection" in index
    assert (ROOT / "docs/grid_reuse_selection.rst").is_file()


def test_fit_only_default_keeps_selection_spectral_and_accurate():
    y = np.random.default_rng(123).normal(size=38)
    fit_only = PreparedPLSSolver(len(y), order=3)
    assert fit_only.method == "cholesky"
    spectral = TrendSmoother(len(y), order=3)
    for mu in (0.0, 0.15):
        fitted = fit_penalized(y, lambda_=12.0, order=3, mu=mu)
        target = spectral.fit(y, lambda_=12.0, mu=mu)
        np.testing.assert_allclose(fitted, target.trend, rtol=2e-7, atol=2e-7)
    selection = select_lambda(spectral, y, criterion="gcv", mu=0.15)
    assert selection.lambda_ >= 0
    assert np.isfinite(selection.score)
