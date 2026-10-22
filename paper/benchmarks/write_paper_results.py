"""Render provenance-labelled LaTeX tables from paper-only benchmark CSVs.

Run after both suites:
  python paper/benchmarks/write_paper_results.py
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = ("dense_fresh", "dense_cached", "spectral", "banded")
TRACE = tuple(s + "_trace" for s in FULL)


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Empty benchmark results: " + str(path))
    return rows


def tex_escape(value):
    characters = "\\&%$#_{}~^"
    replacements = (
        r"\textbackslash{}", r"\&", r"\%", r"\$", r"\#",
        r"\_", r"\{", r"\}", r"\textasciitilde{}",
        r"\textasciicircum{}",
    )
    return "".join(dict(zip(characters, replacements)).get(ch, ch)
                   for ch in str(value))


def summarize_full(rows):
    groups = {}
    for row in rows:
        if int(row["d"]) == 2 and abs(float(row["mu"])) < 1e-14:
            groups.setdefault((int(row["n"]), int(row["M"])), {})[row["method"]] = row
    groups = {key: group for key, group in groups.items()
              if all(method in group for method in FULL)}
    if not groups:
        raise ValueError("Missing complete d=2, fixed-mu full-fit data")
    choices = [key for key in sorted(groups) if key[1] in (1, 64)] or sorted(groups)
    choices = choices[:8]
    lines = [r"\begin{tabular}{rrrrrrr}", r"\toprule",
             r"$n$ & $M$ & Fresh & Cached & Spectral & Banded & $R$ \\",
             r"\midrule"]
    for n, m in choices:
        durations = [float(groups[(n, m)][method]["total_median_s"])*1000
                     for method in FULL]
        ratio = durations[0] / durations[2]
        lines.append(str(n) + " & " + str(m) + " & " +
                     " & ".join(f"{v:.3f}" for v in durations) +
                     f" & {ratio:.2f} " + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    return "\n".join(lines), max(float(x["max_error_banded"]) for x in rows)


def summarize_trace(rows):
    groups = {}
    for row in rows:
        groups.setdefault((int(row["n"]), int(row["d"]), int(row["M"])), {})[
            row["method"]] = row
    groups = {key: group for key, group in groups.items()
              if all(method in group for method in TRACE)}
    if not groups:
        raise ValueError("Missing complete EDF/trace data")
    choices = [key for key in sorted(groups) if key[1] == 2] or sorted(groups)
    choices = choices[:6]
    lines = [r"\begin{tabular}{rrrrrr}", r"\toprule",
             r"$n$ & $M$ & Fresh & Cached & Spectral & Banded \\",
             r"\midrule"]
    for n, d, m in choices:
        values = [1000 * float(groups[(n, d, m)][method]["total_median_s"])
                  for method in TRACE]
        lines.append(f"{n} & {m} & " + " & ".join(f"{v:.3f}" for v in values) +
                     " " + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    return "\n".join(lines), max(float(x["max_abs_trace_error"]) for x in rows)


def run(folder):
    fits = read_rows(folder / "full_fit_timings.csv")
    traces = read_rows(folder / "trace_timings.csv")
    env = json.loads((folder / "environment.json").read_text(encoding="utf-8"))
    table_full, err_full = summarize_full(fits)
    table_trace, err_trace = summarize_trace(traces)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "full_fit_table.tex").write_text(table_full, encoding="utf-8")
    (folder / "trace_table.tex").write_text(table_trace, encoding="utf-8")
    fields = [
        ("Platform", env.get("system", "not provided")),
        ("CPU", env.get("processor") or "not reported"),
        ("Logical CPUs", env.get("logical_cpus", "?")),
        ("NumPy", env.get("numpy", "?")),
        ("SciPy", env.get("scipy", "?")),
        ("BLAS threads", env.get("blas_threads", "?")),
        ("Repetitions", env.get("repeats", "?")),
        ("Preset", env.get("preset", "?")),
        ("Revision", env.get("git_revision", "local-unrecorded")),
    ]
    note = (r"\noindent\textbf{Measurement provenance:} "
            + "; ".join(f"{name}: {tex_escape(value)}" for name, value in fields)
            + ".\n\n"
            + r"\noindent Maximum observed absolute trend disagreement: "
            + "$" + format(err_full, ".3g") + "$; "
            + r"maximum EDF trace disagreement: "
            + "$" + format(err_trace, ".3g") + "$.\n")
    (folder / "benchmark_environment.tex").write_text(note, encoding="utf-8")
    (folder / "paper_result_manifest.json").write_text(
        json.dumps({"source": ["full_fit_timings.csv", "trace_timings.csv",
                               "environment.json"],
                    "max_full_fit_abs_error": err_full,
                    "max_trace_abs_error": err_trace,
                    "note": "Host-specific measurements, not universal speedups"},
                   indent=2), encoding="utf-8")
    print("Generated LaTeX tables and hardware notes in", folder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE/"results")
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == "__main__":
    main()
