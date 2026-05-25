# 10 Open Issues and Deferred Design

## Status

Current register of unresolved decisions, implementation work and deferred
design for `src/products/make_site2`.

The active Requirements, Specification and Design documents define the product.
This document records remaining work or decisions without allowing them to
become implicit design through convenience or drift. Detailed supporting audits
currently include:

```text
06 Rendering Audit and Changes.md
10.1 Selected History Coherence Audit.md
```

---

## 1. Issue Statuses

```text
Open
  A known question requiring a decision.

Decided; implementation outstanding
  The design rule is settled but code or migration remains.

Implemented; verification outstanding
  Code has been changed but agreed inspection/closure remains.

Deferred
  Deliberately postponed until real pressure justifies design work.

Done; remove on tidy
  Completed and retained temporarily for continuity/regression protection.
```

---

## 2. Current Baseline

The following positions are now established in the active document set:

```text
PG is rooted at PublicUI.

PublicUI contains NavigationBar and ContentPanel.

Contents contains FilterSection? and PAPanel.

PAPanel contains PA and Notes; Notes do not belong to FilterSection.

Rendering is an auditable realisation of modelled public structure.

The current public-link design uses one static application shell.

Canonical Public View Links state selected Page identity and all applicable
material Filter values, including defaults.

Navigation links identify canonical default Page views.

An explicit History input selects the History/data instance for the whole built
site.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.

A canonical link identifies a view of the published site; it does not ordinarily
freeze the underlying build History/data instance.

Producers own analytical computation and meaning; make_site2 owns coherent
public publication, planning, validation, rendering/output assembly and refusal
to publish incoherent required material.
```

The Selected-History rule is now incorporated in:

```text
02 Specification.md
04.2 Publication Plan Model.md
07 Build, Output and Runtime Design.md
08 Producer Integration and Migration.md
```

---

## 3. Completed or Near-Completed Correction Work

### 3.1 Notes Placement Under `PAPanel`

**Status:** Done; remove on tidy.

The UI model, manifest assembly and modular runtime now represent and render:

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

Notes render within `.pa-panel`, are limited to the Note ids owned by that
PAPanel, and no longer visibly span Filters and PA. The temporary
`G1Contents`/`grammar="G1"` seam has been removed. Local inspection confirmed
the corrected rendering works.

### 3.2 Canonical Single-Shell Public View Links

**Status:** Implemented; verification and documentary closure outstanding.

**Former issue:** Navigation anchors advertised route-local `.../index.html`
destinations that were not generated, while ordinary left clicks appeared to
work only because JavaScript intercepted them.

**Implemented correction:** Navigation hrefs are now emitted as canonical
single-shell Page/default-Filter links, and runtime URL handling writes
canonical Page-plus-material-Filter public state.

**Verified so far:** after pulling, rebuilding and deploying the changed code,
opening **Standings by Wins** in a new tab uses its canonical link rather than a
nonexistent route-local page; the observed 404 is gone.

**Remaining checks before closure:**

```text
copy/reopen a filtered table Page link
copy/reopen a filtered chart Page link
change from a filtered Page to an unfiltered Page and confirm stale parameters go
reload behaviour
browser back/forward behaviour
incomplete/invalid state normalisation
```

**Clarification recorded during testing:** A link records reader-selected state,
not an immutable snapshot of source data. A default Banzuke Changes link may
correctly continue to mean “latest changes in the History published by this
site”.

---

## 4. Active P0: Selected History / Whole-Site Data Coherence

### 4.1 Explicit-History Build Coherence

**Status:** Decided rule; enforcement policy and implementation outstanding.

**Owning documents:** `02 Specification.md`, `04.2 Publication Plan Model.md`,
`07 Build, Output and Runtime Design.md`, `08 Producer Integration and Migration.md`.

**Detailed evidence:** `10.1 Selected History Coherence Audit.md`.

**Observed failure:** A build invoked with a history zip ending at `1980_11`
showed:

```text
Basho Results
  correctly reflecting the selected History and ending at 1980_11.

Banzuke Changes
  incorrectly displaying copied current/full-history 2026 data.
```

**Established rule:**

```text
An explicit History input selects the History/data instance for the whole built
site.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.
```

**Why P0:** A site that renders successfully but mixes incompatible data
instances across promoted Pages is materially misleading.

**Current implementation fact:** `build_site(...)` passes `resolved_history`
only into Basho Results. Banzuke Changes and the other included PA inputs are
staged from pre-existing outputs without selected-History validation; several
source paths visibly identify wider/current intervals.

**Initial audit:**

| Assessment | Pages / PAs |
| --- | --- |
| Conforming for explicit History selection | Basho Results |
| Demonstrated or plainly nonconforming for the restricted-history build | Banzuke Changes; Finish by Chii; Rank at Retirement; Career Length |
| Not proven coherent because copied input is not derived from or validated against selected History | Standings by Wins; Banzuke Division by Era; Makuuchi Rank by Era; Division Stability; First Chii Appearance; Typical Equelo Ratings; Win Probability by Standing |

### 4.2 Enforcement Policy to Decide and Implement

Two implementation paths remain legitimate:

```text
Policy A
  Integrate/prep all included History-dependent promoted PAs before allowing an
  explicit-History build to succeed.

Policy B
  Fail or explicitly omit unsupported PAs in explicit-History builds while
  integrating producers incrementally.
```

**Recommended immediate policy:** adopt Policy B as the safety rule, and
integrate Banzuke Changes first. A normal public build must not silently omit
required promoted Pages; omission would need an explicit reduced
inspection/non-public build policy.

### 4.3 Next Technical Investigation

Inspect the Banzuke Compare producer boundary to determine whether it:

- already accepts a `History` object or selected-history serialization;
- can produce `site_config.json` and `banzuke_change_report.csv` for a supplied
  History/output root;
- emits enough identity/provenance to validate prepared output against the
  selected History; or
- needs a deliberate site-facing preparation API.

The correction must preserve the boundary:

```text
Producer
  computes Banzuke Changes from the selected History.

make_site2
  plans, validates, stages and presents coherent site-facing output.
```

---

## 5. Open Rendering Decisions

These remain independent of the active data-coherence P0:

| Issue | Status | Owner on resolution |
| --- | --- | --- |
| Notes-panel height, overflow and framing, including the discussed `170px` cap | Open | `05 Rendering Design.md` |
| Heading typography ownership: role-specific treatment versus general heading defaults | Open | `05 Rendering Design.md` |
| Banzuke Changes central Rank value: row-header semantics or ordinary data value | Open | `04.4 Published Artifact Model.md` and `05 Rendering Design.md` |
| Local/remote/preview background colours as deliberate context cue | Open | `05 Rendering Design.md`, possibly `09 Deployment and Operations.md` |

---

## 6. Public Status and Build Inclusion Policy

### 6.1 Status Vocabulary and Inclusion Modes

**Status:** Open; now relevant to Selected-History enforcement.

The current status vocabulary is:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

The project still needs to confirm build-mode inclusion policy. In particular,
it must decide whether a restricted-history inspection build can omit unsupported
promoted PAs under an explicit non-public policy, while a normal public build
must fail rather than omit or publish mixed-history material.

### 6.2 Page Promotion Review

**Status:** Open.

All currently declared Pages remain `PROMOTED`. This should eventually be
reviewed against public-contract completeness, including coherent data-instance
support, not merely rendering availability.

---

## 7. Producer Integration and Migration

### 7.1 Immediate Producer Pressure

**Status:** In progress as P0 investigation.

Banzuke Changes is no longer merely a useful custom-table migration example. It
is the first demonstrated selected-History producer-integration failure and is
the next concrete producer boundary to inspect.

### 7.2 Broader Producer/Input Contract

**Status:** Deferred in general; data-instance identity/validation is immediate
where required by the P0.

Copied producer output is insufficient for a History-dependent promoted PA in
an explicit-History build unless it is prepared from, or validated against, the
Selected History. A wider producer orchestration or interchange API should be
designed from real integration pressure rather than invented in advance.

---

## 8. Runtime, Output and Operational Policy

| Issue | Status | Note |
| --- | --- | --- |
| Runtime/bootstrap schema/versioning | Deferred | Runtime now exposes `PAPanel` and canonical URL writing; long-term serialization policy remains open. |
| Build metadata / data-instance identity | Open | Selected-History identity is now a strong candidate for inspectable build or per-PA validation metadata. |
| Production cache policy | Deferred | Development module cache-busting is active. |
| Deployment target safety | Open / P1 | Add a safety guard before cleaning arbitrary CLI-supplied local targets; check documented `htm` versus code `html` target spelling. |
| Remote exact synchronisation | Deferred | Current remote deployment may leave stale files unless later strengthened. |

---

## 9. Other Deferred Design Pressure

The following remain deferred pending real need:

- durable compatibility guarantees for published canonical Public View Links;
- home/landing Page modelling and any additional quick links;
- richer Note targeting;
- PA terminal-kind versus specialised-renderer registration refinement;
- richer `PG` structures for multiple PAs or nested Filter scope;
- centralisation of repeated runtime page/PAPanel assembly;
- ordinary chart/prose shared rendering policy beyond current real cases;
- documentation index/archive/proposal tidy.

---

## 10. Current Priority View

```text
Completed foundation
  explicit Contents / PAPanel / Notes model and rendering
  removal of the obsolete G1 compatibility seam
  modular browser-runtime activation
  plan-driven assembly of visible panels and exported artefacts
  canonical single-shell Navigation/runtime link implementation
    (reported new-tab defect verified; full closure checks remain)
  normative incorporation of the Selected-History coherence rule

P0
  enforce coherent explicit-History builds across included promoted
  History-dependent PAs; investigate/integrate Banzuke Changes first

Closure check outstanding
  complete canonical-link browser verification and update its final status

P1
  settle explicit-history inspection/public build inclusion behaviour
  follow through on producer integrations exposed by the audit
  add local deployment target-safety protection

P2
  settle open rendering choices
  refine build metadata/runtime/output conventions
  centralise repeated page-level runtime structure where worthwhile

P3
  production cache policy
  remote exact-sync/deployment maturity
  durable published-link compatibility policy
  richer PG extensions only where promoted public need requires them
```

---

## 11. Summary

The Notes/PAPanel structural correction is complete. The canonical single-shell
link correction is implemented and has fixed the observed right-click/new-tab
failure; its remaining agreed browser checks still need completing before final
closure.

The new active P0 is fully recorded: a Selected History governs all included
promoted History-dependent material in a build, but the current implementation
uses it directly only for Basho Results and can publish incompatible copied PA
data. That governing rule is now present in the active specification and design
set, with `10.1 Selected History Coherence Audit.md` providing the evidence and
PA-by-PA audit.

The next substantive implementation task is to settle safe immediate enforcement
and inspect/integrate the Banzuke Changes producer boundary without duplicating
producer-owned analysis inside `make_site2`.