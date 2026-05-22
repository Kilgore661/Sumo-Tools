# **infra**

## 1. Status of this Document

This document is a reconstruction of the current `infra` subsystem, derived from existing module documentation and the implementation.

It is not assumed to be a definitive source of truth. The module documents and the codebase may disagree with each other and with this account in places. Such discrepancies should be treated as useful signals: they may indicate gaps in documentation, drift in implementation, or errors in interpretation.

The aim of this document is to provide a coherent, system-level view of `infra` as it appears to operate today. It should be read as a working model, to be tested against the code and refined over time.

Terminology is standardised here where possible, but may not yet match all existing module names or documentation.

---

## 2. Introduction

The `infra` layer contains the components responsible for maintaining a complete, validated, and locally available representation of historical basho data, and for making that data efficiently accessible to downstream consumers.

Although grouped under `infra`, these components do not form a general-purpose infrastructure layer in the abstract. In the current system, they operate together as a single subsystem centred on the **Tracker**. The remaining components exist to support the Tracker in fulfilling its responsibility: maintaining a complete and up-to-date local corpus.

At its core, the system enforces a simple invariant:

> There exists a current, internally consistent `History` model representing all known data, along with a canonical persisted form from which that model can be reconstructed.

To maintain this invariant, the system operates as a pipeline under the coordination of the Tracker:

* data is **downloaded** from upstream sources
* raw inputs are **parsed and normalised** into the domain model (`History`)
* the model is **persisted** in a canonical, reversible format
* the persisted state may be **materialised into a cache** for efficient reuse

Each stage has a clearly bounded responsibility:

* upstream data is the source of raw truth
* the `History` model is the source of semantic truth
* the canonical representation is the source of durable truth
* the cache is an optimisation layer and is not authoritative

The Tracker governs this process by determining what data should exist, identifying gaps or inconsistencies, and initiating the work required to bring the system into a complete and current state.

The system is designed to tolerate incomplete upstream data, incremental updates, and repeated processing, while ensuring that any materialised `History` instance is internally consistent and reconstructible from persisted state.

---

## 3. System Overview

The infra subsystem is organised around the Tracker, which acts as the coordinating component responsible for maintaining a complete and current local corpus of basho data.

The remaining components exist to support the Tracker in this role:

Downloader — acquires raw upstream data (currently HTML)
Parser — transforms raw data into a valid History model
Serialiser — persists and reconstructs the model in canonical form
Cache — provides an in-memory snapshot for efficient access

These components form a pipeline, executed under the direction of the Tracker:

Tracker → Downloader → Parser → History → Serialiser → Cache

The flow of data is forward, but the flow of control originates with the Tracker:

the Tracker determines which basho require processing
the Downloader retrieves the corresponding raw data
the Parser incorporates that data into a valid History
the Serialiser persists the updated model as the canonical representation
the Cache may materialise the persisted state for efficient reuse

The components are not peers in a symmetric pipeline. The Tracker governs the process, while the other components perform specialised transformations or storage functions within clearly defined boundaries.

These boundaries are strict:

the Downloader does not interpret data
the Parser does not decide what data should be fetched
the Serialiser does not define the structure of the model
the Cache does not introduce or modify state

This separation allows the system to be understood as a sequence of transformations—acquisition, interpretation, persistence, and access—coordinated by a single component responsible for completeness and currency.

---

## 4. Core Concepts and Terminology

This section defines the core concepts and terms used throughout the `infra` layer. These definitions are normative and apply across all components.

---

### 4.1 History

**`History`** is the canonical in-memory domain model representing all known basho data.

It is the primary semantic representation of the system. All interpretation of upstream data is expressed in terms of `History`, and all downstream processes operate on or derive from it.

A valid `History` instance is:

* internally consistent
* complete with respect to the data it contains
* structured according to the domain model

The **Parser owns `History`**. It defines:

* the structure of the model
* the invariants that must hold
* what constitutes a valid instance

---

### 4.2 BashoState, Banzuke, Summary

`History` is composed of domain-specific substructures, including:

* **BashoState** — represents the state of a single basho
* **Banzuke** — represents ranking information
* **Summary** — represents aggregated or derived information

These are part of the domain model defined by the Parser and inherit its invariants. They are not independently versioned or persisted outside the context of `History`.

---

### 4.3 Canonical Representation

The **canonical representation** is the durable, on-disk form of the `History` model.

It is:

* a complete representation of `History`
* reversible (it can be used to reconstruct `History` without loss)
* stable across runs

In the current system, the canonical representation is implemented as a **zip-backed JSON structure**.

The **Serialiser owns the canonical representation**. It defines:

* the on-disk format
* how `History` is transformed to and from that format
* compatibility and evolution of the stored form

The canonical representation is the source of durable truth in the system.

---

### 4.4 Cache

The **cache** is a materialised, read-only snapshot of the canonical representation, held in memory for efficient access.

It is:

* fully derived from the canonical representation
* non-authoritative
* replaceable without loss of information

The cache exists solely to avoid repeated reconstruction of `History` from persistent storage.

The **Cache component owns the cached state**, including:

* how the snapshot is materialised
* how it is stored in memory
* how it is exposed to consumers

The cache does not define or modify the structure of `History`.

---

### 4.5 Downloader

The **Downloader** is responsible for acquiring raw upstream data.

It operates at the level of byte retrieval and performs no interpretation of the data it fetches. In the current system, this consists of downloading HTML.

The Downloader owns:

* the mechanism by which data is fetched
* the mapping from identifiers (e.g. basho) to upstream resources

It does not:

* parse or interpret data
* enforce domain constraints
* produce `History` or any part of the domain model

---

### 4.6 Tracker

The **Tracker** is responsible for determining what data should exist locally and managing completeness over time.

It maintains a view of:

* which basho records are known
* which are missing or incomplete
* which require updating or retrying

The Tracker owns the system’s **completeness state**, including:

* planning and scheduling of downloads
* retry behaviour within active windows
* decisions about when the local corpus is up to date

It does not interpret raw data or construct the domain model.

---

## 5. Component Responsibilities

The `infra` subsystem is organised around the **Tracker**, which is the top-level coordinating component. The remaining components exist to support the Tracker in maintaining a complete and current local corpus.

Each component has a clearly defined responsibility and operates within strict boundaries. Components interact through well-defined inputs and outputs, and no component is authoritative outside its domain of ownership.

---

### 5.1 Tracker

**Purpose**
The Tracker governs the system. It determines what data should exist locally and ensures that the corpus becomes and remains complete over time.

**Owns**

* completeness state
* knowledge of which basho are present, missing, or incomplete

**Responsibilities**

* identify missing or incomplete data
* execute update cycles to restore completeness
* schedule and trigger downloads
* manage retry behaviour within active windows
* determine when the local corpus is up to date

A successful update cycle results in all required data being incorporated into `History` and persisted as the canonical representation.

**Inputs**

* current state of the local corpus (implicit or derived)

**Outputs**

* instructions to download specific basho
* initiation of downstream processing

**Does not**

* download data
* parse or interpret data
* define the structure of `History`
* define persistence format

**Current limitation**
The Tracker does not currently ensure that the Cache reflects the latest persisted state after an update cycle.

---

### 5.2 Downloader

**Purpose**
The Downloader acquires raw upstream data.

**Owns**

* data acquisition mechanisms
* mapping from basho identifiers to upstream resources

**Responsibilities**

* fetch raw data (currently HTML)
* handle network and retrieval concerns

**Inputs**

* instructions from the Tracker specifying what to download

**Outputs**

* raw, uninterpreted data

**Does not**

* interpret or parse data
* enforce domain constraints
* construct `History`

---

### 5.3 Parser

**Purpose**
The Parser constructs and maintains the `History` model from raw data.

**Owns**

* the structure and invariants of `History`

**Responsibilities**

* interpret raw data
* construct or update `History`
* enforce model correctness and consistency
* reject or fail on invalid data

**Inputs**

* raw data from the Downloader
* existing `History` (for incremental updates, where applicable)

**Outputs**

* a valid `History` instance

**Does not**

* determine what data should be fetched
* manage persistence strategy
* define storage format
* manage caching

---

### 5.4 Serialiser

**Purpose**
The Serialiser provides durable storage for the `History` model.

**Owns**

* the canonical representation

**Responsibilities**

* convert `History` to canonical representation
* reconstruct `History` from stored form
* manage format compatibility and evolution

**Inputs**

* valid `History` instances

**Outputs**

* canonical representation (on disk)
* reconstructed `History`

**Does not**

* define the structure of `History`
* interpret raw upstream data
* decide when persistence should occur
* manage cache lifecycle

---

### 5.5 Cache

**Purpose**
The Cache provides efficient access to the current system state.

**Owns**

* the materialised in-memory snapshot

**Responsibilities**

* load `History` from the canonical representation
* materialise and store it in memory
* provide read access to consumers

**Inputs**

* canonical representation from the Serialiser

**Outputs**

* in-memory snapshot of `History`

**Does not**

* modify `History`
* persist data
* define model structure
* act as a source of truth

**Current limitation**
The Cache is not automatically refreshed when the canonical representation is updated. As a result, it may temporarily diverge from persisted state.

---

## 5.6 Interaction Model

The system operates as a pipeline coordinated by the Tracker:

* the Tracker determines required work and executes update cycles
* the Downloader retrieves raw data
* the Parser produces a valid `History`
* the Serialiser persists the result as the canonical representation
* the Cache may materialise the persisted state for efficient access

The flow of **control** originates with the Tracker, while the flow of **data** proceeds through the pipeline.

Completion of an update cycle is defined at the point where the canonical representation has been successfully updated. Cache refresh is not currently part of this cycle and may occur separately.

---

# **6. Boundaries and Invariants**

This section defines the constraints that govern the behaviour of the `infra` subsystem. These constraints are normative. A violation of a stated invariant indicates that the system is incorrect.

---

## 6.1 Core Invariants

### 6.1.1 History Validity

All `History` instances produced by the Parser are internally consistent and satisfy the domain model.

Invalid or partially valid `History` states must not be produced. If parsing fails, the update cycle terminates without modifying the existing canonical representation.

---

### 6.1.2 Persistence Fidelity

The canonical representation fully and faithfully represents `History`.

A `History` instance reconstructed from the canonical representation is equivalent to the original model. No information is lost or altered in serialisation.

---

### 6.1.3 Completion Invariant

A successful update cycle results in a canonical representation that includes all required basho data.

Completeness is defined at the level of persistence. The system is considered complete when all required data has been incorporated into `History` and serialised.

---

### 6.1.4 Cache Derivation

The Cache is derived exclusively from the canonical representation.

The Cache must not be constructed directly from in-memory `History` or any other intermediate state.

---

## 6.2 Non-Invariants

The following conditions are explicitly not guaranteed by the current system:

### 6.2.1 Cache Freshness

The Cache is not guaranteed to reflect the latest canonical representation.

After a successful update cycle, the Cache may remain stale until it is explicitly refreshed.

---

### 6.2.2 Immediate Consistency

Different components may observe different system states at a given time.

In particular, the Cache may not reflect the most recent persisted state.

---

## 6.3 Component Boundaries

### 6.3.1 Parser and Serialiser

The Parser defines the structure and correctness of `History`.
The Serialiser defines its representation.

The Serialiser is strictly mechanical. It must not:

* alter the structure of the model
* introduce or repair inconsistencies
* apply domain logic

---

### 6.3.2 Serialiser and Cache

The Cache is strictly downstream of the Serialiser.

The Cache:

* loads from the canonical representation
* does not modify or reinterpret the model
* does not introduce new state

---

### 6.3.3 Tracker and Domain Model

The Tracker governs execution but does not interpret domain data.

It does not:

* define or validate the structure of `History`
* perform parsing
* depend on internal model semantics beyond what is required to determine completeness

---

## 6.4 Authority Hierarchy

Authority in the system is strictly ordered:

1. **History** — semantic truth
2. **Canonical representation** — durable truth
3. **Cache** — materialised view

No component may override a higher level of authority:

* persistence does not redefine the model
* cache does not override persisted state

---

## 6.5 Allowed Transformations

The system permits only the following transformations:

* raw data → Parser → `History`
* `History` → Serialiser → canonical representation
* canonical representation → Cache → in-memory snapshot

No other transformation paths are part of the system design.

In particular:

* the Cache must not modify `History`
* the Serialiser must not introduce domain logic
* the Parser must not bypass persistence

---

## 6.6 Failure Boundaries

### 6.6.1 Parser Failure

If parsing fails:

* the update cycle terminates
* the canonical representation remains unchanged

No partial or invalid `History` is persisted.

---

### 6.6.2 Serialisation Failure

If serialisation fails:

* the existing canonical representation is preserved
* no partial or corrupted state is written

---

### 6.6.3 Cache State

The system remains correct in the absence of a Cache, or when the Cache is stale.

Cache state does not affect correctness.

---

## 6.7 History Lifecycle

Each successful update cycle produces a complete and valid `History` which is then persisted.

`History` is not updated incrementally across cycles. Each cycle results in a coherent model that fully represents the current known corpus.

---

## 7. Lifecycle of a Basho

The lifecycle of a basho describes how it is acquired, incorporated into the system, and made available for use. This lifecycle is governed by the Tracker and executed through repeated update cycles.

A basho enters the lifecycle when it is identified by the Tracker as part of the required data set.

---

### 7.1 Acquisition

During an active period, the Tracker executes update cycles in which it attempts to acquire the data for each day of the basho.

For each day:

* the Downloader retrieves the corresponding HTML
* if retrieval fails, the attempt is retried in subsequent update cycles

The Tracker operates at the level of individual days, incrementally attempting to obtain a complete set of results for the basho.

---

### 7.2 Parsing and Model Construction

Once the required data has been successfully acquired, the Parser constructs a `History` representing the current state of all known basho.

Parsing is all-or-nothing with respect to persistence:

* if parsing succeeds, a valid `History` is produced
* if parsing fails, the update cycle terminates and no changes are persisted

The system does not persist partial or invalid states.

---

### 7.3 Persistence

On successful parsing, the resulting `History` is serialised and stored as the canonical representation.

At this point, the basho is considered complete within the system, in the sense that its data is:

* incorporated into the domain model
* persisted as durable state

Completeness is defined at the level of the canonical representation.

---

### 7.4 Visibility

The persisted state may be materialised into the Cache to make it available to consumers.

A basho becomes visible to consumers only once it is present in the Cache. Since cache refresh is not currently part of the update cycle, there may be a delay between persistence and visibility.

---

### 7.5 Reprocessing

During an active period, the same basho may be processed repeatedly across update cycles as new data becomes available or previous retrieval attempts succeed.

Each cycle follows the same lifecycle:

* acquisition
* parsing
* persistence

The system does not update `History` incrementally across cycles. Each successful cycle produces a complete and coherent model.

---

### 7.6 Limitations

The lifecycle described above reflects the behaviour of the system, but has two important limitations:

* **Cache divergence**
  The Cache may not reflect the latest persisted state until it is refreshed.

* **Upstream mutability**
  Upstream data may change after a basho has been processed. The system does not automatically detect or incorporate such changes once the basho has passed its active period.

---

## 8. Failure and Recovery Model

The system is designed to tolerate failures in data acquisition and processing while preserving the integrity of the canonical representation. Failures are handled by terminating the current update cycle and retrying in subsequent cycles, subject to the constraints of the Tracker.

---

## 8.1 Acquisition Failures

Failures in downloading upstream data are expected and handled as part of normal operation.

If a download attempt for a given day fails:

* the failure is recorded implicitly by the absence of the required data
* the Tracker retries the download in subsequent update cycles

Acquisition failures do not affect existing state. No partial or invalid data is introduced into the system as a result of failed downloads.

---

## 8.2 Parser Failures

If parsing fails during an update cycle:

* the update cycle terminates
* no new `History` is persisted
* the existing canonical representation remains unchanged

Parser failure is treated as a hard failure for the current cycle. The system does not attempt to persist partial results.

Subsequent update cycles may retry parsing after additional data has been acquired.

---

## 8.3 Serialisation Failures

If serialisation fails:

* the existing canonical representation is preserved
* no partial or corrupted representation is written

Serialisation failure prevents completion of the update cycle but does not compromise existing persisted state.

---

## 8.4 Cache State and Failures

The Cache is not part of the correctness boundary of the system.

If the Cache is:

* absent
* stale
* or fails to initialise

the system remains correct, provided the canonical representation is intact.

Cache refresh is currently a separate operational step. As a result, consumers may observe stale data even after a successful update cycle.

---

## 8.5 End-of-Window Incompleteness

The system operates within a bounded active period for each basho.

If, at the end of this period:

* some required data has not been successfully acquired

then:

* the Tracker signals that the basho is incomplete
* no further attempts are made to retrieve missing data for that basho

The system accepts incomplete basho as final for the purposes of persistence.

---

## 8.6 Recovery Model

Recovery is achieved through repeated execution of update cycles within the active basho window.

* transient acquisition failures are retried
* parsing is retried once sufficient data is available
* no manual intervention is required for normal recovery within the active window

Outside the active window, no automatic recovery is performed.

---

## 8.7 Failure Containment

Failures are contained within the current update cycle.

At all times:

* the canonical representation remains valid
* previously persisted data is preserved
* no partial or inconsistent state is exposed as durable truth

This ensures that the system either advances to a new valid state or remains at the previous valid state.

---

## 9. Performance Model

The `infra` subsystem is designed with a clear separation between correctness and performance.

Correctness is defined entirely by the canonical representation. Performance optimisations must not affect the validity or integrity of the system.

---

## 9.1 Persistence as the Correctness Boundary

The canonical representation provides a complete and durable representation of the system state.

All correctness guarantees are defined at this boundary:

* a valid `History` is persisted
* the canonical representation can reconstruct that state

Operations that rely solely on persistence are correct but may be expensive.

---

## 9.2 Cost of Reconstruction

Reconstructing `History` from the canonical representation requires:

* reading and decompressing the stored data
* deserialising JSON into domain objects

This process may be computationally expensive, particularly when performed repeatedly or concurrently.

---

## 9.3 Role of the Cache

The Cache exists to avoid repeated reconstruction of `History`.

It provides:

* a materialised in-memory snapshot of the canonical representation
* fast access for consumers

The Cache improves performance by trading freshness for speed.

---

## 9.4 Cache Characteristics

The Cache is:

* **derived** — built exclusively from the canonical representation
* **read-only** — does not modify the underlying model
* **replaceable** — can be discarded and rebuilt at any time
* **non-authoritative** — does not define system correctness

Because the Cache is decoupled from the update cycle, it may temporarily diverge from the persisted state.

---

## 9.5 Consistency Trade-off

The system deliberately allows a trade-off between:

* **freshness** — immediate reflection of updates
* **performance** — efficient repeated access

In the current design:

* persistence is updated as part of the update cycle
* cache refresh is a separate operation

This allows consumers to continue using an existing cache even after new data has been persisted.

---

## 10. Non-Goals and Exclusions

The `infra` subsystem is responsible for acquiring, constructing, persisting, and exposing historical basho data. It deliberately excludes a number of concerns that are outside its scope.

These exclusions define the boundaries of the system and prevent responsibilities from drifting across components.

---

## 10.1 No Upstream Authority

The system does not control or influence upstream data sources.

It:

* retrieves data as it exists upstream
* does not attempt to correct or override upstream content
* does not enforce consistency beyond what is expressed in the domain model

Upstream changes are not automatically detected or incorporated once a basho has passed its active processing window.

---

## 10.2 No Late Data Reconciliation

The system does not attempt to repair or reconcile incomplete basho after the active window has ended.

If data is missing at the end of the basho:

* the incompleteness is recorded or signalled
* no further automatic attempts are made to retrieve missing data

Manual intervention (such as clearing downloaded data) may be required to force reprocessing.

---

## 10.3 No Incremental Model Updates

The system does not update `History` incrementally across update cycles.

Each successful update cycle produces a complete and coherent `History` which replaces the previous state.

There is no concept of partially updated or progressively mutated domain state.

---

## 10.4 No Cache Coherency Guarantees

The system does not guarantee that the Cache reflects the most recent persisted state.

Cache refresh is not part of the update cycle and is currently an explicit operational step.

Consumers of the Cache must tolerate temporary staleness.

---

## 10.5 No Cross-Component Responsibility Leakage

Each component operates within its defined boundary:

* the Parser does not manage persistence
* the Serialiser does not interpret domain data
* the Cache does not modify state
* the Tracker does not perform parsing or define model structure

The system does not support components taking on responsibilities outside their domain.

---

## 10.6 No General-Purpose Infrastructure Guarantees

Although grouped under `infra`, the subsystem is not intended to provide general-purpose infrastructure services.

It is specifically designed to support the Tracker in maintaining the basho corpus.

Other tools or subsystems may require different infrastructure, and should not assume that the components in `infra` are reusable in a general context.

---

## 11. Relationship to Module Documentation

This document provides a system-level view of the `infra` subsystem. It defines the roles of components, the flow of data, and the invariants that govern correctness.

The module-level documents provide detailed accounts of individual components. These documents should be read as complementary to this one.

---

## 11.1 Role of This Document

This document defines:

* the overall architecture of the subsystem
* the responsibilities and boundaries of each component
* the invariants that must hold across the system
* the lifecycle of data as it moves through the pipeline

It is normative in intent, describing how the system is expected to behave as a coherent whole.

---

## 11.2 Role of Module Documentation

The module-level documents (Tracker, Parser, Serialiser, Cache) describe:

* internal structure and behaviour of individual components
* implementation details and design decisions
* component-specific terminology and concepts

These documents may vary in completeness and may reflect the state of the system at different points in its development.

---

## 11.3 Consistency and Authority

Where possible, the module-level documents should be consistent with the system-level model defined here.

In cases of discrepancy:

* this document defines the intended architecture
* module documentation may reflect implementation details, historical artefacts, or incomplete descriptions

Such discrepancies should be treated as candidates for review and resolution.

---

## 11.4 Known Sources of Divergence

The current documentation set includes known areas where module-level descriptions may not fully align with the system model:

* **Serialiser legacy structure**
  The Serialiser retains structure related to earlier annotation models which are no longer conceptually required.

* **Cache lifecycle integration**
  The Cache is not currently integrated into the Tracker’s update cycle, despite being downstream of persistence.

* **Naming inconsistencies**
  The `memory` module name does not reflect its role as a Cache.

These divergences do not invalidate the system model, but indicate areas where the implementation and documentation may require alignment.

---

## 11.5 Use of This Document

This document should be used:

* as a reference for understanding how components fit together
* as a basis for evaluating changes to the system
* as a guide for identifying inconsistencies or gaps in module-level documentation

It is not a replacement for module-level documentation, but a framework within which those documents can be interpreted.

---

Good—this is where the audit turns into something actionable.

---

# **12. Next Steps**

---

## 12. Next Steps

This section captures areas where the current system or documentation diverges from the intended model, along with potential directions for improvement. These are not part of the system definition, but represent work identified through analysis of the current state.

---

## 12.1 Integrate Cache Refresh into Update Cycle

**Issue**
The Cache is not refreshed as part of the Tracker’s update cycle. After a successful update, the canonical representation may change without being reflected in the Cache.

**Impact**

* consumers may observe stale data
* correctness and visibility are decoupled

**Next Step**
Integrate cache refresh into the update cycle so that, upon successful persistence, the Cache is either:

* refreshed automatically, or
* explicitly invalidated and rebuilt

---

## 12.2 Replace Manual Cache Restart Warning

**Issue**
Cache refresh currently depends on operator intervention (e.g. restarting after zip changes).

**Impact**

* introduces operational fragility
* relies on manual correctness

**Next Step**
Replace manual warnings with system-enforced behaviour, such as:

* automatic cache invalidation
* detection of canonical representation changes

---

## 12.3 Simplify Serialiser Structure

**Issue**
The Serialiser retains structural complexity related to earlier annotation models that are no longer required.

**Impact**

* increases cognitive overhead
* risks misrepresenting the current domain model

**Next Step**
Refactor the Serialiser to reflect the current model in which all `History` instances are fully annotated, removing legacy transitional structures.

---

## 12.4 Align Naming: `memory` → `cache`

**Issue**
The module name `memory` does not reflect its role as a Cache.

**Impact**

* creates conceptual mismatch
* increases confusion when reading the system

**Next Step**
Rename the module to reflect its function more accurately (`cache`), and update documentation accordingly.

---

## 12.5 Clarify Tracker Update Cycle Documentation

**Issue**
The Tracker doc does not explicitly state that successful update cycles result in persistence of `History`.

**Impact**

* leaves an implicit step in a critical process
* weakens the connection between Tracker and persistence

**Next Step**
Update the Tracker documentation to explicitly include serialisation and persistence as part of a successful update cycle.

---

## 12.6 Document Basho Lifecycle in Tracker

**Issue**
Detailed basho scheduling and lifecycle behaviour was not previously documented.

**Impact**

* key operational assumptions are implicit
* difficult to reason about system behaviour without reading code

**Next Step**
Include basho schedule and update behaviour in the Tracker documentation (as described in Section 7).

---

## 12.7 Reconcile `infra` Scope

**Issue**
The `infra` module is named as general infrastructure, but currently exists primarily to support the Tracker.

**Impact**

* conceptual mismatch between name and role
* potential confusion if additional tools are introduced

**Next Step**
Revisit the role of `infra` if additional applications are developed, or clarify its current scope as Tracker-specific infrastructure.

---

## 12.8 Strengthen Cross-Document Consistency

**Issue**
Module-level documentation varies in completeness and terminology, having been developed independently.

**Impact**

* inconsistencies in language and assumptions
* increased effort required to reconcile documents

**Next Step**
Align module-level documentation with the system model defined here, ensuring consistent terminology and explicit connections between components.
