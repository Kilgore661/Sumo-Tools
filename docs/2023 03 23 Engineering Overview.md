# Sumo Tools — Engineering Notes

## 1. Context

We are building a set of tools for analysing sumo data.

The system is structured in layers:

    raw data → canonical model → shared memory → tools

- Raw data: scraped HTML and related files
- Canonical model: validated representation of sumo history (`sumo_core`)
- Shared memory: fast access layer for tools
- Tools: analysis, reporting, etc.

The immediate goal is to establish a reliable pipeline that produces a
canonical representation of sumo history and keeps it up to date.

---

## 2. General Principles

### Top-down, contract-first design

The system is designed from the top level downwards.

Each component is defined in terms of:

- what it assumes (inputs)
- what it guarantees (outputs)

Lower-level modules are then implemented to satisfy these contracts.

---

### Separation of concerns

Each layer has a single responsibility:

- tracker: when to run
- scraper: fetch data
- parser: validate and build canonical model
- persistence: write canonical snapshot
- memory: load into shared memory
- tools: consume

Components do not take on responsibilities outside their layer.

---

### Time-driven orchestration

The system is driven by when data is expected to exist,
not by inspecting the filesystem.

---

### Offensive (non-defensive) coding

Code assumes that inputs satisfy their declared contracts.

Invalid states are excluded by design, not handled defensively.

Checks are only introduced where failure modes are part of the problem
domain (e.g. network unreliability, provisional external data).

---

### Explicit handling of real uncertainty

Only uncertainty that arises from the domain is handled explicitly:

- network failures (scraping)
- provisional or incomplete data (parsing)

Other hypothetical failure modes are not treated as part of normal execution.

---

### OOP as a design tool, not an implementation requirement

Object-oriented thinking is used to identify:

- concepts (e.g. BashoWindow, UpdateResult)
- responsibilities
- boundaries

Implementation remains simple:

- data structures for state
- functions for behaviour

Classes are used only where they add clarity.

---

### Incremental development with traceability

Development proceeds in small, coherent steps:

- define contracts
- implement minimal structure
- refine through use

Progress is recorded alongside the design.

---

## 3. Progress

(Monday 23 March 2026)

- Canonical model (`sumo_core`) established and validated via shared memory
  (repository tag: `core-v1`)

- Tracker implementation started
  (responsible for maintaining an up-to-date canonical `History`)

- Tracker skeleton implemented:
  
  - main loop and state model (DORMANT / READY / ACTIVE)
  - scheduling logic (basho window, trigger hour)
  - update cycle interface
  - in-memory ledger
  - stub tray and alert modules

- Tracker runs and scheduling works; scraper and parser not yet implemented

- Next steps:
  
  - implement scraper
  - implement parser / canonical builder
