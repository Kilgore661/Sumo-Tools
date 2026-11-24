# Torikumi infrastructure

> **Retrospective documentation (November 2026).** This README was written
> after the Torikumi feature had been implemented because its original
> requirements were not recorded. It describes intent inferred from the
> current code, tests, artifacts and published page, and should not be read as
> a contemporaneous specification.

`src.infra.torikumi` acquires, validates and persists the published bout
schedule for the active or immediate upcoming basho. Its output is a typed
`Future` snapshot which analysis code can combine with ratings and other
domain data.

This package owns schedule-source infrastructure. It does **not** calculate
ratings or probabilities, build website tables, modify canonical `History`,
or write into the ordinary daily-results cache.

```text
History + optional NewBanzuke
  -> select active or upcoming target
  -> probe SumoDB Results.aspx for Days 1..15
  -> recognize published schedules and unpublished pages
  -> parse ordered East/West bouts
  -> persist raw pages and future.json as one coherent refresh
  -> src.analysis.site89.torikumi
  -> rating-annotated public CSVs
```

## Why this is separate from results

One SumoDB `Results.aspx` URL moves through a lifecycle:

```text
unpublished -> published torikumi -> completed results
```

The mature results pipeline is concerned with incorporating completed outcomes
into `History`. This package is concerned with preserving the published
schedule, including days whose bouts have not happened yet. It therefore uses
its own raw cache under `files/output/torikumi/raw` and its own parser.

The parser counts rows which already contain results for diagnostics, but the
`Future` model retains only the pairing, orientation, order, identities and
source labels. It does not publish winners or outcomes.

## Target selection

`resolve_torikumi_target()` selects exactly one coherent target:

1. If the latest basho in `History` is incomplete, that active basho is the
   target.
2. Otherwise, if `NewBanzuke` represents the immediate successor to the
   completed History, that upcoming basho is the target.
3. Otherwise there is no Torikumi target and the command exits without
   refreshing anything.

The immediate-successor rule also covers the November-to-January year
transition. A newer banzuke with a gap is rejected rather than silently joined
to the wrong History.

An upcoming target depends on the independently produced artifact at:

```text
files/output/infra/new_banzuke/new_banzuke.json
```

Produce it with:

```powershell
py -m src.infra.new_banzuke
```

## Acquisition and refresh semantics

`refresh_future()` probes the bounded range Day 1 through Day 15. It
distinguishes:

- a positively recognized schedule page;
- SumoDB's valid HTTP-200 shell for an unpublished day;
- HTTP 404, also treated as unpublished;
- transport or other HTTP failures; and
- unrecognized or malformed HTML.

The first unpublished day ends the probe normally. Network failures and
unrecognized pages raise `TorikumiRefreshError`.

For a snapshot already representing the same basho, a refresh retains the
known published-day prefix and can update its last day or extend it with newly
published days. A refresh is rejected if it would discard an already persisted
day. Raw pages and `future.json` are not written until the complete network and
parse probe has succeeded, so those acquisition failures preserve the saved
snapshot.

The command-level policy is:

- on refresh failure, retain an existing snapshot only when it represents the
  selected target basho;
- fail rather than use a snapshot for a different basho; and
- treat zero published days for a valid target as a legitimate empty snapshot.

## Data model

The package exposes three immutable models:

- `FutureBout`: source order, East and West rikishi IDs, and optional source
  shikona;
- `FutureDay`: one published day's non-empty ordered bouts, source URL,
  acquisition time and diagnostic result count;
- `Future`: target basho, the last completed History day if applicable, all
  available schedule days and snapshot generation time.

Persistence is deterministic JSON with an explicit schema version. The
default artifact is:

```text
files/output/torikumi/future.json
```

A simplified payload has this shape:

```json
{
  "schema_version": 1,
  "basho": "2026/11",
  "completed_through": 3,
  "generated_at": "2026-11-11T12:00:00+00:00",
  "days": [
    {
      "day": 4,
      "source_url": "https://sumodb.sumogames.de/Results.aspx?...",
      "downloaded_at": "2026-11-11T12:00:00+00:00",
      "result_count": 0,
      "bouts": [
        {
          "order": 1,
          "east": 123,
          "west": 456,
          "east_shikona": "East",
          "west_shikona": "West"
        }
      ]
    }
  ]
}
```

An empty `days` list means that the target is coherent but no schedule has yet
been published. It is not evidence that the feature is absent or broken.

## Command line

Refresh from the live History and the default New Banzuke artifact:

```powershell
py -m src.infra.torikumi
```

Use an explicit, reproducible History snapshot:

```powershell
py -m src.infra.torikumi `
  --history-zip ".\files\output\Historys\1989_01 to 2026_11.zip"
```

Useful options are:

- `--history-zip PATH`: load an annotated History zip instead of the live
  store;
- `--new-banzuke PATH`: select another typed New Banzuke artifact; and
- `--output-root PATH`: write the raw cache and `future.json` elsewhere.

The default live-store path requires the tracker to be running and publishing
a History. There is no automatic live-store-to-zip fallback.

## Package map

| Module | Responsibility |
| --- | --- |
| `model.py` | Immutable `Future`, `FutureDay` and `FutureBout` types and their invariants. |
| `target.py` | Active/upcoming target selection and basho-successor rules. |
| `scraper.py` | Bounded probing, source classification, refresh preservation and raw-page persistence. |
| `parser.py` | Validation of the requested basho/day and extraction of ordered East/West pairings. |
| `persistence.py` | Versioned deterministic JSON save/load functions. |
| `__main__.py` | Live-store or explicit-zip CLI and retained-snapshot failure policy. |

The public API is re-exported from `src.infra.torikumi`:

```python
from src.infra.torikumi import (
    Future,
    TorikumiRefreshError,
    load_future,
    refresh_future,
    resolve_torikumi_target,
)
```

## Publication integration

The Sumo '89 boot workflows produce `NewBanzuke`, refresh `Future`, and then
produce the site-data bundle. `src.analysis.site89.torikumi` combines History
and the current snapshot with:

- the matching History or upcoming banzuke;
- Elo-89 ratings immediately before each published day; and
- projected next-basho start ratings when the target is not yet in History.

It writes one CSV per basho plus an index containing the fifteen day states and
daily division summaries. The public page uses the Basho Results calendar
selector and a four-column day grid. No day is selected by default; unavailable
days are disabled. Selecting a day shows the bouts, fair decimal Elo89 odds,
the favourite prediction and (where results exist) whether it was correct.
Fusen and exact rating ties are omitted from the tally. The summary also shows
the return from staking £1 on each favourite, £1 on each higher-chii rikishi
and, as a hindsight benchmark, £1 on each winner.

## Relationship to decimal-odds analysis

[`src.analysis.decimal_odds`](../../analysis/decimal_odds/README.md) is a newer,
exploratory analysis of pre-bout Elo probabilities and externally quoted odds.
The packages are not currently integrated: `decimal_odds` reads the selected
bouts in an external-odds file and resolves their identities independently,
whereas this package acquires the complete published schedule and deliberately
contains no ratings or market policy.

The public Torikumi artifact now performs the first three steps of that
connection: it uses `Future` for published future pairings, `History` for
completed schedules and outcomes, and pre-bout ratings for fair odds. External
market odds remain separate exploratory work. Probability, scoring and
presentation policy remain in the analysis/product layers rather than this
infrastructure package.

## Tests and deeper documentation

Run the focused infrastructure and lifecycle coverage with:

```powershell
.\.venv\Scripts\python.exe -m pytest -s `
  tests\test_torikumi_infra.py `
  tests\test_torikumi_lifecycle.py `
  tests\test_make_site89_bundle.py
```

The tests cover parsing, deterministic persistence, target selection,
published/unpublished classification, refresh preservation, upcoming-basho
ratings and bundle validation.

For the design history and the pre-basho lifecycle repair, see:

- [`docs/Proposal.md`](docs/Proposal.md)
- [`docs/Lifecycle Repair Proposal.md`](docs/Lifecycle%20Repair%20Proposal.md)
