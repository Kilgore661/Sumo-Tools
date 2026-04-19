# Design / Modeling Principles for the Standings Project

These are the working principles established so far for future development.

---

## 1. Top-Down Design First

Design begins with the **function we want**.

Start from clear top-level signatures and decompose downward into smaller functions.

Example:

```python
f(x: X) -> Y
z = g(x)        # g: X -> Z
return h(x, z) # h: X × Z -> Y
```

Implementation details come after the contract is clear.

---

## 2. Signatures Are the Primary Specification

A good function signature should communicate:

* required inputs
* result type
* important distinctions in meaning

Prefer signatures that explain the system.

---

## 3. Use Named Types Where They Clarify Meaning

Do **not** turn everything into a class.

Create named types only when they improve clarity, especially when they appear in important signatures.

Good candidates:

* request objects
* result objects
* core domain concepts

Example:

```python
get_single_basho_standings(...) -> SingleBashoStandings
```

Better than:

```python
-> list[dict]
```

---

## 4. Prefer Concrete Types Over Premature Abstraction

Do not generalize until a real common abstraction is earned.

Prefer:

* `SingleBashoStandings`
* `MultiBashoStandings`

over an early vague type such as:

* `Standings`

if the shapes differ.

---

## 5. Design by Contract

Each function is called only after its preconditions have been established by the caller.

Each layer’s responsibility is to establish the contract required by the next layer.

Examples:

* CLI layer converts `argv` into valid arguments
* orchestration layer converts arguments into domain requests
* domain layer assumes valid inputs

---

## 6. Avoid Optionality Unless It Is Real Domain Meaning

Do not use `None`, `Optional`, or `| None` unless “missingness” is genuinely part of the requirements.

Defaults and omitted values belong at outer boundaries, not in core domain signatures.

Prefer:

```python
get_standings(history: History, date: Date, ...)
```

over:

```python
get_standings(history: History, date: Date | None, ...)
```

unless absence is truly meaningful.

---

## 7. Fail Loudly on Broken Contracts

Do not add defensive code merely to suppress errors.

Avoid unnecessary use of:

* `dict.get()`
* broad `try/except`
* silent fallbacks

If a contract is broken, failure is acceptable and often desirable.

---

## 8. Boundary Code Is Still Real Code

`main()` and CLI entry points are functions too.

Treat them as adapters with clear responsibilities, not dumping grounds.

Conceptually:

```python
argv -> console messages × output files
```

---

## 9. Separate Domain Results from Presentation

Core functions should return domain objects.

CSV, logs, charts, HTML, etc. are renderings of those results.

Example:

```python
History -> SingleBashoStandings -> CSV
```

not:

```python
History -> CSV
```

---

## 10. Correctness Before Efficiency

First priority:

1. clear specification
2. correct implementation

Only optimize when performance is a demonstrated problem.

Do not let speculative efficiency drive design prematurely.

---

## 11. Derived Data Is Acceptable

There is no purity rule against storing derived values.

If cached or precomputed values make the implementation simpler and remain correct, they are acceptable.

Avoid confusing implementation choices with design principles.

---

## 12. Keep Scope Controlled

Do not let useful tools become monsters.

Build the capability currently required.

Delay speculative features, over-generalization, and exotic metrics until justified by real needs.

---

## 13. Prefer Readability and Meaningful Names

Names should reflect domain meaning and make contracts obvious.

Examples:

* `get_single_basho_standings`
* `SingleBashoStandings`
* `wins_mode`

Better names reduce the need for comments.

---

## 14. Evolve by Specific Use Cases

Start with a concrete use case.

Implement it cleanly.

Generalize only after multiple real use cases reveal the right abstraction.

---

# Practical Summary

For this project:

* clear signatures first
* named result types where useful
* no unnecessary optionality
* caller establishes contracts
* fail loudly on misuse
* domain objects before reports
* optimize later
* generalize only when earned

----

AND

Agreed.

That’s a good balancing rule, and it fits the overall style.

The principle would be:

> decompose by meaning, not mechanically

So if a step is genuinely carrying semantic weight, give it a function and possibly a named type. If it is just a tiny local transformation, keep it inline.

## A workable rule of thumb

A separate function is justified when at least one of these is true:

* it has a clear contract of its own
* naming it makes the top-level algorithm easier to read
* it is likely to be reused
* it isolates a nontrivial decision or policy
* it could reasonably be tested independently

A step can stay inline when it is truly trivial, like:

* one obvious sort
* one obvious field selection
* one small if/else whose meaning is already clear from surrounding code

## Applied to the single-basho case

I would still separate:

* deriving per-rikishi totals from a `BashoState`
* ranking those totals into standings

because those are semantically distinct.

But I would not feel compelled to split out every small helper inside them. For example:

* choosing the primary ranking key from `wins_mode`
* the sort key lambda
* a tiny competition-rank loop

could well remain inline if the code reads cleanly.

So the decomposition might be:

```python
get_single_basho_standings(basho: BashoState, wins_mode: WinsMode) -> SingleBashoStandings
```

implemented as:

* one meaningful auxiliary function:

  * `get_single_basho_totals(basho) -> SingleBashoTotals`
* then inline ranking logic if it is short and clear

rather than forcing:

* `select_primary_key(...)`
* `sort_rows(...)`
* `assign_positions(...)`

into separate functions just because they can be.

## The same applies to types

You likely do want:

* `WinsMode`
* `SingleBashoStandings`
* probably `SingleBashoStandingRow`

You may or may not want:

* `SingleBashoTotals`

depending on whether it clarifies enough.

You almost certainly do not need:

* `PrimarySortKey`
* `RankingPolicy`
* `PositionAssignmentResult`

unless the code later proves that they pull their weight.

## So the emerging design principle is

> introduce functions and types where they clarify the contract or the algorithm; keep trivial mechanics inline

That is a very good antidote to overengineering.

## In practical terms

For the single-basho function, I would now aim for:

* a clear signature
* one or two meaningful types
* at most one meaningful helper function
* trivial mechanics left inline

That should keep the code honest and compact.

