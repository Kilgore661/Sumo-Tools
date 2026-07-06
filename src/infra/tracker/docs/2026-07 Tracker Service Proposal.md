# Tracker Service Proposal

## Status

Draft proposal, 2026-07-06.

This document records a proposed direction for making the tracker a proper
service in contract before making it a Windows service in deployment.

The proposal follows the current document spine:

- `src/infra/tracker/docs/2026 03 24 The Tracker2a.md`
- `src/infra/docs/Live Store Operational Notes.md`
- `src/infra/docs/2026 03 30 The Sumo Data Store Manager.md`

## Context

The tracker is already service-like.

It is a continuously running program whose role is to maintain the canonical
sumo data store and publish usable representations of that store. In current
terms, it is the implementation of the Sumo Data Store Maintainer for
canonical `History`.

Operationally, however, the tracker is usually run from a foreground shell.
That is intentional. The implementation is still settling, diagnostics are most
useful when visible in the shell, and manual restart remains a practical part
of the operating model.

This proposal therefore separates two questions:

```text
service role
  The tracker owns data-store maintenance and live-store publication.

service deployment
  Whether the tracker is installed and supervised as an operating-system
  service.
```

The first question should be clarified now. The second can remain deferred.

## Current Contract

The tracker currently:

1. waits until new source data may exist;
2. attempts retrieval of required source artifacts;
3. retries later when retrieval fails;
4. rebuilds canonical `History` when source data changes;
5. writes the canonical History zip;
6. publishes `History` into the live store.

The live store is currently exposed through:

```text
files/output/store_name.txt
```

Consumers read this file, obtain a shared-memory segment name, and connect to
that named segment.

The current implementation uses a name shaped like:

```text
history{VERSION}
```

For example:

```text
history4
```

That name is a protocol/version placeholder. It is not a data generation.

## Problem

The tracker can update the canonical History zip and refresh the live store
while another process has already loaded a `History` snapshot.

For a short-running producer, this creates a bounded stale-snapshot risk:

```text
producer starts
producer loads History generation G
tracker publishes generation G+1
producer writes output based on G
```

For a long-running consumer, the problem is larger. A process may behave as if
it is using "the live store" while actually holding a snapshot loaded from one
past generation.

The current name-file mechanism gives us the right hook, but not yet the right
identity. Because the published name does not change when data changes, a
consumer cannot cheaply test whether its loaded snapshot is stale.

## Requirement

The tracker service contract should distinguish:

```text
published generation
  The latest data-store generation advertised by the tracker.

loaded generation
  The data-store generation from which a consumer obtained its History
  snapshot.

fresh snapshot
  loaded generation == published generation.

stale snapshot
  loaded generation != published generation.
```

Consumers that retain `History` across time must be able to test freshness at
each meaningful point of use.

## Proposed Service Contract

The tracker is the single writer for the live-store publication pointer.

After each successful publication of canonical `History`, the tracker publishes
a new generation identity and updates the pointer atomically enough for local
consumer use.

The live-store name should identify a data generation, not merely an API
version.

Example shape:

```text
history4-20260706T100102
```

or:

```text
history4-<history-zip-fingerprint>
```

The exact generation key is a design detail, but it must change whenever the
published History generation changes.

The existing `store_name.txt` then becomes:

```text
latest live-store generation pointer
```

not merely:

```text
shared-memory protocol version selector
```

## Consumer Contract

Live-store consumers fall into two broad classes.

Snapshot producers:

- load a `History` generation;
- produce an output;
- before writing or declaring success, confirm that the published generation is
  still the loaded generation;
- if it changed, stop with a clear stale-History failure.

Long-running consumers:

- load a `History` generation;
- retain both the `History` object and its generation identity;
- before each meaningful use, compare loaded generation with published
  generation;
- either reload, reconnect, or terminate according to their own explicit
  contract.

This test must be visible in code. It should not silently invent a default or
pretend stale data is current.

## Proposed API Direction

The current API:

```python
history = get_history()
```

can remain for simple one-shot consumers.

A new API should expose generation identity explicitly:

```python
session = get_history_session()
history = session.history
generation = session.generation
```

The session should support direct freshness checks:

```python
session.assert_fresh()
```

or:

```python
if session.is_stale():
    ...
```

The important property is that freshness is a contract decision at the point of
use, not hidden inside ordinary `History` access.

## Tracker Service Role

The tracker service owns:

- retrieval timing and retry policy;
- canonical History rebuild;
- canonical History zip publication;
- live-store generation creation;
- live-store generation pointer publication;
- service diagnostics for current state and generation.

It does not own:

- website generation;
- report generation;
- experimental analysis outputs;
- consumer reload policy.

Those consumers may depend on the service, but they do not define it.

## Foreground Operation Remains Valid

This proposal does not require immediately installing a Windows service.

Current foreground operation remains the right practical mode while the tracker
is still being hardened:

```powershell
py -m src.infra.tracker.tracker
```

Running in a shell keeps diagnostics visible, makes manual restart simple, and
matches the current development reality.

The word "service" in this proposal names the role and contract. Actual Windows
Service deployment is a later operational hardening step.

## Windows Service Deployment Is Deferred

A future Windows-service wrapper should only be considered after the service
contract is stable.

That later work should answer:

- how stdout/stderr and structured logs are retained;
- how fatal alerts are surfaced;
- how the service is started, stopped and restarted;
- how owner-process diagnostics are reported;
- how stale or orphaned shared-memory generations are cleaned up;
- how multiple repository checkouts are isolated or deliberately forbidden;
- how startup validates the canonical zip and publication pointer.

Until those answers are explicit, a foreground shell process is preferable.

## Relationship To Existing Docs

This proposal is not a replacement for the tracker specification.

It extends the existing model:

- `Tracker2a` already defines the tracker as the continuously running SDSM
  implementation for canonical `History`.
- `Live Store Operational Notes` already records that the live store has become
  server-like without service-grade safety properties.
- This proposal supplies the missing generation/freshness contract that lets
  service-like operation become explicit.

## Initial Work Plan

1. Introduce live-store generation identity distinct from `VERSION`.
2. Change successful tracker publication to create or select a new generation
   name when the published History changes.
3. Keep `store_name.txt` as the latest-generation pointer.
4. Add a `HistorySession` API carrying `history` and `generation`.
5. Add freshness tests: `current_generation()`, `is_stale()`,
   `assert_fresh()`.
6. Update snapshot producers that write public artifacts to assert freshness
   before publication.
7. Identify long-running consumers and give each an explicit stale-generation
   policy: reload, reconnect, or terminate.
8. Add diagnostics that report tracker state, current generation and owner
   process.
9. Only after the above is stable, revisit actual Windows service deployment.

## Non-Requirements

This proposal does not require:

- a database;
- a network server;
- a query API;
- automatic consumer reload by default;
- immediate Windows Service installation;
- promoting downstream products into the maintained store.

## Open Questions

- Should the generation key be timestamp-based, content-fingerprint-based, or
  both?
- Should the old generation remain available until consumers disconnect, or is
  replacing the live shared-memory segment sufficient?
- Should generation metadata include the canonical zip path, zip hash,
  repository root and owner process id?
- Should multiple checkouts on one machine be explicitly unsupported, or should
  the generation name include repository/output-root identity?
- Which producers must assert freshness before writing output?
- Which long-running consumers exist today beyond the tracker itself?
