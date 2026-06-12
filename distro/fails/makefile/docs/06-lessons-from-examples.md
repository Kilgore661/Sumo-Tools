# Lessons From Examples

These are working rules learned while looking at small real packages.

They are deliberately practical. They should guide the audit even before the tooling is mature.

## Name Graphs By Edge Meaning

Avoid saying "dependency graph" until the edge types are explicit.

Use narrower names first:

```text
import graph
dataflow graph
execution graph
typed dependency graph
```

This prevents a single arrow from accidentally meaning imports, reads, writes, copies, runs-before and "conceptually related".

## Arrow Direction Depends On Graph Type

In an import graph:

```text
A -> B
```

means `A imports B`.

In a dataflow graph:

```text
A -> B
```

means `A feeds data/artifacts to B`.

These are not the same relationship. Always name the graph before interpreting the arrows.

## Include Isolated Modules

An import graph must show every module in the package, including isolated nodes.

Otherwise possible orphans disappear from the picture.

```text
isolated in the import graph != irrelevant
```

A module may be isolated by imports but connected by dataflow, command-line use, or manual workflow.

## Import-Orphan Is Not System-Orphan

`src.infra.get_bios` showed the important case.

Several modules look isolated in the import graph, but the dataflow graph shows them participating in related artifact input/output facts:

```text
__main__.py -- raw HTML output --> external
external -- raw HTML input --> parser.py
parser.py -- JSON output --> external
external -- JSON input --> probes/API/integrity
```

Do not classify a module as redundant from the import graph alone.

## Do Not Reconcile During Package Audit

A package-local audit records what the package itself says.

If a module writes an artifact, send it to `external`.

If a module reads an artifact, read it from `external`.

Do not connect those edges merely because the path patterns look related. Matching outputs to inputs is a later global reconciliation step.

This matters even inside one package. For example:

```text
downloader -- OUTPUT_DIR/infra/rikishi/{rikid:05d}.html --> external
external -- OUTPUT_DIR/infra/rikishi/*.html --> parser
```

Those may match, but the package-local graph should not collapse them.

## Prefer Modules As Nodes And Artifacts As Edge Labels

For early package-level dataflow, this is easier to read:

```text
producer -- path/to/artifact.csv --> consumer
```

than this:

```text
producer -> path/to/artifact.csv -> consumer
```

File nodes may still be useful later for a full graph database, but they make hand-read Mermaid diagrams noisy.

## Every Dataflow Edge Needs A Label

In a dataflow graph, the edge label carries the meaning.

An unlabeled edge is usually a mistake.

## Avoid Many Parallel Edges From A Generic External Node

Mermaid can render parallel labelled edges badly.

Instead of:

```text
external -> module
external -> module
external -> module
```

prefer distinct boundary nodes:

```text
live History -> module
SumoDB page -> module
existing cache -> module
```

This also makes the graph more truthful.

## Use Explicit Path Templates

Use concrete templates where possible:

```text
files/output/HTML results/{year} {month}/{day}.html
```

instead of vague wildcards:

```text
files/output/HTML results/*/*.html
```

The template records what the variable parts mean.

## Virtual Inputs Are Real Inputs

Some important inputs are not simple files.

Examples:

```text
History object from connect(start, end, use_zip)
live History from get_history()
RetrievalPlan
environment variables
network URLs
```

They should appear in dataflow when they determine outputs.

## Generated Views Are Not Canonical

Mermaid and HTML graph views are useful, but they are generated outputs.

The canonical audit data should be CSV-style inventories. Rendered graph output belongs under:

```text
files/output/makefile/...
```

## Small Packages Can Still Teach The Model

`src/misc` is mostly trivial:

```text
five standalone-ish producers
one producer with helper modules
no internal data pipe between the five programs
```

But it clarified the difference between:

```text
import graph
dataflow graph
downstream publication consumption
```

`src.infra.tracker.scraper` is tiny:

```text
one real downloader module
one docs folder
no internal import graph
clear raw-HTML acquisition dataflow
```

But it clarified that a package can be small and still central.

`src.infra.get_bios` is the useful medium example:

```text
downloader writes raw HTML
parser reads raw HTML and writes JSON
API/probes/integrity read JSON
```

It clarified why separate graphs are necessary before a typed dependency graph is safe.
