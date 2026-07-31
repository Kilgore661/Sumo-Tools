# Clean Elo: Code Description

## Purpose

`clean_elo` replays the available sumo history as an Elo simulation. It is
deliberately narrower than the older Equelo experiments:

- ratings persist once a rikishi has been initialized;
- no attempt is made to interpret the absolute meaning of a rating;
- the mean rating of the current basho population is held fixed;
- initialization and k are supplied by policies;
- kyujo can either be ignored or counted explicitly.

The input is a `History` and a start `Date`. The main output is one CSV for
each processed basho, containing the ratings at the basho boundaries and the
appearance accounting used by the simulation.

## Package layout

### `config.py`

Defines the defaults:

- initial rating: Equelo's shared `INITIAL_ELO`, currently `1517`;
- Elo scale q: Equelo's shared `INITIAL_Q`, currently `900`;
- k configuration: `files/input/elo_fide.json`;
- output root: `files/output/analysis/clean_elo`.

### `policies.py`

Defines the two policy interfaces consumed by the simulator.

`InitialRatingPolicy.rating_for(chii)` supplies the rating used the first time
a rikishi enters the registry. Implementations are:

- `ConstantInitialRatingPolicy`, which defaults to `1517`;
- `FileInitialRatingPolicy`, which loads a chii-to-rating map.

The file policy accepts:

- CSV with `chii` and either `initial_rating` or `rating`; or
- JSON keyed by a display chii or a chii ordinal.

An exact annotated chii is tried first. If it is absent, the same rank without
an annotation is tried. A file policy cannot initialize a mae-zumo rikishi
whose chii is not represented by the core model.

`KPolicy.k_for(chii)` supplies the k used for an update. Implementations are:

- `ConstantKPolicy`;
- `FideKPolicy`, which reproduces the divisional mapping used by Equelo.

For an unranked mae-zumo participant, `FideKPolicy` uses the configuration's
`max` value, currently `35`.

### `simulate.py`

Contains the simulation and its result types:

- `BashoRatings` holds the boundary ratings and appearance accounting for one
  basho;
- `SimulationResult` holds all basho snapshots, the persistent final registry,
  and run-wide counters;
- `simulate()` performs the replay.

### `output.py`

Creates a unique UTC datetime-stamped run directory, then writes the per-basho
CSV files and `manifest.json` inside it. `OutputPaths` reports both the
configured base root and the paths created by the particular run.

### `run.py`

`run_clean_elo()` is the application-level Python API. It resolves default
policies, calls `simulate()`, writes the outputs, and returns both the
`SimulationResult` and `OutputPaths`.

### `cli.py` and `__main__.py`

Provide the command-line application:

```powershell
python -m src.analysis.clean_elo --start 1989/01
```

### `index_probe.py`

Provides a standalone probe of the chii values actually encountered in
fights. It applies four nested binning policies:

- BP1 retains the complete chii;
- BP2 removes annotations and requires an east or west side;
- BP3 removes annotations and sides;
- BP4 additionally removes the number from Y/O/S/K indices.

The probe counts bout endpoints rather than banzuke positions. Paired fusen is
excluded because no fight occurred; an ordinary W/L result with no kimarite is
included. A bout endpoint whose rikishi ID is absent from that basho's banzuke
is itemised without attempting to classify it as Mz or a data error. It is not
treated as a binning-policy conversion failure because there is no source chii
to convert.

Probe runs are timestamped beneath:

```text
files/output/analysis/clean_elo/index_probe
```

They contain:

- `manifest.json`;
- `policy_summary.csv`;
- `index_frequencies.csv`;
- `frequency_bands.csv`;
- `chii_forms.csv`;
- `chii_index_map.csv`;
- `conversion_exceptions.csv`;
- `missing_banzuke_occurrences.csv`.

The probe verifies the accounting identity that converted and exceptional
endpoint occurrences, plus missing-banzuke endpoints, sum to twice the number
of eligible fights.

Every emitted index has an `index_ordinal` using the chii decimal layout.
Components removed by the selected policy are replaced by zero. The ordinal
must be interpreted together with its policy because the same integer may
mean an exact sided chii under BP1 and a collapsed index under BP3 or BP4.

The manifest records the requested start date, actual first and last processed
dates, observation and eligibility rules, BP1-BP4 definitions, run-wide
counts, policy summaries, and every output path.

### `rating_probe.py`

Provides a standalone probe of the relationship between start-of-basho Elo
ratings and banzuke indices:

```powershell
python -m src.analysis.clean_elo.rating_probe --start 1989/01
```

The unit of observation is one represented rikishi in one basho. For each
basho, the probe associates:

- the rikishi's current banzuke chii, converted under BP1 through BP4; and
- the rikishi's `initial_after_normalisation` rating.

This is intentionally not one observation per bout. A chii describes the
rikishi's position at the start of the basho. After the first bout, the
rikishi's changing daily rating is no longer being compared with a newly
assigned chii. Equivalently, an end-of-basho rating compared with the next
basho's chii is the same temporal correspondence shifted forward one basho.

Each timestamped run beneath
`files/output/analysis/clean_elo/rating_probe` writes:

- `index_rating_statistics.csv`;
- `bp1_standard_error_by_relative_margin_of_error.html`;
- `bp4_mean_rating_with_ci95.html`;
- `manifest.json`.

For each index, the CSV contains support \(n\), arithmetic mean, sample
standard deviation, standard error, a naive Student-t 95% confidence interval,
and its margin and width.

The measures answer different questions:

- sample standard deviation describes the spread of individual
  rikishi-basho ratings at an index;
- standard error estimates uncertainty in the arithmetic mean;
- the confidence interval expresses that uncertainty on the Elo scale.

The CSV's `naive_relative_margin_of_error` is:

\[
\frac{\text{95% margin of error}}{|\text{mean rating}|}
\]

This percentage is descriptive only. Elo has no natural zero and is invariant
to a common additive shift, whereas this ratio is not. It must not be confused
with a margin divided by a chosen global or index-specific rating range.

The confidence calculations are labelled `naive` because rikishi-basho
observations are not independent. The same rikishi may contribute in many
basho, ratings are generated recursively from earlier bouts, and banzuke
positions are themselves influenced by results. The current calculations show
the picture under an independence assumption; they are not the final account
of sampling uncertainty.

The BP4 mean chart uses a categorical Plotly axis, so every index is spaced
equally. The blue trace is the mean and the grey vertical marks are the naive
95% confidence intervals. Its rating axis is limited to the minimum and
maximum observed mean rating; exceptionally wide intervals at very
low-support indices can therefore be clipped at the chart boundary.

### `boundary_rating_probe.py`

Re-expresses the historical rating curve using position relative to the
current basho's lower Makuuchi boundary:

```powershell
python -m src.analysis.clean_elo.boundary_rating_probe --start 1989/01
```

The shared `analysis.boundary_positions` helper first maps every chii to its
competitive division. Y/O/S/K/M all belong to Makuuchi. Rikishi are sorted by
chii ordinal within each division and assigned:

- position from the top;
- position from the bottom.

The probe retains Makuuchi observations and emits two coordinates:

- `raw_slot`: individual distance from the bottom, beginning at 1;
- `paired_group`: \(\lceil\text{raw slot}/2\rceil\).

Thus the bottom two rikishi form `top_bottom_1`, the next two form
`top_bottom_2`, and so forth. This matches the paired boundary groups in
`toy_elo.boundary_monotonicity` without assuming that a fixed boundary
distance always has the same literal maegashira number.

Each timestamped run beneath
`files/output/analysis/clean_elo/boundary_rating_probe` writes:

- `boundary_rating_statistics.csv`;
- `boundary_curve_summary.csv`;
- `boundary_curve_fitted_values.csv`;
- `boundary_curve.html`;
- `manifest.json`.

The statistics contain the same naive Student-t quantities as `rating_probe`.
The default seven-group curve is ordered from `top_bottom_7` to
`top_bottom_1` and is tested with the same inverse-SE weighted isotonic
parametric bootstrap as `monotonicity_probe`.

The endpoint difference is defined as:

\[
\bar R_{\mathrm{top\_bottom\_1}}
-
\bar R_{\mathrm{top\_bottom\_7}}
\]

A positive value is an endpoint reversal; a negative value retains the
expected better-to-worse direction.

### `bp4_cutoff_probe.py`

Runs a series of no-replacement lower-maegashira deletion experiments:

```powershell
python -m src.analysis.clean_elo.bp4_cutoff_probe --start 1989/01
```

The runner defaults to first-excluded rank numbers 19, 18, ..., 12. For
cutoff \(n\):

1. every bout involving a rikishi currently ranked M\(n\) through M18 is
   removed;
2. no alternative opponent is supplied and absence inference is disabled;
3. Elo is replayed from the requested start date;
4. one start-of-basho rating observation is collected for each represented
   rikishi at BP4 indices Y, O, S, K, and M1 through M\(n-1\);
5. adjacent increases in mean rating as the BP4 ordinal worsens are counted
   as monotonicity violations.

Cutoff 19 is defined as the unmodified baseline and reports Y through M18.
Cutoff 18 removes M18 bouts and reports through M17; cutoff 17 removes
M17--M18 bouts and reports through M16; and so on.

The filtered history retains all daily records and rebuilds each day's
`results_lookup` and `torikumi` from retained bouts. A rikishi's other career
appearances are unaffected: the bout is removed only when the rikishi
occupies an excluded rank.

Each timestamped run beneath
`files/output/analysis/clean_elo/bp4_cutoff_probe` writes:

- `bp4_cutoff_ratings.csv`, a wide table with one row per cutoff and one
  rating column per BP4 index;
- `bp4_index_ordinals.csv`, the ordinal corresponding to every table column;
- `bp4_cutoff_violations.csv`, the location and size of every adjacent
  increase;
- `manifest.json`, recording cutoffs, removed and rated bout counts, and
  violation summaries.

This is a point-mean diagnostic rather than the bootstrap goodness-of-fit
test used by `monotonicity_probe.py`. Equality is permitted; only a strict
increase at the next weaker index is counted as a violation.

### `monotonicity_probe.py`

Consumes the BP4 summaries written by `rating_probe.py`:

```powershell
python -m src.analysis.clean_elo.monotonicity_probe `
  files/output/analysis/clean_elo/rating_probe/RUN/index_rating_statistics.csv
```

It tests the null hypothesis:

> Expected BP4 mean start-of-basho Elo rating is non-increasing as index
> ordinal increases.

Two scopes are reported:

- M1 through M18;
- Y through Jd100.

The null model is the weighted least-squares non-increasing isotonic
regression of the observed group means. The weight for index \(i\) is:

\[
w_i = \frac{1}{SE_i^2}
\]

The lack-of-fit statistic is:

\[
Q =
\sum_i
\left(
\frac{\bar R_i-\hat R_i^{\mathrm{iso}}}{SE_i}
\right)^2
\]

where \(\bar R_i\) is the observed mean and
\(\hat R_i^{\mathrm{iso}}\) is the fitted monotonic mean.

The p-value is calculated by a plug-in parametric bootstrap:

1. Generate independent normal group means around the fitted null means,
   using the observed standard errors.
2. Refit the isotonic model to each generated dataset.
3. Recalculate \(Q\).
4. Count how often the generated statistic is at least the observed one.

The reported p-value uses the plus-one calculation:

\[
p = \frac{\text{exceedances}+1}{B+1}
\]

where \(B\) is the number of bootstrap simulations. Consequently, zero
exceedances from 10,000 simulations is reported as \(1/10001\), not as a
literal probability of zero.

Each timestamped run beneath
`files/output/analysis/clean_elo/monotonicity_probe` writes:

- `monotonicity_test_summary.csv`;
- `monotonicity_fitted_values.csv`;
- `manifest.json`.

The fitted-values file includes the observed mean, isotonic fitted mean,
residual, and standardized residual for every tested index. The manifest
records the null hypothesis, weighting, bootstrap method, source statistics
file, random seed, and limitations.

This test inherits the rating probe's independence assumption. It additionally
treats the estimated standard errors as fixed and uses a normal approximation
for group means. It tests monotonicity of conditional mean Elo by BP4 index;
it does not test every possible claim about what chii mean.

The numerical 1989+ results and their interpretation are recorded in
[Rating Probe Findings](Rating%20Probe%20Findings.md).

## Elo calculation

For ratings \(R_a\) and \(R_b\), the expected score for \(a\) is:

\[
E_a = \frac{1}{1 + 10^{(R_b-R_a)/q}}
\]

The update is:

\[
R'_a = R_a + k_a(S_a-E_a)
\]

and likewise for \(b\), using \(b\)'s own k. Consequently, a bout between
rikishi with different k values need not preserve their combined rating.
End-of-basho normalization removes the resulting change in the population
mean.

W and FS have score 1; L and FP have score 0; a draw has score 0.5.

The `decision` field is not used to decide whether an ordinary W/L result is
valid. In particular, `decision == "blank"` means that the kimarite is absent;
the recorded W/L outcome is still rated.

## Persistent registry

The simulator owns a registry:

```text
RikId -> current rating
```

A rikishi not already in the registry is initialized on first inclusion in a
basho population. Once present, the rating remains in the registry even if the
rikishi is absent from later basho. If the rikishi reappears, the persisted
rating is reused.

With absence counting disabled, the basho population consists of everyone in
at least one recorded result. This includes participants in a paired fusen
result even though that result is not rated.

With absence counting enabled, the population additionally contains banzuke
rikishi whose divisions qualify for absence inference. This means a rikishi
who is kyujo for an entire basho can be initialized despite having no recorded
bout.

## Processing order for a basho

For every history date whose numeric `(year, month)` is at or after the start
date, the simulator:

1. Counts recorded appearances by rikishi and by day.
2. Determines which divisions have represented results.
3. Builds the current basho population.
4. Initializes previously unseen members of that population.
5. Records their initial ratings before normalization.
6. Shifts the current population to the fixed target mean.
7. Records the initial ratings after normalization.
8. Processes recorded results in day order.
9. Optionally applies inferred kyujo adjustments.
10. Shifts the current population back to the target mean.
11. Persists and records the normalized final ratings.

Numeric date comparison is intentional. Live histories can use a subclass of
the core `Date`, whose object equality does not recognize an otherwise equal
core `Date`.

## Target mean and normalization

The target is the mean of the first non-empty basho population immediately
after initialization and before any normalization. It is not a separately
configured constant. With the default initialization policy, it is `1517`.

For current mean \(\bar R\) and target mean \(M\), every member of the current
basho population receives the same adjustment:

\[
\Delta_{\text{normalization}} = M-\bar R
\]

This preserves every rating difference within that population.

Normalization is performed:

- once at basho entry, after new members have been initialized; and
- once at basho end, after results and optional kyujo adjustments.

The scope is the current basho population. Ratings retained in the registry
for rikishi outside that population are unchanged.

## Absence accounting

`count_absences` defaults to `False`.

### Disabled

- Ordinary W/L and draw results are rated.
- Paired FS/FP results are counted as appearances but are not rated.
- No opponentless kyujo is inferred.

### Enabled

- Paired FS/FP results are rated against the recorded opponent.
- Opponentless kyujo is inferred from the banzuke and recorded appearances.
- Each inferred absence is scored as a loss to a virtual opponent with the
  same current rating.

The virtual opponent therefore has expected score \(1/2\), giving the raw
adjustment:

\[
\Delta_{\text{kyujo}} = -k/2
\]

The virtual opponent is not stored and receives no compensating rating gain.
The end-of-basho normalization restores the population mean, so the final
normalized difference is not simply the raw \(-k/2\).

### Preconditions for inference

Opponentless absences are inferred only when:

- day 15 exists in the basho summary, so an in-progress basho is not treated
  as having future absences; and
- the rikishi's division is represented by at least one recorded bout between
  two banzuke members of that same division.

The second rule prevents a lone interdivisional bout from being treated as
evidence that the lower division's complete result set is present.

The current model assumes that, once a division meets this representation
test, its result data for that basho is complete.

### Sekitori

Makuuchi and Juryo rikishi are sekitori and are expected to appear on all 15
days. After each day's recorded results are processed, a represented
sekitori who did not appear that day receives one inferred \(-k/2\)
adjustment.

An FP is an appearance, so it is not also counted as an opponentless absence.

### Sub-sekitori

Makushita, Sandanme, Jonidan, and Jonokuchi rikishi are expected to have seven
appearances across the basho. Their scheduled days cannot be inferred merely
from daily non-appearance, so their deficit is calculated at basho end:

\[
\text{inferred absences} =
\max(0, 7-\text{recorded appearances})
\]

All of those inferred losses are then applied together. An FP contributes to
the recorded-appearance total.

Mae-zumo rikishi have no modeled division and are therefore not candidates
for opponentless absence inference.

### Authoritative rating boundary

Only the normalized end-of-basho ratings should be treated as complete model
outputs.

Sekitori absences can be identified and applied day by day, but the scheduled
days of sub-sekitori are not known from non-appearance. Their inferred
absences are therefore calculated and applied together at basho end. Until
that calculation has been performed, an in-progress sub-sekitori rating does
not yet include every adjustment attributable to that basho.

The population mean is also restored only by the final basho normalization.
Intermediate ratings may therefore reflect both unapplied sub-sekitori
absence adjustments and temporary changes in the total points held by the
current population. The next basho starts from the completed, normalized
end-of-basho ratings.

## Output

The default base root is:

```text
files/output/analysis/clean_elo
```

Every invocation creates a child directory whose name is a UTC timestamp in
`YYYY-MM-DD_HH-MM-SS` format:

```text
files/output/analysis/clean_elo/2026-07-24_22-15-30/
```

Directory creation is exclusive. In the unlikely event of a timestamp
collision, the code selects the next unused second. Existing run directories
are never reused or overwritten.

Within a run directory, every `basho/YYYY_MM.csv` contains the ordinary Elo
schema:

- `rikid`;
- `shikona`;
- display `chii`;
- authoritative `chii_ordinal`;
- initial rating before normalization;
- initial rating after normalization;
- final rating after normalization;
- the common initial normalization adjustment;
- the common final normalization adjustment.

When `count_absences=True`, the run uses a distinct extended schema that also
contains:

- recorded appearances;
- expected appearances;
- inferred absences;
- raw absence rating adjustment.

The absence columns are not written at all when absence counting is disabled.
Their absence distinguishes “this model does not calculate absences” from an
extended-schema value of zero, which means that absence accounting was
performed and found no missing appearances for that rikishi.

Whenever a chii is written, its ordinal is written as a separate field. The
ordinal is the authoritative identity; the display string is for people.

Within an extended-schema run, `expected_appearances` is 0 when inference
cannot be applied to that rikishi because the basho or division does not meet
the inference preconditions.

`manifest.json` records:

- the model and generation time;
- the configured base output root and the actual stamped run directory;
- start date, target mean, and q;
- whether absences were counted;
- resolved initialization and k policy metadata;
- rated-bout, ignored-fusen, and inferred-absence totals;
- all generated basho CSV paths.

## Python API examples

Use all defaults:

```python
from src.analysis.clean_elo import simulate

result = simulate(history, start_date)
```

Count paired and opponentless absences:

```python
result = simulate(
    history,
    start_date,
    count_absences=True,
)
```

Run the simulator and write files:

```python
from src.analysis.clean_elo import run_clean_elo

result, paths = run_clean_elo(
    history=history,
    start_date=start_date,
    count_absences=True,
)
```

## CLI options

Examples:

```powershell
# Default: do not count absences
python -m src.analysis.clean_elo --start 1989/01

# Count paired fusen and inferred opponentless kyujo
python -m src.analysis.clean_elo --start 1989/01 --count-absences

# Explicit boolean form
python -m src.analysis.clean_elo --start 1989/01 --count-absences true

# Constant k
python -m src.analysis.clean_elo --start 1989/01 --k-value 35

# Rank-based initial ratings
python -m src.analysis.clean_elo --start 1989/01 `
  --initial-ratings-file path/to/ratings.json
```
