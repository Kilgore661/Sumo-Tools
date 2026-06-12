# Website Runtime Data Contracts

## Purpose

The public website is one consumer of generated outputs. It is important, but it is not special.

For `make_site2`, clickable navigation entries define current website-output roots. A generated file is protected by the website graph only if it is needed for a material public state reachable from a clickable page.

## Core Rule

For a clickable `make_site2` page, the required output is not only the default browser view.

It is the full set of material public views reachable through declared page controls.

```text
clickable nav item
  -> Page
      -> Published Artifact
          -> material Filter state
              -> runtime data contract
                  -> staged data files required for each reachable view
```

## Prefer Existing Site Vocabulary

When working inside `make_site2`, prefer its existing vocabulary where possible:

```text
Filter
FilterSection
material public state
Published Artifact
site-facing input
PA data
indexed table payload
required data reference
canonical Public View Link
BrowserRuntime
```

The makefile audit may still use operational terms such as "dataflow edge" or "reachable payload", but those should not replace product-facing site terms without a deliberate decision.

## Runtime Data Contract

A runtime data contract records how a page obtains the staged data needed to realise its material public states.

Fields:

```text
page_id:
published_artifact_id:
terminal_form:
formal_filters:
other_option_axes:
default_public_view:
canonical_link_state:
contract_shape:
default_payloads:
manifest_or_index_files:
reachable_payload_family:
payload_addressing_rule:
additional_browser_fetches:
producer_output_source:
selected_history_coherence:
open_questions:
```

## Contract Shapes

### single payload

One data file or small fixed set of files is sufficient.

### aggregate payload with client-side filtering

One larger staged dataset contains all selectable values. Runtime state selects rows, traces or visible subsets.

### indexed payload family

An index or manifest declares selectable values and maps each value to one or more payload files.

### hybrid payload

The page uses both aggregate data and indexed/detail payloads.

### unknown

The contract cannot yet be determined from docs/code inspection.

## Reachable Payload

A reachable payload is any staged data file that can be loaded or selected through declared public page state.

For an indexed payload family, reachable payloads include the index plus all payloads it can address.

For an aggregate payload, the reachable payload is the aggregate file itself, plus any config or provenance files required for meaningful display.

## Consequences

- A default view does not exhaust the graph.
- A manifest may be required but not sufficient.
- Copied files that are not reachable from a clickable page are not protected by the website graph.
- Data files are not coherent merely because they exist in `files/output`.
- A page can be current while one of its copied upstream outputs is stale or incoherent.
