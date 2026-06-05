# Shikona Resolution

## Purpose

The system needs a deterministic mapping from rikishi identity to public display shikona:

```text
rikid -> public shikona
```

This mapping is needed wherever a rikishi is identified by shikona in public-facing output.

The central principle is conservative:

> The normal public shikona is the shikona recorded in History.

That History shikona should be preserved unless it is not sufficient to identify the rikishi unambiguously under the system’s publication assumptions.

## Current requirement

Let `H` be the rikishi’s shikona as recorded in History.

The public shikona rule is:

```text
If H is unique:
    public shikona = H

If H is not unique and the rikishi has not retired:
    public shikona = H

If H is not unique and the rikishi has retired:
    public shikona = full shikona
```

Equivalently:

```python
public_shikona = history_shikona

if history_shikona_is_non_unique and rikishi_is_retired:
    public_shikona = full_shikona
```

The earlier formulation included the phrase “when disambiguation is needed”. We have decided not to implement a separate catalogue-specific ambiguity test. For the purposes of this system, a retired rikishi with a non-unique History shikona is treated as needing disambiguation.

## Why active rikishi keep the History shikona

If a History shikona is non-unique, active rikishi still keep the History shikona.

This preserves the normal contemporary public name for current rikishi. The disambiguation burden is placed on retired rikishi instead, because duplicate historical names are mainly a problem when identifying past rikishi in public catalogue output.

## Chosen disambiguator

When a retired rikishi with a non-unique History shikona needs disambiguating, the system shall use the rikishi’s full shikona.

This is the chosen production behaviour.

## Status of the normalisation/probe code

The existing shikona normalisation code in `infra/get_bios` is prototype and legacy code.

It should not be treated as production implementation logic. Its value is as reference material: it records the investigation into possible disambiguators and the evidence that led to the current rule.

The production resolver should be much simpler than the probe code. It should not attempt to reproduce the exploratory normalisation workflow.

## Probe findings

The prototype investigation considered several possible disambiguators.

### `rikid`

`rikid` is technically effective because it is unique.

However, it is unsuitable for public-facing output. It is an internal identifier, not a user-natural name. Using it would solve the machine problem while producing ugly public labels.

Conclusion: reject as public disambiguator.

### Hatsu date

The hatsu date was considered as a possible historical disambiguator.

It has two problems:

1. It is incomplete for the data we need to support.
2. It is not especially natural for users reading public-facing output.

Even where available, a hatsu date is not the form most users would expect as part of a rikishi display name.

Conclusion: reject as public disambiguator.

### Intai date

The intai date is more meaningful than hatsu for retired rikishi, because retirement is directly related to the population being disambiguated.

However, the probe showed that intai date is not sufficient.

Important findings to preserve:

1. Some rikishi have missing intai dates.
2. Some rikishi with the same History shikona retired in the same year.
3. In at least one case, rikishi with the same History shikona retired in the same year and month.

This matters because it means that even a year-month intai disambiguator is not guaranteed to distinguish all relevant duplicate-name retired rikishi. It is also sometimes ugly in public output.

Conclusion: reject as public disambiguator.

### Full shikona

Full shikona is user-facing, name-like, and natural in public output.

The probe validated it as an effective disambiguator for the duplicate retired-shikona cases under consideration. It avoids exposing internal identifiers and avoids relying on incomplete or insufficient dates.

Conclusion: use full shikona as the production disambiguator.

## Required production inputs

The production resolver needs reliable access to the following data:

```text
rikid
History shikona
full shikona
retirement status
whether the History shikona is unique
```

The duplicate test should be global over History shikona values, not local to a single output page.

## Expected production shape

The production implementation should expose a deterministic resolver, for example:

```python
def public_shikona_for(rikid: Rikid) -> str:
    ...
```

or a precomputed mapping:

```python
dict[rikid, public_shikona]
```

The implementation should be pure or effectively pure: given the same source data, it should always produce the same public shikona mapping.

## Pseudocode

```python
def build_public_shikona_map(rikishi_records):
    history_name_counts = Counter(
        record.history_shikona
        for record in rikishi_records
    )

    public_shikona_by_rikid = {}

    for record in rikishi_records:
        history_shikona = record.history_shikona
        is_duplicate = history_name_counts[history_shikona] > 1

        if is_duplicate and record.is_retired:
            public_shikona = record.full_shikona
        else:
            public_shikona = history_shikona

        public_shikona_by_rikid[record.rikid] = public_shikona

    return public_shikona_by_rikid
```

## Open implementation questions

The rule is settled, but the implementation still needs to decide:

1. Where the resolver should live.
2. Which existing data model owns `history_shikona`, `full_shikona`, and `is_retired`.
3. Whether the mapping is computed at build time, loaded from an artefact, or exposed through an API.
4. What tests should lock down duplicate-name retired cases.
5. Whether missing `full_shikona` should be treated as a hard data error.

## Recommended tests

The implementation should include tests for at least the following cases:

### Unique History shikona

```text
H is unique
rikishi may be active or retired
result = H
```

### Duplicate History shikona, active rikishi

```text
H is shared
rikishi is active
result = H
```

### Duplicate History shikona, retired rikishi

```text
H is shared
rikishi is retired
result = full shikona
```

### Duplicate retired rikishi with same intai year

This case records why intai year is not an acceptable disambiguator.

```text
same H
both retired
same intai year
result = full shikona for each retired rikishi
```

### Duplicate retired rikishi with same intai year and month

This case records the strongest known failure of intai-date disambiguation.

```text
same H
both retired
same intai year and month
result = full shikona for each retired rikishi
```

### Missing intai date

This case records why intai date cannot be required.

```text
same H
retired rikishi has missing intai date
result = full shikona
```

## Non-goals

The production resolver should not:

1. Use `rikid` in public-facing labels.
2. Use hatsu date as the public disambiguator.
3. Use intai date as the public disambiguator.
4. Re-run the legacy probe workflow during normal publication.
5. Implement page-specific or catalogue-specific ambiguity checks.

## Current status

The investigation phase is complete enough to choose the production rule.

The chosen rule is:

> Preserve the History shikona by default. If the History shikona is non-unique and the rikishi is retired, use full shikona.

The next task is implementation: add a small deterministic resolver, wire it into public-facing output generation, and add regression tests for the duplicate retired-shikona cases identified by the probe.

