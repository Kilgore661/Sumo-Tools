# Output and Module Classification

## Status

Draft.

This document defines classification terms for generated outputs and modules in the generated-output dependency graph.

## Legacy

A generated output, producer, or consumer is **legacy** if it is no longer part of any current or intended line of work.

Legacy material may have historical value, but it should not remain in the live generated-output graph merely because it exists.

## Non-legacy

A generated output, producer, or consumer is **non-legacy** if it is current, intentionally retained, plausibly needed for a named future use, or valuable as a deliberate research/reference artifact.

"Potentially useful someday" is not enough. The future use should be nameable.

## Output layers

Generated outputs should be classified by layer.

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

## Output classifications

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

## Module classifications

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

## Deletion policy

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
