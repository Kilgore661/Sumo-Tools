# 10 Open Issues and Deferred Design

## Status

Current register of unresolved decisions, implementation work and deferred
design for `src/products/make_site2`.

The active Requirements, Specification and Design documents define the product.
Detailed evidence is recorded in:

```text
06 Rendering Audit and Changes.md
10.1 Selected History Coherence Audit.md
```

---

## 1. Issue Statuses

```text
Open
  A known question or observed defect requiring investigation or decision.

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

## 2. Established Baseline

```text
PG is rooted at PublicUI.
PublicUI contains NavigationBar and ContentPanel.
Contents contains FilterSection? and PAPanel.
PAPanel contains PA and Notes; Notes do not belong to FilterSection.
Rendering is an auditable realisation of modelled public structure.

The public-link design uses one static application shell.
Canonical Public View Links state selected Page identity and all applicable
material Filter values, including defaults.
Navigation links identify canonical default Page views.

A build has a coherent publication context.
An explicit History input selects the History/data instance for material whose
public meaning depends on that History.
A Page whose meaning additionally requires compatible successor/live input must
have that input validated or be explicitly resolved as unavailable in production.
```

### 2.1 Banzuke Changes Semantics

The meaning of **2.1 Banzuke Changes** is now settled:

```text
Banzuke Changes is a new-banzuke change report.

It answers:
  A newly published banzuke is available before that basho has results of its
  own. How does it differ from the preceding represented basho?

It is not:
  a general adjacent-historical-basho comparison Page;
  a view of the final two bashos in an arbitrary selected History; or
  a Page which may silently display unrelated current/live material in an
  archive-history publication.
```

Production availability requires:

```text
predecessor context
  the latest relevant BashoState in the site's History;

current subject
  a compatible newly published successor banzuke which has not yet entered
  History with results of its own.
```

When that condition is not met, the production Page shall be unavailable. Its
Navigation treatment shall not invite ordinary selection and a direct request
shall explain that no newly published banzuke is available and direct readers
to Basho Results for represented historical comparison.

### 2.2 Temporary Development Exception

**Status:** Decided; warning implementation outstanding.

Outside the short natural availability window, developers still need to inspect
and regress the Banzuke Changes UI. Therefore a development build may leave 2.1
selectable and render the existing prepared/live report even when production
availability is not established.

This is a testing affordance, not alternate public semantics. Until production
availability enforcement is implemented, the enabled development Page must add
a conspicuous warning after its existing subheading `New-banzuke change
report.` materially equivalent to:

```text
DEVELOPMENT WARNING: availability is not yet validated against this build's
History. This Page is intended only for a newly published banzuke before its
first results enter History; archive or historical builds may show unrelated
live output.
```

The current command-line mode distinction is appropriate for this policy:

```text
ordinary build without --prod
  development output; may expose the warning-backed testing affordance.

build with --prod
  production output; eventually must enforce the availability rule rather than
  silently removing the warning while publishing unvalidated material.
```

---

## 3. Completed Correction Work

### 3.1 Notes Placement Under `PAPanel`

**Status:** Done; remove on tidy.

The UI model, manifest assembly and modular runtime now represent and render:

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

Notes render within `.pa-panel`, are limited to the Note ids owned by that
PAPanel, and no longer visibly span Filters and PA. The temporary `G1` seam has
been removed and local inspection confirmed the corrected rendering works.

### 3.2 Canonical Single-Shell Public View Links

**Status:** Done; remove on tidy.

Navigation hrefs are emitted as canonical single-shell Page/default-Filter links
and runtime URL handling writes canonical Page-plus-material-Filter public
state. Verification established:

```text
examined Navigation anchors use ?page=... links with explicit defaults;
no Navigation href advertises an unwritten .../index.html Page destination;
representative new-tab destinations work without a 404;
filtered table and chart links copy/reopen with their states restored;
Page changes remove stale parameters;
reload and browser back/forward preserve views; and
incomplete/invalid incoming state behaves acceptably.
```

A canonical Page/view link does not itself establish that an
availability-sensitive Page has publishable material in a particular build.

---

## 4. Active P0: Whole-Site Publication Coherence

**Status:** General rule and Banzuke Changes meaning decided; implementation
outstanding.

A restricted-history build ending at `1980_11` correctly displayed Basho Results
for `1980_11` but also displayed copied current/live Banzuke Changes material
from 2026. This is not a link failure. It is misleading publication-context
handling.

For Banzuke Changes the correction is now understood as availability handling,
not as recomputing a generic final-two-bashos report from the selected History.

For directly History-derived copied PAs the existing Selected-History issue
remains:

| Assessment | Pages / PAs |
| --- | --- |
| Conforming for explicit History selection | Basho Results |
| Availability-sensitive; misleading in archive builds until warned/enforced | Banzuke Changes |
| Plainly nonconforming for the restricted-history build | Finish by Chii; Rank at Retirement; Career Length |
| Not proven coherent because copied input is unvalidated against selected History | Standings by Wins; Banzuke Division by Era; Makuuchi Rank by Era; Division Stability; First Chii Appearance; Typical Equelo Ratings; Win Probability by Standing |

### Immediate Action Already Decided

```text
Add the visible development warning to 2.1 when rendering development output,
leaving its present testable behaviour otherwise unchanged.
```

### Later Production Enforcement

This is one P0 work item, not a set of independent priorities. It includes:

- implementing Banzuke Changes production availability handling;
- resolving availability from History plus compatible successor banzuke input;
- rendering Banzuke Changes normally only when available;
- otherwise disabling or marking its Navigation entry unavailable and providing
  a direct-request explanation directing readers to Basho Results;
- continuing Selected-History enforcement for ordinary History-derived copied
  PAs;
- deciding whether `--prod` remains the production-coherence switch;
- keeping quick explicit-history inspection builds usable only if their reduced
  or caveated scope is clear in command output and, where useful, the generated
  site; and
- carrying data-instance identity/provenance far enough to enforce or explain
  those decisions.

---

## 5. New Defect: Empty Plotly Line Charts

**Status:** Open; reproduce, scope and diagnose.

Pages rendering Plotly line charts have been observed to display a chart frame
without visible traces. The affected Pages, states and cause have not yet been
established.

Investigation shall determine whether data files load and contain rows, whether
runtime errors occur, whether traces are constructed before Plotly invocation,
and whether the problem affects only line charts or other Plotly renderers.
A reliably empty promoted chart PA is a material rendering failure.

This defect does not reopen the canonical-link correction.

---

## 6. Other Open or Deferred Matters

| Issue | Status | Note |
| --- | --- | --- |
| Structural hider implementation | Implemented; verification outstanding | NavigationBar and Notes now use the same pattern: a first-class hider strip remains visible while the controlled content region collapses. NavigationBar controls NavigationContent; Notes controls NotesContent. |
| Table chrome/body split as explicit PA model | Deferred / TBD | Runtime now implements table-body-only scrolling for ordinary table PAs. Consider a richer producer-facing PA model only if future pressure requires explicit non-scrolling chrome and scrolling data-region semantics. |
| Ranked tabular views versus sortable table views | Deferred / TBD | Longest Careers shows the distinction: a table-like ranked view may intentionally preserve pre-sorted row order as public meaning. If arbitrary reader sorting is wanted for the same data, consider a separate neutral tabular/table-browser view rather than making the ranked view itself sortable. |
| Heading typography ownership | Open | Rendering decision. |
| Banzuke Changes central Rank semantics | Open | PA/rendering decision. |
| Context-specific background colours | Open | Rendering/operations decision. |
| General unavailable-Page model/rendering | Open | Banzuke Changes is the first concrete required case. |
| Page promotion review | Open | Review against coherence, availability and actual PA rendering. |
| Documentation chunking for LLMs | Deferred / TBD | Consider whether active docs should be refactored into smaller LLM-manageable chunks with hierarchical README/front-door files. |
| Code chunking for LLMs | Deferred / TBD | Consider whether make_site2 code should be refactored into smaller LLM-manageable modules or package areas without introducing abstraction churn. |
| Nested table sorting | Deferred / TBD | Investigate whether table sorting should support secondary sort keys, and possibly only primary/secondary ordering rather than arbitrary-depth sort stacks. |
| Producer result-field shape | Deferred / TBD | Where distinct result values are emitted by a data builder, do not coalesce them into one display string as current result fields do. Current sortable-column implementation may parse compact result strings for wins sorting, but should carry an explicit warning comment until this issue is resolved. |
| Plotly interaction state in deep links | Deferred / TBD | Decide whether canonical public links should preserve Plotly legend/trace visibility, zoom/pan, or other client-side chart state. Complexity is moderate-to-high if yes: define which Plotly state is public material state versus temporary reader interaction, serialize it without unstable Plotly internals, restore it after data/render completion, keep URLs readable, and avoid breaking canonical-link semantics. |
| Table sort state in deep links | Deferred / TBD | Decide whether ordinary table sort state should be encoded in canonical public view links or remain PA-local browser interaction. |
| Runtime/bootstrap schema/versioning | Deferred | Long-term serialization policy. |
| Build metadata / data-instance identity | Open | Include History/successor-input identity where useful. |
| Deployment target safety | Open / P1 | Guard cleaning arbitrary local targets; check `htm`/`html` spelling. |
| Production cache policy and remote exact sync | Deferred | Operational maturity. |

---

## 7. Priority View

```text
Completed
  Contents / PAPanel / Notes model and rendering
  removal of the obsolete G1 compatibility seam
  modular browser runtime activation
  canonical single-shell Navigation/runtime links, implemented and verified
  QuickLinks model and rendering in NavigationBar

Immediate decided patch
  add conspicuous development warning to Banzuke Changes while its present
  out-of-window testing behaviour remains accessible in development output

P0
  whole-site publication coherence as one grouped item:
    implement Banzuke Changes production availability handling
    enforce coherent selected-History publication for directly History-derived
    copied PAs
    decide whether --prod remains the production-coherence switch
    carry enough data-instance identity/provenance to enforce or explain policy

Next independent observed defect requiring triage
  Plotly line-chart Pages can display empty chart frames with no traces;
  establish scope/cause and promote priority if reproducible on promoted Pages

Deferred model follow-up
  decide later whether the runtime table chrome/body split needs promotion into
  an explicit PA model concept
  preserve the distinction between ranked table-like views and neutral sortable
  table-browser views

P1
  add local deployment target-safety protection
  follow through on further producer integrations after the P0 policy and
  Banzuke Changes slice

P2
  settle the remaining open rendering choices
  consider documentation chunking for LLM-manageable orientation
  consider code chunking for LLM-manageable maintenance
  refine build metadata/runtime/output conventions
  centralise repeated page-level runtime structure where worthwhile

P3
  production cache policy
  remote exact-sync/deployment maturity
  durable published-link compatibility policy
  richer PG extensions only where promoted public need requires them
```

---

## 8. Summary

The Notes/PAPanel, sortable-column, notes-panel and canonical-link corrections
are complete and verified.

The active publication-coherence issue is now more accurately defined. Banzuke
Changes is a Page for a newly published successor banzuke before results enter
History; it is not an arbitrary historical comparison Page. Production must
only expose it when its successor-input condition is met, while development may
temporarily keep it accessible for regression testing provided a conspicuous
warning makes that exception visible.

Other copied History-derived PAs remain subject to the broader Selected-History
coherence audit. A separate Plotly empty-trace defect remains open for triage.
A future explicit PA model for table chrome/body separation remains deferred
unless real pressure appears.
