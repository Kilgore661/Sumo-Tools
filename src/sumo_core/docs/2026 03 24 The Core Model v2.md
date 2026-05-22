# LLM’s Guide to the Sumo Core Model

## 0. What this model is trying to do

This codebase models professional sumo as a **typed semantic system**, not as scraped tables.

Key idea:

> The real world is messy; the model imposes a **clean, ordered, identity-based structure** that can still represent that mess.

There are three core pressures the design resolves:

1. **Ranks must be strictly orderable** (for sorting, indexing, comparisons)
2. **Real-world ranks are not perfectly structured** (overflow, exceptions, historical quirks)
3. **Identity must be stable** (rikishi are primary, ranks are attributes)

Everything else follows from those.

---

# 1. The Core Shape of the Model

At the highest level:

```text
History : Date → BashoState

BashoState = Banzuke × Summary

Summary = (Day → DailyResults) × Performances
```

Interpretation:

* **History** = archive of tournaments
* **BashoState** = one tournament
* **Banzuke** = who + what rank
* **Summary** = what happened

This decomposition is **intentional and strong**.

---

# 2. Identity Comes First

The fundamental identity type is:

```text
RikId
```

Everything is keyed off this:

* `RikId → Chii` (rank)
* `RikId → Shikona` (name)
* `RikId → Performance`

Important:

> Rank is **not identity**
> Rank is an **attribute of identity**

This is why:

* `Banzuke` is not a list of ranks
* it is a mapping from `RikId`

---

# 3. Chii: The Most Important Object

## 3.1 What Chii is

A `Chii` is a **semantic rank**, not a string.

Structure:

```text
(level, number, side, annotation)
```

Examples (display only):

* `M3e`
* `M3eHD`
* `Y1w`

---

## 3.2 What Chii is NOT

* Not a string
* Not lexically ordered
* Not guaranteed unique

---

## 3.3 The Core Rule: ordinal()

Every `Chii` has:

```text
ordinal() : int
```

This defines **all ordering semantics**.

### Exact layout

```text
lnnnas
```

Where ordering precedence is:

```text
level → number → annotation → side
```

Lower ordinal = stronger rank

---

## 3.4 Why annotation comes before side

This is not arbitrary.

It reflects real structure:

* `(level, number, side)` defines a **base slot**
* Sometimes that slot has **multiple occupants**
* Annotation distinguishes them

So ordering is:

```text
M3e  <  M3eHD  <  M3w
```

Meaning:

* annotation refines **within a side slot**
* side is only used after annotation

---

## 3.5 Annotation semantics (critical)

Annotations (e.g. `HD`, `TD`, `YO`, `OB`) are:

> **Structural disambiguators for irregular rank placement**

They are:

* not full rank levels
* not mere display
* not semantically ordered among themselves

### Known meanings

* `HD` = marginalia (extra occupant of a rank slot)
* `TD` = exceptional high placement for a newcomer
* others = historical / unclear

### Ordering rule

```text
EMPTY annotation is stronger than ANY annotation
```

Between non-empty annotations:

```text
ordering is arbitrary but fixed
```

This exists only to ensure:

```text
Chii is strictly totally ordered
```

---

## 3.6 What Chii really models

Not just rank — but **rank slots**:

```text
(level, number, side) → 1..n occupants
```

Annotation = which occupant

So effectively:

```text
(level, number, side, slot_index)
```

---

## 3.7 Consequences

* Rank strings must never be sorted lexically
* `(level, number, side)` is **not unique**
* Multiple rikishi may share a base rank
* Ordinal is a **linearization of a partially messy structure**

---

# 4. Banzuke: The Roster

## 4.1 Structure

```text
RikId → Chii
RikId → Shikona
```

with shared domain.

## 4.2 What it guarantees

* Every rikishi has:
  
  * a rank
  * a name

## 4.3 What it does NOT guarantee

* Rank uniqueness
* Unique ordinal
* Unique rank string

This is intentional.

---

## 4.4 Mental model

> Banzuke = “who is in the tournament and where they are placed”

Not:

> “a list of ranks”

---

# 5. Summary: What Happened

## 5.1 Structure

```text
Day → DailyResults
RikId → Performance
```

## 5.2 Key invariant

If days exist:

```text
they start at Day 1 and are contiguous
```

Meaning:

* Summary is a **prefix of the tournament timeline**

---

# 6. DailyResults: One Day

Contains:

* `Torikumi` (scheduled bouts)
* `Pair → BoutResult`

Important:

> This class is intentionally light on validation

Do not assume:

* full consistency enforced here
* uniqueness enforced here

---

# 7. BoutResult: One Match

## 7.1 Structure

* two rikishi
* two outcomes
* decision (kimarite / fusen / blank)
* symbol

## 7.2 Enforced rules

* exactly two distinct rikishi

* valid outcome pairs:
  
  * `(W, L)`
  * `(FS, FP)`
  * `(DRAW, DRAW)`

## 7.3 Not fully enforced

* symbol vs outcome consistency (exists but not enforced)

---

# 8. Performance

Represents:

* prizes (Yusho, etc.)
* promotion/demotion markers

Invariant:

* cannot have both Yusho and Jun-Yusho

---

# 9. History

```text
Date → BashoState
```

* archive of tournaments
* ordering is chronological

Note:

* API inconsistency: may raise instead of returning None

---

# 10. Validation Philosophy (VERY IMPORTANT)

The codebase mixes two styles:

* Author intent: **offensive programming**
* LLM residue: **defensive checks**

Therefore:

### DO NOT assume

* “checked = important”
* “unchecked = unimportant”

### Instead infer from:

1. representation (data structures)
2. ordering logic (especially `ordinal`)
3. parsing grammar
4. comments explaining edge cases

---

# 11. What the Model Gets Right

* Rank is semantic, not textual
* Identity is stable and central
* Irregular rank cases are representable
* Ordering is total and deterministic

---

# 12. Known Gaps / Limits

* `Mz` (mae-zumo) not modeled
* Annotation meanings mostly not encoded
* Some validation incomplete or inconsistent
* Parser/model boundary not fully visible

---

# 13. The Most Important Takeaways

If you are an LLM reasoning about this system:

### 1. Never treat rank as a string

Always use `Chii` / `ordinal()`

### 2. Never assume rank uniqueness

Multiple rikishi may share a rank slot

### 3. Annotation is structural, not decorative

It resolves irregular placement

### 4. Identity is `RikId`

Everything else hangs off it

### 5. The model is a **clean ordering over a messy domain**

Not a perfect mirror of reality

---

# One-line summary

> This system models sumo as a mapping from stable identities (`RikId`) to semantic ranks (`Chii`) and outcomes, where rank is a strictly ordered slot system that can represent real-world irregularities via annotations.
