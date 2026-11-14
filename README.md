# Sumo-Tools

Sumo-Tools is a Python project for building tools and static public exhibits
from professional sumo data.

At a high level, the project pipeline is:

```text
historical sumo data
  -> domain models and analysis
  -> published artifacts
  -> assembled static website
```

The web layer is a publication renderer. It should present precomputed
analytical outputs consistently; it should not become the computational core.

If you are working with Codex or another LLM, read
`docs/LLM Guide.md` before making changes. It records the collaboration style,
environment quirks, test commands and local build/preview conventions for this
workspace.

## Current Workspace

The active workspace is:

```text
X:\Sumo-Tools
```

Avoid old `G:` references. The local/LAN deploy target may be mapped on `A:`,
but Codex normally cannot access mapped network drives.

## Main Areas

| Path                      | Role                                                          |
| ------------------------- | ------------------------------------------------------------- |
| `src/sumo_core`           | Core domain model.                                            |
| `src/infra`               | Scraping, parsing, persistence, tracker and live store.       |
| `src/analysis`            | Derived views, public tools, experiments and reports.         |
| `src/products/make_site89` | Current post-1988/Elo-89 static publication system.          |
| `src/products/make_site2` | Legacy 1958+/Equelo publication system and reference.         |
| `docs`                    | Project-level orientation and working conventions.            |
| `files/output`            | Local generated data and build artifacts; not tracked by git. |

## Data Sources

Most analysis and production paths use a `History` object. The current public
site deliberately selects the represented History from January 1989 onward;
full-history analyses remain separate research unless explicitly incorporated
into that production contract.

> **Important data-model caveat:** the parsed banzuke intentionally excludes
> mae-zumo (`Mz`), although `Mz` rikishi and bouts can still appear in source
> pages. Consequently, absence from the parsed banzuke does not always mean
> absence from basho activity. See
> [`docs/Mae-zumo (Mz) Data Semantics and Audit.md`](docs/Mae-zumo%20(Mz)%20Data%20Semantics%20and%20Audit.md).

The normal live-store-first site build is:

```powershell
.\_boot89.ps1 --build-only
```

`src.analysis.site89` produces the coherent site-data bundle; make_site89 then
validates and presents it. See
[`src/products/make_site89/README.md`](src/products/make_site89/README.md) for
the production boundary and other build modes.

History zips live under `files/output/Historys` on this machine, but
`files/output` is ignored by git. A fresh clone will not contain those zips.

## Running Tests

Use the repo-local virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -s <test paths>
```

The `-s` flag avoids a known pytest capture teardown issue in this environment.
The user-site pytest installation may be visible to an interactive shell but
not to Codex, so prefer the repo-local `.venv` command.

Tests live under the repository-root `tests` directory. Discover them locally
rather than relying on GitHub connector search:

```powershell
git ls-files "tests/*"
git ls-files "tests/test_make_site89*"
```

For make_site89 work, run focused tests that protect the current change rather
than assuming every historical test remains current. Useful starting points
for the site shell and bundle contract are:

```powershell
.\.venv\Scripts\python.exe -m pytest -s `
  .\tests\test_make_site89_build.py `
  .\tests\test_make_site89_bundle.py
```

Broaden to all tests only when the focused checks are understood:

```powershell
.\.venv\Scripts\python.exe -m pytest -s tests
```

Tests may be current, stale or legacy. Treat failures as project facts to
classify, not as automatic proof that product code is wrong or that the
environment is broken.

Pytest does not replace browser-functional inspection. make_site89 must be
viewed over HTTP because its pages fetch produced JSON and CSV data.

## Publication Systems

`make_site89` is the current publication system. It accompanied two related
changes:

- replacement of the earlier 1958+/Equelo production scope with one coherent
  post-1988 History and Elo-89 model; and
- separation of upstream analysis and site-data production from the static
  site assembler and renderer.

Its package overview is:

```text
src/products/make_site89/README.md
```

The detailed implementation record is in:

- `src/products/make_site89/docs/Implementation Plan.md`
- `src/products/make_site89/docs/Production Documentation Strategy.md`
- `src/products/make_site89/docs/2026-10-30 Site Build Data Integrity and History Consistency.md`

`make_site2` is retained as legacy code and as evidence about the earlier
1958+/Equelo site. It is not the current production path, and make_site89 does
not import it. Its documentation remains useful for historical behavior and
design context but does not govern new public-site work.

This distinction concerns publication scope, not the value of historical data.
Full-history work may still be run as research and can be reconsidered if the
project later adopts a systematic multi-epoch production design.

## Documentation Map

| Document                                 | Use                                                                |
| ---------------------------------------- | ------------------------------------------------------------------ |
| `docs/LLM Guide.md`                      | Collaboration rules, environment notes and project style for LLMs. |
| `docs/Open Issues.md`                    | After-the-fact bucket for significant unrecorded project-wide TBDs. |
| `docs/Mae-zumo (Mz) Data Semantics and Audit.md` | Warning and required audit for `Mz`, banzuke membership and result coverage. |
| `docs/Project Map.md`                    | Public-site product map and candidate pages.                       |
| `docs/What is an Equelo Rating.md`       | Foundational explanation, assumptions and validation of Equelo.    |
| `docs/House Style.md`                    | Writing and documentation conventions.                             |
| `src/products/make_site89/README.md`     | Current site purpose, production boundary and documentation map.   |
| `src/products/make_site2/docs/README.md` | Legacy make_site2 documentation and historical design record.      |

Archived docs are useful evidence, but active numbered docs and current review
documents govern current work.
