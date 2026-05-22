# The Parser

# **1. Context in the Tracker Architecture**

## 1.1 Position in the System

The parser is a component within the `infra` layer of the *Sumo-Tools* repository. It operates as part of a larger **data ingestion and maintenance pipeline**, whose purpose is to maintain a complete, validated, and up-to-date representation of sumo basho data.

At a high level, the system consists of:

* **Tracker** (continuous process)
* **Downloader** (file acquisition; currently named “scraper”)
* **Parser** (this component)
* **Persistence layer** (serialization to zip)
* **Cache layer** (shared memory access)

The parser sits between raw data acquisition and persistence:

```text
HTML (downloaded files)
        ↓
Parser (normalisation + validation)
        ↓
History (in-memory model)
        ↓
Persistence (zip)
        ↓
Cache (shared memory)
```

---

## 1.2 Role of the Parser

The parser is responsible for:

> Converting downloaded HTML files into a validated, model-compliant `History` object.

It performs:

* structural parsing of HTML-derived data,
* reconciliation of inconsistent or ambiguous data,
* normalization into semantic domain objects,
* and preparation of data for persistence.

It is **not** responsible for:

* detecting when new data is available (Tracker),
* downloading files (Downloader),
* managing cache lifecycle (Cache),
* or serving data to applications.

---

## 1.3 Relationship to the Tracker

The parser is invoked by the Tracker as part of a continuous update loop.

The Tracker’s responsibility is to maintain the invariant:

> There exists a current, valid, up-to-date `History` snapshot.

The parser contributes to this by:

* rebuilding `History` from source HTML,
* ensuring that the resulting data is internally consistent,
* and failing fast when reconciliation is not possible.

From the Tracker’s perspective, the parser is a **deterministic transformation step**:

```text
(raw HTML files) → (validated History or failure)
```

---

## 1.4 Relationship to Persistence and Cache

The parser produces an in-memory `History` object, which is then:

1. serialized to a zip archive (Persistence layer),
2. optionally loaded into shared memory (Cache layer).

The parser defines the **data boundary**:

* upstream: messy, inconsistent HTML
* downstream: clean, model-compliant data

No downstream component needs to understand:

* HTML structure,
* rank string formats,
* or reconciliation logic.

---

## 1.5 Design Principle

The parser embodies the following core architectural principle:

> **All normalization and correction happens once, at ingestion time.**

This has several consequences:

* downstream consumers operate on trusted data,
* parsing complexity is isolated,
* and historical inconsistencies are resolved centrally.

---

# **2. Purpose**

## 2.1 Primary Purpose

The parser exists to:

> Transform imperfect, real-world HTML data into a consistent and semantically correct representation of sumo basho history.

The output is a `History` object:

```text
History : Date → BashoState
```

where:

```text
BashoState = Banzuke × Summary
```

---

## 2.2 The Core Problem

The upstream data source (e.g. sumodb) is **not perfectly reliable**.

In practice, the HTML data exhibits issues such as:

* ambiguous or missing rank sides (e.g. `"M3"` instead of `"M3e"`/`"M3w"`)
* duplicated or misordered ranks
* inconsistent annotation placement
* occasional historical anomalies
* mismatches between body tables and margin rankings

These are not hypothetical — they are observed.

### Example: Sideless Rank

```text
Margin:   M3
Body:     M3e  Aonishiki
          M3w  Another Rikishi
```

The margin alone is insufficient to determine side.

---

### Example: Transposed Entries

```text
Expected (margin):
    M5e  Rikishi A
    M5w  Rikishi B

Body:
    M5e  Rikishi B
    M5w  Rikishi A
```

The data is valid but **misordered**.

---

## 2.3 Why a Simple Parser Is Not Enough

A naive parser would:

* read rank strings,
* assign them directly,
* and propagate errors downstream.

This would lead to:

* inconsistent rank assignments,
* incorrect historical records,
* and fragile downstream analysis.

Instead, this parser:

> **actively corrects known classes of upstream errors**

---

## 2.4 The Role of the FSM

The finite state machines (FSMs) exist specifically to address these issues.

They provide:

* structured parsing of rank sequences,
* validation against expected margin data,
* and controlled recovery from inconsistencies.

This is not just syntactic parsing.

It is:

> **a reconciliation process between two imperfect representations of the same underlying reality**

* body rows (with structure and side information)
* margin data (with ordering and expected membership)

---

## 2.5 Identity vs Representation

A key design principle of the parser is:

> **Rikishi identity (`RikId`) is authoritative; textual rank representations are not.**

Consequences:

* rank strings in HTML are treated as *inputs*, not truth
* final rank is represented as a semantic `Chii`
* reconciliation is based on identity + structure, not string equality

---

## 2.6 Output Guarantees

The parser guarantees that, on success:

* every rikishi in the output has:
  
  * a valid `RikId`
  * a normalized `Chii`
  * a consistent `Shikona`

* the banzuke is internally consistent

* daily results refer only to known rikishi

* no out-of-domain entities (e.g. `Mz`) appear in the final model

---

## 2.7 Non-Purposes

The parser explicitly does **not** aim to:

* preserve exact HTML structure,
* reproduce upstream errors,
* or model all possible entities present in source data.

Examples of excluded or de-emphasized data:

* `Mz` (Mae-zumo participants)
* “Bg” (absence markers)
* informational sections such as retirements or shikona changes

These may be parsed incidentally but are not part of the core model.

---

## 2.8 Summary

In one sentence:

> The parser converts unreliable HTML representations of banzuke and results into a clean, validated, identity-driven historical dataset.

---

# **3. Inputs and Outputs**

## 3.1 Overview

The parser operates as a **deterministic transformation**:

```text
(downloaded HTML files) → (validated History)
```

It consumes locally stored HTML files (already downloaded by the Tracker) and produces a fully normalized in-memory model, which is then passed to the persistence layer.

---

## 3.2 Inputs

The parser consumes two categories of HTML input:

### 3.2.1 Current Standings (Primary Input)

Location (by convention):

```text
files/output/current standings/{year} {month:02d}.html
```

This file serves **two distinct purposes**:

1. **Margin data source**
   
   * Provides the expected ordered list of `(RikId, Chii)`
   * Used as the reference for FSM reconciliation

2. **Body HTML source**
   
   * Contains the banzuke tables that are parsed into row streams
   * These rows are fed into FSMs

This dual use is important:

> The same file provides both the *expected structure* (margin) and the *observed structure* (body).

---

### 3.2.2 Daily Results (Secondary Input)

Location (by convention):

```text
files/output/HTML results/{year} {month:02d}/{day}.html
```

* One file per day (1–15)

* Parsed after the banzuke has been validated

* Used to construct:
  
  * `DailyResults`
  * `RikishiPerformance`

---

## 3.3 Derived Inputs (Intermediate Structures)

Before FSM processing, the parser constructs several intermediate data structures.

### 3.3.1 Margin Data

From `get_margin_data(...)`:

```text
sorted_margin_data : List[(RikId, Chii)]
dups               : Dict[...]
```

* `sorted_margin_data`
  
  * ordered list of expected ranks
  * used as the authoritative reference sequence

* `dups`
  
  * duplicate-rank pool
  * used by FSM to resolve ambiguous rank assignments

---

### 3.3.2 FSM Body Stream

From body parsing and adapters:

```text
List[BanzukeRow]
```

Each `BanzukeRow` contains:

* `rank_string` (raw, e.g. `"M3"`, `"Y"`)
* optional east/west rikishi (`RikishiData`)
* annotation context (implicit via row type)

This is the **input stream consumed by FSMs**.

---

### 3.3.3 FSM Configuration

From parser code:

```text
FSM_CONFIG = [
    ('Y', YokozunaFSM),
    ('OSK', OSK_FSM),
    ('M', GruntFSM),
]
```

This defines:

* which FSM handles which rank family
* the order in which FSMs are applied

---

## 3.4 Outputs

### 3.4.1 Primary Output: BashoState

For a single basho:

```text
BashoState = Banzuke × Summary
```

#### Banzuke

```text
Dict[RikId, FinalBanzukeEntry]
```

Where each entry contains:

* `chii` (normalized rank, including side and annotation)
* `shikona` (name)

Derived entirely from FSM-validated output.

---

#### Summary

Constructed from daily results:

```text
Summary = {
    daily_results,
    rikishi_performances
}
```

* `daily_results`
  
  * bouts per day

* `rikishi_performances`
  
  * wins/losses/absences per rikishi

---

### 3.4.2 Aggregate Output: History

Across multiple basho:

```text
History : Date → BashoState
```

This is built incrementally:

```text
for each date:
    parse_bashostate(date)
    add to History
```

---

### 3.4.3 Persistence Output (Downstream)

The parser passes `History` to the persistence layer:

```python
save_history_with_annotations(history, filename)
```

Which produces:

```text
filename.zip
    └── filename.json
```

Containing:

* serialized `History`
* `Chii` stored as ordinal integers
* no `Mz` entries

---

## 3.5 Output Invariants

On successful parsing, the following are guaranteed:

### 3.5.1 Identity Consistency

* Every entry is keyed by valid `RikId`
* No duplicate keys
* All daily results reference known `RikId`

---

### 3.5.2 Rank Validity

* Every ranked rikishi has a valid `Chii`
* No sideless ranks remain
* No invalid rank strings are propagated

---

### 3.5.3 Model Compliance

* Output conforms to the core model:
  
  * `Banzuke`
  * `Summary`
  * `History`

* No raw HTML artifacts remain

---

### 3.5.4 Domain Filtering

The following are excluded from final output:

* `Mz` (Mae-zumo)
* non-ranked informational entries
* parsing-only constructs

---

## 3.6 Failure Behaviour

If parsing fails for a basho:

* the parser may:
  
  * raise an exception, or
  * return an error indicator (implementation-dependent)

* that basho is **not included** in `History`

* no partial or invalid data is persisted

This ensures:

> The persisted dataset is always internally consistent.

---

## 3.7 Worked End-to-End Example

### Input

**Current standings (simplified):**

```text
Margin:
    M3
    M4

Body:
    M3e  Aonishiki
    M3w  Hokutofuji
    M4e  Someone
    M4w  SomeoneElse
```

**Daily results (Day 1):**

```text
Aonishiki vs Hokutofuji → Aonishiki wins
```

---

### Processing

* Margin → sorted `(RikId, Chii)` with sideless `M3`

* FSM:
  
  * resolves `M3` → `M3e`, `M3w`
  * assigns correct rikishi to each

* Daily parser:
  
  * uses `RikId` mapping from FSM output

---

### Output

```text
Banzuke:
    Aonishiki   → M3e
    Hokutofuji  → M3w
    ...

Summary:
    Day 1:
        Aonishiki beats Hokutofuji
```

---

## 3.8 Summary

The parser:

* consumes:
  
  * current standings HTML
  * daily results HTML

* produces:
  
  * validated `BashoState`
  * aggregated `History`

* guarantees:
  
  * identity consistency
  * rank correctness
  * model compliance

And it does so by:

> combining structural parsing with FSM-based reconciliation against expected margin data.

---

# **4. Conceptual Model (Parser-Relevant Subset)**

## 4.1 Overview

The parser does not operate directly on HTML concepts such as:

* table rows,
* rank strings,
* or textual annotations.

Instead, it targets a **semantic domain model** in which:

* identity is explicit,
* rank is structured,
* and ordering is well-defined.

This section describes only the parts of the model that are **essential to understanding the parser**.

---

## 4.2 Identity: `RikId` Is Primary

Each rikishi is identified by a unique:

```text
RikId : int
```

This is the **only authoritative identifier**.

All parser operations ultimately reduce to:

```text
RikId → (rank, name, results)
```

### Key Principle

> **Identity is authoritative; representation is not.**

This has several consequences:

* rank strings are not used as keys
* name (`shikona`) is not used for identity
* all reconciliation is performed against `RikId`

---

### Example

Even if HTML contains:

```text
"M3e Aonishiki"
"M3e Aonishiki (alt spelling)"
```

Both map to the same:

```text
RikId = 12345
```

The parser never relies on string equality.

---

## 4.3 Rank Representation: `Chii`

Ranks are represented by a structured object:

```text
Chii = (level, number, side, annotation)
```

Where:

* `level` ∈ {Y, O, S, K, M, J, Ms, Sd, Jd, Jk}
* `number` ∈ ℕ
* `side` ∈ {e, w}
* `annotation` ∈ {empty, TD, HD, OB, YO, ...}

---

### Example

```text
"M3e"     → (M, 3, e, ∅)
"M3wHD"   → (M, 3, w, HD)
"Y1e"     → (Y, 1, e, ∅)
```

---

## 4.4 Ordering: `Chii.ordinal()`

Each `Chii` has a total ordering:

```text
ordinal : Chii → int
```

This defines:

* rank hierarchy
* ordering within a banzuke
* serialization format

---

### Example Ordering

```text
Y1e < Y1w < Y2e < ... < O1e < ... < M1e < M1w < M2e < ...
```

---

### Key Principle

> **Rank ordering is numeric, not textual.**

This avoids ambiguity such as:

* `"M10"` vs `"M9"`
* `"Ms2"` vs `"J1"`

---

## 4.5 Banzuke

The banzuke is represented as:

```text
Banzuke:
    RikId → Chii
    RikId → Shikona
```

This is a **mapping**, not a list.

Ordering is derived from `Chii.ordinal()` when needed.

---

### Consequence

* There is no requirement for rank strings to be unique
* Duplicate visible ranks (e.g. multiple `"M3"`) are resolved structurally

---

## 4.6 Summary

The summary captures tournament outcomes:

```text
Summary:
    daily_results
    rikishi_performances
```

Where:

* results are keyed by `RikId`
* not by rank or name

---

## 4.7 Separation of Concerns

The model separates:

| Concept  | Representation |
| -------- | -------------- |
| Identity | `RikId`        |
| Rank     | `Chii`         |
| Name     | `Shikona`      |
| Results  | `DailyResults` |

The parser enforces this separation.

---

## 4.8 Why Rank Strings Are Not Trusted

HTML provides rank strings such as:

```text
"M3"
"M3e"
"M3wHD"
```

These are:

* incomplete (missing side)
* inconsistent (annotation placement)
* sometimes incorrect

Therefore:

> Rank strings are treated as **hints**, not truth.

---

### Example: Ambiguous Rank

```text
Margin: M3
Body:   M3e A
        M3w B
```

The string `"M3"` does not encode enough information.

Only the combination of:

* structure (row layout)
* identity (RikId)
* and ordering

can resolve the true ranks.

---

## 4.9 FSM as a Model Enforcer

The FSM layer exists to enforce:

> consistency between the observed structure (body) and expected structure (margin)

It produces:

```text
RikId → Chii
```

which satisfies:

* valid structure
* correct ordering
* resolved ambiguity

---

## 4.10 Out-of-Model Entities

Certain entities appear in source data but are not part of the model.

### Example: `Mz` (Mae-zumo)

* appears in upstream HTML
* does not represent a ranked position
* is excluded from `Banzuke`

---

### Principle

> The model includes only **ranked banzuke participants**.

Anything outside that:

* may be tolerated during parsing
* but is not persisted

---

## 4.11 Annotation Semantics

Annotations (e.g. `HD`, `TD`) are:

* part of `Chii`
* but semantically weak

The only guaranteed rule is:

> **empty annotation dominates non-empty**

Ordering among non-empty annotations is not semantically significant.

---

## 4.12 Model Invariants

The parser produces data satisfying:

### Identity

* every rikishi has a unique `RikId`

### Rank

* every ranked rikishi has a valid `Chii`
* no sideless ranks remain

### Consistency

* ordering derived from `ordinal()` is valid
* no structural contradictions exist

---

## 4.13 Summary

The parser targets a model where:

* identity (`RikId`) is primary,
* rank (`Chii`) is structured and ordered,
* textual representations are unreliable,
* and only meaningful domain entities are preserved.

This model explains:

* why FSM reconciliation is necessary,
* why rank strings are not trusted,
* and why the parser performs normalization rather than direct extraction.

---

# **5. End-to-End Pipeline**

## 5.1 Overview

The parser operates as a **multi-stage transformation pipeline**, converting raw HTML into a validated `BashoState`, and then aggregating these into a `History`.

At a high level:

```text
Current Standings HTML
        ↓
Margin Extraction + Body Extraction
        ↓
FSM Reconciliation (Banzuke)
        ↓
Validated Banzuke
        ↓
Daily Results Parsing (uses validated banzuke)
        ↓
Summary
        ↓
BashoState
        ↓
History (across dates)
        ↓
Persistence (zip)
```

Each stage is deterministic and feeds the next.

---

## 5.2 Stage 0 — Orchestration

At the top level:

```text
for date in range:
    basho_state = parse_bashostate(date)
    add to History
save History
```

The parser processes one basho at a time, then aggregates.

---

## 5.3 Stage 1 — Load Current Standings

### Input

```text
files/output/current standings/{year} {month}.html
```

### Output

* raw HTML (for body parsing)
* structured margin data

### Responsibilities

* read file
* extract rank-related data
* prepare inputs for downstream stages

---

## 5.4 Stage 2 — Margin Extraction

From the current standings HTML:

```text
sorted_margin_data : List[(RikId, Chii)]
dups               : Dict[...]
```

### Responsibilities

* extract all ranked rikishi
* construct expected `(RikId, Chii)` pairs
* sort by `Chii.ordinal()`
* identify duplicate ranks

---

### Example

```text
Raw margin:
    M3
    M3
    M4

Processed:
    [(A, M3), (B, M3), (C, M4)]

dups:
    "M3" → [A, B]
```

---

## 5.5 Stage 3 — Body Parsing

The same HTML is parsed into logical rows:

```text
List[BanzukeRow]
```

Each row represents:

* a rank entry
* or an annotation
* or a structural artifact

---

### Example

```text
Row 1: "M3e Aonishiki"
Row 2: "M3w Hokutofuji"
Row 3: "TD"
```

---

## 5.6 Stage 4 — FSM Segmentation and Execution

The body rows are processed by a sequence of FSMs:

```text
YokozunaFSM → OSK_FSM → GruntFSM
```

Each FSM:

* consumes a prefix of the row stream
* processes only its rank family
* stops when it encounters an incompatible row

---

### Key Mechanism

```text
while rows remain:
    run FSM
    advance by rows_processed
```

Segmentation is **emergent**, not predefined.

---

## 5.7 Stage 5 — FSM Reconciliation

Each FSM:

1. interprets rows structurally
2. infers rank assignments
3. reconciles with `sorted_margin_data`

---

### Inputs

* `BanzukeRow` stream
* `sorted_margin_data`
* `dups`

---

### Output

```text
Dict[RikId, FinalBanzukeEntry]
```

---

### Example: Sideless Rank Resolution

```text
Margin: M3
Body:   M3e A
        M3w B

FSM output:
    A → M3e
    B → M3w
```

---

### Example: Transposition Recovery

```text
Margin:
    A → M5e
    B → M5w

Body:
    M5e B
    M5w A

FSM corrects:
    A → M5e
    B → M5w
```

---

## 5.8 Stage 6 — Build Validated Banzuke

FSM outputs are merged into:

```text
Banzuke:
    RikId → Chii
    RikId → Shikona
```

At this point:

* all ranks are normalized
* all ambiguity is resolved
* the banzuke is authoritative

---

## 5.9 Stage 7 — Adapt for Daily Parser

The validated banzuke is converted into a legacy-compatible structure:

```text
banzuke_mz : Dict[RikId, {...}]
```

This includes:

* `chii` (structured rank)
* `code` (ordinal-derived classification)
* optional `'Mz'` entries for compatibility

---

### Purpose

* reuse existing daily parser
* avoid rewriting complex bout parsing logic

---

## 5.10 Stage 8 — Parse Daily Results

For each day:

```text
_parse_daily_results(day_html, banzuke_mz)
```

---

### Key Property

Daily parsing is done **relative to the validated banzuke**.

* uses `RikId` for lookup
* uses `Chii` for classification
* does not rely on rank strings in HTML

---

### Example

```text
Aonishiki vs Hokutofuji

Lookup:
    rid(Aonishiki) → M3e
    rid(Hokutofuji) → M3w
```

---

## 5.11 Stage 9 — Build Summary

From daily results:

```text
Summary:
    daily_results
    rikishi_performances
```

Includes:

* bout outcomes
* win/loss records
* absences

---

## 5.12 Stage 10 — Assemble BashoState

```text
BashoState = Banzuke × Summary
```

This is the complete representation of one basho.

---

## 5.13 Stage 11 — Aggregate History

Across dates:

```text
History[date] = BashoState
```

---

## 5.14 Stage 12 — Persist

Finally:

```text
save_history_with_annotations(history, filename)
```

Produces:

```text
filename.zip → filename.json
```

---

## 5.15 Key Pipeline Properties

### Deterministic

* same input → same output

---

### Identity-Driven

* all joins via `RikId`

---

### Single Correction Point

* all inconsistencies resolved during FSM stage

---

### Layered Processing

* standings → structure
* FSM → validation
* daily → results

---

### No Backtracking

* each stage consumes and produces forward-only

---

## 5.16 Failure Points

The pipeline may fail at:

* margin extraction
* body parsing
* FSM reconciliation
* daily parsing

Failure results in:

* no `BashoState` for that date
* no partial persistence

---

## 5.17 Summary

The parser pipeline:

* ingests HTML,
* extracts structure,
* reconciles inconsistencies,
* constructs a semantic model,
* and persists a clean historical dataset.

Each stage has a clear responsibility, and the FSM stage is the critical point where unreliable input is transformed into authoritative data.

---

## 6. Component Responsibilities

This section maps the end-to-end pipeline onto the actual parser modules. The point is not to document every helper, but to state clearly which module owns which responsibility, and how the pieces fit together. The parser is not a monolith. It is a small pipeline of cooperating components, with a clear boundary between extraction, reconciliation, compatibility adaptation, orchestration, and persistence hand-off.

At the highest level, the responsibilities break down like this:

```text
current standings HTML
    ├─ parser2_margin.py        → margin extraction
    ├─ parser2_stub.py          → body table extraction
    ├─ parser2_body_adapter.py  → body → FSM row adaptation
    └─ parser2_body.py          → FSM orchestration / validation

validated banzuke
    └─ parser2_utils.py         → compatibility adapter for daily parser

daily results HTML
    └─ parser_daily.py          → daily bout parsing

single basho / date range
    └─ parser2.py               → top-level orchestration and save hand-off
```

### 6.1 `parser2.py`: top-level orchestration

`parser2.py` owns the top-level parse flow. It is the entry point that turns “available basho in a date range” into a `History`, and then hands that `History` to persistence. The outer workflow is:

1. determine which basho are available,
2. parse each basho with `parse_bashostate(date)`,
3. store the result in a `History`,
4. call `save_history_with_annotations(...)` to persist it. 

This means `parser2.py` is responsible for:

* range-level orchestration,
* per-basho orchestration,
* and the boundary between parsing and persistence.

It is **not** responsible for:

* parsing body tables directly,
* parsing daily results directly,
* or implementing reconciliation itself.

Those are delegated.

A simplified view of its role is:

```text
parse_range
    → parse_bashostate(date)
        → margin stage
        → body/FSM stage
        → daily-results stage
        → final assembly
    → save History
```

That role is visible directly in `parse_and_save_history(...)`, which computes the output path, ensures the output directory exists, and then calls `save_history_with_annotations(history, full_path)`.

### 6.2 `parser2_margin.py`: current standings marginalia extraction

`parser2_margin.py` owns the extraction of rank-bearing information from the “current standings” HTML. Its main public responsibility is `get_margin_data(date)`, which:

* calls the trusted raw marginalia parser,

* converts raw `chii` strings into `Chii` objects,

* filters out non-ranked entries such as `Mz` and `Sj`,

* sorts the result by `Chii`,

* and returns:
  
  * the sorted `(RikId, Chii)` list,
  * the duplicates structure,
  * and the raw HTML text for the body parser. 

This module therefore owns the creation of the parser’s **expected reference sequence**.

That is an important distinction:

* the body parser extracts what the page body *appears* to say,
* the margin parser extracts what the page marginalia *claims* the ranked roster is.

The FSM layer exists to reconcile those two.

A useful mental model is:

```text
parser2_margin.py = “what should be there, in rank order”
```

### 6.3 `parser2_stub.py`: raw body-table extraction

`parser2_body.py` imports `parse_body` from `parser2_stub.py`, which makes clear that `parser2_stub.py` owns raw body extraction from the current standings HTML. 

Its role is to:

* parse the HTML body tables,
* preserve division/table structure,
* and return a representation of the body that is still close to the source.

This module is **not yet at the semantic level** of the core model. It is still operating in terms of table-like structures and row-like source entities.

Conceptually:

```text
parser2_stub.py = “extract the body tables from the current standings HTML”
```

This is a distinct responsibility from margin extraction, even though both start from the same HTML file.

### 6.4 `parser2_body_adapter.py`: adapt body data into FSM input

Once the raw body tables exist, they still are not in the form the FSM expects. `parser2_body.py` imports `adapt_body_data_for_fsm(...)` from `parser2_body_adapter.py`, which establishes that this adapter layer is responsible for converting parsed body tables into FSM-ready row streams. 

It also provides `_extract_performance`, which `parser2_body.py` calls before running the FSMs. That means this adapter layer is doing two jobs:

* reshaping body data into `BanzukeRow` streams,
* and extracting body-derived performance metadata such as prizes.

This is an important design boundary. The adapter is where source-oriented body tables become parser-oriented row streams. It therefore owns:

* reshaping,
* normalization of row structure,
* and the parser’s last purely structural phase before validation.

Conceptually:

```text
parser2_body_adapter.py = “turn extracted body tables into FSM-consumable rank rows”
```

### 6.5 `parser2_body.py`: body orchestration and FSM-based validation

This is the parser’s main reconciliation module. `parse_and_validate_body(...)` is where:

* raw body HTML is parsed,
* body data is adapted,
* special prizes are extracted,
* FSMs are selected and run,
* their outputs are merged,
* and the validated banzuke mapping is returned.

This module owns:

* FSM configuration,
* rank-family routing,
* margin slicing,
* Makuuchi shared-stream sequencing,
* lower-division per-stream processing,
* and parser-level handling of FSM failure.

The key config is explicit in `FSM_CONFIG`, which maps:

* `Y` → `YokozunaFSM`
* `O`, `S`, `K` → `OSK_FSM`
* `M`, `J`, `Ms`, `Sd`, `Jd`, `Jk` → `GruntFSM`. 

It also defines the Makuuchi rank order:

```text
['Y', 'O', 'S', 'K', 'M']
```

and processes Makuuchi as one shared body stream, advancing by `rows_processed` after each FSM run. Lower divisions are handled one division at a time.

This module therefore is the parser’s **validation core**, but not because it contains validation logic itself. Rather, it owns the orchestration of the FSM validation layer.

A precise summary is:

```text
parser2_body.py = “drive the FSMs over the adapted body rows and merge their outputs”
```

### 6.6 FSM package: rank-family-specific reconciliation engine

The FSM package is not part of the top-level parser orchestration, but from the parser’s point of view it is a major dependency. The parser-visible contract is minimal:

* construct the FSM with `date`, `sorted_margin_data`, and `dups`,
* call `run(fsm_body_stream)`,
* read `fsm.output`,
* and for Makuuchi shared-stream processing, read `fsm.rows_processed`.

The parser does **not** need to know:

* token classes,
* internal states,
* or reconciliation algorithms.

That is all internal to the FSM package.

So in a parser technical document, the FSM package should be treated as:

```text
FSM = “black-box rank-family validator/reconciler”
```

with the parser depending only on the public contract above.

### 6.7 `parser2_utils.py`: compatibility layer for the daily parser

This module contains one of the most important bridging functions in the codebase: `adapt_banzuke_for_daily_parser(...)`.

Its responsibility is very narrowly defined and explicitly explained in its own docstring: it translates the modern FSM-validated banzuke structure into the legacy “rikishi context dictionary” expected by `_parse_daily_results(...)`. 

This module therefore owns:

* compatibility adaptation,
* mixed-type handling for `Mz`,
* and ordinal-derived classification fields needed by the legacy parser.

It does **not** parse any HTML itself.
It does **not** validate ranks.
It exists purely to bridge between:

* the new parser output, and
* the trusted old daily parser.

Conceptually:

```text
parser2_utils.py = “make validated banzuke data look like legacy daily-parser input”
```

That compatibility role is crucial, because it explains why this module exists at all rather than simply rewriting the daily parser.

### 6.8 `parser_daily.py`: legacy daily results parser

The daily parser is responsible for turning daily result HTML files into `DailyResults`. It runs *after* the banzuke has already been validated, and it consumes the compatibility context produced by `adapt_banzuke_for_daily_parser(...)`. This means daily parsing is downstream of FSM reconciliation, not independent of it. That relationship is explicit in the top-level per-basho flow shown in `parser2.py`: validate first, adapt, then parse daily pages 1–15. 

This module owns:

* bout extraction,
* daily result construction,
* handling of `Mz` boundary cases in legacy form,
* and reuse of the previously trusted result-parsing logic.

It does **not** determine who belongs in the ranked banzuke. That has already been settled by the standings/body/FSM pipeline.

So:

```text
parser_daily.py = “parse bout outcomes against an already-validated roster context”
```

### 6.9 `parser_warning_logger.py`: diagnostics, not semantics

Although not central to the data model, the warning logger is part of the parser’s operational structure. It owns diagnostic output and logging, not parsing semantics. Its presence matters because the parser is intended as a robust ingestion component that may need to record irregularities without polluting the core logic.

In a technical account, it should be described as:

* operational support,
* not part of the semantic transformation pipeline.

### 6.10 Persistence hand-off: parser stops at `History`

The parser’s responsibility ends when it has a complete `History` in memory and hands it to the persistence layer. The persistence code then serializes that `History` into a zip-backed JSON representation, with `Chii` stored as ordinals and `History` stored as a date-keyed mapping. The parser triggers that hand-off via `save_history_with_annotations(...)`, but does not itself own zip writing or shared-memory publication.

That boundary is important for later docs:

* Parser doc: how `History` is produced
* Persistence doc: how `History` is stored
* Cache doc: how stored `History` is exposed efficiently
* Tracker doc: how freshness and publication are coordinated across all of them

### 6.11 Responsibility summary table

A concise summary table for this section would be:

| Module                    | Responsibility                                                                            |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| `parser2.py`              | Top-level orchestration over basho/date ranges; hand-off to persistence                   |
| `parser2_margin.py`       | Extract and prepare sorted ranked margin data from current standings HTML                 |
| `parser2_stub.py`         | Extract raw body tables from current standings HTML                                       |
| `parser2_body_adapter.py` | Convert body tables into FSM-ready row streams; extract body-derived performance metadata |
| `parser2_body.py`         | Route rank families to FSMs; run reconciliation; merge validated banzuke output           |
| `FSM` package             | Rank-family-specific parsing and reconciliation against margin data                       |
| `parser2_utils.py`        | Adapt validated banzuke into legacy daily-parser input format                             |
| `parser_daily.py`         | Parse daily bout results using validated roster context                                   |
| persistence layer         | Serialize `History` to zip-backed JSON                                                    |
| cache layer               | Load serialized `History` into shared memory for consumers                                |

### 6.12 Summary

The parser is best understood not as one parser file, but as a set of cooperating modules with sharply different roles:

* margin extraction,
* body extraction,
* body adaptation,
* FSM orchestration,
* compatibility adaptation,
* daily results parsing,
* top-level orchestration.

That decomposition is a strength of the design. It localizes complexity, makes the FSM dependency narrow and explicit, and allows the parser to reuse trusted legacy logic where rewriting would be risky.

---

## 7. The Parser’s Contract with the FSM

This section defines **exactly what the parser assumes about the FSM layer** and what it requires in return. The FSM is the parser’s only non-trivial dependency, but the interface between them is deliberately narrow and clean.

The key idea is:

> The parser treats the FSM as a **black-box reconciler** that converts structured row streams into validated rank assignments.

---

## 7.1 Role of the FSM (from the parser’s perspective)

From the parser’s point of view, the FSM is responsible for:

* interpreting a stream of `BanzukeRow` objects,
* assigning a valid `Chii` to each rikishi,
* reconciling those assignments with `sorted_margin_data`,
* and returning a consistent mapping:

```text
RikId → FinalBanzukeEntry
```

The parser does **not**:

* inspect FSM internal states,
* depend on token types,
* or replicate reconciliation logic.

---

## 7.2 FSM Construction

Each FSM is constructed with:

```text
(date, sorted_margin_data, dups)
```

### Parameters

* `date`
  
  * used for date-specific logic (e.g. historical anomalies)

* `sorted_margin_data`
  
  * ordered list of expected `(RikId, Chii)`
  * serves as the reconciliation reference

* `dups`
  
  * duplicate-rank pool
  * used by FSM to resolve ambiguity

---

### Parser Assumptions

The parser assumes:

* `sorted_margin_data` is already filtered and sorted
* `dups` is consistent with that margin data
* both are valid inputs for FSM construction

It does **not** validate these further.

---

## 7.3 FSM Execution

The parser invokes the FSM via:

```text
fsm.run(fsm_body_stream)
```

Where:

```text
fsm_body_stream : List[BanzukeRow]
```

---

### Effects of `run(...)`

After execution:

* `fsm.output` contains the validated mapping
* `fsm.rows_processed` indicates how many rows were consumed

---

## 7.4 Output Contract

The parser expects:

```text
fsm.output : Dict[RikId, FinalBanzukeEntry]
```

Where each entry contains:

* `chii` (fully resolved, including side and annotation)
* `shikona`

---

### Output Guarantees

The parser relies on the FSM to ensure:

1. **Rank completeness**
   
   * every included rikishi has a valid `Chii`

2. **No ambiguity**
   
   * no sideless ranks remain

3. **Consistency with margin**
   
   * output aligns with `sorted_margin_data`
   * modulo allowed recovery (e.g. transpositions)

4. **Identity correctness**
   
   * mapping is keyed by correct `RikId`

---

## 7.5 Row Consumption and Segmentation

A critical part of the contract is:

```text
fsm.rows_processed
```

This enables **sequential FSM execution**.

---

### Mechanism

```text
while rows remain:
    fsm.run(rows)
    rows = rows[rows_processed:]
```

---

### Parser Assumptions

The parser assumes:

* FSM consumes a **prefix** of the row stream
* FSM does **not** over-consume
* FSM leaves the first unprocessable row untouched

---

### Implication

> FSM segmentation boundaries are determined entirely by FSM behaviour.

There is:

* no external slicing,
* no lookahead,
* no backtracking.

---

## 7.6 Rank-Family Routing

The parser determines which FSM to use based on rank family.

Configuration:

```text
'Y'     → YokozunaFSM
'O/S/K' → OSK_FSM
others  → GruntFSM
```

---

### Responsibilities Split

| Concern                       | Owned by |
| ----------------------------- | -------- |
| Which FSM to use              | Parser   |
| How to parse that rank family | FSM      |

---

## 7.7 Margin Consumption

Although the parser passes the full `sorted_margin_data` to each FSM, it does **not** track which elements are consumed.

The parser assumes:

> The FSM internally consumes and validates against the appropriate portion of the margin.

---

### Implicit Contract

* FSM must:
  
  * align output with margin ordering
  * ensure no missing or extra assignments

* parser does not verify margin exhaustion explicitly

---

## 7.8 Error Handling

The FSM may fail by raising exceptions such as:

* `ReconciliationError`
* `UnclassifiableRowError`

---

### Parser Behaviour

The parser:

* treats FSM failure as **fatal for that basho**
* does not attempt recovery or fallback
* does not partially accept results

---

### Design Principle

> All reconciliation must succeed for the basho to be valid.

---

## 7.9 Independence from FSM Internals

The parser deliberately does not depend on:

* FSM state machines
* token definitions
* transition logic
* reconciliation strategies

---

### Benefit

This allows:

* FSM implementation to evolve independently
* parser to remain stable
* clear separation of concerns

---

## 7.10 What the Parser Does *Not* Know

The parser does not know:

* how duplicates are resolved internally
* how transpositions are detected
* how annotations are normalized
* how sideless ranks are resolved

It only knows that:

> The FSM produces correct `RikId → Chii` mappings or fails.

---

## 7.11 Minimal Interface Summary

The entire parser–FSM interface reduces to:

```text
Construct:
    FSM(date, sorted_margin_data, dups)

Execute:
    run(fsm_body_stream)

Read:
    output
    rows_processed
```

---

## 7.12 Summary

The parser–FSM relationship is:

* tightly coupled in purpose,
* but loosely coupled in implementation.

The parser:

* provides structured input,
* selects the correct FSM,
* and integrates the output.

The FSM:

* performs all rank interpretation and reconciliation,
* and guarantees a consistent, validated mapping.

This contract is what allows the parser to treat the FSM as a **black-box correctness engine**.

---

## 8. Handling of Out-of-Model and Compatibility Cases

This section explains how the parser deals with **entities and data that appear in the source HTML but are not part of the core model**, and how it bridges between the new FSM-based pipeline and legacy components.

The key idea is:

> The parser **accepts messy, real-world input**, but only **persists clean, model-relevant data**.

---

## 8.1 Overview

There are three categories of “non-standard” data the parser must handle:

1. **Out-of-model entities**
   (e.g. `Mz`, `Bg`)

2. **Non-rank informational sections**
   (e.g. shin-deshi, retirements, shikona changes)

3. **Legacy compatibility requirements**
   (interaction with the existing daily parser)

Each is handled differently, but all follow the same principle:

> tolerate at ingestion → normalize or discard → never pollute the final model

---

## 8.2 `Mz` (Mae-zumo)

### 8.2.1 Nature of `Mz`

`Mz` represents **mae-zumo participants**:

* not part of the ranked banzuke
* may appear in upstream data (especially daily results)
* may be paired with ranked rikishi

---

### 8.2.2 Parser Policy

The parser enforces:

```text
Mz ∉ Banzuke
Mz ∉ History
```

That is:

* `Mz` is **never part of the final model**
* it is treated as **out-of-domain**

---

### 8.2.3 Where `Mz` Appears

* may appear in:
  
  * margin data (filtered out)
  * daily results (must be handled)

* does **not** appear in:
  
  * FSM input (rank families)
  * final `Banzuke`

---

### 8.2.4 Handling Strategy

#### During margin extraction

* `Mz` entries are filtered out before constructing `sorted_margin_data`

#### During FSM processing

* `Mz` is not a rank family
* FSMs never see or process it

#### During daily parsing

* `Mz` is reintroduced **only for compatibility**
* represented as:

```text
'chii' = 'Mz'
```

* used to:
  
  * identify and ignore `Mz vs Mz`
  * handle `Mz vs ranked` correctly

---

### 8.2.5 Example

```text
Daily result:
    M3e Aonishiki vs Mz newcomer

Parser behaviour:
    - include Aonishiki result
    - ignore Mz participant
```

---

### 8.2.6 Design Rationale

`Mz` is excluded because:

* it is not part of the ranked system
* including it would violate model invariants
* it adds no value to rank-based analysis

---

## 8.3 `Bg` (Banzuke-gai / absence markers)

### 8.3.1 Nature of `Bg`

`Bg` indicates:

* absence / not appearing on the banzuke
* typically associated with non-ranked or transitional cases

---

### 8.3.2 Parser Policy

```text
Bg ∉ Banzuke
Bg ∉ FSM processing
```

* ignored for rank validation
* treated as informational only

---

### 8.3.3 Rationale

As you noted:

> `Bg` is only relevant in the context of `Mz` and does not affect ranked structure.

Therefore it is excluded from the core model.

---

## 8.4 Informational Sections

The HTML may include sections such as:

* shin-deshi (new entrants)
* retirements
* shikona changes

---

### 8.4.1 Parser Treatment

These are:

* parsed or detectable in body extraction
* **not used in FSM or rank validation**
* **not included in `Banzuke` or `Summary`**

---

### 8.4.2 Rationale

* they do not affect rank assignment
* they can be derived from historical data if needed
* including them would expand the model beyond its purpose

---

## 8.5 Compatibility Layer for Daily Parser

One of the most important non-model concerns is:

> the parser reuses an existing daily-results parser

---

### 8.5.1 Problem

The daily parser expects a legacy structure:

```text
Dict[RikId, {
    'chii': <value>,
    'code': <value>,
    ...
}]
```

This does not match the new model directly.

---

### 8.5.2 Solution

`adapt_banzuke_for_daily_parser(...)` performs:

* conversion from `FinalBanzukeEntry` → legacy dict

* insertion of:
  
  * `chii` (either `Chii` or `'Mz'`)
  * `code` (derived from `ordinal()`)

---

### 8.5.3 Mixed-Type Handling

This is the only place where:

```text
'chii' ∈ {Chii, 'Mz'}
```

exists.

This is **intentional and contained**.

---

### 8.5.4 Example

```text
Validated:
    A → Chii(M,3,e)

Adapted:
    A → {
        'chii': Chii(M,3,e),
        'code': ordinal(...)
    }

Mz entry:
    X → {
        'chii': 'Mz'
    }
```

---

## 8.6 Why Compatibility Is Isolated

The compatibility layer exists to:

* reuse trusted legacy parsing logic
* avoid rewriting complex daily parsing code

But it is **strictly contained** so that:

* the core model remains clean
* no legacy artifacts leak into persistence

---

## 8.7 No Leakage into Persistence

The persistence layer enforces:

* only `Chii` objects are serialized
* `'Mz'` entries are excluded

---

### Result

```text
Final persisted data:
    contains only ranked rikishi
    contains only valid Chii
```

---

## 8.8 Design Pattern

The parser follows a consistent pattern:

```text
accept → normalize → isolate → exclude
```

| Stage         | Behaviour                  |
| ------------- | -------------------------- |
| Input         | tolerate all upstream data |
| Processing    | normalize and reconcile    |
| Compatibility | isolate legacy needs       |
| Output        | emit only model-valid data |

---

## 8.9 Summary

The parser handles non-standard and out-of-model data by:

* **accepting it at the boundary**
* **using it only where necessary**
* **excluding it from the final model**

Key outcomes:

* `Mz` and similar entities do not pollute the model
* legacy compatibility is preserved without compromising design
* the final dataset remains clean, consistent, and semantically meaningful

---

## 9. Error Handling and Failure Modes

This section describes how the parser behaves when things go wrong, what constitutes failure, and what guarantees are preserved.

The guiding principle is:

> **The parser either produces a fully valid `BashoState` or nothing at all.**

There is no concept of a partially valid basho.

---

## 9.1 Overview of Failure Strategy

The parser is **fail-fast and all-or-nothing** at the basho level.

For a given date:

* success → complete, validated `BashoState`
* failure → no `BashoState` produced

Across a range:

* successful basho are included in `History`
* failed basho are skipped or abort processing (depending on orchestration)

---

## 9.2 Failure Categories

Failures can occur at several stages of the pipeline.

### 9.2.1 Input / File Errors

**Cause:**

* missing HTML file
* unreadable file
* unexpected file structure

**Effect:**

* parsing cannot begin

**Handling:**

* exception raised
* basho not processed

---

### 9.2.2 Margin Extraction Errors

**Cause:**

* malformed marginalia
* invalid `chii` strings
* inability to construct `Chii`

**Effect:**

* `sorted_margin_data` cannot be built

**Handling:**

* exception raised
* no attempt to continue

---

### 9.2.3 Body Parsing Errors

**Cause:**

* HTML structure not matching expected patterns
* failure in table extraction
* adapter unable to construct valid `BanzukeRow`

**Effect:**

* FSM input cannot be constructed

**Handling:**

* exception raised
* basho parsing aborted

---

### 9.2.4 FSM Reconciliation Errors (Critical)

**Cause:**

* mismatch between body and margin that cannot be resolved
* unclassifiable rows
* duplicate ambiguity not resolvable
* structural inconsistency

**Effect:**

* no valid mapping `RikId → Chii`

**Handling:**

* FSM raises:
  
  * `ReconciliationError`
  * `UnclassifiableRowError`

* parser treats as fatal

---

### Example

```text
Margin:
    M3 A
    M4 B

Body:
    M3e C
    M3w D
```

No consistent mapping exists → failure.

---

### 9.2.5 Daily Parsing Errors

**Cause:**

* malformed daily HTML
* unexpected bout structure
* unknown `RikId` (should not happen if FSM succeeded)

**Effect:**

* incomplete or invalid `DailyResults`

**Handling:**

* treated as fatal for the basho
* no partial summary accepted

---

## 9.3 No Partial Recovery

The parser does **not**:

* skip problematic ranks
* partially accept FSM output
* partially accept daily results

---

### Design Principle

> **Consistency is more important than completeness.**

A basho is either:

* internally consistent → accepted
* inconsistent → rejected

---

## 9.4 Error Propagation

Errors propagate upward:

```text
FSM / parsing error
        ↓
parse_bashostate(date) fails
        ↓
date omitted or processing stops
```

The parser does not attempt:

* fallback strategies
* alternative interpretations
* heuristic fixes beyond FSM logic

---

## 9.5 Guarantees on Success

If a basho is successfully parsed:

### 9.5.1 Structural Guarantees

* all ranked rikishi have valid `Chii`
* no unresolved ambiguity
* margin and body are reconciled

---

### 9.5.2 Identity Guarantees

* all references use valid `RikId`
* daily results refer only to known rikishi

---

### 9.5.3 Model Guarantees

* conforms fully to `Banzuke × Summary`
* no out-of-model entities included
* no raw HTML artifacts

---

## 9.6 Guarantees on Failure

If parsing fails:

* no `BashoState` is produced
* no partial data is persisted
* previously valid data is unaffected

---

## 9.7 Interaction with Tracker

The parser’s failure behaviour is designed to support the Tracker:

* failure signals that new data is not yet reliable

* Tracker can:
  
  * retry later
  * retain previous valid snapshot

This aligns with the system invariant:

> the published `History` is always valid

---

## 9.8 Logging and Diagnostics

The parser may emit warnings via:

```text
parser_warning_logger
```

These are:

* diagnostic only
* do not affect success/failure

---

### Examples of warnings

* unexpected but recoverable annotation
* minor structural irregularity handled by FSM

---

## 9.9 Known Non-Fatal Irregularities

Some irregularities are handled internally and do not cause failure:

* sideless ranks (resolved by FSM)
* duplicate ranks (resolved via `dups`)
* minor ordering issues (transpositions)
* annotation inconsistencies

These are **expected in real data** and part of normal operation.

---

## 9.10 Summary

The parser’s error model is:

* **fail-fast at the basho level**
* **no partial acceptance**
* **strong guarantees on success**

It ensures that:

> any persisted `History` represents a fully consistent and validated dataset.

---

## 10. Persistence Boundary

This section defines where the parser’s responsibility ends and the persistence layer begins, and what is guaranteed at that boundary.

The key principle is:

> **The parser produces a complete, model-valid `History` and hands it off. It does not manage storage details.**

---

## 10.1 Boundary Definition

The parser’s final act is:

```python
save_history_with_annotations(history, filename)
```

At this point:

* `history` is fully constructed
* all validation is complete
* no further transformation is required

Everything after this call belongs to the **persistence layer**.

---

## 10.2 What the Parser Guarantees at the Boundary

The parser guarantees that the `History` object:

### 10.2.1 Is Complete

* contains all successfully parsed basho

* each basho contains:
  
  * a fully validated `Banzuke`
  * a complete `Summary`

---

### 10.2.2 Is Internally Consistent

* no unresolved rank ambiguity
* no invalid `Chii`
* no mismatched identities
* no dangling references

---

### 10.2.3 Is Model-Compliant

* conforms exactly to:

```text
History : Date → BashoState
BashoState = Banzuke × Summary
```

* uses:
  
  * `RikId` for identity
  * `Chii` for rank
  * structured data only

---

### 10.2.4 Is Clean

* contains no:
  
  * HTML fragments
  * raw rank strings
  * parser-specific artifacts
  * FSM internals

---

### 10.2.5 Excludes Out-of-Model Data

* no `Mz`
* no `Bg`
* no informational sections (retirements, etc.)

---

## 10.3 What the Parser Does Not Do

The parser explicitly does **not**:

* choose output file format
* manage file naming conventions
* handle versioning of stored data
* manage atomic writes or concurrency
* load or publish data into shared memory

These responsibilities belong to:

* **Persistence layer**
* **Cache layer**
* **Tracker**

---

## 10.4 Persistence Layer Responsibilities

The persistence layer is responsible for:

* serializing `History`
* writing it to disk
* defining file structure

From the observed implementation:

```text
filename.zip
    └── filename.json
```

Where:

* JSON contains serialized `History`
* `Chii` is stored as `ordinal()` integers
* data is human-readable (indented JSON)

---

## 10.5 Serialization Semantics

Although implemented outside the parser, the parser assumes:

### 10.5.1 `Chii` Serialization

```text
Chii → ordinal (int)
```

This preserves:

* ordering
* identity of rank

without relying on string representation.

---

### 10.5.2 Identity Preservation

* `RikId` stored as integers
* relationships preserved explicitly

---

### 10.5.3 No Legacy Leakage

* `'Mz'` strings are not serialized
* compatibility-layer constructs are excluded

---

## 10.6 Example Output Structure

Simplified example:

```json
{
  "2026/03": {
    "banzuke": {
      "12345": { "chii": 1023, "shikona": "Aonishiki" },
      "23456": { "chii": 1024, "shikona": "Hokutofuji" }
    },
    "summary": {
      "daily_results": { ... },
      "rikishi_performances": { ... }
    }
  }
}
```

Where:

* `1023`, `1024` are `Chii.ordinal()` values

---

## 10.7 Idempotence

The parser + persistence combination is:

> **idempotent with respect to input HTML**

Given identical input files:

* the same `History` is produced
* the same serialized output is written

---

## 10.8 Failure Interaction

If parsing fails:

* persistence is **not invoked**
* no output file is written or updated

This ensures:

> persisted data is always valid

---

## 10.9 Interaction with Cache

The parser does not interact directly with shared memory.

However:

* the persisted zip is the source for cache loading

* cache layer assumes:
  
  * zip contains valid `History`
  * no partial writes

This reinforces the importance of:

> parser delivering a fully consistent object

---

## 10.10 Design Principle

The boundary enforces a clean separation:

```text
Parser        → produces valid data
Persistence   → stores it
Cache         → serves it
Tracker       → coordinates updates
```

Each layer has a single responsibility.

---

## 10.11 Summary

The parser’s responsibility ends at:

> delivering a fully validated, model-compliant `History` object

It guarantees:

* correctness
* consistency
* completeness

It does **not** concern itself with:

* how that data is stored,
* how it is accessed,
* or how it is updated over time.

Those concerns are handled by other components in the system.

---

## 11. Non-Goals

This section makes explicit what the parser is **not** designed to do. These boundaries are as important as its responsibilities, because they prevent scope creep and clarify where other components (Tracker, Persistence, Cache, or future tools) take over.

The guiding principle is:

> **The parser is a one-way ingestion and normalization component, not a general-purpose data system.**

---

## 11.1 Not a General HTML Scraper

The parser does **not** aim to:

* extract all information from source HTML
* preserve full page structure
* act as a reusable HTML parsing library

It extracts only what is required to build:

```text
Banzuke × Summary
```

All other HTML content is:

* ignored,
* discarded,
* or treated as incidental.

---

## 11.2 Not a Lossless Representation of Source Data

The parser does **not** preserve:

* exact rank strings (`"M3eHD"`, etc.)
* formatting details
* table layout
* annotation positioning in source text

Instead, it produces:

> a **normalized semantic representation**

---

### Example

```text
Input:   "M3eHD"
Output:  Chii(level=M, number=3, side=e, annotation=HD)
```

The original string is not retained.

---

## 11.3 Not a Historical Record of Source Errors

The parser does **not**:

* record upstream inconsistencies
* track corrections made by the FSM
* preserve “what the HTML said”

Instead:

> it outputs only the **corrected result**

---

### Implication

You cannot reconstruct:

* original mistakes
* ambiguous cases
* raw margin/body discrepancies

from the persisted data.

---

## 11.4 Not a Query or Analysis Layer

The parser does **not**:

* provide APIs for querying data
* compute statistics
* perform analysis

Those responsibilities belong to:

* downstream tools in the repository

---

## 11.5 Not Responsible for Data Freshness

The parser does **not**:

* detect when new data is available
* decide when to re-run
* manage update schedules

This is the responsibility of the **Tracker**.

---

## 11.6 Not Responsible for File Management

The parser does **not**:

* manage input file downloads
* validate file completeness across days
* manage output file lifecycle
* perform atomic writes or versioning

These belong to:

* Downloader (input acquisition)
* Persistence (output storage)
* Tracker (coordination)

---

## 11.7 Not a Cache Manager

The parser does **not**:

* load data into shared memory
* manage cache invalidation
* coordinate readers and writers

It produces data for the cache but does not interact with it directly.

---

## 11.8 Not a Streaming or Incremental Processor

The parser does **not**:

* process partial basho data incrementally
* update a `BashoState` day-by-day
* support real-time ingestion

Instead:

> it rebuilds a complete `BashoState` from available inputs

---

### Implication

Even though current standings are updated daily:

* the parser treats each run as a **full reconstruction**
* not a delta update

---

## 11.9 Not a General Rank Parser

The parser does **not**:

* accept arbitrary rank formats
* support unknown rank systems
* attempt to generalize beyond sumo banzuke

It is explicitly:

> **domain-specific and data-source-specific**

---

## 11.10 Not Responsible for All Domain Concepts

The parser intentionally excludes:

* `Mz` (Mae-zumo)

* `Bg` (absence markers)

* informational sections:
  
  * retirements
  * shin-deshi
  * shikona changes

Even if present in HTML, they are:

* not part of the model
* not persisted

---

## 11.11 Not a Validation Layer Beyond FSM Scope

The parser does **not**:

* enforce business rules beyond rank consistency
* validate long-term historical continuity
* check cross-basho invariants

Its validation scope is:

> **within a single basho, at the level of rank assignment and results consistency**

---

## 11.12 Not Concerned with Performance Optimization

The parser:

* is not optimized for real-time performance
* does not cache intermediate results
* does not parallelize parsing

Performance concerns are addressed later via:

* serialized snapshots
* shared memory cache

---

## 11.13 Not Intended as a Stable External API

The parser:

* is an internal component of the ingestion pipeline
* is not designed as a public-facing API
* may change as internal needs evolve

External tools should depend on:

> the persisted `History`, not the parser itself

---

## 11.14 Summary

The parser is deliberately narrow in scope:

It **does**:

* parse, reconcile, and normalize data into the core model

It **does not**:

* preserve source detail
* manage data lifecycle
* serve or analyze data
* model out-of-scope entities

This strict separation enables:

* a clean architecture
* reliable downstream usage
* and a well-defined role within the Tracker system

---

## 12. Appendix — Code Map and Data Flow Summary

This appendix provides a compact reference for navigating the code and understanding the end-to-end data flow. It is intended for maintainers who want a quick orientation after reading the main sections.

---

## 12.1 End-to-End Data Flow (Single Basho)

```text
Current Standings HTML
    ↓
[parser2_margin.py]
    → sorted_margin_data, dups, raw_html
    ↓
[parser2_stub.py]
    → body tables
    ↓
[parser2_body_adapter.py]
    → List[BanzukeRow] (+ performance metadata)
    ↓
[parser2_body.py]
    → FSM orchestration
    → validated_banzuke (RikId → FinalBanzukeEntry)
    ↓
[parser2_utils.py]
    → banzuke_mz (legacy compatibility dict)
    ↓
[parser_daily.py]
    → DailyResults (days 1–15)
    ↓
[parser2.py]
    → assemble BashoState (Banzuke × Summary)
```

Across dates:

```text
for each date:
    BashoState
        ↓
History[date] = BashoState
        ↓
save_history_with_annotations(...)
        ↓
zip (JSON)
```

---

## 12.2 Key Data Structures (at a glance)

### Core model

```text
History : Date → BashoState
BashoState = Banzuke × Summary

Banzuke:
    RikId → Chii
    RikId → Shikona

Summary:
    daily_results
    rikishi_performances
```

---

### FSM interface

```text
Input:
    List[BanzukeRow]
    sorted_margin_data
    dups

Output:
    Dict[RikId, FinalBanzukeEntry]

Control:
    rows_processed
```

---

### Compatibility layer

```text
banzuke_mz : Dict[RikId, {
    'chii': Chii | 'Mz',
    'code': int
}]
```

---

## 12.3 Module-to-Responsibility Map

| Module                    | Responsibility                                                                 |
| ------------------------- | ------------------------------------------------------------------------------ |
| `parser2.py`              | Top-level orchestration; per-basho parsing; History assembly; persistence call |
| `parser2_margin.py`       | Extract and prepare sorted margin data (`sorted_margin_data`, `dups`)          |
| `parser2_stub.py`         | Extract raw body tables from standings HTML                                    |
| `parser2_body_adapter.py` | Convert body tables to `BanzukeRow` streams; extract performance metadata      |
| `parser2_body.py`         | Run FSMs; manage segmentation; merge validated banzuke                         |
| FSM package               | Rank-family parsing and reconciliation                                         |
| `parser2_utils.py`        | Adapt validated banzuke to legacy daily-parser format                          |
| `parser_daily.py`         | Parse daily bout results                                                       |
| persistence layer         | Serialize `History` to zip/JSON                                                |
| cache layer               | Load `History` into shared memory                                              |

---

## 12.4 FSM Routing Summary

```text
Rank family → FSM

Y           → YokozunaFSM
O / S / K   → OSK_FSM
M, J, Ms,
Sd, Jd, Jk  → GruntFSM
```

Execution model:

```text
while rows remain:
    run FSM
    advance by rows_processed
```

---

## 12.5 Example Data Flow (Concrete)

### Input (simplified)

```text
Margin:
    M3
    M3
    M4

Body:
    M3e A
    M3w B
    M4e C
    M4w D

Daily:
    A beats B
```

---

### Intermediate

```text
sorted_margin_data:
    [(A, M3), (B, M3), (C, M4), (D, M4)]

BanzukeRow stream:
    [M3e A, M3w B, M4e C, M4w D]
```

---

### FSM output

```text
A → M3e
B → M3w
C → M4e
D → M4w
```

---

### Final

```text
Banzuke:
    A → M3e
    B → M3w
    C → M4e
    D → M4w

Summary:
    Day 1:
        A beats B
```

---

## 12.6 Invariants Checklist

A quick checklist for validating parser correctness:

### Identity

* [ ] All keys are valid `RikId`
* [ ] No duplicates

### Rank

* [ ] Every entry has a valid `Chii`
* [ ] No sideless ranks
* [ ] Ordering via `ordinal()` is consistent

### Consistency

* [ ] Body and margin reconciled
* [ ] No unresolved duplicates

### Results

* [ ] All bouts reference known rikishi
* [ ] Performances consistent with daily results

### Cleanliness

* [ ] No `Mz` in final output
* [ ] No raw HTML artifacts

---

## 12.7 Failure Checklist

When debugging a failure:

1. **Margin stage**
   
   * Is `sorted_margin_data` correct?
   * Any invalid `chii`?

2. **Body extraction**
   
   * Are tables parsed correctly?

3. **Adapter**
   
   * Are `BanzukeRow` objects valid?

4. **FSM**
   
   * Which FSM failed?
   * Is it a reconciliation issue?

5. **Daily parsing**
   
   * Missing `RikId`?
   * Unexpected bout structure?

---

## 12.8 Glossary

| Term         | Meaning                                              |
| ------------ | ---------------------------------------------------- |
| `RikId`      | Unique identifier for a rikishi                      |
| `Chii`       | Structured rank (level, number, side, annotation)    |
| FSM          | Finite State Machine for rank parsing/reconciliation |
| Margin       | Expected ordered rank list from standings            |
| Body         | Table-derived row structure from HTML                |
| `Mz`         | Mae-zumo (out-of-model)                              |
| `dups`       | Duplicate-rank pool for ambiguity resolution         |
| `BanzukeRow` | FSM input row abstraction                            |

---

## 12.9 Final Summary

The parser can be understood as:

```text
HTML → structured rows → FSM reconciliation → semantic model → serialized history
```

With:

* **identity-first design** (`RikId`)
* **structured rank representation** (`Chii`)
* **single correction point** (FSM)
* **clean output boundary** (`History`)

This appendix ties the conceptual model, pipeline, and code structure into a single reference for practical use.
