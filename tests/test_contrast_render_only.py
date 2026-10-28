"""Re-render from archived computed values without tuning or timing new models."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import pytest

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"paper/computational-statistics-submission"
sys.path.insert(0,str(HERE))


def load(name:str):
    path=HERE/(name+".py")
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_awesomefigures_contrast_palette_is_pinned():
    from contrast_theme import METHODS, SERIES, apply
    import awesomefigures as af
    assert len(SERIES)==8
    assert set(METHODS)=={"cv","gcv","aicc","bic","mle","controlled"}
    assert len(set(METHODS.values()))==6
    assert set(METHODS.values()).issubset(
        set(af.color_palette("okabe-ito",as_hex=True))
    )
    apply()


def test_dashboard_render_only_does_not_optimize_or_change_json(monkeypatch):
    mod=load("make_selection_dashboards")
    files=[
        HERE/"data/co2_recent_dashboards.json",
        HERE/"data/dashboard_selection_summary.csv",
    ]
    checksums=[sha(p) for p in files]
    def cannot_run(*args,**kwargs):
        raise AssertionError("A benchmark/criterion optimization was rerun")
    monkeypatch.setattr(mod,"analyze",cannot_run)
    monkeypatch.setattr(mod,"select_lambda",cannot_run)
    monkeypatch.setattr(mod,"fitted_selection",cannot_run)
    reported=mod.generate(datasets=("co2_recent",),render_only=True)
    assert len(reported)==1
    assert reported[0]["dataset"]=="co2_recent"
    for fname in (
        "co2_recent_dashboard_holdout_mu_zero.pdf",
        "co2_recent_dashboard_future_mu_data.svg",
        "co2_recent_selection_summary_mu_zero.png",
        "co2_recent_mu_sensitivity.pdf",
    ):
        assert (HERE/"figures"/fname).is_file(),fname
    assert [sha(p) for p in files]==checksums


def test_archived_record_is_rejected_when_s_changed():
    mod=load("make_selection_dashboards")
    from copy import deepcopy
    dates,y=mod.load_series(mod.DATA/"noaa_mlo_monthly_1990_2026_09.csv",
                            "average_ppm")
    dates,y=dates[-120:],y[-120:]
    cached=json.loads((HERE/"data/co2_recent_dashboards.json").read_text())
    corrupted=deepcopy(cached)
    corrupted["records"]["zero"]["d2_cv"]["s"]=.99999
    with pytest.raises(ArithmeticError,match="smoothness"):
        mod._from_archived_selection(dates,y,"zero",corrupted)


def test_orchestrator_dry_run_never_runs_commands(monkeypatch):
    render=load("render_all_figures")
    def cannot_run(*args,**kwargs):
        raise AssertionError("Subprocess called on dry-run")
    monkeypatch.setattr(render.subprocess,"run",cannot_run)
    summary=render.run(scope="all",dry_run=True,build_pdf=True)
    assert summary["dry_run"]
    args="\n".join(" ".join(v) for v in summary["planned"])
    assert "--render-only" in args
    assert "render_awesomefigures.py" in args
    assert "render_final_computation.py" in args
    assert "latexmk" in args
    assert "formal_solver_study.py" not in args
    assert "inversion_study.py" not in args


def test_current_examples_support_render_only_without_refitting_selectors(monkeypatch):
    import make_current_examples as mod
    def cannot_optimize(*args,**kwargs):
        raise AssertionError("Archived selection must not be retuned")
    monkeypatch.setattr(mod,"estimate_candidates",cannot_optimize)
    dates,series=mod.load_series(mod.DATA/"noaa_mlo_monthly_1990_2026_09.csv",
                                 "average_ppm")
    path=mod.DATA/"co2_recent_results.json"
    before=sha(path)
    result=mod.evaluate("NOAA Mauna Loa CO2 (ppm)",dates,series,
                        recent_months=120,render_only=True)
    assert result["n"]==120
    assert sha(path)==before
