# Remove Adapter Layer Proposal

## Status

Proposal, added 2026-05-14.

This records the proposed direction for removing the current deep-link adapter
layer after the PA runtime is mature enough to own all promoted public pages.

## Problem

The public site currently has two kinds of make_site-owned table or tool pages:

* PA-runtime pages, where `make_site` owns the public page shell, manifest
  loading, option state, URL state, cache-busting, and shared behaviour;
* bespoke or copied pages, where an older app or custom renderer owns its own
  HTML, JavaScript, option controls, URL parser, validation, and styling.

The second category now has small adapters so those pages can participate in
deep-site URLs.  That was the right short-term repair, because it made the
site usable without reworking several pages at once.  It should not become the
long-term architecture.

The deeper issue is not the adapters themselves.  The deeper issue is that the
site still has more than one public UI model.

## Current Examples

Current PA-runtime-managed pages include pages whose view is rendered from PA
manifest data by the shared runtime.

Current adapted pages include:

* Banzuke Changes;
* Standings by Wins;
* Win Probability by Standing;
* Career Length.

These are all public-site pages in practice, but they do not all participate in
the same ownership model yet.

## Target Model

Promoted public pages should follow this model:

```text
analysis producer -> data/config/PA manifest
make_site runtime -> public UI, options, URL state, cache-busting, styling
```

The target distinction should be:

1. external or legacy artefacts that are deliberately embedded or linked as
   opaque pages;
2. real public-site pages rendered by `make_site` from PA manifests.

There should not be a permanent subcategory of real public-site pages that need
page-specific deep-link adapters because they have private UI runtimes.

## Proposed Migration

### 1. Inventory Page Ownership

Create a short inventory of all current `TableAppView`, `StandaloneHtmlView`,
custom inline renderer, and PA-runtime pages.

For each page, record:

* whether the page is intended to be a promoted public page;
* current view type;
* current URL parameters;
* current option controls;
* current data/config source;
* behaviours that must survive migration.

This should make the remaining adapter surface explicit rather than implicit.

### 2. Fill PA Runtime Feature Gaps

Before flipping pages, add the shared runtime features that the adapted pages
currently provide privately.

Likely gaps include:

* sortable tables and sort indicators;
* stable default sort metadata;
* table view modes;
* column and column-group visibility;
* option-sensitive notes;
* note popovers;
* sticky table headers and constrained table scrolling;
* shikona link behaviour;
* Plotly-backed chart and multi-view page support;
* browser-side validation of manifest and data shape;
* uniform URL state handling for options, sort state, and view state.

The behaviour inventory documents should be treated as the checklist for this
step.

### 3. Migrate One Page at a Time

Move pages from bespoke/copy/adapted rendering into the PA-runtime model one at
a time.

Good pilot choices:

* Standings by Wins, if the goal is to exercise sorting, view modes, notes, and
  richer table URL state;
* Banzuke Changes, if the goal is to exercise option-sensitive columns,
  banzuke-shaped table projection, and validation.

For each migrated page:

* keep the existing producer output stable where possible;
* move UI facts into the PA manifest or `make_site` renderer metadata;
* make the shell/runtime own URL restoration and state publication;
* compare the native page against the adapted page before removing the adapter.

### 4. Remove Adapter Modes

When no promoted public page depends on adapters, remove:

* page-specific `postMessage` adapter code from copied apps;
* page-specific inline renderer URL adapters;
* shell special cases for adapter parameter modes;
* any documentation that presents adapters as a target architecture.

After this point, opaque embedded artefacts should remain isolated by default.
If an opaque artefact needs to be promoted, the preferred path is to give it a
PA manifest contract and render it through `make_site`.

## Success Criteria

The proposal is complete when:

* every promoted table/tool page has one declared PA manifest or equivalent
  make_site-owned page contract;
* options are described as page state, not private widget code;
* meaningful page state appears in the browser URL;
* browser back/forward restores selected page and options;
* development cache-busting is infrastructure, not page-local state;
* no promoted public page needs a bespoke deep-link adapter.

## Non-Goals

This proposal does not require every historical HTML artefact to be rewritten.
Some old outputs may remain as reference material, diagnostic pages, or
deliberate external embeds.

This proposal also does not require doing the migration immediately.  The
current adapters are acceptable as temporary scaffolding while the PA runtime
learns the behaviours needed by the existing public pages.

## Related Documents

* `Public UI Grammar.md`
* `PA Manifest Classes.md`
* `Table App Bundle Migration.md`
* `Public Table Behaviour Inventory.md`
* `TBD Register.md`
