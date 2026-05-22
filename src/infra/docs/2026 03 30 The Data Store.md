Here is a draft **Requirements Clarification** document, written to be concise, stable, and aligned with the decisions we’ve made.

---

# Requirements Clarification

## A. Previous Perspective and Issues

### A.1 Previous Perspective

The system has so far been viewed as a **tracker pipeline**, responsible for:

* determining required data
* downloading source data
* parsing and rebuilding history
* persisting results
* maintaining cache
* performing analysis
* producing outputs

This view treated all stages as part of a single continuous process.

---

### A.2 Issues with This Perspective

This led to several ambiguities:

#### 1. Blurred Responsibilities

* No clear distinction between:
  
  * maintaining canonical data
  * deriving intermediate structures
  * producing application-specific outputs

#### 2. Ambiguous “Cache”

* “Cache” was used without a clear definition:
  
  * Was it optional or required?
  * Was it authoritative or derived?
  * Was it part of the system’s core responsibility?

#### 3. Analysis Mixed into Core

* Analytical outputs (e.g. reports, ratings) were treated as part of the main pipeline
* This made it unclear what the system fundamentally *owns*

#### 4. Mechanism-driven Terminology

* Terms such as “tracker”, “cache”, “daemon”, “service” introduced unintended assumptions about implementation and lifecycle

---

### A.3 Key Realisation

> The system’s primary responsibility is to maintain a canonical **sumo data store**.

This replaces the “tracker pipeline” as the central concept.

---

## B. Revised Requirements (Prescriptive)

### B.1 Definition: Sumo Data Store

> The sumo data store is the current authoritative in-memory representation of sumo history and its core structural data.
> It is maintained by a single program and may also have persisted and shared-memory representations.
> It does not imply a database, service, or query engine.

---

### B.2 Core Responsibility

The program shall:

1. Determine the required coverage of sumo history
2. Ensure required source data is available
3. Rebuild the canonical data store (`History`)
4. Publish representations of that data store

---

### B.3 Representations of the Data Store

The data store shall be published in two forms:

#### 1. Durable Representation

* A persisted form (currently a zip file)
* Used for storage and interchange

#### 2. Runtime Representation

* An in-memory form of the data store
* Currently implemented using shared memory
* Used by other tools at runtime

These are **representations of the same data store**, not separate components.

---

### B.4 Structure of the Data Store

The data store currently consists of:

* `History` (canonical state)

It may later include:

* **Auxiliaries**: maintained, derived components that are broadly reusable

Example (likely future auxiliary):

* `EloRatings`

Auxiliaries must:

* be derived from the canonical history
* be broadly useful across multiple tools
* remain explicitly dependent on `History`

---

### B.5 Auxiliaries

Auxiliaries are:

* **materialized derived data**
* maintained for efficiency and reuse
* conceptually equivalent to functions of `History`, but stored

Example:

```python
history.auxiliaries.elo_ratings
```

Their derived nature must remain explicit (e.g. via versioning or provenance).

---

### B.6 Tools

The system distinguishes **Tools** from the data store.

Tools:

* consume the data store (and possibly auxiliaries)
* produce application-specific outputs
* are not part of the data store

Examples:

* website generator (depends on `History` and `EloRatings`)
* future tools as required

The program is **not responsible** for implementing or maintaining tools.

---

### B.7 Explicit Exclusions

The program shall **not**:

* produce application-specific outputs (e.g. websites, reports)
* embed analytical tools into the core data store
* assume any service/server/API behaviour
* expose query interfaces or database semantics

---

### B.8 Replacement of “Tracker”

The concept of a “tracker” is replaced.

The system is now defined as:

> a program that maintains a canonical sumo data store and publishes its representations.

---

## C. Structural Implications (Code-Level)

### C.1 Core Modules

A possible structure:

```text
data_store/
    history.py
    auxiliaries.py
    elo_ratings.py (future)

maintenance/
    planner.py
    downloader.py
    parser.py
    update_cycle.py

tools/
    website.py
```

---

### C.2 Data Structures

Minimal form:

```python
class DataStore:
    history: History
    auxiliaries: Auxiliaries
```

Where:

```python
class Auxiliaries:
    elo_ratings: EloRatings | None
```

---

### C.3 Update Cycle

The update cycle shall:

1. Determine required coverage
2. Ensure source data exists
3. Rebuild `History`
4. Publish durable representation (zip)
5. Publish runtime representation (shared memory)
6. Optionally refresh auxiliaries

It shall not invoke tools.

---

### C.4 Tools Layer

Tools exist separately:

```python
# tools/website.py

def make_website(history: History, elo_ratings: EloRatings):
    ...
```

They:

* depend explicitly on required inputs
* are decoupled from the data store maintenance process

---

## D. Summary

The system is redefined from:

> a pipeline that downloads, parses, and produces outputs

to:

> a program that maintains an authoritative sumo data store and publishes representations of it

This provides:

* clear responsibility boundaries
* separation of data, derivation, and application
* flexibility for future tools without coupling them to the core system

---

Appendix: Design Principles

1. The primary responsibility is to maintain the sumo data store

The program exists to maintain a current authoritative sumo data store.
It is not defined by its scheduling mechanism, storage mechanism, or downstream outputs.

2. Canonical state is distinct from its representations

The data store and its representations are different things.

The data store is the maintained content.
Durable and runtime forms are representations of that same content.

The current zip file and shared-memory form are therefore not separate stores, but separate representations of one store.

3. History is canonical; auxiliaries are derived

History is the canonical core of the data store.
Any auxiliary component must be explicitly derived from History.

Auxiliaries may be materialized and maintained for efficiency, but their derived status must remain clear.

4. Only broadly reusable derived data belongs in the store

A derived component should be promoted into the maintained data store only if it is broadly useful across multiple tools.

This excludes tool-specific or speculative outputs from the core system.

5. Tools are separate from store maintenance

Tools consume the data store and possibly its auxiliaries, but they are not part of store maintenance.

Examples of tools include:

website generation
reports
forecasts
other application-specific outputs

These may depend on the store, but do not define it.

6. The system should not imply more architecture than is required

Terms that carry hidden assumptions — such as “cache”, “daemon”, “service”, or “server” — should be avoided unless those assumptions are actually intended.

Project terminology should describe conceptual roles, not implementation mechanisms.

7. Representations and auxiliaries must not blur responsibility boundaries

Publishing the data store, maintaining runtime representations, and maintaining auxiliaries are part of store maintenance.

Producing application-specific outputs is not.

8. Completeness and correctness are enforced at maintenance boundaries

The maintained system should move only between valid states.

It should not expose:

partial rebuilds
half-published representations
stale mandatory representations after a claimed successful update
9. Future growth should occur by promotion, not by leakage

New derived data should begin life outside the core system.
Only when it proves stable, reusable, and broadly valuable should it be promoted into the maintained store as an auxiliary.

10. The conceptual model takes priority over the current implementation

Implementation details may change over time.
The conceptual structure should remain stable:

maintained data store
representations of that store
optional auxiliaries
separate tools
