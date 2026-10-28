"""Safety and model checks for the final measured Windows VM study.

No publication-sized benchmark is run automatically in normal CI.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _import(path: Path, name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def test_brent_newton_secant_bisect_correct_same_inverse():
    from trendestimation import TrendSmoother
    m=_import(ROOT/"benchmarks/inversion_study.py","new_inverse_study")
    model=TrendSmoother(32,order=2)
    for s in (.01,.5,.99):
        roots=[]
        for method in m.METHODS:
            item=m._invert(model,s,method)
            assert item["success"]==1, (s,method,item)
            assert item["relative_tail_error"]<1e-9
            assert item["elapsed_us"]>0
            roots.append(item["lambda_"])
        assert np.allclose(roots,roots[0],rtol=1e-8,atol=0)


def test_analytical_case_not_ranking_root_methods():
    from trendestimation import TrendSmoother
    m=_import(ROOT/"benchmarks/inversion_study.py","analytic_inverse_study")
    model=TrendSmoother(30,order=0)
    values=[m._invert(model,.5,method) for method in m.METHODS]
    assert all(x["success"] for x in values)
    assert all(x["iterations"]==0 for x in values)


def test_paper_contains_required_qualifications():
    p=ROOT/"paper/computational-statistics-submission"
    paper=(p/"main.tex").read_text(encoding="utf-8")
    section=(p/"computational_synthesis.tex").read_text(encoding="utf-8")
    assert r"\input{computational_synthesis.tex}" in paper
    for needle in (
        "80,640","pointwise","Holm","bisection",
        "not", "exact", "failed",
    ):
        assert needle in section
    rscript=(p/"run_final_vm_study.py").read_text(encoding="utf-8")
    assert "--seeds" in rscript and "--root-repeats" in rscript
    assert "benchmarks/formal_solver_study.py" in rscript
    assert "benchmarks/analyze_formal_solver_study.py" in rscript
    assert "benchmarks/inversion_study.py" in rscript


def test_tracked_output_directory_not_under_ignored_build_tree():
    import subprocess
    path="paper/computational-statistics-submission/research/final_vm/inversion/summary.csv"
    process=subprocess.run(
        ["git","check-ignore",path],
        cwd=ROOT,capture_output=True,text=True,check=False,
    )
    assert process.returncode==1, process.stdout
