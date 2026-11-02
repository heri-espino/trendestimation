"""Check the mathematical and data-provenance contract of Experiment009."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]/"paper"/"benchmarks"/"experiment009"
spec = importlib.util.spec_from_file_location("experiment009_crossover", ROOT/"crossover.py")
assert spec and spec.loader
cross = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cross)


def test_asymptotic_cost_basis_positive_and_criterion_specific():
    for mode in ("fit", "aicc"):
        for method in ("svd", "cholesky"):
            v = cross.basis(mode, method, 128, 3, 7, 3)
            assert np.all(np.isfinite(v))
            assert np.all(v > 0)
            assert v.ndim == 1
    assert len(cross.basis("fit", "svd", 128, 3, 7, 3)) == 4
    assert len(cross.basis("aicc", "cholesky", 128, 3, 100, 2)) == 5


def test_theoretical_surface_has_all_six_orders_and_six_candidate_counts():
    const = {"svd": np.ones(4), "cholesky": np.ones(4)}
    surf = cross.theoretical_surface(const, "fit")
    assert len(surf) == 7*6*6*2
    assert {x["n"] for x in surf} == set(cross.N_GRID)
    assert {x["d"] for x in surf} == set(range(1,7))
    assert {x["M"] for x in surf} == {1,7,100,1000,10000,100000}
    assert any(x["n"]==131072 and not x["svd_memory_runtime_gate"] for x in surf)


def test_frozen_sources_and_separate_full_criterion_calibration():
    fit=cross.collect_fit()
    aicc=cross.collect_aicc()
    assert len(fit)==3*6*2*2*4
    assert len(aicc)==4*6*4
    assert {r["criterion"] for r in fit} == {"full_trend"}
    assert {r["criterion"] for r in aicc} == {"aicc"}
    assert {r["n"] for r in fit} == {64,128,256}
    assert {r["n"] for r in aicc} == {64,128,256,512}
    assert all(r["mu"] == "data" for r in aicc)
    assert all("svd" in r and "cholesky" in r for r in fit+aicc)


def test_coefficient_fit_preserves_holdout_and_admissibility():
    fit=cross.collect_fit()
    models,train,holdout=cross.fit_models(fit,"fit")
    assert train == (64,128) and holdout == 256
    assert all(np.all(v>=0) for v in models.values())
    comps,quality=cross.compare(fit,models,"fit",holdout)
    assert quality["paired_comparable"]>0
    assert 0<=quality["accuracy"]<=1
    assert all(r["empirical_winner"]=="not_comparable"
               for r in comps if not r["svd_eligible"] or
               not r["cholesky_eligible"])


def test_complete_aicc_model_has_separate_holdout():
    rows=cross.collect_aicc()
    models,train,holdout=cross.fit_models(rows,"aicc")
    assert train == (64,128,256) and holdout==512
    assert all(np.all(v>=0) for v in models.values())
    out,quality=cross.compare(rows,models,"aicc",holdout)
    assert len(out)==len(rows)
    assert all(x["set"]=="holdout" for x in out if x["n"]==512)
