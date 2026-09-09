# Signed normalisation contributions

## Question and approach

This assessment examines whether normalisation leaves a net contribution to
reported rating changes once positive and negative adjustments cancel. It uses
signed contributions throughout. Absolute-change summaries are not used to
judge significance here.

Within a window, the contributions are summed with their signs. Across the
population of windows, signed means describe their average direction and net
contribution. Signed percentiles preserve variation that a mean alone cannot
show. Overlapping windows are not added together to construct a cumulative
history; cumulative totals use each basho adjustment exactly once.

The source is the existing production run, January 1989 through July 2026.
The recent-period view starts in January 2016, an explicit exploratory cutoff,
not a fitted breakpoint or a claim that this is the uniquely correct meaning
of recent. Common-adjustment totals include that January adjustment. Recent
rating-change windows start at or after the January 2016 end snapshot, so their
first included adjustment is later. They also weight wrestler-windows rather
than basho; the resulting averages need not match.

## Cancellation is substantial, but historically incomplete

Across all 224 basho, pre-basho adjustments sum to +264.640 points and post-basho
adjustments to -4.829 points. Their combined sum is +259.810 points: a signed
mean of +1.160 points per basho. The median combined adjustment is -0.449.

The positive mean and negative median have a straightforward interpretation:
many negative adjustments are counterbalanced by fewer, larger positive ones.
The historical combined mean by basho month makes the pattern visible:

| Basho month | Mean combined adjustment |
|---|---:|
| January | -1.045 |
| March | -1.115 |
| May | +12.178 |
| July | +0.900 |
| September | -1.758 |
| November | -2.135 |

There is therefore cancellation across the seasonal cycle. It is not complete
over the full record. These monthly averages describe the pattern; they do not
by themselves establish why it occurs.

The +259.810 total is a cumulative index of common shifts, not an amount to
subtract from every current wrestler. Wrestlers receive only shifts while
represented, and reinitialisation starts a new rating episode. Nor does this
total demonstrate rating inflation: the population mean is restored by these
very operations, and this accounting has not rerun an alternative model.

## Recent years show much closer cancellation

For January 2016 through July 2026, 63 basho adjustments sum to:

| Contribution | Signed total |
|---|---:|
| Pre-basho | +14.130 |
| Post-basho | -1.856 |
| Combined | +12.275 |

The mean combined adjustment is +0.195 points per basho; its median is -0.826.
Calendar-year combined totals show the cancellation directly:

| Year | Combined contribution |
|---|---:|
| 2016 | -1.086 |
| 2017 | +2.137 |
| 2018 | +5.483 |
| 2019 | +10.041 |
| 2020 | +6.063 |
| 2021 | +0.097 |
| 2022 | -6.296 |
| 2023 | +3.865 |
| 2024 | -5.586 |
| 2025 | +0.634 |
| 2026, through July | -3.078 |

2020 contains five represented basho; the 2026 row contains four. These are
observed totals, not annualised estimates. A wrestler continuously represented
through this interval receives the combined +12.275 contribution across those
63 basho. This statement does not apply across a reinitialisation.

## Makuuchi reporting windows

For continuous rating windows, with Makuuchi membership determined at the end
endpoint, the signed normalisation contributions are:

| Period | Window | Mean | Median | 5th percentile | 95th percentile |
|---|---:|---:|---:|---:|---:|
| Full history | 1 basho | +1.145 | -0.453 | -4.770 | +15.312 |
| Full history | 6 basho | +6.830 | +5.712 | -5.358 | +27.019 |
| Full history | 12 basho | +13.758 | +11.038 | -5.990 | +50.374 |
| Windows starting January 2016 onward | 1 basho | +0.254 | -0.826 | -4.106 | +7.566 |
| Windows starting January 2016 onward | 6 basho | +1.458 | +1.586 | -7.602 | +9.328 |
| Windows starting January 2016 onward | 12 basho | +3.566 | +4.036 | -6.199 | +15.525 |

The percentiles describe the signed distribution, not confidence intervals.
Each wrestler-window has equal weight. Rolling windows overlap. Reinitialising
windows are excluded here because their reset term is a distinct contribution.
For continuously represented wrestlers sharing the same endpoints, the common
normalisation contribution is identical; a Makuuchi subgroup does not receive
a different adjustment merely because it is Makuuchi.

On this signed basis the recent six-basho result is a small average upward
contribution, +1.458 points. It is substantially closer to zero than the
full-history average of +6.830. The distribution also contains windows with
negative net contributions and windows with larger positive contributions.
Cancellation supports the recent-period expectation without establishing that
every individual reporting period is unaffected.

## Individual cases retain their signs

May 1992 remains an example of a substantial positive contribution in a single
basho. Konishiki's bout updates sum to -26.132, while the combined common
adjustment is +30.363, giving a displayed change of +4.231. Nothing about using
signed summaries removes that observation. Later adjustments must be included
with their signs when considering a longer period; this example alone does
not establish his net adjustment over that longer period.

## Assessment

The signed results support substantial cancellation, especially in the recent
period. They do not support complete cancellation over the full historical
record. My assessment is that the recent average net contributions are modest,
while historical tables should acknowledge that some periods have appreciable
positive contributions from population normalisation.

That is a qualification of how reported changes should be read, not a finding
that Elo-89 needs replacing. These results quantify an accounting contribution,
not a defect in matchup probabilities or the causal effect of the policy.
They provide a basis for the author's judgement of practical importance; no
numerical pass/fail rule is introduced.

Absolute-change summaries could separately describe the size of temporary
departures irrespective of direction. They are deliberately not part of this
assessment, and the earlier absolute-ratio interpretation should not be treated
as its conclusion.

## Reproduction

After generating the main diagnostic outputs, run:

```powershell
python -m src.analysis.elo89_normalisation.signed_results
```

This reads the existing `basho_adjustments.csv` and `window_changes.csv` in
`files/output/analysis/elo89_normalisation`. It does not reload History or
recalculate ratings. `--output-root` selects another existing diagnostic
directory. It writes `signed_summaries.csv`, `signed_years.csv`,
`signed_seasons.csv`, `signed_cumulative.csv` and a separate
`signed_manifest.json` identifying source hashes, weighting and cutoff.

The main generated `report.md` retains the original absolute summaries for
traceability. This document is the subsequent signed assessment.
