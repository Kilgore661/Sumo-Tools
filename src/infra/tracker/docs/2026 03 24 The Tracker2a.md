#### 1. The Tracker

## 1.1 Overview

This document describes the **Tracker**, the current implementation of the Sumo Data Store Maintainer (SDSM).

The role of the Tracker is to maintain a local sumo data store that is complete, up to date, and consistent with the data available from sumodb.de.

At present, the maintained store consists of canonical `History` and its representations. Other derived artefacts or downstream products are not part of the maintained system unless explicitly promoted.

---

## 1.2 Purpose

The Tracker is a continuously running program that maintains a complete and up-to-date local copy of sumo data.

It ensures that:

- all required source data is available
- canonical `History` can be reconstructed from that data
- the maintained data store is published and usable

---

## 1.3 The maintained data store

The maintained data store is defined by canonical `History`.

This store exists in multiple forms:

- a **durable data store**, which is persisted (e.g. as a zip file)
- a **live data store**, which is the in-memory representation of the store

Both forms represent the same underlying data and are part of the maintained system.

The Tracker is responsible for ensuring that both forms are present and consistent.

---

## 1.4 Scope and boundaries

The Tracker is responsible for maintaining the data store itself.

It is not responsible for:

- application-level processing
- statistical analysis
- derived artefacts such as Elo ratings
- downstream products such as websites

Such things may consume the maintained data store, but they are not part of it unless explicitly promoted.

---

## 1.5 Growth by promotion

The maintained data store may be extended in future.

A derived artefact should begin life outside the maintained system. It should only be incorporated into the Tracker if:

> **it proves stable, broadly reusable, and valuable enough to guarantee as part of the maintained system**

This ensures that the core system remains focused and avoids premature commitment to application-specific functionality.

---

## 1.6 **Caveat**

At present, validation of the maintained data store is limited.

In practice, validation is effectively defined as the existence of the expected artefacts (e.g. durable and live data stores). No additional integrity or consistency checks are currently guaranteed.

Strengthening validation may be considered in future.

---

## 1.7 Summary

The Tracker maintains a canonical sumo data store.

At present, this consists of:

- `History` as the canonical core
- a durable data store
- a live data store

Other functionality remains outside the system unless explicitly promoted.

---

# 2. Specification

## 2.1 Basho lifecycle

Basho follow a fixed schedule:

- Each basho begins on the second Sunday of each odd-numbered month
- Each basho lasts for 15 days

A basho is therefore either:

- in progress (from its start date until the end of day 15), or
- complete (after the final scheduled day)

---

## 2.2 Overview

The tracker ensures that all required basho records are present and usable, and that the canonical History representation derived from them is up to date.

At any point in time, the system maintains:

- a complete and usable set of required source data
- a canonical zip representation consistent with that data

If required source data changes or is restored, the canonical zip must be rebuilt to reflect the current state.

The tracker does not perform partial or incremental updates to the canonical History. Instead, it rebuilds the representation from the complete set of required source data whenever necessary.

---

## 2.3 Required data

At any given time, the tracker defines a set of **required basho days** based on the current time and the basho lifecycle.

For each required basho day, the system must have sufficient raw data to support parsing and reconstruction of the canonical History.

In the current implementation, this requirement is realised as the presence of the following local HTML artifacts:

- **Daily results**  
  One file per required basho day
- **Current standings**  
  One file per distinct basho (year, month) represented in the required set

A required artifact is considered present if a corresponding local file exists at the expected location.

The tracker assumes that any existing file is valid. Files are treated as immutable once written. If a file is modified or corrupted outside the control of the tracker, the behaviour of the system is undefined.

A required artifact is considered missing if the corresponding file does not exist.

The tracker is responsible only for ensuring that all required artifacts exist. It does not validate file contents beyond successful retrieval.

---

## 2.4 Determining required data

At any given time, the tracker determines the set of required records based on the current time and the basho lifecycle.

For completed basho, all basho-day records are required.

For a basho that is in progress, only those days that should have occurred by the current time are required.

Future basho and future days within a basho are not required.

The tracker derives the set of required basho-day records from the current time and compares this with the set of existing local files.

The tracker supplies the full required set to the retrieval component, which determines which records are already present and which must be fetched.

---

## 2.5 Execution model

The tracker runs continuously and evaluates its state at regular intervals.

At any given time, the tracker is in one of the following states:

- DORMANT: no basho is in progress and no action is required
- READY: a basho is in progress and new data may become available
- ACTIVE: an update cycle is in progress
- RECOVERY: a previous retrieval attempt failed and must be retried

The tracker determines the current basho and derives its state from the current time and system conditions.

When in READY or RECOVERY, the tracker periodically evaluates whether new data may exist. If so, it enters ACTIVE and performs an update cycle.

Upon completion of an update cycle:

- SUCCESS returns the tracker to READY
- NO_NEW_DATA leaves the tracker in READY
- RETRIEVAL_FAILED moves the tracker to RECOVERY
- Any other failure is treated as fatal and causes termination

If the basho completes while the tracker is in RECOVERY and required data is still missing, the tracker aborts.

---

## 2.6 Update cycle

An update cycle consists of the following stages:

1. Determine the current required data set.

2. Attempt retrieval of all required source records.

3. If retrieval succeeds, determine whether the required source data has changed.

4. If the source data has changed:
   
   - rebuild the canonical History
   - serialise and store it as the canonical zip representation

5. If the source data has not changed:
   
   - retain the existing canonical zip

6. Ensure the live data store is present and consistent with the canonical History.
   
   Additional derived artefacts or application-level processes are not part of the maintained system at present.

Each update cycle produces one of the following outcomes:

- SUCCESS  
  All stages completed successfully and either:
  - new data was incorporated and the canonical zip was rebuilt, or
  - no changes were required and the maintained data store was already up to date
- NO_NEW_DATA  
  Retrieval succeeded but no required source data changed
- RETRIEVAL_FAILED  
  One or more required source records could not be obtained
- REBUILD_FAILED  
  The canonical History could not be rebuilt successfully
- PUBLISH_FAILED  
  The canonical zip could not be written or persisted
- LIVE_STORE_FAILED  
  The live data store could not be created, refreshed, or validated

Failures in optional external processes do not affect the update cycle outcome.

The outcome of the update cycle determines the subsequent behaviour of the tracker as defined in Section 2.5.

---

## 2.7 Recovery behaviour

If an update cycle fails, the tracker enters a **recovery condition**.

In this condition:

- some required data is presumed missing or unusable
- the tracker will attempt further update cycles to resolve the condition

The recovery condition persists until a successful update cycle occurs.

---

## 2.8 Retry behaviour

The tracker retries failed update cycles subject to the following rules:

- retries occur only while within the active window
- retries are repeated until either:
  - a successful update occurs, or
  - the active window ends

---

## 2.9 Terminal failure

If the active window ends while the tracker is still in a recovery condition:

> The tracker terminates with an error indicating that required data could not be obtained.

This represents a failure to meet the data completeness requirement within the allowed retry window.

---

## 2.10 Dormant behaviour

When outside the active window:

- the tracker performs no update cycles
- no retries are attempted
- the system remains idle until the next active window

---

## 2.11 Notes

- The specification does not define how data is retrieved (e.g. downloading).
- The specification does not define internal state names or implementation details.
- Timing parameters (e.g. trigger hour, polling interval) are implementation details.

---

## 

## 3. Design

### 3.1 Overview

The tracker is a continuously running program whose purpose is to maintain a complete and up-to-date local corpus of basho records and the maintained data store.

The design separates this into the following concerns:

- scheduling: deciding when the program should attempt an update
- planning: determining what data is required as of the current time
- retrieval: obtaining required source data
- reconstruction: rebuilding the canonical History representation
- publication: persisting the canonical zip representation
- live-store: ensuring the maintained data store is available in memory

This separation keeps time-based logic, data requirements, data acquisition, reconstruction, and runtime representation clearly distinct.

## **3.2 Main components**

The tracker system is composed of a set of cooperating components, each responsible for a distinct stage in the update pipeline. These components correspond directly to the concerns identified in Section 3.1.

### **Tracker (controller)**

The tracker is the top-level orchestrator. It runs continuously and is responsible for:

- determining whether the system is within an active basho window

- deciding when to initiate an update cycle

- managing runtime state (`DORMANT`, `READY`, `ACTIVE`, `RECOVERY`)

- interpreting update outcomes

- enforcing terminal failure if recovery is unresolved at the end of the active window

The tracker does **not** perform data retrieval, parsing, or persistence itself. It delegates all work to the update cycle.

---

### **Planner (requirements engine)**

The planner determines what data *should exist* at the current point in time.

Its responsibilities are:

- determining the current basho and day

- computing the set of required basho-day records

- distinguishing between required, missing, and future data

The planner defines the system’s notion of **completeness**. It is purely time-based and does not inspect file contents.

---

### **Downloader (retrieval component)**

The downloader (formerly “scraper”) is responsible for ensuring that all required source records exist locally.

Its responsibilities are:

- checking for the presence of required files

- downloading missing records

- rejecting unusable retrievals

- reporting success or failure for the retrieval stage

The downloader operates on a **set of required records**, not individual requests, and its outcome is treated as all-or-nothing for the update cycle.

---

### **Parser (reconstruction component)**

The parser is responsible for transforming the retrieved HTML corpus into a validated, model-compliant `History`.

Its responsibilities are:

- parsing current standings and daily results

- reconciling inconsistencies via FSMs

- constructing validated `BashoState` objects

- assembling the complete `History`

The parser enforces:

- identity consistency (`RikId`)

- rank correctness (`Chii`)

- internal structural validity

If parsing fails for any required basho, the rebuild stage fails.

---

### **Persistence (publication component)**

The persistence layer is responsible for producing the canonical representation of the data.

Its responsibilities are:

- serializing `History`

- writing the canonical zip representation

- ensuring the output reflects the current source data

The tracker treats this stage as mandatory:

- failure to write or persist the zip is a **fatal error**

- no partial or outdated zip is acceptable

---

### **Live-store (runtime representation)**

This stage is responsible for ensuring that the maintained data store is available in its **live (in-memory) form**.

Its responsibilities include:

- loading the canonical History into a live data store
- ensuring that the live data store is present and consistent with the canonical representation

The live data store is considered part of the maintained system:

- failure to create or refresh it is a **fatal error**

Additional derived artefacts (e.g. analysis outputs or application-specific data) are **not part of the maintained system at present**:

- they may consume the canonical data store
- they are not required for a successful update cycle
- failures in such processes do not affect system correctness

---

### **Update cycle (integration point)**

The update cycle coordinates all components into a single operation:

```text
Planner → Downloader → Parser → Persistence -> Live Store
```

It is responsible for:

- executing stages in order

- enforcing all-or-nothing success

- producing a single outcome (`SUCCESS`, `RETRIEVAL_FAILED`, etc.)

The tracker interacts only with the update cycle, not with individual components.

---

### **Design principle**

The system enforces a strict separation of concerns:

```text
Tracker     → when to act
Planner     → what is required
Downloader  → obtain data
Parser      → make it correct
Persistence → store it
Live store  → make the data store usable in memory
```

Each component has a single responsibility, and correctness depends on all stages succeeding.

---

### **Summary**

The tracker is not a single process but a coordinated pipeline of components:

- time-driven orchestration (Tracker, Planner)

- data acquisition (Downloader)

- data validation and reconstruction (Parser)

- canonical publication (Persistence)

- downstream usability (Live-store)

This structure aligns the implementation with the specification and ensures that:

> the system always produces a complete, validated, and usable representation of basho history.

---

### **3.3 Update flow (revised)**

A single update cycle is the fundamental unit of work performed by the tracker. It is a **deterministic, all-or-nothing pipeline** that ensures the system’s data is complete, consistent, and usable.

The update cycle proceeds through the following stages:

---

### **Stage 1 — Determine required data**

The planner computes the set of required basho-day records based on the current time and basho lifecycle rules.

This defines:

- which basho are complete

- which days within the current basho should exist

- which records are required vs future

The result is a complete specification of what data must be present for the system to be considered up to date.

---

### **Stage 2 — Retrieval**

The downloader attempts to ensure that all required records exist locally.

This includes:

- checking for missing files

- downloading missing records

- rejecting unusable retrievals

The retrieval stage is evaluated as a whole:

- **success**: all required records are present and usable

- **failure**: one or more required records could not be obtained

If retrieval fails, the update cycle terminates with:

```text
RETRIEVAL_FAILED
```

No further stages are executed.

---

### **Stage 3 — Change detection**

If retrieval succeeds, the system determines whether the required source data has changed since the last successful update.

Changes include:

- newly retrieved files

- restored missing files

- absence of the canonical zip

If no changes are detected and the maintained data store is already consistent:

- the cycle may terminate early with:

```text
NO_NEW_DATA
```

Otherwise, the pipeline proceeds to reconstruction.

---

### **Stage 4 — Reconstruction (parser)**

The parser rebuilds the complete `History` from the current set of source HTML files.

This involves:

- parsing standings and daily results

- reconciling inconsistencies via FSMs

- constructing validated `BashoState` objects

- assembling the full `History`

This stage is **all-or-nothing**:

- if any required basho fails to parse, the stage fails

Failure results in:

```text
REBUILD_FAILED
```

---

### **Stage 5 — Publication (canonical zip)**

If reconstruction succeeds, the system serializes and writes the canonical zip representation.

This stage guarantees:

- the zip reflects the current `History` exactly

- the representation is complete and consistent

Failure to write or persist the zip results in:

```text
PUBLISH_FAILED
```

This is treated as a fatal error.

---

### **Stage 6 — Live store**

After successful publication, the system ensures that the live data store is available and consistent with the canonical History.

This stage:

- loads or refreshes the in-memory representation
- verifies that the live data store is usable

Failure results in:

LIVE_STORE_FAILED

---

### **Stage 7 — Completion**

If all stages succeed, the update cycle completes with:

```text
SUCCESS
```

This indicates that:

- all required source data is present

- the canonical History is up to date

- the maintained data store is available in both durable and live form

---

## **3.3.1 Pipeline summary**

The full update pipeline can be summarized as:

```text
Planner
    ↓
Downloader
    ↓
Change Detection
    ↓
Parser (rebuild History)
    ↓
Persistence (write zip)
    ↓
Live store (in-memory representation)
```

---

## **3.3.2 All-or-nothing guarantee**

The update cycle enforces a strict invariant:

> The system never publishes or exposes a partially updated state.

This means:

- retrieval must be complete

- parsing must fully succeed

- publication must complete

- the maintained data store must be available in both durable and live form

Any failure prevents the system from advancing.

---

## **3.3.3 Relationship to tracker state**

The outcome of the update cycle determines the tracker’s next state:

- `SUCCESS` → return to `READY`

- `NO_NEW_DATA` → remain in `READY`

- `RETRIEVAL_FAILED` → enter `RECOVERY`

- any other failure → terminate

This behaviour is defined in Section 2.4.

---

## **3.3.4 Design principle**

The update cycle is designed around a single rule:

> **Completeness and correctness are enforced at cycle boundaries, not incrementally.**

The system does not:

- partially rebuild History

- incrementally update the canonical zip

Instead, each cycle produces a fully valid system state or fails.

---

## **3.3.5 Summary**

The update flow ensures that the system progresses only through **fully valid states**:

- incomplete data → retry (RECOVERY)

- inconsistent data → fail

- complete and valid data → publish

This guarantees that:

> at any successful boundary, the system holds a complete, consistent, and usable representation of all required basho data.

---

### 3.4 State model

The tracker operates as a continuous process governed by a small, explicit runtime state model. This model determines when update cycles occur and how failures are handled.

At any point in time, the tracker is in one of four states:

```text
DORMANT → READY → ACTIVE → (READY | RECOVERY | TERMINATE)
```

---

### **3.4.1 DORMANT**

The tracker is outside the active basho window.

In this state:

- no update cycles are performed

- no retries are attempted

- the system remains idle

The tracker transitions out of `DORMANT` when a basho enters its active window.

---

### **3.4.2 READY**

The tracker is within the active basho window and is eligible to perform update cycles.

In this state:

- no update is currently in progress

- no unresolved retrieval failure is being carried

- the system may initiate an update cycle when appropriate

The tracker transitions from `READY` to `ACTIVE` when it decides to perform an update.

---

### **3.4.3 ACTIVE**

An update cycle is currently in progress.

In this state:

- the tracker is executing the full update pipeline

- no concurrent update cycles are allowed

- the system is temporarily not idle

The tracker transitions out of `ACTIVE` based on the outcome of the update cycle.

---

### **3.4.4 RECOVERY**

The tracker is within the active basho window, but a previous update cycle failed due to incomplete retrieval.

In this state:

- required data is presumed missing or unusable

- the tracker continues attempting update cycles

- retries occur under the same scheduling rules as `READY`

`RECOVERY` differs from `READY` only in that:

> there is known unresolved incompleteness in required data.

---

## **3.4.5 State transitions**

The state transitions are driven entirely by:

- basho lifecycle (time)

- update cycle outcomes

---

### **From DORMANT**

- → `READY` when entering an active basho window

---

### **From READY**

- → `ACTIVE` when an update cycle begins

---

### **From ACTIVE**

After an update cycle completes:

- `SUCCESS` → `READY`

- `NO_NEW_DATA` → `READY`

- `RETRIEVAL_FAILED` → `RECOVERY`

- any other failure → **TERMINATE**

---

### **From RECOVERY**

- → `ACTIVE` when a retry update cycle begins

- → `READY` after a successful update cycle

- → **TERMINATE** if the active window ends while still in `RECOVERY`

---

## **3.4.6 Key invariant**

The state model enforces the following invariant:

> Outside `ACTIVE`, the system is always in a stable and well-defined state.

- `READY` → complete and up to date

- `RECOVERY` → known incomplete but retrying

- `DORMANT` → no updates required

---

## **3.4.7 READY vs RECOVERY (clarified)**

The distinction between `READY` and `RECOVERY` is **semantic, not behavioural**.

Both states:

- allow update cycles

- follow the same scheduling rules

They differ only in system knowledge:

- `READY`  
  → no known missing required data

- `RECOVERY`  
  → at least one previous retrieval attempt failed  
  → completeness is not yet guaranteed

This distinction is important because:

> it determines whether termination at the end of the active window is acceptable.

- `READY` at window end → normal transition to `DORMANT`

- `RECOVERY` at window end → **fatal error**

---

## **3.4.8 No hidden states**

The tracker does not maintain additional implicit states such as:

- “partially updated”

- “rebuilding”

- “publishing”

All internal activity during an update cycle is represented by `ACTIVE`.

---

## **3.4.9 Design principle**

The state model is intentionally minimal:

- it separates **time-based eligibility** (`DORMANT` vs active states)

- from **data completeness status** (`READY` vs `RECOVERY`)

- and **execution** (`ACTIVE`)

This avoids:

- complex state transitions

- hidden intermediate states

- ambiguity about system health

---

## **3.4.10 Summary**

The tracker state model provides:

- a clear separation between idle, active, and recovery conditions

- deterministic transitions based on update outcomes

- explicit handling of incomplete data

It ensures that:

> the system either maintains a complete dataset, is actively working to restore completeness, or fails explicitly when it cannot.

---

### **3.5 Recovery model**

The recovery model defines how the tracker responds to incomplete source data during an active basho.

Recovery is triggered when the tracker determines that required data **should exist but cannot be obtained**.

---

### **3.5.1 Definition of recovery**

Recovery is the condition in which:

> the system knows that required data is missing or unusable, and must continue attempting retrieval.

This condition arises when an update cycle produces:

```text
RETRIEVAL_FAILED
```

At this point:

- the system cannot guarantee completeness

- the canonical History may be outdated

- the tracker must continue attempting to restore correctness

---

### **3.5.2 What is being recovered**

Recovery applies only to **required source data**.

Specifically:

- missing basho-day HTML files

- unusable or malformed retrieved files

- any required record that could not be obtained

Recovery does **not** apply to:

- parsing failures

- zip publication failures

- live-store failures

These are treated as **fatal errors**, not recoverable conditions.

---

### **3.5.3 Recovery scope**

Recovery is scoped to the **current basho in progress**.

Only data that is expected to exist *at the current time* is considered recoverable.

This includes:

- all completed basho (which must already be complete)

- all elapsed days within the current basho

Future days are not part of recovery.

---

### **3.5.4 Recovery behaviour**

While in `RECOVERY`, the tracker behaves as follows:

- continues running normally

- periodically re-evaluates whether new data may exist

- initiates update cycles under the same conditions as `READY`

Each retry:

- re-attempts retrieval of all required records

- re-evaluates completeness

- either restores the system or remains in recovery

There is no special or reduced retry path:

> recovery uses the same full update cycle as normal operation.

---

### **3.5.5 Exit from recovery**

Recovery ends only when a full update cycle succeeds:

```text
SUCCESS
```

At that point:

- all required data is present

- the canonical zip has been rebuilt if necessary

- the maintained data store is available and consistent

The tracker transitions:

```text
RECOVERY → READY
```

---

### **3.5.6 Recovery failure (terminal condition)**

Recovery is bounded by the basho lifecycle.

If:

- the basho completes (window closes), and

- required data is still missing

then recovery is considered to have failed.

In this case:

- the tracker emits a fatal alert

- the process terminates

This enforces the invariant:

> completed basho must be fully and correctly represented.

---

### **3.5.7 No partial recovery**

The tracker does not support:

- partial completeness

- degraded operation

- skipping missing data

Recovery is binary:

- either completeness is restored

- or the system eventually terminates

---

### **3.5.8 Relationship to update cycle**

Recovery does not introduce a different execution path.

Instead:

- every retry is a full update cycle

- the same pipeline (Section 3.3) is executed

- the same outcomes apply

The only difference is interpretation:

- in `READY`, failure → new problem

- in `RECOVERY`, failure → continued unresolved problem

---

### **3.5.9 Design principle**

The recovery model is based on a single rule:

> missing required data is acceptable temporarily, but never indefinitely.

This ensures that:

- transient issues (network, timing, source delays) are tolerated

- persistent inconsistencies are surfaced explicitly

- the system never silently degrades

---

### **3.5.10 Summary**

Recovery provides controlled tolerance for incomplete data during an active basho:

- it allows repeated attempts to obtain missing data

- it ensures eventual consistency within the basho window

- it enforces strict correctness at the boundary

The system therefore guarantees:

> either the dataset becomes complete within the allowed time, or the failure is made explicit and the system stops.

# **4. Notes, limitations, and future work**

# **4.1 Known limitations**

### **4.1.1 Full rebuild strategy**

The tracker rebuilds the canonical History from the complete dataset whenever required.

- This is not incremental.

- Performance depends on:
  
  - total number of basho
  
  - parser efficiency
  
  - system characteristics (CPU, disk, caching effects)

Observed behaviour:

- Initial runs may be significantly slower than subsequent runs due to caching effects.

- Rebuild time is acceptable on modern hardware but not guaranteed to be constant.

---

### **4.1.2 Parser format assumptions**

The parser assumes a stable external HTML format.

- Changes in upstream data format (e.g. new layout or structure) may cause:
  
  - parsing failures
  
  - incorrect reconstruction of History

Example:

- Data for 2026 introduced format changes that were not compatible with the existing parser.

---

### **4.1.3 File validity assumptions**

The tracker assumes that:

- any existing file is valid

- files are immutable once written

There is:

- no checksum validation

- no revalidation of existing files

If files are externally modified or corrupted, behaviour is undefined.

---

## **4.2 Operational caveats**

### **4.2.1 Simulated time (test mode)**

Test mode uses a scaled clock, which may advance faster than the system can process update cycles.

This can result in:

- apparent jumps in time

- skipped intermediate states

- recovery or state transitions that would not occur in real-time operation

As a result:

> test mode is suitable for functional testing but not for validating timing-sensitive behaviour.

---

### **4.2.2 Pre-publication data availability**

The tracker may attempt to retrieve data that is expected but not yet published.

Examples include:

- early publication of standings pages (e.g. all records at 0–0)

- basho data prior to official release

In such cases:

- retrieval may fail repeatedly

- the tracker may enter RECOVERY

This is expected behaviour under current assumptions.

---

### **4.2.3 Dependency on external source behaviour**

The system depends on external data sources:

- availability is not guaranteed

- responses may be incomplete or malformed

The tracker treats such conditions as retrieval failures.

---

## **4.3 Design trade-offs**

### **4.3.1 No incremental updates**

The system intentionally avoids incremental reconstruction.

Advantages:

- simpler correctness model

- no partial state

- deterministic rebuild

Disadvantages:

- potentially higher computational cost

- rebuild time scales with dataset size

---

### **4.3.2 Minimal validation philosophy**

Validation is limited to:

- successful retrieval

- successful parsing

The system does not attempt:

- deep semantic validation

- cross-checking against external sources

This keeps the system simple but shifts responsibility for deeper validation elsewhere.

---

## **4.4 Future work**

The following areas may be revisited if requirements evolve:

---

### **4.4.1 Incremental rebuild**

Introduce the ability to:

- rebuild only affected basho

- avoid full reconstruction on every change

This would improve performance but significantly increase complexity.

---

### **4.4.2 Parser robustness**

Enhancements may include:

- handling multiple upstream formats

- version-aware parsing

- graceful degradation for partially incompatible data

---

### **4.4.3 Improved data validation**

Possible additions:

- file integrity checks (e.g. hashing)

- validation of parsed structures

- detection of silent data corruption

---

### **4.4.4 Retrieval awareness**

Improve handling of “expected missing” data:

- distinguish between:
  
  - not-yet-published data
  
  - genuinely missing data

This could reduce unnecessary recovery cycles.

---

### **4.4.5 Performance instrumentation**

Add:

- timing metrics for rebuild stages

- logging of cycle durations

- visibility into bottlenecks

---

## **4.5 Summary**

The current system prioritises:

- correctness

- determinism

- simplicity

over:

- performance optimisation

- incremental processing

- deep validation

These trade-offs are intentional and may be revisited as requirements evolve.

---

This gives you:

- zero duplication of the spec

- preservation of all the important “real-world” knowledge

- a clear boundary between **what must happen** and **what we know about it** 👍

---

# 🧾 Next Steps / Outstanding Issues

## 1. Command-line robustness

The tracker must be run from the project root:

> `PS X:\Sumo\Sumo-Tools> py -m src.infra.tracker.tracker ...`

(and *not* `Sumo-Tools/src` otherwise "files" will refer to the wrong location due the to use of relative paths.

## ---

## 2. “Usable” vs “exists” (temporary simplification)

- Downloader currently treats existing files as usable without revalidation.

- You added Caveat 1.0 — good.

- Tracker spec still speaks in stronger terms (“usable”).

- Action:
  
  - Probably acceptable for now
  
  - Revisit when validation is implemented properly

---

## 3. Ledger role unresolved (likely remove or downgrade)

- Ledger:
  
  - used only to suppress same-day reruns
  
  - not part of correctness, completeness, or planning

- Not mentioned in tracker spec

- Action:
  
  - Decide later:
    
    - remove it, or
    
    - keep as run-throttle, or
    
    - replace with simple run log

- Current status: **implementation detail, not design**

---

## 4. Scheduler purity (time vs run-history)

- Scheduler currently:
  
  - time-based ✔
  
  - plus ledger-based suppression ❗

- This mixes concerns slightly

- Action:
  
  - Likely remove ledger dependency
  
  - or explicitly treat as tracker policy, not scheduling

---

## 5. Planner is coverage-blind (by design)

- Planner returns **full prefix from epoch every run**

- Ignores:
  
  - ledger
  
  - filesystem

- This is intentional but should remain explicit

- Action:
  
  - Already clarified in code comment (good)
  
  - No further action needed unless design changes

---

## 6. Downloader validation shortcut

- Existing daily-results files:
  
  - accepted without revalidation (performance hack)

- Proper model would revalidate or checksum

- Action:
  
  - Keep for now
  
  - Upgrade later (performance vs correctness tradeoff)

---

## 7. File immutability assumption

- Files written read-only

- System assumes:
  
  - files are not tampered with after write

- Not enforced beyond permissions

- Action:
  
  - Optional future hardening (checksums, etc.)
  
  - Not required for current design

---

## 8. Naming consistency (scraper → downloader)

- Still exists in some code paths (e.g. import path)

- Not a doc issue per your scope

- Action:
  
  - Fix later during refactor

---

## 9. Parser dependency on current standings (implicit coupling)

- Parser depends on:
  
  - current standings
  
  - daily results

- Now reflected in updated Required Data section ✔

- Action:
  
  - None for now

---

## 10. Update cycle semantics (SUCCESS vs NO_NEW_DATA)

- Subtle but now aligned between:
  
  - code
  
  - tracker spec
  
  - tracker docstrings (after fixes)

- Action:
  
  - No further change needed

---

## **11. Rebuild range derivation (remove hard-coded years)**

### **Current state**

- The rebuild stage uses hard-coded values:
  
  ```python
  start_year=1958, end_year=2025
  ```

- This does not reflect the tracker’s actual required data set.

- It also masks parser incompatibilities (e.g. 2026 format changes) by silently excluding newer data.

---

### **Required behaviour**

The rebuild range should be derived dynamically:

- **Start year**
  
  - defined by the project epoch (e.g. `EPOCH`)
  
  - should be sourced from a shared constant (currently defined in planner)

- **End year**
  
  - derived from the current required set:
    
    ```text
    max(requested_basho_days)
    ```
  
  - specifically:
    
    ```python
    requested_date_days[-1].date.year
    ```

This ensures that:

- the rebuild always covers exactly the data the tracker considers required

- no filesystem artefacts or manual downloads influence behaviour

---

### **Implementation approach**

- Modify `_rebuild_canonical_history(...)` to accept:
  
  ```text
  (start_year, end_year)
  ```

- Compute these in `run_update_cycle(...)`:
  
  ```python
  start_year = int(EPOCH.year)
  end_year = int(requested_date_days[-1].date.year)
  ```

- Pass them into the rebuild stage

---

### **Temporary workaround (parser incompatibility)**

If the parser cannot yet handle newer data (e.g. 2026 HTML changes):

- **Do not bake limits into the design**

- Acceptable temporary options:
  
  - explicitly fail when unsupported years are encountered  
    *(preferred — honest failure)*
  
  - temporarily cap `end_year` with a clearly marked workaround

- The current behaviour (silent truncation at 2025) is **not acceptable long-term**

---

### **Design note**

This aligns the implementation with the core design principle:

> the canonical History is always rebuilt from the complete required data set

and avoids hidden divergence between:

- what the tracker *requests*

- what the rebuild *actually processes*

---

### **Future refinement**

- Move `EPOCH` to a shared config/constants module to avoid cross-component coupling (planner → update cycle)

---

## **12. Test-mode timing calibration**

### **Problem**

In test mode, simulated time advances independently of the actual time taken to execute tracker operations.

- Long-running stages (e.g. download, parse, rebuild) may take longer than a “virtual” time step
- This can cause:
  - skipped states
  - missed scheduling boundaries
  - unrealistic transitions

---

### **Required investigation**

Measure the execution time of the most significant stages:

- downloader (per run and per batch)
- parser / rebuild
- persistence (zip write)
- any future live-store / analysis stages

---

### **Goal**

Determine a **minimum safe virtual tick duration**, such that:

> one iteration of the main loop (including an update cycle) completes within a single simulated time step under normal conditions

---

### **Outcome**

- establish a recommended lower bound for:
  
  real_seconds_per_simulated_day

- document this as guidance for test mode usage

---

### **Design note**

This does not eliminate the fundamental limitation of scaled time, but:

- reduces distortion
- improves reliability of simulation
- provides an empirical basis for choosing test parameters

## **13. Publication stage implementation**

### **Current state**

The publication stage (writing the canonical History zip) is currently implemented as a stub:

- always reports success

- does not enforce that the canonical representation is actually written or valid

---

### **Required work**

- implement canonical History serialization and persistence

- ensure:
  
  - the output reflects the rebuilt History exactly
  
  - failure to write or persist is detected

- return `PUBLISH_FAILED` on failure

---

### **Design note**

Publication is a **mandatory stage**:

> a successful update cycle must guarantee that the canonical representation exists and is correct

---

### **Required work**

- implement live-store population from the canonical History

- define and enforce required live-store state

- ensure:
  
  - live-store is present and consistent after a successful cycle
  
  - missing or invalid live-store is detected

- return `LIVE_STORE_FAILED` or `DERIVED_ARTIFACTS_MISSING` as appropriate

---

### 

# ✔️ Summary

You’re now in a very good state:

- Core pipeline (planner → downloader → parser → serialiser) is **coherent**

- Docs and code are **aligned on meaning**

- Remaining issues are:
  
  - deferred features
  
  - implementation shortcuts
  
  - minor architectural choices

---

# Proposal: Deterministic Simulated Clock for Tracker

## 1. Problem Statement

The current test-mode clock scales real time:

> simulated time advances continuously as real time passes

This has two undesirable consequences:

1. **Execution-time distortion**
   
   * Long-running operations (especially rebuild) advance simulated time significantly
   * Cold rebuild (~300s) can skip **multiple simulated days**
   * Warm rebuild (~8s) can skip **hours**

2. **Non-deterministic scheduling tests**
   
   * Whether a publication boundary is observed depends on runtime performance
   * Tests become sensitive to machine speed, cache state, and workload

This makes it difficult to:

* reason about `--rate`
* write reliable timing tests
* explain behaviour

---

## 2. Design Goal

> **Make simulated time advance only when the system is “waiting”, not when it is “working”.**

This separates:

* **time progression** (scheduler behaviour)
  from
* **computation cost** (implementation detail)

---

## 3. Proposed Model

Introduce a **deterministic simulated clock** where:

* `clock.now()` returns a stored simulated time
* **simulated time advances only via `clock.sleep()`**
* execution time does **not** affect simulated time

---

## 4. API Changes

### Replace direct sleep

Current:

```python
time.sleep(poll_interval_seconds)
```

Proposed:

```python
clock.sleep(poll_interval_seconds)
```

---

### Clock interface

```python
class Clock:
    def now(self) -> datetime
    def sleep(self, seconds: float) -> None
    def pause(self) -> None      # optional
    def resume(self) -> None     # optional
```

---

## 5. Clock Implementations

### RealClock (unchanged behaviour)

* `now()` → wall clock
* `sleep()` → `time.sleep()`
* `pause/resume` → no-op

---

### SimulatedClock (new behaviour)

State:

* `current_time`

Behaviour:

* `now()` → returns `current_time`

* `sleep(seconds)`:
  
  * advance simulated time:
    
    ```
    current_time += seconds / rate  (in days)
    ```
  
  * optionally sleep in real time

Key property:

> **No simulated time passes during computation**

---

## 6. Consequences

### Eliminates timing distortion

* rebuild (300s) → **0 simulated time**
* file check (0.05s) → **0 simulated time**

### Deterministic scheduling

* publication boundaries are always observed

* behaviour depends only on:
  
  * simulated time
  * logic

* not on:
  
  * machine speed
  * cache state

### Simplifies reasoning

* `--rate` only affects **how fast time moves between checks**
* no need to account for rebuild duration in documentation

---

## 7. Polling Behaviour (unchanged)

The current design:

* poll interval = `rate / 4`
* ⇒ ~4 checks per simulated day (≈ every 6 simulated hours)

This remains unchanged.

---

## 8. Optional Extensions

### Pause/Resume

May be added if needed, but not required if:

> time only advances via `clock.sleep()`

---

### Dual-mode clocks

Retain both:

1. **ScaledClock (current)**
   
   * realistic but distorted

2. **SimulatedClock (proposed)**
   
   * deterministic, test-friendly

---

## 9. Migration Plan

Minimal changes required:

1. Replace all `time.sleep(...)` with `clock.sleep(...)`
2. Implement `sleep()` in clock classes
3. Ensure all time reads go through `clock.now()`

No changes required to:

* update cycle
* planner
* scheduler logic

---

## 10. Trade-offs

### Advantages

* deterministic tests
* simpler documentation
* no dependence on execution time
* easier parameter selection

### Disadvantage

* no longer simulates “real time passes while computing”

This is acceptable because:

> test mode is for validating logic, not modelling system load

---

## 11. Recommendation

Adopt the deterministic simulated clock as the primary test-mode behaviour.

Retain the current scaled clock only if:

* realism under load is specifically required

---

## One-line summary

> **Advance simulated time only during `clock.sleep()`, not during computation.**

---

### Proposal: Configurable Live Store Initialisation for Testing

#### Motivation

The current live store initialisation is hard-wired to load the full canonical history range:

```
1958_01 to <current_year>_11
```

This results in:

- ~20–30 seconds startup time

- unnecessary work for testing and development

- tight coupling between `LiveStore` and canonical persistence assumptions

For SDSM testing, we often want to:

- load a smaller prebuilt history range

- iterate quickly

- simulate specific time windows

#### Proposal

Introduce **configurable initialisation of the live store from arbitrary zip ranges**, without changing the core semantics of the system.

---

## 1. API Change (LiveStore)

Change:

```python
def init_live_store(self) -> bool
```

to:

```python
def init_live_store(self, zip_path: Path | str) -> bool
```

### Rationale

- Removes hidden dependency on `_canonical_zip_path()`

- Makes `LiveStore` reusable and explicit

- Aligns with the idea that the store is a *mechanism*, not a policy

---

## 2. Canonical Path Helper (outside class)

Retain a helper for default behaviour:

```python
def canonical_zip_path(start_year: int, end_year: int) -> Path
```

This preserves:

- current naming convention

- existing production behaviour

---

## 3. CLI Enhancements (LiveStore module)

Extend `__main__` with optional parameters:

### Option A (structured)

```
--start YYYY
--end YYYY
```

Example:

```
py -m src.infra.live_store.LiveStore --start 2020 --end 2022
```

### Option B (direct)

```
--zip <path>
```

Example:

```
py -m src.infra.live_store.LiveStore --zip files/output/Historys/2024_01 to 2024_11.zip
```

### Behaviour

- If `--zip` is provided → use it directly

- Else if `--start/--end` provided → construct path

- Else → fall back to canonical default (current behaviour)

---

## 4. Behavioural Goals

- No change to production semantics

- No change to tracker/SDSM logic

- Faster iteration during development

- Explicit control over loaded dataset

---

## 5. Non-Goals

- No change to zip naming scheme

- No versioning of live store contents

- No change to shared memory protocol

- No client notification mechanism

---

## 6. Future Extensions (Optional)

- Partial-history publish without full rebuild

- Named test profiles (e.g. "last_basho_only")

- Integration with simulated clock scenarios

---

## Summary

This change:

- decouples `LiveStore` from hard-coded persistence assumptions

- significantly improves developer workflow

- keeps the system architecture clean and aligned with SDSM principles

and can be implemented with minimal, localised changes.

Here is a draft proposal.

## Proposal: distinguish pre-basho and in-basho readiness in tracker state reporting

### Summary

The tracker currently reports a single `READY` state for all times within the active window. That is sufficient for control flow, but it hides an operational distinction that matters to a human reader:

* the **pre-basho** period, when the tracker is active because a basho is approaching
* the **in-basho** period, when daily results are expected
* the **between-basho** period, when the tracker is inactive

At present, `state_for(...)` returns `READY` for the entire interval from `pre_basho_start` to `basho_end`, and `DORMANT` outside it.  The runtime state model likewise only distinguishes `DORMANT`, `READY`, `RECOVERY`, and `ACTIVE`. 

This proposal adds a separate notion of **schedule phase** for reporting and observability, while leaving the existing execution-state machine unchanged.

### Motivation

The current model is good enough for deciding whether the tracker may run, but not for expressing *what kind of readiness* applies.

For example, these are both currently shown as `READY`:

* two days before a basho starts
* day 11 of an active basho

Operationally, those states are different. The tracker is eligible to run in both cases, but the expectation is different:

* before the basho, the system is in a preparatory or watchful state
* during the basho, the system is in a live daily-results state

The distinction would improve:

* tray/status output
* log readability
* debugging of timing behaviour
* future policy changes, if pre-basho and in-basho need different handling

### Current behaviour

The current scheduling code defines a `BashoWindow` with:

* `pre_basho_start`
* `basho_start`
* `basho_end`
* `trigger_hour` 

`state_for(...)` currently does only this:

* `READY` if `now` is within the window
* `DORMANT` otherwise 

The tray output simply prints `state.name`. 

### Proposed change

Add a second, separate concept called `WindowPhase` or `SchedulePhase`.

Suggested values:

```python
class WindowPhase(Enum):
    BETWEEN_BASHO = auto()
    PRE_BASHO = auto()
    IN_BASHO = auto()
```

The classification would be:

* `BETWEEN_BASHO` if `now < pre_basho_start` or `now > basho_end`
* `PRE_BASHO` if `pre_basho_start <= now < basho_start`
* `IN_BASHO` if `basho_start <= now <= basho_end`

This should be derived from the existing `BashoWindow`, so no scheduling semantics need to change.

### Design principle

Do **not** split `RunState.READY` into multiple execution states.

`RunState` currently mixes lifecycle and operational flow:

* `READY`
* `ACTIVE`
* `RECOVERY`
* `DORMANT` 

Those are execution-oriented states.

By contrast, pre-basho versus in-basho is a **calendar phase**, not an execution state. Keeping the concepts separate avoids muddying the state machine.

Recommended model:

* `RunState`: execution/lifecycle state
* `WindowPhase`: calendar/scheduling phase

### Scope of first implementation

The initial implementation should be **observational only**.

That means:

* no change to run eligibility
* no change to `time_when_new_data_may_exist(...)`
* no change to planner behaviour
* no change to update-cycle policy

The new phase should only affect reporting.

Suggested tray output:

```text
[tray] 2026/03/22 11:28 state -> READY (IN_BASHO)
```

or:

```text
[tray] 2026/04/26 09:00 state -> READY (PRE_BASHO)
```

### Suggested implementation steps

1. Add a new enum in `types.py`:
   
   * `WindowPhase` or `SchedulePhase`

2. Add a helper in `schedule.py`:
   
   * `phase_for(now, window) -> WindowPhase`

3. Extend `TrackerRuntime` with a `phase` field.

4. In `run()`, update `runtime.phase` each loop alongside `runtime.current_window` and `runtime.state`. 

5. Update `set_tray_state(...)` so that it can display both lifecycle state and phase. The current tray function only prints the state. 

### Alternative minimal implementation

A smaller first step would be to avoid changing `TrackerRuntime` and compute phase only when printing tray output.

That would reduce structural change, but it spreads scheduling interpretation into presentation code. The cleaner long-term design is to compute phase once in scheduling/runtime logic and pass it to the tray layer.

### Backward compatibility

This proposal is backward-compatible if introduced carefully.

* Existing control flow remains unchanged.
* Existing `RunState` values remain unchanged.
* Existing policy logic remains unchanged.
* Only the formatting of status output changes.

If needed, tray output could remain backward-compatible by only showing the phase when explicitly requested.

### Benefits

This change would make the tracker easier to reason about without increasing risk in the core update logic.

It would give a clearer account of what `READY` means in practice:

* `READY (PRE_BASHO)`
* `READY (IN_BASHO)`

while preserving the existing execution semantics that now appear to be working correctly.

### Recommendation

Implement this as a small, reporting-only enhancement after the current happy-path and failure-path behaviour is considered stable.

That keeps the scheduling and update logic untouched while improving visibility into tracker behaviour.

Here is a clean draft proposal, with no branching or alternatives.

---

# Proposal: Bootstrap Phase for Tracker Startup

## Summary

Introduce a **bootstrap phase** at tracker startup whose sole responsibility is:

> **Ensure a valid canonical History exists and is published in the live store before the tracker FSM begins.**

This phase executes once at startup and is independent of scheduling and `--now`.

---

## Design Principles

1. **Separation of concerns**
   
   * Bootstrap establishes initial state
   * FSM maintains that state over time

2. **Single source selection**
   
   * Prefer canonical zip
   * Fall back to raw HTML
   * Fall back to download

3. **Operational validity, not exhaustive verification**
   
   * Zip is valid if it can be opened and read
   * Raw data is valid if rebuild succeeds

4. **Fail fast**
   
   * If a valid state cannot be established, terminate with a fatal alert

5. **Reuse existing pipeline**
   
   * Planner defines required dataset
   * Downloader ensures coverage
   * Parser rebuilds History
   * Persistence writes canonical zip
   * Live store publishes result

---

## Bootstrap Algorithm

At tracker startup, before entering the main loop:

```text
1. Obtain current time:
       now = clock.now()

2. Attempt to load canonical zip:

       IF canonical zip exists AND can be opened and read:
           load History from zip
           initialise live store with this History
           publish live store name
           SUCCESS → proceed to FSM

3. Attempt rebuild from raw HTML:

       TRY:
           rebuild History from raw HTML files
       IF rebuild succeeds:
           write canonical zip
           initialise live store with rebuilt History
           publish live store name
           SUCCESS → proceed to FSM

4. Download and rebuild:

       requested = planner(now)

       retrieval_result = download(requested)

       IF retrieval_result == FAILURE:
           FATAL → terminate

       rebuild History

       IF rebuild fails:
           FATAL → terminate

       write canonical zip

       IF write fails:
           FATAL → terminate

       initialise live store with rebuilt History
       publish live store name

       SUCCESS → proceed to FSM
```

---

## Definitions

### Canonical zip validity

A canonical zip is considered valid if:

* the file exists
* it can be opened
* it can be read successfully into a `History`

No attempt is made to verify that its contents exactly match raw HTML.

---

### Raw data validity

Raw HTML data is considered usable if:

* a rebuild using the parser succeeds

No pre-check for completeness is required.

---

### Required dataset

The required dataset is determined by:

```python
requested = get_requested_date_days(now, ledger, config)
```

This represents all BashoDayRefs that should exist as of `now`. 

The downloader is responsible for determining which of these require fetching. 

---

## Integration with Existing Code

### New structure

```text
run():
    bootstrap()
    enter FSM loop
```

### Bootstrap responsibilities

* determine initial source of truth
* construct canonical History if needed
* initialise and retain live store
* publish store name

### FSM responsibilities (unchanged)

* scheduling
* triggering update cycles
* maintaining canonical state over time

---

## Live Store Handling

Bootstrap must:

* create a single `LiveStore` instance
* initialise it with the chosen History
* retain ownership for the lifetime of the tracker process
* publish its name via `write_published_name(...)`

This aligns with current live-store ownership semantics.  

---

## Failure Handling

Bootstrap terminates the tracker with a fatal alert if:

* canonical zip cannot be read and rebuild fails
* download fails
* rebuild fails after download
* canonical zip cannot be written

This ensures the FSM never runs without a valid initial state.

---

## Relationship to `--now`

`--now` remains unchanged in meaning:

> Run one update cycle immediately after startup.

Execution order:

```text
bootstrap
if --now:
    run one update cycle
enter FSM loop
```

`--now` does not participate in bootstrap logic.

---

## Benefits

* Guarantees a valid initial state before FSM begins
* Eliminates reliance on implicit repair via update cycle
* Keeps bootstrap logic simple and deterministic
* Reuses existing, well-tested components
* Aligns behaviour with original mental model of the tracker

---

## Non-goals

* No attempt to validate zip contents against raw HTML
* No optimisation of download scope (planner remains coverage-blind)
* No change to scheduling or update-cycle behaviour

---

## Conclusion

This proposal introduces a clear and minimal bootstrap phase that:

* resolves the current startup gap
* preserves the existing architecture
* keeps complexity low
* matches the intended behaviour of the tracker

The tracker becomes:

```text
1. Establish valid state
2. Maintain it
```

which is exactly the model you described.
