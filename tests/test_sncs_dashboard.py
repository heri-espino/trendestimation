"""SN Computer Science short-paper cached dashboard regressions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest

HERE=Path(__file__).resolve().parents[1]/"paper/computational-statistics-submission"
sys.path.insert(0,str(HERE))


def _load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+".py"))
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_short_paper_preserves_archival_article():
    short=(HERE/"sncs_main.tex").read_text(encoding="utf-8")
    old=(HERE/"main.tex").read_text(encoding="utf-8")
    assert r"\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}" in short
    assert r"\bibliography{bibliografia}" in short
    assert "80,640" in short and "Holm" in short
    for ref in ("berns2022automated","gauss2021skeleton","cardoso2025novelty"):
        assert ref in short
        assert "@article{"+ref in (HERE/"bibliografia.bib").read_text()
    assert r"\input{dashboard_applications.tex}" in old
    assert r"\input{dashboard_applications.tex}" not in short
    assert "sncs_compact_dashboard.pdf" in short


def test_archived_results_are_complete_and_consistent():
    dash=_load("sncs_dashboard")
    for key in ("co2_full","co2_recent","fedfunds_full"):
        archived,h=dash.read_results(key)
        for mode in ("zero","data"):
            for field in ("s","lambda","rmse","mae"):
                matrix=dash.as_matrix(archived,mode,field)
                assert matrix.shape==(4,6)
                assert np.isfinite(matrix).all()
        assert digest(dash.DATA/(key+"_dashboards.json"))==h


def test_compact_figure_requires_no_fitting_or_experiments(monkeypatch):
    dash=_load("sncs_dashboard")
    def forbidden(*args,**kwargs):
        raise AssertionError("No fit or optimizer is allowed in summary rendering")
    import trendestimation
    monkeypatch.setattr(trendestimation,"select_lambda",forbidden)
    paths=[dash.DATA/(key+"_dashboards.json")
           for key in ("co2_full","fedfunds_full")]
    before=[digest(p) for p in paths]
    files=dash.plot_compact()
    assert len(files)==3
    assert all(p.exists() and p.stat().st_size>1000 for p in files)
    assert [digest(p) for p in paths]==before


def test_detailed_view_uses_saved_parameters_not_criteria(monkeypatch):
    app=_load("sncs_dashboard_app")
    import trendestimation
    def forbidden(*args,**kwargs):
        raise AssertionError("Selection criteria must never be reoptimized")
    monkeypatch.setattr(trendestimation,"select_lambda",forbidden)
    for kind in ("holdout","future"):
        dates,y,fit,pred,row=app.fit_saved_case(
            "co2_recent","data",2,"mle",kind
        )
        assert len(pred)==12 and np.isfinite(pred).all()
        assert np.isfinite(fit).all()
        assert row["method"]=="mle"
        assert float(row["lambda"])>0
