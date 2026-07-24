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

Within a run directory, each `basho/YYYY_MM.csv` contains:

- `rikid`;
- `shikona`;
- display `chii`;
- authoritative `chii_ordinal`;
- initial rating before normalization;
- initial rating after normalization;
- final rating after normalization;
- recorded appearances;
- expected appearances;
- inferred absences;
- raw absence rating adjustment;
- the common initial normalization adjustment;
- the common final normalization adjustment.

Whenever a chii is written, its ordinal is written as a separate field. The
ordinal is the authoritative identity; the display string is for people.

When absence inference is disabled or does not apply to a rikishi,
`expected_appearances` is 0 and the absence fields contain zero adjustments.

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
