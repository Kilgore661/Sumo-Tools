# Live Store Operational Notes

## Status

Operational note for the current `src.infra.live_store` implementation.

This is not a redesign. It records the actual operating assumptions and risks
that matter when the project is run from more than one checkout or by someone
other than the original single developer.

## Original Purpose

The live store was originally a local convenience for one developer.

Its job was to avoid repeatedly loading a large canonical `History` zip during
interactive work. A single process would load one canonical History into shared
memory, and downstream code could connect to that in-memory snapshot quickly.

That is the design centre:

```text
one developer
one machine
one intended canonical History
one live store instance
many local consumers
```

## What It Has Become

The live store now behaves like a small server-like entity because multiple
tools and products call `get_history()` and expect a long-lived process to
publish the current `History`.

That server-like role was not the original intent. The current implementation
does not provide the safety properties normally expected from a multi-instance
service, cache manager or data-store server.

## Current Implementation Facts

The shared-memory segment name is global to the machine for a given version:

```text
history{VERSION}
```

For example, with `VERSION = 4`, every checkout using the same code version
targets:

```text
history4
```

That name is not scoped by repository root, working directory, output directory
or selected History zip.

The published-name file is repository-relative:

```text
files/output/store_name.txt
```

but it only contains the shared-memory segment name. It does not make the live
store itself repository-local.

The resulting shape is:

```text
repo-local store_name.txt -> machine-global shared memory segment
```

## Consequences

Multiple checkouts on the same machine can point at the same live store.

If a live store named `history4` already exists, another tracker process using
the same `VERSION` will see that shared-memory segment and publish its name in
that checkout's local `files/output/store_name.txt`. It will not necessarily
load that checkout's own canonical History zip.

If a process publishes a new History to the same name, it may replace the
machine-global segment used by consumers in other checkouts.

Consumers do not know which checkout created the segment. They only read a
name and connect to that machine-global shared-memory object.

The practical rule is therefore:

```text
Treat the current live store as a singleton per machine and VERSION.
```

## Intended Use

For the original single-user workflow, this remains acceptable:

1. Build or update the canonical History zip.
2. Start one tracker/live-store process.
3. Run downstream tools that consume `get_history()`.
4. Stop the process when finished.

The live store is a fast local convenience, not an authority boundary.

## Non-Goals of the Current Code

The current implementation does not attempt to support:

- multiple live stores with different selected History data;
- multiple repository checkouts publishing independently;
- multi-user operation;
- durable service discovery;
- instance ownership diagnostics;
- protection against one process replacing another process's store;
- guarantees about which checkout a consumer is connected to.

Anyone running several stores at once with different data should expect
confusing results. Last-publisher and surviving-owner behaviour are accidental
implementation facts, not a safe operating contract.

## Distribution Note

A source distribution or clean-room bootstrap guide should mention this
explicitly.

For simple bootstrap builds, prefer commands that name the History zip directly
where supported, for example:

```powershell
py -m src.products.make_site2 --build-only --history-zip ".\files\output\Historys\1958_01 to 2026_11.zip"
```

Use the live store when testing or running tools whose current interface only
supports `get_history()`, and keep in mind that it is machine-global for the
configured `VERSION`.

## Future Redesign Pressure

If the live store remains server-like, it should eventually grow explicit
instance identity and lifecycle semantics, such as:

- a caller-selected instance name;
- repository/output-root scoping;
- recorded source zip or History identity;
- owner-process diagnostics;
- safe replacement rules;
- clear startup and shutdown commands;
- consumer diagnostics showing which store was connected.

The current tracker-service proposal records the next intended contract step:
the published live-store name should identify a data generation, and consumers
that retain `History` across time should be able to test whether their loaded
generation is stale. See:

```text
src/infra/tracker/docs/2026-07 Tracker Service Proposal.md
```

Until then, the current implementation should be understood as a single-user
local accelerator that has acquired broader operational importance without yet
being redesigned for it.
