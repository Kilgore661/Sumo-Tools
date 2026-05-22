## Proposed replacement structure

# 1. Requirements

## Purpose

A continuously running program that maintains:

* a complete and up-to-date local corpus of required basho records
* a current canonical zip representation of that corpus
* a refreshed cache derived from that zip
* a defined set of derived analysis artifacts produced from the cached history

The tracker is therefore responsible not only for source-data completeness, but for keeping the project’s published downstream outputs in sync with the current canonical history.

## Data completeness

The program must ensure that all required basho records are present and usable.

* If required source data is missing, it must be retrieved.
* If local source data exists but is unusable, it must be treated as missing.
* The canonical zip must be rebuilt whenever the required source data changes, is restored, or the zip is missing.

## Published-state completeness

The program must ensure that the published downstream state is current with respect to the canonical zip.

* If a new zip is built, the cache must be refreshed from that zip.
* Required derived analysis artifacts must then be regenerated from the refreshed cache.
* A successful tracker cycle means both the canonical artifact and the required derived artifacts are current.

## Failure handling

An update cycle is unsuccessful if any required stage fails.

Examples:

* required source data cannot be obtained
* parsing fails
* zip rebuild fails
* cache restart or cache publication fails
* a required analysis job fails
* a required derived output is not produced or is unusable

## Retry policy

* The tracker retries unsuccessful update cycles while within the active basho window.
* If the active window ends while required source data or required derived outputs are still unresolved, the tracker terminates with an error.

## Scope boundary

The tracker coordinates the pipeline. It does not itself contain domain-analysis logic.

* `infra` is responsible for acquisition, parsing, persistence, and cache publication.
* `analysis` is responsible for computing derived outputs from the published history.
* The tracker is responsible for orchestration, sequencing, and success/failure interpretation across both.

---

# 2. Specification

## 2.1 Overview

The tracker is a continuously running program that periodically attempts to ensure that the project’s required published state is complete and current.

The published state consists of:

1. required source basho data
2. canonical serialized history
3. refreshed cache contents derived from that history
4. required derived analysis outputs

It does this by repeatedly executing an update cycle while within an active basho window.

## 2.2 Required source data

At any given time, there exists a set of required source data:

> All basho records that should have been published as of the current time.

This set is time-dependent and based on the basho schedule and publication timing.

## 2.3 Required derived artifacts

At any given time, there also exists a set of required derived artifacts.

These are analysis outputs that the system defines as part of its maintained published state.

Examples may include:

* a simple results table for a requested basho such as `2026/03`
* summary extracts
* lightweight reporting files produced by the `analysis` module

The exact list of required derived artifacts is configuration or implementation policy, but the tracker treats them as first-class maintained outputs.

## 2.4 Active window

The tracker performs update cycles only while within an active window.

The active window is defined relative to a basho:

* begins a fixed number of days before basho start
* ends at a fixed time after the final scheduled basho day

Outside this window, the tracker is dormant and performs no update cycles.

## 2.5 Update cycle

An update cycle consists of:

1. determining the current required source data set
2. attempting to ensure all required source data is present and usable
3. rebuilding the canonical history snapshot if needed
4. refreshing the cache from the current canonical snapshot
5. running required analysis jobs against the refreshed cache
6. verifying that all required derived artifacts were produced successfully
7. evaluating the overall outcome

## 2.6 Outcome rule

An update cycle is treated as all-or-nothing at the tracker level.

* If all required stages succeed, the cycle succeeds.
* If any required stage fails, the cycle fails.

This keeps the meaning of success simple:

> success means the required source data, canonical zip, cache state, and required derived outputs are all current and usable.

## 2.7 Outcomes

Each update cycle has one of the following outcomes:

**Success**
All required source data is present and usable; the canonical history snapshot is current; the cache reflects that snapshot; and all required derived artifacts have been regenerated successfully.

**Failure**
One or more required stages failed.

**No new data**
No additional source data is currently required, and the published state is already current.

## 2.8 Recovery behaviour

If an update cycle fails, the tracker enters a recovery condition.

In this condition:

* some required source data may be missing or unusable, or
* some required downstream published artifact may be stale, missing, or failed

The tracker continues attempting update cycles until a successful cycle occurs or the active window ends.

## 2.9 Terminal failure

If the active window ends while recovery is still unresolved:

> The tracker terminates with an error indicating that the maintained published state could not be brought fully up to date.

This includes unresolved failures in either source completeness or required derived outputs.

## 2.10 Non-goals

The specification does not define:

* the internal implementation of scraping
* parser internals
* zip file encoding details
* the internal implementation of cache publication
* the analysis logic used to compute specific derived outputs
* exact timing parameters for polling or retries

Those belong to design and implementation.

---

# 3. Design

## 3.1 Overview

The tracker remains a continuously running coordinator, but its maintained pipeline is now:

```text
required source records
        ↓
retrieval
        ↓
parser
        ↓
canonical History
        ↓
serialisation to zip
        ↓
cache refresh / republish
        ↓
analysis jobs
        ↓
derived artifacts
```

This extends the current archive-maintenance design into a broader published-artifact pipeline. The parser still transforms raw HTML into validated `History` , the serialiser still persists that `History` as zip-backed JSON , and the cache still publishes the loaded history into shared memory for downstream consumers . The new addition is that analysis jobs become an explicit downstream phase after cache refresh.

## 3.2 Main components

### Tracker

The tracker is the top-level controller.

Its responsibilities are:

* maintain runtime state
* determine whether an update attempt should occur
* invoke planning, retrieval, rebuild, cache refresh, and analysis phases in order
* interpret overall success or failure
* terminate with an error if recovery remains unresolved when the active window ends

### Planner

The planner determines what source data should exist as of the current time.

Its responsibilities are unchanged:

* determine the latest basho day whose data should have been published
* derive the required source-record set
* provide that set to the tracker

### Retrieval component

The retrieval component attempts to ensure that all required source records are present and usable.

Its responsibilities are unchanged:

* detect missing or unusable source records
* obtain them
* report success or failure

### Parser and serialisation path

This stage rebuilds validated `History` from the available source files and persists it as the canonical zip.

### Cache manager

This stage is responsible for ensuring that the shared-memory publisher reflects the current canonical zip.

Its responsibilities are:

* stop any prior publisher instance if one is already active
* start a new publisher using the current zip
* verify that the cache is now connectable and current

### Analysis runner

This stage invokes one or more analysis jobs from the sibling `analysis` module.

Its responsibilities are:

* connect to the refreshed cache
* run defined analysis tasks
* write required derived outputs
* report success or failure back to the tracker

## 3.3 Update flow

A normal update cycle proceeds as follows:

1. The tracker decides that an update attempt is due.
2. The planner computes the set of required source records.
3. The retrieval component ensures that all required source records are present and usable.
4. The parser rebuilds validated `History`.
5. The serialisation layer writes the canonical zip.
6. The tracker refreshes the cache by restarting the publisher against the new zip.
7. The tracker invokes required analysis jobs.
8. The tracker verifies the required derived outputs.
9. The tracker interprets the total result and updates runtime state.

## 3.4 State model

You can keep the existing state model almost unchanged:

* `DORMANT`
* `READY`
* `ACTIVE`
* `RECOVERY`

That still works because `RECOVERY` can now simply mean:

> some required maintained artifact is unresolved

not only missing source records. That preserves the nice simplicity of the present design, where recovery is about unresolved incompleteness rather than a special scheduling mode .

## 3.5 Recovery model

Recovery should now cover failures in any mandatory stage:

* source retrieval failure
* parse failure
* zip rebuild failure
* cache refresh failure
* derived-artifact generation failure

The core idea remains the same as the current design: the tracker does not need a different recovery mechanism for each failure type. It only needs the rule:

> if a required update cycle did not complete successfully, some required maintained state may be missing or stale, so further attempts are needed.

That matches the existing philosophy of retry by repeated full verification rather than by tracking a tiny bespoke repair state for each failure class .

## 3.6 Cache-refresh strategy

The tracker should treat cache refresh as a mandatory post-serialisation step.

Suggested operational rule:

1. if a cache publisher is already running, terminate it
2. start a fresh publisher from the newly built canonical zip
3. wait until the shared-memory segment is available
4. optionally verify compatibility/version metadata
5. only then run analysis jobs

This directly addresses the current known limitation that the cache is not invalidated when a new zip is produced .

## 3.7 Analysis strategy

The tracker should not embed analysis code directly.

Instead, it should treat analysis as a list of jobs with a stable invocation contract, for example:

* input: current cache
* parameters: artifact-specific options such as basho `2026/03`
* output: one or more derived result files
* success criterion: process completed and expected outputs exist and are usable

This keeps the separation of concerns clean: `infra` publishes trusted history; `analysis` consumes trusted history to create human-usable results.

## 3.8 Success semantics

The old meaning of success was roughly “the corpus is complete up to the required point” . The new meaning should become:

> the maintained published state is complete up to the required point.

That published state includes both the canonical history artifact and the required downstream outputs built from it.

## 3.9 Scope boundaries

The design does not require the tracker to know how analysis is performed internally.

The tracker is concerned with:

* dependency ordering
* process coordination
* artifact freshness
* success/failure semantics

It is not concerned with:

* HTML parsing details
* zip encoding details
* shared-memory byte layout
* statistics or table-generation logic inside `analysis`

## 3.10 Known limitations and future work

Good things to call out here:

* formal definition of which derived artifacts are mandatory
* how analysis jobs are configured
* how to detect and terminate an already-running cache publisher robustly
* whether cache freshness metadata should be exposed
* whether derived artifacts should record the source zip version or timestamp
* whether some derived jobs may later be made optional rather than mandatory

## What I’d change in one sentence

I’d replace the old tracker slogan:

> maintain a complete and up-to-date local copy of basho records, together with a canonical zip representation of that data

with:

> maintain a complete and up-to-date published history pipeline: required basho source records, canonical serialized history, refreshed cache state, and required derived analysis outputs. 

There is one design choice you should settle early: whether **all** analysis outputs are mandatory for tracker success, or whether there is a smaller configured set of “tracked” derived artifacts and everything else is best-effort. I’d recommend the latter.
