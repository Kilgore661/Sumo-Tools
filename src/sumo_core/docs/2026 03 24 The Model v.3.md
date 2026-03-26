# **The Sumo Core Model — Definitive Technical Specification**

## 0. Purpose

This model represents professional sumo tournaments as a **typed, identity-first system**.

It is not a scrape model and not a UI model.
It is a **semantic model** designed to:

* represent tournaments cleanly despite real-world irregularities
* provide a **total ordering of rank**
* maintain stable identity for rikishi
* support deterministic comparison, indexing, and persistence

---

## 1. Top-Level Structure

The model has a simple algebraic form:

```text
History : Date → BashoState

BashoState = Banzuke × Summary

Summary = (Day → DailyResults) × Performances
```

### Interpretation

* **History**: date-indexed collection of tournaments
* **BashoState**: one tournament
* **Banzuke**: who is present and their rank
* **Summary**: what happened

This decomposition is **intentional and authoritative**.

---

## 2. Identity Model

### 2.1 Primary identity

```text
RikId
```

All core data is keyed by `RikId`.

### 2.2 Principle

> Identity is primary. Rank, name, and performance are attributes of identity.

Consequences:

* No rank-centric data structures
* No reliance on rank strings as identifiers
* All mappings originate from `RikId`

---

## 3. Chii (Rank)

## 3.1 Definition

A `Chii` is a **fully specified rank designation**.

```text
Chii = (level, number, side, annotation)
```

Examples:

* `M3e`
* `M3eHD`
* `Y1w`

### Important

> A `Chii` is atomic. It is not a base rank plus modifiers.

---

## 3.2 Terminology

The term *rank* is avoided because it is overloaded in sumo.

In this document:

> “Rank” means a **full `Chii`**, not:

* division (e.g. Makushita)
* title (e.g. Yokozuna)
* partial strings (e.g. “M3”)

---

## 3.3 Completeness

A `Chii` is always fully specified.

* `"M3e"` is valid
* It is equivalent to `"M3e" + EMPTY annotation`

There is no concept of an “incomplete Chii”.

---

## 3.4 Uniqueness (critical invariant)

> No two distinct rikishi share the same `Chii`.

Formally:

```text
RikId → Chii is injective
```

### Status

* Holds for all known real data
* Believed true by construction of the source
* **Not currently enforced in code**

See *Next Steps*.

---

## 3.5 Ordering

Every `Chii` defines:

```text
ordinal() : int
```

This is the **canonical ordering function**.

Ordering precedence:

```text
level → number → annotation → side
```

Lower ordinal = stronger rank.

---

## 3.6 Canonical representation

> `ordinal()` is the canonical, portable, and comparable representation of rank.

Consequences:

* equality is defined via ordinal
* ordering is defined via ordinal
* hashing is defined via ordinal
* persistence uses ordinal

String forms are **presentation only**.

---

## 3.7 Annotation

Annotation is an intrinsic component of `Chii`.

* It is not a secondary disambiguation layer
* It is part of the rank identity
* Its semantics are partially understood

Known examples:

* `HD` — marginalia (extra placement)
* `TD` — exceptional placement
* others — historical / unclear

### Ordering rule

* EMPTY annotation outranks any non-empty annotation
* ordering among non-empty annotations is arbitrary but fixed

Purpose:

> Ensure `Chii` is totally ordered.

---

## 4. Banzuke

## 4.1 Structure

```text
RikId → Chii
RikId → Shikona
```

with identical domain.

---

## 4.2 Meaning

> Banzuke = “who is present and where they are placed”

---

## 4.3 Guarantees

* Every rikishi has:

  * a `Chii`
  * a `Shikona`
* Domains are consistent

---

## 4.4 Non-guarantees (by code)

* Injectivity (not enforced, but intended)
* Any ordering of entries
* Any structure beyond mappings

---

## 5. Summary

## 5.1 Structure

```text
Day → DailyResults
RikId → Performance
```

---

## 5.2 Invariant

If any days exist:

```text
days start at 1 and are contiguous
```

This means:

> Summary represents a prefix of a tournament.

---

## 6. DailyResults

Contains:

* `Torikumi` (scheduled bouts)
* `Pair → BoutResult`

### Important

> This class does not enforce full consistency.

It represents recorded data, not validated tournament logic.

---

## 7. BoutResult

Represents a single bout.

### Structure

* two rikishi
* two outcomes
* decision (kimarite / fusen / blank)
* symbol

---

### Enforced invariants

* rikishi are distinct
* valid outcome pairs:

```text
(W, L)
(FS, FP)
(DRAW, DRAW)
```

---

### Not enforced

* consistency between:

  * outcome
  * symbol
  * decision

---

## 8. Performance

Represents:

* prizes
* promotion/demotion markers

Invariant:

* cannot contain both Yusho and Jun-Yusho

---

## 9. History

## 9.1 Structure

```text
Date → BashoState
```

---

## 9.2 Meaning

> History is a date-indexed collection of basho data.

It is:

* ordered by date
* largely contiguous (with known exceptions)

---

## 9.3 Non-semantics

History does **not** model:

* temporal evolution
* causality
* promotion rules
* state transitions

It is **not a process model**.

---

## 10. Mappings and Functions

Mappings are used interchangeably as:

* containers
* functions

### Principle

> If a mapping is known to be total, it is treated as a total function.

Therefore:

* use `mapping[key]`
* avoid `.get()` when key presence is guaranteed

`.get()` introduces false partiality and should not be used in such cases.

---

## 11. Validation Philosophy

The model follows an **offensive programming** style.

### Principle

> Validation occurs where an invariant is owned.

Consequences:

* absence of validation ≠ absence of constraint
* upstream construction is trusted
* invalid states indicate:

  * bad input
  * broken contract
  * implementation compromise

---

## 12. Model Boundary

The model represents **ranked banzuke participants only**.

Certain real-world categories (e.g. mae-zumo / `"Mz"`) are:

* handled at parsing boundaries
* not part of the core model
* not persisted as `Chii`

---

## 13. Next Steps

### 13.1 Enforce injectivity

Add validation to ensure:

```text
∀ r1 ≠ r2 : Chii(r1) ≠ Chii(r2)
```

This is a known invariant not currently enforced.

---

### 13.2 Remove defensive residue

* eliminate unnecessary `.get()`
* remove redundant try/except blocks
* align implementation with total-function assumptions

---

### 13.3 Optional: tighten consistency checks

* `BoutResult`:

  * enforce symbol/outcome consistency
* API consistency:

  * align docstrings with actual behaviour

---

# One-line summary

> The model represents sumo tournaments as mappings from stable identities (`RikId`) to fully specified rank objects (`Chii`) and outcomes, where rank is atomic, totally ordered via `ordinal()`, and uniquely assigned within each tournament.


## 14 Appenidix: Alphabetical Class Index

### A

* **Annotation** — `BasicEnums.py` 

---

### B

* **Banzuke** — `Banzuke.py` 
* **BashoState** — `BashoState.py` 
* **BoutResult** — `Summary.py` 

---

### C

* **Chii** — `Chii.py` 

---

### D

* **DailyResults** — `Summary.py` 
* **Date** — `History.py` 
* **Decision** — `Summary.py` 
* **Direction** — `BasicEnums.py` 
* **Division** — `BasicEnums.py` 
* **Day** — `BasicPrimitives.py` 

---

### H

* **History** — `History.py` 

---

### K

* **Kimarite** — `Kimarite.py` 

---

### L

* **Level** — `Chii.py` 

---

### M

* **Month** — `BasicPrimitives.py` 
* **MSD** — `BasicEnums.py` 

---

### O

* **Outcome** — `BasicEnums.py` 

---

### P

* **Pair** — `BasicPrimitives.py` 
* **Performance** — `Performance.py` 
* **Performances** — `Performance.py` 
* **Prize** — `BasicEnums.py` 

---

### R

* **RikChii** — `Banzuke.py` 
* **RikId** — `BasicPrimitives.py` 
* **Riks** — `BasicPrimitives.py` 
* **RikShikona** — `Banzuke.py` 
* **ResultLookup** — `Summary.py` 

---

### S

* **Shikona** — `BasicPrimitives.py` 
* **Side** — `BasicEnums.py` 
* **Summary** — `Summary.py` 
* **Symbol** — `BasicEnums.py` 

---

### T

* **Torikumi** — `BasicPrimitives.py` 

---

### Y

* **Year** — `BasicPrimitives.py` 

---


