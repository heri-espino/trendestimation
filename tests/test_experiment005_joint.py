"""Lightweight mathematical and protocol regression checks for Experiment005."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"paper"/"benchmarks"/"experiment005"/"run_joint.py"


def module():
    spec=importlib.util.spec_from_file_location("experiment005_joint",SOURCE)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod


def test_positive_difference_orders_and_nonzero_mean_cases():
    m=module()
    for preset in ("smoke","pilot","full"):
        ns,ds,shapes,noises,seeds=m.design(preset)
        assert ns and shapes and noises and seeds
        assert all(1<=d<min(ns) for d in ds)
    assert 6 in m.design("pilot")[1]
    assert m.MU_POLICIES==("fixed_zero","observed_difference")


def test_exact_s_infinity_polynomial_constraint():
    m=module()
    n,d=30,3
    t=np.linspace(0,1,n)
    y=1.+.4*t-.8*t*t+.6*t**3+.2*np.sin(3*np.pi*t)
    mu=.015
    x=m.reference_limit(n,d,y,mu,1.)
    assert np.allclose(np.diff(x,n=d),mu,atol=1e-11,rtol=0)
    assert np.array_equal(m.reference_limit(n,d,y,mu,0.),y)


def test_solver_and_selection_grid_protocol():
    m=module()
    assert m.METHODS==("svd","eigh","banded_cholesky")
    assert m.FIT_METHOD["banded_cholesky"]=="cholesky"
    assert set(m.CRITERIA)=={"cv","gcv","aicc","bic","mle"}
    grid=m.complete_s_grid()
    assert len(grid)==17 and grid[0]==0 and grid[-1]==1
    assert (grid>0).sum()==16
    assert np.all(np.diff(grid)>0)


def test_measured_median_preserves_first_output():
    m=module()
    state={"count":0}
    def f():
        state["count"]+=1
        return state["count"]
    result,ms,measurements=m.median_measure(f,3)
    assert result==1
    assert state["count"]==3
    assert ms>=0 and len(measurements)==3
