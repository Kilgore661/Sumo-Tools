# Clean Elo

See:

- [Code Description](docs/Code%20Description.md) for the detailed code,
  algorithms, output schemas, and probe methods;
- [Rating Probe Findings](docs/Rating%20Probe%20Findings.md) for the research
  questions, 1989+ results, interpretation, and limitations.

`clean_elo` simulates ordinary Elo updates over every available sumo result
from a supplied start date.

The model has two defining properties:

1. Once a rikishi receives a rating, that rating persists across missing basho
   and is reused on the rikishi's next represented bout.
2. At basho boundaries, the represented basho population is shifted uniformly
   to a fixed mean. The target is the mean of the first represented basho before
   any normalisation.

Uniform normalisation preserves every rating difference and therefore every Elo
expectation.

## Policies

The default initial rating is `1517`.

The default k policy is the existing FIDE-style divisional policy in
`files/input/elo_fide.json`. A constant k can be selected instead.
These defaults apply both to the Python API and the CLI.

Initial ratings may be loaded from:

- CSV containing `chii` and either `initial_rating` or `rating`; or
- JSON mapping chii display strings or ordinal strings to ratings (including
  the existing `fixed_v1/entrant_initial_ratings.json` format).

Annotated chii fall back to the corresponding unannotated rank when a file map
does not contain the exact annotated value.

Mae-zumo entrants may occur in bouts without a modeled rank. Under the defaults
they receive rating `1517` and the FIDE fallback k (`max`, currently `35`).
A rank-based initial-rating file cannot initialize an entrant with no chii and
reports that data-policy mismatch explicitly.

## Decisions

- Ordinary scored bouts are rated.
- A blank decision means only that the kimarite is unavailable; its W/L result
  is rated normally.
- Absences are ignored by default.
- `count_absences=True` rates paired FS/FP and infers opponentless kyujo for
  completed, represented divisions. Each inferred absence costs `k / 2`.

## Output

Each basho CSV contains:

- the human-readable chii and its authoritative ordinal;
- the rating at basho entry before normalisation;
- the rating at basho entry after normalisation;
- the final rating after results and final normalisation;
- the initial and final common adjustments.

With absence counting enabled, the CSV uses an extended schema that also
contains recorded and expected appearances, inferred absences, and their raw
rating adjustment. With it disabled, those columns are not written.

With absence counting disabled, only represented rikishi appear in a basho
file. With it enabled, banzuke rikishi subject to absence accounting also
appear. The internal registry retains all previously rated rikishi.

The normalized end-of-basho ratings are the authoritative outputs.
Sub-sekitori absence deficits and final mean restoration are applied only at
that boundary, so intermediate daily ratings would be provisional.
The default output root follows the package path:
`files/output/analysis/clean_elo`.
Each invocation creates a UTC `YYYY-MM-DD_HH-MM-SS` directory beneath that
root, so an earlier run is never overwritten.

## CLI

The CLI reads the current live History:

```powershell
python -m src.analysis.clean_elo --start 1989/01
```

Use `--help` for policy and output options.

## Index probe

The standalone index probe measures the observed chii domain under BP1 through
BP4:

```powershell
python -m src.analysis.clean_elo.index_probe --start 1958/01
```

Each timestamped probe run writes policy summaries, marginal index
frequencies, frequency bands, raw chii-form frequencies, the complete
raw-chii-to-index map, true policy conversion exceptions, unbanzuked bout
endpoints, and a provenance manifest beneath
`files/output/analysis/clean_elo/index_probe`.

Every emitted index is accompanied by its policy-qualified `index_ordinal`.
Components removed by a policy are encoded as zero.

## Rating and monotonicity probes

The rating probe associates each rikishi's start-of-basho rating with the
rikishi's current banzuke index:

```powershell
python -m src.analysis.clean_elo.rating_probe --start 1989/01
```

It writes one observation per rikishi-basho, summary statistics by index, and
interactive Plotly charts beneath
`files/output/analysis/clean_elo/rating_probe`.

The monotonicity probe consumes one of those
`index_rating_statistics.csv` files:

```powershell
python -m src.analysis.clean_elo.monotonicity_probe `
  files/output/analysis/clean_elo/rating_probe/RUN/index_rating_statistics.csv
```

It tests the null hypothesis that expected BP4 mean rating is non-increasing
as the index ordinal worsens. Results are reported separately for M1--M18 and
for Y--Jd100. The probe fits a weighted non-increasing isotonic regression and
uses a reproducible parametric bootstrap goodness-of-fit test.

This first test is deliberately naive: it treats the rikishi-basho
observations as independent and treats their estimated standard errors as
fixed. The output manifest records these limitations.

For the 1989+ data, the M1--M18 test produced no bootstrap result as extreme as
the observation in 10,000 simulations (`p = 1/10001` under the plus-one
calculation). Sensitivity checks show that the rejection is already decisive
when M16 is included, so it is not an artefact of the six M18 observations.
This rejects a simple immutable monotonic mapping from BP4 index to mean Elo
under the naive model; it does not establish that chii fail to measure
performance in every relevant sense.
