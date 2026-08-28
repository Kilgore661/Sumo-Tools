# Pre-1989 Bout-Data Completeness and Rating Persistence

## Purpose and status

This note records the result of the bout-data completeness investigation at the
start of Equelo2 work. It supplies the evidential basis for retaining a
rikishi's most recently informed rating across gaps in the represented result
record.

It is an **established data finding plus a modelling rationale**, not an
experiment showing how missing data affect rating accuracy. The project has not
measured, and does not currently plan to measure, rating variance or predictive
degradation as a function of the amount or duration of missing historical data.

The reproducible analysis package is:

```text
src/analysis/bout_data_completeness
```

Its generated outputs are written to:

```text
files/output/analysis/bout_data_completeness
```

## The question that led to the audit

Equelo2 is intended to run over the represented history from 1958 rather than
starting afresh in January 1989. Elo-89 supplies an initial rating by literal
chii. If a lower-division rikishi appears in an eligible recorded bout, the
full-history model can update that rating. The question is what to do when the
same rikishi then has no represented results for one or more basho.

The adopted direction is to preserve the most recently informed rating while
the rikishi remains on the banzuke. Reinitialising from chii after every result
gap would discard evidence already obtained. Under a persistent-rating model,
any eligible result contributes information: even one represented result in a
long interval is more information than none. This is a rationale for retaining
state, not a claim that one old result is highly informative or that skill does
not change over time.

Before relying on that argument, the project needed to know whether historical
lower-division results were occasional isolated observations in an otherwise
empty archive, or part of a substantial but incomplete record.

## Sources and definitions

The audit combines three existing project sources:

- the `History` banzuke, normally read from the live store, supplies every
  actual literal chii and rikishi identity in each selected basho;
- cached SumoDB `Rikishi.aspx` career rows supply the daily `hoshi` symbols; and
- the parsed BioStore supplies `Intai`, the retirement basho.

The audited interval contains 408 represented basho from 1958/01 through
2026/03. Chii annotations are preserved literally. A chii absent from a
banzuke contributes no observation.

For this 1958-forward scope, an individual rikishi-basho record is:

- **complete** when it contains exactly 15 daily `hoshi` symbols and none is
  `hoshi_empty`;
- **partial** when it contains some known daily symbols but is not complete;
- **absent** when it contains no daily symbols; and
- **retirement-exempt** when BioStore `Intai` equals the basho.

A division-basho is complete only when every non-retirement-exempt chii in that
division has a complete individual record. It is partial when some but not all
of those records are complete, and has no records when none contains known
daily information.

This is intentionally a strict definition. One incomplete rikishi makes the
division-basho incomplete.

## Headline results

### Complete basho across the full interval

| Division | No records | Partial | Complete | Complete out of 408 | Continuous complete from |
|---|---:|---:|---:|---:|---:|
| Makuuchi | 0 | 0 | 408 | 100.0% | 1958/01 |
| Juryo | 0 | 0 | 408 | 100.0% | 1958/01 |
| Makushita | 0 | 53 | 355 | 87.0% | 1966/11 |
| Sandanme | 17 | 41 | 350 | 85.8% | 1973/03 |
| Jonidan | 32 | 37 | 339 | 83.1% | 1986/09 |
| Jonokuchi | 44 | 18 | 346 | 84.8% | 1992/07 |

Every division therefore has at least 339 completely represented basho out of
408. The result record is incomplete in historically important places, but it
is not well described as generally sparse.

### The pre-1989 interval itself

There are 186 represented basho from 1958/01 through 1988/11.

| Division | No records | Partial | Complete | Complete out of 186 |
|---|---:|---:|---:|---:|
| Makuuchi | 0 | 0 | 186 | 100.0% |
| Juryo | 0 | 0 | 186 | 100.0% |
| Makushita | 0 | 53 | 133 | 71.5% |
| Sandanme | 17 | 41 | 128 | 68.8% |
| Jonidan | 32 | 37 | 117 | 62.9% |
| Jonokuchi | 44 | 17 | 125 | 67.2% |

Even the least complete lower division, Jonidan, has complete records for 117
of the 186 pre-1989 basho. Partial records add further evidence beyond those
complete basho.

### How sparse are the partial basho?

The label *partial* covers both a nearly complete division with one exception
and a division with very little represented information. To expose that
difference, the audit counts 15 expected daily records for each non-retired
rikishi in partial basho. Retirement-basho rikishi are excluded from both the
numerator and denominator.

| Division | Pre-1989 missing / expected daily records | Known | Missing |
|---|---:|---:|---:|
| Makushita | 115,110 / 141,120 | 18.431% | 81.569% |
| Sandanme | 106,111 / 118,920 | 10.771% | 89.229% |
| Jonidan | 79,345 / 126,930 | 37.489% | 62.511% |
| Jonokuchi | 8,214 / 11,070 | 25.799% | 74.201% |

Thus the early partial basho are often genuinely sparse. This does not negate
the larger result: each lower division also has between 117 and 133 completely
represented pre-1989 basho, and its partial basho contain additional usable
observations.

## What the audit does and does not measure

The density figures concern **daily source records**, not missing bout outcomes.
For sekitori, fifteen nominal bout days make the relationship comparatively
direct. For lower-division rikishi, a dash or `hoshi_yasumi` can mean either a
scheduled non-bout day or kyujo. The source does not always distinguish those
cases. Consequently, the exact number of missing lower-division bout outcomes
cannot be recovered from these career-row symbols alone.

The audit therefore establishes:

- when complete and partial daily records exist;
- how completeness changes by division and date;
- the density of known daily information within partial basho; and
- that substantial lower-division evidence exists before 1989.

It does **not** establish:

- the exact number of missing lower-division bout outcomes;
- how missingness changes the variance, bias or calibration of ratings;
- how quickly an old rating becomes stale as skill changes;
- that persistence is superior under every possible forgetting or
  reinitialisation policy; or
- predictive validation of the eventual Equelo2 construction.

Retirement is another deliberate boundary. When BioStore `Intai` equals the
basho, an incomplete record is exempted because the rikishi need not have
completed the nominal schedule. The audit does not try to reconstruct the day
of retirement or decide how many pre-retirement bouts ought to have occurred.

## Ranked-banzuke gaps are not necessarily permanent departures

It is possible for a rikishi to appear on two banzuke at a ranked, or "pro",
chii (`Jk` or above) while having no ranked chii on one or more intervening
banzuke. Absence from one banzuke therefore does not by itself establish
retirement or permanent departure.

An audit of the January 1958 through July 2026 History found 679 such gap events
among 590 rikishi. The History contains 9,071 distinct rikishi with at least one
ranked-banzuke appearance, so the affected population is 6.504% of all observed
ranked rikishi. Of the 679 episodes, 666 (98.085%) are specifically
`Jk -> unranked -> Jk`; excluding Sokokurai gives 666 of 678 (98.230%). The
ranked History deliberately excludes the administrative
categories needed to explain them, so the audit compared each gap with the
downloaded SumoDB rikishi career table. Across the intervening basho, those
tables contain:

The latest observed returns are on the July 2026 banzuke: Kyokuhayate returns
at `Jk17w` after last appearing at `Jk16e` in November 2025 and spending three
basho at `Bg`; Dewanowaka returns at `Jk19w` after `Jk16w` in March 2026 and
`Bg` in May 2026.

Excluding Sokokurai, the last ranked chii before the 678 gaps are distributed
as follows:

| Last ranked division | Gap events | Percentage |
|---|---:|---:|
| `Jk` | 668 | 98.525% |
| `Jd` | 9 | 1.327% |
| `Sd` | 1 | 0.147% |

Thus the practical edge case is overwhelmingly a Jonokuchi phenomenon, but not
exclusively so. The 668 pre-gap Jonokuchi chii range from `Jk1` to `Jk70`; their
median rank number is 18 and the most frequent is `Jk14` (31 events). Because
the size of Jonokuchi changes substantially over the historical interval, those
raw numbers do not measure a stable percentile or prove that every rikishi had
reached the numerical bottom of the division before disappearing.

The ten non-Jonokuchi departures, excluding Sokokurai, are:

| Rikishi at departure | Last ranked appearance | Ranked return |
|---|---:|---:|
| Matsuokayama | 1966/09 `Sd51w` | 1967/09 `Jk16w` |
| Beppu | 1964/05 `Jd87e` | 1966/07 `Jk22w` |
| Nishimura | 1965/03 `Jd131e` | 1965/09 `Jk25w` |
| Akao | 1965/09 `Jd125e` | 1966/01 `Jk20e` |
| Fukuazuma | 1967/01 `Jd80w` | 1968/01 `Jk8e` |
| Fukusoyama | 1967/01 `Jd70w` | 1967/07 `Jk16w` |
| Suonada | 1968/05 `Jd49e` | 1969/09 `Jk2w` |
| Akinoyama | 1970/07 `Jd54e` | 1973/03 `Jk12e` |
| Kitanomine | 1976/07 `Jd102e` | 1977/01 `Jk16w` |
| Yado | 1978/09 `Jd62w` | 1979/01 `Jk16e` |

`Mz`, `Bg` and `Kg` are not ranks or chii. They are unranked source statuses;
none belongs to the professional banzuke domain `Jk` and above. `Sj` is likewise
treated here as an unranked historical entry status, not as a chii.

| SumoDB status | Intervening basho |
|---|---:|
| `Bg` (Banzuke-gai) | 739 |
| `Mz` (Mae-zumo) | 663 |
| `Kg` (Out of Kyokai) | 67 |
| `Sj` (Shinjo) | 6 |
| `??` (SumoDB's unresolved value) | 2 |

In 678 of the 679 events, every intervening basho has an explicit `Bg`, `Mz`,
`Kg` or `Sj` status. The sole source-level ambiguity is Muraishi:

```text
1970/03 Mz -> 1970/05 Jk8e -> 1970/07 ?? -> 1970/09 ??
-> 1970/11 Mz -> 1971/01 Jk4w
```

The two `??` values belong to SumoDB, not to the parser. Because the same career
row explicitly records `Mz` immediately before Muraishi's return, he is included
among the observed gap-and-return cases rather than treated as evidence of a
ranked banzuke omission.

Most returns have an intervening `Mz` status and reappear at `Jk`. Return above `Jk` is
nevertheless possible. Tamabungo and Tochinoya each have an intervening `Sj`
status in January 1959 and return at `Jd` in March 1959. The notable modern case
is Sokokurai:

```text
2011/01 M16e -> 12 basho Kg -> 2013/05 Bg -> 2013/07 M15w
```

SumoDB uses `Bg` for someone outside the ranked banzuke but still within the
Kyokai's entry or return machinery, and `Kg` for "Out of Kyokai". Nine other
post-1958 careers contain `Kg` gaps, all between 1966 and 1977; unlike
Sokokurai, each goes through `Mz` and returns at `Jk`:

| Rikishi | Last ranked appearance | Administrative gap | Ranked return |
|---|---:|---|---:|
| Matsuoka | 1966/09 `Sd51w` | 4 `Kg`, then `Mz` | 1967/09 `Jk16w` |
| Fukusoyama | 1967/01 `Jd70w` | 1 `Kg`, then `Mz` | 1967/07 `Jk16w` |
| Fukuazuma | 1967/01 `Jd80w` | 4 `Kg`, then `Mz` | 1968/01 `Jk8e` |
| Fukushima | 1967/09 `Jk5w` | 9 `Kg`, then `Mz` | 1969/07 `Jk9e` |
| Tamanofuji | 1968/01 `Jk16e` | 2 `Bg`, 13 `Kg`, then `Mz` | 1970/11 `Jk1e` |
| Wakayutaka | 1968/05 `Jd49e` | 6 `Kg`, then `Mz` | 1969/09 `Jk2w` |
| Chiyominato | 1970/07 `Jd54e` | 14 `Kg`, then `Mz` | 1973/03 `Jk12e` |
| Fukunobori | 1974/11 `Jk9w` | 3 `Kg`, then `Mz` | 1975/09 `Jk17e` |
| Kitanomine | 1976/07 `Jd102e` | 1 `Kg`, then `Mz` | 1977/01 `Jk16w` |

These are lifecycle facts, not yet a final model decision. They establish the
edge case that a rating system must address: a missing ranked-banzuke appearance
cannot safely be equated with permanent departure. The current Equelo2 baseline
archives the rating during the gap, but this finding alone does not decide
whether the definitive model should persist, reset or otherwise adjust it. The
small affected fraction and overwhelming concentration in `Jk -> Jk` episodes
make a small aggregate effect plausible, especially because an archived rating
is inert during the absence. They do not establish that the effect on every
returnee, on other ratings, or on predictions is insignificant; that would
require a persistence-versus-reset comparison.

Nor does a return at `Jk` establish that the rikishi now has ordinary
Jonokuchi ability. In these careers `Jk` is commonly the procedural destination
after an unranked status and `Mz`, rather than a competitive assessment derived
from the rikishi's immediately preceding bouts. A former Sandanme rikishi might
therefore return with a persisted rating well above the entrant prior associated
with his new `Jk` chii without the persisted value necessarily being "too high".
The old rating is evidence about ability before the absence; the return chii is
evidence about the administrative route back. Neither tells us quantitatively
how injury, inactivity, age or other circumstances changed ability during the
gap.

The model's Jonokuchi chii-to-rating relationship fails an important
face-validity test: across the deep-Jonokuchi region, fitted ratings increase as
the formal chii gets lower. In that strong and directly relevant sense, the
model does not work in `Jk`; its exact-`Jk` values cannot be interpreted as a
credible ordered ability scale. This does not show that Elo updates on
Jonokuchi bout results contain no information--sub-sekitori Elo has predictive
signal in aggregate--but it does mean that resetting a returnee to an exact
`Jk` prior is not an evidence-based correction for rating staleness. Tranche 1
also found that broad division membership supplied more useful initialisation
information than exact lower-division chii.

Persistence is consequently a carry-forward convention under ignorance, not a
claim that ability remains constant while absent. If the carried rating is too
high or too low, later observed results allow Elo to correct it and transfer the
corresponding points. The numerical size and duration of that local disturbance,
and any propagation to other rikishi, remain unmeasured.

## Why the findings support rating persistence

The evidence supports a restrained argument:

1. Pre-1989 lower-division observations are not merely isolated bridge bouts.
   Complete division-wide records occur in most pre-1989 basho, and partial
   basho add further observations.
2. Coverage improves at different times for different divisions rather than
   changing everywhere at one January 1989 boundary.
3. A rikishi can therefore accumulate genuine rating information, pass through
   a gap in represented results, and later contribute or receive more rating
   information.
4. Reinitialising after each gap would erase that accumulated evidence.
   Preserving the latest rating retains it. Even a very occasional eligible
   result is evidence that an unconditional reinitialisation would discard.
5. As lower-division coverage becomes more complete, persisted ratings receive
   progressively more direct support without requiring a discontinuous model
   restart.

This justifies persistence as the working Equelo2 policy. It does not quantify
the policy's predictive benefit. That distinction should remain explicit in
technical and public accounts.

## Reproduction

Run:

```powershell
python -m src.analysis.bout_data_completeness
```

The entry point prefers the live History store, uses the parsed BioStore for
`Intai`, reads cached Rikishi pages for daily symbols, records source identities
in `manifest.json`, and writes:

- `basho_chii_record_availability.csv`;
- `basho_division_record_availability.csv`;
- `division_record_availability_summary.csv`; and
- `findings.md`.

The generated files are the numerical authority. This tracked note records the
interpretation and claim boundary needed by the Equelo2 story.
