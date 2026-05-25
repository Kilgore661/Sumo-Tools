# Second `make_site2` Review

## Status

Current review of `src/products/make_site2` against the replacement active
documentation set drafted in May 2026, updated after the first corrective work,
canonical-link implementation and discovery of the Selected-History coherence
failure.

This review is comparative. It records corrected findings as completed, names
current code/design mismatches, and orders the remaining work. Supporting detail
for the new data-coherence finding is recorded in:

```text
10.1 Selected History Coherence Audit.md
```

The `PAPanel`/Notes correction and modular-runtime activation have been checked
through the normal local build/deploy inspection workflow and reported as
working. The canonical single-shell public-link correction has fixed the
reported right-click/new-tab 404, but its wider verification checklist remains
to be completed. The Selected-History coherence rule is now specified and
designed; its implementation remains the active P0.

---

## 1. Active Documentation Baseline

The active documentation now establishes:

```text
01 Requirements
  The public site must remain coherent as analytical artefacts are added.

02 Specification
  PG specifies the full visible page; public material views have canonical
  copyable links; a selected History governs History-dependent published
  material throughout a build.

03 Architecture and Design Thesis
  Promoted public material is represented in explicit models before rendering.

04 Model Design
  Site Definition, Publication Plan, Public UI Model and Published Artifact
  Model have distinct responsibilities.

05 / 06 Rendering
  Rendering is an auditable realisation of modelled relationships and declared
  presentation policy.

07 Build, Output and Runtime
  One static application shell delivers canonical public-view links and stages
  only coherent selected-data-instance material.

08 Producer Integration and Migration
  Producers own analytical computation; make_site2 publishes only deliberate,
  coherent site-facing inputs.

10 / 10.1
  Remaining issues and the Selected-History evidence/audit are recorded
  explicitly.
```

The governing page structure is:

```text
PublicUI -> NavigationBar . ContentPanel
NavigationBar -> <site caption> . Navigation . <hider>
ContentPanel -> Heading . Contents
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

The governing public-link policy is:

```text
one static application shell
canonical link = selected Page + all applicable material Filter values
Navigation link = canonical default view of the selected Page
```

The governing build/data-instance policy is:

```text
An explicit History input selects the History/data instance for the whole built
site.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.

A canonical view link does not ordinarily freeze the History/data instance of a
later deployment; each individual built site must nevertheless be internally
coherent.
```

---

## 2. Current Implementation Areas Considered

```text
models.py
site_definition.py
navigation.py
publication_model.py
ui_model.py
artifact_model.py
site_manifest.py
manifest/
  filters.py
  artifacts.py
  builder.py
render.py
runtime/site.css
runtime/site-refactor/
build.py
data_output.py
routes.py
deploy.py
__main__.py
```

Material changes since the initial review include:

- activation of the modular ES-module browser runtime;
- explicit `Contents`, `PAPanel` and `Notes` representation in `ui_model.py`;
- rendering of Notes inside the PA-owned region;
- split manifest declarations behind a stable `site_manifest.py` facade;
- direct assembly of `PAPanel` without the old `G1` compatibility seam;
- plan-driven inclusion of visible panels/exported artefacts;
- canonical single-shell Navigation-link generation and runtime URL writing.

---

## 3. Overall Assessment

The codebase remains a suitable basis for continued development rather than
replacement. The first review cycle has removed the principal structural drift
between the new documentation and the visible page implementation.

The original top-priority structural defect is complete:

```text
formerly
  Notes were outside the PA-owned region and the active model retained an inner
  G1 contents story.

now
  ContentPanel contains Contents; Contents contains optional FilterSection and
  PAPanel; PAPanel contains PA and Notes; runtime renders that relationship.
```

The next link/output defect has been implemented and partly verified:

```text
formerly
  anchors advertised unwritten route-local entry files.

now
  anchors and runtime use canonical single-shell Page-plus-Filter state links;
  the reported open-in-new-tab 404 has been eliminated.
```

Testing that correction exposed the new active P0:

> `build_site(...)` accepts an explicit `History`, but currently passes it only
> into Basho Results. Other included promoted PA inputs are copied from
> pre-existing outputs without validation against that selected History. A build
> from history ending at `1980_11` therefore displayed correct `1980_11` Basho
> Results alongside incorrect current/2026 Banzuke Changes data.

This is more serious than a visual or routing defect: it can produce a
successful-looking public site whose promoted analytical Pages disagree about
which data instance the site publishes.

---

## 4. Summary of Current Findings

| Priority | Finding | Current assessment |
| --- | --- | --- |
| Done | `Contents`, `PAPanel` and `Notes` are explicitly modelled; Notes render within the PA region. | Central `PG` structural nonconformance corrected and locally verified. |
| Done | The former `G1` compatibility seam and monolithic manifest declaration/assembly file obscured the active model. | Manifest split complete; model constructed directly. |
| Done | The monolithic browser runtime impeded manageable change. | Modular ES-module runtime activated and working locally. |
| Implemented; verification outstanding | Navigation links advertised unwritten route-local pages. | Canonical single-shell links implemented; reported new-tab 404 fixed; remaining browser tests pending. |
| **P0** | Explicit-History builds mix coherent and unrelated copied promoted PA data. | Rule now specified/designed; enforcement and first producer integration outstanding. |
| P1 | Planning does not yet drive all producer/data staging dependencies. | The History P0 is the first concrete consequence; mature incrementally from producer cases. |
| P1 | Runtime PA-renderer branches repeat ContentPanel/PAPanel assembly. | Drift/scaling risk remains, though repeated shape is now correct. |
| P1 | All current Pages remain `PROMOTED` despite incomplete data-instance integration policy. | Status/inclusion review remains necessary. |
| P1 | Local deployment cleaning lacks intended-target safety validation. | Operational safety improvement required. |
| P2 | Heading typography, Rank-cell semantics, Notes visual/dimension policy and context-colour meaning remain unsettled. | Independent deliberate design choices. |
| P2 | Some PA metadata mixes analytical/provenance and rendering/runtime hints. | Clarify under real PA migration pressure. |

---

## 5. Public UI Model and Rendering Corrections (`02`, `04.3`, `05`, `06`)

### 5.1 Corrected Relationship

The implementation now directly models and renders:

```text
PublicSiteShell
  NavigationBar
  ContentPanel
    Heading
    Contents
      FilterSection?
      PAPanel
        PA
        Notes
```

`NavigationBar` is retained as the accepted public-model term. The obsolete
inner-content `G1` arrangement and compatibility adapter have been removed.

### 5.2 Corrected Notes Rendering

Rendered Contents now has the relationship:

```html
<div class="content-body">
  <!-- optional FilterSection -->
  <section class="pa-panel">
    <div class="pa-slot">...</div>
    <aside class="notes-panel">...</aside>
  </section>
</div>
```

Visible Notes are restricted to the Note ids owned by the visible `PAPanel`.
This is structural conformance, not merely styling improvement.

### 5.3 Remaining Rendering Decisions

These are open but no longer P0 defects:

- Notes-panel maximum height, overflow and visual framing;
- heading typography ownership;
- semantic/visible treatment of Banzuke Changes central Rank values;
- whether local/remote/preview page-background colours are an intended context
  cue.

---

## 6. Public Selection and Canonical Links (`02`, `04.2`, `07`)

### 6.1 Former Mismatch and Implemented Correction

The former implementation exposed route-local hrefs such as:

```text
current-sumo/standings-by-wins/index.html
```

while the build writes one root `index.html`. Ordinary click behaviour appeared
to work only because runtime intercepted the link.

The current implementation now generates Navigation destinations from Page
identity and declared default Filter state and writes canonical runtime URLs in
the single application shell. For example, the built Standings by Wins link is
now of the form:

```text
?page=standings_by_wins&view=standard&num_basho=6&current_only=true&division=makuuchi
```

After rebuild/deployment, the originally reported right-click/open-in-new-tab
404 no longer occurs.

### 6.2 Remaining Closure Checks

The canonical-link issue should remain marked **implemented; verification
outstanding** until these are checked:

```text
filtered table Page copied and reopened
filtered chart Page copied and reopened
Page change after filtering removes irrelevant stale parameters
reload restores the same selected public view
browser back/forward restores coherent public views
incomplete or invalid incoming state normalises predictably
```

### 6.3 Clarified Meaning of Links and Data

The link decision does not require immutable snapshot links for all published
source data.

For Banzuke Changes, a canonical default link correctly means:

```text
show the selected view of latest-basho changes in the History published by this
built site
```

A later coherent deployment may show later latest-basho changes through the same
link. Conversely, if a Page exposes a reader selection such as a fixed basho,
that Filter value belongs in its canonical public view state.

---

## 7. Active P0: Selected-History Coherence (`02`, `04.2`, `07`, `08`, `10.1`)

### 7.1 Observed Failure

Using:

```text
--history-zip '.\files\output\Historys\1978_01 to 1980_11.zip'
```

produced a site in which:

```text
Basho Results
  correctly used the selected History and displayed the latest basho as
  1980_11.

Banzuke Changes
  copied pre-existing current/full-history material and displayed 2026 data.
```

### 7.2 Code Cause

`build.py` resolves one `resolved_history`, then invokes:

```python
build_basho_results_data_output(history=resolved_history, ...)
```

but invokes the remaining PA paths as copying operations without that History,
including:

```python
copy_banzuke_changes_data_output(output_root=output_root)
copy_standings_by_wins_data_output(output_root=output_root)
copy_finish_by_chii_data_output(output_root=output_root)
copy_rank_at_retirement_data_output(output_root=output_root)
copy_career_length_data_output(output_root=output_root)
```

Banzuke Changes copies from `files/output/bcr/...`; other copied sources include
paths naming current/latest or `1958_01_to_2026_05` / `1958_2026` material.

### 7.3 Current Audit Assessment

| Assessment | Pages / PAs |
| --- | --- |
| Conforming for explicit History selection | Basho Results |
| Demonstrated or plainly nonconforming in the restricted-history case | Banzuke Changes; Finish by Chii; Rank at Retirement; Career Length |
| Not proven coherent because copied input is not derived from or validated against selected History | Standings by Wins; Banzuke Division by Era; Makuuchi Rank by Era; Division Stability; First Chii Appearance; Typical Equelo Ratings; Win Probability by Standing |

### 7.4 Rule Now Incorporated

The active documents now require:

```text
An explicit History input selects the History/data instance for the whole built
site.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.
```

Planning must treat incoherent required input as blocking unless explicit
non-public/inspection policy permits reduced inclusion. Output must not stage
convenient but unvalidated copied material as coherent. Producer integration
must preserve the boundary that producers compute analytical material and
`make_site2` validates/stages/publishes it.

### 7.5 Next Implementation Decision and Investigation

There are two legitimate immediate enforcement paths:

```text
Policy A
  Prepare or validate all included History-dependent PAs before allowing an
  explicit-History build to succeed.

Policy B
  Fail or explicitly omit unsupported PAs under explicit-history builds while
  integrating producers one by one.
```

The documented recommendation is to use Policy B as the immediate safety rule
and investigate/integrate Banzuke Changes first. The next technical task is to
inspect the Banzuke Compare producer boundary for a History-consuming
preparation path or validation identity, without reimplementing its analysis in
`make_site2`.

---

## 8. Site Definition and Publication Planning (`04.1`, `04.2`)

The explicit Site Definition, Page statuses, subject-led Navigation and
`PublicationPlan` layer remain sound foundations. Manifest assembly now maps
planned Pages to visible panels/exported artefacts and generates canonical
Navigation links.

The new P0 reveals the remaining planning gap: the plan/build path does not yet
resolve or validate the selected data instance required by all included
History-dependent PA inputs. This is no longer a merely abstract maturation
item; it is the immediate build-contract correction.

All currently declared Pages remain `PROMOTED`. That status should later be
reviewed against the ability to supply coherent data in relevant build modes,
not only against whether the UI can render a copied output.

---

## 9. Published Artifact and Producer Boundaries (`04.4`, `08`)

The current PA model provides useful concepts including data sources, indexed
sources, table columns/groups, chart traces/axes, sectioned tables, Notes and
specialised Banzuke Changes/Standings declarations.

The Selected-History failure reinforces the producer boundary:

```text
Producer
  computes History-dependent analytical material for a selected input and may
  supply validation/provenance identity.

make_site2
  declares Pages/PAs, resolves coherent requirements, rejects incoherent input,
  renders and publishes the result.
```

Copied producer output remains acceptable only where it is deliberate
site-facing material and, where required, demonstrably coherent with the
selected build data instance. It cannot be treated as valid solely because its
CSV/JSON shape matches what the runtime can read.

Longer-term PA questions remain: specialised kinds versus broad terminal forms,
and separation of analytical provenance from rendering/runtime configuration.

---

## 10. Runtime Architecture and Build/Output (`03`, `07`)

The modular ES-module runtime has substantially reduced editing risk and made
URL, Filter, Note, table, chart and panel responsibilities inspectable. It now
supports canonical public-view URL writing.

The runtime still repeats common page/PAPanel assembly in specialised renderer
functions; this is later scaling/drift work rather than a current correctness
failure.

`build.py` is now the locus of the active P0 because it combines one PA built
from `resolved_history` with multiple copied PA data outputs whose relation to
that History is not validated. Build metadata identifying selected History and
per-PA derivation/validation may become useful, but validation/enforcement comes
first.

---

## 11. Deployment and Other Operational Findings (`09`)

Existing commands support build-only, local deployment, remote SFTP deployment
and deployment of existing output. These broadly align with the operations
design.

Two concrete operational matters remain P1:

1. check the documented local target spelling (`A:\local\htm\sumo-tools2`)
   against the current code value (`A:/local/html/sumo-tools2`); and
2. add clean-target safety validation before treating arbitrary CLI-supplied
   local roots as safe for destructive replacement.

Neither should be mixed into the Selected-History producer/data correction.

---

## 12. Additional Specific Findings Still Open

### 12.1 Page Summary Containing Escaped HTML

The `first_chii_appearance` Page summary includes embedded HTML anchor markup,
while runtime escapes summaries as text. This should eventually be corrected as
plain text or modelled deliberately as structured framing; escaped HTML in a
summary string is not a valid link implementation.

### 12.2 Home/Landing Presentation

Runtime landing behaviour remains outside the declared Page set and displays
site context. Since home/landing policy is still open, this remains provisional
rather than a blocker. The root shell URL must not become an alternative
canonical link for a material selected-Page view.

---

## 13. Recommended Sequence From Here

### Completed or Implemented Pending Closure Checks

```text
Activate modular runtime without intended behaviour change.
Correct active terminology to NavigationBar.
Model Contents / PAPanel / Notes explicitly.
Render Notes within PAPanel and verify locally.
Split manifest declarations behind a stable facade and remove the G1 seam.
Specify and implement canonical single-shell Page-plus-Filter links.
Verify the reported new-tab/404 defect is fixed.
Specify/design the Selected-History whole-build coherence rule.
```

### Active P0

```text
Settle immediate enforcement policy for explicit-History builds.
Inspect the Banzuke Compare producer boundary.
Integrate or validate Banzuke Changes against resolved_history.
Prevent a successful explicit-History build from silently including other
unvalidated History-dependent promoted material.
```

### Outstanding Closure Check

```text
Complete the remaining canonical-link browser verification and update its final
status in the central documents.
```

### Later Work

```text
Resolve independent rendering choices.
Review Page promotion/build-mode inclusion policy.
Add deployment target-safety validation.
Reduce repeated runtime page/PAPanel assembly when worthwhile.
Mature plan-driven data dependencies through further real producer cases.
```

---

## 14. Conclusion

The first correction cycle has corrected public-structure drift and replaced
invalid route-local live links with a coherent single-shell public-state design.
That link change is implemented and has fixed the defect which exposed it,
although its full verification closure remains outstanding.

That verification uncovered a deeper active P0: `make_site2` currently allows an
explicit selected History to govern only Basho Results while other promoted
History-dependent Pages can publish unrelated copied data. The project has now
recorded and incorporated the correct rule: a selected History governs the
whole built site's dependent promoted material, with producers responsible for
analytical computation and `make_site2` responsible for coherent publication.

The next task is therefore not more page styling or URL design. It is to enforce
that rule safely, beginning with the Banzuke Changes producer boundary and with
an explicit policy preventing misleading mixed-history builds during incremental
integration.