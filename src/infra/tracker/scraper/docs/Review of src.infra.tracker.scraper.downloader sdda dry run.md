# Review of src.infra.tracker.scraper.downloader SDDA Dry Run

## Status

This document records the SDDA dry-run interpretation of `src.infra.tracker.scraper.downloader`.

The result is:

```text
N/A
```

There is no real entrypoint in this module.

This module is a library producer module. It provides functions that download and maintain local SumoDB HTML cache files.

## Module Investigated

```text
src.infra.tracker.scraper.downloader
```

The module ensures that requested SumoDB source HTML artifacts exist locally.

It is used by other code in the `_history_` producer chain.

It is not itself a user-facing SDDA entrypoint.

## Expected SDDA Summary

```text
Module investigated:
  src.infra.tracker.scraper.downloader

Entrypoint:
  N/A

Input entities:
  internet

Output file families:
  files/output/current standings/{year} {month}.html
  files/output/HTML results/{year} {month}/{day}.html

Review items:
  files/output/current standings/{year} {month}.html
    read/check + write family
    default self-maintained cache/generated output

  files/output/HTML results/{year} {month}/{day}.html
    read/check + write family
    default self-maintained cache/generated output
```

## Evidence Layer

The module reads/checks and writes two local HTML cache families.

It also downloads data from SumoDB.

The intended data function is:

```text
internet
-> downloaded SumoDB source HTML caches
```

The current standings family is fetched from:

```text
https://sumodb.sumogames.de/Banzuke.aspx?b={yyyymm}&heya=-1&shusshin=-1
```

The daily results family is fetched from:

```text
https://sumodb.sumogames.de/Results.aspx?b={yyyymm}&d={day}&simple=on
```

## Distribution Conclusion

No files need to be included in the source distribution because of `src.infra.tracker.scraper.downloader` itself.

Its local HTML files are output/cache families, not required source inputs.

The distribution-level conclusion for this module is:

```text
Input files:
  none

Input entities:
  internet

Output file families:
  files/output/current standings/{year} {month}.html
  files/output/HTML results/{year} {month}/{day}.html
```

Those output families are still important to SDDA because they discharge another module's input requirements.

In particular:

```text
src.infra.parser.parser2
  needs downloaded SumoDB HTML cache families

src.infra.tracker.scraper.downloader
  can create those cache families from internet

therefore the downloaded HTML families do not need to be shipped
```

This makes downloader part of the evidence chain for `_history_`:

```text
internet
  -> downloaded SumoDB HTML caches
  -> _history_
```

## Cache Rule Review

Both output families are checked or read before being written.

That does not make them fundamental input families.

Under the SDDA cache-maintenance rule, a file family that is read, observed, or checked and also written by the same program is removed from the automatic required-input set and emitted as a review item.

The expected human review outcome for these two families is:

```text
self-maintained generated cache
not required in source distribution when internet is available
```

## Current Dataflow Limitation

Current `sdda.dataflow` sees the read/write/download operations, but it does not yet fully resolve path variables such as `path` to the concrete file-family templates above.

The required improvement is normalized path-family resolution for simple path-builder functions and helper calls.

This module is the canonical simple test case for that improvement.
