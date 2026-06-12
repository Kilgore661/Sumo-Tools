# SDDA Integration Notes

These are current design notes, not a committed interface.

They describe how `sdda.entrypoints` and `sdda.dataflow` might later be stitched together to answer distribution questions.

## Background

The original SDDA work was mainly exercised against the final site-building stage, especially `make_site2`.

For that narrow use it could produce plausible information about files read by the final stage.

The harder question is broader:

```text
If the deliverable is make_site2, what has to exist before it can run?
```

Some of the files read by `make_site2` are probably outputs of earlier modules. Those earlier modules may read files that are outputs of still earlier modules. Eventually the chain should bottom out at fundamental input files.

## Current package split

The split is:

```text
sdda.entrypoints
  identify and review executable modules / candidate entrypoints

sdda.dataflow
  analyse one selected module and report apparent file reads/writes
```

The split is deliberate.

`entrypoints` is about Python module topology and human review of runnable modules.

`dataflow` is about data-file relationships for a selected module.

Neither package currently answers the full distribution question by itself.

## Working mental model

The eventual distribution analysis can be viewed as a graph problem with two kinds of nodes:

```text
program nodes
  reviewed entrypoints / pipeline stages

data-file nodes
  files that are read or written by those programs
```

Possible edge meanings:

```text
program -> data file
  the program writes or emits the file

data file -> program
  the program reads or requires the file
```

Given a deliverable entrypoint, such as `make_site2`, the task is to walk backwards through this graph until every required data file is either:

```text
produced by a known upstream entrypoint
```

or:

```text
classified as a fundamental input
```

## Proposed broad workflow

A likely workflow is:

```text
1. Run sdda.entrypoints over the relevant import root.
2. Review the generated entrypoint form.
3. Decide which candidate programs are true pipeline entrypoints.
4. Run sdda.dataflow for the deliverable entrypoint.
5. Run sdda.dataflow for the reviewed upstream entrypoint candidates.
6. Build a file producer/consumer table.
7. Starting from the deliverable, walk backwards through required files.
8. Report the required entrypoints, intermediate generated files, fundamental input files, and unresolved files.
```

This is broad but controlled: `entrypoints` narrows the module universe before `dataflow` is applied.

## Alternative recursive workflow

Another possible workflow is recursive:

```text
1. Run sdda.dataflow on the deliverable entrypoint.
2. For each file it reads, search for candidate producing modules.
3. Run sdda.dataflow only on those candidates.
4. Repeat until no new producers are found.
```

This may do less work, but it depends on being able to search reliably for file producers. It may be more brittle than first building a reviewed entrypoint set.

## Current preference

The current preference is the broad-but-controlled workflow:

```text
entrypoints -> dataflow -> distribution closure
```

Reasons:

```text
entrypoints gives a human-reviewed set of runnable modules
dataflow can then be applied to a meaningful subset of modules
the final closure calculation can be deterministic over collected dataflow records
```

## Possible future package

A future package might be:

```text
sdda.distribution
```

Possible command shape:

```powershell
python -m sdda.distribution --import-root .\src --deliverable products.make_site2.__main__
```

Possible inputs:

```text
reviewed entrypoint list
per-entrypoint dataflow summaries
```

Possible outputs:

```text
distribution_requirements.md
distribution_requirements.csv
pipeline_graph.csv
unresolved_files.csv
```

## Desired final report shape

For a deliverable such as `make_site2`, the report should eventually say something like:

```text
Deliverable:
  products.make_site2.__main__

Required entrypoints:
  stage_a
  stage_b
  products.make_site2.__main__

Fundamental input files:
  files/input/foo.csv
  files/input/bar.json

Intermediate generated files:
  files/output/stage_a/x.json
  files/output/stage_b/y.csv

Unresolved files:
  files/output/unknown/z.csv
    read by: stage_b
    no producing entrypoint found
```

## Important caveats

The current tools are conservative and incomplete.

`entrypoints` assumes the import root is the closed universe for syntactic reference analysis.

`entrypoints` does not detect dynamic imports.

`dataflow` is still a probe-style analysis and may over-report or under-report file relationships.

The final distribution layer should not pretend to infer author intent. It should present evidence and unresolved cases clearly.

## Natural hand-off point

The current target hand-off state is:

```text
sdda.entrypoints
  documented and usable for entrypoint review

sdda.dataflow
  old SDDA behaviour preserved under a clearer package name

sdda/README.md
  explains the package split

sdda/docs/Notes.md
  records current thinking about how the pieces may later be combined
```

This gives a clean break before designing the future distribution-closure layer.
