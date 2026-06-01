# PA Runtime Data Contracts

## Status

Draft.

This document translates the existing `make_site2` specification vocabulary into generated-output dependency-graph terms.

The `make_site2` documentation spine already describes Pages, Filters, material public state, PA data, indexed-table payloads, canonical Public View Links and runtime loading/selecting staged data. This note does not replace that spine. It provides audit vocabulary for deciding which generated files are required by a clickable site output.

## Core rule

For a clickable `make_site2` output root, the required output is not only the default browser view.

It is the full set of material public views reachable through declared Filters/options on that clickable Page.

```text
Clickable nav item
  -> Page
      -> PA
          -> material Filter state
              -> runtime data contract
                  -> staged data files required for each reachable public view
```

If the browser can show a PA state through ordinary declared controls, then the data needed for that state is part of the current website-output graph.

## Existing spine terms

The current `make_site2` documentation uses these terms:

```text
Filter
FilterSection
material public state
Published Artifact / PA
site-facing inputs
PA data
indexed table payloads
required data references
canonical Public View Link
BrowserRuntime
```

The makefile audit should prefer those terms when discussing public semantics.

This note introduces additional operational terms only where needed to inspect generated files.

## Runtime data contract

A **runtime data contract** describes how a PA obtains the staged data needed to realise all material public views reachable from a clickable Page.

The contract should identify:

```text
PA identity:
PA terminal form:
Filter / option axes:
Default public view:
Default payloads:
Additional reachable payloads:
Payload addressing rule:
Runtime load/select behaviour:
Producer output source:
Data-instance / Selected-History coherence requirement:
```

## Option axis

An **option axis** is an audit term for a declared finite public selection dimension.

In the documentation spine, this is normally a Filter, especially a `SingleFiniteChoice`, or a PA-specific material state represented in the canonical Public View Link.

Examples may include:

```text
basho
rank/chii
division
era
standing
metric
view mode
```

Use the documentation-spine term **Filter** where the option is a formal Filter. Use **option axis** only as a graph/audit convenience when examining how files are selected.

## Data contract shapes

Classify each clickable PA's runtime data contract as one of the following.

### single payload

One staged data file or small fixed set of files is sufficient for the PA.

```text
Page state
  -> one declared payload set
```

### aggregate payload with client-side filtering

One larger staged dataset contains all selectable values along the option axis. Runtime changes select rows, traces or visible subsets from already-loaded data.

```text
all-data.csv
  -> browser selects/filter rows for chosen state
```

This matches the conceptual model of a database-like table where a user choice selects a point or slice from a larger dataset.

### indexed payload family

A manifest/index file declares selectable values and maps each value to one or more payload files. Runtime changes may fetch a payload for the selected value.

```text
index.json
  -> selected key
      -> by-key/<key>.csv
```

The current output graph includes every payload reachable through the published index, unless the corresponding option value is hidden, unavailable or explicitly legacy.

### hybrid payload

The PA uses both aggregate data and additional indexed/detail payloads.

```text
summary.csv
index.json
  -> selected key
      -> detail/<key>.csv
```

### unknown

The data contract cannot yet be determined from docs/code inspection.

Unknown contracts should be marked for follow-up before any deletion or provenance decision depends on them.

## Reachable payload

A **reachable payload** is any staged data file that can be loaded or selected by the browser through declared public state from a clickable Page.

For an indexed payload family, reachable payloads include the index plus all payloads it can address.

For an aggregate payload, the reachable payload is the aggregate file itself, plus any config/notes/provenance files required for meaningful display.

## Dependency-graph consequence

For a clickable Page:

```text
current website-output root
  -> every material public view reachable from that Page
      -> every staged data file needed for those views
          -> producer output family
              -> producer module and upstream inputs
```

Therefore:

- a default view does not exhaust the dependency graph;
- a manifest/index may be required but not sufficient;
- all reachable payloads are current if the controls exposing them are current;
- copied files that are not reachable from a clickable Page are not protected by the website graph;
- data files with the right shape are not coherent merely because they exist in `files/output`.

## make_site2 audit fields

Add these fields to the clickable-output audit table:

```text
Clickable page id:
PA identity:
PA terminal form:
Formal Filters:
Other option axes:
Default public view:
Canonical link state:
Runtime data contract:
Default payloads:
Manifest/index files:
Reachable payload family:
Payload addressing rule:
Additional browser fetches?:
All reachable payloads staged?:
Producer output source:
Selected-History / data-instance coherence evidence:
Open questions:
```

## Open issue: vocabulary normalisation

The makefile docs currently use some audit-oriented terms that are not yet normalised with the `make_site2` documentation spine.

Terms needing alignment include:

```text
option axis
runtime data contract
single payload
aggregate payload
indexed payload family
reachable payload
browser-visible output root
```

These should be mapped to, replaced by or explicitly distinguished from the spine's terms:

```text
Filter
material public state
Public View Link
PA data
site-facing input
required data reference
indexed table payload
BuildOutput
BrowserRuntime
```

Until that normalisation is done, the makefile docs should be treated as audit vocabulary rather than normative `make_site2` specification vocabulary.
