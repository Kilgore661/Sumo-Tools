## `make_site2` code/doc comparison — `dev` branch

`make_site2` is present on **`dev`**, at `src/products/make_site2/`; it is not present on `main`. I compared its active code against its adjacent active documentation, excluding `src/products/old/make_site`.

This is a static review of repository contents; I have not executed the build.

### Overall assessment

The code implements a substantial static-site prototype: site/page declarations, navigation, artifact definitions, runtime rendering, data staging, and deployment. However, it has moved beyond the documented “first slice” while leaving several core I thcontracts either unimplemented or contradicted by the implementation.

| Severity | Finding                                                                                                | Code/doc relationship                                   |
| -------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| High     | Canonical route pages are not actually generated                                                       | Code contradicts build/output design                    |
| High     | Output root is not cleaned before builds                                                               | Code contradicts build/output design                    |
| High     | `G2` selected-alternative grammar is absent; Career Length is implemented as `G1`                      | Code contradicts specification                          |
| Medium   | All declared pages are implicitly promoted                                                             | Code weakens explicit curation/status contract          |
| Medium   | Unknown page state can render blank content                                                            | Code contradicts explicit error-state contract          |
| Medium   | `option_value` remains in implementation vocabulary                                                    | Code contradicts vocabulary decision                    |
| Medium   | Documentation still describes unsettled/first-slice work after implementation expanded to twelve pages | Documentation is stale                                  |
| Medium   | Site/page model does not yet carry several fields required by the specification                        | Implementation is incomplete relative to model contract |

---

## 1. Canonical static routes are declared, but not built

The documentation states that each canonical route should be written as a real static `index.html` page, such as `/current/basho-results/index.html`. 

The code derives route-shaped hrefs in `routes.py`, for example `.../index.html`. 

But `build.py` writes only:

* `<output_root>/index.html`
* `<output_root>/runtime/site-manifest.json`
* runtime CSS and JavaScript
* data files

It does **not** write HTML pages for each canonical route. 

Instead, `site.js` intercepts navigation clicks and represents the selected page through a query parameter such as `?page=basho_results_browser`. 

### Consequence

The public route model and the delivered site behaviour disagree. A copied/opened navigation href such as a canonical route directory is not backed by a generated HTML file, while the live application state is actually query-string based.

### Likely fix

Choose one route model and make all layers agree:

* Generate real route `index.html` files and have runtime bootstrap from the route; or
* Revise the docs/specification to describe a single-shell query-driven site.

The current hybrid is misleading and brittle.

---

## 2. The documented clean-build policy is not implemented

The build/output design says:

> The output root is cleared before each build.

Its rationale is to prevent stale pages, assets, routes, or data files remaining after removal. 

`build_site()` does not clear `output_root`; it only creates directories and overwrites selected files. Certain page data directories are individually removed and recreated, but obsolete files elsewhere in the output tree can survive across builds.  

### Consequence

A deployment can contain stale public files that are no longer represented by the current site definition or runtime manifest.

### Likely fix

Clear the output root at the beginning of a full build, or explicitly revise the documentation to specify incremental-build semantics and implement stale-file tracking.

---

## 3. The specification requires `G2`; the implementation supports only `G1`

The specification requires two content grammar shapes:

* `G1`: one visible artefact
* `G2`: selected alternative branches

It explicitly identifies **Career Length** as the known pressure case for `G2`. 

However, `ui_model.py` defines:

```python
ContentGrammar = Literal["G1"]
```

There is no `G2`, `BranchSelector`, or `Branch` model. 

`site_manifest.py` constructs the Career Length page as a `G1` panel with a `view` filter selecting among distribution, PMF, CDF, survival, and longest-careers content. 

`site.js` further enforces this limitation by rejecting any grammar other than `G1`. 

### Consequence

The implementation has encoded the known multi-view pressure case as a filter-driven special artifact instead of implementing the documented grammar boundary. Either the design decision changed, or the model has drifted.

### Likely fix

Decide whether Career Length is truly:

* a single artifact with representation filters; or
* a `G2` page selecting between alternative branches.

Then update either the implementation or the specification and design documents consistently.

---

## 4. Curation exists as an enum, but pages are implicitly promoted

The requirements and specification emphasise explicit public status and prevention of accidental publication. Page candidates are expected to carry statuses such as `promoted`, `candidate`, `research`, `diagnostic`, `legacy`, `superseded`, and `excluded`.  

The implementation does define this complete `PageStatus` enum. However:

* `PageDefinition.status` defaults to `PROMOTED`.
* Every page in `site_definition.py` omits an explicit status.
* The publication plan includes promoted pages by default.
* The runtime shell creates panels for all twelve declared pages.    

### Consequence

The code technically supports status, but the active site declaration effectively says “everything is public” by omission. That undermines the specification’s curation principle.

### Likely fix

Require `status=` explicitly in every `PageDefinition`, at least for the active site registry, and consider rejecting omitted status in production declarations.

---

## 5. Unknown-page behaviour does not meet the explicit error-state contract

The specification identifies unknown routes and missing required content as conditions that must be handled explicitly; a public page should not silently render blank space when necessary material is unavailable. 

In `site.js`, when the selected page id does not resolve to a panel, the code performs:

```javascript
contentPanel.replaceChildren();
return;
```

That produces an empty content region without a user-facing explanation. 

### Consequence

Malformed shared URLs or stale links can produce a blank interface rather than a controlled “page not found” or “content unavailable” state.

### Likely fix

Render an explicit not-found/error panel and normalise or remove invalid URL state.

---

## 6. The banned `Option` vocabulary remains in code

The specification says that **Filter**, not **Option**, is the public and implementation-facing model term; it expressly states that `Option` is not part of the `make_site2` model vocabulary. 

But `artifact_model.py` defines:

```python
class SelectedTableDataSource:
    option_value: str
```

and `site_manifest.py` populates that field for standings sources.  

### Consequence

This is a direct naming-contract violation, albeit a straightforward one.

### Likely fix

Rename `option_value` to something aligned with the filter model, such as `filter_value`, `selector_value`, or `window_value`.

---

## 7. The active documentation is stale relative to the implemented scope

`09 Open Issues.md` still describes BRB/Basho Results as the leading first vertical slice and treats several implementation choices as unresolved, including output-tree defaults, runtime bootstrap shape, deployment targets, and runtime boundaries. 

But the implementation already includes:

* twelve page definitions;
* multiple chart/table artifact types;
* runtime manifest generation;
* concrete local and remote deployment defaults;
* concrete output directories;
* concrete runtime URL-state behaviour.    

### Consequence

A maintainer reading the docs cannot reliably tell which architectural decisions are still open and which have already been implemented.

### Likely fix

Update `09 Open Issues.md` to distinguish:

* implemented decisions needing documentation;
* remaining genuine design questions;
* intentional deviations from the earlier specification.

---

## 8. The declared model is narrower than the specification requires

The specification says a site definition should declare global assets and build defaults, and a page definition should include data dependencies, asset dependencies, producer site-facing input references, and filter/default state where applicable. 

The current Python model provides:

* `SiteDefinition`: `id`, `title`, `navigation`, `pages`
* `PageDefinition`: `id`, `title`, `summary`, `artifact`, `status`, `data`

Filters, artefact details, source data paths, and runtime structure are instead hard-coded separately in `site_manifest.py`.  

### Consequence

The public-site declaration is not yet the complete authoritative structure described by the specification. Meaning is split between `site_definition.py` and an extensive manually coordinated manifest module.

### Likely fix

Either expand the declared model so pages connect explicitly to filters/assets/site-facing inputs, or revise the documentation to make `site_manifest.py` an intentional authoritative composition layer.

---

## Positive alignment

Several important pieces do align with the documentation:

* `PageStatus` includes the documented status vocabulary. 
* Routes are derived from navigation placement rather than producer filenames. 
* The implementation uses `Filter` consistently in the UI model itself. 
* Artifact renderers are represented separately from page shell/navigation structure.
* The build creates a static output tree and copies runtime/data assets rather than requiring a live Python server. 
* Build and deployment are implemented as separate concerns.  

## Recommended order of work

1. Resolve the route/output contradiction: real static route pages versus query-driven single shell.
2. Implement clean-build behaviour.
3. Decide whether Career Length requires `G2` or whether the specification should be revised.
4. Make page status explicit in `site_definition.py`.
5. Add visible invalid-route/error handling.
6. Remove `option_value` terminology.
7. Refresh the active documentation to reflect the implemented twelve-page state.
