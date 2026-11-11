# Cumulative Performance Rating

This package produces one CSV for one basho and one division, with one row per
rikishi at the end of every represented day.

CPR is the extended-real rating at which expected wins against the opponents
actually faced equal actual rated wins. Elo-89's rated bout ledger supplies the
pre-bout opponent ratings and excludes fusen and draws.

Run with defaults (latest basho containing results, Makuuchi):

```powershell
python -m src.analysis.cpr
```

Select a basho or division:

```powershell
python -m src.analysis.cpr --date 2026/09 --division juryo
```

Write one combined CSV for every represented basho in a division:

```powershell
python -m src.analysis.cpr --all-basho --division makuuchi
```

Sort by descending Z and retain only the most surprising day for each rikishi
in each basho:

```powershell
python -m src.analysis.cpr --all-basho --division makuuchi --remove-repetitions
```

Output is written below `files/output/analysis/cpr/YYYY-MM/`. CPR is `+inf` for
an undefeated rated record, `-inf` for a winless rated record, and `N/A` when
there have been no rated bouts. Combined output is written below
`files/output/analysis/cpr/all-basho/`. Repetition-free output uses the suffix
`-no-repetitions.csv`; the complete CSV is not overwritten.
