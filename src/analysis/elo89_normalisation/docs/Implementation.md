# Implementation and verification

The first implementation consumes a saved Elo-89 production run. History is
read from the live store by default or from an explicit `--history-zip`, using
the standard repository readers. Outputs are written beneath
`files/output/analysis/elo89_normalisation` by default.

`inputs.py` validates the represented dates, active population, means, eligible
bouts and ledger chii. `accounting.py` reconstructs changes and resets over
the seven reporting windows. `summary.py` supplies descriptive distributions
and group-level comparisons. `report.py` produces CSVs, the prose report and
offline charts, using the local `charts.html` template. Source artifact hashes,
a represented History fingerprint and implementation hashes are recorded in
the output manifest.

The charts select an endpoint, window, population and episode status. The
table can be searched, sorted and filtered to large adjustments or sign
reversals. Full-history distributions and per-endpoint statistics are retained
in CSVs; the report includes full-history comparison tables. Reinitialisation
is a separate accounting term, and no normalisation is attributed during an
absence from the represented population.

## Verification run

The explicit ZIP run used `1989_01 to 2026_11.zip` against the existing
`site89_bundle/sources/elo89` artifacts. The artifact coverage was January 1989
through July 2026, comprising 224 basho. Later History dates were not used to
extend the saved ratings. The live-store invocation was attempted, but the
standard reader reported no published name file available to the process;
the ZIP option was therefore used for the production-data check.

- All 14 package tests passed using unittest, including hand-calculated
  continuous windows, single and multiple returns, no-bout periods, endpoint
  exclusions, input mismatches, statistics and source selection.
- All 985,401 eligible wrestler-windows reconciled. The maximum absolute
  residual was approximately 7.59e-12 points, against a 1e-6 tolerance.
- All 3,822 latest site rows matched for membership, endpoint ratings and
  displayed changes within the site's rounding tolerance.
- Input hashes were checked for changes during execution.
- Browser inspection confirmed populated charts, Makuuchi/window filters and
  the historical May 1992 sign-reversal view, with readable tables and plots.

Tests and the diagnostic run used the bundled Codex Python runtime with NumPy
and pandas because the repository virtual environment points to a missing
Python installation. No environment repair was performed.

These checks establish accounting and presentation correctness for the tested
inputs. They do not constitute the author's judgement of materiality. That
interpretation remains to be recorded separately after examining the outputs.
