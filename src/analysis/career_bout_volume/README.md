# Career Bout Volume and Relative Banzuke Position

## Research question

This probe investigates the empirical relationship between a rikishi's usual
place on the banzuke and the number of bouts in his career.

The motivating question is of the form:

> Do rikishi who spend their careers around a particular relative banzuke
> position tend to have short careers?

The outcome is bouts fought rather than basho attended. This matters because
the scheduled number of bouts per basho varies by division.

The analysis describes an association. It does not show that rank causes a
career to be long or short, and it is not a prediction made at career entry.
The mean rank is calculated over the completed career and therefore already
contains information about how that career developed.

## A stable coordinate for a changing banzuke

Literal chii are not stable coordinates. For example, `M16e` can occupy a
different absolute place in different basho, and some basho have no `M16` at
all. The probe instead orders the rikishi on each actual banzuke and defines:

```text
normalized position = number of ranked rikishi above
                      ---------------------------------
                      number of ranked rikishi minus 1
```

Thus normalized position is `0` for the top rikishi and `1` for the bottom
rikishi, irrespective of the size or detailed structure of that banzuke. A
rikishi's career value is the unweighted arithmetic mean of these values over
his banzuke appearances.

The volume scatter uses the visually more natural complement:

```text
relative banzuke height = 1 - normalized position
```

On that chart, `0` means the bottom of the banzuke and `1` means the top. The
best rikishi therefore appear at the top of the screen. The transformation is
applied to the plotted values and the endpoints of their confidence intervals;
it is not merely an inverted display axis.

The probability analysis retains the original normalized-position coordinate.
Its band labels consequently run from `0` at the top to `1` at the bottom:

| Mean normalized-position band | Interpretation |
|---|---|
| 0.0000 to below 0.2000 | Highest part of the banzuke |
| 0.2000 to below 0.4000 | High |
| 0.4000 to below 0.6000 | Middle |
| 0.6000 to below 0.8395 | Lower |
| 0.8395 to 1.0000 | Lowest tail, beginning at the Jd100-related boundary used in this investigation |

The `0.8395` cut is deliberately retained because of the separate Elo and
Equelo evidence concerning Jd100 and below. The other cuts are broad
descriptive reference bands, not discovered change points.

## Population and bout rules

The principal probability population contains only completed careers that do
not begin in the first basho of the supplied History. This removes:

- active careers, whose final bout totals are right-censored;
- partial-start careers already in progress when the History begins.

All career states remain available in the volume scatter for reference.
Completed, non-partial careers are visible initially. Active, partial-start,
and active-plus-partial-start traces begin hidden and can be enabled through
the Plotly legend.

A fought bout is a result recorded as win, loss, or draw. Fusensho and
fusenpai records are retained in the audit data but do not count as bouts
fought.

A bout endpoint absent from that basho's banzuke cannot be assigned a relative
position. Such occurrences are ignored at that boundary and counted as
exceptions. The final exception count is printed by the command and recorded
in the manifest.

## Outputs

Each invocation creates an immutable UTC date-time-stamped directory beneath:

```text
files/output/analysis/career_bout_volume/
```

The run contains:

- `rikishi_basho.csv`: one auditable observation per rikishi-basho;
- `rikishi_careers.csv`: career totals and position summaries;
- `career_bout_volume.html`: unbinned career scatter;
- `career_bout_probability.csv`: probability curve data;
- `career_bout_probability.html`: interactive empirical tail-probability chart;
- `manifest.json`: source, contracts, counts, output inventory, and Git state.

The CSV files intentionally retain supporting fields rather than presenting
only the values needed to draw the charts.

## Reading the charts

### Career bout volume

The horizontal axis is total career bouts fought. The vertical axis is mean
relative banzuke height, with `0` at the bottom and `1` at the top. Each point
is one rikishi.

This is the complete reference view. It preserves individual careers rather
than binning approximately 9,000 points. Status traces can be shown or hidden
by clicking their legend entries.

The hover data includes the standard deviation of the rikishi's observed
positions and a naive normal 95% confidence interval for his mean position.
The interval is clipped to the coordinate range. Repeated observations within
one career are temporally dependent, so this interval is descriptive rather
than a complete sampling model.

### Probability of reaching a bout total

For a bout threshold `x`, a curve reports:

```text
P(total career bouts fought >= x | mean-position band,
  completed non-partial career)
```

For example, a value of `0.30` at 200 bouts means that 30% of the completed,
non-partial careers in that position band fought at least 200 bouts. It does
not mean that a particular active rikishi currently in the band has a 30%
chance of reaching 200 bouts.

Every point estimate has a Wilson 95% binomial confidence interval. Each CI95
band is a separate Plotly trace, hidden initially. It can be enabled or hidden
independently by clicking its legend entry. This doubles the legend entries:
one line and one CI95 band for every populated position band.

## Initial empirical reading

The scatter suggests three broad features worth describing rather than
over-formalising at this stage:

- the densest region consists of short careers in the lower half of the
  banzuke;
- high mean career position is associated with substantially greater bout
  volume, with the upper part of the cloud showing an approximate gradient;
- a much smaller group combines low mean position with high bout volume, the
  visually identifiable long-serving lower-division or "journeyman" tail.

The probability curves turn that visual impression into statements about the
observed proportion of completed careers reaching each bout threshold. They
are preferable to a single assertion such as "rikishi below Jd100 rarely last
two years" because they:

- use bouts rather than calendar time or basho count;
- show the whole survival-like curve instead of one arbitrary cutoff;
- distinguish broad regions of the actual banzuke;
- expose sample size and uncertainty at every threshold.

The results do not establish that Jd100 is a causal or statistically fitted
longevity boundary. Here it is an evidence-motivated comparison point inherited
from the separate rating-curve investigation.

## Running the probe

The default command uses the complete History from the live store when it is
available:

```powershell
python -m src.analysis.career_bout_volume
```

Use the standard short History for development and smoke tests:

```powershell
python -m src.analysis.career_bout_volume --short
```

An explicit persisted History zip can also be supplied:

```powershell
python -m src.analysis.career_bout_volume --history-zip path\to\History.zip
```

Focused verification is in `tests/test_career_bout_volume.py`.

## Implemented rating-maturity investigation

[Proposal 1: Rating Maturity, Initialisation Sensitivity and Banzuke
Position](docs/Proposal%201%20-%20Rating%20Maturity%20by%20Banzuke%20Position.md)
defines the follow-up whose new declared replay begins at `1989/01`. The existing
career-volume run covers `1958/01`--`2026/07` and motivates the question; it is
not the complete-results-era test.

The implemented `rating_maturity` subpackage measures prior rated-bout support
at each current banzuke position, compares coupled `B_k` and `B_kP` processes,
and tests whether controlling for rating maturity helps explain the irregular
chii-rating relationship below approximately `Jd100`.

Run the declared `1989/01`--`2026/07` investigation with:

```powershell
python -m src.analysis.career_bout_volume.rating_maturity
```

It writes a timestamped audit directory beneath:

```text
files/output/analysis/career_bout_volume/rating_maturity/
```

The output `findings.md` leads with answers to the three staged questions.
Focused replay and reporting verification is in `tests/test_rating_maturity.py`.
