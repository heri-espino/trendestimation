"""Experiment011 independent status/paired-score audit.

Never changes raw measured times. Never fabricates a missing method,
replaces a failed CHOLMOD dependency, or certifies high-precision accuracy
from float64 selected scores. Run independently on any archived block:
    python paper/benchmarks/experiment011/verify.py path/to/block000
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path


SCENARIOS = (
    "one_s_one_series", "grid_one_series",
    "one_s_multiple_series", "grid_multiple_series"
)
POLICIES = ("direct_s", "mapped_lambda")
FLOAT64_SCORE_REL_TOL = 1e-7
SELECTED_S_ABS_TOL = 1e-10


def _f(row: dict, key: str) -> float:
    try:
        return float(row[key])
    except (TypeError, ValueError, KeyError):
        return math.nan


def audit_rows(rows: list[dict], manifest: dict, environment: dict) -> dict:
    case = manifest["case"]
    methods = manifest["method_order"]
    repeat_count = case["repeats_per_block"]
    if not methods or len(set(methods)) != len(methods):
        raise ValueError("Duplicate/empty method list")
    if environment["n"] != case["n"] or environment["d"] != case["d"]:
        raise ValueError("n/d not the declared experiment")
    if environment["criterion"] != case["criterion"]:
        raise ValueError("Criterion mismatch")
    if environment["denominator"] != case["grid_denominator"]:
        raise ValueError("Candidate grid mismatch")
    if environment["R"] != case["series_count"]:
        raise ValueError("R mismatch")
    if environment["repeats"] != repeat_count:
        raise ValueError("Repeat-count mismatch")
    if environment["blas_threads"] != 1:
        raise ValueError("Must be one BLAS thread")
    if environment["methods"] != methods:
        raise ValueError("Method execution order mismatch")
    if environment["git_sha"] != manifest["source_commit"]:
        raise ValueError("Recorded source commit mismatch")
    expected = {
        (method, coord, scenario)
        for method in methods for coord in POLICIES for scenario in SCENARIOS
    }
    actual = defaultdict(list)
    statuses = Counter()
    for row in rows:
        method, coord, scenario = (
            row.get("method"), row.get("coordinate"), row.get("workload")
        )
        key = (method, coord, scenario)
        if key not in expected:
            raise ValueError("Unexpected measured design key " + str(key))
        if (
            int(row["n"]) != case["n"]
            or int(row["d"]) != case["d"]
            or row["criterion"] != case["criterion"]
            or int(row["grid_denominator"]) != case["grid_denominator"]
        ):
            raise ValueError("Measured design differs from the declared case")
        nr = 1 if scenario.endswith("one_series") else case["series_count"]
        m = 1 if scenario.startswith("one_s") else case["grid_denominator"]
        if int(row["R"]) != nr or int(row["M"]) != m:
            raise ValueError("Wrong number of series/candidates for workload")
        status = row["status"]
        statuses[status] += 1
        if status == "ok":
            for field in ("total_cold_s", "total_warm_s", "selected_s", "selected_score"):
                value = _f(row, field)
                if not math.isfinite(value):
                    raise ValueError("Successful row has nonfinite " + field)
            if _f(row, "total_cold_s") <= 0:
                raise ValueError("Nonpositive measured time")
            if not 0 <= _f(row, "selected_s") <= 1:
                raise ValueError("Selected smoothness outside [0,1]")
            if int(row["repeat"]) not in range(repeat_count):
                raise ValueError("Successful row has wrong repeated-block index")
        else:
            if int(row["repeat"]) not in (-1, *range(repeat_count)):
                raise ValueError("Unexpected failure/repeat index")
        actual[key].append(row)
    if set(actual) != expected:
        raise ValueError("Missing complete method/coordinate/workload cells")
    for key, cells in actual.items():
        ids = [int(row["repeat"]) for row in cells]
        if ids == [-1]:
            if cells[0]["status"] == "ok":
                raise ValueError("Successful method unexpectedly marked skipped")
        elif sorted(ids) != list(range(repeat_count)):
            raise ValueError("Incomplete or duplicate repeat IDs in "+str(key))

    paired = defaultdict(dict)
    for row in rows:
        if row["status"] == "ok":
            key = (row["coordinate"], row["workload"], int(row["repeat"]))
            paired[key][row["method"]] = row
    comparisons, issues = [], []
    for key, group in sorted(paired.items()):
        if len(group) < 2:
            continue
        reference_name = "spectral_svd" if "spectral_svd" in group else next(iter(group))
        reference = group[reference_name]
        ref_s = _f(reference, "selected_s")
        ref_score = _f(reference, "selected_score")
        for method, row in sorted(group.items()):
            if method == reference_name:
                continue
            s_diff = abs(_f(row, "selected_s") - ref_s)
            # Complete criteria may differ by lambda-INDEPENDENT MLE
            # determinant offsets; the selected minimizer is comparable
            # but the raw absolute ML value is not.
            same_score_basis = case["criterion"] != "mle"
            score_rel_diff = (
                abs(_f(row, "selected_score") - ref_score) /
                max(1.0, abs(ref_score))
                if same_score_basis else None
            )
            parity = (s_diff <= SELECTED_S_ABS_TOL and
                      (score_rel_diff is None or
                       score_rel_diff <= FLOAT64_SCORE_REL_TOL))
            comparisons.append({
                "coordinate": key[0], "workload": key[1], "repeat": key[2],
                "reference": reference_name, "method": method,
                "selected_s_difference": s_diff,
                "relative_score_difference": score_rel_diff,
                "score_levels_comparable": same_score_basis,
                "status": "float64_selected_score_parity" if parity
                          else "needs_independent_numerical_review",
            })
            if not parity:
                issues.append(f"{key}/{method}: selected S or score differs")
    all_ok = all(status == "ok" for status in statuses.elements())
    if issues:
        state = "needs_independent_numerical_review"
    elif not comparisons:
        state = "insufficient_paired_comparisons"
    elif not all_ok:
        state = "partial_success_with_skips_or_failures"
    else:
        state = "float64_parity_only_not_precision_certified"
    return {
        "experiment": "experiment011",
        "case_id": case["id"],
        "block": manifest["block"],
        "classification": state,
        "raw_rows": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "paired_method_comparisons": comparisons,
        "issues": issues,
        "has_all_methods_successful": all_ok,
        "interpretation": (
            "This checks only recorded success status, matching selected S "
            "and candidate score in float64 (except ML constants). It does "
            "not certify forward error at arbitrary penalty, estimate a "
            "universal crossover or establish statistical forecast accuracy."
        ),
    }


def audit_run(block_dir: Path) -> dict:
    root = Path(block_dir)
    manifest = json.loads((root / "experiment011_case.json").read_text())
    environment = json.loads((root / "measurements" / "environment.json").read_text())
    with (root / "measurements" / "raw_times.csv").open(newline="", encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    output = audit_rows(rows, manifest, environment)
    (root / "experiment011_qa.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf8"
    )
    return output


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("block_dir", type=Path)
    args = p.parse_args()
    result = audit_run(args.block_dir)
    print(result["classification"])
    print("Statuses:", result["status_counts"])
    print("Paired comparisons:", len(result["paired_method_comparisons"]))
    print("Audit:", args.block_dir / "experiment011_qa.json")


if __name__ == "__main__":
    main()
