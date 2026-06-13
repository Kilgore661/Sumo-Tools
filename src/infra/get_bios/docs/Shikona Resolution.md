# Shikona Resolution

## Purpose

The system needs a deterministic mapping from rikishi identity to public display shikona:

```text
rikid -> public shikona
```

This mapping is needed wherever a rikishi is identified by shikona in public-facing output.

The central principle is conservative:

> The normal public shikona is the shikona recorded in History.

That History shikona should be preserved unless it is not sufficient to identify the rikishi unambiguously.

## Current requirement

Let `H` be the rikishi's shikona as recorded in History.

History currently records single-word shikona. That is the context problem this work addresses: public output sometimes needs a fuller public name without changing History itself.

The public shikona rule is:

```text
If H is unique:
    public shikona = H

If H is not unique and the rikishi is the latest holder of H:
    public shikona = H

If H is not unique and the rikishi is an earlier holder of H:
    public shikona = full shikona
```

Equivalently:

```python
public_shikona = history_shikona

if history_shikona_is_non_unique and rikishi_is_not_latest_holder_of_that_shikona:
    public_shikona = full_shikona
```

The important interpretation is that retirement is not the deciding condition. The latest rikishi to use a History shikona keeps the handle, whether or not that rikishi has retired.

For example, Hakuho Sho is the latest holder of the History shikona `Hakuho`. Even though he has retired, he remains the public `Hakuho`. Earlier holders of `Hakuho` need disambiguation, not him.

## Current resolved policy

The production policy now uses a hybrid rule:

```text
Group by History shikona H.

The latest holder of H owns the bare public label H.

Earlier holders first try their maximal shikona M from BioStore when M differs
from H.

Earlier holders use an Intai suffix when:
  - M is not distinct from H;
  - M collides with another earlier-holder candidate;
  - M collides with any latest-holder bare History shikona.

The suffix is YYYY unless YYYY is insufficient, in which case it is YYYY/MM.
```

This preserves the latest-holder rule while using shikona text where possible.
Brevity is not the main concern for earlier holders; unambiguous public labels
are.

Known examples under the current rule:

```text
RikId(1123)  Hakuho Sho          -> Hakuho
RikId(8206)  Hakuho              -> Hakuho (1975)
RikId(9111)  Abe Kenichiro       -> Abe
RikId(9048)  Abe                 -> Abe (1973)
RikId(2103)  Takahashi Hirokazu  -> Takahashi Hirokazu
RikId(7237)  Takahashi Shinichi  -> Takahashi Shinichi
```

The implementation is isolated in:

```text
src/infra/get_bios/FullShikonaStore.py
```

`FullShikonaStore` is a publication-time entity parallel to `History`. This is
intentional containment of a modelling hack: the information probably belongs
in or beside the History-building pipeline in the long run, but this rollout
does not mutate `History`.

The store is built from:

```text
History
BioStore / rikishi_bios.json
Rikishi.aspx shikona-search CSV
```

The Career Comparisons dropdown now receives full shikona through the existing
`trajectory_master.json` artifact rather than through new JavaScript plumbing.

On a fresh source-cache rebuild, the Career Comparisons artifact was checked:

```text
labels 9064
unique 9064
duplicates 0
```

Historical sections below record the investigation path. Some earlier
conclusions, especially the rejection of Intai as a general disambiguator and
the insufficiency of full shikona alone, should now be read as background
rather than the final production policy.

## Why the latest holder keeps the History shikona

If a History shikona is non-unique, the latest holder is the rikishi most users will expect to be identified by the bare handle.

This preserves the normal public meaning of the shikona. The disambiguation burden is placed on earlier holders instead.

The earlier retired-vs-active formulation was a useful approximation, but it was not the real rule. A retired rikishi can still be the latest holder of a shikona.

This latest-holder rule is the settled working principle even though the
residual disambiguator is not settled. In short: the most recent `X` gets to be
public `X`; earlier `X` holders must be distinguished. That creates a
publication-maintenance responsibility: as new rikishi take old shikona, the
catalogue-wide resolver must be rebuilt so the new latest holder can inherit
the bare label and displaced earlier holders can receive disambiguated labels.

## Chosen disambiguator

When an earlier holder of a non-unique History shikona needs disambiguating, the system shall use the rikishi's full shikona.

This is the current implemented behaviour, but it is now known not to be a
complete disambiguation policy.

## Update: full shikona is not sufficient

The full-shikona rule has a counterexample.

Hakuho Sho, `RikId(1123)`, is the latest holder of the History shikona
`Hakuho`, so under the latest-holder rule he remains public `Hakuho`.

The earlier Hakuho, `RikId(8206)`, retired in 1975. His full shikona is also
just `Hakuho`. Therefore the current rule cannot distinguish these two rikishi:
the earlier holder's "full" shikona collapses back to the same public label as
the latest holder's bare History shikona.

This does not mean the system should fall back to public `rikid` suffixes.
`rikid` remains an internal identity key and an ugly public disambiguator. The
open policy question is how often full-shikona collisions occur, what kinds of
cases they represent, and what non-`rikid` public disambiguator should be used
when full shikona is not enough.

The strongest new theory is that the ambiguity is partly a romanisation
problem. If a shikona is treated as the kanji string used to write it, then:

1. The first romanised shikona word, represented as kanji, should be unique
   within a single basho.
2. The full shikona, represented as kanji, may be unique across the whole
   catalogue.
3. Where the first-word kanji is not unique across basho, the second-word kanji
   may provide the natural disambiguator.

This should be tested before adopting a suffix-like residual disambiguator. It
may require extending the `get_bios` scrape/parser contract: the current parsed
bio cache stores romanised `Shikona` values, and does not expose a kanji
shikona field.

Other plausible candidates are already available from `get_bios`:

1. `Shusshin`, the rikishi's region of origin.
2. Former shikona from the rikishi's parsed shikona history.

Both are public-facing biographical facts rather than internal keys. Neither
should be adopted without a probe: `Shusshin` values can be long, foreign,
historical or shared, and former-shikona labels may be absent, unfamiliar, or
still non-unique. The next investigation should measure these candidates across
the full cache and inspect their public readability.

## Status of the normalisation/probe code

The existing shikona normalisation code in `infra/get_bios` is prototype and legacy code.

It should not be treated as production implementation logic. Its value is as reference material: it records the investigation into possible disambiguators and the evidence that led to the current rule.

The production resolver should be much simpler than the probe code. It should not attempt to reproduce the exploratory normalisation workflow.

## Probe findings

The prototype investigation considered several possible disambiguators.

The recurring result is that disambiguation itself is the hard problem. Every
candidate below either fails to identify all required rikishi, depends on data
that is incomplete or stale, creates ugly public text, or needs more source data
than the current parsed cache exposes. `rikid` is the reliable machine answer,
but not an acceptable public label.

### `rikid`

`rikid` is technically effective because it is unique.

However, it is unsuitable for public-facing output. It is an internal identifier, not a user-natural name. Using it would solve the machine problem while producing ugly public labels.

Conclusion: reject as public disambiguator.

### Hatsu date

The hatsu date was considered as a possible historical disambiguator.

It was rejected because it did not provide a suitable public disambiguator. It is incomplete for the data we need to support and is not especially natural for users reading public-facing output.

Conclusion: reject as public disambiguator.

### Intai date

The intai date is meaningful for retired rikishi, but the probe showed that it is not sufficient.

Important findings to preserve:

1. Some rikishi have missing intai dates.
2. Some rikishi with the same History shikona retired in the same year.
3. In at least one case, rikishi with the same History shikona retired in the same year and month.

This matters because even a year-month intai disambiguator is not guaranteed to distinguish all relevant duplicate-name rikishi. It is also sometimes ugly in public output.

Conclusion: reject as public disambiguator.

### Full shikona

Full shikona is user-facing, name-like, and natural in public output.

The original probe validated it as an effective disambiguator for the duplicate
History shikona cases then under consideration. It avoids exposing internal
identifiers and avoids relying on incomplete or insufficient dates.

Later review found the Hakuho counterexample: `RikId(1123)` is public `Hakuho`
as latest holder, while the earlier `RikId(8206)` also has full shikona
`Hakuho`.

Conclusion: full shikona is the current implemented disambiguator, but it is
not a complete policy. Research the frequency and shape of full-shikona
collisions before choosing the next public disambiguator.

### Kanji shikona

Kanji shikona is the strongest current candidate for repairing the policy
without exposing internal ids or adding artificial suffixes.

The theory is that much of the ambiguity exists in the romanised label, not in
the name as written. A public shikona could be understood as the kanji string
used to write it:

```text
first-word kanji
full-shikona kanji
first-word kanji plus second-word kanji where needed
```

This may solve both the per-basho identity problem and the cross-catalogue
disambiguation problem more naturally than `Shusshin`, former names, or dates.

The immediate practical question is data availability. The current
`get_bios` parser persists romanised `Shikona` history only. Test whether the
raw SumoDB `Rikishi.aspx` pages expose kanji shikona reliably, then extend the
parser/cache if they do.

Conclusion: investigate before choosing any residual suffix policy.

### Shusshin

`Shusshin` is a plausible residual disambiguator for cases where full shikona
does not distinguish rikishi.

It has attractive properties: it is public, biographical, and already parsed in
`get_bios`. It may read naturally in labels such as:

```text
Hakuho (Yamagata-ken)
```

The cost is that `Shusshin` is not a simple controlled vocabulary. Values may be
long, may include historical/current municipality chains, and may still collide.

Conclusion: investigate as a candidate residual disambiguator.

### Former shikona

A rikishi's shikona history is another plausible residual disambiguator.

It has attractive properties when a former name is distinctive and familiar. It
also stays within the naming domain rather than introducing dates or geography.

The cost is that some rikishi may have no useful former shikona, a former
shikona may be less recognizable than an origin, and former names may themselves
collide.

Conclusion: investigate as a candidate residual disambiguator.

## Required production inputs

The production resolver needs reliable access to the following data:

```text
rikid
History shikona
full shikona
latest holder of each History shikona
whether the History shikona is unique
```

History owns the normal shikona and the latest-holder calculation.

`get_bios` / `BioStore` owns the full shikona used for disambiguation.
It also owns candidate residual disambiguators such as `Shusshin` and former
shikona history.

The duplicate test should be global over History shikona values, not local to a single output page.

## Expected production shape

The production implementation should expose a deterministic resolver, for example:

```python
def make_public_shikona(history: History) -> dict[RikId, Shikona]:
    ...
```

The public API should hide `BioStore` from publication callers. `get_bios` owns
the cache read. Given the same History and the same parsed `get_bios` cache, it
should always produce the same public shikona mapping.

## Pseudocode

```python
def build_public_shikona_map(history, bios):
    history_shikona_by_rikid = make_history_shikona_by_rikid(history)
    latest_holder_by_history_shikona = make_latest_holder_by_history_shikona(history)
    history_name_counts = Counter(history_shikona_by_rikid.values())

    public_shikona_by_rikid = {}

    for rikid, history_shikona in history_shikona_by_rikid.items():
        is_duplicate = history_name_counts[history_shikona] > 1
        is_latest_holder = latest_holder_by_history_shikona[history_shikona] == rikid

        if is_duplicate and not is_latest_holder:
            public_shikona = bios[rikid].latest_shikona()
        else:
            public_shikona = history_shikona

        public_shikona_by_rikid[rikid] = public_shikona

    return public_shikona_by_rikid
```

The production module may keep an explicit-BioStore helper for tests or cache
checks, but normal consumers should call `make_public_shikona(history)`.

## Useful tests

The implementation should include tests for at least the following cases.

### Unique History shikona

```text
H is unique
result = H
```

### Duplicate History shikona, latest holder

```text
H is shared
rikishi is the latest holder of H
result = H
```

This should hold whether the latest holder is active or retired.

### Duplicate History shikona, earlier holder

```text
H is shared
rikishi is an earlier holder of H
result = full shikona
```

This is the current implemented behaviour, not a uniqueness guarantee.

### Full-shikona collision

This case records the known gap in the current policy.

```text
H is shared
latest holder result = H
earlier holder full shikona is also H
result = unresolved policy issue
```

Known example:

```text
RikId(1123): Hakuho Sho, latest holder, public Hakuho
RikId(8206): earlier Hakuho, full shikona Hakuho
```

### Latest holder is retired

This case records the corrected interpretation.

```text
H is shared
latest holder of H is retired
latest holder result = H
earlier holder result = full shikona
```

### Intai-date failures remain documented

These cases record why intai date is not an acceptable disambiguator.

```text
same H
missing intai date, or same intai year, or same intai year and month
result = full shikona for earlier holders; intai date is not used
```

## Non-goals

The production resolver should not:

1. Use `rikid` in public-facing labels.
2. Use hatsu date as the public disambiguator.
3. Use intai date as the public disambiguator.
4. Re-run the legacy probe workflow during normal publication.
5. Implement page-specific or catalogue-specific ambiguity checks.
6. Modify History directly to store full shikona.

The current non-goal on hatsu/intai dates does not settle the residual
full-shikona collision policy. It only records that date suffixes have already
been rejected as the general public disambiguator.

## Current status

The first production implementation exists, but the policy is no longer
considered settled.

The implemented rule is:

> Preserve the History shikona by default. If the History shikona is non-unique, the latest holder keeps the History shikona and earlier holders use full shikona.

This rule is known to fail when an earlier holder's full shikona is identical
to the latest holder's public History shikona, as in the Hakuho `1123` / `8206`
case. The next policy step is to research how often this occurs and decide on a
public, non-`rikid` disambiguator for those residual collisions. Current
candidates include `Shusshin` and former shikona history.

The implementation lives in:

```text
src/infra/get_bios/make_public_shikona.py
```

The module can be run directly for a small manual check:

```bash
python -m src.infra.get_bios.make_public_shikona
```
