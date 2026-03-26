# 1. Scraper

## 1.1 Purpose

The scraper module provides the basic data-acquisition functionality of the tracker: it downloads whatever sumo data the tracker asks for.

The scraper does not decide what data is needed. It receives a set of requested basho days from the tracker and attempts to ensure that the corresponding raw HTML artifacts exist locally.

If the scraper fails, it simply reports this to the tracker; it is then up to the tracker to try again.

---

## 1.2 Interface

```
scrape(requested_basho_days) -> bool
```

### 1.2.1 Inputs

* `requested_basho_days`: an iterable of `(year, month, day)` tuples

### 1.2.2 Output

* `True` if all required artifacts are present and usable after the run
* `False` if any required artifact could not be obtained or validated

---

## 1.3 Responsibilities

### 1.3.1 The scraper is responsible for

* ensuring **daily results** pages exist for each requested basho day
* ensuring **current standings** pages exist for each distinct `(year, month)` in the request
* validating that stored or fetched HTML is usable
* writing HTML artifacts to disk

### 1.3.2 The scraper is not responsible for

* deciding which basho days are needed
* interpreting or parsing HTML content
* retrying failures across runs
* maintaining coverage or completeness state

---

## 1.4 Usability criteria

The scraper applies minimal, heuristic checks to determine whether an HTML artifact is usable.

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
* The scraper does not attempt deeper validation or interpretation

---

## 1.5 Behaviour

Given a set of requested basho days, the scraper performs two phases.

---

### 1.5.1 Phase 1 — Current standings (per basho)

For each distinct `(year, month)`:

1. If the basho is known to have no data, it is skipped
2. Otherwise:

   * if a usable file already exists, it may be reused
   * if the basho has finished and the existing file predates completion, it is refreshed
   * if no usable file exists, a fetch is performed

If any required standings page cannot be obtained in usable form, the scrape fails.

---

### 1.5.2 Phase 2 — Daily results (per requested day)

For each `(year, month, day)`:

1. If the basho is known to have no data, it is skipped
2. Otherwise:

   * if a usable file already exists, it is reused
   * if not, a fetch is performed and the result is validated

If fetched HTML appears invalid (e.g. too short), it is written to:

```
files/output/text_weirdness.html
```

to aid debugging.

If any required daily results page cannot be obtained in usable form, the scrape fails.

---

## 1.6 Handling of unusable cached artifacts

If a cached HTML file exists but does not meet the usability criteria defined in Section 1.4, it is treated as **unusable**.

### 1.6.1 Behaviour

In this case:

1. The existing file is **not accepted** as satisfying the requirement
2. The scraper performs **a single fetch attempt** to obtain a replacement
3. The fetched content is validated using the same usability rules

---

### 1.6.2 Outcomes

* **If the fetched content is usable**

  * it is written to disk, overwriting the previous file

* **If the fetched content is not usable**

  * the existing (unusable) file is left in place
  * the scrape **fails** and returns `False`

No further attempts are made within the same run.

---

## 1.7 Failure model

The scraper follows an **all-or-nothing** model:

* success means *all* required artifacts are present and usable
* failure means *at least one* required artifact could not be obtained or validated

### 1.7.1 Key rule

> An unusable cached artifact must either be successfully replaced during the scrape, or the entire scrape fails.

---

## 1.8 Special cases

The following basho are treated as having no data and are skipped:

* March 2011 `(2011, 3)`
* May 2020 `(2020, 5)`

No files are required or fetched for these tournaments.

---

## 1.9 Rationale

The scraper is designed to be:

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

The scraper guarantees the following:

* it will attempt to ensure all requested artifacts exist and are usable
* it will reuse valid cached data where possible
* it will attempt a single replacement for invalid data
* it will fail if any required artifact cannot be validated

It does not guarantee:

* completeness of the request set
* correctness of HTML beyond basic heuristics
* recovery from failure within a single run

