# JSA Check

JSA Check is an isolated empirical experiment within the `absences` analysis
area.

Its question is:

> To what extent can recorded sub-sekitori absences be assigned to particular
> scheduling windows under the Japan Sumo Association's normal seven-window
> guideline?

The experiment covers makushita, sandanme, jonidan and jonokuchi from January
1989 onward.  It compares the final absence count with the empty scheduling
windows.  Opportunity totals, dated-result reconciliation and departures from
the normal at-most-one-outcome-per-window pattern are reported independently as
data and scheduling diagnostics; they are not automatic inference filters.

The experiment may assign an absence to a scheduling window, but it does not
infer a particular kyujo day, explain why a departure occurred, or propose
changes elsewhere in the project.

## Documentation

- [Stage 1 Proposal](docs/Stage%201%20Proposal.md)

## Run

Use the live History store:

```powershell
python -m src.analysis.absences.jsa_check
```

Or select a reproducible History zip:

```powershell
python -m src.analysis.absences.jsa_check `
  --history-zip ".\files\output\Historys\1989_01 to 2026_11.zip"
```

The default output directory is:

```text
files/output/analysis/absences/jsa_check
```

It contains the atomic rikishi-basho CSV and a text summary of the diagnostics
and absence-inference classifications.  The summary also records a timezone-
aware generation timestamp and the selected History, final-record and
retirement sources.  The final records are read from the cached SumoDB banzuke
pages under `files/output/current standings`; they are not reconstructed from
the daily outcomes.  The latest post-parsing
rank-at-retirement rikishi artifact under `files/output/rank_at_retirement` is
joined by rikishi ID to identify final observed basho.  Use `--retirement-csv`
to select a particular artifact explicitly.

Draws occupy scheduling windows.  The experiment therefore stops with a clear
error if a final draw count cannot be reconciled with dated draws in History;
rebuild History with the current parser before rerunning it.
