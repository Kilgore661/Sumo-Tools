# make_site89

`make_site89` is the current static publication system for the Sumo-Tools
post-1988 site. It validates and presents a coherent bundle of site-facing data
produced from the History beginning at `1989/01` and the Elo-89 rating model.

## Why this package exists

The preceding `make_site2` system belongs to the earlier 1958+/Equelo phase of
the project. It combined presentation with a mixture of analysis invocation,
copied outputs and independently selected data sources.

`make_site89` accompanied the decision to adopt Elo-89 as the operational
rating model and January 1989 as the single production History boundary. That
boundary applies to model-independent site artifacts as well as rating
artifacts: production coherence is preferred to silently giving each page a
different historical scope.

The migration also established a clearer architectural boundary:

```text
selected 1989+ History and other declared inputs
                         |
                         v
analysis and site-facing producers
                         |
                         v
validated site-data bundle
                         |
                         v
make_site89
  - validate
  - copy
  - assemble
  - render
                         |
                         v
static HTTP-served site
```

Production orchestration may run analyses. `make_site89` itself does not load
History, calculate ratings or derive analytical results.

## Relationship to make_site2

The presentation code began as a private fork of the parts of `make_site2`
needed during migration. Deliberate duplication allowed the new production
contract to develop without changing the existing site at the same time.
`make_site89` does not import `make_site2`.

`make_site2` is now legacy. It remains useful as a historical implementation,
behavioral reference and record of the full-history/Equelo publication era,
but it is not the production target for new site work.

The 1989 boundary is pragmatic, not a claim that pre-1989 records are useless.
Earlier banzuke and result data remain available for research. Incorporating
different epochs into the public site would require an explicit multi-scope
production design rather than an individual artifact silently bypassing the
site's selected History.

## Production components

- `src.analysis.site89` orchestrates the Elo-89 replay and site-facing
  producers and writes `files/output/analysis/site89_bundle`.
- `src.products.make_site89.bundle` validates that produced bundle and its
  declared files.
- this package assembles the static tree under
  `files/output/make_site89` and optionally deploys it to configured targets.
- browser code renders only the structured data supplied in the bundle.

## Commands

The normal live-store-first build is:

```powershell
.\_boot89.ps1
```

Build the bundle and static tree without deployment:

```powershell
.\_boot89.ps1 --build-only
```

Assemble an already-produced bundle without rerunning production:

```powershell
python -m src.products.make_site89 --build-only
```

Deploy an existing static tree without rebuilding it:

```powershell
.\_boot89.ps1 --no-build
```

The generated site must be viewed through HTTP. Opening `index.html` through
`file://` prevents its fetch-based JSON and CSV pages from loading.

## Documentation

The principal records are:

- [Implementation Plan](docs/Implementation%20Plan.md) — the migration,
  production contract, bundle boundary and relationship to make_site2;
- [Production Documentation Strategy](docs/Production%20Documentation%20Strategy.md)
  — the public story, interpretation and proportional explanation of the 1989
  boundary; and
- [Site Build Data Integrity and History Consistency](docs/2026-10-30%20Site%20Build%20Data%20Integrity%20and%20History%20Consistency.md)
  — source freshness, snapshot coherence and build safety.

The implementation plan was written during migration and retains some
historical wording about make_site2 being the then-current site. This README
records the subsequent status: make_site89 is now current and make_site2 is
legacy.
