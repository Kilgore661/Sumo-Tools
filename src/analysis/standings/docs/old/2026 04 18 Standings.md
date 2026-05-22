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

# ## 3. Revised Specification

## 3.1 Delivered Capability

The standings capability now provides ranked standings over one or more basho selected from the canonical `History`.

The implementation supports:

- **single-basho standings**

- **multiple-basho standings over a contiguous basho window**

- alternative win definitions

- ranked structured outputs

- derived comparative metrics for multi-basho analysis

The capability continues to operate over canonical `History`.

---

## 3.2 Interface Shape

The current consumer-facing interface is provided as command-line tools or equivalent callable interfaces.

Representative command shapes are:

```text
single_basho_main --date YYYY/MM --wins MODE
multiple_basho_main --date YYYY/MM --direction DIR --num-basho N --wins MODE
```

These command shapes are illustrative of the required functionality and do not constrain future interfaces.

---

## 3.3 Parameters

### `date`

A basho date used as the reference point for selecting the standings scope.

For single-basho mode, this identifies the basho to evaluate.

For multiple-basho mode, this is the anchor date for selecting the basho window.

### `direction`

Supported values:

- `BACKWARDS`

- `FORWARDS`

Semantics for multi-basho mode:

- `BACKWARDS`: the given date is the last basho in scope

- `FORWARDS`: the given date is the first basho in scope

### `num-basho`

The number of basho in the standings window for multiple-basho mode.

### `wins`

Supported values:

- `real`

- `all`

---

## 3.4 Defaults

Initial defaults remain:

- `direction = BACKWARDS`

- `num-basho = 1`

- `wins = real`

Date default depends on mode and direction:

- single-basho mode: latest basho in `History`

- multiple-basho mode with `BACKWARDS`: latest basho in `History`

- multiple-basho mode with `FORWARDS`: earliest basho in `History`

---

## 3.5 Current Basho Handling

If the selected scope includes the current basho, standings shall be computed using results available up to the last day for which results are defined.

A current basho remains a basho; only the available day cutoff differs.

---

## 3.6 Win Policy

Supported standings modes are:

- **real wins**: wins in bouts where both rikishi fought

- **all wins**: real wins plus fusen-sho

Outputs may expose both values regardless of the selected ranking mode.

Paper wins remain derivable:

```text
paper wins = all wins - real wins
```

---

## 3.7 Output Forms

The capability currently produces structured tabular outputs suitable for presentation or further processing.

At minimum, rows identify the rikishi and include ranking position and relevant standings metrics.

### Single-basho outputs

Rows contain at least:

- position

- rikishi id

- shikona

- chii

- chii ordinal

- real wins

- all wins

- bout count

### Multiple-basho outputs

Rows contain at least:

- position

- rikishi id

- shikona

- chii

- chii ordinal

- real wins

- all wins

- bout count

- selected basho count

- basho present count

and may include derived comparative metrics.

---

## 3.8 Ranking Semantics

Standings shall support tied positions using competition ranking semantics.

Example:

```text
1
2
2
4
```

Stable secondary ordering (for example rikishi id) may be used for deterministic presentation.

Single-basho standings are ranked primarily by selected wins totals.

Multiple-basho standings may be ranked by derived average measures appropriate to the selected win mode.

---

## 3.9 Derived Metrics

For multiple-basho standings, the capability may compute derived metrics from core totals.

Currently supported categories include:

### Exposure Measures

- basho present count

- selected basho count

### Average Measures

- window average wins

- presence average wins

### Reliability Measures

- standard deviation

- standard error of mean (SEM)

- CI95 half-width using a symmetric normal-style approximation

These metrics are derived outputs and do not alter the underlying core standings totals.

---

## 3.10 Persistence and Run Artefacts

Runs may produce persistent artefacts for later inspection.

Current conventions may include:

- timestamped run folders

- CSV outputs

- run metadata files such as `run.json`

- latest convenience copies of recent outputs

These persistence conventions are operational details and may evolve without affecting standings logic.

---

## 3.11 Architecture

The implementation is structured in layers where practical:

- **core**: standings totals and rankings from `History`

- **derived**: enriched or comparative metrics computed from core outputs

- **reporting**: CSV or other persisted artefacts

- **entrypoints**: command-line orchestration

This separation supports maintainability and future extension.

Yes — that is a strong and logical revision.



---



## ## 3.12 Presentation Layer (Draft)

### 3.12.1 Position

The standings capability shall support an initial browser-based presentation layer providing human-readable access to current standings.

This presentation layer is not the standings engine itself. It is a downstream consumer of standings outputs generated elsewhere.

Its purpose is to make standings conveniently accessible to ordinary users without requiring direct use of command-line tools, raw data files, or analytical workflows.

The initial presentation layer is intentionally narrower in scope than the full analytical capability of the standings engine.

---

### 3.12.2 Relationship to Standings Capability

The standings engine remains responsible for:

- correctness of calculations

- basho-window aggregation

- ranking logic

- metric definitions

- generation of publishable artefacts

The presentation layer remains responsible for:

- rendering standings in a browser

- allowing limited user interaction

- presenting standings clearly

- exposing only supported views

- communicating notes and caveats

The presentation layer shall not perform standings calculations itself.

---

### 3.12.3 Publication Model

The initial presentation layer shall be implemented as a simple static website.

Standings data shall be generated offline and published as precomputed artefacts.

The hosting environment is assumed to be storage-constrained and operationally simple. Accordingly:

- only a finite set of supported standings datasets shall be published

- no arbitrary historical query capability is initially required

- no server-side standings computation is initially required

- no database is initially required

Browser-side scripting may be used to load and present published datasets.

[Ed.: Design or Implementation? Exact published file formats (CSV / JSON / other) need not be fixed here.]

---

### 3.12.4 Temporal Model

The initial presentation layer shall present standings **as of the latest available data**.

Users shall not initially select arbitrary anchor dates.

The standings period shall therefore be implicitly current and backwards-looking.

Users may select the retrospective depth of the standings calculation using a supported number of previous basho.

Illustrative example:

- standings as of the latest available data over the previous 12 basho

Approximate calendar interpretations may be shown where helpful (for example, roughly two years).

---

### 3.12.5 User Controls

The page shall initially expose only controls necessary for the published-current standings model.

These shall include:

- selection of retrospective basho count

- selection of division

- sortable standings columns

The page shall not initially expose:

- arbitrary start-date selection

- arbitrary end-date selection

- free-form date-range construction

- unsupported basho-window values

The initially supported basho-window values shall be:

- 1

- 2

- 3

- 4

- 5

- 6

- 12

- 18

- 24

- 36

- 60

Initial default value:

- 6

[Ed.: Spec or Design? Exact supported values may be revised operationally.]

---

### 3.12.6 Page Structure

The initial page shall present standings in a clear tabular form.

The page shall ordinarily comprise:

- page title or heading

- control area

- standings table

- notes area

An illustrative title format is:

**Standings (Last 12 Basho: YYYY/MM–YYYY/MM)**

The title or heading shall indicate the effective standings period.

[Ed.: Exact wording and punctuation are presentation details.]

---

### 3.12.7 Table Content

The initial visible table may include columns such as:

- Position

- Shikona

- Chii

- Wins

- Count

- Mean

These columns are intended to present obvious headline standings measures rather than the full analytical outputs available internally.

Additional metrics may remain available in published artefacts or future presentation revisions.

---

### 3.12.8 Metric Semantics

Where columns such as Wins, Count, or Mean are shown, their meanings shall be defined explicitly.

Current meanings are:

- **Wins** = all wins

- **Count** = opportunities to fight

- **Mean** = Wins divided by Count

Any non-obvious definitions shall be stated in the notes area.

---

### 3.12.9 Identity Semantics

Displayed rikishi identity fields such as:

- shikona

- chii

shall be taken from the most recent basho within the effective standings period in which the rikishi appears.

This is intended to reflect the most current identity relevant to the displayed standings period.

---

### 3.12.10 Interaction Model

Browser-side interaction may include:

- changing supported basho-window views

- changing division filters

- sorting visible columns

- updating headings and notes to reflect current selections

The page shall remain usable even where richer interaction is unavailable.

[Ed.: Progressive enhancement / fallback behaviour may belong in Design.]

---

### 3.12.11 Notes and Explanations

The page shall provide a notes area or equivalent explanatory space.

This area may be used to communicate matters such as:

- meanings of Wins / Count / Mean

- data cutoff date

- interpretation caveats

- identity-field policy

- approximate basho-to-year guidance

This is intended to support ordinary users without cluttering the main table.

---

### 3.12.12 Relationship to Future Enhancements

The presentation layer design shall not prevent future support for:

- richer filtering

- additional metrics

- historical archive browsing

- alternative presentation surfaces

- improved styling

- automated publication workflows

Such future enhancements shall remain subordinate to clarity and maintainability.

---

### 3.12.13 Matters Arising

1. Should basho selectors be labelled numerically only, or with approximate year equivalents?

2. Which details belong formally in Specification versus Design versus Implementation?

3. [Ed.: If desired] Should headings also state the metric basis (e.g. all wins)?

---

## ## 3.13 Deferred Features

The following remain recognised as desirable but are not currently required:

- robustness or sensitivity analysis over window-length choices

- predictive or forward-looking models

- threshold filters and support bins

- additional domain-specific comparative metrics

- persisted optimisation caches if justified by use-cases

The capability should remain focused on delivering clear and trustworthy standings outputs.



# 4. Design

(Presentaion layer only - this doc has got way behind the code.)
