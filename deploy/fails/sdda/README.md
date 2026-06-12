# SDDA

SDDA is being split into two related tools:

```text
sdda.entrypoints
sdda.dataflow
```

The split is intended to make the project easier to reason about before adding a higher-level distribution analysis layer.

## `sdda.entrypoints`

`entrypoints` indexes Python modules under an import root and helps identify candidate entrypoints.

It answers questions such as:

```text
Which modules are executable programs?
Which programs are not imported by other indexed modules?
Which programs are imported and need human review?
Which candidates look command-like?
```

Read more in:

```text
sdda/entrypoints/README.md
sdda/entrypoints/docs/
```

## `sdda.dataflow`

`dataflow` contains the original SDDA analysis code.

It analyses a selected module and reports apparent data-file inputs and outputs.

It is intended to answer questions such as:

```text
What data files does this module read?
What data files does this module write?
```

Run it with:

```powershell
python -m sdda.dataflow
```

Read more in:

```text
sdda/dataflow/README.md
sdda/dataflow/docs/
```

## Intended longer-term direction

The eventual goal is to combine entrypoint review with dataflow analysis to answer distribution questions such as:

```text
If the deliverable is make_site2, which entrypoints must be run,
and which data files are fundamental inputs?
```

That layer does not exist yet as a finished tool.

Current design notes are in:

```text
sdda/docs/Notes.md
```
