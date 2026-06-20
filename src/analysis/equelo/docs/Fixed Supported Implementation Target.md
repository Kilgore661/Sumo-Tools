# Fixed Supported Implementation Target

## Status

Implementation standard.

This document says what the production code shall look like. It is not a tour
of the current experiment. Existing code should be refactored until it conforms
to this target.

## Production Boundary

The production package shall be named `fixed_supported`.

Code outside the package shall not import from
`src.analysis.equelo.experiments.support_domain_fp` to produce public Equelo
artifacts.

Experiment modules may remain as research history, but they shall not be the
production API.

## Entry Points

The package shall deliver two entry points:

1. a maintainer-facing generation entry point;
2. a consumer-facing artifact access API.

The distinction is essential. The access API must not run the solver as a side
effect.

## Generation Entry Point

The generation entry point deliberately refreshes the canonical production data.

It may be slow. It is allowed to:

- run the supported fixed-point solver;
- complete the master chii initial-rating map;
- write the master map and metadata;
- build process/day-end ratings from the master map;
- write production process-rating artifacts;
- build public landmark artifacts when requested or as a documented part of the
  refresh.

This entry point is for maintainers. It should be invoked explicitly, for
example as a command under `src.analysis.equelo.fixed_supported`.

`make_site2` shall not trigger this work merely by reading data for a site
build.

## Artifact Access API

The access API shall be cheap and side-effect free.

It shall expose canonical paths and loaders for already-generated artifacts.
Conceptually, it should provide:

```text
master_chii_initial_rating_map_path()
load_master_chii_initial_rating_map()
day_end_ratings_path()
load_day_end_ratings()
metadata_path()
load_metadata()
typical_equelo_values_path()
```

The access API may validate that required files exist. It shall not generate
them.

The API should use design names rather than investigation names. In particular,
it should refer to:

- master chii initial-rating map;
- supported chii;
- completed chii;
- direct source;
- nearest-supported source;
- support collapse policy;
- support threshold;
- completion policy;
- base convention.

## Internal Shape

The package should be organised around the two entry points rather than around
the investigation history.

A reasonable module sketch is:

```text
api.py          canonical paths and artifact loaders
model.py        model names, output roots, policy defaults
master_map.py   row types, map loader/writer, completion helpers
build.py        process/day-end rating build from an existing master map
refresh.py      explicit solver-plus-post-processing generation workflow
landmarks.py    public landmark generation from production sources
```

This sketch is guidance, not a requirement to create exactly these files. The
important rule is that consumer code imports the access API, not the refresh
workflow.

## Policy Configuration

The following shall be explicit policy values, not hidden constants inside
ad-hoc scripts:

- support collapse policy;
- support measure;
- support threshold, currently `collapsed_appearance_count >= 60`;
- completion policy, currently nearest supported chii by ordinal;
- tie-break rule, currently stronger/lower ordinal;
- additive base convention;
- solver parameters.

Policy values may have defaults, but production outputs must record the values
that were used.

## Artifacts

The master chii initial-rating map shall be a first-class artifact.

The artifact shall make clear that it is keyed by chii, not rikishi. Its rows
shall identify whether each value was directly estimated or completed, and
shall identify the supported source chii for completed values.

Process/day-end ratings shall be separate artifacts. They are ratings of
rikishi over time, downstream of the master map.

Public landmark artifacts shall be generated from a documented production
source and shall not depend on experiment output paths.

## Metadata

Generated artifacts shall include metadata sufficient to answer:

- which history/data world was used;
- which support collapse policy was used;
- which support rule and threshold were used;
- which completion rule and tie-break were used;
- which solver parameters were used;
- which base convention was used;
- which master map produced the process ratings;
- when the artifacts were generated.

Metadata should be useful to future maintainers without requiring them to infer
meaning from file paths.

## Downstream Consumption

`make_site2` and data producers shall consume production APIs or canonical
production artifacts.

They shall not point at feasibility-study run folders, latest-sweep folders, or
temporary experimental outputs.

Temporary plumbing may exist only during the migration and must be removed
before the final production switch is accepted.

## Legacy Code

Legacy `fixed_v2` code may remain only until the archive/deletion pass is
complete. It is not a production fallback.

Once `fixed_supported` is production and regression-tested, legacy v2 code and
the development/test scaffolding used to derive it should be moved to a clear
archive location or deleted. It should not remain the conceptual owner of the
new model.

## File Size And Shape

Production modules should be small enough to understand in one sitting.

If a module mixes policy, IO, solver orchestration, artifact writing, and
regression reporting, it should be split. Prefer modules with one clear reason
to change over large scripts that remember the investigation history.
