# SDDA Requirements

## Purpose

SDDA, the Static Data-Dependency Analyser, shall analyse the Sumo-Tools repository as a collection of tools that consume, produce, transform, and publish data.

Its purpose is to explain static data dependency relationships across the repository: which data artefacts depend on which other data artefacts, through which tools, and with what supporting code evidence.

The website distribution report is one important view over this model, not the whole model. `make_site2` is a significant tool because it assembles many results into a website, but SDDA's broader responsibility is to map the tools and data dependencies of Sumo-Tools as a whole.

## Tool Identification

To explain data dependency relationships, SDDA must first identify the repository's tool surface.

SDDA shall use module dependency evidence to distinguish likely standalone programs, imported programs requiring review, and support or library modules.

Modules that are executable and not imported by other project modules are especially important candidate entrypoints, because they are likely independent tools whose data dependencies should be analysed.

## Per-Tool Dataflow

For each selected tool, SDDA shall analyse apparent non-code data relationships.

This includes files, directories, globs, generated artefact families, external sources, configuration, caches, diagnostics, and deployment assumptions that the tool reads, writes, observes, downloads, creates, or otherwise depends on.

## Repository-Level Explanations

SDDA shall support repository-level explanations, including:

```text
what tools exist
what each tool consumes and produces
which tool outputs are inputs to other tools
which tools and data are required for a selected deliverable, such as make_site2
which tools and data are not required for that deliverable, and why
which cases remain unresolved or require human review
```

## Evidence And Review

SDDA shall be conservative and evidence-backed.

It must not pretend to infer perfect author intent or full Python runtime behavior.

Ambiguous tool status, dynamic behavior, unresolved producers or consumers, and uncertain data-family matches shall be reported for human review rather than hidden.
