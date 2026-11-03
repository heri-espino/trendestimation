"""Validate the frozen three-backend n=64 BIC publication timing table.

This code NEVER executes benchmarks. The 48 rows were copied verbatim from
immutable GitHub results branches and include source SHA and worker count.
Values in the manuscript are checked against independent raw records.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

DATA = Path(__file__).with_name("three_backend_bic_n64_d1.csv")
METHODS = ("spectral_svd", "naive_inverse",
           "sparse_cholesky_banded_trace")
WORKLOADS = ("one_s_one_series", "grid_one_series",
             "one_s_multiple_series", "grid_multiple_series")
POLICIES = ("direct_s", "mapped_lambda")

# Distinct source revisions and concurrency settings are part of the
# evidence; these timings are DESCRIPTIVE, not fair isolated speed ranks.
WORKERS = {"spectral_svd": 8, "naive_inverse": 8,
           "sparse_cholesky_banded_trace": 1}
SHA = {"spectral_svd": "bf4195c12e3c4b07e039df85971b303ab1d83d37",
       "naive_inverse": "bf4195c12e3c4b07e039df85971b303ab1d83d37",
       "sparse_cholesky_banded_trace":
           "f16f2bab6cfa37c6423c7f2d4554208efa9f683a"}

# Frozen medians in seconds, computed over exactly two recorded repeats.
# First candidate(s) then 100000-candidate workloads. All mapped_lambda.
EXPECTED_MAPPED = {
    "one_s_one_series": (0.00194855, 0.00112990, 0.00269520),
    "grid_one_series": (10.22646546, 15.16694395, 31.53344458),
    "one_s_multiple_series": (0.00188985, 0.00101520, 0.00273975),
    "grid_multiple_series": (11.68596480, 20.63986061, 37.14448288),
}


def load_and_validate():
    with DATA.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 48, f"Expected 48 measured rows, got {len(rows)}"
    by_method = defaultdict(dict)
    for row in rows:
        method = row["method"]
        assert method in METHODS, method
        assert row["parallel_workers"] == str(WORKERS[method])
        assert row["source_sha"] == SHA[method]
        assert (row["n"], row["d"], row["mu"], row["amplitude"],
                row["criterion"], row["grid_denominator"]) == (
                    "64", "1", "data", "high", "bic", "100000")
        assert row["status"] == "ok", row
        assert row["coordinate"] in POLICIES
        assert row["workload"] in WORKLOADS
        assert row["repeat"] in ("0", "1")
        expected_M = "100000" if row["workload"].startswith("grid_") else "1"
        expected_R = "2" if row["workload"].endswith("multiple_series") else "1"
        assert row["M"] == expected_M and row["R"] == expected_R
        key = (row["coordinate"], row["workload"], row["repeat"])
        assert key not in by_method[method], (method, key)
        by_method[method][key] = row
    assert all(len(by_method[m]) == 16 for m in METHODS)

    max_abs = {m: 0.0 for m in METHODS[1:]}
    max_rel = {m: 0.0 for m in METHODS[1:]}
    for key, spectral in by_method["spectral_svd"].items():
        for method in METHODS[1:]:
            candidate = by_method[method][key]
            ds = abs(float(candidate["selected_score"]) -
                     float(spectral["selected_score"]))
            scale = max(1.0, abs(float(spectral["selected_score"])))
            max_abs[method] = max(max_abs[method], ds)
            max_rel[method] = max(max_rel[method], ds/scale)
            assert abs(float(candidate["selected_s"]) -
                       float(spectral["selected_s"])) < 1e-13
    assert max_rel["naive_inverse"] < 3e-12
    assert max_rel["sparse_cholesky_banded_trace"] < 5e-13

    for workload, expected in EXPECTED_MAPPED.items():
        for method, target in zip(METHODS, expected):
            values = [float(by_method[method][
                ("mapped_lambda", workload, str(rep))]["total_cold_s"])
                for rep in (0, 1)]
            measured = median(values)
            assert abs(measured - target) < 1e-7, (
                method, workload, measured, target)
    return max_abs, max_rel


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.parse_args()
    a, r = load_and_validate()
    print("VERIFIED: 48/48 real observations, 16/16 per solver; "
          "same n,d,mu,criterion,seed and workload; different concurrency")
    for method in METHODS[1:]:
        print(method, "max_abs_score_difference", f"{a[method]:.12g}",
              "max_relative_score_difference", f"{r[method]:.12g}")
    for workload, values in EXPECTED_MAPPED.items():
        print(workload, "mapped-lambda median seconds:",
              dict(zip(METHODS, values)))


if __name__ == "__main__":
    main()
