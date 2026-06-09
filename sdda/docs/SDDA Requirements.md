# SDDA Requirements

The Static Data-Dependency Analyser, `sdda.py`, is required to determine what non-code file families may be needed, produced, or observed by a Sumo-Tools Python entry point, package, or command.

The purpose is to support source-distribution and reproduction decisions for the repository.

The target distribution mode is:

```text
source distribution with internet access
```

In particular, the analyser should help answer:

```text
What non-code files need to be included in a source distribution of the repo?
What non-code files can be regenerated from code, internet sources, or other generated file families?
What file dependencies are currently implicit in the code?
What deployment-time settings or local assumptions are currently implicit in the code?
```

The analyser is not primarily required to generate a Makefile. A Makefile, Ninja file, `doit` task file, or other build recipe may be a later output, but build-file generation is only a test of whether the extracted dependency information is sufficiently complete and precise.

The analyser should be conservative. It should report file families that may be used, not only file families that must be used on every execution path.
