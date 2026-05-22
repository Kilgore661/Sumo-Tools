# The PL Fix

## Proposal: Reorganisation of standings metric types and values

### 1. Purpose

This proposal revises the internal type/value vocabulary used by the standings application.

Its purpose is to replace ambiguous or weakly named concepts with a clearer and more extensible model, while preserving current behaviour.

At present, the code and documentation use terms such as:

* `WinsMode.REAL`
* `WinsMode.ALL`
* `window`
* `presence`

These terms were good enough to support the first implementation, but they no longer provide a stable basis for further extension. In particular:

* `REAL` and `ALL` do not clearly describe the actual domain distinction
* `presence` is grammatically and conceptually unsatisfactory
* the existing naming does not provide a coherent place for a third metric dimension

The immediate goal is therefore to reorganise the type system around a clearer set of axes and values.

This proposal concerns that reorganisation only.

---

## 2. General modelling principle

The standings model should distinguish:

* **domain categories**
* **counting policies**
* **bases of inclusion or counting**

These should not be conflated in a single enum or in ad hoc field names.

The revised type system should make each semantic axis explicit.

---

## 3. Revised type set

The application shall use the following types.

### 3.1 `WinKind`

`WinKind` represents the kind of credited win that may occur in the domain.

```python
class WinKind(Enum):
    FOUGHT = auto()
    FUSENSHO = auto()
```

#### Meaning

* `FOUGHT` means a win obtained in a fought bout
* `FUSENSHO` means a win credited by fusensho

#### Rationale

The current values `REAL` and `ALL` are not parallel domain categories.

By contrast, `FOUGHT` and `FUSENSHO` are true peer categories and reflect the actual distinction present in the data.

---

### 3.2 `WinPolicy`

`WinPolicy` represents the policy used when counting wins for standings purposes.

```python
class WinPolicy(Enum):
    FOUGHT_ONLY = auto()
    CREDITED = auto()

    def includes(self) -> set[WinKind]:
        if self is WinPolicy.FOUGHT_ONLY:
            return {WinKind.FOUGHT}
        if self is WinPolicy.CREDITED:
            return {WinKind.FOUGHT, WinKind.FUSENSHO}
        raise ValueError(f"Unsupported win policy: {self}")
```

#### Meaning

* `FOUGHT_ONLY` counts only fought wins
* `CREDITED` counts all credited wins, namely fought wins and fusensho

#### Rationale

The existing `WinsMode` enum mixes policy and terminology in a way that is not extensible.

The revised model separates:

* the kinds of win that exist
* the policy deciding which kinds are counted

This gives a cleaner and more exact model.

---

### 3.3 `BashoBasis`

`BashoBasis` represents the basis on which basho are counted or included.

```python
class BashoBasis(Enum):
    SELECTED = auto()
    CONTAINING = auto()
```

#### Meaning

* `SELECTED` means basho selected by the standings window rule
* `CONTAINING` means basho containing the rikishi

#### Rationale

The current terminology `window` / `presence` is unsatisfactory.

`window` is serviceable but informal; `presence` is misleading because it compresses the relation “a basho in which the rikishi is present” into a phrase that reads as if the basho itself were “present”.

`SELECTED` and `CONTAINING` form a clearer and more grammatically coherent pair.

---

### 3.4 `BoutBasis`

`BoutBasis` represents the basis on which bouts are counted.

```python
class BoutBasis(Enum):
    EXPECTED = auto()
    AVAILABLE = auto()
```

#### Meaning

* `EXPECTED` means the bouts a rikishi would normally be expected to have in the relevant basho
* `AVAILABLE` means the bouts actually available in the recorded data

#### Rationale

This type is introduced now as part of the revised vocabulary even though it may not yet be active in current calculations.

Its presence makes the type system complete and provides the correct conceptual place for the later extension of the metrics model.

---

## 4. Type/value mapping from the current model

The revised model should replace current terms as follows.

### 4.1 Win counting

Current:

* `WinsMode.REAL`
* `WinsMode.ALL`

Proposed replacement:

* `WinPolicy.FOUGHT_ONLY`
* `WinPolicy.CREDITED`

Interpretation:

* current “real wins” becomes “fought wins”
* current “all wins” becomes “credited wins”

### 4.2 Win categories

Current code does not explicitly model win categories as such.

Proposed addition:

* `WinKind.FOUGHT`
* `WinKind.FUSENSHO`

These underpin `WinPolicy`.

### 4.3 Basho basis terminology

Current informal vocabulary:

* `window`
* `presence`

Proposed replacement:

* `selected`
* `containing`

Examples:

* `window_average_real_wins` becomes conceptually “mean fought wins per selected basho”
* `presence_average_real_wins` becomes conceptually “mean fought wins per containing basho”

### 4.4 Bout basis terminology

No current explicit type exists.

Proposed vocabulary:

* `EXPECTED`
* `AVAILABLE`

This is added now for consistency and future use.

---

## 5. Proposed naming policy

The codebase shall follow these naming rules.

### 5.1 Type names

Semantic axes should use singular names ending in `Kind`, `Policy`, or `Basis` as appropriate.

Examples:

* `WinKind`
* `WinPolicy`
* `BashoBasis`
* `BoutBasis`

### 5.2 Value names

Enum values should be:

* short
* domain-meaningful
* at the same semantic level within a type

Examples:

* good: `FOUGHT`, `FUSENSHO`
* good: `FOUGHT_ONLY`, `CREDITED`
* good: `SELECTED`, `CONTAINING`
* good: `EXPECTED`, `AVAILABLE`

Avoid:

* vague umbrella terms such as `ALL`
* non-parallel pairs
* compressed relational labels such as `PRESENCE`

### 5.3 Derived field names

Field names should reflect the revised vocabulary.

In particular:

* replace `real` with `fought`
* replace `all` with `credited`
* replace `window` with `selected`
* replace `presence` with `containing`

This proposal does not yet prescribe the final full field-name set, but it does prescribe the vocabulary from which those names shall be formed.

---

## 6. Immediate class changes required

This proposal requires the following immediate structural changes.

### 6.1 Remove `WinsMode`

`WinsMode` shall be retired.

Where current code requires a standings counting policy, it shall use `WinPolicy`.

### 6.2 Introduce `WinKind`

A distinct `WinKind` enum shall be added and used wherever the code needs to reason about the category of a credited win.

### 6.3 Introduce `BashoBasis`

`BashoBasis` shall be introduced as the formal replacement for the current informal `window` / `presence` distinction.

### 6.4 Introduce `BoutBasis`

`BoutBasis` shall be introduced as part of the type vocabulary, even if some code paths do not yet make operational use of it.

---

## 7. Proposed canonical definitions

The following definitions are proposed as canonical.

```python
from enum import Enum, auto


class WinKind(Enum):
    FOUGHT = auto()
    FUSENSHO = auto()


class WinPolicy(Enum):
    FOUGHT_ONLY = auto()
    CREDITED = auto()

    def includes(self) -> set[WinKind]:
        if self is WinPolicy.FOUGHT_ONLY:
            return {WinKind.FOUGHT}
        if self is WinPolicy.CREDITED:
            return {WinKind.FOUGHT, WinKind.FUSENSHO}
        raise ValueError(f"Unsupported win policy: {self}")


class BashoBasis(Enum):
    SELECTED = auto()
    CONTAINING = auto()


class BoutBasis(Enum):
    EXPECTED = auto()
    AVAILABLE = auto()
```

---

## 8. Final position

The standings application should adopt the following revised type/value model:

* `WinKind = FOUGHT | FUSENSHO`
* `WinPolicy = FOUGHT_ONLY | CREDITED`
* `BashoBasis = SELECTED | CONTAINING`
* `BoutBasis = EXPECTED | AVAILABLE`

This reorganisation gives the project:

* clearer domain language
* correct separation between categories and policies
* a coherent replacement for the current terminology
* a stable conceptual framework for later extension

without yet committing the application to any new metric behaviour.

# The plan

### Phase 1: reorganise the type system only

Do not add new behaviour yet.

Just replace the old vocabulary and structure with the new vocabulary and structure:

* introduce the three types/classes
* refactor the existing code to use them
* preserve current semantics exactly

So at this stage you are not “adding the third dimension” in implementation terms. You are only making space for it.

### Phase 2: prove semantic equivalence

Run through the codebase and replace the two old axes with the new model, but in such a way that:

* calculations remain the same
* CSV outputs remain the same in substance
* the web page shows the same numbers and ordering

This is the crucial checkpoint.

The question here is:

> can we improve the conceptual model without changing the visible behaviour?

If yes, you have earned the right to proceed.

### Phase 3: add the third dimension

Only after the refactor is stable and behaviour-preserving do you extend the engine/view/publication model to include the new bout basis axis.

That way, when behaviour changes, you know it is because of the new feature, not because of the renaming/restructuring.

---

# Why this is the right order

Because you actually have **two separate jobs**:

## Job A: repair the language and class structure

This is about clarity, maintainability, and getting rid of muddy notions like:

* `WinsMode.REAL`
* `WinsMode.ALL`
* `presence`

## Job B: add new capability

This is about expected vs available bout opportunity.

If you combine A and B in one step, then every failure becomes ambiguous:

* did the result change because the model changed?
* because the enum semantics changed?
* because ranking keys changed?
* because a field got renamed incorrectly?
* because the JS is now reading the wrong column?

Your staged plan avoids that.

---

# What Phase 1 should contain

I would now define the target as:

```python
class WinKind(Enum):
    FOUGHT = auto()
    FUSENSHO = auto()


class WinPolicy(Enum):
    FOUGHT_ONLY = auto()
    CREDITED = auto()

    def includes(self) -> set[WinKind]:
        ...


class BashoBasis(Enum):
    SELECTED = auto()
    CONTAINING = auto()


class BoutBasis(Enum):
    EXPECTED = auto()
    AVAILABLE = auto()
```

But in Phase 1, `BoutBasis` exists only as part of the vocabulary reorganisation. It is not yet used to drive any new calculations.

That is important.

You are not implementing the third axis yet. You are just declaring the taxonomy that will later host it.

---

# What “identical output” should mean

I think you should be strict here.

After the Phase 1 refactor, the following should remain identical:

* published CSV values
* published JSON sidecars, unless renamed fields force harmless contract edits
* row ordering
* positions
* visible web-page values
* visible labels, unless you deliberately postpone label changes too

If possible, even better would be:

* same datasets loaded by the page
* same screenshots of the page for a few standard test cases

The ideal is to prove that the refactor is **purely conceptual/internal**.

---

# One subtle point

You said:

> go through the existing code changing the two old types/values to the new ones

I would slightly refine that.

There are really **two old axes in use**, but only one is presently formalised as a type in the code:

* old win axis: `WinsMode.REAL/ALL`
* old basho basis axis: implicit in names like `window` and `presence`

So Phase 1 should include both:

## 1. Formal replacement of `WinsMode`

Introduce `WinKind` and `WinPolicy`, and adapt logic accordingly.

## 2. Formal naming cleanup of basho basis

Replace `window` / `presence` terminology with `selected` / `containing` in the relevant names and comments.

This second part may not require a controlling enum immediately, but I think it is worth introducing `BashoBasis` anyway so the model is complete.

---

# My recommended phased proposal

## Proposal

The next change should be carried out in three deliberately separate phases.

### Phase 1 — Type/class reorganisation only

Revise the standings vocabulary and type structure so that the model explicitly recognises three axes:

* win category / win policy
* basho basis
* bout basis

This phase is structural only. No new metric behaviour is added.

Its purpose is to replace ambiguous or weak terminology with a clearer internal model.

### Phase 2 — Behaviour-preserving refactor

Refactor the existing engine, derived metrics, publisher outputs, and browser integration so that they use the new types and names while preserving current behaviour.

Success criterion:

> the published outputs and browser page remain substantively identical to the current system.

Only when this equivalence is demonstrated should further extension proceed.

### Phase 3 — Add the third dimension

Extend the model and outputs so that bout basis (`EXPECTED` / `AVAILABLE`) becomes an active analytical dimension rather than merely a declared one.

This phase introduces the first intentional behavioural change.

---

# Why this is strong

It gives you:

* conceptual cleanup first
* a stable checkpoint
* a clean diff between “refactor” and “new feature”
* simpler testing
* much lower risk to the PL

And it fits your stated goal of a **contained extension** perfectly.
