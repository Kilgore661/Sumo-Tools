# Review of src.infra.persistence SDDA Dry Run

## Status

This document records the SDDA dry-run interpretation of `src.infra.persistence`.

The result is:

```text
N/A
```

There is no real entrypoint in this package.

The package is classified by `sdda.entrypoints` as library code:

```text
Library modules: 4
Programs: 0
Standalone programs: 0
```

That classification is correct for SDDA purposes. This review exists only to record why the package does not receive an entrypoint-style input/output dry run.

## Package Investigated

```text
src.infra.persistence
```

The package provides persistence helpers for converting sumo domain objects between in-memory Python objects and zipped JSON files.

It does not provide a command-line tool, and it does not name any fixed source-data file that must be present in a distribution.

## Package Shape

The package contains these conceptual layers:

```text
base_serialiser.py
  generic zip/json and enum helper infrastructure

serialiser.py
  legacy/core sumo object serialisation
  public helpers:
    save_bashostate(...)
    load_bashostate(...)
    save_history(...)
    load_history(...)

new_sumo_serialiser.py
  newer annotated History serialisation
  public helpers:
    save_history_with_annotations(...)
    load_history_with_annotations(...)

annotated_serialiser.py
  closely related annotated History serialisation variant
  public helpers:
    save_history_with_annotations(...)
    load_history_with_annotations(...)
```

`base_serialiser.py` is shared infrastructure.

`serialiser.py`, `new_sumo_serialiser.py`, and `annotated_serialiser.py` expose public persistence services. They are library services, not entrypoints.

## Expected SDDA Summary

For `src.infra.persistence` considered by itself:

```text
Module or package investigated:
  src.infra.persistence

Entrypoint:
  N/A

Input files:
  none

Output files:
  none
```

The reason is that persistence functions receive file names from their callers.

The package defines how a file boundary works, but it does not decide which concrete file family belongs in the source distribution.

## Transfer Semantics

For SDDA, this package contributes transfer rules.

Generic zip/json persistence:

```text
BaseSerialiser.save_to_zip(data, filename)
  data in memory -> {filename}.zip

BaseSerialiser.load_from_zip(filename)
  {filename}.zip -> data in memory
```

History persistence:

```text
save_history(history, filename)
  _history_ -> {filename}.zip

load_history(filename)
  {filename}.zip -> _history_

save_history_with_annotations(history, filename)
  _history_ -> {filename}.zip

load_history_with_annotations(filename)
  {filename}.zip -> _history_
```

These mappings are caller-parameterised. The caller supplies `filename`, so the caller determines the concrete file family.

For example, `src.infra.parser.parser2` supplies the History zip path. `src.infra.persistence` only supplies the memory-to-zip and zip-to-memory machinery.

## Distribution Interpretation

The answer to:

```text
What files need to be included in the distribution because of src.infra.persistence?
```

is:

```text
nothing
```

This does not mean persistence is unimportant. It is an important file-boundary adapter.

It means the distribution impact must be attributed to the entrypoint or library caller that chooses a concrete filename.

## SDDA Rule Captured By This Review

Persistence libraries define file-boundary transfer semantics.

They do not themselves contribute distribution input files unless they contain fixed paths, embedded data, or other non-code resources that are required independently of their callers.

For this package, no such fixed source-data dependency was found.

## Review Items

`annotated_serialiser.py` and `new_sumo_serialiser.py` overlap heavily and expose similarly named public helpers.

That may be an intentional format-evolution story, or it may be historical duplication.

This is a code-maintenance review item, but it does not change the SDDA distribution conclusion.
