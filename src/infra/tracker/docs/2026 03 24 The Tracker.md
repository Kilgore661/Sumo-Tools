### 1. Requirements (draft)

**Purpose**

A continuously running program that maintains a complete and up-to-date local copy of basho records, together with a canonical zip representation of that data.

**Data completeness**

The program must ensure that all required basho records are present and usable.

- If any required data is missing, it must be retrieved.

- If any retrieved data is unusable (e.g. corrupt, empty, malformed), it must be treated as missing and re-retrieved.

- The canonical zip representation must be rebuilt whenever required data changes, is restored, or the zip is missing.

**Failure handling**

A retrieval attempt is considered unsuccessful if any required data cannot be obtained.

- Failures may be caused by missing files, unusable files, or external issues such as network or source unavailability.

- The program must retry unsuccessful retrievals.

**Retry policy**

- The program will continue retrying while within the active basho window.

- If the active window ends and required data is still missing, the program will terminate with an error indicating incomplete data.

---

# 2. Specification

## 2.1 Overview

The tracker is a continuously running program that periodically attempts to ensure that all required basho records are present and usable.

It does this by repeatedly executing an **update cycle** while within an **active basho window**.

---

## 2.2 Required data

At any given time, there exists a set of **required data**.

This is defined as:

> All basho records that should have been published as of the current time.

The exact determination of this set is time-dependent and based on the basho schedule and publication timing.

---

## 2.3 Active window

The tracker only performs update cycles while within an **active window**.

The active window is defined relative to a basho:

- begins a fixed number of days before basho start

- ends at a fixed time after the final scheduled basho day

Outside this window, the tracker is dormant and performs no update cycles.

---

## 2.4 Update cycle

An update cycle consists of:

1. Determining the current required data set

2. Attempting to retrieve all required data

3. Evaluating the outcome

An update attempt is **all-or-nothing**:

- If all required data is successfully retrieved and usable → success

- If any required data cannot be obtained or validated → failure

---

## 2.5 Outcomes

Each update cycle has one of the following outcomes:

- **Success**  
  All required data is present and usable.

- **Failure**  
  One or more required items could not be obtained or are unusable.

- **No new data**  
  No required data exists for the current time.

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

The tracker is designed as a small continuously running program whose job is to maintain a complete and up-to-date local corpus of basho records.

The design separates this into three concerns:

- **scheduling**: deciding when the program should attempt an update

- **planning**: deciding what data is required as of the current time

- **retrieval**: obtaining the required data

This separation keeps the timing model, the notion of required data, and the download logic distinct.

---

### 3.2 Main components

#### Tracker

The tracker is the top-level controller. It runs continuously, determines whether the current time falls within an active basho window, and starts update cycles when appropriate.

Its responsibilities are:

- maintain the current runtime state

- determine whether an update attempt should occur

- respond to update outcomes

- terminate with an error if recovery is still unresolved when the active window ends

#### Planner

The planner determines the set of data that should exist as of the current time.

Its responsibilities are:

- determine the latest basho day whose data should have been published

- derive the required set of basho records from that

- provide the tracker with the set of required records for the current update cycle

The planner is time-based. It defines what “up-to-date” means operationally.

#### Scraper / downloader

The retrieval component attempts to ensure that all required records are present and usable.

Its responsibilities are:

- check whether required records are available locally

- download missing records

- reject unusable records

- report overall success or failure for the attempted update

At design level, this component is concerned with retrieval, not with scheduling or policy.

---

### 3.3 Update flow

A normal update cycle proceeds as follows:

1. The tracker decides that an update attempt is due.

2. The planner computes the set of records required as of the current time.

3. The retrieval component attempts to obtain all required records.

4. The tracker interprets the result and updates its runtime state.

The retrieval attempt is treated as all-or-nothing for the purposes of the update cycle:

- if all required records are present and usable, the cycle succeeds

- if any required record cannot be obtained or is unusable, the cycle fails

This keeps the meaning of success simple: success means the corpus is complete up to the required point.

---

### 3.4 State model

The tracker uses a small runtime state model.

#### DORMANT

The tracker is outside the active basho window and performs no update cycles.

#### READY

The tracker is inside the active basho window and is eligible to perform update cycles. No unresolved retrieval failure is currently being carried.

#### ACTIVE

An update cycle is currently in progress.

#### RECOVERY

The tracker is inside the active basho window, but a previous retrieval attempt failed and required data is therefore presumed missing. The tracker remains eligible to retry.

The important design point is that `RECOVERY` is not a different scheduling mode. It is operationally similar to `READY`, but with unresolved missing data.

---

### 3.5 Recovery model

The design assumes that some failures are temporary and recoverable.

Examples include:

- a file being missing locally

- a file existing locally but being unusable

- a temporary network failure

- the source site being temporarily unavailable

For this reason, a failed retrieval attempt does not immediately terminate the tracker. Instead, the tracker enters `RECOVERY` and keeps retrying while still within the active window.

`RECOVERY` persists until a later successful update cycle occurs.

This means that recovery is not based on proving exactly which records are missing. It is based on the simpler rule that a failed all-or-nothing retrieval implies that required data may be missing and therefore further attempts are needed.

---

### 3.6 Boundary failure

A key design decision is that recovery is allowed only within the active basho window.

If the active window ends while the tracker is still in `RECOVERY`, the tracker terminates with an error rather than silently becoming dormant.

The rationale is that the program should not quietly stop when it knows that required data may still be missing.

This gives the system a clear boundary:

- inside the active window: retry

- at window end with unresolved recovery: fail loudly

This is simpler than extending the retry window indefinitely, while still ensuring that unresolved incompleteness is visible.

---

### 3.7 Planning strategy

The planner is intentionally conservative.

Rather than assuming that prior local state is correct, it computes the required data set from time and basho schedule rules. This allows the system to recover from accidental deletion or other loss of previously acquired files.

The design goal is therefore not merely to fetch newly published data, but to ensure that all data that should exist as of the current time is in fact present and usable.

This makes the system resilient to:

- deleted files

- incomplete prior runs

- temporary source outages

- corrupt local artifacts

---

### 3.8 Design rationale

Several design choices are deliberate.

#### Simple state model

The runtime state model is small because the tracker’s job is small. The states express:

- whether the tracker should currently be active

- whether an update is in progress

- whether unresolved missing data is being carried forward

#### Retry by repeated full verification

The design favours correctness over optimisation. By re-evaluating what should exist and retrying failed retrievals, the tracker naturally supports recovery from missing local data.

#### All-or-nothing update outcome

Treating an update cycle as successful only when all required data is present keeps the notion of completeness straightforward and makes failure handling unambiguous.

#### Explicit failure at boundary

The tracker does not silently tolerate unresolved incompleteness once the retry window has expired. This avoids the system appearing healthy when it is not.

---

### 3.9 Scope boundaries

This design does not define the detailed mechanics of retrieval. In particular, it does not depend on a particular scraping technique or file validation heuristic.

It also does not define user-interface behaviour beyond the idea that runtime state may be surfaced to the user, for example via tray messaging.

The design likewise does not define the internal format of the canonical zip representation, only the requirement that such a representation exists and is kept in sync with the local corpus.

---

### 3.10 Known limitations and future work

The design leaves some matters for future refinement.

- Integration of the canonical zip build/update path

- Richer tray or UI behaviour

- Possible future optimisation of planning or retrieval strategy

These do not alter the present design contract, but they may affect future implementations.

# 
