# Table App Bundle Migration

## Status

Working migration note, created 2026-05-09.

Updated 2026-05-14: this note remains useful for the two original standalone
table apps, but the broader target is now recorded in
`Remove Adapter Layer Proposal.md`.  The long-term aim is to remove the
distinction between copied/adapted public table apps and PA-runtime-managed
public pages.

This records the decision to stop treating the current table apps as final
standalone browser applications.  The analysis modules remain producers.  The
public UI should move into `make_site`.

Current terminology note: the files currently named `page_bundle.json` are the
first PA manifests for these pages.  Future schema/file names should prefer
manifest language.

## Decision

The promoted public-site model is:

```text
analysis module -> data/config/PA-manifest writer
make_site       -> public page rendering, shared JS, URL state, table behaviour
```

The two current standalone browser apps are:

* Standings by Wins;
* Banzuke Changes.

They are no longer target deployment modes for promoted public pages.  Their
current HTML/CSS/JS app shells may remain temporarily as reference material and
for comparison during migration, but they should not be the long-term public
integration contract.

## Current Producer Outputs

### Standings by Wins

Current producer-owned outputs:

* `site_config.json`;
* one CSV per supported window size;
* one JSON sidecar per supported window size;
* `page_bundle.json` as the first make_site-facing PA manifest.

Current UI facts still partly hardcoded in the old app shell/JS:

* view modes: standard, percentages, combined;
* option rendering;
* column headers and groups;
* sort ids and default sort;
* notes and note visibility;
* URL parameter names;
* shikona link behaviour;
* table rendering and formatting.

### Banzuke Changes

Current producer-owned outputs:

* `site_config.json`;
* `data/banzuke_change_report.csv`;
* `page_bundle.json` as the first make_site-facing PA manifest.

Current UI facts still partly hardcoded in the old app shell/JS:

* banzuke-style and one-column rendering templates;
* option rendering;
* column groups and visibility rules;
* notes and note visibility;
* URL parameter names;
* shikona link behaviour;
* delta direction/value formatting;
* table rendering and formatting.

## First PA Manifest Contract

Both producers now write:

```text
page_bundle.json
```

The initial schema id is:

```text
sumo-tools.table-page-bundle.v0
```

This is deliberately provisional.  Its job is to move public-page facts out of
HTML/JS and into producer-owned metadata so that `make_site` can later render
the pages natively.

The manifest currently records:

* page id, title, summary, and status;
* producer module and legacy app shell path;
* the fact that `make_site` is the public UI owner;
* view/table shape;
* data file references;
* options and defaults;
* columns and note links;
* notes;
* expected shared behaviours.

## Migration Order

1. Keep the old app shells working while manifest metadata matures.
2. Teach `make_site` to consume one manifest natively.
3. Migrate the easier or more valuable pilot page first.
4. Extract shared JS only after the native renderer has a clear contract.
5. Retire standalone app deployment paths once the native page matches the old
   app's useful behaviour.

Standings is the better pilot if the goal is to exercise sorting, URL state,
view modes, and shared table behaviour.  Banzuke Changes is the better pilot if
the goal is to exercise option-sensitive columns and banzuke-specific layout.

## Related Cleanup

The publishers previously depended on a hardcoded legacy v9 `full_shiks.pkl`
path for graph-link shikona.  The current code now points at the checked-in
copy under `src/analysis/standings/files/full_shiks.pkl`.

This is still not the final identity/linking solution.  The broader site-wide
task remains: generate or maintain qualified shikona inside Sumo-Tools through
a shared identity/linking service.

The Standings publisher also still tries to deploy to an old local
`A:/local/html/standings` path as part of `main()`.  Bundle writing succeeded,
but that deploy step failed in the current environment because the drive does
not exist.  Producer generation and deployment should be separated as a later
cleanup.
