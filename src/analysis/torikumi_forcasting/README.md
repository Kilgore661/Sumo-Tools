# Torikumi Forecasting

This package will investigate a deliberately narrow question:

> To what extent can the torikumi for a late basho day `d` be forecast from
> the standings and other information available after day `d - 2`?

The package directory uses the requested name `torikumi_forcasting`.  In the
documentation, *forecasting* distinguishes this task from the project's other
uses of *torikumi prediction*.  Those analyses describe scheduled opponents or
predict the result of a bout once its torikumi is known; this analysis asks
which bouts will be scheduled.

Historical heya are compiled into a forecasting-owned artifact rather than
added to canonical `History` during this exploratory work:

```powershell
python -m src.analysis.torikumi_forcasting.heya_compiler
```

This writes `heya_index.json` and `heya_diagnostics.csv` beneath
`files/output/analysis/torikumi_forcasting`.  The compiler is rerunnable and
does not modify the archived HTML or `History`.

Run the greedy experiment after compiling heya:

```powershell
python -m src.analysis.torikumi_forcasting
python -m src.analysis.torikumi_forcasting --start 1989/01 --first-day 11
```

Run the constrained experiment separately:

```powershell
python -m src.analysis.torikumi_forcasting.constrained_cli
python -m src.analysis.torikumi_forcasting.constrained_cli --start 2026/09 --end 2026/09
```

The constrained command prints loading stages and one progress line per basho.

The investigation is intentionally simple.  Its purpose is to find out whether
a basic, intelligible rule is remotely useful before investing in a refined or
probabilistic model.  A failure is an adequate and useful result.

See [Initial Thoughts](docs/Initial%20Thoughts.md) for the current motivation,
source observations, proposed baseline and limits.  The agreed two-approach
experiment is specified in
[Proposal - Greedy and Constrained Matching](docs/Proposal%20-%20Greedy%20and%20Constrained%20Matching.md).
The first full greedy results are recorded in
[Greedy Findings](docs/Greedy%20Findings.md).
The combined interpretation of both experiments is recorded in
[Findings - Falsifying the Rule of Thumb](docs/Findings%20-%20Falsifying%20the%20Rule%20of%20Thumb.md).

