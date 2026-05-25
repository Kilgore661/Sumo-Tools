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
Where a settled rule has implementation or verification work outstanding, this
document may retain a short action item until that work is complete.

Detailed audits may be recorded in companion documents, including:

```text
06 Rendering Audit and Changes.md
10.1 Selected History Coherence Audit.md
```

---

## 2. Issue Statuses

Use the following statuses:

```text
Open
  A known question requiring a decision.

Decided; implementation outstanding
  The design answer is known but code or migration remains.

Implemented; verification outstanding
  The intended change is in code, but agreed inspection/closure remains.

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

A further principle has now been agreed as a result of the Selected History
audit, but still requires incorporation into the owning normative/design
documents and implementation:

```text
An explicit History input selects the History/data instance for the whole
published site build.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.
```

---

## 4. Completed or Near-Completed Correction Work

### 4.1 Notes Placement Under `PAPanel`

**Status:** Done; remove on tidy after protection against regression is judged
sufficient.

**Owner:** `02 Specification.md`, `04.3 Public UI Model.md`,
`05 Rendering Design.md`, `06 Rendering Audit and Changes.md`.

**Former issue:** `make_site2` rendered Notes beneath a combined region
containing both Filters and the PA, implying that Notes belonged to or spanned
both regions.

**Implemented correction:**

- `ui_model.py` represents `Contents`, `PAPanel` and `Notes` directly;
- manifest assembly constructs the model natively and represents an absent
  FilterSection as `None`;
- the modular browser runtime renders Notes within `.pa-panel` and limits them
  to the Note ids owned by that PAPanel;
- the temporary `G1Contents` / `grammar="G1"` compatibility seam has been
  removed;
- local build/deploy inspection confirmed that the corrected rendering works.

### 4.2 Canonical Single-Shell Public View Links

**Status:** Implemented; verification and documentary closure outstanding.

**Owner:** `02 Specification.md`, `04.2 Publication Plan Model.md`,
`07 Build, Output and Runtime Design.md`.

**Former issue:** Navigation anchors advertised route-local destinations such as
`.../index.html`, while the generated site writes a root `index.html` and uses
runtime selected-Page state. JavaScript interception masked invalid copied or
new-tab links.

**Decision and implemented correction:**

```text
The current site uses one static application shell.

Each material selected-Page view has one canonical Public View Link containing:
  selected Page identity
  every applicable material Filter value, including declared defaults

Navigation destinations identify the canonical default view of their Page.
```

The code now emits single-shell Navigation hrefs generated from Page/default
Filter state and provides canonical runtime URL writing. The originally observed
failure has been verified fixed: opening **Standings by Wins** in a new tab no
longer requests a nonexistent route-local page after rebuilding from the updated
code.

**Remaining verification before closure:** filtered Page URL copying/reopening;
filtered chart URL copying/reopening; stale Filter-parameter removal on Page
change; reload; back/forward; and incomplete/invalid state normalisation.

**Important clarification discovered during verification:** a canonical link
records reader-selected material state; it does not freeze the build's underlying
published data instance. For example, the default Banzuke Changes link may
correctly mean “latest basho in this published build's History”.

---

## 5. Current P0: Selected History / Whole-Site Data Coherence

### 5.1 Explicit-History Build Coherence

**Status:** Decided principle; implementation policy and implementation
outstanding.

**Owner on incorporation:** `02 Specification.md`,
`04.2 Publication Plan Model.md`, `07 Build, Output and Runtime Design.md`,
`08 Producer Integration and Migration.md`.

**Detailed audit:** `10.1 Selected History Coherence Audit.md`.

**Observed failure:** A local build invoked with a history zip ending at
`1980_11` displayed:

```text
Basho Results
  correctly based on the selected History and ending at 1980_11.

Banzuke Changes
  incorrectly copied current/full-history output showing 2026 data.
```

**Agreed rule:**

```text
An explicit History input selects the History/data instance for the whole
published site build.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.
```

**Why this is P0:** A successful public build that mixes data instances across
promoted Pages is materially misleading even when every Page renders correctly
and every canonical link works correctly.

**Current implementation fact:** `build_site(...)` passes `resolved_history`
only to Basho Results. Banzuke Changes and the remaining included PA inputs are
currently staged by copying pre-existing producer outputs without selected-
History validation. Several source paths explicitly identify wider/current data
intervals.

**Initial audit assessment:**

| Assessment | Pages / PAs |
| --- | --- |
| Conforming for explicit History selection | Basho Results |
| Demonstrated or plainly nonconforming for the reduced-history build | Banzuke Changes; Finish by Chii; Rank at Retirement; Career Length |
| Not proven coherent because copied input is neither derived from nor validated against selected History | Standings by Wins; Banzuke Division by Era; Makuuchi Rank by Era; Division Stability; First Chii Appearance; Typical Equelo Ratings; Win Probability by Standing |

**Implementation policy to settle:**

1. integrate all History-dependent producer preparation before allowing an
   explicit-history public build; or
2. immediately fail or omit unsupported Pages under explicit-history builds,
   while integrating producers incrementally.

**Recommended immediate policy:** adopt the second policy as a safety rule, and
integrate Banzuke Changes first. The build must not silently claim successful
coherent historical publication while continuing to stage unvalidated copied
promoted material.

**Next technical investigation:** inspect the Banzuke Compare producer boundary
to determine how it can prepare `site_config.json` and
`banzuke_change_report.csv` from the selected `History` without duplicating
analytical logic inside `make_site2`.

---

## 6. Open Rendering Decisions

### 6.1 Notes-Panel Presentation Policy

**Status:** Open.

**Owner on resolution:** `05 Rendering Design.md`.

Notes ownership and placement are correctly implemented, but shared visible
treatment remains unsettled. A bounded panel below the PA with a candidate
maximum height of `170px` has been discussed. Decide maximum height, scrolling,
short/absent-Notes behaviour and any PA-terminal variation.

### 6.2 Heading Typography Ownership

**Status:** Open.

**Owner on resolution:** `05 Rendering Design.md`.

Current CSS mixes role-specific site-title styling with general HTML heading
selectors. Decide whether intentional typography is attached to modelled roles,
HTML hierarchy, or an explicit combination.

### 6.3 Banzuke Changes Rank-Cell Semantics

**Status:** Open.

**Owner on resolution:** `04.4 Published Artifact Model.md` where semantic
clarification is needed, and `05 Rendering Design.md` for visible treatment.

Decide whether the central Rank value is a semantic row header rendered with
explicit ordinary weight, or an ordinary data value without `scope`.

### 6.4 Site-Context Colour Treatment

**Status:** Open for deliberate acceptance, revision or removal.

**Owner on resolution:** `05 Rendering Design.md` and, where operational context
is involved, `09 Deployment and Operations.md`.

Runtime currently gives local, remote and preview contexts distinct page
background colours without a settled documented meaning.

---

## 7. Public Status and Build Inclusion Policy

### 7.1 Status Vocabulary

**Status:** Open for confirmation.

**Owner on resolution:** `02 Specification.md`, `04.1 Site Definition Model.md`,
`04.2 Publication Plan Model.md`.

The current vocabulary is:

```text
promoted
candidate
research
diagnostic
legacy
superseded
excluded
```

Confirm whether this is durable and what status information is visible in
non-public builds.

### 7.2 Inclusion Policy by Build Mode

**Status:** Open; now directly relevant to Selected History enforcement.

**Owner on resolution:** `04.2 Publication Plan Model.md`,
`07 Build, Output and Runtime Design.md`.

Determine build modes, status inclusion policy and whether an explicit-history
inspection build may omit unsupported PAs only under a declared non-public
policy. A normal promoted/public build shall not silently omit or publish
mixed-history material.

---

## 8. Public Selection and Entry Points

### 8.1 Durable Evolution of Published Public Links

**Status:** Deferred beyond the current canonical-link implementation.

**Settled current position:** One static shell and canonical Page-plus-material-
Filter links are the current public-state design. Canonical links explicitly
state applicable material Filter values rather than relying on defaults.

**Questions still deferred:** long-term compatibility for publicly published Page
ids/Filter ids/values, and whether some invalid requested states should
ultimately show an explicit public message rather than normalise safely.

### 8.2 Home / Landing Page

**Status:** Open.

The root shell URL may remain the current undeclared landing view while policy
is unsettled, but it shall not create a second canonical link for a material
selected-Page view.

### 8.3 Additional Entry Points / Quick Links

**Status:** Deferred pending reader need.

Any quick link must point to a canonical Public View Link for an included Page,
not define a competing information architecture or unwritten output destination.

---

## 9. Producer Integration and Migration

### 9.1 Producer Preparation / Orchestration API

**Status:** No longer wholly deferred: Banzuke Changes requires immediate
investigation under the Selected History P0.

**Owner on resolution:** `08 Producer Integration and Migration.md` and command
implementation design.

The broader common producer-preparation API remains evidence-driven, but the
current P0 requires a concrete answer for Banzuke Changes: whether an existing
producer function can accept the selected `History`, whether prepared output can
carry/validate History identity, and how `make_site2` stages only coherent
site-facing data.

### 9.2 Site-Facing Input Representation

**Status:** Deferred in general; selected-History identity/validation is now an
immediate pressure case.

A copied producer output used in a build selected by explicit `History` is not
sufficient merely because its file shape is correct. It must either be prepared
from that History or carry enough identity/provenance for planning/build
validation to prove coherence.

### 9.3 Migration Priorities and Scope

**Status:** Open as planning work, with Banzuke Changes promoted to the immediate
integration case by the P0 failure.

Banzuke Changes is now the first producer-integration investigation because it
has already demonstrated incoherent public output under a reduced-history
build. Other PA families should follow according to the audit in `10.1` and
real public priority.

---

## 10. Public UI and PA Model Extension Pressure

### 10.1 Note Targeting and Relevance Representation

**Status:** Deferred until more real Notes cases require structure.

Notes belong to PAs or visible PA features, not Filters. The runtime now
respects the Note ids owned by each visible PAPanel.

### 10.2 PA Metadata and Renderer Registration

**Status:** Deferred; evidence-driven.

Future work may clarify terminal-kind/renderer-kind boundaries and separate
analytical provenance from rendering/runtime hints now held in PA metadata.

### 10.3 Richer Page Grammar Beyond Initial PG

**Status:** Deferred until a promoted-page need justifies specification change.

The active `PG` supports one visible PAPanel containing one PA, with an optional
flat sibling FilterSection. This ordinary structure is represented and rendered
directly in the current implementation.

---

## 11. Runtime, Output and Operational Policy

### 11.1 Runtime Bootstrap / Serialized Model Material

**Status:** Open for long-term contract refinement.

Browser-readable runtime material now exposes `PAPanel` directly and the runtime
implementation now provides canonical public-view URL writing. Bootstrap/schema
versioning and long-term representation remain later questions.

### 11.2 Output Tree and Build Metadata

**Status:** Open for standardisation; selected-History identity has become an
important candidate for inspectable build metadata or validation inputs.

The settled current output principle is that material Page views are selected
within one static application shell; output is not required to write route-local
HTML files for each Page. A coherent explicit-history build additionally needs a
way to demonstrate or enforce the data instance used for all included
History-dependent PAs.

### 11.3 Cache and Freshness Policy

**Status:** Deferred for production.

The modular ES-module runtime is copied as the active runtime source, with
development cache-busting extended across relative module imports.

### 11.4 Deployment Interface, Safety and Remote Synchronisation

**Status:** Open for operational improvement.

Immediate concerns remain: check the documented local target spelling (`htm`
versus code's `html`) and add a target-safety guard before treating arbitrary
CLI-supplied clean local roots as safe for destructive replacement.

### 11.5 Archive/ZIP and Restricted-History Workflows

**Status:** Decided at principle level; enforcement outstanding.

An explicit `history` or `history_zip` is not merely a Basho Results override. It
selects the History/data instance for the whole built site. The exact workflow
for preparing or rejecting unsupported copied PA inputs remains part of the new
P0 implementation policy.

---

## 12. Error Presentation and Validation Policy

### 12.1 Browser Error Presentation

**Status:** Open for UX refinement.

Determine how invalid selected Page or Filter state should be reported before or
alongside canonical normalisation, and how runtime data-load failures should be
shown in the public interface.

### 12.2 Build and Model Validation Coverage

**Status:** Open; Selected History coherence is now the highest-value validation
pressure.

Current improvements include validation that a planned Page has a public panel
declaration and canonical Navigation URL generation. Next, a successful
explicit-history build must not stage promoted History-dependent PA material
from a different or unvalidated data instance.

---

## 13. Documentation Consolidation and Maintenance

### 13.1 Normative Incorporation of Selected History Rule

**Status:** Required follow-up before implementation is regarded as design-led.

The governing rule established in `10.1 Selected History Coherence Audit.md`
should be incorporated into:

```text
02 Specification.md
04.2 Publication Plan Model.md
07 Build, Output and Runtime Design.md
08 Producer Integration and Migration.md
```

The immediate implementation-policy choice (prepare all versus reject/omit
unsupported inputs under explicit-history builds) must then be reflected where
it settles the build/integration contract.

### 13.2 Archive Review, Documentation Index and Proposal Disposition

**Status:** Deferred tidy after the active set is complete.

Archived material remains evidence only. A compact documentation index and a
decision on whether `Proposal.md` remains as rationale or moves to archive may
be useful later.

---

## 14. Current Priority View

```text
Completed foundation
  explicit Contents / PAPanel / Notes model and rendering
  removal of the obsolete G1 compatibility seam
  modular browser-runtime activation
  plan-driven assembly of visible panels and exported artefacts
  canonical single-shell Navigation/runtime link implementation
    (reported new-tab defect verified; full closure checks remain)

P0
  make explicit-History builds coherent across all included promoted
  History-dependent PAs; investigate/integrate Banzuke Changes first

Closure check outstanding
  complete canonical-link browser verification and update its final status

P1
  decide the next producer integrations exposed by the History audit
  confirm status/inclusion and explicit-history inspection-build policy
  add local deployment target-safety protection

P2
  settle open rendering choices
  refine runtime/bootstrap/output conventions as real pressure emerges
  centralise repeated page-level runtime structure where useful

P3
  production cache policy
  remote exact-sync/deployment maturity
  durable compatibility policy for published Public View Links
  richer PG extensions only where promoted public need requires them
```

---

## 15. Summary

The Notes/PAPanel structural correction is complete. The canonical single-shell
link correction is implemented and has fixed the observed right-click/new-tab
failure, although the remaining planned browser verification should still be
completed before documentary closure.

Verification of those links uncovered the new active P0: an explicit History
input currently governs Basho Results but does not govern or validate the copied
inputs for other promoted PAs. A restricted-history build therefore published a
correct `1980_11` Basho Results view alongside incorrect `2026` Banzuke Changes
material.

The detailed audit is recorded in `10.1 Selected History Coherence Audit.md`.
The next substantive task is to incorporate its agreed rule into the owning
active documents, settle the immediate enforcement policy, and investigate the
Banzuke Changes producer boundary as the first integration correction.