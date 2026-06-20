# Basho Results Browser Analysis Docs

This folder is the analysis/producer-side documentation home for the Basho
Results Browser (BRB).

The BRB public-page design currently lives in make_site docs:

```text
src/products/make_site/docs/current/Basho Results Browser Design Notes.md
src/products/make_site/docs/current/BRB Implementation Start Brief.md
```

Those documents describe the public page: placement, options, table behaviour,
notes, reading guide, PA manifest/direct-rendering integration, and open UI
questions.

This folder should describe the analysis feature: how BRB data is assembled,
what inputs it consumes, what outputs it writes for make_site, and which
producer-side choices were made during implementation.

## Current Producer Contract

BRB should be implemented as its own feature module under:

```text
src/analysis/sumo_history/basho_results/
```

The first producer should target historical completed-basho mode and emit enough
data/config for make_site to render a selectable basho results table.

The implementation should use fixed-supported process ratings through the
public Equelo API:

```text
src.analysis.equelo.api.EqueloLookup
files/output/Equelo/fixed_supported/day_end_ratings.json
files/output/Equelo/fixed_supported/master_chii_initial_rating_map.csv
```

`Typical Equelo Ratings` are public landmarks only.  They must not be used as
row-level lookup values for individual rikishi ratings or derived BRB columns.

## Expected Code Responsibilities

Likely producer responsibilities include:

* valid-basho date index construction;
* selected-basho membership and score extraction;
* fixed-supported start/end rating lookup;
* record formatting;
* division and banzuke slot ordering helpers;
* BRB row/config/output dataclasses;
* CSV/JSON output for make_site;
* a CLI/build entry point.

## Documentation Split

Use the make_site docs for public-page decisions.

Use this folder for implementation notes about:

* data source shape;
* producer outputs;
* rating lookup policy details;
* validation findings;
* payload-size decisions;
* reusable helpers promoted out of BRB-local code.
