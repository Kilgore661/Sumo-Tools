# live_store Package Audit

## Scope

This report covers:

```text
src/infra/live_store
```

Imports are classified relative to that package.

## What The Package Is For

`src.infra.live_store` provides runtime access to the current canonical `History` object.

It stores a pickled `History` in a named shared-memory segment and records the current segment name in a small file.

Consumers call:

```python
get_history()
```

and receive a `History` object without directly loading a History zip.

## What Is In It

| Module | Role |
|---|---|
| `LiveStore.py` | Shared-memory publisher/connector for pickled `History` payloads. |
| `api.py` | Client-facing API that reads the published name file and returns the current `History`. |
| `config.py` | Version and published-name file path. |

## Internal Imports

Internal imports are imports from one module in `src.infra.live_store` to another.

```text
api.py -> LiveStore.py
api.py -> config.py
LiveStore.py -> config.py
```

## External Imports

Third-party external imports: none seen.

Project imports outside the package:

```text
src.sumo_core.History.History
src.infra.persistence.annotated_serialiser.load_history_with_annotations
src.infra.parser.parser2.OUTPUT_DIR
src.infra.config.EPOCH
```

Standard-library imports are not treated as dependency edges in this package report.

## Package-Local Dataflow

This package has two important boundary mechanisms:

```text
files/output/store_name.txt
named shared-memory segment history{VERSION}
```

Visible package-local facts:

```text
external
  -- files/output/store_name.txt -->
api.py
  -- shared-memory segment name -->
LiveStore.py
  -- History object -->
api.py
  -- History object -->
external
```

Publisher/bootstrap flow:

```text
external
  -- files/output/Historys/{EPOCH}_01 to {current_year}_11 -->
LiveStore.py
  -- named shared-memory segment history{VERSION} -->
external
```

Name publication helpers:

```text
api.py -- files/output/store_name.txt --> external
api.py -- deletes files/output/store_name.txt --> external
```

Package-local reconciliation does not connect this package to downstream `get_history()` consumers. Those consumers are discovered in their own package audits or global reconciliation.

## Inputs By Thing

| Thing | Inputs |
|---|---|
| `LiveStore.py` | `History` object supplied to `publish`; canonical History zip path for `init_live_store`; shared-memory segment name. |
| `api.py` | `files/output/store_name.txt`; named shared-memory segment. |
| `config.py` | None. |

## Outputs By Thing

| Thing | Outputs |
|---|---|
| `LiveStore.py` | named shared-memory segment containing pickled `History`; in-memory `History` returned by `connect()`. |
| `api.py` | `History` returned by `get_history()`; `files/output/store_name.txt` via `write_published_name`; deletion of name file via `clear_published_name`. |
| `config.py` | constants only. |

## Preliminary Reading

`live_store` is infrastructure, not an analysis producer.

It is central because many modules depend on `get_history()`, but package-local audit should treat its shared-memory and name-file outputs as boundary artifacts until global reconciliation.

## Open Questions

- Should `files/output/store_name.txt` be treated as a generated runtime control file rather than ordinary output?
- Should the shared-memory segment be represented as a virtual artifact family in global reconciliation?
- Should `LiveStore.py` remain directly executable as a bootstrap/test entry point?
