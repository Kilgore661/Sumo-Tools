# BRB Producer Implementation Proposal

## Purpose

Implement the producer for the Basho Results Browser (BRB).

The producer writes the static data files consumed by the BRB
`IndexedTablePA`.  The renderer is a separate job, but this producer proposal
defines the contract the renderer should be able to rely on.

## Public Question

For a selected basho date and division:

> What was the state of play for each rikishi in this basho, with optional
> previous-basho and rating context?

The default user experience is intentionally basic.  The data files should also
support progressively nerdier options, including previous-basho movement,
previous result, fixed_v2 Equelo ratings, rating change, and `νChii`.

## Output Root

Write producer outputs under:

```text
files/output/basho_results/
```

The intended public-site copy target is:

```text
sumo-history/basho-results/data/
```

## File Layout

Use one index file and one payload file per represented basho:

```text
files/output/basho_results/
  basho_results_index.json
  by-basho/
    2026-03.csv
    2026-05.csv
    ...
```

Each per-basho CSV contains all divisions for that basho.  The renderer loads
one basho payload, then filters division client-side.

## Index Contract

`basho_results_index.json` should be JSON with this shape:

```json
{
  "schema": "sumo-tools.basho-results.index.v0",
  "generated_at": "2026-05-12T18:45:00+01:00",
  "default_basho": "2026/05",
  "entries": [
    {
      "basho": "2026/05",
      "year": 2026,
      "month": 5,
      "label": "May 2026",
      "status": "in_basho",
      "latest_day": 3,
      "payload_path": "data/by-basho/2026-05.csv"
    }
  ]
}
```

### Status Vocabulary

`status` describes the static payload state at producer generation time, not
the state at page visit time.

Use:

| Status | Meaning |
| --- | --- |
| `in_basho` | At least Day 1 is available, but the basho is not complete. |
| `post_basho_pre_banzuke` | All results are available, but the next banzuke is not known. |
| `post_banzuke_pre_basho` | The next banzuke is known, but the next basho has not started. |
| `completed` | Historical settled state; results and next-banzuke context are available and the basho is no longer the current publication window. |

The first producer may mark historical non-current basho as `completed`.

### Default Basho

`default_basho` should be the latest generated payload.

## Payload CSV Contract

Each payload CSV is one row per rikishi across all represented divisions in the
selected basho.

Required columns:

```text
basho
division_id
division_label
rikishi_id
shikona
graph_shikona
chii
chii_ordinal
score
previous_delta_direction
previous_delta
previous_result
previous_chii
previous_chii_ordinal
previous_equelo
equelo
delta_equelo
nu_chii
nu_chii_ordinal
```

Unavailable values should be written as:

```text
-
```

Use `YYYY-MM.csv` file names for payloads.

## Column Semantics

### Identity

`shikona` is the displayed shikona for the selected basho.

`graph_shikona` should use the existing site convention for graph links.  Reuse
the Banzuke Change Report helper initially if no shared identity/linking
service exists yet.

`chii` is the official rank slot at the start of the selected basho.

`chii_ordinal` is the semantic sort key from `Chii.ordinal()`.

### Score

Use the same score rules as Banzuke Change Report:

* `Outcome.W` and `Outcome.FS` count as wins;
* `Outcome.L` and `Outcome.FP` count as losses;
* expected bouts are 15 for Makuuchi and Juryo;
* expected bouts are 7 below Juryo;
* absences are expected bouts minus recorded available bouts;
* display `wins-losses` when absences are zero;
* display `wins-losses-absences` when absences are nonzero.

Reuse or adapt:

```text
src/analysis/banzuke_compare/results.py
```

### Previous Basho Context

Previous-basho context should mirror Banzuke Change Report semantics where
possible:

* `previous_chii` is the rikishi's chii on the previous banzuke, if present;
* `previous_result` is the previous basho result, including prize letters where
  available;
* `previous_delta_direction` and `previous_delta` describe movement from the
  previous basho to the selected basho using occupied banzuke slots;
* `previous_equelo` is the fixed_v2 day-end rating after the previous basho.

Entrants or rikishi without previous context should use `-`.

### Rating Context

Use fixed_v2 process ratings:

```text
files/output/Equelo/fixed_v2/day_end_ratings.json
files/output/Equelo/fixed_v2/entrant_initial_ratings.json
```

Do not use `Typical Equelo Ratings` as row-level lookup values.  Those are
public landmarks only.

For a selected basho:

* `previous_equelo` is the previous basho end rating;
* `equelo` is the rating at the represented payload point:
  * final day-end rating for complete historical payloads;
  * latest available day-end rating for in-basho payloads;
* `delta_equelo` is `equelo - start_equelo`;
* `start_equelo` is normally the previous represented rating for that rikishi;
* if there is no previous rating, use the fixed_v2 entrant initial rating for
  the selected basho chii.

The producer may compute `start_equelo` internally without publishing it as a
column in v1.

### `νChii`

`νChii` belongs to the after/during context.

For v1:

* if the actual next banzuke chii is known, publish it;
* otherwise publish `-`;
* publish `nu_chii_ordinal` when `nu_chii` is available, otherwise `-`.

The estimated `νChii` algorithm remains TBD.  Do not block the first producer
on it.

## Suggested Module Layout

Implement under:

```text
src/analysis/sumo_history/basho_results/
```

Suggested files:

```text
classes.py     BRB row, index entry, and output dataclasses
dates.py       represented basho date/index helpers
records.py     BRB-facing wrappers around BCR record logic
ratings.py     fixed_v2 rating lookup helpers
build.py       build one basho payload and the full index
reports.py     write JSON index and CSV payload files
publisher.py   CLI orchestration entry point
```

Keep code local to BRB at first unless a helper is clearly shared by another
feature.  Promote helpers later when the reuse is real.

## Implementation Slices

1. Build the date index from `History` and write `basho_results_index.json`.
2. Write one payload CSV for a selected historical basho with identity and
   score columns.
3. Extend to all represented basho.
4. Add previous-basho context by reusing Banzuke Change Report logic.
5. Add fixed_v2 rating lookup and rating columns.
6. Add actual next-banzuke `νChii` where the next banzuke is known.
7. Add generated-output validation against the `IndexedTablePA` source-field
   and sort-key contract.

## Renderer Implications

The renderer should:

1. load `data/basho_results_index.json`;
2. use the selected `basho_date` option to find an index entry;
3. fetch `entry.payload_path`;
4. filter rows by `division_id`;
5. render table columns/groups according to the BRB `IndexedTablePA`;
6. use `entry.status`, `entry.latest_day`, and `generated_at` for headings,
   notes, and freshness display.

The renderer should not infer live publication state from the visitor's current
date/time.  It should render the state represented by the static files.
