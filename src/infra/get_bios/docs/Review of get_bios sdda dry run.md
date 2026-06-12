# Review of get_bios SDDA Dry Run

## Status

This document records a requirements-level dry run of SDDA reasoning over `src.infra.get_bios.__main__`.

The purpose is not to assert that current SDDA code already derives this result automatically. The purpose is to record the intended data-dependency interpretation, including the caveats discovered while walking the dependency stack by hand.

## Target

The reviewed program is:

```text
src.infra.get_bios.__main__
```

It downloads raw SumoDB `Rikishi.aspx` HTML pages for all rikishi ids present in the current sumo `History`.

It does not parse those HTML pages into structured biography data. That is the responsibility of `src.infra.get_bios.parser`.

## Intended Data Function

As a function from input data to output data, `src.infra.get_bios.__main__` should be understood as:

```text
_history_
+ internet
-> files/output/infra/get_bios/rikishi/{rikid:05d}.html
```

The generated HTML files form the raw rikishi bio-page cache used by later `get_bios` tools.

For final source-distribution closure, `_history_` expands to:

```text
internet
```

Therefore the final distribution input for this program is:

```text
internet
```

## Inputs

### History

The program needs a `History` value so it can discover the set of rikishi ids that appear in parsed tournament history.

For SDDA, this should be represented as the abstract data entity:

```text
_history_
```

Current code obtains this `History` through:

```text
src.infra.live_store.api.get_history()
```

That is an implementation access path, not the fundamental dependency.

The live store exists for runtime speed and convenience. It should be collapsed to `_history_` when reasoning about data dependencies.

The intended runnable contract is that modules needing `History` should also accept an explicit History zip path, for example through a `--history-zip` CLI option. `src.infra.get_bios.__main__` does not currently expose that option. That is a boundary bug discovered by this dry run.

The History zip is a representation of `_history_`, not the final source-distribution input. `_history_` is produced from downloaded SumoDB HTML caches whose own final input closure is expected to be `internet`.

### Internet

For each missing rikishi id, the program downloads:

```text
https://sumodb.sumogames.de/Rikishi.aspx?r={rikid}
```

These pages are internet inputs.

## Outputs

The program writes downloaded HTML pages to:

```text
files/output/infra/get_bios/rikishi/{rikid:05d}.html
```

Each successful response is saved only if it is at least the configured minimum size.

## Cache Review Item

The program also observes existing files:

```text
files/output/infra/get_bios/rikishi/*.html
```

It uses those files to avoid re-downloading pages that are already present.

Operationally, this file family is both an input and an output:

```text
observed:
  files/output/infra/get_bios/rikishi/*.html

written:
  files/output/infra/get_bios/rikishi/{rikid:05d}.html
```

For Sumo-Tools-style SDDA reasoning, a file family that is both observed and written by the same program should not be automatically treated as a fundamental input.

The default interpretation for this family is:

```text
role:
  self-maintained generated cache

distribution default:
  not required in principle

review question:
  confirm that the cache may be omitted from a source distribution, or explicitly promote it if there is a practical reason to include it for efficiency, politeness to SumoDB, or reproducibility.
```

## Recursive Dependency Walk

The initial code-level walk found a dependency on:

```text
src.infra.live_store.api.get_history()
```

Following that dependency led to `src.infra.live_store`, which uses a shared-memory segment and a published-name file:

```text
files/output/store_name.txt
```

For distribution analysis, that shared-memory mechanism is a red herring. The live store is not a source data file, and it is not required if the History zip is available.

The corrected SDDA interpretation is:

```text
get_history()
  -> _history_
```

The recursive walk does not terminate at a History zip. A History zip is one representation of `_history_`. The final distribution closure expands `_history_` through its producer chain:

```text
internet
  -> downloaded SumoDB HTML caches
  -> _history_
```

## Result

The intended SDDA result for `src.infra.get_bios.__main__` is:

```text
Input entities:
  internet

Output file families:
  files/output/infra/get_bios/rikishi/{rikid:05d}.html

Review items:
  files/output/infra/get_bios/rikishi/*.html
    read/write family
    default excluded from required source inputs
    likely self-maintained generated cache
```

The local program-level dependencies before final closure are:

```text
_history_
internet
```

The final distribution input list collapses to:

```text
internet
```

## Implementation Gap

`src.infra.get_bios.__main__` should expose the intended History file boundary directly, most likely with:

```text
--history-zip <path>
```

When supplied, the program should load History from that zip instead of requiring a live store.

When not supplied, it may continue to use the live store as the fast local default.
