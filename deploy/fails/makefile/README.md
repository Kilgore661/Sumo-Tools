# Makefile Sub-Project

This sub-project exists to get Sumo-Tools back under build control.

The rough requirement is:

```text
Take out the trash.
Create a makefile.
```

That means:

- identify the real source, producer, output and consumer relationships in `src`;
- distinguish live generated outputs from stale experiments, duplicate artifacts and legacy debris;
- preserve outputs that are canonical, consumed, deliberately retained, or useful diagnostics;
- delete or quarantine generated material that is no longer part of an active line of work;
- turn the surviving build knowledge into explicit, repeatable make rules.

The first phase is not to write the Makefile. The first phase is to make the graph visible enough that the Makefile can be written without encoding confusion.

## Layout

Audit artifacts mirror the `src` tree under `makefile`.

Examples:

```text
src/infra/get_bios -> makefile/infra/get_bios
src/misc           -> makefile/misc
```

This does not decide the final Makefile architecture. A future build may use one top-level Makefile, included fragments, generated dependency files, or a mix. The audit tree mirrors `src` because package-local reports are easier to find and compare that way.

## Working Principles

- Keep graph types separate at first.
- Use CSV-style inventories as the canonical audit material.
- Treat rendered graphs as views, not source of truth.
- Produce charts and graph views on demand.
- Generate graph renderings under `files/output/...`, not inside `src` or `docs`.
- Ask human-intent questions explicitly instead of guessing whether an old output is still valuable.

## Documentation

- [01 Graph Vocabulary](docs/01-graph-vocabulary.md)
- [02 Audit Workflow](docs/02-audit-workflow.md)
- [03 Output and Module Classification](docs/03-output-and-module-classification.md)
- [04 Review Checklists](docs/04-review-checklists.md)
- [05 Website Runtime Data Contracts](docs/05-website-runtime-data-contracts.md)
- [06 Lessons From Examples](docs/06-lessons-from-examples.md)
- [07 Process Deliverables](docs/07-process-deliverables.md)
- [08 Makefile Layout](docs/08-makefile-layout.md)
- [Mermaid graph notes](docs/mermaid/README.md)

## Intended Outputs

The audit should eventually produce machine-readable files such as:

```text
files/output/makefile/import_edges.csv
files/output/makefile/dataflow_edges.csv
files/output/makefile/entry_points.csv
files/output/makefile/output_families.csv
files/output/makefile/module_classification.csv
files/output/makefile/output_classification.csv
```

Rendered graph views, if generated, should also live under `files/output/makefile/...`.
