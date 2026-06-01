# Generated Output Dependency Graph Proposal

## Status

Draft proposal.

This document defines a project-wide exercise for deriving the generated-output dependency graph of Sumo-Tools.

The immediate motivation is that the repository now contains many generated files, producer scripts, standalone browser artifacts, caches, reports, diagnostics, and publication outputs. Some are current. Some are useful but unused. Some are legacy. Some are only still present because they were important when a module was first written.

The goal is not to preserve everything. The goal is to understand what produces what, what consumes what, and which generated outputs and modules still belong in the active project.

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

The exercise is deliberately broader than `make_site2`. The public website is one important consumer, but it is not special. Any generated file may later become important depending on the current line of work. Therefore, generated files need to be understood in terms of producers, consumers, data context, and current project value.

## Core Terms

### Generated output

A file or file family written by project code.

Generated outputs include CSV, JSON, HTML, ZIP, text reports, diagnostics, static browser files, copied site bundles, caches, charts, and publication outputs.

### Producer

A module, script, command, or function that writes a generated output.

A producer may be an executable entry point, a helper called by an entry point, or a build step inside a larger product.

### Consumer

A module, script, command, browser runtime, test, deployment step, manual workflow, or external process that uses a generated output as an input.

### Used

A generated output is **used** if it is an input to something else.

This is a strict graph term. It does not mean useful, current, public, important, or worth keeping. It only means that another process consumes the file.

### Unused

A generated output is **unused** if no known process consumes it.

Unused outputs divide into:

```text
unused legacy
unused non-legacy
```

### Legacy

A generated output, producer, or consumer is **legacy** if it is no longer part of any current or intended line of work.

Legacy material may have historical value, but it should not remain in the live generated-output graph merely because it exists.

### Non-legacy

A generated output, producer, or consumer is **non-legacy** if it is current, intentionally retained, plausibly needed for a named future use, or valuable as a deliberate research/reference artifact.

"Potentially useful someday" is not enough. The future use should be nameable.

### Leaf output

A **leaf output** is an unused generated output.

A leaf output may be:

```text
unused legacy
unused non-legacy
```

Unused legacy leaf outputs should normally be deleted.

Unused non-legacy leaf outputs may be retained, but should be explicitly classified and documented.

### Legacy-only used output

A generated output is **legacy-only used** if it is used, but only by legacy consumers.

Such an output is not unused in the strict graph sense, but it becomes a backtracking candidate. If all of its consumers are removed from the active graph, the output must be reclassified.

### Active producer

A producer that produces at least one non-legacy output.

### Legacy producer

A producer whose generated outputs are all legacy.

This does not automatically mean the module can be deleted. The producer may still contain code used by non-legacy modules.

### Support module

A module that is used by non-legacy code, regardless of whether its own generated outputs are legacy or nonexistent.

A support module may contain important parser, model, transformation, rendering, or reporting logic.

### Redundant module

A module that produces no non-legacy output and supports no non-legacy code.

A redundant module is a deletion candidate.

## Output Layers

Generated outputs should also be classified by layer.

### 1. Source Capture

Raw or near-raw material captured from the outside world or manually supplied as source material.

Examples:

```text
downloaded HTML
raw source snapshots
rikishi bio HTML
manual source files used as source data
```

### 2. Canonical Data

Coherent internal project data.

Examples:

```text
History zip
LiveStore History-equivalent data
canonical parsed data instances
```

### 3. Producer Output

Analysis-specific or tool-specific output produced from canonical data or other producer outputs.

Subtypes include:

```text
analysis output
site-facing input
process cache
diagnostic output
research output
standalone browser app
```

### 4. Publication Output

A generated static publication file tree.

Examples:

```text
make_site2 output tree
deployable static site files
copied route data
runtime files included in a build
```

### 5. Runtime View

A browser-realised view created from static files and URL/filter/runtime state.

Runtime views are not normally files. They are included in the graph only where a browser runtime consumes generated files and creates visible user state.

## Graph Model

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

For example:

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

## Recursive Pruning Rule

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

## Important Distinctions

### Used is not the same as non-legacy

A file may be used only by legacy code. It is still used in the graph, but it may not be worth keeping.

### Unused is not the same as legacy

A leaf output may be unused but still non-legacy. For example, a standalone chart or calibration report may be a deliberately useful final result.

### A legacy producer is not automatically a redundant module

A module may produce only legacy outputs but still contain logic imported by non-legacy code. In that case it is a support module, not a redundant module.

### The website is not special

`make_site2` is one consumer of generated outputs. The same provenance and dependency rules apply to every other consumer.

## Audit Products

The exercise should produce at least these audit artifacts:

```text
1. Entry point inventory
2. Generated output inventory
3. Producer-output-consumer graph
4. Output classification table
5. Module classification table
6. Deletion/quarantine proposal
7. Human decision list
```

The inventory should be kept in a form that can be reviewed and updated.

A spreadsheet or CSV may be useful for the inventory. A Markdown document may be better for decisions and rationale.

## Output Review Fields

Each generated output family should be reviewed with the following fields.

```text
Output family:
Example path(s):
Producer entry point:
Producer module:
Generated by command:
Layer:
Output subtype:
Input files / input data:
Parameters / build context:
Data instance represented:
Used?:
Known consumers:
Consumer status:
  non-legacy / legacy / unknown / manual / external
Leaf output?:
If leaf, legacy or non-legacy?:
Provenance present?:
Freshness rule:
Can be regenerated?:
Regeneration command:
Risk if stale or wrong:
Current proposed classification:
Proposed action:
Human decision needed:
Notes:
```

## Module Review Fields

Each producer or support module should be reviewed with the following fields.

```text
Module:
Entry points:
Produces generated outputs?:
Generated outputs:
Output statuses:
Imported by:
Used by non-legacy code?:
Contains reusable logic?:
Tests:
Docs:
Replacement / successor:
Module classification:
  active producer / legacy producer / support module / redundant module / unknown
Proposed action:
Human decision needed:
Notes:
```

## Output Classification

Use these classifications for generated outputs.

```text
canonical
used by non-legacy consumer
used only by legacy consumer
unused non-legacy
unused legacy
research record
diagnostic
unknown manual use
trash
```

### canonical

Foundational project data that other tools are allowed to rely on.

### used by non-legacy consumer

An input to at least one current or intentionally retained process.

### used only by legacy consumer

An input, but only to legacy consumers. This output should be re-evaluated during pruning.

### unused non-legacy

A leaf output that is not consumed but is still worth retaining.

Examples may include selected charts, research summaries, manually inspected reports, or future-input candidates with a named purpose.

### unused legacy

A leaf output that is no longer useful.

### research record

A selected generated output retained as evidence for a research conclusion or modelling decision.

This should be deliberate. Not every old experiment run is a research record.

### diagnostic

An output used to inspect correctness, calibration, warnings, weirdness, or build health.

Diagnostics attached to active processes may be retained. Diagnostics from legacy processes should usually be deleted or archived.

### unknown manual use

No code consumer is known, but human/manual use is plausible. These require human review.

### trash

Accidental, duplicate, stale, debug, broken, or meaningless generated material.

## Module Classification

Use these classifications for modules.

```text
active producer
legacy producer
support module
research module
redundant module
unknown
```

### active producer

Produces at least one non-legacy generated output.

### legacy producer

Produces generated outputs, but all of them are legacy.

### support module

Used by non-legacy code, regardless of whether it produces current outputs itself.

### research module

Retained because it encodes an active or selected research method, even if its current generated outputs are not part of the active product pipeline.

### redundant module

Produces no non-legacy output and supports no non-legacy code.

### unknown

Requires further inspection.

## Actions

Use these action labels.

```text
KEEP
KEEP_AND_DOCUMENT
ADD_PROVENANCE
PROMOTE_TO_CONTRACT
QUARANTINE
DELETE_OUTPUT
DELETE_PRODUCER
DELETE_ENTRY_POINT_ONLY
ASK_HUMAN
```

### KEEP

Keep as-is for now.

### KEEP_AND_DOCUMENT

Keep, but add missing documentation.

### ADD_PROVENANCE

Keep, but require metadata sufficient to identify producer, inputs, parameters, data instance, and generation time.

### PROMOTE_TO_CONTRACT

Turn an informal generated output into a deliberate producer-consumer contract.

### QUARANTINE

Move or mark as historical/legacy so it cannot be mistaken for live pipeline material.

### DELETE_OUTPUT

Delete generated file or file family.

### DELETE_PRODUCER

Delete the module or producer after confirming it supports no non-legacy code.

### DELETE_ENTRY_POINT_ONLY

Remove or disable the output-producing entry point while keeping reusable support code.

### ASK_HUMAN

The LLM cannot decide because the value depends on human intent.

## LLM Checklist

The LLM should fill mechanical and evidence-based fields.

For each entry point, the LLM should identify:

```text
- command or function entry point
- module path
- files read
- files written
- directories written
- network access
- use of LiveStore
- use of History zip
- use of existing files/output artifacts
- generated output families
- obvious downstream consumers from code search
- make_site2 consumption, if any
- tests or docs that mention the output
- apparent metadata/provenance
- apparent regeneration command
- apparent stale-data risk
```

For each output, the LLM should classify as far as evidence allows:

```text
- generated or source-controlled
- source capture / canonical data / producer output / publication output / runtime view
- used or unused by known code
- known consumers
- whether consumers appear legacy or non-legacy
- whether output has provenance
- whether it is copied blindly by another process
- whether it is a candidate leaf output
```

The LLM should not decide human-intent questions such as:

```text
- whether an unused chart is still interesting
- whether a research result is worth retaining
- whether a future use is plausible enough
- whether a manual workflow still matters
```

When uncertain, the LLM should mark:

```text
ASK_HUMAN
```

The LLM should be conservative about deletion recommendations where imports or consumers have not been fully searched.

## Human Checklist

The human should decide intent and value.

For each unused output, decide:

```text
- legacy or non-legacy?
- if non-legacy, why?
- is the future use named and plausible?
- is it a useful final result?
- is it a selected research record?
- should it remain in files/output?
- should it be regenerated on demand instead of stored?
```

For each legacy-only used output, decide:

```text
- are its consumers really legacy?
- does the output have another non-code use?
- can the downstream legacy chain be deleted?
```

For each producer module, decide:

```text
- active producer, support module, research module, or redundant module?
- should only the generated outputs be deleted?
- should the entry point be removed but support code retained?
- should the whole module be deleted?
- is a replacement module already present?
```

For each retained output, decide:

```text
- what contract justifies keeping it?
- what provenance should it carry?
- what command regenerates it?
- when is it stale?
- who is allowed to consume it?
```

## Human Decision Prompts

Useful prompts for human review:

```text
Would I deliberately regenerate this today?

Would I deliberately open this today?

Can I name a future task that needs this?

Is this output evidence for a decision recorded in docs?

Is this merely a thing I made while exploring?

If this disappeared, would I know how to recreate it?

If this disappeared, would anything non-legacy break?

If this stayed, could it mislead me later?
```

## Deletion Policy

Generated files do not earn a permanent place merely by existing.

A generated output should remain live only if it is:

```text
canonical,
used by a non-legacy consumer,
an unused non-legacy leaf,
a declared future input,
a selected research record,
or an active diagnostic.
```

A generated output should be deleted or quarantined if it is:

```text
unused legacy,
used only by legacy consumers,
unproven as current but easy to regenerate,
a duplicate,
a stale debug artifact,
or a generated artifact from a redundant module.
```

A module should be deleted only if it is a redundant module:

```text
no non-legacy outputs,
no non-legacy imports,
no retained research/model value,
and no active tests/docs depending on it.
```

Where a module contains reusable logic but its output-producing entry point is legacy, prefer:

```text
DELETE_ENTRY_POINT_ONLY
```

or refactor the reusable logic into a support module.

## Proposed Workflow

### Phase 1: Inventory

Find entry points and generated outputs.

Produce:

```text
entry_points.csv
output_families.csv
```

### Phase 2: Consumer Search

For each output family, search for code, docs, tests, and build scripts that read or copy it.

Produce:

```text
output_consumers.csv
```

### Phase 3: Initial Classification

Classify outputs mechanically:

```text
used
unused
unknown-use
source capture
canonical
producer output
publication output
runtime view
```

Produce:

```text
initial_output_classification.csv
```

### Phase 4: Human Leaf Review

Human reviews unused outputs and unknown manual-use outputs.

Decide:

```text
unused legacy
unused non-legacy
research record
trash
```

### Phase 5: Backtracking

Remove legacy terminal outputs from the active graph.

Re-evaluate producers and their inputs.

Repeat until classifications stabilize.

### Phase 6: Action Plan

Produce a deletion/quarantine/refactor plan.

Separate actions into:

```text
safe deletes
needs tests first
needs human confirmation
needs provenance before promotion
module deletion candidates
entry-point deletion candidates
```

### Phase 7: Implementation

Apply changes in small commits.

Suggested order:

```text
1. delete obvious generated trash
2. quarantine legacy output folders
3. remove obsolete entry points
4. remove redundant modules
5. add provenance to retained outputs
6. add contracts for promoted producer outputs
```

## Final Test

After pruning, every remaining generated output should be able to answer:

```text
What made me?
What did it use?
What data instance do I represent?
Who consumes me, or why am I kept as a leaf?
How do I get regenerated?
When am I stale?
```

If a generated output cannot answer those questions, it should not be treated as active project material.
