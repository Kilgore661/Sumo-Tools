# Buggy data-flow output snapshot

This directory contains a checked-in snapshot of the introspection output generated for the `make_site2` command while the data-flow tooling is being generalised.

It was generated with:

```powershell
python -m src.introspection.data_flow_graph src.products.make_site2.__main__ --import-root .
```

The generated report directory was:

```text
files/output/introspection/data_flow/src.products.make_site2.__main/
```

and its contents were copied here under:

```text
src/products/make_site2/buggy_output/src.products.make_site2.__main/
```

## Status

This is not an authoritative build model and not the final `make_site2` Makefile.

It is a regression fixture / evidence snapshot. Its purpose is to preserve the current behaviour of `src.introspection.data_flow_graph` before changing the data-flow analysis to handle cases exposed by `src.infra.get_bios.__main__`.

In particular, the current tooling is known or suspected to have problems around:

- treating a module imported only for a constant as though the whole module's dataflow belongs to the root command;
- treating an output family that is read or globbed for incremental/idempotent behaviour as though it were an ordinary source input;
- distinguishing reachable code from code that is plausibly executed by the analysed command;
- representing dynamically named output families as Makefile-usable artifact families.

## Intended use

When changing the introspection/data-flow code:

1. rerun the tool against `src.infra.get_bios.__main__`;
2. compare the result with the existing `makefile/infra/get_bios` audit;
3. rerun the tool against `src.products.make_site2.__main__`;
4. compare the new `make_site2` output with this snapshot.

The aim is not to preserve this snapshot exactly. The aim is to make any changes visible and explainable while the tool becomes less `make_site2`-specific and more generally useful for project build analysis.
