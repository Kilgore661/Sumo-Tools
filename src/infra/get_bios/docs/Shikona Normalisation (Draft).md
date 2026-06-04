# Shikona Normalisation (Draft)

## Status

Draft requirements note for `src.infra.get_bios` shikona normalisation work.

## Purpose

This document records the emerging public-labelling requirement for rikishi whose shikona changed over time or whose last/current shikona is not unique.

The immediate purpose is to state the requirement clearly enough that a probe can test whether the proposed rule works against the current project data. If the rule survives that probe, later documents can proceed to specification, design and implementation.

---

# 1. Requirements

## 1.1 Public Identity Labels

The system shall identify rikishi in public displays by their last/current shikona.

A rikishi id remains the internal identity key, but it shall not normally be used as the human-facing public disambiguator.

Roman-numeral succession labels such as `I`, `II`, `III` shall not be used as the general disambiguation policy. They imply a title, fame or lineage convention that is not meaningful for ordinary shikona collisions.

## 1.2 Publication-Time Catalogue

Public rikishi labels shall be resolved against the current publication catalogue, not against the date of the historical record being displayed.

The current publication catalogue is the set of rikishi identities known to the project at the time of publication, using `History` from the Jan 1958 epoch through the latest available basho, plus biographical and shikona-history data needed to identify and disambiguate rikishi whose careers or shikona histories extend before the epoch.

The project does not need to support time-traveller semantics. It is not a requirement to reproduce the name catalogue that would have been available to a reader at the time of a past basho.

Therefore, a rikishi may be displayed with their current or terminal public label even on a page showing basho before that shikona was adopted.

## 1.3 Non-Unique Last/Current Shikona

Where a last/current shikona is unique in the current publication catalogue, the public label shall be the bare shikona.

Where a last/current shikona is not unique in the current publication catalogue, the latest rikishi to hold that shikona shall use the bare shikona. Earlier rikishi with the same last/current shikona shall be identified by the shikona plus their retirement year:

```text
Shikona (YYYY)
```

The date in parentheses is a disambiguator for an earlier holder of the same last/current shikona. It is not the rikishi id, not the first-use date of the shikona, and not the date of the historical record being displayed.

## 1.4 Kirishima Example

As of publication in 2026, rikishi `12231` has not retired and no subsequent rikishi has used `Kirishima` as a last/current shikona.

Rikishi `12231`, whose first shikona was `Kiribayama` and who changed it to `Kirishima` in 2023, is therefore identified publicly as:

```text
Kirishima
```

This remains true even in records before 2023.

Rikishi `1301`, who started as `Yoshinaga`, changed his name to `Kirishima` in 1982, and retired in 1996, is an earlier holder of the same last/current shikona. He is therefore identified publicly as:

```text
Kirishima (1996)
```

This remains true even in records before 1982.

## 1.5 Historical Shikona

Historical shikona are facts about a rikishi's career. They may support biography, shikona-history display, search aliases, integrity checks or other explicit features.

Historical shikona shall not by themselves define the primary public identity label for a historical page.

## 1.6 Probe Requirement

A probe shall test the proposed rule against the current project data before implementation is treated as settled.

The probe shall report at least:

```text
same last/current shikona collisions
active/current collisions
retired collisions
missing retirement years
same shikona plus same retirement year collisions
cases where required bio or shikona-history data is absent or contradictory
```

If `Shikona (YYYY)` is not sufficient to produce unique public labels for all relevant rikishi identities, the requirement shall be revised before implementation rather than patched with an ad hoc fallback.

---

# 2. Status

A pre-specification probe now exists:

```text
src/infra/get_bios/shikona_normalisation_probe.py
```

The probe explores whether the proposed public-label rule works against the existing parsed `get_bios` data before the rule is promoted to a specification.

## 2.1 Retirement month refinement

The first probe pass found that `Shikona (YYYY)` is almost sufficient, but not quite. Some rikishi share the same last/current shikona and the same retirement year. The working rule has therefore been refined to use retirement month only when year-level disambiguation is not sufficient:

```text
Shikona (YYYY/MM)
```

The preferred month form uses a zero-padded month number, for example:

```text
Kawakami (1988/03)
```

This is still a probe result rather than a final specification decision, but it is the current working refinement.

## 2.2 Missing `Intai` investigation

The main unresolved data problem became missing `Intai` data. Some records that collide by last/current shikona do not have a parsed retirement date, so the probe cannot immediately determine whether they are genuinely active/current holders or earlier holders requiring a retirement-date suffix.

The probe now includes a demand-driven repair path. When a missing-`Intai` case is encountered, it attempts to read a cached SumoDB shikona search-result page for the relevant shikona. If the page is not already cached, the probe downloads exactly that needed page, waits one second after the request, and stores it under:

```text
files/output/infra/get_bios/shikona_normalisation_probe/intai_search_pages/
```

This is intentionally dirty-boundary prototype behaviour. The normaliser/probe does not batch-download all possible pages.

The SumoDB search-page parser expects the search-result table shape with these columns:

```text
Shikona
Heya
Shusshin
Birth Date
Highest Rank
Hatsu Dohyo
Intai
Last Shikona
```

Rows are matched by the `Rikishi.aspx?r=<rikid>` link in the `Shikona` column. Rikishi ids are normalised to the plain numeric form before comparison, so local ids with leading zeroes and SumoDB ids without leading zeroes compare correctly.

If SumoDB provides an `Intai` value in `YYYY.MM` form, the probe normalises it to `YYYY/MM` and uses it for the probe run.

## 2.3 Blank `Intai` and latest-basho confirmation

A blank `Intai` value in the SumoDB search result is not by itself accepted as proof that a rikishi is active.

The probe now loads `History` using the standard project pattern:

```text
--history-zip supplied: load from the zip-backed History
otherwise: use the live store
```

It then identifies the latest represented basho and builds the set of rikishi present in that basho.

The current probe rule is:

```text
SumoDB row has Intai YYYY.MM:
  use that as repaired Intai

SumoDB row has blank Intai and rikid is present in latest represented basho:
  treat the rikishi as active/current for this probe

SumoDB row has blank Intai and rikid is absent from latest represented basho:
  report a problem
```

The corresponding finding for the last case is:

```text
intai_fix_blank_intai_absent_from_latest_basho
```

This remains an investigation point. It may indicate missing retirement data, a SumoDB inconsistency, a local History/data issue, or a modelling problem.

## 2.4 First-token versus full-shikona key

The probe originally treated a recorded shikona as atomic. A logic issue was then found: some recorded latest shikona values contain more than one word. The probe was changed to group on the first token by default, via a named helper:

```text
public_shikona_key(...)
```

That default reflects the current hypothesis that the public-label problem may be about the leading shikona element rather than the whole recorded string.

However, full recorded latest shikona is now a serious alternative disambiguation strategy. The probe therefore has a comparison switch:

```text
--full-shikona
```

Default mode:

```text
use the first token of the recorded latest/current shikona
```

`--full-shikona` mode:

```text
use the full recorded latest/current shikona string
```

The selected mode is written to the probe summary. The design question is now explicit:

```text
Should the public normalisation key be the leading shikona element, or the full recorded latest/current shikona?
```

If full shikona removes or materially reduces collisions without producing ugly or non-public labels, the requirement may be revised to use full latest/current shikona first, reserving retirement-date suffixes for the remaining genuinely ambiguous cases.

Possible revised hierarchy:

```text
1. full latest/current shikona
2. if still ambiguous, full latest/current shikona plus retirement year
3. if year is still ambiguous, full latest/current shikona plus retirement year/month
```

This is not yet settled.

## 2.5 Current probe behaviour

The probe currently writes:

```text
files/output/infra/get_bios/shikona_normalisation_probe/summary.txt
files/output/infra/get_bios/shikona_normalisation_probe/proposed_labels.csv
files/output/infra/get_bios/shikona_normalisation_probe/latest_shikona_collisions.csv
files/output/infra/get_bios/shikona_normalisation_probe/unresolved_findings.csv
```

It can be run in first-token mode:

```text
py -m src.infra.get_bios.shikona_normalisation_probe --history-zip <history.zip>
```

or full-shikona mode:

```text
py -m src.infra.get_bios.shikona_normalisation_probe --history-zip <history.zip> --full-shikona
```

The two runs should be compared by looking at:

```text
summary.txt
unresolved_findings.csv
latest_shikona_collisions.csv
proposed_labels.csv
```

Useful comparison signals are:

```text
latest-shikona collision groups
rikishi in collision groups
unresolved findings
whether proposed labels look natural enough for public display
```

## 2.6 Current block

The investigation is temporarily blocked because SumoDB is currently unavailable. Cached pages can still be parsed, but new missing-`Intai` cases cannot be checked or repaired until SumoDB is reachable again.

When SumoDB is available, the next step is to rerun the probe in both modes, compare first-token and full-shikona results, and inspect any remaining `intai_fix_blank_intai_absent_from_latest_basho` findings.

## 2.7 Known probe fixes since the first status note

The following probe issues have been found and corrected:

```text
- SumoDB result parsing now targets the actual <thead>/<tbody> result table
  instead of scanning unrelated page-layout rows.

- Rikishi ids are compared in normalised plain numeric form, because local
  data may include leading zeroes and SumoDB links do not.

- Download timeout handling retries every 30 minutes until success.

- Non-timeout download failures now raise a diagnostic and terminate the run.

- A bogus singleton proposed-label collision bug was fixed in
  find_label_collisions().
```

These fixes are probe-quality changes, not final production design.

## 2.8 Status before specification

The probe is now useful enough to inform the requirement, but the requirement is not yet ready to promote to a specification.

Open questions before specification:

```text
1. Is the public key the first token or the full recorded latest/current shikona?
2. Do the remaining blank-Intai-but-not-latest-basho cases represent data errors,
   SumoDB inconsistencies, or a flaw in the model?
3. Is retirement month sufficient for all remaining same-year collisions?
4. Are the generated labels acceptable as public-facing names?
```

Once those questions are answered, this draft can be rewritten from a progress note into a stable requirement/specification document.
