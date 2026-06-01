# Dependency Graph Model

## Status

Draft.

This document defines the graph vocabulary for the generated-output audit.

## Purpose

The project shall derive a dependency graph covering generated outputs and the modules that produce or consume them.

The graph shall answer:

```text
What generated files exist?
What produced them?
What inputs did the producer use?
What consumes them?
Are they still non-legacy?
If not, what can be deleted?
```

The exercise is deliberately broader than `make_site2`. The public website is one important consumer, but it is not special. Any generated file may later become important depending on the current line of work.

## Core nodes

The dependency graph contains three main node kinds:

```text
Source / Input
Producer
Generated Output
```

Edges are directional:

```text
Input -> Producer
Producer -> Generated Output
Generated Output -> Consumer
```

A consumer may also be a producer.

Example:

```text
raw HTML
  -> parser
      -> History zip
          -> analysis producer
              -> CSV bundle
                  -> make_site2
                      -> static site files
                          -> browser runtime view
```

## Generated output

A generated output is a file or file family written by project code.

Generated outputs include CSV, JSON, HTML, ZIP, text reports, diagnostics, static browser files, copied site bundles, caches, charts, and publication outputs.

## Producer

A producer is a module, script, command, or function that writes a generated output.

A producer may be an executable entry point, a helper called by an entry point, or a build step inside a larger product.

## Consumer

A consumer is a module, script, command, browser runtime, test, deployment step, manual workflow, or external process that uses a generated output as an input.

## Used

A generated output is **used** if it is an input to something else.

This is a strict graph term. It does not mean useful, current, public, important, or worth keeping. It only means that another process consumes the file.

## Unused

A generated output is **unused** if no known process consumes it.

Unused outputs divide into:

```text
unused legacy
unused non-legacy
```

## Leaf output

A leaf output is an unused generated output.

A leaf output may be:

```text
unused legacy
unused non-legacy
```

Unused legacy leaf outputs should normally be deleted.

Unused non-legacy leaf outputs may be retained, but should be explicitly classified and documented.

## Legacy-only used output

A generated output is **legacy-only used** if it is used, but only by legacy consumers.

Such an output is not unused in the strict graph sense, but it becomes a backtracking candidate. If all of its consumers are removed from the active graph, the output must be reclassified.

## Recursive pruning rule

The graph shall be pruned recursively.

If a module produces only legacy outputs, then that producer role is legacy. If the module is not used by non-legacy code, it is redundant and may be removed from the active graph.

When a producer is removed from the active graph, its inputs must be re-evaluated.

Example:

```text
A -> M -> B -> N -> C
```

If `C` is legacy, then `N` may be legacy. If `N` has no other non-legacy output or support role, remove `N` from the active graph and re-evaluate `B`.

If `B` is then used only by removed legacy consumers, re-evaluate `M`.

If `M` has no other non-legacy output or support role, remove `M` and re-evaluate `A`.

This continues until all remaining generated outputs are justified by one of:

```text
canonical status
non-legacy consumer
unused non-legacy leaf value
declared future use
selected research/reference value
```

## Important distinctions

### Used is not the same as non-legacy

A file may be used only by legacy code. It is still used in the graph, but it may not be worth keeping.

### Unused is not the same as legacy

A leaf output may be unused but still non-legacy. For example, a standalone chart or calibration report may be a deliberately useful final result.

### A legacy producer is not automatically a redundant module

A module may produce only legacy outputs but still contain logic imported by non-legacy code. In that case it is a support module, not a redundant module.

### The website is not special

`make_site2` is one consumer of generated outputs. The same provenance and dependency rules apply to every other consumer.
