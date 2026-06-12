# SDDA Review - parser2

## Status

This document records the SDDA dry-run interpretation of `src.infra.parser.parser2`.

It is a module-local review note and a candidate acceptance example for producer/consumer file-family matching.

## Module Investigated

```text
src.infra.parser.parser2
```

This module parses downloaded SumoDB source HTML into the canonical parsed sumo `History`.

## Expected SDDA Summary

```text
Input file families:
  files/output/current standings/{year} {month}.html
  files/output/HTML results/{year} {month}/{day}.html

Output entities:
  _history_

Output file families:
  files/output/Historys/{start}_01 to {end}_11.zip

Diagnostic output file families:
  files/output/banzuke warnings.html
  files/output/file-format weirdness.html
  files/output/warnings/state {year} {month:02d}.txt
  files/output/warnings/chii {year} {month:02d}.txt
```

## Data Function

The intended data function is:

```text
downloaded SumoDB source HTML caches
-> _history_
-> files/output/Historys/{start}_01 to {end}_11.zip
```

The current standings family supplies banzuke/marginalia data.

The daily results family supplies bout results.

Together they are parsed into a `History` object and serialized as a History zip.

## Relationship To Downloader

The parser's input file families are the downloader's output file families:

```text
src.infra.tracker.scraper.downloader
  -> files/output/current standings/{year} {month}.html
  -> files/output/HTML results/{year} {month}/{day}.html

src.infra.parser.parser2
  reads those families
  produces _history_
```

This is the canonical producer/consumer matching example for SDDA integration.

## Current Dataflow Limitation

Current `sdda.dataflow` sees the relevant read points and warning-file writes, but it does not yet always resolve local variables such as `fn` to concrete file-family templates.

For example, the desired normalized families are:

```text
files/output/current standings/{year} {month}.html
files/output/HTML results/{year} {month}/{day}.html
```

not only scoped local expressions such as:

```text
src.infra.parser.parser2_margin:_parse_raw_marginalia:fn
src.infra.parser.parser_daily:_parse_daily_results:fn
```

Current `sdda.dataflow` also needs better recognition of History zip writes through the serializer stack:

```text
save_history_with_annotations(...)
  -> BaseSerialiser.save_to_zip(...)
  -> ZipFile(filename + ".zip", "w")
```

## Distribution Interpretation

The parser's raw HTML inputs are generated/cache outputs of the downloader.

After producer-closure expansion and cache-rule review, the expected final input closure for `_history_` is:

```text
internet
```
