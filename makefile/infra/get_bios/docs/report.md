# get_bios Package Audit

## Scope

This report covers:

```text
src/infra/get_bios
```

Imports are classified relative to that package.

## What The Package Is For

`src.infra.get_bios` enriches parsed sumo `History` data with rikishi biographical data from SumoDB `Rikishi.aspx` pages.

It is not one thing. It is a small pipeline plus support tools:

```text
download raw biography HTML
  -> parse raw HTML into structured biography JSON
    -> expose a typed API over that JSON
      -> run probes and integrity checks
```

## What Is In It

| Module | Role |
|---|---|
| `__main__.py` | Downloader entry point for missing raw SumoDB rikishi biography HTML. |
| `parser.py` | Parser from downloaded HTML to structured JSON plus missing-field diagnostics. |
| `api.py` | Typed access layer over parsed biography JSON. |
| `integrity.py` | Cross-checks parsed bio lifecycle dates against represented `History` appearances. |
| `bmi.py` | Probe that reports BMI distribution from parsed height/weight fields. |
| `hw_distr.py` | Probe that reports height-history support counts. |
| `probe.py` | Probe that reports `Shusshin` frequency bins. |

## Internal Imports

Internal imports are imports from one module in `src.infra.get_bios` to another.

```text
api.py -> parser.py
integrity.py -> api.py
```

All other modules are isolated in the internal import graph.

## External Imports

Third-party external imports: none seen.

Project imports outside the package:

```text
src.infra.live_store.api.get_history
src.infra.parser.parser2.OUTPUT_DIR
src.infra.persistence.new_sumo_serialiser.load_history_with_annotations
src.sumo_core.BasicPrimitives.RikId
src.sumo_core.BasicPrimitives.Shikona
src.sumo_core.History.Date
```

Standard-library imports are not treated as dependency edges in this package report.

## Package-Local Dataflow

This report does not reconcile package outputs with package inputs through shared storage.

From the package-local perspective, artifact writes go to `external` and artifact reads come from `external`.

The visible facts are:

```text
live History
  -- get_history() -->
__main__.py
  -- OUTPUT_DIR/infra/rikishi/{rikid:05d}.html -->
external

external
  -- OUTPUT_DIR/infra/rikishi/*.html -->
parser.py

parser.py
  -- OUTPUT_DIR/infra/rikishi_bios.json -->
external

external
  -- OUTPUT_DIR/infra/rikishi_bios.json -->
api.py / bmi.py / hw_distr.py / probe.py / integrity.py
```

The likely match between `__main__.py`'s raw HTML output and `parser.py`'s raw HTML input is deliberately not asserted here. It belongs to global reconciliation.

Additional outputs:

```text
parser.py    -- OUTPUT_DIR/infra/rikishi_bio_missing_fields.csv
hw_distr.py  -- OUTPUT_DIR/infra/height_support_bins.csv
probe.py     -- OUTPUT_DIR/infra/shusshin_bins.csv
integrity.py -- OUTPUT_DIR/infra/rikishi_bio_history_integrity.csv
```

`integrity.py` also reads a History zip, defaulting to:

```text
OUTPUT_DIR/Historys/1958_01 to 2026_11
```

## Inputs By Thing

| Thing | Inputs |
|---|---|
| `__main__.py` | live History from `get_history()`; existing `OUTPUT_DIR/infra/rikishi/*.html`; `https://sumodb.sumogames.de/Rikishi.aspx?r={rikid}` |
| `parser.py` | `OUTPUT_DIR/infra/rikishi/*.html` |
| `api.py` | `OUTPUT_DIR/infra/rikishi_bios.json` |
| `bmi.py` | `OUTPUT_DIR/infra/rikishi_bios.json` |
| `hw_distr.py` | `OUTPUT_DIR/infra/rikishi_bios.json` |
| `probe.py` | `OUTPUT_DIR/infra/rikishi_bios.json` |
| `integrity.py` | `OUTPUT_DIR/infra/rikishi_bios.json`; `OUTPUT_DIR/Historys/1958_01 to 2026_11` unless overridden |

## Outputs By Thing

| Thing | Outputs |
|---|---|
| `__main__.py` | `OUTPUT_DIR/infra/rikishi/{rikid:05d}.html` |
| `parser.py` | `OUTPUT_DIR/infra/rikishi_bios.json`; `OUTPUT_DIR/infra/rikishi_bio_missing_fields.csv`; stdout diagnostics |
| `api.py` | in-memory `BioStore` / `RikishiBio` objects |
| `bmi.py` | stdout BMI summary |
| `hw_distr.py` | `OUTPUT_DIR/infra/height_support_bins.csv`; stdout summary |
| `probe.py` | `OUTPUT_DIR/infra/shusshin_bins.csv`; stdout summary |
| `integrity.py` | `OUTPUT_DIR/infra/rikishi_bio_history_integrity.csv`; stdout summary |

## Preliminary Reading

This package is coherent and non-trivial. It should not be judged from the import graph alone.

The import graph makes `__main__.py`, `bmi.py`, `hw_distr.py`, and `probe.py` look isolated. The package-local dataflow graph shows that they read or write related biography artifacts, while leaving actual artifact matching to reconciliation.

## Open Questions

- Should `rikishi_bios.json` be promoted to canonical data or remain producer output?
- Which probes are retained diagnostics and which are exploratory legacy scripts?
- Is `integrity.py` an active quality gate, a diagnostic, or a research check?
- Should `OUTPUT_DIR/infra/rikishi/{rikid}.html` be treated as source capture with a freshness policy?
