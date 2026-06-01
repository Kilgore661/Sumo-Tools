# Audit Workflow

## Status

Draft.

This document defines the workflow for deriving and pruning the generated-output dependency graph.

## Audit products

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

## Proposed workflow

### Phase 1: Inventory

Find entry points and generated outputs.

Produce:

```text
entry_points.csv
output_families.csv
```

The inventory should include Python, JavaScript, shell/PowerShell, test helpers, publisher scripts, deployment scripts, and any function that behaves as a producer even if it is not a command-line entry point.

### Phase 2: Consumer search

For each output family, search for code, docs, tests, and build scripts that read or copy it.

Produce:

```text
output_consumers.csv
```

A consumer may be code, a browser runtime, a deployment step, a test, a manual workflow, or another generated-output producer.

### Phase 3: Initial classification

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

This phase should not make human-intent decisions. It should record evidence and mark uncertain cases.

### Phase 4: Human leaf review

Human reviews unused outputs and unknown manual-use outputs.

Decide:

```text
unused legacy
unused non-legacy
research record
trash
```

A vague future possibility is not enough to keep a generated output live. A retained future use should be nameable.

### Phase 5: Backtracking

Remove legacy terminal outputs from the active graph.

Re-evaluate producers and their inputs.

Repeat until classifications stabilize.

The key recursive question is:

```text
After removing legacy consumers, does this input still feed any non-legacy consumer?
```

If not, classify it as unused and decide whether it is legacy or non-legacy.

### Phase 6: Action plan

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

## make_site2-specific start rule

For `make_site2`, the current website-output roots are the clickable navigation entries.

```text
Clickable entry = current website output root.
Non-clickable entry = historical planning residue, not a current website output.
```

This means:

```text
clickable browser page
  -> route data files needed by that page
      -> producer outputs copied or derived by make_site2
          -> upstream producers and inputs
```

Physical files written by `make_site2` are implementation artifacts unless they support one of the clickable website-output roots.

## Final test

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
