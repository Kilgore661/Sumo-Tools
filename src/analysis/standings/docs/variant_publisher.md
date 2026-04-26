# Proposal: Introduce `variant_publisher.py` for Multi-Regime Standings Publication

## Status

Draft technical change proposal.

This document concerns publication-layer changes only. It does not define product requirements, browser behaviour, or final UI design.

---

# 1. Purpose

The current standings publication process emits a single family of browser-consumable datasets representing one fixed metric regime.

This proposal recommends replacing or supplementing that process with a new publisher named:

**`variant_publisher.py`**

Its purpose would be to emit multiple coherent published dataset families, one for each supported policy variant.

---

# 2. Context

The standings browser currently consumes precomputed static CSV / JSON artefacts.

This architecture has substantial advantages:

* no live server computation
* fast browser interaction
* simple deployment
* low operational complexity
* reproducible published outputs

These advantages remain desirable.

However, future browser enhancements may require users to switch between alternative metric regimes rather than consuming one fixed regime only.

To preserve the static-publication model, all supported regimes should be precomputed offline.

---

# 3. Immediate Objective

Near-term development is expected to explore two advanced / expert policy dimensions:

## 3.1 WinsPolicy

Controls how wins are counted.

Initial supported values:

* include fusensho
* exclude fusensho

## 3.2 BoutBasis

Controls how bouts are counted.

Initial supported values:

* expected
* available

---

# 4. Required Publication Scope

Supporting both dimensions requires publication of all combinations:

| WinsPolicy       | BoutBasis |
| ---------------- | --------- |
| include fusensho | expected  |
| include fusensho | available |
| exclude fusensho | expected  |
| exclude fusensho | available |

Therefore the publisher should emit:

> **2 × 2 = 4 dataset families**

Each family must be internally coherent under its own metric rules.

---

# 5. Core Principle

Each published dataset family shall represent a complete standings world under one selected regime.

This means values within a family must be mutually consistent.

Examples:

* Wins must reflect the selected WinsPolicy.
* Bouts must reflect the selected BoutBasis.
* Derived metrics such as Average and Win % must be computed from the same governing rules.

The browser should not be required to reconstruct regime semantics from mixed raw ingredients.

---

# 6. Output Structure

A directory-based structure is recommended in preference to long encoded filenames.

Illustrative example:

```text
data/
  include_fusensho/
    expected/
      ...
    available/
      ...
  exclude_fusensho/
    expected/
      ...
    available/
      ...
```

Within each leaf directory, existing per-window files may continue using current naming conventions based on anchor date, direction, and number of basho.

Example:

```text
multiple basho standings view (2026_03, BACKWARDS, 6).csv
multiple basho standings view (2026_03, BACKWARDS, 6).json
site_config.json
```

---

# 7. Behaviour of `variant_publisher.py`

The publisher should conceptually iterate over supported policy values:

```text
for each WinsPolicy
    for each BoutBasis
        for each supported basho window
            compute standings
            write outputs
```

Implementation details may vary.

---

# 8. Relationship to Existing Publisher

Several migration paths are possible:

## Option A — Replacement

`variant_publisher.py` becomes the primary publisher.

## Option B — Parallel Tooling

Existing publisher remains for legacy/simple publication.

`variant_publisher.py` is added for advanced publication.

## Option C — Refactor Existing Publisher

Current publisher absorbs variant behaviour but is renamed conceptually.

No decision is required in this document.

---

# 9. Browser Implications (Informational Only)

Future browser controls may select a desired regime and load the corresponding published dataset family.

No runtime standings recomputation need be introduced.

This proposal does not define browser implementation.

---

# 10. Benefits

## 10.1 Preserves Static Architecture

Advanced behaviour can be supported without abandoning precomputed artefacts.

## 10.2 Keeps Browser Lightweight

The browser continues to load data rather than compute standings logic.

## 10.3 Improves Semantic Integrity

Each dataset family is internally coherent and directly interpretable.

## 10.4 Enables Controlled Expansion

Additional future policy dimensions could be added systematically if justified.

---

# 11. Non-Goals

This document does not decide:

* whether advanced controls should be exposed publicly
* default settings
* wording of user-facing labels
* notes text
* menu layout
* broader product philosophy
* future additional policy dimensions

Those belong in requirements/specification work.

---

# 12. Recommended Next Step

Adopt `variant_publisher.py` as a working publication concept, then separately revise product requirements and specification to determine whether and how WinsPolicy and BoutBasis should be surfaced in the browser product.

---

# 13. Final Position

The proposed publisher is a modest structural extension of the current architecture.

It preserves the operational simplicity of static publication while enabling future multi-regime standings behaviour.

