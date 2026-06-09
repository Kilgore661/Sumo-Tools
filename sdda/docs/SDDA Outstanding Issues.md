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
