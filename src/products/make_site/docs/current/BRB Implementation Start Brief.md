# BRB Implementation Start Brief

## Status

Historical first-start brief.  Parts of this document have been overtaken by
the current implementation.  Use `Basho Results Browser Design Notes.md`, the
current producer code under `src/analysis/sumo_history/basho_results/`, and the
current `make_site` PA runtime as the live sources before relying on this
handoff note.

## Purpose

This is the handoff note for starting implementation of the Basho Results
Browser (BRB).

Use this when opening a fresh development conversation.  The longer source
document is:

```text
src/products/make_site/docs/current/Basho Results Browser Design Notes.md
```

The analysis/producer-side documentation home is:

```text
src/analysis/sumo_history/basho_results/docs/
```

That document remains the design source of truth.  This brief says how to start
without treating every unresolved design question as a blocker.

## Implementation Instruction

Implement BRB according to `Basho Results Browser Design Notes.md`.

Before writing code, inspect the current repository state because the repo may
have moved since these notes were written.  Prefer existing make_site, PA
manifest, table-rendering, and fixed_v2 access patterns over inventing a new
architecture.

Where the design notes leave a choice open, choose conservatively and document
the choice.  Do not stop implementation merely because defaults or polish-level
decisions are still open.

## First Implementation Scope

The first BRB implementation should be historical completed-basho mode.

In scope:

* a selectable completed basho date;
* valid-basho date index, skipping missing basho such as `2022/03` and
  `2011/05`;
* one row per rikishi in the selected division/basho;
* final score in wins-losses or wins-losses-absences form;
* fixed_v2 start/end Equelo values where available;
* enough metadata/config for the make_site page to render the first table.

Out of scope for the first pass:

* live/current-basho semantics;
* projected next-banzuke values;
* perfect final defaults for every option;
* all optional explanatory columns if their data path is not yet ready.

The first version may start with a smaller useful column set, provided the code
is shaped so the remaining planned columns can be added without a rewrite.

## First Deliverable

The first useful deliverable is a producer that can build BRB data/config for a
single selected historical basho.

After that works, extend it to all represented basho if the payload size and
runtime are acceptable.  If the all-basho payload is large, choose an explicit
static-data strategy such as one file per basho, grouped files by year, or an
index plus lazy-loaded per-basho files.

## Rating Source

Use fixed_v2.

Row-level rikishi ratings must come from fixed_v2 process-rating artefacts, not
from `Typical Equelo Ratings`.

Use:

```text
files/output/Equelo/fixed_v2/day_end_ratings.json
files/output/Equelo/fixed_v2/entrant_initial_ratings.json
```

The intended lookup policy is:

* `end_rating(date, rikishi_id)` is the selected basho's final day-end rating;
* `start_rating(date, rikishi_id, chii)` is the previous represented rating for
  that rikishi, usually the previous basho's final day-end rating;
* if the rikishi has no previous rating, use the fixed_v2 entrant initial
  rating for the selected basho chii;
* for the earliest represented basho, start ratings come from entrant initial
  ratings.

`Typical Equelo Ratings` are public landmarks for reading the scale.  They must
not be used as lookup values for individual rikishi ratings, `DeltaBZ`,
`nuChii`, or `DeltaChii`.

fixed_v1/Brier-compressed ratings are historical diagnostic context only.

## Likely Code Location

Prefer a new feature module under:

```text
src/analysis/sumo_history/basho_results/
```

Feature-specific producer notes should live under:

```text
src/analysis/sumo_history/basho_results/docs/
```

Likely responsibilities:

* date index construction;
* completed-basho row construction;
* fixed_v2 rating lookup helpers;
* record/score formatting;
* banzuke slot ordering helpers;
* BRB row/config dataclasses;
* CSV/JSON writing for make_site;
* CLI/build entry point.

If existing modules already provide part of this, reuse them rather than
duplicating logic.  Banzuke Changes and Standings by Wins are likely comparison
points, but BRB should be its own feature module.

## make_site Integration Target

Add BRB under:

```text
Sumo History
  Basho Results
```

It should become item `7.1`, with later Sumo History items renumbered as
needed.

The public-site integration should follow the current PA manifest/direct
rendering direction.  Avoid iframe/static-HTML integration for BRB.

The BRB page should use the standard tool layout:

```text
options panel | table/content panel
```

The options and table behaviour are specified in the design notes.  The first
implementation should preserve enough manifest/config structure for later deep
links, sortable columns, column-group toggles, and the Reading Guide option.

## Open Decisions That Should Not Block First Code

These remain open, but can be handled incrementally:

* exact initial defaults for division, visible columns, and sort;
* whether all planned columns ship in v1;
* final wording of long notes and Reading Guide;
* hidden active-sort fallback policy;
* exact static-data packing strategy for all basho;
* whether to promote rating lookup helpers from BRB-local code into a shared
  fixed_v2 consumer API.

If a choice is needed to make progress, choose the smallest reversible option
and record it in the relevant doc or code comment.

## Suggested First Engineering Steps

1. Read `Basho Results Browser Design Notes.md`.
2. Inspect the current make_site PA manifest/runtime code and active page
   instances.
3. Inspect fixed_v2 API/output shape.
4. Inspect Banzuke Changes and Standings by Wins for reusable table, score,
   link, division, and sorting conventions.
5. Build a BRB producer for one historical basho.
6. Add make_site integration for the generated BRB manifest/data.
7. Extend to the full date index and all represented basho.
