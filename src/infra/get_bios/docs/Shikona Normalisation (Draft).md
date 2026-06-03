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

The first probe pass found that `Shikona (YYYY)` is almost sufficient, but not quite. Some rikishi share the same last/current shikona and the same retirement year. The working rule has therefore been refined to use retirement month only when year-level disambiguation is not sufficient:

```text
Shikona (YYYY/MM)
```

The preferred month form uses a zero-padded month number, for example:

```text
Kawakami (1988/03)
```

The remaining unresolved problem is missing `Intai` data. Some records that collide by last/current shikona do not have a parsed retirement date, so the probe cannot yet determine whether they are genuinely active/current holders or earlier holders requiring a retirement-date suffix.

The missing-`Intai` cases must be understood or repaired before this requirement can advance cleanly to specification.
