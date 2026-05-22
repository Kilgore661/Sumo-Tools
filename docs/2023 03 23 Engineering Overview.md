# Engineering Overview (Revised Draft v1.1)

## Purpose

The purpose of this system is to construct and maintain a canonical representation of sumo history.

This representation must be:

* **validated** — internally consistent and structurally correct
* **structured** — expressed in terms of the `sumo_core` domain model
* **complete (time-relative)** — containing all results that should have been published as of the current time

The system prioritises **correctness over completeness**: no canonical state is published unless it is fully validated.

---

## Publication Time

During a basho, results for each day are published at **10:00 UK time**.

Define:

> **Last day (of results)** = the latest day of the current basho for which results should have been published as of the current UK time.

When the context is clear, this is abbreviated to **“the last day.”**

This quantity determines how far the canonical history is expected to extend at any given time.

---

## Canonical Model

The canonical model (`History`) is:

> A validated, structured representation of sumo history that is complete from the epoch (1958/01) through the last day.

Formally, `History` is defined over the domain:

```
(BashoDate, Day) where Day ∈ [1, 15]
```

restricted to all `(BashoDate, Day)` pairs whose results should have been published as of the current time.

For each such pair, `History` contains:

* bout-by-bout results for that day
* the standings as of that day

A canonical `History` must be **total over this domain**.

---

## System Responsibilities

The system is divided into four components:

* **Tracker** — determines when updates should occur and orchestrates the update cycle
* **Scraper** — obtains raw source data
* **Parser** — validates and constructs canonical data from raw inputs
* **Persistence** — writes canonical snapshots

Each component has a strictly defined responsibility.

---

## Tracker

**Role**
The tracker maintains a canonical `History` that is complete from the epoch through the last day.

**Behaviour**

* Determines when new results should be available based on time
* Initiates update cycles
* Does not inspect or reason about historical completeness
* Does not interpret raw data

**Success condition**

An update cycle succeeds iff a canonical `History` is produced or confirmed to be complete through the last day.

---

## Scraper

**Role**
The scraper obtains raw artifacts required to construct history up to the last day.

**Behaviour**

* Fetches raw source data (e.g. HTML or equivalent)
* Does not parse or interpret the data
* Does not reason about history or completeness
* Does not decide what constitutes a valid result

**Success condition**

A scrape succeeds iff all raw artifacts required to cover every `(BashoDate, Day)` up to the last day have been obtained.

**Failure mode**

* Failures are expected (e.g. network issues)
* Failures are recoverable
* No partial success is accepted

---

## Parser

**Role**
The parser constructs and validates the canonical `History` from scraped data.

**Behaviour**

* Interprets raw artifacts
* Validates structural and logical correctness
* Assembles a canonical `History`

**Success condition**

A parse succeeds iff the scraped artifacts are sufficient to construct a valid canonical `History` that is total through the last day.

Otherwise, the update is rejected.

---

## Persistence

**Role**
Persistence writes canonical snapshots.

**Behaviour**

* Serialises the canonical `History`
* Writes timestamped artifacts (e.g. zip files)
* Does not interpret or validate data

---

## System Invariants

At all times:

* The canonical `History` is **valid**
* The canonical `History` is **total through the last day**
* The system may lag behind real-world publication, but must never publish invalid data

---

## Design Principles

* **Correctness over completeness**
  Incomplete updates are acceptable; invalid canonical states are not.

* **Separation of concerns**
  Each component has a single, clearly defined responsibility.

* **Deterministic contracts**
  Each stage has a clear success/failure condition.

* **Monotonic extension**
  History is extended forward in time; existing canonical data is not revised.

---

## Summary

The system maintains a canonical `History` that is:

* validated
* structured
* complete through the last day of published results

The tracker determines when updates should occur.
The scraper obtains raw data.
The parser validates and constructs the canonical model.
Persistence records the result.

Completeness is defined relative to publication time, and correctness is never compromised.
