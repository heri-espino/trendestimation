"""Preflight checks for Paper C's statistical (not computational) manuscript.

No simulation, image rendering, raw-data download or parameter search occurs.
Only the frozen TeX source graph and existing PDF figure paths are checked.
"""
from __future__ import annotations
import re
from pathlib import Path
import argparse
import json

PAPER=Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS=(
    "sections/introduction.tex",
    "sections/methods.tex",
    "sections/simulation_benchmarks.tex",
    "sections/precision_calibration.tex",
    "sections/real_data_study.tex",
    "sections/discussion.tex",
)
FORBIDDEN=(
    "generated/solver_table",
    "figures/backend_comparison",
    "sections/results}",
)
REQUIRED_LABELS=(
    "eq:pls","eq:S","eq:effective-df","eq:gls-mu","eq:reml-mean",
    "tab:sim-jerk-classical","tab:sim-joint","tab:ngsim-main",
    "fig:precision-spectrum","fig:precision-jerk",
    "fig:precision-calibration","fig:precision-effects",
    "fig:precision-robustness","fig:precision-endpoints",
    "fig:forecast","fig:jerk","fig:horizons","fig:criteria",
)
def check(paper:Path=PAPER)->dict:
    main=(paper/"main.tex").read_text(encoding="utf-8")
    actual=re.findall(r"\\input\{(sections/[^}]+)\}",main)
    expected=[p.removesuffix(".tex") for p in REQUIRED_SECTIONS]
    if actual!=expected:
        raise AssertionError(f"Incorrect actual reading order {actual}; expected {expected}")
    texts=[main]
    for rel in REQUIRED_SECTIONS:
        texts.append((paper/rel).read_text(encoding="utf-8"))
    all_text="\n".join(texts)
    for item in FORBIDDEN:
        if item in all_text:
            raise AssertionError(f"Computational benchmark cannot occur in article: {item}")
    labels=re.findall(r"\\label\{([^}]+)\}",all_text)
    duplicates=sorted({v for v in labels if labels.count(v)>1})
    if duplicates:
        raise AssertionError(f"Duplicate LaTeX labels: {duplicates}")
    missing=sorted(set(REQUIRED_LABELS)-set(labels))
    if missing:
        raise AssertionError(f"Missing required methodological/empirical labels: {missing}")
    cited_refs=re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",all_text)
    unbound=sorted(set(cited_refs)-set(labels))
    if unbound:
        raise AssertionError(f"References to missing labels: {unbound}")
    figure_names=re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{(figures/[^}]+)\}",all_text)
    if len(figure_names)!=10 or len(set(figure_names))!=10:
        raise AssertionError(f"Expected 10 unique scientific figures, found {figure_names}")
    for rel in figure_names:
        f=paper/rel
        if not f.is_file() or f.stat().st_size<100:
            raise FileNotFoundError(f"Missing publication figure {f}")
    if "1{,}296" not in all_text or "1{,}944" not in all_text:
        raise AssertionError("Known-jerk and calibration simulations must both be reported")
    if "200" not in all_text or "US-101" not in all_text or "I-80" not in all_text:
        raise AssertionError("Expanded two-site real NGSIM case is required")
    if "60.9131" not in all_text or "0.3480" not in all_text:
        raise AssertionError("Unfavorable classical-comparator outcomes must remain")
    if "72" not in all_text or "five" not in all_text:
        raise AssertionError("Scientific dependence caveats must be present")
    return {
        "status":"pass","section_order":REQUIRED_SECTIONS,
        "n_publication_figures":len(figure_names),
        "n_classical_solver_timing_figures":0,
        "figure_paths":figure_names,
        "n_unique_labels":len(labels),
        "n_crossrefs":len(cited_refs),
        "assurance":"TeX input path/content preflight only; PDF layout and reference resolution still require actual LaTeX build",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    result=check()
    print(json.dumps(result,indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        if args.out.exists():
            raise FileExistsError(args.out)
        args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
