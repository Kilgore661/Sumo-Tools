# 10 Open Issues and Deferred Design

## Status

Draft register of unresolved decisions, deferred design work and known pressure
points for `src/products/make_site2`.

This document is not a competing specification or a second design notebook. The
active Requirements, Specification and Design documents define the current
product. This document records matters that those documents deliberately leave
open, or implementation work required to bring the product into conformity with
them.

---

## 1. Purpose

An item belongs in this document when:

- a real design, policy or implementation question has been identified;
- the answer is not yet agreed, or implementation/consolidation remains to be
  done;
- leaving it unrecorded would risk accidental decision by local code or later
  confusion;
- the issue is broader than a single rendering audit/change entry, or needs to
  be visible in the project-wide design register.

A settled rule belongs in the owning active document, not permanently here.
Where a settled rule has implementation work outstanding, this document may
retain a short action item until the implementation and audit work are complete.

Rendering-specific provisional matters should be recorded first in:

```text
06 Rendering Audit and Changes.md
```

and repeated here only where they are material project issues or known
implementation nonconformances.

---

## 2. Issue Statuses

Use the following statuses:

```text
Open
  A known question requiring a decision.

Decided; implementation outstanding
  The design answer is known but code, migration or verification remains.

In progress
  Active work is being undertaken.

Blocked
  Work depends on another unresolved matter.

Deferred
  Deliberately postponed until real pressure justifies further design.

Done; remove on tidy
  Completed and retained only briefly to protect against regression or aid a
  documentation tidy.
```

Items in this document should name an owning active document or the document to
which an eventual decision will be incorporated.

---

## 3. Current Normative Baseline

The following positions are no longer open questions in the active document set:

```text
The formal page grammar is PG, rooted at PublicUI, not a grammar confined to
inner selected-page contents.

PublicUI contains NavigationBar and ContentPanel.

Contents contains an optional FilterSection and a PAPanel.

PAPanel contains a Published Artifact (PA) and Notes.

Notes belong to PAPanel, not to FilterSection.

A promoted Page is represented in the Public UI Model before rendering.

Rendering is an auditable realisation of the model, with informed rendering
policy recorded in 05 Rendering Design.md.

The current public-link design uses one static application shell.

Every material selected-Page view has one canonical Public View Link containing
Page identity and all applicable material Filter values, including defaults.

Navigation destinations identify canonical default Page views; transient or
shell-only state such as NavigationBar visibility is not part of a Public View
Link.

Producer modules own analytical meaning; make_site2 owns coherent public
publication of that meaning.

Legacy code and archived documents are evidence, not authority.

Static BuildOutput is downstream of modelling/rendering; Deployment transports
or exposes completed output rather than redefining it.
```

Issues recorded below shall be resolved consistently with this baseline unless
the active specification or design is deliberately amended.

---

## 4. Immediate Conformance and Rendering Work

### 4.1 Notes Placement Under `PAPanel`

**Status:** Done; remove on tidy after protection against regression is judged
sufficient.

**Owner:** `02 Specification.md`, `04.3 Public UI Model.md`,
`05 Rendering Design.md`, `06 Rendering Audit and Changes.md`.

**Former issue:** `make_site2` rendered Notes beneath a combined region
containing both Filters and the PA, implying that Notes belonged to or spanned
both regions.

**Settled relationship:**

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

**Implemented correction:**

- `ui_model.py` now represents `Contents`, `PAPanel` and `Notes` directly;
- manifest assembly constructs this model natively and represents an absent
  FilterSection as `None` where there are no Filters;
- the modular browser runtime renders Notes within `.pa-panel` and limits them
  to the Note ids owned by that PAPanel;
- the temporary `G1Contents` / `grammar="G1"` compatibility seam has been
  removed;
- local build/deploy inspection has confirmed that the corrected rendering
  works.

**Separate open choice:** Exact Notes-panel height, overflow and visual
treatment remain open under Section 4.2.

### 4.2 Notes-Panel Presentation Policy

**Status:** Open.

**Owner on resolution:** `05 Rendering Design.md`.

**Issue:** Notes ownership and placement are now correctly implemented, but the
shared visible treatment is not settled. A bounded panel below the PA with a
candidate maximum height of `170px` has been discussed.

**Questions:**

- Should a shared maximum height be used?
- Is `170px` an appropriate initial value?
- Should overflow be internally scrollable?
- How should the layout behave where Notes are very short or absent?
- Should Notes-panel treatment vary by PA terminal form?

**Decision criterion:** The treatment should keep Notes accessible while avoiding
unnecessary crowding of the PA; it must not undo their clear ownership by
`PAPanel`.

### 4.3 Heading Typography Ownership

**Status:** Open.

**Owner on resolution:** `05 Rendering Design.md`.

**Issue:** Existing provisional CSS treats site-title typography using a
role-specific selector but content headings using general HTML heading-level
selectors. This leaves unclear whether the visible hierarchy is owned by the
modelled roles or only by convenient markup.

**Questions:**

- Should typography be attached to modelled rendered roles such as site
  caption, Page main heading and Page sub heading?
- Should semantic HTML heading hierarchy supply intentional shared defaults?
- Is an explicit combination appropriate, and if so what is its rule?

**Why this matters:** Heading size and weight tell readers what is primary,
secondary and site-level. The choice should be deliberate rather than a side
effect of element selection.

### 4.4 Banzuke Changes Rank-Cell Semantics

**Status:** Open.

**Owner on resolution:** `04.4 Published Artifact Model.md` where semantic
clarification is needed, and `05 Rendering Design.md` for visible treatment.

**Issue:** The central Rank value in banzuke-style Banzuke Changes rows may be a
semantic row header or an ordinary value. Previous/current implementation
choices have entangled this semantic question with browser-default bold text.

**Questions:**

- Is the central Rank value a row header for the East/West entries?
- If it is, should it use row-header markup with explicit ordinary-weight
  rendering?
- If it is not, should it use ordinary data-cell markup without `scope`?

**Why this matters:** Markup semantics and visible emphasis should each express
intended meaning; neither should be chosen merely to avoid a browser default.

### 4.5 Site-Context Colour Treatment

**Status:** Open for deliberate acceptance, revision or removal.

**Owner on resolution:** `05 Rendering Design.md` and, where operational context
is involved, `09 Deployment and Operations.md`.

**Issue:** Runtime currently gives local, remote and preview contexts distinct
page-background colours. This may be a useful operational cue, but it remains an
implemented presentation choice without an explicit settled meaning.

---

## 5. Public Status and Build Inclusion Policy

### 5.1 Status Vocabulary

**Status:** Open for confirmation.

**Owner on resolution:** `02 Specification.md`, `04.1 Site Definition Model.md`,
`04.2 Publication Plan Model.md`.

**Current vocabulary:**

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

**Questions:**

- Is this the durable status vocabulary?
- Are `candidate` and `research` sufficiently distinct?
- Is any development-only classification required, or is build mode enough?
- What status information, if any, should be visible to readers in non-public
  builds?

### 5.2 Inclusion Policy by Build Mode

**Status:** Open.

**Owner on resolution:** `04.2 Publication Plan Model.md`,
`07 Build, Output and Runtime Design.md`.

**Current direction:**

```text
promoted
  included in ordinary public builds where valid

candidate / research / diagnostic / legacy
  included only by explicit preview/development policy or deliberate public
  exposure under status

superseded / excluded
  omitted by default
```

**Questions:**

- What named build modes are supported?
- Which statuses are included by each mode?
- How is non-promoted inclusion visibly marked where included for inspection?
- Should invalid non-promoted material block a development build or be reported
  and omitted?

---

## 6. Public Selection, URLs and Entry Points

### 6.1 Canonical Single-Shell Public View Links

**Status:** Decided; implementation and verification outstanding.

**Owner:** `02 Specification.md`, `04.2 Publication Plan Model.md`,
`07 Build, Output and Runtime Design.md`.

**Former implementation issue:** Navigation anchors currently advertise
route-local destinations such as `.../index.html`, while the generated site
writes only a root `index.html` and relies on JavaScript query-state Page
selection during ordinary clicks. JavaScript interception therefore masks a
mismatch between visible link behaviour and actual static output.

**Decision made:**

```text
The current site uses one static application shell.

Each material selected-Page view has one canonical Public View Link containing:
  selected Page identity
  every applicable material Filter value, including declared defaults

Navigation destinations identify the canonical default view of their Page.
```

Links need not be human-readable. They must be deterministic, copyable and able
to restore the same material public view. NavigationBar visibility, scroll,
hover, tooltip state and other transient/shell-only interaction are not part of
the link.

**Implementation required:**

- generate Navigation hrefs from Page identity and default Filter declarations,
  rather than emitting unwritten route-local HTML destinations;
- centralise runtime canonical public-view URL writing/restoration;
- include applicable Filter values explicitly, including defaults;
- normalise incomplete or safely resolved invalid incoming state to the
  canonical link of the displayed valid view;
- remove Filter parameters belonging to a previously selected Page when the
  Page changes.

**Verification required:** Ordinary click, open-in-new-tab/copied link, direct
navigation, reload, filtered view restoration, Page changes after Filters,
invalid/missing Filter resolution and browser back/forward behaviour.

### 6.2 Durable Evolution of Published Public Links

**Status:** Deferred beyond the current decision.

**Owner on resolution:** `02 Specification.md`, `04.2 Publication Plan Model.md`,
`07 Build, Output and Runtime Design.md`.

**Settled current position:** One static shell and canonical Page-plus-material-
Filter links are the current public-state design. Canonical links explicitly
state applicable material Filter values rather than relying on current defaults.

**Questions still deferred:**

- What exact parameter names, ordering and Boolean encoding are adopted in code?
- Once links are publicly published, what compatibility guarantees apply to
  later changes in Page ids or Filter ids/values?
- Which invalid requested states should eventually display an explicit public
  message rather than normalise silently to a safe view?

### 6.3 Home / Landing Page

**Status:** Open.

**Owner on resolution:** `04.1 Site Definition Model.md`,
`04.2 Publication Plan Model.md`, possibly `02 Specification.md` if observable
public behaviour changes.

**Current constraint:** The root shell URL may remain the current undeclared
landing view while policy is unsettled, but it shall not create a second
canonical link for a material selected-Page view.

**Questions:**

- Is the landing/home display a normal declared Page?
- Is it a resolved default selection over an existing public Page?
- Is a distinct landing presentation required at all?
- How is an unavailable configured home Page handled in a build?

### 6.4 Additional Entry Points / Quick Links

**Status:** Deferred pending reader need.

**Owner on resolution:** `04.1 Site Definition Model.md` and Rendering Design if
visible placement is introduced.

**Current constraint:** Any quick link must point to a canonical Public View
Link for an included Page rather than define a competing information
architecture or an unwritten output destination.

**Questions:**

- Are quick links useful or required?
- Are they part of NavigationBar, a landing Page or another declared public
  entry route?
- Which Pages merit quick access initially?

---

## 7. Producer Integration and Migration

### 7.1 Producer Preparation / Orchestration API

**Status:** Deferred until repeated producer integration pressure.

**Owner on resolution:** `08 Producer Integration and Migration.md` and command
implementation design.

**Questions:**

- Does `make_site2` invoke producer preparation in the ordinary workflow or
  consume prepared site-facing inputs by default?
- Is a common producer preparation interface needed?
- Is a producer registry or orchestration module warranted?
- How are build-mode/date/data-instance restrictions passed to producer
  preparation, where supported?

### 7.2 Site-Facing Input Representation

**Status:** Deferred; to be driven by real migrated PA families.

**Owner on resolution:** `04.4 Published Artifact Model.md`,
`08 Producer Integration and Migration.md`.

**Questions:**

- Is a shared stable interchange representation needed across producers?
- When is a Python-object handoff sufficient?
- When are generated JSON/CSV/data files preferable?
- Does a manifest-like representation become useful as a serialization/handoff
  mechanism without becoming a new semantic layer?
- What validation information must travel with PA input?

### 7.3 Migration Priorities and Scope

**Status:** Open as planning work.

**Owner:** `08 Producer Integration and Migration.md`.

**Current pressure cases:**

```text
Banzuke Changes
Basho Results / BRB
an ordinary table PA
an ordinary chart PA
a sectioned-table or prose PA
richer-structure Pages only after ordinary PG/PA paths are stable
```

**Questions:**

- Which Page is the next complete producer-to-public migration target?
- Which former Pages should be promoted, retained only as legacy/research, or
  excluded?
- What comparison/audit tooling is required while migrating real Pages?

---

## 8. Public UI and PA Model Extension Pressure

### 8.1 Note Targeting and Relevance Representation

**Status:** Deferred until more real Notes cases require structure.

**Owner on resolution:** `04.3 Public UI Model.md`,
`04.4 Published Artifact Model.md`, `07 Build, Output and Runtime Design.md`.

**Current position:** Notes belong to PAs or visible PA features, not Filters.
The current model intentionally avoids a large target taxonomy in advance of
need. The implemented runtime now respects the Note ids owned by each visible
PAPanel.

**Possible targets under pressure:**

```text
PA as a whole
table column or column group
chart trace or source
declared representation/view
prose section
custom-PA visible feature
```

**Questions:**

- How should richer Note targets be represented in model/serialized runtime data?
- How should relevance conditions grow if PA-level ownership is insufficient?
- Are current PA-level Notes sufficient for most near-term Pages?

### 8.2 PA Metadata and Renderer Registration

**Status:** Deferred; evidence-driven.

**Owner on resolution:** `04.4 Published Artifact Model.md` and
`05 Rendering Design.md`.

**Questions:**

- What additional semantic metadata do real table, chart or sectioned-table PAs
  require?
- What standard chart rendering policy is required once a real chart Page is
  promoted?
- Does custom PA renderer registration need a formal mechanism?
- Are any PA terminal forms missing from the initial set?

### 8.3 Richer Page Grammar Beyond Initial PG

**Status:** Deferred until a promoted-page need justifies specification change.

**Owner on resolution:** `02 Specification.md`, then downstream model and
rendering documents.

**Current position:** The active `PG` supports one visible PAPanel containing
one PA, with an optional flat sibling FilterSection. This ordinary structure is
now represented and rendered directly in the current implementation.

**Pressure indicating that PG may need extension includes:**

- a genuine public Page requiring multiple simultaneously visible PAs;
- nested or conditional Filter scope that cannot be honestly expressed as a
  flat FilterSection governing one PA;
- Notes/provenance ownership that cannot be represented clearly within the
  existing PAPanel relationship;
- repeated renderer-local conditional layout that reveals an unmodelled public
  distinction;
- readers being materially misled by the current allowed structure.

A richer structure shall not be implemented silently inside a custom renderer.

---

## 9. Rendering Policy and Theme Consolidation

### 9.1 Shared Theme and Density Tokens

**Status:** Open for consolidation; not required before ordinary styling work
continues under `05`/`06` discipline.

**Owner on resolution:** `05 Rendering Design.md` and implementation.

**Current settled principle:** Shared rendering treatments may use revisable
presentation tokens. Exact colour or spacing values are not in themselves
semantic commitments unless used to communicate meaning.

**Questions:**

- Should ThemeConfig, LayoutConfig or equivalent token structures become formal
  implementation concepts?
- Which current CSS values should be promoted to explicit shared tokens?
- How should table density, Notes-panel treatment and context themes be
  configured consistently?
- Is there a useful development/preview visual-context treatment that does not
  misstate public meaning?

### 9.2 Chart and Prose Shared Rendering Rules

**Status:** Deferred pending real promoted cases.

**Owner on resolution:** `05 Rendering Design.md`.

**Questions:**

- What shared chart container, palette, legend and interaction treatments are
  appropriate?
- What public explanation of chart-library interactions is warranted, if any?
- What shared prose typography and inline structure are required?

These questions should be answered from real PAs rather than invented abstractly.

---

## 10. Runtime, Output and Operational Policy

### 10.1 Runtime Bootstrap / Serialized Model Material

**Status:** Open for long-term contract refinement.

**Owner on resolution:** `07 Build, Output and Runtime Design.md`.

**Current position:** Browser-readable runtime material transports the modelled
public site and PA references needed for a static interactive site. It must not
become a second hidden public model. The current serialized material exposes
`PAPanel` directly rather than the former inner-content `G1` arrangement.
Runtime material must next expose/use canonical default Navigation links and
support canonical material-view state in the single shell.

**Questions:**

- What bootstrap/manifest schema is durable enough to document or version?
- Should schema or runtime version metadata be emitted?
- What should remain implementation-local?
- How should any future richer Note relevance and PA/runtime dependencies be
  transported cleanly?

### 10.2 Output Tree and Build Metadata

**Status:** Open for standardisation.

**Owner on resolution:** `07 Build, Output and Runtime Design.md`.

**Settled current output principle:** Material Page views are selected within
one static application shell; output is not required to write route-local HTML
entry files for each Page.

**Questions:**

- What is the canonical output-root default?
- What are the durable `runtime`, `assets`, `data` and metadata path
  conventions?
- Should a build metadata file always be emitted?
- What fields should it contain: build mode, Page identities/count, git
  revision, runtime identity or diagnostic summary?
- Is a sitemap, route/state index or output manifest required later?

### 10.3 Cache and Freshness Policy

**Status:** Deferred for production; local/development freshness remains a
practical concern.

**Owner on resolution:** `07 Build, Output and Runtime Design.md` and
`09 Deployment and Operations.md`.

**Current observation:** The modular ES-module runtime is now copied as the
active runtime source, with development cache-busting extended across relative
module imports.

**Questions:**

- What production cache/version policy is eventually required?
- How are runtime/bootstrap and PA data updates invalidated consistently?

### 10.4 Deployment Interface, Safety and Remote Synchronisation

**Status:** Open for operational improvement.

**Owner on resolution:** `09 Deployment and Operations.md`.

**Current position:** Clean replacement of a safely scoped local successor-site
target is desirable. Initial remote deployment may upload/overwrite without
purging stale remote files, with that limitation understood.

**Immediate implementation concerns:**

- verify the documented local target spelling (`htm` versus the code's `html`);
- add a target-safety guard before regarding arbitrary CLI-supplied clean local
  deployment roots as conforming.

**Further questions:**

- What is the final command vocabulary for build, preview, deploy and deploy
  existing output?
- Should preview serving be built into `make_site2` or remain an external
  workflow?
- Should remote deployment become exact synchronisation with stale-file
  removal?
- What automated post-deployment verification or rollback policy is needed?

### 10.5 Date-Limited and Archive/ZIP Workflows

**Status:** Open as workflow/convenience questions.

**Owner on resolution:** `07 Build, Output and Runtime Design.md`, and possibly
`08 Producer Integration and Migration.md` where producer preparation is
involved.

**Questions:**

- Should local inspection builds be able to stage only a chosen date/data range
  where full producer data is slow to prepare or copy?
- Is that restriction a producer-preparation concern, a site-assembly/output
  concern, or both under a declared workflow?
- Is ZIP/archive output a supported build-output artefact, a deployment
  interchange form, or merely an implementation convenience?

Any such workflow must clearly distinguish reduced local/test output from a
complete public build.

---

## 11. Error Presentation and Validation Policy

### 11.1 Browser Error Presentation

**Status:** Open for UX refinement.

**Owner on resolution:** `02 Specification.md` where public behaviour changes,
and `07 Build, Output and Runtime Design.md` / Rendering Design for realisation.

**Questions:**

- How should invalid selected Page or Filter state be reported to readers before
  or alongside canonical normalisation?
- Should runtime data-load failures appear inline in the ContentPanel or PA
  region rather than through transient alerts/logging?
- How much detail is appropriate in public versus development contexts?

### 11.2 Build and Model Validation Coverage

**Status:** Open as implementation grows.

**Owner on resolution:** Relevant model/build documents and tests.

**Current improvement:** Manifest assembly now fails if a Page included by the
Publication Plan lacks a corresponding public panel declaration, and exports
artefacts only for planned public panels.

**Next validation pressure:** Planned Navigation links must be generated as
canonical default Public View Links for the selected single-shell design rather
than preserve unwritten route-local destinations.

**Questions:**

- Which remaining invariants in `04.1` through `04.4` require executable
  validation first?
- Which failures should block builds versus appear as diagnostics under
  development policy?
- How should rendering audit findings be connected to regression tests where a
  stable rule has been adopted?

---

## 12. Documentation Consolidation and Maintenance

### 12.1 Archive Review and Recovery of Useful Material

**Status:** In progress / deferred tidy after the active set is complete.

**Owner:** Active documentation set as a whole.

The archived documents remain useful evidence. Once the active set is complete,
they should be reviewed to identify any useful contract, operational fact,
implementation pressure case or open issue that has not been carried forward.

The result should not be wholesale copying. Material should be recovered only
where it remains relevant under the new `PG`-centred narrative and boundaries.

### 12.2 Documentation Index / Reading Order

**Status:** Open; likely small follow-up.

**Owner on resolution:** docs root/index or README.

The active documents now tell a deliberate sequence from requirements to
operations and open issues. A compact index or reading-order page may be useful
once drafting is complete, identifying the active normative documents and
marking `docs/archive` as historical evidence only.

### 12.3 Proposal Disposition

**Status:** Deferred until the new active set is accepted.

**Question:** Once the replacement documents are reviewed and accepted, should
`Proposal.md` remain as a historical rationale, be moved to archive, or be
reduced to a short record of the redocumentation decision?

---

## 13. Product and Analytical Ideas Not Yet Design Issues

Product or analytical ideas may be worth recording without treating them as
current `make_site2` design commitments.

Examples inherited from earlier notes include:

- possible explanatory help for rich chart interactions;
- investigation of apparent missing rating values in analytical output;
- new analytical comparisons or public Pages.

Such ideas should become active Page/PA/producer work only when their public
purpose, analytical ownership and publication requirements are considered. An
interesting analytical question is not automatically a public-site design issue.

---

## 14. Current Priority View

The likely immediate priorities are:

```text
Completed foundation
  explicit Contents / PAPanel / Notes model and rendering
  removal of the obsolete G1 compatibility seam
  modular browser-runtime activation
  plan-driven assembly of visible panels and exported artefacts
  decision to use canonical Page-plus-material-Filter links in one static shell

P0
  implement and verify canonical single-shell Navigation/runtime links
  settle or explicitly defer rendering choices needed for current work

P1
  decide the next real producer-to-public migration target
  confirm build-status inclusion and local iteration workflow requirements
  add local deployment target-safety protection

P2
  refine runtime/bootstrap/output conventions as real pressure emerges
  centralise page-level runtime structure where useful
  establish ordinary chart/prose/sectioned-table PA treatments from real Pages

P3
  production cache policy
  remote exact-sync/deployment maturity
  durable compatibility policy for published Public View Links
  richer PG extensions only where promoted public need requires them
```

This priority view is provisional and should change when real implementation or
publication priorities change.

---

## 15. Summary

The first material structural mismatch between the new documentation and the
current implementation has been resolved: the UI model, runtime manifest and
browser rendering represent Notes inside `PAPanel`, not as material spanning
Filters and PA.

A decision has now been made for the most immediate remaining contract defect:
`make_site2` shall use one static shell and canonical Public View Links that
state Page identity and all applicable material Filter values. The current code
still needs to replace route-local Navigation destinations and canonicalise
runtime URL writing/restoration accordingly, followed by inspection of copied,
reloaded, new-tab and filtered-view links.

Other live decisions remain deliberately open:

- Notes visual/dimension policy;
- heading typography ownership;
- Banzuke Changes Rank semantics;
- public status/inclusion and future link-compatibility policies;
- integration/migration priorities;
- runtime/output/deployment maturity and safety.

This document shall keep those matters visible without allowing unresolved work
to become implicit design through convenience or drift.