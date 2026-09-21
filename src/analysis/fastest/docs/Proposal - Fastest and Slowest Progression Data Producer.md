# Proposal: Fastest and Slowest Progression Data Producer

## Status

Proposed. This document specifies a model-independent historical data producer
under `src/analysis/fastest/`. It deliberately does not specify a website,
page, controls, prose, or `make_site89` integration.

The purpose of this stage is to freeze what can be calculated from the
banzuke, based on the preceding investigation of promotion paths and career
entry divisions. A separate design exercise can later test whether this output
is sufficient for the desired public artifact.

## Questions the data should answer

The primary question is:

> Among rikishi whose first career banzuke appearance was in rank group *d*,
> who reached higher rank group *d'* in the fewest basho?

The same data must answer the corresponding slowest-progression question and
support cohort context such as:

- how many rikishi began in each division;
- what share of all observed starters that cohort represents;
- how many and what percentage later reached each higher group;
- the exact starting and finishing ranks and basho; and
- which rikishi never reached a selected group.

This is a career-entry cohort analysis. It is not a search for the quickest
passage between any two divisions during a career.

## Historical scope

The command line declares an epoch and selects the annotated banzuke History
from that represented banzuke onward. The epoch banzuke is a left boundary:
rikishi already present on it may have begun their careers earlier. It is used
to identify and exclude those boundary incumbents.

For the `make_site89` proof of concept, the CLI default is `1989/01`. The first
eligible career starts are therefore on the `1989/03` banzuke.

The declared analytical range is:

```text
eligible career starts: 1989/03 through the latest represented banzuke
supporting boundary:    1989/01 (CLI default epoch)
```

The analysis itself has no rating dependency. A natural finished historical
artifact would use the banzuke epoch `1958/01`, admitting starters from
`1958/03`. The proof of concept deliberately accepts the narrower `1989/01`
scope so that it can join the current consistently post-1988 `make_site89`
artifact set without first redesigning site production. This is a temporary
publication constraint, not an analytical claim about promotion history.

The core analysis should accept a `History` object. The command-line wrapper
should expose `--epoch`, defaulting to `1989/01`, and use the live store when
available or an explicitly supplied annotated History zip otherwise, following
the established analysis-package pattern. The requested epoch must exist in
the source History. The producer manifest must record the actual source,
epoch, and selected range.

The producer also depends on parsed rikishi bio data and the established
`FullShikonaStore` label policy. A rikishi represented in History but missing
from the bio data cannot receive a publication shikona and is excluded under
the explicit missing-bio contract below.

## Rank groups

Use the following ordered groups:

| Key | Meaning |
|---|---|
| `Jk` | Jonokuchi |
| `Jd` | Jonidan |
| `Sd` | Sandanme |
| `Ms` | Makushita |
| `J` | Juryo |
| `M` | Maegashira only |
| `KS` | Komusubi or Sekiwake |
| `O` | Ozeki |
| `Y` | Yokozuna |

`M`, `KS`, `O`, and `Y` deliberately split the top division. Reaching `M`
means appearing at a Maegashira rank; it does not mean merely entering
Makuuchi at any rank. `KS` is one combined milestone, reached on the first
appearance at either Komusubi or Sekiwake.

The observed starting cohorts are expected to be concentrated in `Jk`, with
small `Jd`, `Sd`, and `Ms` cohorts. The producer must derive the available
starting cohorts from the data rather than assume that every group has
starters.

Rank annotations such as `TD`, `OB`, `HD`, and `YO` do not change group
membership. They must remain present in the retained full chii.

## Level-zero milestone matrix

The first and lowest-level output is one wide CSV row for every rikishi in the
selected History for whom bio data is available, including epoch-boundary
incumbents. Its columns are:

```text
shikona
rik_id
Jk_chii, Jk_chii_ordinal, Jk_date, Jk_basho_ordinal
Jd_chii, Jd_chii_ordinal, Jd_date, Jd_basho_ordinal
Sd_chii, Sd_chii_ordinal, Sd_date, Sd_basho_ordinal
Ms_chii, Ms_chii_ordinal, Ms_date, Ms_basho_ordinal
J_chii,  J_chii_ordinal,  J_date,  J_basho_ordinal
M_chii,  M_chii_ordinal,  M_date,  M_basho_ordinal
KS_chii, KS_chii_ordinal, KS_date, KS_basho_ordinal
O_chii,  O_chii_ordinal,  O_date,  O_basho_ordinal
Y_chii,  Y_chii_ordinal,  Y_date,  Y_basho_ordinal
```

There are nine rank-group quartets and thirty-eight columns in total. Each
quartet records the exact chii, `Chii.ordinal()`, human-readable banzuke date,
and one-based ordinal of that date in the sorted represented History. All four
fields are empty if the
rikishi never appeared in the group.

Every chii written to CSV must be followed immediately by its ordinal. Chii
display strings are not lexically sortable in banzuke order; spreadsheet users
must sort on the adjacent ordinal column.

`KS_chii` retains the actual first Komusubi or Sekiwake rank. All annotations
remain in the chii string. Dates use `YYYY/MM`.

`basho_ordinal` is the calculation key. The selected epoch banzuke is ordinal
1 and every next represented banzuke is `n + 1`, irrespective of calendar gaps
caused by a cancelled tournament. Elapsed basho is therefore the difference
between finishing and starting basho ordinals.

`rik_id` is the identity key. `shikona` is the catalogue-wide public label from
`FullShikonaStore`, not an identity substitute.

Keeping all represented rikishi makes this matrix a direct audit of History.
The derived cohort analysis excludes any row whose earliest milestone is dated
at the epoch. With the default epoch, eligible career starts therefore begin at
`1989/03`.

The columns are in rank order, not necessarily career chronology. For example,
a Makushita starter who is later demoted to Sandanme will have an `Ms_date`
earlier than the `Sd_date`. The starting group is the group with the earliest
non-empty date, not simply the leftmost populated group.

## Missing-bio contract

Missing bio data is an expected recoverable input defect, not a reason to fail
the complete run. For each `RikId` represented in History but absent from the
parsed bio data, the producer must:

1. exclude the rikishi from the milestone matrix and every derived cohort;
2. record one row in `missing_bios.csv`, using the rikishi's first represented
   banzuke occurrence;
3. record the exclusion count and audit-file path in `manifest.json`; and
4. print one warning to the console.

The audit columns are:

```text
rik_id
shikona
chii
chii_ordinal
date
basho_ordinal
reason
```

The warning should contain at least `rik_id`, the History shikona, exact chii,
chii ordinal, and date. All values must come from exceptions discovered in the
current run; no rikishi exception is hard-coded.

```text
WARNING: missing bio; excluded rik_id=<id> shikona=<shikona> chii=<chii> chii_ordinal=<ordinal> date=<date> basho_ordinal=<ordinal>
```

Warn and audit once per rikishi rather than once per represented basho. The
History shikona in this record is diagnostic fallback text; it does not replace
the missing publication label.

## Cohort contract

For each stable `RikId`:

1. Find the earliest represented banzuke containing that rikishi.
2. If it is the declared epoch, classify the rikishi as a boundary incumbent
   and exclude him from every starter cohort.
3. Otherwise, classify the first chii into exactly one starting group.
4. Retain the exact starting basho, chii, and shikona.
5. For every higher group, find the first subsequent banzuke appearance in
   that exact group.
6. Retain explicit non-achievement when the rikishi never reaches that group.

The starting group is determined solely by the first career banzuke
appearance. A tsukedashi or other exceptional entrant belongs to the observed
higher starting cohort, not to a hypothetical Jonokuchi cohort.

This definition permits like-for-like comparisons. For example, a Makushita
starter cannot enter a Jonokuchi-start progression table merely because he
reached the same finishing group quickly.

## Elapsed-basho contract

Index the represented banzuke in chronological order. For each achieved
milestone:

```text
elapsed_basho = finishing_banzuke_index - starting_banzuke_index
```

Therefore:

- reaching a group on the immediately following banzuke takes one basho;
- the starting banzuke is not counted as elapsed time;
- the finishing basho is the first appearance in the exact destination group;
- absences and banzuke-gai intervals still count as elapsed scheduled basho;
  and
- elapsed basho is not the same as basho fought or bouts contested.

Only upward start/finish pairs are part of this analysis. Same-group and
downward movements are outside the contract.

## Career and milestone data

Produce one career record for every eligible starter. It should contain at
least:

```text
rikishi_id
start_group
start_basho
start_basho_ordinal
start_chii
start_chii_ordinal
start_shikona
last_observed_basho
active_at_history_end
milestones
```

For each higher group, `milestones` must record either:

```text
reached = true
finish_group
finish_basho
finish_basho_ordinal
finish_chii
finish_chii_ordinal
finish_shikona
elapsed_basho
```

or:

```text
reached = false
finish_group
```

Retaining non-achievement explicitly makes the cohort denominators auditable.
Retaining activity at the end of History allows a later consumer to identify
right-censored careers without changing the primary calculation.

## Cohort and route summaries

For every starting group, produce:

- `starter_count`;
- `starter_share` of all eligible observed starters;
- earliest and latest starting basho; and
- active and inactive counts at the end of History.

For every valid starting/finishing pair, produce:

- `starter_count`;
- `reached_count`;
- `not_reached_count`;
- `reached_share`;
- reached-active and reached-inactive counts;
- not-reached-active and not-reached-inactive counts;
- minimum and maximum elapsed basho; and
- the complete set of qualifying rikishi-route records.

The slowest population is still the set of rikishi who reached the destination.
Non-achievers are not assigned infinite elapsed time.

These are structured facts. Any explanatory prose derived from them belongs to
the later artifact design, not to this producer specification.

## Route records and ordering

Each achieved start/finish route should expose a flat audit record containing:

```text
rikishi_id
shikona
active
fastest_position
slowest_position
elapsed_basho
start_chii
start_chii_ordinal
start_date
start_basho_ordinal
finish_chii
finish_chii_ordinal
finish_date
finish_basho_ordinal
```

The enclosing route supplies `start_group` and `finish_group`.

`active` is true exactly when the rikishi is present on the latest represented
banzuke. It is publication metadata, so it belongs in `rankings.json` rather
than changing the locked-down thirty-eight-column milestone matrix. It permits
a consumer to hide retired rikishi from an already selected historical ranking
range without constructing or renumbering an active-only ranking.

Define deterministic fastest ordering as:

```text
elapsed_basho ascending, finish_basho_ordinal ascending, rikishi_id ascending
```

Define deterministic slowest ordering as:

```text
elapsed_basho descending, finish_basho_ordinal ascending, rikishi_id ascending
```

The producer assigns consecutive positions from 1 through the complete route
population. Equal `elapsed_basho` values do not share a position; the declared
secondary keys give them a deterministic order. Each route record retains both
`fastest_position` and `slowest_position`, allowing a consumer to select any
requested number of rows without rerunning the analysis.

## Proposed outputs

Write a self-contained run beneath a path such as:

```text
files/output/analysis/fastest/<run-id>/
```

Recommended files:

| File | Purpose |
|---|---|
| `first_rank_group_appearances.csv` | Level-zero thirty-eight-column milestone matrix containing every represented rikishi with available bio data |
| `rankings.json` | Complete qualifying route records with consecutive fastest and slowest positions for every valid starting/finishing pair |
| `careers.json` | One structured record per eligible career starter, including all higher-group milestones |
| `routes.csv` | Flat audit table with one row per achieved start/finish route |
| `route_summary.csv` | Cohort and achievement counts for every valid pair |
| `cohort_summary.csv` | Counts and shares for starting cohorts |
| `missing_bios.csv` | One audit row per represented rikishi excluded because parsed bio data is absent |
| `manifest.json` | Source provenance, schema versions, date range, contracts, exclusions, counts, and output inventory |

A publication-oriented JSON derived from these files may be added after the
artifact requirements are designed. It should not be guessed at in this phase.

## Package design

A likely package boundary is:

```text
src/analysis/fastest/
    __init__.py
    __main__.py
    model.py
    analysis.py
    output.py
    producer.py
    docs/
```

Responsibilities:

- `model.py`: immutable analytical and output-schema dataclasses;
- `analysis.py`: pure History-to-cohort and milestone calculations;
- `output.py`: JSON, CSV, and manifest writing;
- `producer.py`: orchestration and declared output paths; and
- `__main__.py`: live-store/zip source selection and command-line arguments.

The package must have no dependency on `make_site89` or a browser runtime.

## Validation and tests

Unit tests should use small synthetic Histories covering:

1. epoch-boundary incumbents being excluded;
2. the first represented post-epoch banzuke being the first eligible starting
   banzuke;
3. correct classification of every rank group;
4. annotations not changing group membership;
5. a consecutive-banzuke promotion producing `elapsed_basho = 1`;
6. represented banzuke during a disappearance counting as elapsed time;
7. first arrival in the exact finishing group being selected;
8. a non-achiever remaining in the cohort denominator;
9. distinct treatment of Maegashira, Komusubi/Sekiwake, Ozeki, and Yokozuna;
10. deterministic fastest and slowest ordering;
11. consecutive positions for equal elapsed-basho values;
12. active-at-end classification; and
13. a missing-bio rikishi being warned about once and excluded everywhere;
14. `missing_bios.csv` placing `chii_ordinal` immediately after `chii`; and
15. reconciliation of career, route, summary, exclusion, and manifest totals.

A selected-history audit should independently reproduce the starting-division
counts and manually inspect the small Jd-, Sd-, and Ms-starting cohorts.

## Acceptance criteria

The producer is complete when:

- it requires the declared epoch to be represented, defaults that boundary to
  `1989/01`, and admits starters from the next represented banzuke onward;
- every eligible rikishi belongs to exactly one starting cohort;
- no boundary incumbent enters a cohort or route;
- every represented rikishi missing bio data is excluded, warned about once,
  and retained in the missing-bio audit;
- every higher-group milestone is represented as reached or not reached;
- every achieved route has reproducible chii, dates, and elapsed basho;
- cohort and route summaries reconcile with the career records;
- complete fastest and slowest positions are deterministic and untruncated;
- every ranking record states whether the rikishi appears on the latest
  represented banzuke;
- all output is derived from the epoch-selected suffix of available banzuke
  History; and
- the outputs make no assumption about a future UI or site assembler.

## Deferred analysis

The first version will not normalize for exact starting rank within a division.
A rikishi starting at `Ms5` and one starting at `Ms60` belong to the same
Makushita-start cohort, although the exact starting chii remains available.

Also deferred:

- comparisons pooling different starting divisions;
- time measured by basho fought or bouts contested;
- era-normalized progression speed;
- special analytical treatment of tsukedashi entrants;
- same-group or downward movement; and
- judgments about how incomplete careers should be presented.
