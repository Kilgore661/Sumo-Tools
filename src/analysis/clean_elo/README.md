# Clean Elo

## Research status

This package is a completed experimental investigation rather than the basis
of a uniquely correct sumo rating system. Its final research objective was to
understand precisely why a persistent Elo-like ordering does not correlate
perfectly with chii, and to find a defensible account of the disagreement.

That objective was not achieved. The experiments established broad agreement
between rating and chii, identified variable banzuke structure as an important
part of the lower-maegashira anomaly, and ruled out several simple
explanations. They did not produce a complete explanation or a principled
adjustment that makes the two orderings agree. In that limited and explicit
sense, `clean_elo` is a failed experiment. The negative result is retained
because it constrains later claims and may be useful to others.

The project no longer assumes that sufficiently deep investigation must yield
an Elo-like system about which no reasonable observer could disagree. An
Equelo rating is instead treated as one transparent, reproducible estimate of
comparative performance. It can be interesting or useful without being a
perfect representation of ability and without reproducing chii. The
project-level position and its consequences are set out in
[What Is an Equelo Rating?](../../../docs/What%20is%20an%20Equelo%20Rating.md).

The implementation and reports below are therefore an experimental record,
not a recipe for forcing ratings to match the banzuke. Further work should
test and justify the stated Equelo policies and decide what, if anything, is
appropriate for a public deliverable.

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

## Boundary rating probe

The boundary rating probe replaces literal rank number with position relative
to the current basho's lower Makuuchi boundary:

```powershell
python -m src.analysis.clean_elo.boundary_rating_probe --start 1989/01
```

It emits both individual boundary slots and paired no-side groups. The bottom
two Makuuchi rikishi form `top_bottom_1`, the next two form
`top_bottom_2`, and so on.

For the 1989+ data, the paired seven-group endpoint difference is -9.31 rather
than the positive M12-M18 reversal. The naive isotonic test does not reject
monotonicity (`p = 0.552`). The previously identified reversal is therefore
not present once the observations are aligned by actual boundary distance.

## BP4 cutoff probe

The BP4 cutoff probe runs the no-replacement lower-maegashira deletion
experiment for first-excluded ranks 19 through 12:

```powershell
python -m src.analysis.clean_elo.bp4_cutoff_probe --start 1989/01
```

For cutoff \(n\), bouts involving M\(n\) through M18 are removed, absence
inference remains disabled, and Elo is replayed. The reported BP4 sequence is
Y, O, S, K, and M1 through M\(n-1\). Cutoff 19 is the unmodified baseline.

The console reports the number and location of adjacent mean-rating increases
for every cutoff. Each timestamped run beneath
`files/output/analysis/clean_elo/bp4_cutoff_probe` writes the wide cutoff-by-
rating table, index ordinals, violation details, and a provenance manifest.

The latest 1989+ run is
`files/output/analysis/clean_elo/bp4_cutoff_probe/2026-07-30_19-15-08`.
For cutoffs 19 through 12 it found respectively 6, 5, 4, 3, 2, 2, 2, and 3
point-mean violations. None of the tested deletions produced a monotonic
sequence. Initially the count fell only because the last violating index was
removed from scope; stronger cutoffs produced new reversals at M9--M11 and,
for cutoff 12, at M5--M6. See
[Rating Probe Findings](docs/Rating%20Probe%20Findings.md) for the full report
and interpretation.
