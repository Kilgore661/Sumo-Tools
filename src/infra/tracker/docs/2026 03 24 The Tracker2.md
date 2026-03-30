### 1. Requirements (draft)

## Caveats

1. Publication, cache refresh, analysis and derived artefacts are all stubs. **TBD**

2. Throughout this project, *validation* of an existing file is currently mostly implicit rather than re-checked. A file is validated when first downloaded, then written read-only, and later treated as acceptable if it still exists.. (Deleting the file would be OK, because it would be downloaded again.) This is because checking a file for validity takes an unacceptably long time in development/testing. Sttictly speaking then, "usable" is a synonym for "exists" until the project is complete.

**Purpose**

A continuously running program that maintains a complete and up-to-date local copy of basho records, together with a canonical zip representation of that data.

This guarantee applies only to completed basho. Data for a basho that is still in progress is not considered final and must not be published as part of the canonical History.

The tracker retries retrieval failures only while a basho is in progress. If required data is still unavailable when the basho completes, the tracker aborts with an error.

**Data completeness**

The program must ensure that all required basho records are present and usable.

- If any required data is missing, it must be retrieved.

- If any retrieved data cannot be successfully obtained or written, it must be treated as missing and re-retrieved.

- The canonical zip representation must be rebuilt whenever required data changes, is restored, or the zip is missing.

**Failure handling**

A retrieval attempt is considered unsuccessful if any required data cannot be obtained.

- Failures may be caused by missing files, unusable files, or external issues such as network or source unavailability.

- A retrieval attempt is considered unsuccessful if any required source data cannot be obtained.
  
  Retrieval failures are deemed recoverable by the tracker only while the basho is in progress.
  
  If required data is still unavailable when the basho completes, the tracker aborts.
  
  Failures after retrieval — including rebuild failure, zip publication failure, cache refresh failure, or analysis failure — are treated as fatal and cause immediate termination.

**Retry policy**

- The program will continue retrying while a basho is in progress.

- If the basho completes and required data is still missing, the program will terminate with an error indicating incomplete data.

---

# 2. Specification

## 2.0 Basho lifecycle

Basho follow a fixed schedule:

- Each basho begins on the second Sunday of each odd-numbered month
- Each basho lasts for 15 days

A basho is therefore either:

- in progress (from its start date until the end of day 15), or
- complete (after the final scheduled day)

## 2.1 Overview

The tracker ensures that all required basho records are present and usable, and that the canonical History representation derived from them is up to date.

At any point in time, the system maintains:

- a complete and usable set of required source data
- a canonical zip representation consistent with that data

If required source data changes or is restored, the canonical zip must be rebuilt to reflect the current state.

The tracker does not perform partial or incremental updates to the canonical History. Instead, it rebuilds the representation from the complete set of required source data whenever necessary.

---

## 2.2 Required data

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

## 2.3 Determining required data

At any given time, the tracker determines the set of required records based on the current time and the basho lifecycle.

For completed basho, all basho-day records are required.

For a basho that is in progress, only those days that should have occurred by the current time are required.

Future basho and future days within a basho are not required.

The tracker derives the set of required basho-day records from the current time and compares this with the set of existing local files.

The tracker supplies the full required set to the retrieval component, which determines which records are already present and which must be fetched.

---

## 2.4 Execution model

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

## 2.5 Update cycle

An update cycle consists of the following stages:

1. Determine the current required data set.

2. Attempt retrieval of all required source records.

3. If retrieval succeeds, determine whether the required source data has changed.

4. If the source data has changed:
   
   - rebuild the canonical History
   - serialise and store it as the canonical zip representation

5. If the source data has not changed:
   
   - retain the existing canonical zip

6. Refresh all required downstream state derived from the canonical zip. ***TBD***
   These artifacts are considered mandatory and must exist after a successful cycle.

Each update cycle produces one of the following outcomes:

- SUCCESS  
  All stages completed successfully and either:
  
  - new data was incorporated and the canonical zip was rebuilt, or
  - no changes were required and all downstream state was already satisfied

- NO_NEW_DATA  
  Retrieval succeeded but no required source data changed, and downstream state was already up to date

- RETRIEVAL_FAILED  
  One or more required source records could not be obtained

- REBUILD_FAILED  
  The canonical History could not be rebuilt successfully

- PUBLISH_FAILED  
  The canonical zip could not be written or persisted

- CACHE_FAILED  
  The cache could not be refreshed successfully

- ANALYSIS_FAILED  
  One or more required analysis outputs could not be produced

- DERIVED_ARTIFACTS_MISSING  
  Required downstream artifacts were found to be missing after a cycle that should have produced them

The outcome of the update cycle determines the subsequent behaviour of the tracker as defined in Section 2.4.

---

## 2.6 Recovery behaviour

If an update cycle fails, the tracker enters a **recovery condition**.

In this condition:

- some required data is presumed missing or unusable

- the tracker will attempt further update cycles to resolve the condition

The recovery condition persists until a successful update cycle occurs.

---

## 2.7 Retry behaviour

The tracker retries failed update cycles subject to the following rules:

- retries occur only while within the active window

- retries are repeated until either:
  
  - a successful update occurs, or
  
  - the active window ends

---

## 2.8 Terminal failure

If the active window ends while the tracker is still in a recovery condition:

> The tracker terminates with an error indicating that required data could not be obtained.

This represents a failure to meet the data completeness requirement within the allowed retry window.

---

## 2.9 Dormant behaviour

When outside the active window:

- the tracker performs no update cycles

- no retries are attempted

- the system remains idle until the next active window

---

## 2.10 Notes

- The specification does not define how data is retrieved (e.g. scraping).

- The specification does not define internal state names or implementation details.

- Timing parameters (e.g. trigger hour, polling interval) are implementation details.

---

## 3. Design

### 3.1 Overview

The tracker is a continuously running program whose purpose is to maintain a complete and up-to-date local corpus of basho records and all required derived representations.

The design separates this into the following concerns:

- scheduling: deciding when the program should attempt an update
- planning: determining what data is required as of the current time
- retrieval: obtaining required source data
- reconstruction: rebuilding the canonical History representation
- publication: persisting the canonical zip representation
- derivation: producing all required downstream artifacts from the canonical zip

This separation keeps time-based logic, data requirements, data acquisition, and derived outputs clearly distinct.

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

### **Derivation / Cache (downstream artifacts)**

This stage produces all required artifacts derived from the canonical zip.

Its responsibilities include:

- loading data into cache (e.g. shared memory)

- generating any required analysis outputs

- ensuring all downstream artifacts are present and consistent

These artifacts are considered **mandatory**:

- if any required artifact is missing after a successful rebuild, the cycle fails

- cache or analysis failures are treated as fatal

---

### **Update cycle (integration point)**

The update cycle coordinates all components into a single operation:

```text
Planner → Downloader → Parser → Persistence → Derivation
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
Derivation  → make it usable
```

Each component has a single responsibility, and correctness depends on all stages succeeding.

---

### **Summary**

The tracker is not a single process but a coordinated pipeline of components:

- time-driven orchestration (Tracker, Planner)

- data acquisition (Downloader)

- data validation and reconstruction (Parser)

- canonical publication (Persistence)

- downstream usability (Derivation / Cache)

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

If no changes are detected and all downstream artifacts are present:

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

### **Stage 6 — Derivation (downstream artifacts)**

After successful publication, all required downstream artifacts are refreshed.

This may include:

- cache population (e.g. shared memory)

- analysis outputs

- any other derived state required by the system

All artifacts are considered **mandatory**.

Failures result in:

```text
CACHE_FAILED
ANALYSIS_FAILED
DERIVED_ARTIFACTS_MISSING
```

depending on the stage of failure.

---

### **Stage 7 — Completion**

If all stages succeed, the update cycle completes with:

```text
SUCCESS
```

This indicates that:

- all required source data is present

- the canonical History is up to date

- all downstream artifacts are valid

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
Derivation (cache + artifacts)
```

---

## **3.3.2 All-or-nothing guarantee**

The update cycle enforces a strict invariant:

> The system never publishes or exposes a partially updated state.

This means:

- retrieval must be complete

- parsing must fully succeed

- publication must complete

- all derived artifacts must exist

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

- tolerate missing derived artifacts

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

### ## **3.4 State model**

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

- cache or analysis failures

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

- all downstream artifacts are valid

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

## 0. Command-line robustness

The tracker must be run from the project root:

> `PS X:\Sumo\Sumo-Tools> py -m src.infra.tracker.tracker ...`

(and *not* `Sumo-Tools/src` otherwise "files" will refer to the wrong location due the to use of relative paths.

## 1. Derived artifacts (TBD)

- The tracker spec defines “downstream state” / “derived artifacts” as mandatory.

- These are **not yet defined or implemented**.

- Current code uses placeholders:
  
  - `_analyse()`
  
  - `_derived_artifacts_exist()`

- Action:
  
  - Keep as **TBD**
  
  - Define later what artifacts are required and how to validate them

---

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
- any future cache / analysis stages

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

---

## **14. Cache / downstream state implementation**

### **Current state**

Cache handling and downstream state management are currently stubbed:

- cache refresh / ensure functions always succeed

- no actual cache population or validation is performed

---

### **Required work**

- implement cache population from the canonical History

- define and enforce required cache state

- ensure:
  
  - cache is present and consistent after a successful cycle
  
  - missing or invalid cache is detected

- return `CACHE_FAILED` or `DERIVED_ARTIFACTS_MISSING` as appropriate

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

If you want to continue, the next direction is:

👉 **“Does the tracker doc fully describe what the tracker actually does at runtime?”**

i.e. a full end-to-end pass rather than component-by-component.
