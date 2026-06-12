# Integration Status Report

## Status

This document records the current integration-level understanding of SDDA after reviewing `sdda.entrypoints`, `sdda.dataflow`, and several hand-walked examples.

It is a status report, not yet a finished specification.

## Core Findings

### The Unit Is A Reviewed Entrypoint

The unit of SDDA investigation is a reviewed entrypoint, not a package folder.

A package folder may contain several tools, probes, helpers, and modules with main guards used only for local testing. Package membership means related code, not necessarily dependent code.

SDDA should analyse reviewed entrypoints one at a time.

### Entrypoints Is The Tool-Identification Layer

`sdda.entrypoints` is the right upstream tool-identification layer.

It is not merely confirming that a known module such as `make_site2.__main__` is runnable. It builds the reviewed universe of program nodes that later producer/consumer matching searches across.

### Dataflow Is The Per-Program Evidence Layer

`sdda.dataflow` is the right per-program evidence layer.

In principle it analyses one selected program and reports what data or file families that program reads, writes, observes, produces, or leaves unresolved.

Remaining `make_site2` assumptions in the current package are extraction debt from the original implementation context, not conceptual failure.

### Path Resolution Is Essential

`sdda.dataflow` must resolve simple path variables and helper functions into normalized file-family templates.

Without path resolution, reports say things like:

```text
parser reads fn
downloader writes path
```

A human can see the match, but the integration layer cannot reliably connect producer and consumer.

With path resolution, reports should say:

```text
downloader writes files/output/HTML results/{year} {month}/{day}.html
parser2 reads files/output/HTML results/{year} {month}/{day}.html
```

This enables graph matching.

The intended resolver is not a general Python theorem prover. It should cover Sumo-Tools-style path idioms and emit unresolved evidence outside that supported subset.

Examples in scope:

```text
string literals
module constants
Path("literal")
Path(...) / ...
os.path.join(...)
f-strings with variable placeholders
simple local assignments
simple path-builder functions
path variables passed into local read/write helpers
```

### Cache Maintenance Rule

If a program reads, observes, or checks a file family and also writes or creates the same family, SDDA should default to treating that family as a self-maintained cache or generated output, not a fundamental input.

The family should still be emitted as an explicit human review item.

The default review stance is:

```text
exclude from automatic required inputs
confirm cache/generated/state/control role
promote only if human review says the family is a true seed input
```

### Abstract Data Entities Exist

Some dependencies are not literal files but behave like file-like data entities in the dependency graph.

The important current example is:

```text
_history_
```

`_history_` can be consumed and produced. It may have file representations, such as a History zip, and runtime access paths, such as the live store, but those representations are not necessarily fundamental distribution inputs.

### Final Inputs Are Producer Closures

Abstract entities and intermediate files should be expanded through their producer closure.

If a program consumes `_history_`, the final distribution input is not necessarily `_history_` or the History zip. It is the input set needed to produce `_history_`.

The expected current closure is:

```text
internet
  -> downloaded SumoDB HTML caches
  -> _history_
  -> History zip / live-store access paths
```

With cache outputs excluded by default, `HistoryFiles` is expected to be:

```text
{ internet }
```

### Live Store Is An Access Path

The live store is an access path for `_history_`, not a distribution input.

A call to:

```text
src.infra.live_store.api.get_history()
```

should be interpreted as consumption of `_history_`.

`files/output/store_name.txt` and shared memory are runtime plumbing, not source-distribution inputs.

### Some Current Code Has Boundary Bugs

Modules that consume `_history_` only through the live store may need an explicit file boundary, such as:

```text
--history-zip
```

This is needed for non-live-store environments and for clear command contracts.

Known or suspected examples include:

```text
src.infra.get_bios.__main__
src.analysis.persistence.__main__
```

### Internet Can Be A Pseudo-Input

For distribution closure, `internet` can be represented as a pseudo-input entity.

It is not packaged, but it explains why generated files need not be included in the source distribution.

### Dry Runs Need A Consistent Bottom Line

Each entrypoint dry run should end with a normalized summary:

```text
Module Investigated:
Input entities / file families:
Output entities / file families:
Review items:
```

Use "file families" where the path expression names a family rather than one concrete file.

## Canonical Examples

### Downloader

`src.infra.tracker.scraper.downloader` is the canonical simple cache-maintenance example.

Expected interpretation:

```text
Module Investigated:
  src.infra.tracker.scraper.downloader

Input entities:
  internet

Output file families:
  files/output/current standings/{year} {month}.html
  files/output/HTML results/{year} {month}/{day}.html

Review items:
  current standings family
    read/check + write
    default self-maintained cache/generated output

  HTML results family
    read/check + write
    default self-maintained cache/generated output
```

This is the go-to test case for the cache rule.

### Parser2

`src.infra.parser.parser2` is the canonical producer/consumer matching example.

Expected interpretation:

```text
Module Investigated:
  src.infra.parser.parser2

Input file families:
  files/output/current standings/{year} {month}.html
  files/output/HTML results/{year} {month}/{day}.html

Output entities:
  _history_

Output file families:
  files/output/Historys/{start}_01 to {end}_11.zip
```

This example exposes why path resolution matters: current `dataflow` sees the reads and writes, but does not yet always normalize local variables such as `fn` and `path` to concrete file-family templates.

### get_bios Downloader

`src.infra.get_bios.__main__` is another cache-maintenance example with an abstract `_history_` input.

Expected interpretation after substituting `_history_` closure:

```text
Input entities:
  internet

Output file families:
  files/output/infra/get_bios/rikishi/{rikid:05d}.html

Review items:
  files/output/infra/get_bios/rikishi/*.html
    read/write family
    default self-maintained generated cache
```

## Overall Conclusion

`sdda.entrypoints` and `sdda.dataflow` give SDDA the right foundations.

The missing work is integration and sharpening, not a change to the top-level requirements.

The important design requirements for the next stage are:

```text
machine-readable reviewed entrypoint catalogue
normalized file-family path resolution in dataflow
cache/read-write-family review policy
abstract data entities such as _history_
producer-closure expansion for final distribution inputs
```
