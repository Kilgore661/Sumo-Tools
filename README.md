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

| Path | Role |
| --- | --- |
| `src/sumo_core` | Core domain model. |
| `src/infra` | Scraping, parsing, persistence, tracker and live store. |
| `src/analysis` | Derived views, public tools, experiments and reports. |
| `src/products/make_site2` | Current static publication system. |
| `docs` | Project-level orientation and working conventions. |
| `files/output` | Local generated data and build artifacts; not tracked by git. |

## Data Sources

Most build paths use a `History` object. There are two common ways to provide
one:

1. Use the live store:

   ```powershell
   py -m src.products.make_site2 --build-only
   ```

2. Use a local History zip, useful for quick repeatable tests:

   ```powershell
   py -m src.products.make_site2 --build-only --history-zip ".\files\output\Historys\1978_01 to 1980_11.zip"
   ```

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

Focused make_site2 tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -s `
  .\tests\test_make_site2_build.py `
  .\tests\test_make_site2_cli.py `
  .\tests\test_make_site2_data_output.py `
  .\tests\test_make_site2_deploy.py `
  .\tests\test_make_site2_publication_plan.py `
  .\tests\test_make_site2_runtime_source.py
```

Some tests may lag behind the current modular runtime and manifest split. Treat
test failures as project facts to inspect, not as proof that the environment is
broken.

## make_site2 Status

`make_site2` is the current publication system. Its active docs are in:

```text
src/products/make_site2/docs
```

Start with:

- `src/products/make_site2/docs/README.md`
- `src/products/make_site2/docs/01 Requirements.md`
- `src/products/make_site2/docs/02 Specification.md`
- `src/products/make_site2/docs/10 Open Issues and Deferred Design.md`
- `src/products/make_site2/docs/Second make_site2 Review.md`

Current high-level status:

- The explicit `Contents -> FilterSection? . PAPanel -> PA . Notes` page
  structure is implemented.
- Canonical single-shell `?page=...` public links are implemented.
- Selected-History coherence is the active production P0: a normal public build
  must not silently present copied History-dependent material as coherent with
  an explicit History selection. Quick local/inspection builds may temporarily
  allow reduced or caveated output, but that policy still needs to be made
  explicit in code and visible output.
- Deployment target safety remains an open operational improvement.

## Documentation Map

| Document | Use |
| --- | --- |
| `docs/LLM Guide.md` | Collaboration rules, environment notes and project style for LLMs. |
| `docs/Project Map.md` | Public-site product map and candidate pages. |
| `docs/House Style.md` | Writing and documentation conventions. |
| `src/products/make_site2/docs/README.md` | make_site2 documentation authority and reading order. |

Archived docs are useful evidence, but active numbered docs and current review
documents govern current work.
