# Ages analysis

This package contains analyses based on rikishi birth dates and age.

## Average age by division

`average_age_by_division.py` writes one row per represented basho and formal
division. It reports the mean, youngest and oldest continuous ages on the exact
civil date of Day 1, together with exact-birth-date coverage counts.

```powershell
python -m src.analysis.ages.average_age_by_division
```

The default output is
`files/output/analysis/ages/average_age_by_division.csv`. Exact Day 1 dates are
currently recovered from downloaded daily-result HTML. This is deliberately
precise, but properly belongs in a future first-class parsed basho calendar.

The standalone producer can use a complete 1958+ History via `--history-zip`,
provided exact Day 1 evidence is available for every represented basho. The
public make_site89 artifact currently uses the site's selected 1989+ History.
Publishing the longer series is parked future work: it should pass a separate
full History to the age artifact rather than changing the Elo-89 bundle's
principal history boundary.

## Birth-date coverage by basho

`birth_date_coverage.py` audits whether age-based historical analysis is
possible for each represented banzuke. It writes one row per basho containing:

- the number of rikishi on the banzuke;
- the number with usable exact birth dates;
- the number without usable exact birth dates;
- how many missing exact dates are caused by an absent bio; and
- how many are caused by a bio with a missing or partial birth date.

Run it from the repository root:

```powershell
python -m src.analysis.ages
```

The default output is:

```text
files/output/analysis/ages/birth_date_coverage_by_basho.csv
```

An exact birth date is a full calendar date loaded through `BioStore`.
Year-only source values are deliberately treated as unavailable. Rikishi with
no bio record are also included in `missing_exact_birth_date`.

An opt-in real-data smoke test loads the live History, persisted bio store and
downloaded exact basho dates. It checks the coverage and average-age analyses
for reconciliation and verifies both CSVs in a temporary directory:

```powershell
python -m src.analysis.ages.smoke_test
```

It is deliberately separate from the normal unit-test suite because it depends
on the published live store.
