# One reproducible AwesomeFigures example

This directory contains **one simple two-panel visualization** for the
CSDA paper. It is not a benchmarking experiment or a comparison of
statistical methods.

## Reproduce

At repository root, install the package and the **already pinned**
AwesomeFigures revision:

```sh
python -m pip install -e . matplotlib
python -m pip install "$(grep '^awesomefigures @ ' paper/requirements.txt)"
python paper/csda-unified-theory/figures/render_gaussian_jerk.py
```

The GitHub Actions workflow
`.github/workflows/csda-unified-theory.yml` does this before
compiling the Elsevier CAS PDF, then archives and commits the rendered
vector PDF, PNG and SVG, numerical CSVs, and JSON manifest.

## Exact illustration protocol

- **Seed:** 20261122; `n=72`, equally spaced times in `[0,1]` seconds.
- **True position (m):** `1+t+0.5t**2+0.30t**3+0.12sin(3*pi*t)`.
- **Observed position:** true position plus independent `N(0,0.08**2)` noise.
- **Penalty:** third forward differences `d=3`. The cubic baseline has
  reference physical jerk `6*0.30=1.8 m/s**3`; fix
  `mu=1.8*(1/71)**3` in the actual discrete third differences.
  The sinusoidal part makes the true jerk nonconstant; this illustrative
  truth is *not* sampled from the full Gaussian random-difference model.
- **Criterion:** the library's existing **profiled Gaussian contrast**
  (`criterion="mle"`, fixed numeric `mu`), selecting from the
  **91 equally spaced normalized smoothness values in [0.02,0.98]**.
- **Upper panel:** observations, known true trend and selected PLS fit.
- **Lower panel:** evaluated contrast **minus its minimum**, so the
  chosen `S` is visible without an arbitrary large score offset.
- **Scope:** one in-sample example with known synthetic truth. This is
  neither forecast evaluation nor an empirical performance claim.

The renderer calls the real AwesomeFigures APIs `set_style`,
`color_palette`, and `save_figure`, pinned centrally in
`paper/requirements.txt`. It fails rather than silently falling back
if AwesomeFigures or the selection routine cannot operate.

## Outputs

- `gaussian_jerk_demo.{pdf,png,svg}`: same two-panel plot, one vector
  journal figure and two convenient previews.
- `gaussian_jerk_series.csv`: time, truth, observations, fit.
- `gaussian_jerk_profile.csv`: smoothness, mapped penalty, criterion.
- `gaussian_jerk_demo.json`: seed, parameters, chosen smoothness,
  penalty, RMSE and SHA-256 for every numerical/figure output.

The source and data are preserved in the repository and Actions artifacts.
No external dataset, network download or expensive experiment is needed.
