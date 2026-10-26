"""Paired MLE/S/lambda experiments and paper figure source invariants."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"paper/benchmarks"))

from selection_coordinate_mle import CRITERIA, POLICIES, s_grid, study  # noqa: E402


def test_s_grid_includes_all_deciles_near_one_and_exact_limits():
    s=s_grid()
    assert len(s)==16
    assert s[0]==0.0 and s[-1]==1.0
    assert np.all(np.diff(s)>0)
    for value in (0.95,0.99,0.999,0.9999,0.999999):
        assert value in s


def test_gaussian_mle_is_fifth_criterion_not_seventh_solver():
    assert CRITERIA==("cv","gcv","aicc","bic","mle")
    assert POLICIES==("matched_lambda","native_s","log_lambda")


def test_smoke_mle_same_scores_in_both_coordinates(tmp_path):
    records=study("smoke",repeats=1,threads=1,
                  seed=20261026,output_dir=tmp_path)
    assert len(records)==2*5*3
    for mu in (0.0,0.15):
        for name in CRITERIA:
            x=next(r for r in records if r["mu"]==mu
                   and r["criterion"]==name
                   and r["policy"]=="matched_lambda")
            y=next(r for r in records if r["mu"]==mu
                   and r["criterion"]==name
                   and r["policy"]=="native_s")
            assert np.isclose(x["lambda_selected"],y["lambda_selected"],
                              rtol=1e-9,atol=1e-8) or (
                                  np.isposinf(x["lambda_selected"]) and
                                  np.isposinf(y["lambda_selected"]))
            assert np.isclose(x["score_selected"],y["score_selected"],
                              rtol=1e-8,atol=1e-8)
    with (tmp_path/"criterion_score_paths.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==2*5*16
    assert all(any(r["criterion"]==c for r in rows) for c in CRITERIA)
    for r in rows:
        if r["criterion"]=="mle" and float(r["lambda"])==0.0:
            assert r["finite"]=="False"
    assert (tmp_path/"environment.json").exists()
    assert (tmp_path/"setup_times.csv").exists()


def test_manuscript_website_notes_and_renderer_register_actual_images():
    paper=(ROOT/"paper/main.tex").read_text(encoding="utf-8")
    figures=(ROOT/"paper/sections/selection_visuals.tex").read_text(
        encoding="utf-8")
    docs=(ROOT/"docs/mle_coordinate_figures.rst").read_text(encoding="utf-8")
    renderer=(ROOT/"paper/figures/render_mle_benchmarks.py").read_text(
        encoding="utf-8")
    assert r"\input{sections/selection_visuals}" in paper
    for name in ("gcv_solver_by_order","gcv_repeated_search",
                 "criteria_with_mle_s_paths","criteria_with_mle_lambda_paths",
                 "criteria_with_mle_search_time"):
        assert f"figures/{name}.pdf" in figures
        assert f"figures/{name}.svg" in docs
    assert "awesomefigures" in (
        ROOT/"paper/figures/render_awesomefigures.py").read_text()
    assert "grid_reuse_reference" in renderer
    assert "selection_coordinate_reference" in renderer
    assert (ROOT/"notes/experiment001_solver_selection_figures.md").exists()
