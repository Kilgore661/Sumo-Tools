# Chii winner prediction

Count how often the rikishi with the stronger pre-basho chii wins. This is a
standalone descriptive baseline, with no Elo fitting or probability calibration.

See [Findings](docs/Findings.md) for the motivation, recorded results, relationship
to the earlier Elo scores, and the agreed limits of this probe.

Run from the repository root:

```powershell
python -m src.analysis.chii_prediction
python -m src.analysis.chii_prediction --start 1989/01 --end 2026/07
```

Options: `--history-zip PATH`, `--start YYYY/MM`, `--end YYYY/MM`,
`--output-root PATH`. The default source is
`files/output/Historys/1958_01 to 2026_11.zip`; the default range begins in
1989/01 and ends at the latest represented basho in that archive.

Outputs in `files/output/analysis/chii_prediction` include both dates in each
filename, for example `counts_1989_01_to_2026_07.csv`,
`report_1989_01_to_2026_07.md`, and `manifest_1989_01_to_2026_07.json`
(source path/hash, range and counts). Re-running the same range replaces these
files; use a different output root to retain separate runs of that range.

The numerator is higher-chii wins; the denominator is eligible bouts. Stronger
means lower `Chii.ordinal()`, including side and annotations. Each W/L result
is counted once using the existing prediction bout selector. Defaults (FS/FP)
and other outcomes are excluded. Blank kimarite does not exclude W/L results.
Missing chii excludes a bout and is reported. The archive also contains some
opponents with equal recorded chii (for example Ms60eTD in 1996/01); these
are excluded and counted separately because no stronger chii can be selected.

Each division row contains bouts with both rikishi in that division.
Cross-division bouts have their own row. The six division rows plus the
cross-division row partition ALL, so no bout is counted twice in that total.
Empty groups have undefined rates, displayed as n/a. The aggregate is weighted
by bout count, not an average of division percentages.

The report gives counts, win percentage, and percentage points above 50%.
These are observed frequencies, not a significance test. The default starts
in 1989 because earlier lower-division records are incomplete. Earlier ranges
can be requested, but results cover only the represented bouts.
