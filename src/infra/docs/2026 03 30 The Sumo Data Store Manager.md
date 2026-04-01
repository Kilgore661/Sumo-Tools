# Sumo Data Store Maintainer (SDSM)

## 1. Intent

We want to work with sumo data.

We do not yet know exactly what the full scope of this will be. It is likely to include:

* maintaining a local record of sumo data available from sumodb.de, in a downloaded and easy-to-use form
* creating and maintaining derived artefacts such as Elo ratings
* building downstream products such as a website

These are not all the same kind of thing. There is a fundamental distinction between:

* the core data we want to possess and keep up to date
* further data derived from that core
* end products built from either of the above

The project structure should reflect this distinction.

---

## 2. Conceptual Structure

The central maintained object is the **Sumo Data Store Maintainer** (`SDSM`).

Its role is to maintain a local sumo data store that remains synchronised with sumodb.de and is available in forms convenient for downstream use.

In minimal form:

```python
class SDSM:
    history: History
    # Other things like Elo ratings will go here
```

At present, the canonical core of the store is `History`.

In future, additional maintained derived data may be added. Elo ratings are the clearest expected example.

This gives a three-level structure:

* **canonical data** — sumo history (`History`)
* **maintained derived data** — e.g. Elo ratings (future)
* **downstream products** — e.g. website, reports

Downstream products consume the maintained store; they do not define it.

---

## 3. Present Uncertainty

Some elements of this model are intentionally only stubs.

We know that synchronisation with sumodb.de is required. We do not yet know exactly which derived artefacts will ultimately be part of the maintained store, nor which will remain separate tools.

This document describes the intended structure, not a claim that all parts are already implemented.

---

## 4. What Is Implemented Now

The current system already supports the core requirement:

* determine required coverage
* ensure source data is available
* rebuild canonical `History`
* publish representations of that maintained state

The existing `tracker` package is best understood as the current implementation of the SDSM’s maintenance behaviour. The name is historical; the role is that of a maintainer.

Operational components such as scheduling, clocks, tray state, and alerting support this behaviour but do not define it.

---

## 5. Current Boundary

At present, the maintained store is deliberately narrow.

It consists of:

* canonical `History`
* its required representations (durable and runtime)

Derived artefacts such as Elo ratings are **not yet part of the maintained store**.

Downstream products such as a website are outside the maintained system entirely. They are consumers of the store.

---

## 6. Growth by Promotion

Future growth should happen by **promotion, not leakage**.

A new derived artefact should begin life outside the maintained system.

It should only be promoted into the SDSM if:

> **it proves stable, broadly reusable, and valuable enough to guarantee as part of the maintained system**

This condition is crucial.

It prevents:

* premature inclusion of experimental features
* accumulation of application-specific logic in the core
* erosion of the boundary between maintained data and downstream products

If a derived artefact meets this standard, it may be added to the maintained store:

```python
class SDSM:
    history: History
    elo_ratings: EloRatings  # example of promoted derived data
```

Until then, it remains external.

---

## 7. Summary

The system is evolving toward a structure in which:

* `History` is the canonical core
* `SDSM` is the maintained store (currently `History`, later possibly more)
* additional derived data may be included, but only by explicit promotion
* downstream products consume the store and remain outside it

This model reflects the current implementation while providing a clear and controlled path for future development.

---

# Appendix A: Codebase Mapping

This section maps the conceptual model onto the current codebase.

## Core Concepts

* **`History`**
  The canonical representation of sumo data.
  This is the core of the maintained store.

* **`SDSM` (conceptual)**
  Not yet a concrete class in code.
  Represented in practice by the combination of:
  
  * `History`
  * persistence layer (durable + runtime representations)

---

## Maintenance (SDSM Behaviour)

* **`tracker` package**
  Implements the maintenance control plane.
  Responsible for:
  
  * running the maintenance loop
  * coordinating updates
  * applying retry/failure policy

* **`planner`**
  Determines what data coverage is required.

* **`update_cycle`**
  Executes a maintenance cycle:
  
  * ensure source data
  * rebuild `History`
  * publish representations

---

## Maintenance Machinery

* **`downloader`**
  Acquires source HTML from sumodb.de.

* **`parser`**
  Reconstructs canonical `History` from source data.

* **`persistence` / `ledger`**
  Publishes and tracks durable representations of the store.

---

## Operational Support (Non-Core)

* **`schedule` / `config`**
  Timing and configuration of maintenance.

* **`tray` / `alert`**
  User-facing status and notifications.

These support maintenance but are not part of the maintained store itself.

---

## Out of Scope (for now)

* Elo ratings
* website generation
* statistical analysis tools

These are currently **external consumers** of the maintained store.

They may later be promoted into the SDSM **only if they meet the promotion criteria**:

> stable, broadly reusable, and valuable enough to guarantee as part of the maintained system
