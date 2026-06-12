# live_store Audit Artifacts

This folder contains the package-level makefile audit for:

```text
src/infra/live_store
```

## Report

- [docs/report.md](docs/report.md)

## CSV Deliverables

- `packages.csv`
- `modules.csv`
- `import_edges.csv`
- `dataflow_edges.csv`
- `entry_points.csv`
- `output_families.csv`
- `output_consumers.csv`
- `module_classification.csv`
- `output_classification.csv`

## Graph Views

These are review views over the CSV facts, not canonical data:

- [graphs/imports.html](graphs/imports.html)
- [graphs/dataflow.html](graphs/dataflow.html)
