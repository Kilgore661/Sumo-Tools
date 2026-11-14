# Proposal: Average Age by Division

## Status

Implemented as the first public artifact in the `Age` research-navigation
category in `make_site89`.

The requirements are sufficiently tight to implement once the presentation
defaults below are adopted. This proposal makes those defaults explicit.

## Question

For every represented basho, what was the average age of the rikishi in each
formal banzuke division?

The public chart answers this with one time-series trace per division. A user
can show or hide individual divisions from the Plotly legend. An optional
control adds the observed youngest and oldest ages as asymmetric vertical
range bars around each mean.

## Adopted presentation defaults

- Makuuchi is visible initially; the other five divisions begin in the legend
  and can be selected there.
- A normal legend click toggles one division.
- A legend double-click isolates one division, following ordinary Plotly
  behaviour.
- Min/max range bars are off initially and controlled by a `Min & Max`
  checkbox.
- Changing the range-bar option preserves the current legend selection.
- The range bars show observed minimum and maximum ages. They are not
  confidence intervals, standard errors, or another measure of uncertainty.
- No smoothing is applied.

## Divisions

The traces are, in this order:

1. Makuuchi;
2. Juryo;
3. Makushita;
4. Sandanme;
5. Jonidan; and
6. Jonokuchi.

Makuuchi includes san'yaku and Maegashira. East and west do not form separate
groups. Maezumo is not a formal banzuke division and is excluded.

## Population and observation unit

The observation unit is one rikishi occupying one formal banzuke position in
one basho. Every rikishi on the represented banzuke belongs to exactly one of
the six division groups.

The calculation does not require a complete represented career. A
left-boundary incumbent is a valid observation for this artifact because only
the rikishi's age and current division are required.

Within each `(basho, division)` group:

- rikishi with a usable full birth date contribute to the age statistics;
- rikishi without a usable full birth date remain in the population and
  missingness counts but do not contribute an invented age; and
- every contributing rikishi has equal weight.

## Age definition

Age is continuous age in years on the exact civil date of Day 1 of the basho.
It is calculated from the full persisted birth date and the exact tournament
start date. Continuous age is used rather than completed integer age because
averaging completed ages would introduce a downward rounding bias of roughly
half a year.

For a rikishi with completed age `A`, continuous age is:

```text
A + days since last birthday / days between adjacent birthdays
```

The 29 February convention must match the existing completed-age convention:
in a non-leap year the anniversary advances on 1 March.

The implementation should put this calculation in a public utility owned by
`analysis.ages`; it must not import the private chart helper currently living
under `analysis.greatness.sanyaku_prospects`.

## Source data

The producer consumes:

- `History`, for the rikishi and chii on each represented banzuke;
- `BioStore`, loaded from the persisted `rikishi_bios.json`, for exact birth
  dates; and
- an exact basho calendar, for the civil date of Day 1.

The current core `History` key contains year and month but not the exact civil
start date. Until infrastructure persists a first-class basho calendar, the
producer may use `infra.parser.basho_calendar.basho_date_coverage` to derive
Day 1 from downloaded daily-results HTML, as the san'yaku-prospects analysis
does. Production must fail rather than silently substitute the first of the
labelled month when a represented basho has missing or inconsistent exact-date
evidence.

The public site artifact uses the same selected History as the `site89` bundle.
At present that means the displayed series begins at 1989/01 even though the
general `analysis.ages` producer may be run against a longer History.

Publishing the complete 1958+ series is parked future work. The intended
implementation is a separate full-History input for this artifact; the main
site89 History and its Elo replay should retain their 1989/01 boundary.

## Statistics

For each `(basho, division)` group calculate:

- arithmetic mean continuous age;
- minimum continuous age;
- maximum continuous age;
- total rikishi on the division banzuke;
- rikishi with exact birth dates;
- rikishi without exact birth dates;
- missing bio records; and
- bio records without usable exact birth dates.

The reconciliation rules are:

```text
banzuke_rikishi
    = exact_birth_date + missing_exact_birth_date

missing_exact_birth_date
    = missing_bio + bio_without_exact_birth_date
```

If a group has no exact birth dates, its mean, minimum and maximum are blank and
the corresponding trace contains a gap. Zero must not be used as an age.

## Produced CSV

The analysis module is:

```text
src/analysis/ages/average_age_by_division.py
```

Its site-facing CSV has one row per basho and division:

```text
basho
start_date
division
banzuke_rikishi
exact_birth_date
missing_exact_birth_date
missing_bio
bio_without_exact_birth_date
mean_age_years
min_age_years
max_age_years
```

Age statistics should be written with enough precision to reproduce the
plotted values; display rounding belongs to the chart renderer. Rows are
ordered by basho and then by the declared division order.

The package-level default standalone output is:

```text
files/output/analysis/ages/average_age_by_division.csv
```

## Chart contract

The chart has:

- x-axis: basho, in chronological order;
- y-axis: age in years;
- trace grouping: division;
- line value: `mean_age_years`; and
- optional asymmetric y error bars:
  - upper array: `max_age_years - mean_age_years`;
  - lower array: `mean_age_years - min_age_years`.

Hover text shows:

- basho and exact Day 1;
- division;
- mean, youngest and oldest ages;
- exact-date contributors divided by total banzuke rikishi; and
- the missing-exact-date count.

The chart and its notes must call the min/max display an observed range. The
The checkbox is labelled `Min & Max` rather than the generic `Error Bars` so
that the display is not mistaken for inferential uncertainty.

## `make_site89` publication

The public page identity is:

```text
page id: average_age_by_division
navigation: Research > Age > Average age by division
route: age/average-age-by-division
title: Average Age by Division
```

The site-data path is:

```text
age/average-age-by-division/data/average_age_by_division.csv
```

Implementation touches the normal publication boundaries:

1. add `Average age by division` as a child of the existing `Age` research
   navigation category;
2. declare and promote the page in `make_site89.site_definition`;
3. add the produced artifact to `analysis.site89.producer`, its manifest and
   the validated `make_site89` bundle contract;
4. declare a chart artifact with one grouped scatter trace, division legend,
   mean y-field and min/max error fields;
5. declare the `error_bars` checkbox, defaulting to false; and
6. render a multi-trace Plotly chart using the division-selection behaviour of
   `division_stability` and the asymmetric error-bar calculation already used
   by `win_probability_by_standing`.

The existing generic grouped-line renderer is currently filterless. The
implementation may either add optional filter/error-bar support to that
renderer without changing `division_stability`, or add a small specialised
`average_age_by_division_chart` renderer. It must not copy the whole standing
win-probability renderer merely to obtain its error-bar arithmetic.

## Notes and caveats shown with the artifact

The page must state that:

- averages include only rikishi with exact birth dates;
- contributor and missing-date counts are available in hover text;
- missing birth dates may vary systematically by period or division;
- the range bars are the youngest and oldest observed rikishi, not uncertainty
  around the mean;
- age is measured on exact Day 1; and
- Maezumo is excluded because it is not a formal banzuke division.

## Validation

Automated tests must cover:

1. exact division assignment, including all Makuuchi ranks in Makuuchi;
2. exact continuous age on both sides of a birthday;
3. the 29 February convention;
4. mean, minimum and maximum for a known synthetic group;
5. missing bio and missing/partial birth-date reconciliation;
6. a group with no exact dates producing blank statistics;
7. one output row per represented `(basho, division)` group;
8. deterministic basho and division ordering;
9. failure on missing or inconsistent exact Day 1 coverage;
10. six legend-selectable division traces;
11. error bars absent when the checkbox is off;
12. asymmetric min/max bars present when it is on;
13. page, navigation, bundle-manifest and staged-file integration; and
14. no regression to the existing `division_stability` grouped-line chart.

An opt-in real-data smoke test should verify that the selected `site89` History
produces non-empty, reconciling rows and a serializable CSV. It should not be
part of the normal unit-test run because it depends on the live History and
downloaded daily-result pages.

## Non-goals

This first artifact does not provide:

- confidence intervals or standard errors for mean age;
- smoothing, trend fitting or forecasts;
- age by exact rank within a division;
- entry-route or career-stage conditioning;
- completed-career eligibility restrictions; or
- Maezumo ages.
