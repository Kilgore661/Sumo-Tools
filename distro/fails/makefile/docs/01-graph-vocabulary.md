# Graph Vocabulary

## Purpose

This project will eventually need a dependency graph, but the word "dependency" is too broad for early audit work.

For now, keep graph types separate.

```text
import graph
dataflow graph
execution graph
typed dependency graph
```

The first two are the working graphs.

## Arrow Direction

The same arrow shape means different things in different graph types.

In an import graph:

```text
A -> B
```

means:

```text
A imports B
A depends on B
A uses exports from B
```

The arrow points from importer to exporter.

In a dataflow graph:

```text
A -> B
```

means:

```text
A feeds data, an artifact, or a virtual input to B
```

The arrow points from source to consumer.

Do not read import arrows as dataflow arrows.

## Import Graph

An import graph records Python module knowledge.

```text
A -> B means A imports B
```

The import graph should include every module in the audited package, including modules with no import edges. Isolated nodes matter because they reveal possible entry points, probes, scripts, or orphans.

Import graph records should include:

```text
source_module
target_module
import_form
evidence_file
evidence_line
notes
```

Use these scope concepts consistently in CSVs:

```text
intra-package imports
package-external exports
package-external imports
installed-library exports
```

Package-local graph views may collapse large outside-package lists into boundary nodes. Prefer explicit boundary names:

```text
package-external exports
package-external imports
installed-library exports
```

Interpretation:

```text
package module -> package-external exports
```

means the package module imports names exported by modules outside the package.

```text
package-external imports -> package module
```

means modules outside the package import names from the package module.

Do not label a boundary node merely `external imports`; that can be read in either direction.

The two boundary questions are different:

```text
What outside exports does this package import?
What outside imports use this package?
```

Package-local graph views may include a `package-external imports` boundary when a broader search has already found outside-package users. Otherwise, record it as pending broader search.

Example:

```csv
source_module,target_module,import_form,evidence_file,evidence_line,notes
src.infra.get_bios.api,src.infra.get_bios.parser,from import,src/infra/get_bios/api.py,18,imports OUTPUT_JSON
src.infra.get_bios.integrity,src.infra.get_bios.api,from import,src/infra/get_bios/integrity.py,14,uses typed BioStore API
```

## Dataflow Graph

A dataflow graph records inputs and outputs.

For this audit, modules are the primary nodes and artifacts are usually labels on edges.

```text
source -- artifact/input/output --> target
```

Artifacts may be files, file families, directories, URLs, virtual data objects, process return values or manual inputs.

Examples:

```text
live History -- get_history() --> src.infra.get_bios.__main__
external -- OUTPUT_DIR/infra/rikishi/*.html --> src.infra.get_bios.parser
src.infra.get_bios.parser -- OUTPUT_DIR/infra/rikishi_bios.json --> external
```

Use explicit templated paths rather than vague wildcards where practical:

```text
files/output/HTML results/{year} {month}/{day}.html
```

is better than:

```text
files/output/HTML results/*/*.html
```

Dataflow records should include:

```text
source_id
source_type
target_id
target_type
artifact
edge_type
evidence_file
evidence_line
notes
```

Suggested `edge_type` values:

```text
input
output
reads_existing
writes
copies
downloads
returns
diagnostic_output
manual_input
virtual_input
```

## Execution Graph

An execution graph records commands or runtime calls.

```text
command A -> command B means A is normally run before B
```

This matters for files such as `_run.ps1`, future make rules, publisher scripts and deployment steps.

Do not confuse execution order with import dependency or dataflow. A script may run after another script without importing it.

## Typed Dependency Graph

A typed dependency graph is the eventual union of the smaller graphs.

It may contain edges such as:

```text
imports
reads
writes
copies
downloads
runs-before
deploys
```

This graph is useful, but it is too easy to misread without a visible legend. Build it only after the import and dataflow graphs are understood.

## Canonical Representation

CSV-style inventories are canonical.

Rendered Mermaid, Graphviz or browser views are generated outputs. They are allowed to be useful and attractive, but they are not the source of truth.

Generated graph renderings belong under:

```text
files/output/makefile/...
```

not in source packages.

## Package-Local Dataflow

A package-local audit records only flows that are directly visible from the audited package.

If a module writes a file and no in-scope code explicitly consumes that exact produced object, record the output as going to a boundary node:

```text
module -- path/template.ext --> external
```

If a module reads a file and no in-scope code explicitly supplies that exact object, record the input as coming from a boundary node:

```text
external -- path/template.ext --> module
```

Do not connect a writer to a reader merely because their path patterns look compatible.

For example, these are two separate package-local facts:

```text
downloader -- OUTPUT_DIR/infra/rikishi/{rikid:05d}.html --> external
external -- OUTPUT_DIR/infra/rikishi/*.html --> parser
```

The audit must not prematurely collapse them into:

```text
downloader -- OUTPUT_DIR/infra/rikishi/*.html --> parser
```

That possible match belongs to global reconciliation.

## Global Reconciliation

Global reconciliation happens after package-local audits exist.

It asks:

```text
Which package outputs satisfy which package inputs?
Are matches exact, subset, superset, ambiguous or incompatible?
Which outputs have no consumers?
Which inputs have no producers?
Are the data instance and parameters coherent?
```

This is a separate phase because matching path templates can require judgement.

Example:

```text
OUTPUT_DIR/infra/rikishi/{rikid:05d}.html
```

may satisfy:

```text
OUTPUT_DIR/infra/rikishi/*.html
```

but that is a reconciliation finding, not a package-local edge.
