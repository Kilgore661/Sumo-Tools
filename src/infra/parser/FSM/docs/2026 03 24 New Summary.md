

# FSM Module: Technical Documentation

## 1. Purpose and Scope

The FSM module is responsible for converting a stream of parsed **banzuke body rows** into a validated, normalized mapping of rikishi to final rank entries.

It sits between:

- upstream extraction (which produces `BanzukeRow` objects), and

- downstream consumers (which require consistent `FinalBanzukeEntry` data).

This module does **not**:

- parse HTML or raw text,

- decide which rank family is being processed,

- or construct the expected margin data.

Instead, it implements a set of **finite state machines (FSMs)** that:

- parse rank-family-specific row patterns,

- infer rank assignments,

- reconcile them against expected margin data,

- and emit normalized results.

---

## 2. High-Level Model

The module processes two parallel representations of the same banzuke:

- **Body stream**: row-oriented, includes east/west placement and annotations

- **Margin data**: precomputed ordered list of expected `(RikId, Chii)`

The FSM layer merges these into a single authoritative output:

```
Dict[RikId, FinalBanzukeEntry]
```

This makes the module a **parser + reconciler**, not just a parser.

---

## 3. Public Contract

### 3.1 Inputs

Each FSM instance is constructed with:

- `date`

- `sorted_margin_data: List[Tuple[RikId, Chii]]`

- `dups: Dict[str, List[RikId]]`

And executed via:

```
run(banzuke_row_stream: List[BanzukeRow]) -> Dict[RikId, FinalBanzukeEntry]
```

### 3.2 Outputs

- `Dict[RikId, FinalBanzukeEntry]`

- `rows_processed` (number of rows consumed)

### 3.3 Termination

An FSM stops when:

- a row cannot be classified, or

- a valid token is illegal in the current state

This allows multiple FSMs to consume a shared row stream sequentially.

---

## 4. FSM Family Overview

The module provides three concrete FSMs:

### 4.1 YokozunaFSM

- Handles rank family: `Y`

- Based on `SanyakuBaseFSM`

### 4.2 OSK_FSM

- Handles rank families: `O`, `S`, `K`

- Based on `SanyakuBaseFSM`

### 4.3 GruntFSM

- Handles all non-sanyaku ranks:
  
  - `M`, `J`, `Ms`, `Sd`, `Jd`, `Jk`

---

## 5. Architectural Design

### 5.1 Layering

The module is structured into:

1. **Data classes**
   
   - `BanzukeRow`, `RikishiData`, `FinalBanzukeEntry`

2. **Token classes**
   
   - `SR_Token`, `GR_Token`, `AR_Token`, `GA_Token`

3. **Base FSM engine**
   
   - `BaseFSM`

4. **Concrete FSM implementations**
   
   - `GruntFSM`
   
   - `SanyakuBaseFSM` → `YokozunaFSM`, `OSK_FSM`

---

### 5.2 BaseFSM Responsibilities

`BaseFSM` defines the parsing skeleton:

For each row:

1. Classify → token

2. Compute → next state

3. Execute → transition action

4. Update state

5. Increment `rows_processed`

At end:

- Perform FSM-specific cleanup

- Verify margin data fully consumed

Subclasses implement:

- `_classify_token`

- `_get_next_state`

- `_execute_transition_action`

- `_end_of_stream_action`

---

## 6. Rank Parsing Strategies

### 6.1 Sanyaku (Y, O, S, K)

- Rows contain only the rank letter (`Y`, `O`, etc.)

- Rank number is **derived from position** using a counter:
  
  - `Y1`, `Y2`, `O1`, `O2`, etc.

- Annotation rows (`HD`, `TD`, `OB`, `YO`) modify the most recent rank

### 6.2 Grunt Ranks

- Rows explicitly encode rank:
  
  - e.g. `Ms42`, `J3`

- Annotation rows follow ranks

- Repeated ranks produce a special `GA_Token`, resolved later as `HD`

---

## 7. Reconciliation Model

### 7.1 Core Principle

Every inferred rank from the body must be validated against the expected margin data.

### 7.2 Normal Case

A match requires:

- same `RikId`

- same rank level

- same rank number

Side and annotation are reconciled with specific rules.

---

### 7.3 Recovery Mechanisms

The FSM attempts recovery before failing:

#### Duplicate Pool

- Handles ambiguous rank assignments

- Uses `dups` to match valid candidates

#### Transposition Recovery

- Swaps adjacent margin entries if reversed

#### Sideless Recovery

- Accepts margin entries without side (`Side.NONE`)

- Prefers margin over body when conflicting

#### Annotation Handling

- Special handling for annotation mismatches

- Margin `YO` overrides body annotation

---

### 7.4 Failure

If reconciliation fails:

- `ReconciliationError` is raised

---

## 8. State Machines

### 8.1 GruntFSM States

States control valid token sequences:

- Start → rank row required

- Rank → annotation or next rank allowed

- Special handling for repeated rank (`GA_Token`)

Includes:

- deferred resolution of repeated ranks

- historical special-case logic

---

### 8.2 SanyakuBaseFSM States

Simpler state model:

- Rank rows increment counter

- Annotation rows modify previous rank

Special rule:

- Yokozuna (`Y`) allows annotations at start

- O/S/K do not

---

## 9. Known Irregularities

The FSM includes explicit handling for historical anomalies, e.g.:

- 1978-03 tsukedashi special case

This reflects a design choice:

> correctness on real historical data takes precedence over purity.

---

## 10. Dispatcher (Out of Scope)

This module does **not** decide which FSM to use.

That responsibility lies outside, typically:

```
Y      → YokozunaFSM
O/S/K  → OSK_FSM
others → GruntFSM
```

---

## 11. Treatment of Mz (Mae-zumo)

### 11.1 Domain Context

`Mz` represents mae-zumo participants:

- not part of Grand Sumo rankings,

- may appear in upstream data (e.g. torikumi/results),

- sometimes paired with ranked rikishi.

### 11.2 System Policy

The system applies the following rules:

- `Mz vs Mz` → ignored entirely

- `Non-Mz vs Mz` → processed only for the non-Mz rikishi

- `Mz` rikishi are never persisted

- `Mz` never appears in `FinalBanzukeEntry`

### 11.3 Design Rationale

`Mz` is treated as an **out-of-domain artifact**:

- It exists in upstream data sources (e.g. sumodb)

- It is not part of the modeled banzuke

- Including it would pollute the rank model

Therefore:

> The FSM module tolerates `Mz` at the ingestion boundary but excludes it from the normalized output model.

### 11.4 Architectural Implication

- `Mz` is **not a rank family**

- It is **not handled by any FSM**

- It must be filtered or ignored before or during FSM usage

This is intentional and correct.

---

## 12. Design Philosophy

The FSM module is:

- **Domain-driven**: built around real banzuke structure

- **Fault-tolerant**: recovers from imperfect data

- **Pragmatic**: includes special-case fixes where needed

- **Selective**: accepts noisy input but emits clean output

Key principle:

> Accept what the source provides, but only model what is meaningful.

---

## 13. Summary

The FSM module is a **rank-family-specific parsing and reconciliation engine** that:

- consumes structured banzuke rows,

- infers rank assignments,

- validates them against expected data,

- recovers from known inconsistencies,

- and emits normalized rikishi entries.

It deliberately excludes out-of-domain entities such as `Mz`, ensuring that the final model represents only valid Grand Sumo banzuke rankings.

---
