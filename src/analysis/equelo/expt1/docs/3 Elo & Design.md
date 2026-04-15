# Elo+ — Closed-System Elo with Entry and Exit (Expt1)

## Status

This document is a **design and experimental note** for the rating system used in Expt1.

It is not a finished theory. Several claims are supported empirically, but key
questions remain open (see “Open questions”).

---

## 1. Motivation

The standard Elo rating system assumes a fixed population:

- ratings are exchanged only through pairwise interactions
- total rating mass is conserved
- the mean rating is stable

However, sumo is an **open population**:

- new rikishi enter the system
- existing rikishi retire

Applying standard Elo in this setting introduces external flows of rating mass.

---

## 2. Open-system Elo

In the open system:

- entrants are initialised at a baseline rating `b`
- departing rikishi leave with rating `r ≠ b`

This leads to:

- non-conservation of rating mass at the system level
- drift in the mean rating over time

### Observed (Expt1)

- the mean rating varies over time
- structural changes in the population (e.g. around 1989) produce visible shifts

---

## 3. Closed-system formulation (Elo+)

Elo+ modifies the handling of departures to restore conservation.

For each departing rikishi:

- let `r` be their rating
- let `μ` be the mean rating of the active population
- let `δ = r - μ`

Let `n` be the number of remaining rikishi.

Each survivor receives:

```

-δ / n

```

The departing rikishi is then removed.

### Properties

- rating mass is conserved across basho boundaries
- the mean rating remains constant (up to numerical precision)

---

## 4. Why uniform redistribution?

Elo updates depend only on **rating differences**.

Uniform redistribution shifts all surviving ratings by the same amount, which:

- preserves all pairwise differences
- should therefore preserve expected scores

### Status

- difference preservation: **true by construction**
- preservation of expectations and dynamics: **not yet verified empirically**

---

## 5. Observations from Expt1

Comparing open vs closed systems:

### Open system

- mean rating drifts over time

### Closed system (Elo+)

- mean rating remains approximately constant
- redistribution events occur at basho boundaries

### Diagnostics

- redistribution magnitude is generally small, especially post-1989
- per-bout updates remain the dominant source of rating change

---

## 6. Interpretation

Elo+ enforces conservation of rating mass in an open population.

This removes drift in the mean, but raises the question:

> Does this change anything that matters?

---

## 7. Open questions (TBD)

These questions remain unresolved.

### 7.1 Equivalence to standard Elo

Is Elo+ equivalent to open-system Elo up to an additive constant?

To verify:

- difference invariance (empirical)
- trajectory equivalence (ratings over time)
- ranking stability at basho boundaries
- predictive equivalence (expected scores)

---

### 7.2 Magnitude of redistribution

How large is the correction relative to normal Elo dynamics?

To analyse:

- distribution of redistribution magnitudes (not just max)
- comparison with:
  - typical bout update size
  - variance of ratings

---

### 7.3 Effect on dynamics

Even if pairwise differences are preserved instantaneously:

- does redistribution alter long-term trajectories?
- are feedback effects introduced over many basho?

---

## 8. Limitations and concerns

These are not necessarily defects, but areas where interpretation may be questioned.

### 8.1 Absolute rating levels

Ratings are anchored at the baseline `b`.

- absolute values may appear unintuitive
- interpretation should be relative, not absolute

---

### 8.2 Era effects

Population size and structure vary over time.

- expansion events (e.g. 1989) may affect comparability across eras

---

### 8.3 Entrant model

All entrants are initialised at `b`.

- this is a simplifying assumption
- may affect early-career trajectories

---

### 8.4 Redistribution mechanism

Uniform redistribution is mathematically convenient but may appear artificial.

- alternative redistribution schemes are possible
- not explored in Expt1

---

### 8.5 Missing competitive context

The model does not account for:

- injuries
- scheduling asymmetries
- rank-based matchmaking constraints

Ratings may therefore conflict with domain intuition in specific cases.

---

## 9. Summary

Elo+ is a minimal modification to Elo that enforces conservation of rating mass
in an open population.

### Established

- mean invariance under Elo+
- drift in the open system

### Not yet established

- equivalence to standard Elo up to a shift
- invariance of rankings and trajectories
- predictive equivalence

---

## 10. Notes on scope

Elo+ as defined here is the formulation used in Expt1.

It should be understood as:

- a concrete experimental system
- a candidate modification to Elo
- not a complete or final model of competitive strength
