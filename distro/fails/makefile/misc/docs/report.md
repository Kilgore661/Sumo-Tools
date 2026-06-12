# misc Package Audit

## Scope

This report covers:

```text
src/misc
```

Imports are classified relative to that package.

## What The Package Is For

`src.misc` is a collection of small historical/reporting producers and support helpers.

It is not a single cohesive library. It is mostly a shelf of standalone analysis/chart programs, with one small helper cluster around `finish_by_chii`.

## What Is In It

| Module | Role |
|---|---|
| `banzuke_by_era.py` | Producer for banzuke division composition by era. |
| `makuuchi_by_era.py` | Producer for Makuuchi rank composition by era. |
| `division_churn.py` | Producer for division retention/churn HTML chart. |
| `first_appearance.py` | Producer for first observed bout appearance by `Chii`. |
| `finish_by_chii.py` | Producer for finishing-position distributions by starting `Chii`. |
| `finish_by_chii_charting.py` | Chart rendering helper for `finish_by_chii.py`. |
| `finish_by_chii_deploy.py` | Deployment helper for `finish_by_chii` local HTML pages. |

## Internal Imports

Internal imports are imports from one module in `src.misc` to another.

```text
finish_by_chii.py -> finish_by_chii_charting.py
finish_by_chii.py -> finish_by_chii_deploy.py
```

All other modules are isolated in the internal import graph.

## External Imports

Third-party external imports:

```text
paramiko
```

Project imports outside the package:

```text
src.infra.config.EPOCH
src.infra.connect.connect
src.sumo_core.BasicEnums
src.sumo_core.BasicPrimitives
src.sumo_core.Chii
src.sumo_core.History
```

Standard-library imports are not treated as dependency edges in this package report.

## Package-Local Dataflow

This report does not reconcile package outputs with consumers outside the package.

Most programs consume a virtual `History` object via `connect(start, end, use_zip)` and write independent output artifacts to `external`.

Visible package-local facts:

```text
History from connect(...)
  -> banzuke_by_era.py
  -> makuuchi_by_era.py
  -> division_churn.py
  -> first_appearance.py
  -> finish_by_chii.py
```

`finish_by_chii.py` also directly calls charting helpers:

```text
finish_by_chii.py
  -- in-memory summary/threshold rows and output paths -->
finish_by_chii_charting.py
  -- HTML chart files -->
external
```

Deployment is recorded separately:

```text
external -- A:/local/html/finish_by_chii/index.html --> finish_by_chii_deploy.py
external -- A:/local/html/finish_by_chii/average.html --> finish_by_chii_deploy.py
external -- GEOLOCATION env var --> finish_by_chii_deploy.py
finish_by_chii_deploy.py -- /var/www/html/finish_by_chii/{index,average}.html --> external
```

The likely match between `finish_by_chii.py` chart output and `finish_by_chii_deploy.py` input is not asserted here. It belongs to reconciliation.

## Inputs By Thing

| Thing | Inputs |
|---|---|
| `banzuke_by_era.py` | `History` from `connect(start, end, use_zip)`; CLI parameters. |
| `makuuchi_by_era.py` | `History` from `connect(start, end, use_zip)`; CLI parameters. |
| `division_churn.py` | `History` from `connect(start, end, use_zip)`; CLI parameters. |
| `first_appearance.py` | `History` from `connect(start, end, use_zip)`; CLI parameters. |
| `finish_by_chii.py` | `History` from `connect(start, end, use_zip)`; CLI parameters. |
| `finish_by_chii_charting.py` | In-memory rows and output paths supplied by caller. |
| `finish_by_chii_deploy.py` | Local HTML files; `GEOLOCATION` env var; remote SFTP endpoint. |

## Outputs By Thing

| Thing | Outputs |
|---|---|
| `banzuke_by_era.py` | `files/output/banzuke_division_era_chart.csv`; `files/output/banzuke_division_era_chart.html`; `files/output/banzuke_division_era/site/banzuke_division_by_era/*`. |
| `makuuchi_by_era.py` | `files/output/rank_era_chart.csv`; `files/output/rank_era_chart.html`; `files/output/rank_era/site/makuuchi_rank_by_era/*`. |
| `division_churn.py` | `files/output/division_churn.html`. |
| `first_appearance.py` | `files/output/first_app.csv`; `files/output/first_app.html`; `files/output/first_app/site/first_chii_appearance/*`. |
| `finish_by_chii.py` | `files/output/misc/finish_by_chii_{start}_{end}_summary.csv`; `top_thresholds.csv`; `bottom_thresholds.csv`; chart input rows for charting helper. |
| `finish_by_chii_charting.py` | Finish-by-chii HTML chart files at caller-supplied paths. |
| `finish_by_chii_deploy.py` | Remote files under `/var/www/html/finish_by_chii/`. |

## Preliminary Reading

`src.misc` contains five report-style producers plus two support helpers for one of those producers.

The package appears real but loosely organised. The central open question is which outputs are active product/research artifacts and which are legacy exploratory charts.

## Open Questions

- Are all five producer entry points still intentionally retained?
- Is `division_churn.py` superseded by `src.analysis.persistence` / Division Stability?
- Should `finish_by_chii_deploy.py` remain inside `misc`, or should deployment be separated from production?
- Which chart HTML outputs are on-demand views rather than retained outputs?
