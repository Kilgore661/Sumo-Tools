# Clean Elo

See [docs/Code Description.md](docs/Code%20Description.md) for the detailed
code and data-flow description.

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
- recorded and expected appearances, inferred absences, and their raw rating
  adjustment;
- the initial and final common adjustments.

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
