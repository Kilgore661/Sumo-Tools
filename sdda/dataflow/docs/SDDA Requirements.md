# SDDA Requirements

The Static Data-Dependency Analyser, now housed in `sdda.dataflow`, is required to determine what non-code file families may be needed, produced, or observed when building and deploying the Sumo-Tools website.

The purpose is to support source-distribution and reproduction decisions for the website product.

The target distribution mode is:

```text
source distribution with internet access
```

The distribution scope is:

```text
everything needed to build and deploy a functioning website locally and remotely from src.products.make_site2.__main__
```

Code not reachable from that website build/deploy entry point is out of distribution scope, even if it defines a command-line tool, a main guard, or a useful research/probe workflow.

Such code is treated as research unless and until it becomes reachable from the website build/deploy path.

In particular, the analyser should help answer:

```text
What non-code files need to be included in a source distribution of the website product?
What non-code files can be regenerated from code, internet sources, or other generated file families?
What file dependencies are currently implicit in the website build/deploy path?
What deployment-time settings or local assumptions are currently implicit in that path?
```

The analyser is not primarily required to generate a Makefile. A Makefile, Ninja file, `doit` task file, or other build recipe may be a later output, but build-file generation is only a test of whether the extracted dependency information is sufficiently complete and precise.

The analyser should be conservative. It should report file families that may be used by the website build/deploy path, not only file families that must be used on every execution path.
