# Bout-data completeness

## Question

For every literal chii that actually appears on each selected banzuke, does the
corresponding rikishi's cached SumoDB `Rikishi.aspx` career row contain any
`hoshi` result symbols for that basho?

The audit does not infer an expected number of bouts. Wins, losses, fusen,
kyujo and scheduled lower-division rest days are known source symbols.
`hoshi_empty` is an explicit missing-day placeholder. For the 1958-forward
scope, a rikishi-basho record is complete when it contains exactly 15 symbols
and none is `hoshi_empty`; it is partial when some but not all 15 daily records
are known; and it has no records when no daily symbols occur.

An incomplete record is not counted as missing when the rikishi's parsed
BioStore `Intai` date equals the basho. `Intai` is the retirement fact already
persisted by the application; the probe does not parse or use HTML presentation
classes such as `retired` or `debut`. The atomic output preserves both the empty
field (`recorded=False`) and the retirement (`retired=True`).

Annotations are preserved literally. For example, `O2eHD` is recorded as
`O2eHD`. A chii absent from a basho contributes no row and is not counted as
missing.

## Run

```powershell
python -m src.analysis.bout_data_completeness
```

Defaults:

```text
History:       live store when available
Fallback:      files/output/Historys/1958_01 to 2026_11.zip
BioStore:      files/output/infra/get_bios/rikishi_bios.json
Rikishi pages: files/output/infra/get_bios/rikishi
Date range:    1958/01 through 2026/03
Output:        files/output/analysis/bout_data_completeness
```

An explicit `--history-zip` bypasses the live store for a reproducible run.
Otherwise, an absent or stale published live store causes an automatic fallback
to the default History zip. All paths and date boundaries have command-line
options.

## Outputs

- `basho_chii_record_availability.csv`: one binary availability observation for
  every actual chii-rikishi banzuke occurrence;
- `basho_division_record_availability.csv`: per-basho division counts and the
  classification `none`, `partial` or `complete`, with explicitly retired empty
  rows counted separately rather than as missing, plus expected, known and
  missing daily-record counts and percentages;
- `division_record_availability_summary.csv`: first-any, first-complete,
  last-incomplete and continuous-completeness milestones by division, plus
  daily-record density within partial basho before 1989 and over all data;
- `findings.md`: readable division summary and every partial basho; and
- `manifest.json`: source hashes and the exact interpretation contracts.

Missing cached pages, missing career rows, duplicate career rows and dated rows
without a `hoshi` cell are source-contract failures. They are not silently
classified as missing result records.

The tracked interpretation, quantitative headline findings and claim limits
for Equelo2 are recorded in
[Pre-1989 Bout-Data Completeness and Rating Persistence](../docs/story/17%20Pre-1989%20Bout-Data%20Completeness%20and%20Rating%20Persistence.md).
