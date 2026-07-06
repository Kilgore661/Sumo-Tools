# New Banzuke Artifact Proposal

## Status

Draft proposal, 2026-07-06. Initial implementation in progress on
`codex/new-banzuke-artifact`.

This document records the agreed requirements, specification and implementation
plan for making Banzuke Changes update when a new banzuke is published before
the basho has started.

The document remains the contract reference for the implementation work.

## Problem

`page=banzuke_changes` is the one public page whose natural trigger is a newly
published banzuke.

When SumoDB publishes the next `Banzuke.aspx`, the page is authoritative for
the new ranks, rikishi and shikona. It is also pre-basho data: the result cells
show `0-0`, and there are no daily-result files for that basho yet.

This creates a gap in the current model.

Canonical `History` is built from represented basho records. A newly published
pre-basho banzuke is not yet a completed or represented `BashoState`, but
Banzuke Changes legitimately needs to consume it.

The observed failure was:

```text
KeyError: 13005
```

The July 2026 banzuke contained a rikishi that was present in the new banzuke
source page but absent from canonical `History` and from the derived
`FullShikonaStore`.

## Requirement

Banzuke Changes must update from the latest locally available newly published
`Banzuke.aspx` page, even before that basho has daily results and before it is
represented in canonical `History`.

Other public pages are not required to treat the newly published banzuke as part
of their data model. They remain `History`-derived unless explicitly promoted
later.

## Non-Requirements

This change does not make a pre-basho banzuke part of canonical `History`.

This change does not introduce a fake day-zero `BashoState`.

This change does not create a public archive of historical Banzuke Changes
reports.

This change does not require pages such as longest careers, standings or basho
results to update from pre-basho banzuke publication data.

## Model

Introduce a first-class infra-owned artifact called **New Banzuke**.

The New Banzuke is:

- the latest locally available parsed `Banzuke.aspx` publication
- persisted at a stable path
- internally dated
- producer-safe for public-facing analysis code
- separate from canonical `History`

It represents publication state, not completed basho state.

The durable source remains the raw SumoDB HTML:

```text
files/output/current standings/YYYY MM.html
```

The producer-safe parsed artifact should live at a stable path such as:

```text
files/output/infra/new_banzuke/new_banzuke.json
```

The stable filename is intentional. Banzuke Changes is a current/new-banzuke
page, not a date-selectable archive.

The artifact metadata must still carry the represented basho date.

## Chii Serialization Rule

A `Chii` is its ordinal.

Chii strings are human gloss only. They may be written where a human needs to
read the file, but they must not be used as input to later calculation,
ordering, reconstruction or comparison.

The New Banzuke artifact therefore persists `chii_ordinal` as the machine
field. It may also persist a display string such as `chii` or `chii_label`, but
that string is display-only.

Example shape:

```json
{
  "date": "2026/07",
  "source_path": "files/output/current standings/2026 07.html",
  "source_url": "https://sumodb.sumogames.de/Banzuke.aspx?b=202607&heya=-1&shusshin=-1",
  "generated_at": "2026-07-06T10:00:00",
  "entries": [
    {
      "rikishi_id": 13005,
      "shikona": "Kakizoe",
      "chii_ordinal": 632,
      "chii": "Jk16w"
    }
  ]
}
```

The exact ordinal in the example is illustrative only.

## Specification

### New Banzuke Producer

Add an infra-owned producer command:

```powershell
py -m src.infra.new_banzuke
```

The producer:

1. Finds the latest available raw banzuke page under
   `files/output/current standings`.
2. Parses that page using infra-owned parser code.
3. Writes `files/output/infra/new_banzuke/new_banzuke.json`.
4. Fails loudly if the source page cannot be parsed.

The producer is responsible for translating raw source HTML into a stable
project artifact. Public-facing producers must not parse raw SumoDB HTML
directly.

### New Banzuke Loader

Add an infra-owned loader API:

```python
load_new_banzuke() -> NewBanzuke
```

The loaded model must provide enough information to reconstruct or expose:

- banzuke date
- rikishi ids
- shikona
- chii ordinal
- optional display chii gloss

If a `Banzuke` object is still needed by existing Banzuke Compare code, provide
an explicit conversion helper rather than making analysis code parse JSON
ad hoc.

### Banzuke Changes Producer

Change Banzuke Compare so that its current banzuke input comes from
`load_new_banzuke()`, not from `parser2.get_banzuke(current_date)`.

Banzuke Compare should consume:

- New Banzuke
- previous completed `BashoState` from canonical `History`
- Equelo snapshot before the New Banzuke date
- a complete BCR display-label map for every rikishi in the New Banzuke

Current-only rikishi are expected in the pre-basho case. They are not an
exceptional condition.

### BCR Display-Label Rule

Banzuke Changes requires a complete display-label map for the New Banzuke.

That map is built as a model transition from:

```text
New Banzuke
+ canonical History public labels
-> BCR display-label map
```

The rule is:

- rikishi represented in canonical `History` use the established public label
- current-only rikishi use the shikona carried by the New Banzuke

After this transition, every New Banzuke rikishi has a display label. Later BCR
stages use direct lookup into that complete map. A missing label after this
point is an internal modelling error and should crash.

## Build Order

The relevant build sequence should become:

```powershell
py -m src.infra.parser.parser2
# start or refresh live store as needed
py -m src.infra.get_bios.parser
py -m src.infra.new_banzuke
py -m src.analysis.banzuke_compare.publisher
py -m src.products.make_site2
```

The optional raw bio downloader remains useful when completed `History` gains
new rikishi, but it is not the mechanism that makes pre-basho New Banzuke
rikishi available to Banzuke Changes.

## Implementation Plan

1. Inspect `Chii` construction and ordinal conversion APIs.

2. Add `src/infra/new_banzuke/` with:
   - model dataclasses
   - JSON writer
   - JSON loader
   - CLI entry point

3. Implement latest-source selection from
   `files/output/current standings/*.html`.

4. Reuse parser-owned banzuke parsing inside the infra producer, then serialize
   producer-safe New Banzuke JSON.

5. Replace Banzuke Compare's direct current-banzuke parser call with the New
   Banzuke loader.

6. Add an explicit Banzuke Compare display-label model transition that produces
   a complete label map for the New Banzuke.

7. Update `_boot.ps1` to include `py -m src.infra.new_banzuke` before the
   Banzuke Compare publisher.

8. Add focused tests:
   - New Banzuke artifact writes machine chii ordinals and display gloss.
   - New Banzuke loader round-trips the persisted artifact.
   - Banzuke Compare can build a report when the current banzuke contains a
     rikishi absent from canonical `History`.
   - The BCR display-label transition produces a complete label map for every
     New Banzuke rikishi.
   - Banzuke Compare no longer calls parser-facing `get_banzuke()` for the
     current banzuke.

## Design Notes

The New Banzuke artifact is intentionally current and ephemeral.

If historical banzuke-change browsing is ever promoted, it should be designed as
a separate feature. The current Banzuke Changes page answers "what just changed?"
and should remain focused on the latest new banzuke.

The tracker remains responsible for retrieving raw source artifacts promptly.
The New Banzuke producer is responsible for turning the latest raw banzuke
source into a producer-safe parsed artifact.

Canonical `History` remains the completed-record store.
