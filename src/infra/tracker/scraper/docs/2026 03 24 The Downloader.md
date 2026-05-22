# 1. Downloader

## 1.0 Caveat

Throughout this project, *validation* of an existing file is currently mostly implicit rather than re-checked. A file is validated when first downloaded, then written read-only, and later treated as acceptable if it still exists.. (Deleting the file would be OK, because it would be downloaded again.) This is because checking a file for validity takes an unacceptably long time in development/testing. Sttictly speaking then,  "usable" is a synonym for "exists" until the project is complete.

## 1.1 Purpose

The downloader module provides the basic data-acquisition functionality of the tracker: it downloads whatever sumo data the tracker asks for.

The downloader does not decide what data is needed. It receives a set of requested basho days from the tracker and attempts to ensure that the corresponding raw HTML artifacts exist locally.

If the downloader fails, it simply reports this to the tracker; it is then up to the tracker to try again.

---

## 1.2 Interface

```
download(requested_basho_days) -> RetrievalResult
```

### 1.2.1 Inputs

* `requested_basho_days`: an iterable of `BashoDayRef` tuples (think: `(year, month, day)`)

### 1.2.2 Output

`RetrievalResult` has three values:

- `FAILURE` → required data missing → try again (within window)
- `SUCCESS_UNCHANGED` → everything already present → do nothing
- `SUCCESS_CHANGED` → new data arrived → rebuild and propagate

In more detail:

#### FAILURE

**Meaning:**  
At least one required artifact could not be obtained in a usable form.

**More precisely:**

- A required file (daily results or current standings)
- either could not be fetched
- or was fetched but failed validation 
- > 
- or could not be written/read correctly

**Postcondition:**

- The required set is **not complete and usable**
- The downloader makes **no guarantee about partial results**

**How the tracker should interpret it:**

- This is a **retryable failure** (during the active window)
- Leads to `RECOVERY` state, not immediate abort

#### SUCCESS_UNCHANGED

**Meaning:**  
All required artifacts are already present locally, and no new downloads were needed.

**More precisely:**

- Every required file:
  - already existed
  - and was accepted without modification
- No files were fetched or replaced during the run

**Postcondition:**

- The required set is complete
- The local dataset is **unchanged**

**How the tracker should interpret it:**

- No rebuild needed
- No downstream work needed
- This is the steady-state “nothing to do” case

#### SUCCESS_CHANGED

**Meaning:**  
All required artifacts are now present, and at least one file was newly fetched or replaced.

**More precisely:**

- The downloader successfully ensured completeness
- and at least one artifact:
  - did not exist before, or
  - was refreshed/replaced

**Postcondition:**

- The required set is complete
- The local dataset has **changed**

**How the tracker should interpret it:**

- Rebuild canonical history
- Update downstream artifacts (cache, analysis, etc.)

---

## 1.3 Responsibilities

### 1.3.1 The downloader is responsible for

* ensuring **daily results** pages exist for each requested basho day
* ensuring **current standings** pages exist for each distinct `(year, month)` in the request
* validating that stored or fetched HTML is usable
* writing HTML artifacts to disk

### 1.3.2 The downloader is not responsible for

* deciding which basho days are needed
* interpreting or parsing HTML content
* retrying failures across runs
* maintaining coverage or completeness state

---

## 1.4 Usability criteria

The downloader applies minimal, heuristic checks to determine whether an HTML artifact is usable.

### 1.4.1 Daily results

A daily results HTML file is usable if:

* it can be read from disk, and
* its length is at least **4000 characters**

---

### 1.4.2 Current standings

A current standings HTML file is usable if:

* it can be read from disk, and
* it contains the string `<h1` (case-insensitive)

---

### 1.4.3 General notes

* These checks are intentionally simple and conservative
* They are designed only to reject clearly invalid or incomplete content
* The downloader does not attempt deeper validation or interpretation

---

## 1.5 Behaviour

Given a set of requested basho days, the downloader performs two phases.

---

### 1.5.1 Phase 1 — Current standings (per basho)

For each distinct `(year, month)`:

1. If the basho is known to have no data, it is skipped

2. Otherwise:
   
   * if a usable file already exists, it may be reused
   * if the basho has finished and the existing file predates completion, it is refreshed
   * if no usable file exists, a fetch is performed

If any required standings page cannot be obtained in usable form, the download fails.

---

### 1.5.2 Phase 2 — Daily results (per requested day)

For each `(year, month, day)`:

1. If the basho is known to have no data, it is skipped

2. Otherwise:
   
   * if a usable file already exists (see Caveat §1.0), it is reused
   * if not, a fetch is performed and the result is validated

If fetched HTML appears invalid (e.g. too short), it is written to:

```
files/output/text_weirdness.html
```

to aid debugging.

If any required daily results page cannot be obtained in usable form, the download fails.

---

## 1.6 Handling of unusable cached artifacts

If a cached HTML file exists but does not meet the usability criteria defined in Section 1.4, it is treated as **unusable**.

### 1.6.1 Behaviour

In this case:

1. The existing file is **not accepted** as satisfying the requirement
2. The downloader performs **a single fetch attempt** to obtain a replacement
3. The fetched content is validated using the same usability rules

---

### 1.6.2 Outcomes

* **If the fetched content is usable**
  
  * it is written to disk, overwriting the previous file

* **If the fetched content is not usable**
  
  * the existing (unusable) file is left in place
  * the download **fails** and returns `False`

No further attempts are made within the same run.

---

## 1.7 Failure model

The downloader follows an **all-or-nothing** model:

* success means *all* required artifacts are present and usable (see Caveat in §1.0)
* failure means *at least one* required artifact could not be obtained or validated

### 1.7.1 Key rule

> An unusable cached artifact must either be successfully replaced during the download, or the entire download fails.

---

## 1.8 Special cases

The following basho are treated as having no data and are skipped:

* March 2011 `(2011, 3)`
* May 2020 `(2020, 5)`

No files are required or fetched for these tournaments.

---

## 1.9 Rationale

The downloader is designed to be:

* **single-shot** — it performs at most one fetch per artifact per run
* **stateless** — it does not track past failures or manage retries
* **minimal** — it only ensures raw data availability, not correctness beyond basic checks

Retaining unusable files is intentional:

* it allows inspection of unexpected or malformed responses
* it avoids discarding potentially useful debugging information

This is acceptable because:

* the planner currently does **not** infer coverage from cached files
* it requests the full required range on each run
* therefore, an unusable file will be revisited in subsequent runs

---

## 1.10 Summary

The downloader guarantees the following:

* it will attempt to ensure all requested artifacts exist and are usable
* it will reuse valid cached data where possible
* it will attempt a single replacement for invalid data
* it will fail if any required artifact cannot be validated

It does not guarantee:

* completeness of the request set
* correctness of HTML beyond basic heuristics
* recovery from failure within a single run
