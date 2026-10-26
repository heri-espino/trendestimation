"""Reproduce updated NOAA monthly CO2 experiment without live downloads."""
from __future__ import annotations

import csv
import importlib.util
import math
from datetime import date
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
CODE = PAPER / "figures" / "make_updated_mauna_loa.py"
SNAPSHOT = PAPER / "figures" / "noaa_mlo_monthly_1990_2026_09.csv"


def module():
    spec = importlib.util.spec_from_file_location("mauna_loa_2026_update", CODE)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_pinned_noaa_monthly_series_is_complete_and_has_known_latest_value():
    mod = module()
    dates, values = mod.load_observations()
    assert len(dates) == len(values) == 441
    assert dates[0] == date(1990, 1, 1)
    assert dates[-1] == date(2026, 9, 1)
    assert float(values[-1]) == pytest.approx(426.07)
    assert all(math.isfinite(float(x)) for x in values)
    header = SNAPSHOT.read_text(encoding="utf-8")
    assert "gml.noaa.gov/ccgg/trends/" in header
    assert "datasets/co2-ppm" in header
    assert "2026-10-09" in header
    # No invented October observation or fallback interpolation in input.
    assert "2026-10," not in header
    assert "interpolate(" not in CODE.read_text(encoding="utf-8")


def test_observed_experiment_uses_same_controls_and_recomputes_parameters():
    mod = module()
    summary = mod.generate()
    assert summary["period"] == "1990-01 to 2026-09"
    assert summary["normalized_target_smoothness"] == 0.86
    assert summary["fixed_mu"] == 0.0
    assert summary["orders"] == [2, 3, 4, 5]
    expected_penalties = {
        "2": 41.77329,
        "3": 175.71947,
        "4": 787.52870,
        "5": 3564.46427,
    }
    for d, expected in expected_penalties.items():
        actual = summary["by_order"][d]
        assert actual["lambda"] == pytest.approx(expected, rel=1e-4)
        assert actual["smoothness"] == pytest.approx(0.86, abs=2e-9)
        assert actual["edf_conditional"] == pytest.approx(
            441 - (441 - int(d)) * 0.86, abs=1e-7
        )
    generated = PAPER / "figures" / "mauna_loa_1990_2026_09.dat"
    values = np.genfromtxt(generated, names=True)
    assert values.size == 441
    assert tuple(values.dtype.names) == ("year", "observed", "d2", "d3", "d4", "d5")
    assert values["observed"][-1] == pytest.approx(426.07)
    assert (PAPER / "real_data_2026_summary.json").is_file()


def test_manuscript_and_build_use_new_figure_without_rewriting_legacy():
    text = (PAPER / "sections" / "mauna_loa.tex").read_text(encoding="utf-8")
    builder = (PAPER / "build.py").read_text(encoding="utf-8")
    renderer = (PAPER / "figures" / "render_awesomefigures.py").read_text(
        encoding="utf-8"
    )
    assert "1990--September 2026" in text
    assert "n=441" in text
    assert r"\cite{noaa2026mlo}" in text
    assert r"\includegraphics{figures/mauna_loa_1990_2026_09.pdf}" in text
    assert "make_updated_mauna_loa.py" in builder
    assert "mauna_loa_1990_2026_09.pdf" in builder
    assert 'render_co2_updated(publication)' in renderer
    assert 'render_co2(publication)' in renderer
    assert (PAPER / "figures" / "mauna_loa_1990_1999.dat").is_file()
