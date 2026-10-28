"""Expanded SNCS paper — all figures and tables come from saved evidence."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest

HERE=Path(__file__).resolve().parents[1]/"paper"/"computational-statistics-submission"
sys.path.insert(0,str(HERE))


def _load(name:str):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+".py"))
    assert spec and spec.loader
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj


def _hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_expanded_paper_has_mathematical_and_software_claims():
    main=(HERE/"sncs_main.tex").read_text(encoding="utf-8")
    assert r"\input{sncs_expanded_theory.tex}" in main
    assert r"\input{sncs_expanded_software.tex}" in main
    assert r"\input{sncs_expanded_experiments.tex}" in main
    assert r"\input{sncs_expanded_applications.tex}" in main
    theory=(HERE/"sncs_expanded_theory.tex").read_text(encoding="utf-8")
    for word in ("S_G","n-d","\\mu","\\Lambda_d","\\operatorname{CV}"):
        assert word in theory
    src=(HERE/"sncs_expanded_software.tex").read_text(encoding="utf-8")
    for value in ("search\\_space","TrendSmoother","select_lambda","\\texttt{fit}"):
        assert value in src


def test_only_cached_measurements_reformatting(monkeypatch):
    mod=_load("sncs_expand_results")
    def forbidden(*args,**kwargs):
        raise AssertionError("A statistical selector or benchmark was executed")
    import trendestimation
    import make_current_examples
    monkeypatch.setattr(trendestimation,"select_lambda",forbidden)
    monkeypatch.setattr(make_current_examples,"select_lambda",forbidden)
    sources={p:_hash(p) for p in mod.SOURCE_PATHS}
    result=mod.render()
    assert result["unchanged"] and len(result["tables"])==3
    assert len(result["figures"])==12
    assert sources=={p:_hash(p) for p in mod.SOURCE_PATHS}
    for relative in result["tables"]+result["figures"]:
        assert (mod.ROOT/relative).stat().st_size>100, relative


def test_tables_are_real_and_matched_grid_is_not_misinterpreted():
    mod=_load("sncs_expand_results")
    csv=mod._rows(mod.BENCH/"windows_full_s_analysis"/"selected_s.csv")
    assert len(csv)==10
    for row in csv:
        assert np.isclose(float(row["native_s_S"]),
                          float(row["mapped_s_lambda_S"]),atol=2e-9)
    for mode in ("zero","data"):
        for ds in ("co2_full","fedfunds_full"):
            cache,_=mod.read_results(ds)
            assert len(cache["records"][mode])==24


def test_old_manuscript_remains_untouched_and_citable():
    assert (HERE/"main.tex").is_file()
    assert (HERE/"main.pdf").is_file()
    assert (HERE/"research/final_vm/inversion/raw_inversions.csv").is_file()
    assert (HERE/"research/final_vm/solver/analysis/paired_comparisons.csv").is_file()
