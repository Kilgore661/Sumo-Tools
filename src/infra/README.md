# Infrastructure

> **Retrospective documentation (November 2026).** This README was written
> after the infrastructure had been implemented. It describes the behaviour
> reconstructed from the current code, tests and generated artifacts; it is
> not the original requirements document.

`src.infra` acquires SumoDB source pages, parses them into the project's
`History` domain model, persists canonical History snapshots, and publishes a
live snapshot for analysis and product code. It also owns the smaller source
pipelines for rikishi biographies, a newly published banzuke, and prospective
torikumi.

The main historical-data path is:

```text
tracker planner
  -> SumoDB banzuke and daily-results HTML
  -> parser
  -> complete History
  -> annotated History zip
  -> live shared-memory store
  -> analysis and product consumers
```

Raw downloads, generated snapshots, caches, logs and diagnostics are written
beneath `files/output`; they are not source-controlled project inputs.

## Package map

| Path | Responsibility |
| --- | --- |
| `tracker` | Plans the source pages expected at a given time, downloads missing pages, rebuilds History after a source change, writes canonical snapshots and republishes the live store. |
| `tracker/scraper` | Retrieves SumoDB banzuke and daily-results HTML into the raw source cache. It performs bounded structural checks, not full semantic interpretation. |
| `parser` | Parses cached banzuke and daily-results pages into `BashoState` and `History`, including rank annotations, results, prizes and parser diagnostics. |
| `persistence` | Serialises and loads annotated History zip artifacts. |
| `live_store` | Publishes History in shared memory and provides the normal consumer API, `get_history()`. |
| `get_bios` | Downloads and parses rikishi profile pages and exposes typed biography data. |
| `new_banzuke` | Parses the newest downloaded `Banzuke.aspx` page into a typed artifact before that basho necessarily exists in History. |
| `torikumi` | Selects the active or immediate upcoming basho, acquires published schedules into a separate cache, and persists a `Future` snapshot. It does not calculate ratings or site tables. |
| `history_artifacts.py` | Shared conventions for selecting synchronized History intervals, including the post-1988 publication slice. |
| `bootstrap_sources.py` | One-shot raw-source bootstrap for a clean workspace; it does not parse History or start the live store. |

The domain types themselves live in `src/sumo_core`. Analyses live in
`src/analysis`, and website assembly lives in `src/products`. Infrastructure
should supply typed source data to those layers rather than contain analytical
or presentation policy.

## Primary artifacts and caches

The important local paths are:

| Path | Meaning |
| --- | --- |
| `files/output/current standings/YYYY MM.html` | Downloaded banzuke/current-standings source pages. |
| `files/output/HTML results/YYYY MM/DD.html` | Downloaded daily-results source pages. |
| `files/output/Historys/*.zip` | Canonical annotated History snapshots. |
| `files/output/store_name.txt` | Selector naming the live shared-memory store; it is state for a cache, not a primary data source. |
| `files/output/infra/get_bios/rikishi/*.html` | Downloaded rikishi biography pages. |
| `files/output/infra/get_bios/rikishi_bios.json` | Parsed biography data consumed through `get_bios.api`. |
| `files/output/infra/new_banzuke/new_banzuke.json` | Latest typed banzuke artifact outside canonical History. |
| `files/output/torikumi/future.json` | Current prospective torikumi snapshot. |
| `files/output/torikumi/raw/` | Separate raw cache for torikumi lifecycle snapshots. |

A cache is not a primary dependency. In particular, the live store is a fast
access layer over a History that can also be persisted and loaded explicitly.
Consumers that need a reproducible offline input should accept an explicit
History zip rather than silently falling back from one source to another.

## Normal operation

Start the long-running tracker from the repository root:

```powershell
py -m src.infra.tracker.tracker
```

The tracker owns the live store for its lifetime. On a changed source corpus,
one update cycle downloads the requested pages, rebuilds the complete History,
writes the full and synchronized post-1988 History zips where applicable, and
publishes the rebuilt History to the already-owned live store.

Run one immediate tracker cycle for repair or catch-up work:

```powershell
py -m src.infra.tracker.tracker --now
```

Bootstrap only the raw source cache:

```powershell
py -m src.infra.bootstrap_sources
```

Produce the current auxiliary artifacts used by the Sumo '89 publication
workflow:

```powershell
py -m src.infra.new_banzuke
py -m src.infra.torikumi
```

The Torikumi command uses the live History by default and accepts
`--history-zip PATH` for an intentional fixed snapshot. It retains a coherent
same-basho snapshot after a refresh failure rather than replacing it with
partial data.

Applications should obtain the published History through the consumer API:

```python
from src.infra.live_store.api import get_history

history = get_history()
```

`get_history()` fails explicitly when no published store is available. Product
and analysis code should not create or repair the live store on a consumer
path.

## Correctness and freshness boundaries

The project can validate a page against the checks known when it is acquired,
but it does not guarantee that a cached historical page still matches SumoDB.
SumoDB may correct pages after download, and historical pages are not routinely
re-fetched merely to detect revisions. Public products must preserve the
project's corresponding source-freshness caveat.

The tracker rebuilds History as one complete object rather than exposing a
partially updated model. A consumer receives a stable History snapshot, but
the current live-store API does not identify its generation or notify a
long-running consumer that a newer generation has been published.

Auxiliary artifacts have their own lifecycle:

- `NewBanzuke` represents the latest downloaded banzuke publication, which may
  be newer than canonical History.
- `Future` represents positively recognized published torikumi for the active
  or immediate upcoming basho. Unpublished days are normal, not errors.
- biography data is independently downloaded and parsed; it is not embedded
  in History.

## Documentation

Start with these current contracts and operational notes:

- [`docs/Source Data Freshness and Upstream Revisions.md`](docs/Source%20Data%20Freshness%20and%20Upstream%20Revisions.md)
- [`docs/Live Store Operational Notes.md`](docs/Live%20Store%20Operational%20Notes.md)
- [`torikumi/docs/Lifecycle Repair Proposal.md`](torikumi/docs/Lifecycle%20Repair%20Proposal.md)
- [`get_bios/docs/_README.md`](get_bios/docs/_README.md)

The dated documents under `docs`, `parser/docs`, `persistence/docs` and
`tracker/docs` preserve design and migration history. They remain useful
evidence, but may describe earlier implementations. Prefer current code and
the explicit project-level freshness contract when they disagree.

## Focused tests

Infrastructure coverage is distributed across component and product tests.
Useful starting points include:

```powershell
.\.venv\Scripts\python.exe -m pytest -s `
  tests\test_tracker_downloader.py `
  tests\test_tracker_update_cycle.py `
  tests\test_parser2_history_artifacts.py `
  tests\test_torikumi_infra.py `
  tests\test_torikumi_lifecycle.py
```

When changing a persisted artifact or public-data dependency, also run the
focused analysis or product tests which consume that boundary.
