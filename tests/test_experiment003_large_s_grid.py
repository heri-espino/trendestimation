"""Experiment003: exact matched candidate parity and archival smoke regression."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"paper"/"benchmarks"))

from experiment003_large_s_grid import (  # noqa: E402
    PRESETS, _penalty_lower_bands, data_vectors, map_s_grid,
    positive_banded_eigenvalues, single_measure, run,
)
from trendestimation import TrendSmoother  # noqa: E402


@pytest.mark.parametrize("n,d",[(24,1),(30,2),(45,3)])
def test_banded_eigenvalues_map_to_the_same_s_as_full_svd(n,d):
    bands=_penalty_lower_bands(n,d)
    positives=positive_banded_eigenvalues(bands,n,d)
    model=TrendSmoother(n,order=d)
    sgrid=np.array([.15,.3,.55,.8])
    lam_banded=map_s_grid(sgrid,positives)
    lam_svd=map_s_grid(sgrid,model.eigenvalues[:n-d])
    np.testing.assert_allclose(lam_banded,lam_svd,rtol=1e-6,atol=1e-8)
    np.testing.assert_allclose(
        [model.smoothness(float(x)) for x in lam_banded],
        sgrid,rtol=0,atol=5e-9,
    )


@pytest.mark.parametrize("mu",[0.0,0.15])
def test_validated_matched_grid_workflows(mu):
    phases,workflows,qa=single_measure(35,2,5,3,mu,20261028,0)
    assert len(phases)==16
    assert len(workflows)==8
    assert all(math.isfinite(x["seconds"]) and x["seconds"]>=0 for x in phases)
    assert all(math.isfinite(x) and x>=0 for x in workflows.values())
    assert qa["max_abs_trend_error"]<1e-5
    assert qa["max_relative_lambda_map_error"]<2e-5
    assert qa["spectral_basis_bytes"]>qa["banded_eigen_spectrum_bytes"]
    assert qa["banded_factor_grid_bytes"]>0


def test_independent_series_seed_reproducibility():
    y=data_vectors(30,2,3,20261028)
    assert y.shape==(3,30)
    np.testing.assert_array_equal(y,data_vectors(30,2,3,20261028))
    assert not np.array_equal(y[0],y[1])


def test_smoke_archive_complete_without_pushing(tmp_path):
    # This is an explicit CI smoke run, not a scientific hardware timing result.
    result=run("smoke",seed=20261028,blas_threads=1,
               run_dir=tmp_path/"smoke",publish_results=False,analyze=False)
    expected={
        "raw_phases.csv","raw_workflows.csv","numerical_validation.csv",
        "seed_level_workflows.csv","seed_level_phases.csv",
        "phase_summary.csv","workflow_summary.csv",
        "environment.json","manifest.json",
    }
    assert expected.issubset({p.name for p in result.iterdir()})
    manifest=json.loads((result/"manifest.json").read_text())
    assert manifest["complete"]
    assert set(manifest["files"])==expected-{"manifest.json"}
    with (result/"raw_workflows.csv").open(newline="") as f:
        records=list(csv.DictReader(f))
    assert len(records)==8
    assert set(row["workflow"] for row in records)=={
        "chol_lambda_cold","chol_lambda_cached",
        "chol_S_band_eigs_cached","spectral_lambda_trends",
        "spectral_S_trends","spectral_lambda_GCV",
        "spectral_S_GCV_native","spectral_S_GCV_cached",
    }
    with pytest.raises(FileExistsError):
        run("smoke",run_dir=result,publish_results=False,analyze=False)


def test_presets_hold_M_and_R_constant_for_n_scaling():
    full=PRESETS["full"][0]
    selected=[(n,d,m,r) for n,d,m,r in full
              if d==2 and m==21 and r==4]
    assert {n for n,d,m,r in selected}=={256,512,1024}
    large=PRESETS["large"][0]
    assert {n for n,d,m,r in large if d==2 and m==21 and r==4}=={
        1024,1536,2048,
    }
