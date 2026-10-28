"""Use the real pinned AwesomeFigures public API in paper renderers."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

PAPER = Path(__file__).resolve().parents[1] / "paper" / "computational-statistics-submission"
sys.path.insert(0, str(PAPER))


def _import(name: str):
    spec = importlib.util.spec_from_file_location(name, PAPER / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_theme_uses_real_awesomefigures_apis(monkeypatch, tmp_path):
    af = pytest.importorskip("awesomefigures")
    theme = _import("contrast_theme")
    styles = []
    saved = []
    maps = []
    real_style = af.set_style
    real_save = af.save_figure
    real_cmap = af.named_colormap

    def style(*args, **kwargs):
        styles.append((args, kwargs))
        return real_style(*args, **kwargs)

    def save(*args, **kwargs):
        saved.append(args[1])
        return real_save(*args, **kwargs)

    def cmap(name):
        maps.append(name)
        return real_cmap(name)

    monkeypatch.setattr(af, "set_style", style)
    monkeypatch.setattr(af, "save_figure", save)
    monkeypatch.setattr(af, "named_colormap", cmap)
    theme.apply(strict=True)
    assert styles and styles[0][0][0] == "elegante"
    assert styles[0][1]["palette"] == "okabe-ito"
    assert len(theme.SCHEME) == 8
    from matplotlib.colors import to_hex
    assert to_hex(theme.SCHEME[0]["color"]).upper() == af.color_palette("okabe-ito", as_hex=True)[0]
    assert theme.named_colormap("cividis") is not None
    assert maps == ["cividis"]

    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])
    filename = tmp_path / "demo.svg"
    theme.save_figure(fig, filename, strict=True)
    plt.close(fig)
    assert filename.exists() and filename.stat().st_size > 1000
    assert saved == [filename]


def test_render_only_plan_covers_all_archived_figures():
    pytest.importorskip("awesomefigures")
    command = _import("rerender_awesomefigures")
    plan = command.run(scope="journal", dry_run=True)
    joined = "\n".join(" ".join(args) for args in plan["commands"])
    assert "render_all_figures.py" in joined
    assert "sncs_expand_results.py" in joined
    assert "render_final_computation.py" not in joined  # included by render_all_figures
    assert joined.count("sncs_dashboard.py") == 6
    assert "run_final_vm_study.py" not in joined
    assert "inversion_study.py" not in joined
    assert "formal_solver_study.py" not in joined
    assert len(plan["source_sha256"]) >= 17
    assert plan["awesomefigures"]["source_commit"] == (
        "54c8bf2374551fa39428f47f69580b4822d4b938"
    )


def test_archived_input_must_remain_immutable():
    command = _import("rerender_awesomefigures")
    before = {str(f): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in command.SOURCE_ARCHIVE}
    after = {str(f): hashlib.sha256(f.read_bytes()).hexdigest()
             for f in command.SOURCE_ARCHIVE}
    assert before == after
    required = command.mentioned_figures()
    for name in ("sncs_observed_trends.pdf", "sncs_orders_trends.pdf",
                 "sncs_compact_dashboard.pdf", "final_solver_inference.pdf"):
        assert name in required


def test_full_scope_includes_existing_springer_publication_figures():
    command = _import("rerender_awesomefigures")
    full = "\n".join(" ".join(c) for c in command.commands("all"))
    assert "--scope all" in full
    assert "render_mle_benchmarks.py" in full


def test_core_plotters_delegate_export_to_awesomefigures():
    files = [
        "sncs_dashboard.py", "sncs_expand_results.py",
        "make_selection_dashboards.py", "make_current_examples.py",
        "render_final_computation.py",
    ]
    for name in files:
        source = (PAPER / name).read_text(encoding="utf-8")
        assert "save_figure(" in source
        assert "fig.savefig(" not in source, name
