# Audit Workflow

## Purpose

The audit exists to discover what the repository actually builds, what outputs are still live, and what can be deleted or quarantined before writing a Makefile.

The workflow should produce reviewable inventory data first and decisions second.

## Phase 1: Package Inventory

Visit packages top down.

For each package, record:

```text
modules
entry points
internal import graph
package-external exports used by the package
package-external imports that use the package, if already known
dataflow edges
generated outputs
known consumers
open questions
```

Start small. A package can be real but trivial, like `src/misc`, or small but important, like `src/infra/tracker/scraper`.

## Phase 2: Import Graph

For the package under review:

- list every Python module as a node;
- record only intra-package import edges first;
- separately note important package-external exports used by the package;
- separately note package-external imports that use the package when a broader search has already found them;
- keep isolated nodes visible.

Produce or update:

```text
files/output/makefile/import_edges.csv
```

## Phase 3: Dataflow Graph

For each entry point, producer function or support module that reads/writes artifacts:

- record virtual inputs such as `History` when they are real dependencies;
- record explicit path templates;
- record URLs and manual/external inputs;
- record generated outputs;
- record copied outputs separately from produced outputs;
- record package-boundary inputs as coming from `external`;
- record package-boundary outputs as going to `external`;
- do not infer producer-consumer links from compatible-looking paths during the package-local pass.

Produce or update:

```text
files/output/makefile/dataflow_edges.csv
files/output/makefile/output_families.csv
```

At this phase, these are separate facts:

```text
module_a -- path/template.ext --> external
external -- path/*.ext --> module_b
```

Do not join them unless the code directly connects them inside the audited scope.

## Phase 4: Consumer Search

For each output family, search for code, tests, docs, build scripts, runtime code and deployment scripts that read or copy it.

Produce or update:

```text
files/output/makefile/output_consumers.csv
```

Consumers may be:

```text
module
command
test
browser runtime
deployment step
manual workflow
external process
```

## Phase 5: Initial Classification

Classify mechanically first:

```text
source capture
canonical data
producer output
publication output
runtime view
used
unused
unknown use
```

Do not decide human value yet.

Produce:

```text
files/output/makefile/initial_output_classification.csv
files/output/makefile/initial_module_classification.csv
```

## Phase 6: Human Leaf Review

A leaf output is a generated output with no known consumer.

The human decides whether each leaf is:

```text
unused legacy
unused non-legacy
research record
diagnostic
trash
unknown manual use
```

The test is not "could this someday be useful?" The test is "can we name why this should remain live?"

## Phase 7: Global Reconciliation

Before backtracking, run global reconciliation.

Global reconciliation compares package-boundary outputs and inputs across all audited packages.

It identifies:

```text
matched output/input pairs
unconsumed outputs
unsatisfied inputs
ambiguous matches
data-instance mismatches
parameter mismatches
```

Only after reconciliation should the audit decide whether an output is truly unused or an input is truly unsatisfied.

## Phase 8: Backtracking

After terminal legacy outputs are removed from the active graph, re-evaluate their producers and upstream inputs.

Example:

```text
A -> M -> B -> N -> C
```

If `C` is legacy, `N` may be legacy. If `N` has no other non-legacy role, remove it from the active graph and re-evaluate `B`. Continue until every remaining output has a reason to exist.

## Phase 9: Action Plan

Separate actions into:

```text
safe deletes
quarantine candidates
needs tests first
needs provenance first
needs human confirmation
module deletion candidates
entry-point deletion candidates
Makefile rule candidates
```

## Phase 10: Implementation

Apply changes in small steps.

Suggested order:

```text
1. delete obvious generated trash
2. quarantine legacy output folders
3. remove obsolete entry points
4. remove redundant modules
5. add provenance to retained outputs
6. promote stable producer outputs to contracts
7. encode repeatable steps in a Makefile
```

## Final Test

Every live generated output should be able to answer:

```text
What made me?
What did it use?
What data instance do I represent?
Who consumes me, or why am I kept as a leaf?
How do I get regenerated?
When am I stale?
```
