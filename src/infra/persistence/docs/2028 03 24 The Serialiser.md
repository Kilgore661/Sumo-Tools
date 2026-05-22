# Sumo Serialisation Module

## Overview

This module provides a **serialization and persistence layer** for sumo tournament data structures. It enables complex domain objects (e.g. tournament states, match results, rankings, and historical records) to be:

* Converted into JSON-compatible formats
* Compressed and stored as `.zip` files
* Reconstructed back into full Python objects

The design separates **generic serialization concerns** from **domain-specific logic**, and introduces an extensible pathway for evolving data formats.

---

## Architecture

The module is structured into three main components:

### 1. `BaseSerialiser`

A generic utility class providing shared functionality:

* Enum ↔ string conversion
* JSON serialization helpers
* ZIP file persistence

#### Responsibilities

* Ensure all data is JSON-compatible
* Handle compression and file I/O
* Provide reusable helpers for higher-level serializers

#### Key Methods

```python
enum_to_str(obj)
str_to_enum(value, enum_class)
save_to_zip(data, filename)
load_from_zip(filename)
```

---

### 2. `SumoSerialiser`

The primary serializer for sumo domain objects.

#### Responsibilities

* Convert domain objects into primitive structures (`dict`, `list`, `str`, `int`)
* Reconstruct domain objects from serialized data
* Handle all core types in the `sumo_core` model

#### Supported Objects

* `BashoState` – tournament snapshot
* `Banzuke` – rankings and wrestler mappings
* `Summary` – daily results and performance data
* `History` – collection of tournaments over time
* `BoutResult`, `Performance`, etc.

#### Serialization Strategy

Each object type has:

* `_serialise_*` → object → dict
* `_deserialise_*` → dict → object

Example:

```python
_serialise_basho_state(state) -> {
    "banzuke": {...},
    "summary": {...}
}
```

#### Data Transformations

| Type           | Serialized Form |
| -------------- | --------------- |
| Enum           | String name     |
| Custom objects | Dictionary      |
| IDs (`RikId`)  | Integer         |
| Collections    | Lists / dicts   |

---

### 3. `NewSumoSerialiser`

An extended serializer that introduces a **new encoding for annotated data**.

#### Purpose

To improve efficiency and maintainability while remaining compatible with existing logic.

#### Key Change

The `Chii` object is serialized differently:

* **Old format**: full dictionary representation
* **New format**: compact integer ordinal

```python
# New approach
ordinal = chii.ordinal()
chii = Chii.from_ordinal(ordinal)
```

#### Benefits

* Reduced file size
* Faster serialization/deserialization
* Simpler representation of complex objects

#### Design Approach

* Reuses `SumoSerialiser` methods for unchanged components
* Overrides only the parts that differ (e.g. `Chii`, `RikChii`)

---

## Data Flow

### Saving Data

1. Domain object (e.g. `History`) is passed in
2. Converted into nested dictionaries
3. Special types normalized (enums, IDs, objects)
4. Serialized to JSON
5. Written into a compressed `.zip` file

### Loading Data

1. ZIP file is read
2. JSON is parsed
3. Dictionaries are converted back into domain objects
4. Full object graph is reconstructed

---

## Public API

### Standard Serialisation

```python
save_bashostate(bashostate, filename)
load_bashostate(filename)

save_history(history, filename)
load_history(filename)
```

---

### Annotated Serialisation (New Format)

```python
save_history_with_annotations(history, filename)
load_history_with_annotations(filename)
```

---

## File Format

* Output files are saved as:
  
  ```
  <filename>.zip
  ```

* Inside the ZIP:
  
  ```
  <filename>.json
  ```

* JSON is human-readable (indented)

---

## Design Principles

### 1. Separation of Concerns

* `BaseSerialiser`: infrastructure
* `SumoSerialiser`: domain logic
* `NewSumoSerialiser`: format evolution

---

### 2. Deterministic Serialization

All data is reduced to JSON-safe primitives:

* No object references
* No non-serializable types

---

### 3. Backward-Compatible Evolution

* New formats extend existing ones
* Shared logic is reused wherever possible

---

### 4. Explicit Transformations

Each type has clearly defined serialization/deserialization methods, avoiding implicit or magic behavior.

---

## Extending the System

To support new data types:

1. Add `_serialise_<type>` and `_deserialise_<type>` methods
2. Ensure all fields are JSON-compatible
3. Integrate into parent object serializers

To modify existing formats:

* Prefer extending via a new serializer (like `NewSumoSerialiser`)
* Avoid breaking existing serialized data

---

## Summary

This module provides a robust, extensible system for:

* Persisting complex sumo tournament data
* Maintaining compatibility across evolving formats
* Ensuring reliable, reversible transformations between objects and storage

It is designed to balance **clarity**, **performance**, and **long-term maintainability**.
