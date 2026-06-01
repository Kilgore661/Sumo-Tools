# Makefile Layout

## Audit Layout

The audit artifacts mirror the `src` tree.

```text
src/infra/get_bios -> makefile/infra/get_bios
src/misc           -> makefile/misc
```

This keeps package-local evidence near the conceptual package path while staying outside `src`.

## Build Layout Is A Later Decision

This layout does not imply that the final build must use recursive Make.

Possible final build shapes include:

```text
one top-level Makefile
one top-level Makefile that includes generated .mk fragments
one top-level Makefile plus hand-written package fragments
recursive package Makefiles
another build runner generated from the audit CSVs
```

For now, the goal is not to choose the final Make style. The goal is to collect accurate package-local facts.

## Rule

Put package audit artifacts at:

```text
makefile/{path-under-src}/
```

Generated audit outputs still belong under:

```text
files/output/makefile/
```

The `makefile/...` tree is for hand-authored audit artifacts and package-local CSVs while the process is being designed.
