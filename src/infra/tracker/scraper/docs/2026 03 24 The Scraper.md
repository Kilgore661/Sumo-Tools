# Scraper (Draft 1.0)

## Purpose

The scraper is responsible for acquiring the raw HTML artifacts required to construct canonical `History`.

It performs **data acquisition only**.

It does not interpret, validate, or reason about the data.

---

## Role within Tracker

The scraper is a **tracker module**.

The tracker:

* determines which `(Date, Day)` pairs are required
* invokes the scraper with those requests

The scraper:

* obtains the corresponding raw artifacts
* ensures they are present in the raw-data area

The scraper does **not** determine what should be requested.

---

## Input

The scraper is invoked with an ordered list of requested `BashoDayRef`s.

Each `BashoDayRef` represents:

* a basho `Date`
* a basho `Day` (1–15)

This list is determined entirely by the tracker.

---

## Required Artifacts

Given a requested list of `BashoDayRef`s, the scraper must ensure the existence of:

### Daily Results

For each requested `(Date, Day)`:

* obtain the corresponding daily results HTML
* store it in the raw-data location used by the legacy system

---

### Current Standings

For each distinct `Date` represented in the request list:

* obtain the corresponding per-basho standings HTML
* store it in the raw-data location used by the legacy system

This artifact represents the **current standings** of the basho.

It is not restricted to post–day-15 “final results”.

---

## Success Condition

A scrape succeeds iff:

* all required daily results artifacts are present and usable, and
* all required current-standings artifacts are present and usable

after the scrape attempt.

Partial success is failure.

---

## Failure Handling

Failures are:

* expected
* recoverable
* non-fatal to the tracker

Typical causes:

* network failure
* blank or malformed responses
* failure to write required artifacts

On failure, the tracker will retry in a subsequent cycle.

---

## Existing Artifacts

If a required artifact is already present and usable:

* it may be reused
* it does not need to be re-downloaded

For current-standings artifacts:

* the scraper may refresh an existing artifact
* this allows the stored state to reflect the evolving basho

---

## Scraper-Level Validation

The scraper may perform minimal checks to reject:

* blank pages
* truncated pages
* clearly incorrect responses

The scraper does **not** perform semantic validation.

---

## Non-Responsibilities

The scraper does **not**:

* determine current time or basho state
* decide whether new data should exist
* choose which `(Date, Day)` pairs are required
* interpret HTML content
* construct or validate `History`
* reason about completeness

---

## Defining Behaviour

The legacy scraper defines:

* which artifacts correspond to a given `(Date, Day)`
* where those artifacts are stored
* what constitutes a usable raw page

The legacy date-selection logic is not part of this contract.

---

## Summary

The scraper ensures that all raw HTML artifacts required for the requested `BashoDayRef`s exist in the raw-data area.

It performs acquisition only.

It succeeds only if all required artifacts are present and usable.

---

## Algorithm

The scraper operates as a deterministic executor over the requested `BashoDayRef`s.

It is **postcondition-based**: its goal is to ensure that all required raw artifacts are present and usable after execution, regardless of whether they were newly fetched or already present.

### High-Level Procedure

Given an ordered list of requested `BashoDayRef`s:

1. Derive the set of distinct `Date`s represented in the request list
2. Ensure current-standings artifacts for each `Date`
3. Ensure daily-results artifacts for each requested `BashoDayRef`
4. Return success iff all required artifacts are present and usable

---

### Step 1: Derive Required Artifact Sets

From the requested list:

* `requested_days` = all requested `BashoDayRef`s
* `requested_dates` = distinct `Date`s appearing in the list

These determine the complete set of required raw artifacts.

---

### Step 2: Ensure Current Standings

For each `Date` in `requested_dates`:

1. Determine the expected storage location for the current-standings artifact
2. If a usable artifact already exists:

   * it may be reused
3. Otherwise:

   * fetch the corresponding standings HTML
   * perform minimal sanity checks (e.g. not blank, structurally plausible)
   * write the artifact to the expected location

If any required current-standings artifact cannot be established as present and usable, the scrape fails.

The scraper may refresh an existing artifact when necessary to reflect the current basho state.

---

### Step 3: Ensure Daily Results

For each requested `BashoDayRef`:

1. Determine the expected storage location for the daily-results artifact
2. If a usable artifact already exists:

   * it may be reused
3. Otherwise:

   * fetch the corresponding daily-results HTML
   * perform minimal sanity checks (e.g. not truncated or clearly invalid)
   * write the artifact to the expected location

If any required daily-results artifact cannot be established as present and usable, the scrape fails.

---

### Step 4: Return Result

The scraper returns:

* `True` if all required artifacts are present and usable after execution
* `False` otherwise

---

## Design Notes

### Postcondition-Based Behaviour

The scraper does not distinguish between:

* artifacts fetched during this run, and
* artifacts already present

It only guarantees that all required artifacts exist and are usable after execution.

This allows:

* idempotent operation
* safe retries
* reuse of previously acquired data

---

### Ordering

The scraper may process:

* current-standings before daily results, or
* daily results before current-standings

The contract does not depend on ordering.

The only requirement is that all required artifacts are established.

---

### Failure Model

Failure is immediate and global:

* if any required artifact cannot be obtained or validated, the scrape fails
* partial success is not accepted

This aligns with the tracker’s all-or-nothing update model .

---

### Relationship to Legacy Behaviour

This algorithm reproduces the behaviour of the legacy scraper in a request-driven form:

* identical artifact mapping (day → daily results, date → standings)
* identical storage locations
* equivalent minimal sanity checks
* reuse of existing artifacts

Legacy date-selection logic is intentionally excluded.
