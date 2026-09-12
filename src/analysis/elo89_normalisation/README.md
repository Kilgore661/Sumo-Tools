# Elo-89 normalisation diagnostics

Read [Normalisation Investigation](docs/Normalisation%20Investigation.md) for the
standalone account of the original TBD, the interpretation choices, the recent
Makuuchi/Juryo headline, the full-history exceptions and the resulting judgement.

This package quantifies the contribution of population normalisation to
published Elo-89 rating changes. Its purpose is to give the author numbers,
distributions and concrete examples with which to judge practical importance.
It is not a model-selection gate, and an appreciable effect does not by itself
require changing the accepted model.

**Status: implemented.** Run from the repository root using Python with NumPy
and pandas available. Charts use local HTML/JavaScript and require no plotting
service or remote library.

```powershell
python -m src.analysis.elo89_normalisation
```

History comes from the live store by default. To select an annotated ZIP:

```powershell
python -m src.analysis.elo89_normalisation `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip"
```

The live-store reader follows the repository convention: if no published store
is available it exits rather than creating one or silently choosing a ZIP.

The saved Elo-89 run defaults to
`files/output/analysis/site89_bundle/sources/elo89`; use `--elo-root` to select
another run. History supplies metadata and validates eligible bouts against
that run; its additional dates are not used to extend or rerun Elo-89.

Output defaults to `files/output/analysis/elo89_normalisation` (override with
`--output-root`). Start with `report.md` and `charts.html`. Keep `chart_data`
beside the HTML; the charts work offline or through a local HTTP server.
The package overwrites its named outputs without deleting unrelated files.
Only files listed in the current output manifest belong to the current run.

For a standard site bundle, latest site change tables are discovered and
reconciled automatically. `--site-changes` can specify a different directory.
If none is available, the report records that this comparison was not performed.

## Supplementary analyses

**Proposed, not yet implemented:** [Per-chii rating drift after mean
preservation](docs/Proposal%20-%20Per-Chii%20Rating%20Drift.md) asks whether
ratings at particular banzuke positions trend over historical time despite
the fixed population mean. It uses saved post-normalisation ratings and is
distinct from the contribution accounting below.

The Elo89 account's drafting is postponed until this study and its verification
checks have been run and the findings reviewed. See the
[documentation hand-off](../../products/make_site89/docs/Documentation%20Handoff.md).

For the subsequent assessment allowing signed cancellation, read
[Signed Findings](docs/Signed%20Findings.md). Reproduce its supplementary tables
from the existing diagnostic outputs with:

```powershell
python -m src.analysis.elo89_normalisation.signed_results
```

This supplementary command reads generated CSVs rather than reloading History.
It uses the same default output directory and accepts `--output-root`.

Reproduce the full-history table of 12-basho normalisation contributions as a
percentage of end rating, by division, with:

```powershell
python -m src.analysis.elo89_normalisation.division_percentages
```

This reads `window_changes.csv` and writes `division_percentages.md`,
`division_percentages.csv`, `division_percentage_exceptions.csv` and a source
manifest in the same output directory. It preserves signed cancellation and
reports the proportions within ±1% and ±5%. Reinitialisation windows are
excluded; division is determined at the end endpoint. `--output-root` selects
another existing diagnostic directory.

The same command also generates `recent_sekitori_percentages.md` and `.csv`,
plus the individual rows in `recent_sekitori_windows.csv` and a separate source
manifest. This reproduces the recent Makuuchi/Juryo comparison: continuous
12-basho windows starting January 2016 or later, classified by end division.
The report includes signed minima/maxima and exact counts within and outside
±1%, computed before rounding. The full-history table remains alongside it.

## Verification tests

```powershell
python -m unittest discover -s tests -p test_elo89_normalisation.py -v
```

Read [the implementation proposal](docs/Proposal.md) for the questions, input
contract, accounting definitions, proposed outputs and verification requirements.
The motivating appraisal is
[Elo-89 Rating System Appraisal](../docs/story/22%20Elo-89%20Rating%20System%20Appraisal.md).

The analysis reads existing production Elo-89 artifacts and matching
History metadata. It writes only to its own output directory. It does not
modify the rating calculation, recompute P1, regenerate the website or deploy
anything. The initial experiment concerns observed rating-change accounting;
a replay without normalisation would answer a different question and is not
part of this proposal.
