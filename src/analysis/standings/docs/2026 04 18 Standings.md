# 1. Position

This document concerns a **standings capability** within a broader sumo analysis system.

The wider system maintains a canonical `History` containing basho, rikishi participation, and recorded bout outcomes. This standings capability operates over that `History` to derive ranked results sets that are meaningful to users and reusable by other software components.

The purpose of the capability is to answer questions of the form:

* who is currently performing best?
* who performed best over the last *N* basho?
* how do standings change under different definitions of wins?
* how should rikishi be ordered when judged by recent results rather than by chii?

Accordingly, standings are based on **recorded bout outcomes**, not on chii.

This capability is intentionally narrower than a complete end-user application. It is a computational module that may later be consumed by command-line tools, dashboards, reports, or other analytical features.

Its initial focus is disciplined and practical:

* compute standings reliably
* support clear basho-window selection
* support meaningful win definitions
* return ranked structured results

The capability is **not** initially intended to become a general-purpose statistics laboratory or a host for arbitrary derived metrics. Broader experimentation may belong elsewhere in the wider system.

The design goal is therefore:

> provide a robust, reusable standings engine whose scope is controlled, whose outputs are understandable, and whose future extension remains possible without driving unnecessary complexity into the first implementation.


# 2. Requirements

## 2.1 Core Capability

The system shall provide a way to compute **standings of rikishi** derived from recorded bout outcomes contained in `History`.

A standing is an ordering of rikishi by one or more outcome-based metrics.

Standings shall be based on bout outcomes rather than chii.

---

## 2.2 Basho-Window Selection

The system shall support computing standings over a selectable **window of basho**.

The selection mechanism shall allow the user to specify:

* a basho date
* a direction relative to that date
* a number of basho

Together, these values shall determine the basho included in the standings window.

---

## 2.3 Direction Semantics

The system shall support at least two directional interpretations of the selected date:

* **backwards-looking**, in which the selected date is the last basho in scope
* **forwards-looking**, in which the selected date is the first basho in scope

---

## 2.4 Default Behaviour

The system shall provide sensible defaults for basho-window selection.

At minimum:

* if the direction is backwards-looking, the default date shall be the latest basho in `History`
* if the direction is forwards-looking, the default date shall be the earliest basho in `History`
* the default number of basho shall be `1`

---

## 2.5 Current Basho Evaluation

If evaluation touches the current basho, standings shall be computed using results available up to the **last day for which results are defined** in that basho.

A current basho remains a basho; only the available day cutoff differs.

---

## 2.6 Win Definitions

The system shall support standings based on alternative definitions of wins.

The initial supported definitions shall include:

* **real wins**: wins in bouts where both rikishi fought
* **all wins**: real wins plus fusen-sho

The user shall be able to request standings based on either definition, or to request output that exposes both.

---

## 2.7 Initial Ranking Metric

The system shall support standings ranked by **total wins** over the selected basho window.

This initial metric shall apply to all rikishi in scope.

---

## 2.8 Ranked Results

The system shall return standings in a structured ranked form suitable for presentation or further processing.

Each result row shall identify the rikishi and report the value or values of the ranking metric.

The system shall support tied positions.

---

## 2.9 Extensibility

The design shall allow future support for additional standings metrics, including normalized measures based on basho exposure.

The design shall also allow future support for measures of reliability associated with normalized standings.

Such future support shall not complicate or weaken the initial total-wins capability.

---

## 2.10 Module Boundary

The standings capability shall be implementable as a reusable component within a broader system.

It shall not depend upon any particular presentation layer such as a command-line interface, graphical interface, or reporting tool.

---

# 3. Initial Specification

## 3.1 First Delivered Capability

The first implementation shall provide standings ranked by **total wins** over a selected basho window.

The implementation shall operate over the canonical `History`.

---

## 3.2 Interface Shape

The initial consumer-facing interface may be expressed as a command-line tool or equivalent callable interface.

A representative command shape is:

```text
get_standings --date YYYY/MM --direction DIR --num-basho N
```

This command shape is illustrative of the required functionality and does not constrain future interfaces.

---

## 3.3 Parameters

### `date`

A basho date used as the reference point for selecting the standings window.

### `direction`

Supported values:

* `BACKWARDS`
* `FORWARDS`

Semantics:

* `BACKWARDS`: the given date is the last basho in scope
* `FORWARDS`: the given date is the first basho in scope

### `num-basho`

The number of basho in the standings window.

---

## 3.4 Defaults

Initial defaults shall be:

* `direction = BACKWARDS`
* `num-basho = 1`

Date default shall depend on direction:

* if `BACKWARDS`: latest basho in `History`
* if `FORWARDS`: earliest basho in `History`

---

## 3.5 Current Basho Handling

If the selected window includes the current basho at the relevant edge of the window, that basho shall contribute results up to the last defined day only.

All earlier basho in the selected window shall contribute all available results.

---

## 3.6 Win Policy

The first implementation shall support:

* standings by **real wins**
* standings by **all wins**
* output that displays both values for comparison

Paper wins need not be separately stored or ranked, as they are derivable:

```text
paper wins = all wins - real wins
```

---

## 3.7 Output Form

The initial output shall be a flat ranked table.

Each row should contain at least:

* position
* rikishi id
* shikona
* real wins
* all wins

Additional columns may be added provided they do not obscure the primary standing.

---

## 3.8 Ties

Tied standings shall use competition ranking semantics.

Example:

```text
1
2
2
4
```

A stable secondary ordering (for example rikishi id) may be used for display consistency.

---

## 3.9 Example Uses

### Latest Basho

```text
get_standings
```

Equivalent to:

```text
get_standings --direction BACKWARDS --num-basho 1
```

using the latest available basho.

### Last Three Basho Ending at May 2026

```text
get_standings --date 2026/05 --direction BACKWARDS --num-basho 3
```

### First Five Basho from Earliest Available Date

```text
get_standings --direction FORWARDS --num-basho 5
```

---

## 3.10 Deferred Features

The following are recognized as desirable but are not part of the first implementation:

* normalized standings based on average wins
* exposure-aware denominators
* reliability measures (e.g. CI95 width)
* support thresholds and support bins
* richer comparative views
* additional derived metrics beyond wins

The first implementation should remain focused on delivering a clear and trustworthy total-wins standings capability.
