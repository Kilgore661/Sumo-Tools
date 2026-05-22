Here’s a draft you can drop straight into your docs folder.

---

# 2026 03 24 FSM / Parser Migration – Nuance Points

## Purpose

This document captures the **non-mechanical risks** in migrating the old parser/FSM infrastructure from `NewFoo` to the new canonical `Chii` model.

The migration is largely a matter of **type and module substitution**, but there are a small number of **semantically sensitive areas** where care is required.

---

## 1. Rank object equivalence

The migration assumes:

```text
NewFoo  →  Chii
NewAnn  →  Annotation
```

This is valid only if the following behaviors are equivalent:

* equality (`==`)
* ordering (if used)
* hashing (if used as dict keys)
* `.level`, `.number`, `.side`, `.ann`
* `from_str(...)`
* `__str__()`

### Action

* Verify `Chii.from_str(...)` accepts all strings previously accepted by `NewFoo.from_str(...)`
* Verify `str(Chii)` produces the same canonical form used by FSM logic

---

## 2. Duplicate-key normalization

FSM uses string representations of rank objects as keys:

```python
key = str(foo)
```

### Risk

If `str(Chii)` differs from `str(NewFoo)`:

* duplicate detection may silently fail
* recovery logic may not trigger
* subtle data corruption may occur without exceptions

### Action

* Compare `str(NewFoo(x))` vs `str(Chii(x))` for representative cases:
  
  * normal ranks
  * sideless ranks
  * annotated ranks
  * edge cases (e.g. yokozuna)

---

## 3. Sideless recovery logic

FSM includes logic that reconstructs ranks with:

```text
side = NONE
```

### Assumptions

* `Side.NONE` exists and is used consistently
* removing side does not affect identity beyond side
* equality/ordinal behavior remains valid

### Risk

If `Chii` ordinal or equality semantics differ from `NewFoo`, comparisons like:

```python
sideless_version == expected_version
```

may behave differently.

### Action

* Verify that constructing a sideless `Chii` preserves all other identity fields
* Verify equality comparisons behave identically to `NewFoo`

---

## 4. Annotation recovery logic

FSM performs recovery by manipulating annotations:

```text
ann == EMPTY
ann == YO
```

### Assumptions

* `Annotation.EMPTY` means “no annotation”
* annotations can be changed independently of other fields
* equality reflects annotation correctly

### Risk

* incorrect handling of `EMPTY` vs non-empty annotations
* mismatches in annotation semantics (especially YO)

### Action

* Verify mapping:
  
  * `NewAnn.EMPTY` → `Annotation.EMPTY`
  * `NewAnn.YO` → `Annotation.YO`

* Confirm no hidden differences in meaning or usage

---

## 5. String representation as identity

FSM frequently relies on:

```python
str(foo)
```

as a **canonical identifier**.

### Risk

If `Chii.__str__()` differs even slightly:

* duplicate pools break
* matching logic fails
* debugging becomes difficult

### Action

* Treat `__str__()` as part of the **FSM contract**
* Do not assume cosmetic differences are harmless

---

## 6. Removal of transitional bridge code

The following are legacy constructs:

* `NewFoo`
* `NewAnn`
* `from_chii()`
* `to_chii()`

These were part of a **transitional model layer**.

### Observation

* `from_chii()` appears to be used only in self-test code
* FSM and parser logic operate directly on `NewFoo`, not via conversion

### Action

* Do not replicate these in the new system
* Remove or ignore them unless a real dependency is discovered

---

## 7. Parser-side type assumptions

The parser contains explicit assumptions such as:

```python
isinstance(foo_obj, NewFoo)
```

### Risk

* hard failures after migration if not updated
* hidden reliance on `NewFoo`-specific behavior

### Action

* Replace with `Chii`
* Review any logic that assumes more than simple typing

---

## 8. Boundary between FSM and parser

The interface between FSM and parser is:

```text
FSM → FinalBanzukeEntry(chii=...)
```

### Key point

* FSM defines the **rank semantics**
* parser consumes and assembles objects

### Risk

* mismatched expectations about rank object behavior
* parser assuming properties no longer guaranteed

### Action

* Treat FSM output as the **single source of truth**
* ensure parser does not reinterpret rank semantics

---

## 9. General migration principle

The migration is:

> Mostly mechanical, with a small number of semantically sensitive hotspots.

### Mechanical parts

* imports
* type names
* container classes

### Non-mechanical parts

* rank comparison logic
* recovery heuristics
* string-based identity

---

## 10. Recommended workflow

1. Migrate FSM (`NewFoo` → `Chii`)
2. Validate FSM behavior in isolation
3. Migrate parser assembly
4. Verify end-to-end pipeline

---

## One-line summary

The migration is straightforward structurally, but correctness depends on preserving the **behavioral contract of rank objects** in a few technically sensitive parts of FSM logic.

---

Here’s a checklist version.

---

# 2026 03 24 FSM / Parser Migration – Nuance Checklist

## Rank model substitution

* [ ] Replace `NewFoo` imports with `Chii`

* [ ] Replace `NewAnn` imports with `Annotation`

* [ ] Replace `IntDate` with `Date` or keep `IntDate` consistently

* [ ] Replace all type hints:
  
  * [ ] `NewFoo` → `Chii`
  * [ ] `Optional[NewFoo]` → `Optional[Chii]`
  * [ ] `Tuple[RikId, NewFoo]` → `Tuple[RikId, Chii]`
  * [ ] `Dict[..., NewFoo]` → `Dict[..., Chii]`

## Rank object behavior

* [ ] Confirm `Chii` exposes:
  
  * [ ] `.level`
  * [ ] `.number`
  * [ ] `.side`
  * [ ] `.ann`

* [ ] Confirm `Chii.from_str(...)` can parse all needed rank strings

* [ ] Confirm `Chii` equality behaves as FSM expects

* [ ] Confirm `Chii` hashing behaves as FSM expects

* [ ] Confirm `Chii` ordering/ordinal behavior matches FSM needs

## Duplicate-key normalization

* [ ] Find every place FSM uses `str(foo)` as a key

* [ ] Compare `str(NewFoo)` vs `str(Chii)` for:
  
  * [ ] normal ranks
  * [ ] sideless ranks
  * [ ] annotated ranks
  * [ ] yokozuna/edge cases

* [ ] Confirm duplicate lookup keys still match migrated data

## Sideless recovery

* [ ] Find every place FSM constructs a sideless rank

* [ ] Confirm `Side.NONE` is still the correct representation

* [ ] Confirm making a rank sideless preserves:
  
  * [ ] level
  * [ ] number
  * [ ] annotation

* [ ] Confirm sideless `Chii` compares the same way as sideless `NewFoo`

## Annotation recovery

* [ ] Replace `NewAnn.EMPTY` with `Annotation.EMPTY`
* [ ] Replace `NewAnn.YO` with `Annotation.YO`
* [ ] Check any use of `HD`, `TD`, `OB`, `YO`
* [ ] Confirm `EMPTY` means exactly “no annotation”
* [ ] Confirm changing annotation alone produces the intended rank identity

## Legacy bridge code

* [ ] Do not carry over `from_chii()` unless real usage is found
* [ ] Do not carry over `to_chii()` unless real usage is found
* [ ] Treat `parser_UrChii` bridge helpers as legacy unless proven needed

## Parser-side assumptions

* [ ] Find all `isinstance(..., NewFoo)` checks
* [ ] Replace them with `Chii`
* [ ] Find all comments or logic that say “preserve NewFoo”
* [ ] Update parser assembly to preserve canonical `Chii` instead

## FSM/parser boundary

* [ ] Confirm `FinalBanzukeEntry.chii` becomes/contains `Chii`
* [ ] Confirm parser consumes FSM output without converting rank type again
* [ ] Confirm any helper code downstream of FSM accepts `Chii`

## Imports and module paths

* [ ] Update moved core imports, especially:
  
  * [ ] `Performance`
  * [ ] `RikId`
  * [ ] `Day`
  * [ ] `RikChii`
  * [ ] `RikShikona`

* [ ] Remove stale transitional imports once migration is complete

## Testing strategy

* [ ] Start with FSM in isolation
* [ ] Run single-basho reconciliation first
* [ ] Compare migrated output with old known-good output
* [ ] Only then move upward into parser assembly
* [ ] After parser migration, verify serializer + shared-memory still work

## Red-flag rule

* [ ] If a change touches:
  
  * [ ] `str(foo)`
  * [ ] sideless logic
  * [ ] annotation recovery
  * [ ] duplicate handling
    stop and review semantically, not just mechanically

---

## One-line working rule

> Most lines can be migrated mechanically; any line involving rank identity, string form, side, or annotation must be checked semantically.
