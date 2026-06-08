# make_site2 data-flow and Makefile inference status

## Purpose

This note records the current state of the `make_site2` data-flow investigation and the candidate Makefile generation work.

The goal is not simply to produce a Makefile that happens to run. The goal is to understand the build dependencies well enough that the eventual Makefile can explain how the project is built from source data, generated intermediates, and caches.

The current analysis is rooted at:

```powershell
python -m src.introspection.data_flow_graph src.products.make_site2.__main__ --import-root .
```

The reports are written to:

```text
files/output/introspection/data_flow/src.products.make_site2.__main/
```

The most useful reports at this stage are:

```text
artifact_uses.csv
root_artifacts.csv
upstream_rules.csv
root_rule.csv
Makefile.candidate
```

## What the current tool does

The tool walks the modules reachable from `src.products.make_site2.__main__`, extracts import edges, identifies file-like reads/writes/globs, resolves many path constants, classifies observed artifacts, and emits a candidate Makefile fragment.

This is static analysis. The reports are evidence, not proof. They describe the currently observed code path, and they can miss dynamic behaviour or over-emphasise implementation details such as caches.

## Work completed in this phase

### Reachable-only constant resolution

A small cross-module fixture was added under:

```text
src/introspection/fixtures/data_flow_cross_module/
```

The fixture has this shape:

```text
entry.run()
  -> builder.build(OUTPUT_DIR)
    -> writer.write_index(route_data_dir)
```

It reproduced a bug where the analyzer used a callee default path instead of the caller-supplied path. It also exposed a performance issue: constant resolution was being performed over too much of the repository.

The analyzer now resolves constants over the reachable module slice. The fixture now runs quickly rather than paying the full-repository cost.

### Cross-module path propagation

The analyzer now propagates path constants across imported function calls more effectively.

In the fixture, the output changed from the writer default:

```text
files/output/introspection/fixtures/default/index.txt
```

to the caller-supplied route path:

```text
files/output/introspection/fixtures/cross_module/route/data/index.txt
```

The same fix improved the real `make_site2` analysis. The basho-results index is now resolved as:

```text
files/output/make_site2/sumo-history/basho-results/data/basho_results_index.json
```

rather than the default path from the helper module.

### Transitive command outputs

The first Makefile-facing classification treated only modules inside `src.products.make_site2` as root outputs. That was too narrow.

Some outputs are written by reachable helper modules outside the root package. For example:

```text
src.analysis.sumo_history.basho_results.reports
```

writes a `make_site2` output when invoked by the `make_site2` command.

The classification was changed so concrete writes by reachable code are treated as root-command outputs unless they are upstream generated prerequisites, state artifacts, or unsuitable Make targets.

### Candidate Makefile shape

The candidate Makefile now parses under the installed Windows GNU Make 3.81.

A phony default target was added. The root product command is now represented by a stamp target so that GNU Make does not attempt to run the same command once per output target.

A dry run currently has the intended shape:

```text
python -m src.infra.get_bios.parser
python -m src.products.make_site2.__main__
python -c "from pathlib import Path; ..."
```

That means the upstream bios parser would run if needed, then `make_site2` would run once, then the stamp file would be updated.

The candidate should still be treated as a generated diagnostic artifact, not as the final hand-maintained project Makefile.

## Current observed make_site2 inputs

The current analysis observes these direct or prepared inputs for the `make_site2` execution path:

```text
files/input/elo_fide.json
files/output/store_name.txt
files/output/infra/get_bios/rikishi_bios.json
src/products/make_site2/runtime/site-refactor/*
```

These are not all conceptually equivalent.

### files/input/elo_fide.json

This appears to be a fixed source input.

### src/products/make_site2/runtime/site-refactor/*

This appears to be checked-in or source-tree runtime/static site material used by the build.

### files/output/infra/get_bios/rikishi_bios.json

This is a derived artifact. The current candidate identifies an upstream rule:

```makefile
files/output/infra/get_bios/rikishi_bio_missing_fields.csv files/output/infra/get_bios/rikishi_bios.json: files/output/infra/get_bios/rikishi/*.html
	python -m src.infra.get_bios.parser
```

So `rikishi_bios.json` is a direct prepared input to `make_site2`, but not a primary source artifact. It is derived from raw downloaded rikishi HTML.

The downloader that creates the raw HTML files is not currently represented in the `make_site2` graph.

### files/output/store_name.txt

The current reports classify this as a state artifact touched through:

```text
src.infra.live_store.api
```

This is accurate as observed evidence, but it should not be treated as the final conceptual dependency without further investigation.

The working interpretation is:

```text
history zip = primary source artifact
live store = cache / access layer over history data
store_name.txt = implementation detail or selector for the live-store access path
```

The live store should be treated like any other cache. A cache may appear in the observed code path, but the build description must be able to trace it back to the primary artifact from which it can be rebuilt. This matters especially for a first-ever build-and-run, where caches cannot be assumed to exist.

The current evidence shows that the `make_site2` path touches `store_name.txt`. It does not prove that `store_name.txt` is conceptually required. It may exist only after a live store has been started or selected. Some code may defensively fall back to using the history zip if live-store state is absent.

Therefore, `store_name.txt` should be documented as observed live-store state, not accepted as the true source dependency.

The full significance of `store_name.txt` cannot be settled from the `make_site2` analysis alone. It depends on the upstream history/live-store code.

## Cache principle

A cache is not a primary dependency.

A cache can be useful, and the observed code path may read from it, but the build model must be able to trace the cache back to its origin.

For this project, the relevant pattern is:

```text
primary source artifact
  -> derived persistent cache
    -> derived live/in-memory cache
      -> emitted output
```

Examples:

```text
internet pages
  -> downloaded HTML
    -> parsed JSON

history zip
  -> live store / access cache
    -> basho-results site data
```

The live store is not special conceptually. It is another cache. The difference is that it may be live or memory-backed rather than a plain zip, JSON, or CSV file.

## Current Makefile candidate interpretation

The current `Makefile.candidate` is best understood as a Makefile fragment for the observed `make_site2` execution path.

It is useful because it shows what the current code appears to consume and produce. It is not yet the final dependency model for the project.

In particular, the presence of `files/output/store_name.txt` in the candidate reflects the current observed access path through the live-store API. It should not yet be interpreted as meaning that the live store is the primary source of basho/history data.

## Caveats about current code

Some of the introspection code is intentionally pragmatic. It exists to get a useful approximation that can be inspected and refined.

Examples include:

```text
function seed constants
cross-module call-site propagation
root-output classification heuristics
state-artifact classification
stamp-target Makefile generation
```

These are useful scaffolding. They may need to be simplified or replaced once the project’s build boundaries are better understood.

The reports should therefore be read in layers:

```text
raw evidence:
  what the code appears to read/write/glob

candidate Makefile:
  a pragmatic build fragment from that evidence

conceptual dependency model:
  the intended build graph after caches are traced back to primary sources
```

## Next steps

### 1. Stabilise the direct make_site2 input list

Confirm which observed inputs are genuinely required by `make_site2`, which are optional, and which are artifacts of defensive or cached code paths.

Current observed inputs:

```text
files/input/elo_fide.json
files/output/store_name.txt
files/output/infra/get_bios/rikishi_bios.json
src/products/make_site2/runtime/site-refactor/*
```

### 2. Trace each input back to a primary source

Each observed input should be classified as one of:

```text
primary source artifact
fixed source file
derived persistent cache
derived live/in-memory cache
selector/config/state for a cache
unresolved external boundary
```

Then every non-primary item should be traced back until it reaches one of:

```text
the internet
a checked-in/fixed source file
a manually supplied external artifact
an explicit unresolved boundary
```

### 3. Analyse the upstream bios pipeline

The current graph includes the parser from raw HTML to `rikishi_bios.json`, but not the downloader from the internet to raw HTML.

The next upstream bios question is:

```text
internet / source URLs
  -> raw rikishi HTML
    -> rikishi_bios.json
```

### 4. Analyse the upstream history/live-store pipeline

This is the key unresolved area.

Assume the history zip is the primary source artifact. Then identify:

```text
which modules consume the history zip
which modules create or select a live store
whether store_name.txt is created by that process
whether store_name.txt is a selector, marker, cache state file, or something else
whether make_site2 emitters can run directly from the zip
whether they merely prefer the live store when present
```

Only after this upstream analysis can we decide whether the final dependency model should include:

```text
the history zip directly
a live-store preparation target
store_name.txt as an implementation detail
some combination of the above
```

### 5. Reconcile product-level and project-level Makefiles

The likely layering is:

```text
make_site2-level Makefile:
  given prepared inputs, build the site

project/root Makefile:
  prepare raw/generated prerequisites, then invoke product-level targets
```

The `make_site2` layer should not be responsible for downloading bios or importing history zips unless the code actually does that as part of the product command.

### 6. Keep validating Makefile candidates with dry runs

Use:

```powershell
make -f .\files\output\introspection\data_flow\src.products.make_site2.__main\Makefile.candidate -n
```

before any non-dry-run test.

A non-dry-run test should only be performed once the required prepared inputs and cache/source boundaries are understood.
