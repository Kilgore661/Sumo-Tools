# make_site2 Review Action List

## Status

Consolidated working review/action document for `src/products/make_site2`.

This document records conclusions reached during review of implementation against the active requirements, specification and design documents. It is not itself a replacement specification.

The governing rule for action arising from this review is:

```text
Where a requirement or specification decision is wrong, superseded or over-specific,
correct the documentation first and then review or rebuild the code against the
corrected contract.

Where the contract remains correct and the implementation does not meet it,
change the implementation and test the correction.
```

Scope of this review pass:

```text
1. Deep-site URL and page-output model
2. Clean build output and deployment policy
3. G1/G2 content grammar and deferred richer models
4. Explicit public page status
5. Unknown-page browser behaviour
6. Filter vocabulary: option_value
7. Deferred documentation consolidation and aspirational-specification note
```

---

# 1. Deep-Site URL and Page-Output Model

## Finding

The active documentation describes a hybrid route-page model:

```text
page identity is represented by a canonical route
one real HTML page is generated for each planned public page
query/hash state represents selected filter/view state within that page
```

The current implementation behaves as a deep-linked single-shell static application:

```text
one generated index.html shell
runtime manifest describing pages and artifacts
page identity represented in URL/application state, for example ?page=banzuke_changes
filter/view state represented in the same URL-state mechanism
```

## Conclusion

This is not presently an implementation defect.

The product requirement is that the generated static public site supports reliable deep links which restore:

```text
the selected public page
the material analytical state of that page
```

A requirement to generate one HTML file per public page is a more specific specification/design choice, not an unavoidable consequence of that product requirement.

Fully specified analytical URLs are machine-readable state carriers. They need not be human-readable prose. Unreadability of a deep-state URL is therefore not a useful reason to require route-page HTML.

This conclusion is not justified by the existing implementation. The specification decision has been reconsidered independently and appears over-specific relative to the product requirement.

## Documentation Action

Revise the active specification/design spine so that it requires stable reproducible deep linking without mandating page-per-route HTML output.

The corrected contract should state, in substance:

```text
The generated public site shall provide stable deep-linkable URLs.

A deep link shall identify the selected public page and any material analytical
view state required to reproduce the displayed result.

Page identity and view state may be represented by path segments, query state,
hash state or a combination, provided the mechanism is explicit, stable and
compatible with static deployment.

The generated site may use a single static application shell or multiple route
entry pages unless a later public requirement makes one approach necessary.
```

Documents requiring amendment or review include:

```text
src/products/make_site2/docs/02 Specification.md
src/products/make_site2/docs/05 Rendering Design.md
src/products/make_site2/docs/06 Build and Output Design.md
```

Review consequential route-page assumptions in:

```text
src/products/make_site2/docs/03 Design Overview.md
src/products/make_site2/docs/04 Core Model Design.md
src/products/make_site2/docs/04.1 Site Model Design.md
src/products/make_site2/docs/04.2 Publication Plan Model Design.md
src/products/make_site2/docs/04.3 UI Model Design.md
src/products/make_site2/docs/07 Deployment Design.md
```

`09 Open Issues.md` is handled under item 7 rather than edited piecemeal during this pass.

## Implementation Follow-Up

After correcting the contract, review the single-shell runtime against it. In particular:

```text
unknown or invalid selected-page state must not produce blank content
state restoration must reproduce the intended analytical view reliably
irrelevant state inherited from a previously selected page must not cause
incorrect restored behaviour or misleading deep links
default-state URL policy must be stated and implemented consistently if the
revised contract adopts one
```

These are runtime/deep-link correctness issues within a permissible single-shell model, not reasons in themselves to reject that model.

## Acceptance Criteria

```text
active docs no longer require page-per-route HTML unless that requirement is
explicitly re-affirmed on product grounds

the selected deep-link/output contract is stated clearly

the existing implementation is reviewed against that corrected contract

any runtime URL-state defects identified by that review are fixed or recorded
as explicit remaining actions
```

---

# 2. Clean Build Output and Deployment Policy

## Finding

A full `make_site2` build currently writes into an existing generated output root without first clearing it. Obsolete generated files may therefore survive after pages, assets, data files or runtime outputs are removed from the current build.

## Conclusion

This is an implementation gap.

The required policy distinguishes generated output, local deployment and remote deployment:

| Location / Workflow                                         | Required Policy                                                                                                                                    |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Generated build output tree, e.g. `files/output/make_site2` | Clean before a full build; the tree must exactly represent the current generated site.                                                             |
| Preview server over generated output                        | No separate cleanup step; correctness follows from serving a clean generated build tree.                                                           |
| Local/LAN deployed `sumo-tools2` site root                  | Clean the configured site-specific target before copying the latest build output. Do not clean its parent web root or affect another site/project. |
| Remote deployed `sumo-tools2` tree                          | Create directories as needed and upload/overwrite generated files; automatic deletion of stale remote files is not required.                       |

The remote exception is deliberate. The remote server also supports other projects, and the current remote publication workflow is intentionally non-destructive.

## Documentation Action

The policy is already substantially present in:

```text
06 Build and Output Design.md
07 Deployment Design.md
```

No substantive policy change is required. A clarifying edit may set out the cleanup scopes together:

```text
clean generated build output: required
clean site-specific local/LAN deployment root: required
clean remote deployment root: not required in the current deployment model
```

## Code Action

Update the full-build path in:

```text
src/products/make_site2/build.py
```

A full `build_site()` operation should remove its configured generated output root before writing the new static site, conceptually:

```python
if output_root.exists():
    shutil.rmtree(output_root)
output_root.mkdir(parents=True, exist_ok=True)
```

Preserve the existing deployment distinction in:

```text
src/products/make_site2/deploy.py
```

Specifically:

```text
local deployment cleans the configured local sumo-tools2 site root before copy
remote deployment ensures directories exist and uploads/overwrites files only
```

## Validation

1. Place an obsolete file under the generated build output root.

2. Run a full build.

3. Confirm that the obsolete file no longer exists in generated output.

4. Deploy locally and confirm that the local site-specific target contains only current generated output.

5. Confirm by code/test inspection that remote deployment remains non-destructive and does not issue deletion operations.

## Acceptance Criteria

```text
full build clears the generated output root before writing
local deployment remains clean only within its configured site-specific target
remote deployment remains deliberate upload/overwrite without purge
any clarification required to avoid future confusion is made in the docs
```

---

# 3. G1/G2 Content Grammar and Deferred Richer Models

## Finding

The active specification and principal UI/rendering design documents currently say that `make_site2` supports two ContentPanel grammar shapes:

```text
G1: Single Visible Artefact
G2: Selected Alternative
```

They identify Career Length as the known pressure case for G2 and include G2 coverage in acceptance/replacement expectations.

The implementation supports only G1:

```text
ui_model.py defines only G1
Career Length is represented as a G1 panel with a view filter
runtime/site.js accepts only G1
```

## Conclusion

The implementation is aligned with a later design decision that was not fully propagated through the active documents.

The intended current position is:

```text
G1 is the current implemented ContentPanel grammar.

G1 is deliberately simple and does not fully model nested, hierarchical or
conditionally applicable filter/choice structures.

Some pages reveal pressure for a richer model, but that pressure does not yet
justify increasing the current grammar.

Possible richer models are deferred to Appendix A.
```

This is therefore a documentation-consolidation gap, not a current requirement to implement G2.

## Design Rationale to Capture

The corrected documents should explain, in substance:

```text
G1 models a ContentPanel with one visible PA, optionally controlled by a flat
FilterSection and accompanied by relevant Notes.

This is not the only possible way to model a ContentPanel. In particular, it
does not accommodate nested or hierarchical filter/choice ownership.

The current navigation tree is mostly adequately served by G1, so make_site2
keeps the current grammar simple for now.

There are pressure cases where the flat model permits an awkward display or an
awkward valid state. For example, in Win Probability by Standing, Source =
Equelo together with Error bars = true is permitted even though error-bar
evidence belongs to the Observed source rather than Equelo.

Career Length likewise exposes possible pressure for a richer artifact/view
model.

Those richer models are deferred. See Appendix A.
```

## Documentation Action

Remove G2 as an active requirement or current implemented grammar from:

```text
src/products/make_site2/docs/02 Specification.md
src/products/make_site2/docs/04.3 UI Model Design.md
src/products/make_site2/docs/05 Rendering Design.md
```

Edits should include:

```text
remove the requirement that make_site2 support at least two grammar shapes
remove G2 / Selected Alternative as a current specification contract
remove BranchSelector and Branch from current required UI vocabulary
remove Career Length as a required G2 implementation case
remove acceptance criteria requiring a G2 selected-alternative page
remove rendering obligations for G2 as current functionality
replace them with the G1 limitation/deferred-model explanation
refer clearly to A Appendix - Better Models.md
```

Review other active documents for stale references to current G2 support, excluding `09 Open Issues.md` until item 7:

```text
src/products/make_site2/docs/03 Design Overview.md
src/products/make_site2/docs/04 Core Model Design.md
src/products/make_site2/docs/04.1 Site Model Design.md
src/products/make_site2/docs/04.2 Publication Plan Model Design.md
src/products/make_site2/docs/04.4 Artifact Model Design.md
src/products/make_site2/docs/06 Build and Output Design.md
src/products/make_site2/docs/07 Deployment Design.md
src/products/make_site2/docs/08 Producer Integration and Migration.md
```

## Appendix Position to Preserve

Appendix A is deferred model discussion, not a second active specification. It should continue to make clear that:

```text
richer Artifact/View or structured-filter models are possible
Career Length and conditional-control applicability are useful pressure cases
the current implementation is not to be rewritten around those models now
a richer model should be promoted into the active specification only when real
public-page pressure justifies it
```

## Code Action

No G2-related code change is presently required.

## Acceptance Criteria

```text
G1 is stated consistently as the current ContentPanel grammar
G2 is no longer presented as current required functionality
Career Length is no longer required as a G2 example or acceptance case
Appendix A is referenced as the deferred location for richer-model pressure
the implementation is not treated as deficient merely for being G1-only
```

---

# 4. Explicit Public Page Status

## Finding

The specification requires explicit public-status control so that content is not published merely because it exists or is browser-readable.

The implementation defines the status vocabulary, but `PageDefinition.status` defaults to `PROMOTED` and the active pages omit `status=`. Consequently, adding an active page declaration without considering status silently makes it publicly included by default.

## Conclusion

This is an implementation correction. Publication status should be an explicit decision at each active page declaration.

## Code Action

Update the active page declarations in:

```text
src/products/make_site2/site_definition.py
```

to include an explicit `status=` for every page.

Also update the model in:

```text
src/products/make_site2/models.py
```

so that `PageDefinition.status` is required rather than defaulting to `PageStatus.PROMOTED`, unless a deliberate later decision establishes a safe reason for an implicit default.

Preferred form:

```python
status: PageStatus
```

rather than:

```python
status: PageStatus = PageStatus.PROMOTED
```

This ensures omission is detected during construction rather than resulting in accidental public inclusion.

## Documentation Action

No change of requirement is presently indicated. During implementation, check whether any active design example constructs `PageDefinition` without explicit status and update those examples if necessary.

## Validation

```text
all active PageDefinition declarations specify status explicitly
constructing a PageDefinition without status fails
build/publication planning includes only pages whose explicitly declared status
is included by the selected build policy
```

## Acceptance Criteria

```text
no active page becomes promoted solely because status was omitted
status remains an explicit publication/curation decision
```

---

# 5. Unknown-Page Browser Behaviour

## Finding

When browser URL/application state selects a page id for which no content panel exists, the current runtime clears the content region and returns. This can leave the user looking at blank content with no explanation.

Unknown-page conditions may be rare in ordinary use, but can arise through stale links, edited URLs, invalid restored state or later removal/renaming of a page.

## Conclusion

This is an implementation correction.

The existing rendering design already permits simple browser-side error reporting using `alert()` for the initial implementation. At minimum, the runtime should give an informative error instead of silently rendering blank content.

## Code Action

Update:

```text
src/products/make_site2/runtime/site.js
```

When the selected page is unknown, the runtime should:

```text
show an informative alert() message identifying that the requested page cannot
be displayed

fall back predictably, preferably by clearing/removing invalid page selection
state and rendering the landing panel
```

Suggested user-facing intent, not mandatory wording:

```text
The requested page is not available in this site build. Showing the site home page instead.
```

## Documentation Action

No substantive documentation change is required because simple browser-side reporting is already part of the current rendering design. Update a doc only if implementation reveals ambiguity about fallback behaviour.

## Validation

```text
open the application with an unknown page id in URL state
confirm an informative alert is produced
confirm the content does not remain blank
confirm the application returns to a predictable valid display/state
```

## Acceptance Criteria

```text
unknown selected-page state is reported clearly
blank unexplained ContentPanel output is avoided
fallback behaviour is predictable and testable
```

---

# 6. Filter Vocabulary: `option_value`

## Finding

The current model/documentation uses `Filter`, not `Option`, as the formal term for reader-visible analytical selection state.

`SelectedTableDataSource` nevertheless uses the field name:

```python
option_value: str
```

For the standings artefact, the field means: use this source when a particular Filter has this selected value.

## Conclusion

This is a small implementation terminology correction, not a model redesign.

The appropriate term is:

```python
filter_value: str
```

This keeps the implementation-facing vocabulary consistent with the current model and directly describes the relationship between the data source and its selecting Filter.

## Code Action

Rename:

```python
SelectedTableDataSource.option_value
```

to:

```python
SelectedTableDataSource.filter_value
```

Update corresponding construction, serialization, browser-runtime lookup and tests wherever the serialized/runtime field is consumed.

Likely affected areas include:

```text
src/products/make_site2/artifact_model.py
src/products/make_site2/site_manifest.py
src/products/make_site2/runtime/site.js
relevant tests, if present
```

## Documentation Action

No specification change is required. Check active documentation and examples for any residual formal use of `Option` and remove it where it denotes the model concept rather than ordinary informal English.

## Validation

```text
search the active make_site2 code/runtime for option_value and confirm it no
longer exists

build/serialize the runtime manifest and confirm the new field is used

open the standings page and confirm selecting a basho-window Filter still loads
the correct source data
```

## Acceptance Criteria

```text
formal implementation vocabulary is consistent with Filter terminology
standings data-source selection behaviour is unchanged after the rename
```

---

# 7. Deferred Documentation Consolidation and Aspirational-Specification Note

## Finding

`09 Open Issues.md` is expected to contain stale items and unresolved wording while this review and the resulting corrections are in progress.

Separately, the review exposed a wider design principle about the role of an aspirational specification and the practical boundary between modelling semantic distinctions and ordinarily rendering already-modelled leaf values. A draft note capturing this learning has been retained in the current docs folder, but the decision about how it belongs in the canonical documentation set remains open.

## Conclusion

Do not tidy `09 Open Issues.md` incrementally during the current correction work. It should be reconciled after the documentation and implementation actions from this review are complete and verified.

The retained aspirational-specification note should also be considered during that final documentation consolidation. Whether it becomes a canonical design section, a maintained supplementary note, or is folded into an existing design document is a TBD decision for that stage.

## Deferred Documentation Action

After items 1–6 have been implemented and tested:

```text
update 09 Open Issues.md so that it distinguishes:
  resolved decisions
  completed fixes
  remaining open questions
  deferred future model work
  any further implementation actions

review the retained Aspirational Specifications / Practical Model Boundaries note
and decide whether and how it should be folded into the canonical project docs
```

The consolidation should preserve this learned principle in an appropriate form:

```text
make_site2 is model-led, not model-maximal.

Model a distinction when it changes public meaning, ownership, valid
composition, validation, runtime contract or public interpretation.

Use ordinary rendering and shared presentation policy once the remaining work
is simply to display an already-modelled entity or leaf value.
```

## Code Action

None directly arising from item 7.

## Acceptance Criteria

```text
09 Open Issues.md accurately represents the post-review state rather than the
intermediate development history

the retained aspirational-specification learning is deliberately classified and
incorporated or retained in a suitable documentation location
```

---

# Action Summary

| Item                                               | Classification                                                       | Documentation Action                                                                                             | Code Action                                                                                            |
| -------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1. Deep-site URL / page-output model               | Specification/design decision to correct and consolidate             | Replace mandatory route-page HTML rule with stable deep-link/output contract; review dependent route assumptions | Review single-shell runtime against corrected contract; implement any resulting state/error fixes      |
| 2. Clean build output / deployment                 | Implementation gap; deployment policy already substantially correct  | Optional clarification of cleanup scopes                                                                         | Clear generated output root before full build; preserve clean-local/non-destructive-remote distinction |
| 3. G1/G2 grammar                                   | Documentation consolidation gap after deferred richer-model decision | Remove active G2 requirements; state G1 limitation and Appendix A deferral                                       | No G2 implementation required at present                                                               |
| 4. Explicit public page status                     | Implementation correction                                            | Update examples only if required                                                                                 | Make status explicit for each active page; remove implicit `PROMOTED` default                          |
| 5. Unknown-page browser behaviour                  | Implementation correction                                            | None presently required                                                                                          | Informative `alert()` and predictable valid fallback                                                   |
| 6. `option_value` terminology                      | Small implementation terminology correction                          | Remove residual formal `Option` usage if found                                                                   | Rename to `filter_value` through model/manifest/runtime/tests                                          |
| 7. Open-issues and aspirational-note consolidation | Deferred documentation task                                          | Reconcile `09 Open Issues.md` after fixes; decide canonical treatment of retained note                           | None directly                                                                                          |

---

# Implementation Sequence

## Phase 1: Correct Active Documentation

```text
Item 1:
  revise the deep-site URL/page-output contract

Item 3:
  remove current G2 obligations and capture G1 limitation/Appendix A deferral
```

During these edits, update dependent documents identified above, excluding final tidy of `09 Open Issues.md`.

## Phase 2: Correct Implementation

```text
Item 2:
  clean generated output root before a full build

Item 4:
  require explicit page status declarations

Item 5:
  handle unknown-page browser state informatively and predictably

Item 6:
  rename option_value to filter_value consistently
```

## Phase 3: Test and Re-Review

```text
run relevant tests and/or add focused tests for corrected behaviours
perform a local build and local preview/deployment verification
re-review the modified implementation against the amended active documentation
```

## Phase 4: Consolidate Deferred Documentation

```text
update 09 Open Issues.md to reflect resolved and remaining work
review the retained aspirational-specification note and decide how it belongs in
the canonical project documentation set
```


