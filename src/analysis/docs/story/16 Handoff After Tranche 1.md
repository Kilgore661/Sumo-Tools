# Handoff After Tranche 1

## Purpose and status

This is the restart document for the Elo/Equelo work after completion of
Tranche 1. It is intended to let another person resume without reconstructing
the conversation or following every experimental branch.

Tranche 1 is complete analytically. It selected a leading post-1988 replay
model and established the boundary between entrant-prior estimation and
population normalisation. No production or website consumer has yet been
migrated to that model, and the distinctive pre-1989 Equelo extension remains
to be designed and tested.

The detailed evidential account is
[Tranche 1: Population Normalisation Policy](15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md).

## Repository shape

The repository has four useful conceptual regions:

- `src/analysis`: experiments, diagnostic producers and their research record;
- `src/products/make_site2`: the current website producer and its consumers of
  selected analysis artifacts;
- `src/sumo_core`: stable domain primitives and history structures; and
- `src/infra`: stable persistence and infrastructure code.

Tranche 1 deliberately changed only analysis code and documentation. It did
not migrate `make_site2` or replace legacy Equelo producers.

## Model vocabulary at handoff

The following names must be kept distinct:

- \(B\): Basic Elo from 1989 onward, `q=400`, constant `k=35`, constant entrant
  rating and permanent ratings within the run.
- old \(B_{kP}\): the earlier selected B-family model with divisional `k` and
  the retained contextual informed prior.
- \(P_1\): the canonical q=400, support-proportionally recentered (`alpha=1`)
  literal-chii entrant prior produced by `src.analysis.equelo_bkp1`.
- `BKP1, no population adjustment`: divisional `k` plus \(P_1\), using the
  established B-family forecaster. This forecaster performs no population
  boundary adjustment; it must not be called “legacy departure”.
- `BKP1, Expt2 departure redistribution`: the same bout model and prior, but
  with the actual old Expt2 rule that redistributes a departing rikishi's
  deviation from the active mean over survivors.
- `BKP1, whole-population preservation`: the leading Tranche 1 candidate. It
  holds \(P_1\) fixed and uses common additive shifts to preserve the initial
  active-population mean after population formation and after the basho's
  bouts.

A compact final name for the leading candidate has not been chosen. Do not use
plain `BKP1` where the population policy is material until that naming decision
has been made.

## Selected candidate contract

The leading post-1988 candidate currently means:

```text
history                 represented W/L results from 1989/01 onward
forecast scale          q = 400
update size             declared divisional-k policy
entrant initialisation  fixed canonical P1
population              full represented banzuke at each basho boundary
population operator     common shift to the initial active mean after
                        population formation and after bouts
dual-k mass             absorbed by the post-bout common shift
fixed-point feedback    none: do not re-estimate P1 under this operator
chronology              forecast before update
identity                RikId
```

The common shifts preserve every rating difference among the rikishi to whom
they are applied. Although a common shift cannot change probabilities within
the current active population at the instant it is applied, it anchors the
coordinate carried by survivors relative to the absolute \(P_1\) assigned to
future entrants.

## How Tranche 1 reached this point

### 1. Unequal divisional-k mass was isolated

The cumulative dual-`k` diagnostic consumed the exact persisted B-family
forecast ledger. For old \(B_{kP}\), 19,971 of 574,863 bouts used unequal `k`.
They created +2898.668 net rating points, but 94.61% of gross positive and
negative flow cancelled. The implied correction was only about 0.005 points
per rated bout. Sanyaku--maegashira bouts were correctly found not to be rare,
but the resulting scale effect remained small.

Conclusion: unequal `k` needs correct accounting but is not the main
population-drift problem.

### 2. The old literal-chii fixed point was diagnosed

Uniform post-iteration recentering gives every chii the same repeated shift,
regardless of support. This produces absurd values for rare lower-banzuke
cells. A support-weighted sweep tested `alpha = 0, 0.25, 0.5, 1`.

`alpha=1` materially changes pairwise prior differences, so it is not a neutral
normalisation. Nevertheless, its curve was judged the best useful candidate:
the former M12--M18 rise disappeared, the broad shape remained coherent far
into Jonidan, and `Sd100e` looked plausible. Remaining M/J and J/Ms steps,
rare-sanyaku teeth and deep-Jonokuchi anomalies were retained and documented,
not interpolated away.

Conclusion: ratings are not chii, strict monotonicity is not required, and
computed anomalies must not be silently replaced by a preferred-looking line.

### 3. q=400 was made canonical without altering Expt2

The recentering experiment was rerun at `q=400`. The shape conclusions survived
and the `alpha=1` solver converged in 18 iterations. A separate maintained
package, `src.analysis.equelo_bkp1`, was created with `q=400` and `alpha=1`
fixed in its contract. It exposes neither value as a CLI option and does not
import Expt2's hard-coded `q=900`. Original Expt2 and its artifacts were left
untouched.

The canonical producer's 975 values match the explicit experimental q=400
control exactly.

### 4. P1 passed the original B-family predictive gate

With no population adjustment, q=400 BKP1 achieved log loss 0.677319 and Brier
loss 0.242086 over the exact 574,863-bout domain. This was very close to old
\(B_{kP}\), at 0.676945 and 0.241968 respectively. The remaining difference was
concentrated below 30 prior bouts.

Conclusion: \(P_1\) is predictively useful, not merely a visually appealing
chii curve.

### 5. Population correction and fixed-point feedback were separated

Holding \(P_1\) fixed, whole-population preservation removed roughly 159
points of active-mean displacement present under the Expt2 replay. But solving
a new literal-chii fixed point under that operator took 71 iterations and
recreated the pathology: the two-observation `Jk73w` prior rose to about 3169.

Two controls located the cause:

- adding only dual-`k` correction to legacy departure changed the solved map by
  just 0.129 points MAE, maximum 0.810;
- applying turnover correction without dual-`k` correction was virtually
  identical to the pathological full whole-population fixed point.

Conclusion: feedback between turnover correction and rare chii priors causes
the failure. The population operator can be used with fixed \(P_1\), but must
not generate its own literal-chii fixed point.

### 6. The exact population-policy predictive gate selected the leader

All variants below used canonical \(P_1\), `q=400`, divisional `k`, the full
banzuke population where applicable and exactly the same 574,863 W/L forecasts:

| Model | Log loss | Brier loss | ECE |
|---|---:|---:|---:|
| BKP1, no population adjustment | 0.677319 | 0.242086 | 0.014453 |
| BKP1, Expt2 departure redistribution | 0.684196 | 0.245148 | 0.017651 |
| BKP1, whole-population preservation | **0.675629** | **0.241362** | 0.014537 |
| old \(B_{kP}\) | 0.676945 | 0.241968 | **0.013459** |

Whole-population BKP1 improved log loss over no adjustment by 0.001690,
95% interval [-0.002045, -0.001312], and over old \(B_{kP}\) by 0.001316,
interval [-0.001755, -0.000894]. Brier loss agreed. Old \(B_{kP}\) retained the
best ECE. The gain was concentrated in ratings with fewer than 30 prior bouts;
whole-population BKP1 became slightly worse in the longest career bands.

Conclusion: whole-population BKP1 is the leading retrospective candidate, and
Expt2 departure redistribution is substantially worse than either alternative.

## Reproducible code and commands

### Dual-k audit

Code: `src/analysis/elo_model_selection/dual_k_mass.py`

```powershell
python -m src.analysis.elo_model_selection.dual_k_mass `
  --ledger "files/output/analysis/elo_model_selection/retrospective_1989_01_to_2026_07/forecast_ledger.csv"
```

Default output is the `dual_k_mass` directory beside the ledger.

### Canonical P1 producer

Code: `src/analysis/equelo_bkp1/`

```powershell
python -m src.analysis.equelo_bkp1 --start 1989 --end 2026 --zip
```

Output: `files/output/analysis/equelo_bkp1/`.

### Recentering experiments and chart

Code: `src/analysis/equelo_population_policy/run_recentering.py` and
`chart_recentering.py`.

```powershell
python -m src.analysis.equelo_population_policy.run_recentering `
  --start 1989 --end 2026 --zip --q 400 `
  --epsilon 10 --max-iterations 200 `
  --output files/output/analysis/equelo_population_policy/recentering_q400

python -m src.analysis.equelo_population_policy.chart_recentering `
  --input files/output/analysis/equelo_population_policy/recentering_q400/prior_comparison.csv
```

### Population policy and fixed-point controls

Code: `src/analysis/equelo_population_policy/run_bkp1_population.py`.

```powershell
python -m src.analysis.equelo_population_policy.run_bkp1_population `
  --start 1989 --end 2026 --zip
```

Output:
`files/output/analysis/equelo_population_policy/bkp1_q400/`.

### Exact predictive gate

Code: `src/analysis/equelo_population_policy/predict_population_policy.py`.

```powershell
python -m src.analysis.equelo_population_policy.predict_population_policy `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07
```

Output:
`files/output/analysis/equelo_population_policy/prediction_bkp1_population_q400/`.
Its manifest hashes the history and both prior artifacts.

Generated outputs under `files/output` are intentionally not committed. The
commands above reproduce them from the project's existing history and
model-selection artifacts.

## Code map

- `src/analysis/equelo_bkp1`: canonical q=400, alpha=1 \(P_1\) producer.
- `src/analysis/equelo_population_policy/recenter.py`: alternative allocation
  of post-iteration correction mass.
- `src/analysis/equelo_population_policy/simulate.py`: shared replay with
  switchable population policies and controls.
- `src/analysis/equelo_population_policy/solve.py`: corresponding fixed-point
  solver.
- `src/analysis/equelo_population_policy/predict_candidate.py`: original exact
  B-family predictive gate for a supplied candidate prior.
- `src/analysis/equelo_population_policy/predict_population_policy.py`: final
  exact comparison of no adjustment, Expt2 departure redistribution and
  whole-population preservation.
- `src/analysis/elo_model_selection/dual_k_mass.py`: cumulative unequal-`k`
  diagnostic over the persisted canonical forecast ledger.
- `tests/test_equelo_*` and
  `tests/test_elo_model_selection_dual_k_mass.py`: focused regression coverage.

## Decisions not to reopen without new evidence

- Do not change original Expt2 or remove its `q=900`; it remains a reproducible
  historical experiment.
- Do not add a general `q` or `alpha` option to the canonical \(P_1\) producer.
- Do not interpolate the remaining chii-curve anomalies merely to make the
  curve monotone.
- Do not solve \(P_1\) through the whole-population operator: that recreates
  extreme rare-rank priors.
- Do not describe the established B-family forecaster as using legacy
  departure redistribution. It uses no population adjustment.
- Do not interpret cumulative unequal-`k` mass as endpoint active-population
  inflation; leavers break that equivalence.

## Qualifications

- All predictive comparisons are retrospective.
- Both informed priors were derived using future information from the broad
  period being scored.
- The fixed-point stopping tolerance is ten rating points; convergence does
  not make a low-support prior trustworthy.
- Deep Jonokuchi and rare sanyaku literal-chii cells remain low-support and
  should not be presented as definitive measurements of skill.
- Whole-population BKP1 has the best aggregate log and Brier loss tested, but
  old \(B_{kP}\) has slightly better ECE and the longest-career bands slightly
  favour the alternatives.

## Recommended continuation

The next research tranche is the distinctive Equelo question: extend the
selected post-1988 model over the incomplete 1958--1988 record and test whether
carrying that information across January 1989 improves subsequent forecasts.

Before coding that extension, write one bounded specification that fixes:

1. the historical completion rule for ranks present before 1989 but absent
   from \(P_1\), notably M19--M22 and J15--J24;
2. initial treatment of rikishi first observed as sekitori before 1989;
3. treatment of the newly observable lower-banzuke population in January 1989;
4. how the whole-population anchor behaves across that observability break;
5. the post-1988 forecast windows and comparators; and
6. whether the leading candidate receives a concise final name before the
   experiment.

At minimum, compare a fresh 1989 start with a full-history construction while
holding `q`, divisional `k`, \(P_1\), post-1988 bout eligibility and population
policy fixed. Score identical post-1988 bouts, with particular attention to the
years immediately after 1989. Only after that gate should production artifacts,
the website or public Equelo prose be migrated.

## Verification at handoff

The focused suite covering all newly added Tranche 1 code passes:

```text
19 passed
```

The repository was also checked with `python -m py_compile` for the new CLI
modules and `git diff --check` before commit.
