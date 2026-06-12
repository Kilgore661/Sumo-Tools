# Dataflow Review

## Status

This document records the current requirements-level review of `sdda.dataflow`.

The review treats the existing code as evidence, not authority. The question is whether the package delivers something that fits the top-level SDDA requirements, while recognizing that the package was moved out of the original top-level `sdda` location during a hasty hand-off.

## Assessment

In principle, `sdda.dataflow` is the right per-program data dependency analyser for SDDA.

Given a selected Python root module, it should statically analyse the code reachable from that root and produce evidence about the non-code data families that the program may consume, observe, produce, or depend on.

Its core contract is:

```text
selected program/root module
  -> reachable code evidence
  -> file/data use evidence
  -> normalized data-family evidence
  -> producer/consumer hints
  -> classifications and review items
```

That is exactly the evidence needed to connect programs into a repository-level data dependency graph.

## Evidence Model

`sdda.dataflow` is not merely a path grepper.

It builds several layers of static evidence:

```text
module index
reachable import graph
lexical/runtime scopes
type facts
value facts
field facts
call edges
execution call slice
call argument bindings
parameter provenance
file-use evidence
producer-output evidence
file-family normalization
file-family classification
unresolved evidence
```

This matters because data dependencies are often indirect. A program may pass paths through parameters, dataclass fields, producer result objects, local aliases, or helper functions. `sdda.dataflow` is trying to recover enough of that structure to say something useful.

## Fit For SDDA

For each analysed program, `sdda.dataflow` can produce evidence about:

```text
which project modules are reachable
which scopes are relevant
which calls form part of the execution slice
which files, directories, globs, URLs, and environment settings are touched
which data families are read, written, observed, downloaded, created, copied, or checked
which outputs appear to be produced and then consumed
which file families look like required inputs
which look like generated outputs or intermediates
which remain uncertain and need review
```

This fits the intended SDDA pipeline:

```text
sdda.entrypoints
  identify candidate programs

sdda.dataflow
  analyse one candidate program at a time

future SDDA integration layer
  combine per-program dataflow outputs into a repository-level program/data graph
```

The future integration layer can then reason over relationships such as:

```text
program A writes data family X
program B reads data family X
therefore B may depend on A's output
```

That supports both selected-deliverable questions and whole-repository questions:

```text
what a selected deliverable depends on
what other programs and data exist outside that selected chain
```

## Caveats

`sdda.dataflow` still contains historical residue from its original `make_site2`-first implementation.

The move into `sdda.dataflow` separated the package physically, but not fully conceptually. Some `make_site2` product-policy assumptions still live inside the dataflow classification and reporting path.

Known examples include:

```text
DEPLOY_MODULE = "src.products.make_site2.deploy"
hard-coded exception for src.products.make_site2.__main__:main
report prose saying current make_site2 execution slice
docs treating make_site2 as the primary or defining scope
source_distribution_* outputs bundled into the core dataflow report set
```

These are extraction debt. They do not change the top-level SDDA requirements.

The correct direction is to separate:

```text
neutral per-program dataflow evidence
make_site2/source-distribution interpretation policy
```

Some of the current hard-coded `make_site2` names should become root-module-derived or explicitly supplied policy values. Genuinely `make_site2`-specific reports should remain labelled as product-specific views rather than generic dataflow outputs.

## Proper Limitation

`sdda.dataflow` should not be expected to prove exact runtime behavior.

Its proper output is conservative static evidence:

```text
may read
may write
may observe
may produce
may require review
unresolved
```

That is enough for SDDA. The package's job is to build an evidence-backed map, not to pretend to execute or fully understand arbitrary Python.

## Conclusion

`sdda.dataflow` should be kept.

It should not be treated as a throwaway prototype.

The underlying analyser purpose fits SDDA's requirements. The remaining work is to remove or isolate `make_site2`-specific policy assumptions so that the package can cleanly analyse any selected Sumo-Tools-style program.

The existing code does not force a change to the top-level SDDA requirements.
