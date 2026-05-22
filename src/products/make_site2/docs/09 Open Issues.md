# 09 Open Issues

## Status

Current open-issues register for `make_site2`, revised after the first implementation review and resulting documentation/code corrections.

This document records unresolved decisions, deliberately deferred design work, and future implementation pressure points.

It is not a second design notebook and it is not a history of completed implementation work.

---

# 1. Purpose

An issue belongs here when:

```text
the project has identified a real remaining question or deferred action
the answer is not yet settled, or implementation/consolidation remains outstanding
the item matters to future development or maintenance
```

A settled decision should normally be removed once it has been reflected in the relevant requirements, specification, design or implementation material.

A short settled-decision record may remain here temporarily where it prevents a superseded design question from being reintroduced.

---

# 2. Issue Statuses

Use these statuses when maintaining this file:

```text
Open
  Known issue with no settled answer yet.

Decided
  Decision made, but documentation, implementation or consolidation remains.

In progress
  Active implementation or design work is underway.

Blocked
  Cannot proceed until another issue is resolved.

Done
  Completed and ready to remove during the next documentation tidy.

Deferred
  Deliberately postponed until real pressure or a later consolidation stage.
```

Default assumption: if an issue appears here without an explicit status, it is **Open**.

---

# 3. Decisions Settled During the First Implementation Review

This section is retained briefly to prevent superseded questions from returning as apparent open issues. These matters should be removed from this file once the revised design/code baseline is comfortably established.

## 3.1 Deep Links and Static Output Shape

Status: **Done**.

Decision and implementation position:

```text
The public-site requirement is stable deep linking that restores the selected
public page and material analytical state.

The requirement does not mandate one HTML file per public page.

The current implementation uses a static application shell with URL state for
selected page and analytical state. This is compatible with the requirement.
```

Verified follow-up:

```text
unknown selected page state reports an informative error and falls back
invalid finite filter values fall back to defaults
switching pages does not retain irrelevant previous-page filter state
```

## 3.2 Current Content Grammar

Status: **Done**.

Decision:

```text
G1 is the active ContentPanel grammar.

Richer nested/filter-ownership or Artifact/View models are deferred to
A Appendix - Better Models.md.

Career Length is not a required G2 implementation case.
```

## 3.3 Generated Output Cleaning and Deployment Boundary

Status: **Done**.

Decision and implementation position:

```text
A full build clears the contents of the generated build-output root in place.

Local/LAN deployment may clean the configured site-specific local target.

Remote deployment creates/uploads/overwrites and does not automatically purge
stale remote files.
```

The in-place output cleaning avoids requiring removal of the output-root directory itself on Windows.

## 3.4 Explicit Page Status, Unknown Page Handling and Filter Vocabulary

Status: **Done**.

Implemented and checked:

```text
active PageDefinition declarations state status explicitly
unknown selected-page state is reported and falls back predictably
filter_value is used as the implementation field name instead of option_value
```

Terminology clarification:

```text
Filter is the formal model and implementation vocabulary for reader-selectable
analytical state.

Human-facing UI text may use ordinary wording such as "Options".
```

---

# 4. Status and Inclusion Policy

## 4.1 Status Vocabulary

Status: **Open**.

Current vocabulary is:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

Decision needed:

```text
Is this the long-term vocabulary?
Are any statuses redundant?
Is a separate development-only status required?
```

## 4.2 Inclusion by Build Mode

Status: **Open**.

Current direction:

```text
promoted:
  included in ordinary public builds

candidate / research / diagnostic / legacy:
  included only where a build mode or explicit public decision requests them

superseded / excluded:
  excluded by default
```

Decision needed:

```text
What named build modes are supported?
What is the exact status-inclusion policy for each?
How are non-promoted inclusions marked in a rendered development build?
```

---

# 5. Deep-Link Policy and Home Selection

## 5.1 Published URL Compatibility

Status: **Open for future public-compatibility policy**.

The current selected-page/view representation is acceptable and implemented. What remains open is when published URLs become stable enough that later changes require compatibility handling.

Questions:

```text
When does a deep-link shape become public/stable?
Do early development links need compatibility treatment?
If a page id or filter id changes after publication, what compatibility mechanism
is required?
```

## 5.2 Home / Landing Selection

Status: **Open**.

The runtime has a valid landing/fallback state. The model-level treatment remains to be settled if it becomes important.

Questions:

```text
Should home/landing be a normal PageDefinition selected by HomePageId?
Should it be generated from navigation/quick links?
Is the current landing-only treatment sufficient for the public site?
```

---

# 6. Quick Links

Status: **Open**.

Quick links are accepted as potentially useful casual-reader shortcuts into the canonical subject-led navigation structure.

Questions:

```text
Are quick links required?
Where are they rendered: Sidebar, landing page, or both?
What are the initial quick links?
```

Candidate subjects:

```text
Basho Results
Standings
Banzuke Changes
```

Quick links must select existing public pages; they do not define a second information architecture.

---

# 7. Producer Orchestration and Site-Facing Inputs

## 7.1 Producer Orchestration API

Status: **Open as future cleanup/evolution**.

`make_site2` already consumes producer-backed site material. The remaining question is whether producer invocation needs a more formal API as the product grows.

Possible future forms:

```text
producer prepare functions
a producer registry
a small orchestration module
command-line subprocess integration
```

Current direction:

```text
keep orchestration simple until repeated producer integration pressure justifies
a formal API
```

## 7.2 Site-Facing Input Representation

Status: **Open as a generalisation question**.

Current implementation demonstrates concrete artifact/data representations. It remains open whether the project needs a more explicit stable general handoff format across producers.

Possible representations:

```text
Python objects
generated JSON-like structures
CSV/data files consumed by Python or JavaScript
a mixed contract appropriate to Artifact kind
```

The former first-class `PA Manifest` concept remains superseded unless later implementation pressure deliberately reintroduces a manifest as a serialization/handoff format.

---

# 8. ThemeConfig and LayoutConfig

Status: **Open**.

Rendering design identifies the need for centrally managed theme/layout policy.

Questions:

```text
Should ThemeConfig/LayoutConfig/RuntimeConfig become formal code structures?
Where should configuration live?
How are CSS custom properties or equivalent tokens generated?
Which current styling values should become shared tokens first?
```

Goal:

```text
edit centralized presentation policy
  -> rebuild
  -> deploy/preview locally
  -> inspect in browser
  -> adjust
```

Do not turn this into page-specific styling work.

---

# 9. Runtime Bootstrap / Manifest and URL-State Evolution

## 9.1 Runtime Manifest Shape

Status: **Open for future refinement**.

The current single-shell runtime already uses serialized page/artifact/runtime information. Remaining questions concern its long-term contract:

```text
What is the intended stable manifest/bootstrap schema?
Should schema/version metadata be emitted?
How much should remain implementation-local rather than contractual?
```

The manifest/bootstrap data must continue to realize the declared UI/Artifact model rather than become a second hidden public model.

## 9.2 URL-State Policy Beyond Current Fixes

Status: **Open for policy refinement**.

Current behaviour has been corrected for unknown pages, invalid finite filter values and stale filter state during page switching.

Remaining policy questions:

```text
Are all material non-default Filter states shareable?
Should defaults always be omitted or is omission implementation discretion?
Does any ordinary table sort or chart interaction ever become public URL state?
Should invalid values be visibly reported or silently defaulted in all cases?
```

---

# 10. Output Tree, Build Metadata and Cache Policy

## 10.1 Output Tree Conventions

Status: **Open for standardisation**.

The current generated site is a valid static application output tree. Remaining questions concern naming and long-term conventions:

```text
Exact output-root default
runtime/assets/data folder naming
whether to generate a sitemap or route/state index
whether any future static entry aliases are useful
```

No open issue remains about requiring page-per-route HTML.

## 10.2 Build Metadata

Status: **Open**.

Questions:

```text
Should build metadata be emitted?
Exact filename and schema?
Include git branch/commit?
Include build mode?
Include page count/runtime identity?
```

Candidate location:

```text
build/build-info.json
```

## 10.3 Cache Policy

Status: **Open**.

Current direction:

```text
development cache-busting is sufficient for now
production cache policy is deferred
```

Questions:

```text
Asset URL query token or content-stamped filenames?
Data URL cache busting?
How should runtime/manifest updates be invalidated in production?
```

---

# 11. Deployment Commands and Future Remote Sync

## 11.1 CLI Vocabulary

Status: **Open**.

The word `build` can mean different stages of the wider project pipeline:

```text
rebuild analytical world from raw/source inputs
prepare site-facing producer outputs
assemble the static site
deploy completed output
preview an existing output tree
```

`make_site2` should not suggest that its ordinary CLI rebuilds the entire analytical world from source.

Possible vocabulary:

```text
produce
assemble
deploy
preview
```

Questions:

```text
Should current CLI flags be renamed before becoming public/stable?
Should no-build deployment be named deploy-existing?
Should producer preparation and site assembly be separately invokable?
```

## 11.2 Remote Deployment / Future Sync

Status: **Open for future improvement**.

Current accepted behaviour is settled:

```text
ensure directories exist
upload/overwrite files
do not delete stale remote files automatically
manual remote purge is acceptable
```

Future questions:

```text
Will a sync tool eventually replace make_site2 remote upload?
Should any deliberately scoped remote-clean option ever exist?
What upload/synchronisation mechanism should be preferred long-term?
```

---

# 12. Notes, Artifact Metadata and Runtime Boundaries

## 12.1 Note Targeting

Status: **Open**.

Notes are general and belong to PAs or visible Artifact features, not Filters.

Questions:

```text
How are note targets represented as more pages need them?
How much target taxonomy is required?
How are relevance updates represented in runtime data?
Are PA-level notes sufficient for most current cases?
```

Possible targets:

```text
PA
table column
column group
chart trace
chart source
data source
prose section
visible Artifact feature
```

Do not invent a large taxonomy before real examples require it.

## 12.2 Artifact Metadata Extension

Status: **Open as driven by future pages**.

Current Artifact kinds include:

```text
table
indexed_table
chart
sectioned_table
prose
custom_artifact
```

Future questions:

```text
What further table/chart semantic metadata is required?
Does sectioned-table structure need refinement?
What prose representation is sufficient?
How should custom Artifact renderer registration mature?
```

Decision should remain evidence-driven.

## 12.3 Richer Filter / Artifact-View Model

Status: **Deferred**.

Pressure cases remain documented in Appendix A, including conditional control applicability and richer Artifact/View relationships.

Current decision:

```text
retain flat G1 unless a real promoted-page problem justifies an active model
change
```

Promotion criteria should include one or more of:

```text
users are materially misled by states permitted under the flat model
Notes/provenance cannot be owned honestly
renderers accumulate repeated unexplained conditional structure
one visible PA no longer accurately describes the page
```

---

# 13. JavaScript Runtime and Browser Error Presentation

## 13.1 Runtime Boundaries

Status: **Open for future refactoring pressure**.

Current principle:

```text
shared runtime owns declared URL state, common Filters, common rendering
behaviour and page selection

Artifact runtimes own Artifact internals
```

Questions:

```text
When should JavaScript be split into modules?
How is Artifact renderer dispatch best represented long-term?
How generic should table/chart behaviour become?
```

## 13.2 Browser Error Presentation

Status: **Open for future UX improvement**.

Current minimum behaviour is settled and implemented:

```text
invalid selected-page state produces an informative alert and safe fallback
```

Future question:

```text
Should inline error presentation eventually replace or supplement alert()?
```

---

# 14. Documentation Consolidation

## 14.1 Aspirational Specification and Rendering Audit

Status: **Decided / deferred documentation consolidation**.

Decision already reached:

```text
make_site2 is model-led but not model-maximal.

The formal model should represent distinctions that affect public meaning,
ownership, valid composition, validation or runtime/rendering contract.

It need not formalise ordinary presentation of already-modelled leaf values.

05.1 Rendering Grammar Audit How To.md complements this principle by providing
the audit method for distinguishing concrete model ownership, acceptable virtual
ownership, browser defaults, genuine custom Artifact behaviour and unjustified
bespoke implementation.

Human-facing UI text may use ordinary wording such as "Options". The ban on
Option/option applies when naming formal model or implementation
representations of the Filter concept, not to all visible copy.
```

Deferred action:

```text
Decide whether On Aspirational Specifications.md should remain a standalone
canonical design note or be folded into an existing canonical design document,
while preserving its relationship to 05.1 Rendering Grammar Audit How To.md.
```

## 14.2 General Documentation Hygiene

Status: **Open / ongoing**.

Tasks:

```text
Add or update docs index / README if needed.
Standardize BuildOutput terminology.
Keep deferred questions centralized here.
Remove completed items from this file once they no longer prevent regression.
```

---

# 15. Future Analytical Ideas

Status: **Open / unassessed**.

Recorded idea:

```text
Chii versus Elo before and after/during
```

This is an analytical/product idea, not currently a `make_site2` design issue. It should be promoted into page/design work only after its public purpose and producer requirements are considered.

---

# 16. Current Priority View

Current likely priorities after the completed first review pass:

```text
P0:
  confirm and maintain a stable post-review baseline
  decide next public-page/product work

P1:
  status/build-mode inclusion policy
  runtime manifest/bootstrap contract refinement, if needed
  ThemeConfig/LayoutConfig centralisation
  notes/Artifact metadata only where real page pressure demands it

P2:
  remote sync improvement
  production cache policy
  deep-link compatibility policy once URLs are publicly stable
  richer structured Filter/Artifact-view modelling if promoted from Appendix A
```

This priority view should be revised as the next real product task is selected.

---

# 17. Summary

The first implementation review pass has settled and verified the major drift identified between documentation and code:

```text
stable deep-linked static application output is permitted
G1 is the active current grammar
generated output is cleaned safely in place
page status is explicit
unknown-page and invalid/stale URL-state behaviour is controlled
formal filter_value terminology is aligned
```

Remaining issues concern policy maturation, future extension and documentation consolidation rather than immediate correction of the completed review findings.

Do not let this file become a second design notebook.
