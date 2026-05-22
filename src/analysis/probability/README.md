# Probability

The Probability tool explores whether simple Elo-style rating systems can
produce useful pre-bout win probabilities for professional sumo.

The central question is:

> Are the generated probabilities empirically well calibrated?

This package is research/analysis code rather than a user-facing web product.
It generates probabilistic forecasts from historical bouts, evaluates those
forecasts, and writes CSV/console outputs for inspection.

## Current Focus: Expt3

The maintained path is **Expt3**, implemented primarily in `expt3c.py`.

Expt3 uses the Expt1 simulation engine to process bouts sequentially:

1. Maintain scalar Elo-like ratings for rikishi.
2. Before each scored bout, convert the rating difference into a win
   probability using the Elo logistic link.
3. Record the pre-bout probability and realised outcome.
4. Update ratings after the bout.
5. Evaluate the resulting probability/outcome rows.

The default and preferred Expt3 entrant policy is constant initialisation: new
rikishi enter with the same baseline rating.

## What Is Being Evaluated

The focus is probability quality, not ranking quality.

The main evaluation outputs are:

- calibration rows grouped by probability bin
- calibration MAE and RMSE
- raw Brier score
- baseline Brier score
- Brier skill score
- Brier decomposition terms: reliability, resolution, and uncertainty
- optional raw bout-level forecasts
- optional delta-binned calibration rows

The usual interpretation is:

- **calibration** asks whether predicted probabilities match observed
  frequencies
- **Brier score** measures overall probabilistic accuracy
- **Brier skill** measures improvement over a constant base-rate predictor

## Current Findings

The current documented Expt3 result is that a simple rating-based approach
produces meaningful calibrated probabilities over the well-supported central
probability region.

See `docs/5 Results & Findings.md` for the current recorded result set and its
limits.

## Main Files

- `expt3c.py` is the maintained Expt3 entry point.
- `expt3_types.py` contains Expt3 result/data types.
- `expt3_report.py` builds and renders the bottom-line summary.
- `classes.py` contains shared calibration-bin and calibration-row logic.
- `expt3_q_sweep.py` sweeps the logistic scale parameter `q`.
- `expt3_link_sweep.py` explores probability-link variations.
- `expt3c_alpha_sweep.py` sweeps shrinkage for the experimental Expt2-derived
  entrant initialisation path.
- `builder.py` and `__main__.py` belong to the older Expt2-ratings calibration
  path.

## Historical Layer: Expt2-Ratings Calibration

This folder also contains an older path that evaluates probabilities generated
from fixed Expt2 rank/chii ratings.

That path is represented mainly by:

- `builder.py`
- `__main__.py`

It loads Expt2 final rating CSVs, converts rank/chii rating differences into
probabilities, and builds calibration rows from observed bouts.

This is useful historical and comparative code, but it is not the current
maintained Expt3 experiment. When in doubt, start with `expt3c.py`.

## Running Expt3

Run the maintained experiment with:

```powershell
python -m src.analysis.probability.expt3c
```

Useful arguments include:

- `--start` and `--end` to choose the year range
- `--zip` to use zipped input data where supported by the data layer
- `--open` to run in open mode; default is closed mode
- `--k-policy` with `constant` or `divisional`
- `--k-value` for constant K
- `--k-config` for divisional K
- `--b` for entrant baseline rating
- `--q` for the logistic scale parameter
- `--bin-width` for probability calibration bins
- `--output` for probability-binned calibration CSV
- `--bout-output` for raw bout-level forecasts
- `--delta-bin-width` and `--delta-output` for delta-binned calibration

Example:

```powershell
python -m src.analysis.probability.expt3c --start 1958 --end 2026 --q 850 --k-policy divisional
```

## Entrant Policies

Expt3 supports several entrant policies at the experiment boundary:

- `constant`: default and preferred Expt3 policy
- `expt2_example`: example non-constant initialisation from Expt2 ratings
- `expt2_scaled`: Expt2-derived initialisation shrunk by `--expt2-alpha`

The non-constant policies are exploratory. They preserve and test the simulator
boundary for entrant initialisation, but they are not the core Expt3 method.

## Outputs

Default outputs are written under:

```text
files/output/Equelo/
```

Common outputs include:

- `expt3_calibration.csv`
- `expt3_delta_calibration.csv`
- sweep CSVs such as `expt3_q_sweep.csv` and `expt3_alpha_sweep.csv`

Console output reports summary metrics such as Brier score, calibration MAE,
RMSE, base rate, observation counts, and bottom-line support/calibration regions.

## Documentation Map

- `docs/0 Requirements.md` defines the objective and constraints.
- `docs/1 Model & Generation.md` explains how ratings and probabilities are
  generated.
- `docs/2 Evaluation & Calibration.md` defines calibration and Brier evaluation.
- `docs/3 Reporting.md` describes output forms.
- `docs/4 Data & Behaviour.md` records data-handling and behavioural notes.
- `docs/5 Results & Findings.md` records the current results.
- `docs/6 Sensitivity & Variations.md` discusses parameter sensitivity.
- `docs/7 Using Fixed Point Initialisation.md` discusses Expt2-style
  initialisation as a variation.
- dated docs such as `2026 04 17 The Grand Plan(s).md` are exploratory planning
  notes, not the primary operating spec.

## Interpretation Notes

Expt3 is intentionally minimal:

- ratings are scalar values
- predictions depend only on rating differences
- no extra covariates are used
- bouts are processed sequentially
- ignored/fusen/blank bouts are not part of the scored forecast set

The point is not to claim that this is a complete model of sumo performance.
The point is to test whether a simple rating process is enough to produce
probabilities that behave well under calibration and Brier evaluation.
