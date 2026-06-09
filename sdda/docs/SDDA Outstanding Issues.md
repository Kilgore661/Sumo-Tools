# SDDA Outstanding Issues

This document is a working bin for issues that arise while discussing and implementing the SDDA design.

Issues recorded here may be:

```text
accepted limitations for the first implementation
known risks to revisit after initial reports exist
open questions not yet resolved by the requirements, specification, or design
```

## OI-001: Object method call resolution

There is reason to believe that the website build/deploy path may contain calls of the form:

```python
obj.method(...)
```

In many cases the type of `obj` may be statically determinable, but SDDA v1 will not attempt to resolve object method dispatch.

For v1, these calls should be recorded in `unresolved.csv` with enough evidence for human review:

```text
module
scope kind
scope name
line number
source expression
receiver expression
method name
reason: object_method_dispatch_not_resolved
```

This is an accepted limitation of v1, not a claim that such calls are irrelevant.

If unresolved object method calls appear in important parts of the `src.products.make_site2.__main__` analysis, this issue should be revisited.

## OI-002: Conservative call resolution in v1

SDDA v1 will not attempt a full Python call graph.

The Sumo-Tools Python website build/deploy path is not expected to use generated code, callback-heavy control flow, reflection-heavy dispatch, or functions passed around as data.

Therefore v1 will resolve only straightforward call forms such as:

```text
local_function(...)
imported_function(...)
module.function(...)
```

Other call forms should be reported in `unresolved.csv` rather than silently ignored or aggressively inferred.

This is a deliberate implementation boundary for v1 so that SDDA can produce useful evidence quickly without pretending to solve all Python call semantics.

## OI-003: SDDA test location and test data naming

SDDA tests should live alongside the SDDA code, under the top-level `sdda` project.

The preferred future shape is:

```text
sdda/
  tests/
    test_*.py
    testdata/
      ...
```

The term `testdata` is preferred over `fixtures` for SDDA because it is more explicit.

No SDDA testdata directory is required until artificial test inputs are actually needed. During early development, the main regression runs are against real repo modules:

```text
src.products.make_site2.__main__
src.infra.get_bios.__main__
```

Generated SDDA reports should normally remain under:

```text
files/output/sdda/
```

Checked-in snapshots should be rare and explicitly documented.

## OI-004: Deferred make_site2 test/fixture cleanup

There is existing make_site2-specific testing material in the repository, including tests placed under the repo-level `tests` directory and fixture-like material near `make_site2`.

This should not be fixed while implementing SDDA.

After SDDA is complete enough to replace the old `makefile` and `src/introspection` work, revisit make_site2 testing layout.

The likely cleanup is to make make_site2 tests and their test data local to the make_site2 product, or otherwise organise them under a clear product-specific test location.

Questions to resolve later include:

```text
which existing make_site2 fixtures/testdata are still useful regression inputs
whether any temporary fixtures can be deleted
whether test code and test data should be colocated under src/products/make_site2/tests/
whether any checked-in buggy-output snapshots should remain as documented regression evidence
```

## OI-005: Generated SDDA outputs are not committed by default

Generated SDDA outputs should not normally be committed to the repository.

They should be written under:

```text
files/output/sdda/
```

and treated as local generated output.

This keeps routine analysis output from getting in the way during normal Git use.

The accepted trade-off is that, by default, the repository will not preserve the exact SDDA output produced by a historical commit such as:

```text
foo.py at SHA 2348929
```

If a specific output snapshot is important enough to keep, it should be explicitly curated, documented, and checked in as an exception rather than as routine generated output.
