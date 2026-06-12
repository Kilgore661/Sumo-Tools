# History Data Entity

## Status

This document records the special role of `_history_` in SDDA.

It is a design note, not yet a finished specification.

## Purpose

`_history_` is an abstract data entity used to represent the canonical parsed sumo `History`.

It is not a literal source-distribution file. It is a domain data family that behaves like a file-like dependency in the SDDA graph: programs can consume it, programs can produce it, and it can be expanded to the input entities needed to regenerate it.

## Why `_history_` Is Needed

Many Sumo-Tools programs access History through:

```text
src.infra.live_store.api.get_history()
```

The live store is a runtime access path, not a distribution input.

Without a first-class `_history_` entity, each program using `get_history()` would repeatedly drag SDDA into implementation details such as:

```text
files/output/store_name.txt
shared-memory segment names
History zip files
tracker publication mechanics
```

Those details are not the dependency the program semantically needs. The program needs History.

## Production Closure

The expected current production closure is:

```text
internet
  -> downloaded SumoDB HTML caches
  -> _history_
  -> History zip / live-store access paths
```

The downloaded SumoDB HTML families are self-maintained cache/generated outputs. Under the cache-maintenance rule, they are not fundamental source inputs by default.

Therefore, for a source distribution with internet access, the expected final input closure for `_history_` is:

```text
{ internet }
```

## Local Versus Final Views

At local program-analysis time, SDDA may record:

```text
program consumes _history_
```

At final distribution-closure time, SDDA should expand `_history_` through its production closure:

```text
_history_ -> internet
```

Therefore `_history_` should not appear in the final distro-input list.

For example, a program that uses History and also downloads additional internet data may locally consume both:

```text
_history_
internet
```

but the final source-distribution input summary should collapse this to:

```text
internet
```

## Benefits

The `_history_` abstraction makes SDDA simpler and more accurate.

It:

```text
names the domain dependency directly
avoids treating live-store runtime plumbing as source data
prevents repeated manual expansion of get_history()
lets many programs share one producer-closure rule
supports both live-store and History-zip access paths
keeps final distro input summaries focused on true required entities
```

## Costs And Risks

`_history_` requires special handling.

That has costs:

```text
SDDA needs a domain rule for get_history()
the _history_ production closure must be kept correct
programs that only expose live-store access may still have CLI boundary bugs
the final collapse to internet depends on the assumption that the raw SumoDB caches are reproducible generated outputs
```

The abstraction must therefore be evidence-backed, not magical.

The known producer path should remain visible in review material:

```text
internet
  -> files/output/current standings/{year} {month}.html
  -> files/output/HTML results/{year} {month}/{day}.html
  -> src.infra.parser.parser2
  -> _history_
```

## Implementation Consequences

SDDA should recognize:

```text
src.infra.live_store.api.get_history()
```

as consumption of:

```text
_history_
```

History zip reads and writes should be treated as representations of `_history_`, not as fundamental source inputs by default.

Modules that consume `_history_` only through the live store may still need explicit file-boundary options, such as:

```text
--history-zip
```

That is a command-interface concern. It does not change the distribution dependency closure.

## Open Review Point

The current expectation is:

```text
HistoryFiles = { internet }
```

This should remain an explicit review point until SDDA can automatically demonstrate the producer closure and cache classifications for the raw SumoDB HTML families.
