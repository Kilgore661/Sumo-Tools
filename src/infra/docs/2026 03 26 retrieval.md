Retrieval is the right next boundary to pin down, because it is now the **control signal** for the whole downstream path, exactly as set out in the proposal. 

## Retrieval mini-spec

### Purpose

The retrieval stage is responsible for ensuring that the required managed source files exist locally for the current cycle.

Its job is not to interpret basho timing, not to parse HTML, and not to decide what downstream work is needed. Its job is simply:

> given the required source-record set for this cycle, ensure that every required source file exists locally, and report whether the local managed source dataset changed while doing so.

That final clause is now crucial, because the retrieval outcome drives whether canonical publication, cache refresh, and analysis must run. 

---

## Role in the system

The planner determines **which** source records are required.

The retrieval stage determines whether those required records are now present locally, and whether achieving that required state changed the local managed source dataset.

So retrieval sits between:

* **planner output**: what must exist
* **update-cycle branching**: what must happen next

It is therefore a repair-and-report stage, not a transformation stage.

---

## Inputs

Retrieval requires:

### 1. Required source-record set

A complete set of the source records that must exist locally for the current cycle.

Each required record must be specific enough for retrieval to determine:

* its expected local managed path
* its source location or acquisition rule

### 2. Managed storage rules

Retrieval must know where managed source files live locally and how their paths are determined.

### 3. Download capability

Retrieval must be able to attempt acquisition of any required source record that is absent.

---

## Output

Retrieval must return exactly one of three outcomes.

### `FAILURE`

After the retrieval attempt, one or more required source files still do not exist locally.

### `SUCCESS_UNCHANGED`

After the retrieval attempt, all required source files exist locally, and no new files were downloaded during the attempt.

### `SUCCESS_CHANGED`

After the retrieval attempt, all required source files exist locally, and one or more files were downloaded during the attempt.

That is the whole contract.

The retrieval stage does not return parser results, zip results, cache results, or analysis results.

---

## Core rule

The key design rule is:

> retrieval is presence-based, not content-diff-based.

If a required managed source file already exists at its expected managed location, retrieval treats that requirement as satisfied.

It does not inspect the existing file for semantic correctness, mutation, or tampering.

That follows directly from the invariant you settled earlier:

> existence of a required managed source file implies validity.

So retrieval repairs **absence**, not **alteration**.

---

## Success criteria

Retrieval succeeds if and only if:

* every required source file exists locally by the end of the retrieval attempt

Retrieval returns `SUCCESS_CHANGED` if and only if success was achieved and at least one file had to be downloaded during the attempt.

Retrieval returns `SUCCESS_UNCHANGED` if and only if success was achieved and no file had to be downloaded.

Retrieval returns `FAILURE` otherwise.

---

## Operational behaviour

Given a required source-record set, retrieval should conceptually do this:

1. examine each required source record

2. map it to its expected local managed file path

3. check whether that file already exists

4. if it exists, treat that requirement as satisfied

5. if it does not exist, attempt to download it

6. after the attempt, check whether the file now exists

7. if any required file still does not exist, return `FAILURE`

8. otherwise:
   
   * if at least one download occurred, return `SUCCESS_CHANGED`
   * else return `SUCCESS_UNCHANGED`

That is the whole behaviour.

---

## What counts as “changed”

A retrieval cycle counts as **changed** if retrieval had to add one or more previously absent required source files to managed storage.

In other words:

* existing file present → unchanged for that record
* missing file successfully downloaded → changed for that record

At cycle level:

* one or more such additions → `SUCCESS_CHANGED`
* none → `SUCCESS_UNCHANGED`

This keeps “changed” tightly tied to managed source-dataset change.

---

## What does **not** count as changed

The following do not, by themselves, make retrieval “changed”:

* checking that a file exists
* planning
* enumerating required records
* noticing that a file already exists
* observing suspicious or unexpected contents in an existing file, if you choose not to support such inspection

And, by the invariant, in-place edits to an existing managed file are outside contract rather than part of retrieval semantics.

So retrieval does not attempt to answer:

> did the contents of the local source dataset differ from last cycle?

It answers only:

> did this cycle have to add any missing required source files?

---

## Failure semantics

`FAILURE` means:

> after the retrieval attempt, the required managed source dataset is still incomplete.

That is the only failure condition retrieval needs.

This is nice because it keeps retrieval failure simple and objective.

Examples that would lead to `FAILURE` include:

* remote fetch failed
* expected remote source was unavailable
* file download started but no usable local file was created
* filesystem write failed
* path creation failed
* some other error prevented a missing required file from coming into existence locally

The important point is that retrieval failure is judged by the postcondition, not by the internal reason.

---

## Relationship to parser and downstream stages

Retrieval does not:

* parse downloaded HTML
* validate domain semantics
* build canonical `History`
* write the canonical zip
* start or stop cache
* produce derived artifacts

Its only responsibility is to establish the source-file precondition for those later stages.

So the contract boundary is:

* **retrieval** says whether the source dataset is complete, and whether it changed
* **everything else** is downstream of that fact

---

## Idempotence

Retrieval should be idempotent with respect to already-complete managed storage.

If the required source files already exist locally, a repeated retrieval attempt should return `SUCCESS_UNCHANGED` and perform no further source-dataset modification.

That property is important because the tracker is expected to run repeated cycles.

---

## Required assumptions

Retrieval relies on these assumptions:

### 1. Managed-file invariant

If a required managed source file exists at its expected path, it is treated as valid.

### 2. Stable path mapping

For a given required source record, retrieval can determine one expected managed local path.

### 3. Existence is observable

Retrieval can reliably determine whether a required managed file exists.

These assumptions should be explicit, because the simplicity of retrieval depends on them.

---

## Non-responsibilities

Retrieval does not:

* detect manual tampering of existing files
* compare file contents against the source site
* verify freshness beyond the planner’s required-record set
* decide whether a missing file is “important enough” to fetch
* decide whether downstream publication should occur directly

Its contribution to that last question is only indirect: it returns one of the three retrieval outcomes.

---

## Recommended result shape

Conceptually, retrieval wants to return something like:

* `status`: `FAILURE | SUCCESS_UNCHANGED | SUCCESS_CHANGED`

Optionally, for logging/debugging, it may also return structured detail such as:

* which records were missing at start
* which records were downloaded
* which records remained unresolved

But those are secondary. The essential contract is the three-state status.

---

## Invariants after return

After `SUCCESS_UNCHANGED`:

* all required source files exist locally
* no new files were downloaded this cycle

After `SUCCESS_CHANGED`:

* all required source files exist locally
* at least one new required file was downloaded this cycle

After `FAILURE`:

* at least one required source file still does not exist locally

These are strong, useful postconditions, and downstream code can rely on them without reinterpretation.

---

## Short operational summary

Retrieval should behave like this:

* for each required source record, check whether its managed local file exists
* download only those required files that are absent
* if any required file is still absent afterwards, return `FAILURE`
* if all required files exist and at least one was downloaded, return `SUCCESS_CHANGED`
* if all required files exist and none were downloaded, return `SUCCESS_UNCHANGED`

That gives `update_cycle` exactly the control signal it needs.

The next natural one to pin down is the **cache lifecycle contract**, because that is the next stage whose behaviour depends directly on `SUCCESS_CHANGED` versus `SUCCESS_UNCHANGED`.
