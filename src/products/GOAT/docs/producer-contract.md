# GOAT prototype producer contract, version 1

## Boundary

The first producer creates spreadsheet-ready facts and descriptive aggregates
from the complete `History`. It does not decide what constitutes GOATness and
does not rank rikishi.

```python
build_goat_facts(history, output_root, labels=None)
```

The same function is used whether the caller obtains `History` from the live
store or a canonical zip. The command-line entry point is `python -m src.goat`.

## CSV-only output

The version-1 prototype uses CSV throughout:

```text
manifest.csv
rikishi.csv
basho.csv
banzuke.csv
bouts.csv
markers.csv
playoffs.csv
rikishi_summary.csv
summary_definitions.csv
coverage.csv
validation.csv
```

CSV makes every artifact directly inspectable in a spreadsheet. Files use
UTF-8, a header row, standard quoting and deterministic ordering.

## Date coverage

The data epoch begins in January 1958, but there is no single analytical start
date for every possible aggregate.

- Banzuke, Makuuchi bouts, Juryo bouts and performance markers are published
  from 1958/01.
- Sub-sekitori bouts are complete from 1989/01. Earlier records are retained as
  facts but described as incomplete.
- Detailed playoff bouts have per-basho availability and may be wholly absent
  until the parser supplies `History.playoffs`.

Missing earlier lower-division bouts are never converted into zeroes. A later
aggregate must declare the facts it uses and adopt their applicable boundary.

## Factual tables

### `rikishi.csv`

One row for every rikishi referenced by the published facts: ID, latest known
display shikona, presence on the latest banzuke, first and last banzuke, and
first and last Makuuchi banzuke. Blank dates mean inapplicable or unavailable,
not zero.

### `basho.csv`

One row per represented banzuke, with a consecutive sequence, tournament
status and playoff-data status. May 2011 is labelled
`technical_examination`; this layer does not decide how a championship metric
should treat it.

### `banzuke.csv`

One row per occupant, retaining shikona, display chii, division, number, side,
annotation and Makuuchi level (`Y`, `O`, `S`, `K` or `M`). It also publishes a
transparent opposition level index, recalculated for each banzuke:

```text
Y=0, O=1, S=2, K=3, M1=4, M2=5, ...,
J1=(the level after the last Maegashira rank), J2=the next level, ...
```

East and west at the same level receive the same value.

### `bouts.csv`

One row per recorded scheduled bout, not one row per rikishi perspective. It
contains the basho, day, both rikishi IDs, both `W`/`L`/`FS`/`FP`/`DRAW`
outcomes, decision and source symbol.

### `markers.csv`

One row per recorded `Y`, `D`, `J`, `K`, `G` or `S` marker. Markers remain raw
administrative facts at this layer.

### `playoffs.csv`

When available, one row per detailed playoff bout contains basho, sequence,
winner ID, loser ID and source. Without `History.playoffs`, the file contains
its header and no data rows; `basho.csv` reports whether missing detail was
needed for a particular basho.

## Spreadsheet summary

`rikishi_summary.csv` contains one row for every rikishi who appears on a
Makuuchi banzuke in the data epoch. Version 1 supplies:

- identity, active status and Makuuchi career bounds;
- Makuuchi- and Yokozuna-banzuke basho from 1958;
- Makuuchi `Y`, `D`, `J`, `K`, `G` and `S` markers from 1958;
- recorded Makuuchi `W` and `FS` outcomes from 1958; and
- recorded all-division `W` and `FS` outcomes from 1989.

It also supplies Makuuchi strength-of-opposition descriptions from 1958:

- supported contested-bout count and opponent-level sum;
- mean opponent level;
- mean level defeated;
- mean level lost to; and
- contested bouts without a supported opponent level.

Only `W` and `L` bouts contribute. `FS` and `FP` do not. Lower opposition
indices mean stronger schedules or opponents.

Column names include scope and epoch—for example,
`makuuchi_W_1958_onwards` and `all_division_W_1989_onwards`. There is no
ambiguous `total_wins` column.

These values are descriptive conveniences. Their presence does not make them
approved GOAT criteria. `summary_definitions.csv` gives the exact definition,
complete-from date and status of every descriptive column.

## Metadata and validation

`coverage.csv` records completeness by fact and division.

`validation.csv` reports uniqueness and referential-integrity checks. A failed
check makes the build fail. Missing optional playoff detail is a capability
state, not a validation failure.

`manifest.csv` records contract and schema versions, History bounds, every
file's row count and SHA-256 digest, and explicitly states that no GOAT ranking
is included.

## Acceptance

The prototype producer is acceptable when:

1. the live-store and zip paths produce the same rows for the same `History`;
2. every output is CSV and spreadsheet-readable;
3. source facts reconcile with their published rows;
4. Makuuchi aggregates can use 1958 while sub-sekitori-dependent aggregates
   respect the 1989 boundary;
5. `W` and `FS` remain separately visible; and
6. absence of detailed playoff data does not block the remaining output.
