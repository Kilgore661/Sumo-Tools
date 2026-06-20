# Fixed V2 Equelo

## Status

Legacy / deletion candidate.

This package has been replaced by `src.analysis.equelo.fixed_supported`.
`fixed_v2` is retained only until the archive/deletion pass is complete.

The reason for replacement is material: the raw fixed-point entrant-initial
rating path could assign spurious extreme ratings to rarely supported
low-ranked chii. Those inflated initial ratings propagated into process ratings
and were exposed by public artifacts such as Highest Equelo.

Do not add new consumers of this package. Current production consumers should
use `src.analysis.equelo.api` or the fixed-supported artifacts under:

```text
files/output/Equelo/fixed_supported/
```
