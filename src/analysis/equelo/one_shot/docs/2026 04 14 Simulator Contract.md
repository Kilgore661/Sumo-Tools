# `one_shot` Simulator Contract

## 1. Purpose

The `one_shot` simulator performs a **single chronological Elo pass** over a prepared modern `History`, using **closed-population semantics** and a caller-supplied initialization rule.

Its sole purpose is to produce the basho-boundary mapping:

[
\mathrm{bsr}(c,t)
]

where:

* ( c ) = chii (identified by `Chii.ordinal()`)
* ( t ) = basho start date

This mapping is used for convergence analysis.

---

## 2. Scope

The simulator operates under the following fixed conditions:

* **modern regime only** (history pre-filtered to 1989+)
* **closed population only**
* **single forward pass**
* **no diagnostics, logging, or reporting**

---

## 3. Inputs

### 3.1 Prepared History

A `History` satisfying:

* contains exactly the basho to simulate
* basho are in canonical order (iteration by index over keys)
* missing basho may exist; ordering is defined by key sequence, not calendar arithmetic
* each basho provides:

  * a `banzuke`
  * a `summary` of bouts
* each rikishi on the banzuke has an associated `Chii`

The history is assumed **pre-vetted**. The simulator performs no cleansing.

---

### 3.2 Elo Parameters

A structure containing exactly:

* `q`: logistic scale parameter
* `k`: callable mapping `ordinal -> float`

No baseline rating is part of this contract.

---

### 3.3 Entrant Initialiser

A callable:

* input: `Chii`
* output: `float`

Used to initialise a rikishi when first encountered.

Assumptions:

* each rikishi is initialised at most once
* this property is guaranteed by the prepared history

---

## 4. Outputs

### 4.1 Primary Output

A mapping:

```text
Date -> (Chii.ordinal() -> float)
```

For each basho date `t`, this provides:

* the rating of the rikishi occupying each chii
* evaluated at **basho boundary (start of basho)**

This defines:

[
\mathrm{bsr}(c,t)
]

This is the **only required observable**.

---

### 4.2 No Additional Outputs

The simulator does **not** return:

* rikishi-level ratings
* day-level ratings
* diagnostics
* logs

---

## 5. Processing Model

For each basho in sequence order:

1. determine current active rikishi from the banzuke
2. process departures from previous basho (closed mode)
3. initialise any new rikishi using their basho-start chii
4. construct the mapping `chii.ordinal() -> rating` (basho-start snapshot)
5. process all days and bouts in order
6. carry updated ratings forward

---

## 6. Internal State

The simulator may internally maintain:

```text
RikId -> float
```

because:

* bouts are observed between rikishi
* updates must be applied at rikishi level

This is strictly an **implementation detail**.

The public contract remains **chii-centred**.

---

## 7. Bout Update Rule

For each scored bout:

1. read current ratings of both rikishi
2. compute expected outcome using `q`
3. compute actual outcome
4. determine K-factor using `Chii.ordinal()` from current basho
5. compute Elo delta
6. apply equal and opposite updates

Bouts with decision:

* `"fusen"`
* `"blank"`

are ignored.

---

## 8. Closed Population Semantics

At basho boundary:

* rikishi present in previous basho but absent in current basho **depart**
* their rating effect is redistributed uniformly across surviving active rikishi from the previous basho

This behaviour is mandatory.

---

## 9. Invariants

The simulator guarantees:

1. **Single-pass chronology**
   ratings evolve strictly forward in basho order

2. **Basho-boundary observability**
   outputs correspond to basho start states

3. **Closed-population handling**
   departures are redistributed over survivors

4. **Per-bout conservation**
   rating mass is conserved in each scored bout (up to numerical precision)

5. **Single initialisation per rikishi**
   each rikishi is initialised exactly once

6. **Chii identity**
   chii are identified canonically by `Chii.ordinal()`
   string forms are for display only

---

## 10. Non-Responsibilities

The simulator does **not**:

* load data
* filter history to modern regime
* handle bios
* collapse annotations or chii
* compute convergence metrics
* generate charts
* write files

These belong to higher layers in `one_shot`.

---

## 11. Summary Statement

The `one_shot` simulator consumes prepared modern history and Elo parameters, runs a single closed-mode chronological Elo pass, and produces the basho-boundary mapping:

```text
Date -> (Chii.ordinal() -> float)
```

which defines ( \mathrm{bsr}(c,t) ), the rating associated with each chii over time.

---
