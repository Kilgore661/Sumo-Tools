# SDDA Dataflow

`SDDA Dataflow` is the original Static Data-Dependency Analyser code, now separated from `sdda.entrypoints`.

It analyses a selected Python module and reports apparent non-code file inputs and outputs.

## Purpose

The project exists to determine what non-code file families may be needed, produced, or observed by Sumo-Tools code, so that distribution and reproduction decisions can be made explicitly.

The initial requirements and specification are in:

```text
sdda/dataflow/docs/SDDA Requirements.md
sdda/dataflow/docs/SDDA Specification.md
```

## How to run

Run from the repository root.

The positional argument is a **dotted Python module name**, not a filesystem path.

For example, with the repository root as the import root:

```powershell
python -m sdda.dataflow --import-root . src.products.make_site2.__main__
```

Do not pass the equivalent file path:

```powershell
python -m sdda.dataflow --import-root . .\src\products\make_site2\__main__.py
```

That path form is not currently accepted.

## Import root and module name

The module name is interpreted relative to `--import-root`.

With:

```powershell
python -m sdda.dataflow --import-root . src.products.make_site2.__main__
```

the import root is the repository root, so the module name includes `src`.

With:

```powershell
python -m sdda.dataflow --import-root .\src products.make_site2.__main__
```

the import root is `src`, so the module name starts at `products`.

At present, using the repository root import root is usually the safer default because much of the project imports modules using fully qualified `src...` names.

## Output

By default, reports are written under:

```text
files/output/sdda/<root-module>/
```

The exact output location is printed by the command.

## Current status

This package is still probe-style analysis code. It is useful evidence, but it should not be treated as a complete distribution-closure tool by itself.

The intended longer-term workflow is described in:

```text
sdda/docs/Notes.md
```
