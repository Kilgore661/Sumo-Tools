# 08 Producer Integration and Migration

## Status

Draft design document for producer integration and migration in
`src/products/make_site2`.

This document defines how analytical material enters the public-site workflow
and how existing material is assessed for migration into the active
`make_site2` design.

It is downstream of the Requirements, Specification and Model Design, and it is
consistent with the boundary established in:

```text
04.4 Published Artifact Model.md
04.5 Basho Results Model.md, for the specialised Basho Results (7.1) case
07 Build, Output and Runtime Design.md
```

It does not redefine `PG`, public-page rendering policy, Published Artifact
meaning, build-output structure or deployment operations.

---

## 1. Purpose

`make_site2` publishes deliberately selected analytical material supplied by
Sumo-Tools producers.

Producer integration shall answer:

- Which analytical material is intended for public publication?
- Which producer owns its meaning and computation?
- What site-facing input is required to construct a public Page and PA?
- How is that input prepared or obtained for a build?
- Where a build selects a History/data instance, how is each History-dependent
  promoted PA derived from or validated against that selected instance?
- When does an existing legacy/prototype output qualify for promotion?
- What legacy evidence must be retained, corrected or rejected during
  migration?

Migration shall not be treated as copying old output into a new shell. A Page is
migrated into normal `make_site2` publication only when it is represented
through the active public specification, models, rendering path and static
output workflow, using coherent site-facing input for the selected build.

---

## 2. Core Boundary

The central responsibility boundary is:

```text
Producer:
  owns analytical computation and domain meaning, including computation from a
  selected History/data instance where its PA depends on History.

make_site2:
  owns deliberate coherent public publication of that meaning through the
  specified public-site structure.
```

Producers determine matters such as:

- what source data means;
- how analytical results are computed;
- how a selected History or data instance affects those results;
- which values, columns, traces, categories or sections are meaningful;
- which public labels and caveats correctly describe the analysis;
- which provenance/data-instance facts are meaningful or required for
  validation;
- which site-facing material can validly support a public PA.

`make_site2` determines matters such as:

- public site identity and Navigation;
- Page declarations and public status;
- publication planning;
- public selection and reproducible view handling;
- resolution into `PG` and the Public UI Model;
- PAPanel, Filter and Notes presentation;
- shared PA-terminal rendering policy;
- requiring coherent inputs for the Selected History/data instance of a build;
- static output and runtime assembly;
- deployment workflow.

This boundary allows producers to remain analytically authoritative while the
public site remains coherent as a publication product.

---

## 3. Producer Site-Facing Inputs

A producer site-facing input is deliberate material supplied for public
publication rather than an incidental computation artefact.

A site-facing input may contain or refer to:

- public data values;
- PA terminal-form information;
- visible column, trace, section or feature declarations;
- public labels;
- valid public Filter relationships and defaults;
- Notes or caveats;
- provenance;
- public links or domain-link semantics;
- required data/assets;
- PA-specific consistency requirements;
- renderer-kind information where specialised PA rendering is justified;
- selected-History/data-instance identity or other validation information where
  the PA depends on History.

The exact transport representation is not fixed here. It may be a Python object,
structured generated data, CSV/tabular input, JSON-like material, structured
prose or another deliberate project-local representation.

The decisive test is not format. It is intent and adequacy:

```text
Can this material be used to construct the intended public PA and its declared
public relationships without reverse-engineering meaning from old rendered
output, and can it be shown to belong to the selected build data instance where
coherence matters?
```

---

## 4. What Is Not a Site-Facing Input by Default

The existence of an output does not make it a publication contract.

The following shall not be treated as normal site-facing inputs merely because
they are available:

- raw downloaded HTML;
- parser diagnostics;
- warning reports;
- debug output;
- internal caches;
- experiment snapshots;
- old standalone generated pages;
- incidental intermediate files;
- producer output directory names;
- legacy JavaScript or CSS associated with a former page;
- pre-existing analytical CSV/JSON output whose relation to the Selected
  History/data instance is unknown.

Such material may be evidence during evaluation or migration. It becomes a
site-facing input only by deliberate adoption under the active requirements and
model boundaries. For a History-dependent promoted PA in a build with a
Selected History, deliberate adoption additionally requires derivation from or
validation against that History.

---

## 5. Producer Execution and Site Assembly

A public-site workflow may prepare producer material before assembling the
static site.

Conceptually:

```text
select build History/data instance where applicable
  -> prepare or obtain coherent producer site-facing inputs
  -> resolve PublicationPlan
  -> resolve PublicUIModel and PublishedArtifactModel
  -> render
  -> write BuildOutput
  -> optionally deploy
```

A command may orchestrate more than one of these stages for convenience. That
does not collapse their ownership:

```text
Producer preparation:
  produces or refreshes analytical publication inputs from the intended source
  data instance and supplies validation identity where required.

Site assembly:
  consumes only inputs valid for the planned coherent publication.
```

Whether an ordinary build command runs producers, consumes already prepared
inputs carrying sufficient validation information, or supports both modes is an
implementation decision. However, an explicit `History` or `history_zip`
selection is not merely an override for one internally generated PA: it governs
History-dependent promoted material across that build.

---

## 6. Publication Planning and Input Resolution

The Site Definition identifies intended Page publication sources. The
Publication Plan resolves which Pages a particular build requires, which
site-facing inputs, data and assets those Pages need, and what Selected
History/data-instance coherence applies.

Producer integration shall supply or validate those required inputs. It shall
not make Page inclusion accidental by scanning for whatever producer outputs
happen to exist.

For an included promoted Page:

```text
Site Definition:
  declares the Page and its intended publication source.

Publication Plan:
  resolves that the Page is included, identifies required inputs and states
  selected-data-instance coherence requirements.

Producer integration:
  prepares or validates the required intentional inputs from/against that
  selected data instance.

Public UI / Published Artifact model resolution:
  interprets those inputs as a PG-conforming visible page and PA meaning.
```

Where a required promoted input is absent, incomplete, contradictory or not
shown to be coherent with a required Selected History, the normal outcome is a
blocking build/integration failure rather than guessed, stale or mixed-history
public output.

A deliberately reduced non-public/inspection build may omit unsupported
material only under an explicit policy that exposes the reduced scope; such a
policy has not yet been implemented.

---

## 7. Promotion

Promotion is the deliberate adoption of analytical material into the normal
public-site contract.

A promoted Page shall have, directly or through approved resolution:

- a `PageDefinition`;
- an explicit `promoted` status;
- a canonical Navigation placement or another deliberately specified public
  entry route;
- a stable public selection identity;
- sufficient site-facing producer material;
- coherent data-instance derivation or validation where its PA depends on
  History/data-instance selection;
- a Public UI Model representation conforming to approved public structure;
- a Published Artifact Model representation;
- rendering through the shared `make_site2` rendering path, with specialised
  PA rendering only within the PA boundary;
- static build output suitable for local inspection and deployment.

A promoted Page shall not normally depend on:

- iframe display of a former standalone output;
- copying an old generated HTML page as its primary content;
- parsing old HTML to recover public meaning;
- page-specific ownership of the shell, Heading, Filter/PAPanel relationship or
  Notes placement;
- page-specific global theme/layout rules that escape rendering policy;
- unvalidated pre-existing producer output where the build has selected a
  different History/data instance.

Promotion does not require old producer output to be deleted. It requires the
public site to consume a deliberate, model-compatible and build-coherent
publication input.

---

## 8. Migration as Evaluation, Not Copying

Migration is the process of deciding what existing behaviour or material should
be represented in the active design and implementing the corresponding public
path.

For each candidate legacy/prototype Page or visible feature, migration shall
ask:

1. Is this material intended for public publication at all?
2. What public question or reader need does it serve?
3. What PublicStatus should it have?
4. Can its public Page be represented by `PG`, or is specification/model work
   required before promotion?
5. What PA terminal form and PA-specific features are required?
6. What site-facing producer input is required?
7. If the PA depends on History/data-instance selection, can the producer
   prepare or identify coherent input for the selected build instance?
8. Which visible behaviours from the old output express real analytical meaning
   and must be retained or considered?
9. Which old behaviours are merely incidental implementation/styling and need
   not be retained?
10. What rendering/audit work is required for the new public presentation?
11. What data, runtime, build and deployment support is needed?

Migration is complete only when the public material travels through the active
publication, model, rendering and output path using inputs whose semantic and
build-data-instance validity are known. A visual resemblance to legacy output
alone does not demonstrate migration.

---

## 9. Legacy `make_site` as Evidence

The old `src/products/old/make_site` product is evidence, not design authority.

It may provide useful evidence about previously available public material,
reader-visible PA features, Navigation/Page candidate ideas, producer data
sources and orchestration needs, public labels/Notes/caveats worth preserving,
runtime/deployment practicalities, regressions in rewriting a Page and
page-specific architecture problems to avoid.

Legacy evidence must be assessed against the active Requirements,
Specification, Models and Rendering Design. A copied old producer output does
not prove selected-History coherence merely because it reproduces a familiar
page.

For example, legacy evidence may reveal that a Banzuke Changes direction feature
was visible in the old public presentation and missing in a rewrite. That is
useful evidence for deciding whether the new PA model/rendering is incomplete.
It does not mean that all old markup, styling, surrounding page structure or
unvalidated current-data output is normative.

---

## 10. Archived Documentation and Prototype Evidence

Archived `make_site2` documents and earlier UI-model experiments are evidence
rather than competing active specification. They may help identify known Page
and PA candidates, useful model concepts, earlier implementation decisions,
deferred pressure cases, Notes/Filter relationships, already-discovered
regressions or workflow needs.

Where archived material conflicts with active documentation, active
Requirements, Specification and agreed Design govern. Useful archived ideas
should be adopted explicitly rather than inherited by accident.

---

## 11. Producer-Owned Meaning and Rendering-Owned Presentation

Producer inputs should expose semantic facts needed for public presentation and
coherence validation. They should not generally dictate global site
presentation.

### 11.1 Producer-Owned Semantic Material

Examples include:

- a column is rank, direction, rating, rikishi identity or movement magnitude;
- a chart series is observed or modelled data;
- a section represents a particular public analytical grouping;
- a particular label is correct public wording;
- a Note applies to a particular visible feature;
- a link has a particular domain meaning;
- a caveat/provenance fact is required for correct interpretation;
- the History/data-instance basis of a History-dependent analytical output.

### 11.2 Rendering-Owned Shared Presentation

Examples include NavigationBar and ContentPanel layout, Navigation spacing,
shared Page-heading treatment, Filter-panel presentation, Notes-panel treatment,
shared table density/row differentiation, ordinary chart-container presentation,
and general theme/colour/typography policy.

### 11.3 The Grey Area

Some PA-visible treatments are informed by producer-owned meaning but decided in
Rendering Design. For example, a Banzuke Changes PA may declare movement
direction as a visible analytical feature; Rendering Design decides how that
feature is displayed consistently and legibly.

Producer integration shall provide enough meaning and data-instance identity for
such choices to be made responsibly. It shall not solve either presentation or
coherence by exporting entire pre-styled or pre-existing outputs whose public
claims cannot be traced to active model/design/build context.

---

## 12. Labels, Notes and Provenance

Labels, Notes and provenance are often producer-owned in meaning because the
producer knows what its analysis says and which caveats apply.

A producer site-facing input should provide public-facing explanatory material
where generic site assembly cannot correctly infer it, including column/trace
labels, Notes applying to a PA or feature, caveats associated with Filter views,
data/method provenance, sample-size limitations, definitions needed to interpret
the display, and data-instance identity required to validate a selected-History
build.

`make_site2` owns consistent public placement and rendering of Notes/provenance
and owns rejection of input that does not satisfy required build coherence. It
shall not invent domain explanations or data-instance equivalence by guessing
from internal field names, directory names or old markup.

---

## 13. Links and Domain Behaviour

Producer site-facing inputs may declare link meaning where a PA contains
domain-relevant links, for example a rikishi-name link or a link to related
public material.

Canonical Public View Links belong to the public site and identify selected
Page/Filter state against the currently published coherent data. They do not
normally freeze the Selected History of the build. Thus a canonical Banzuke
Changes default-view link may remain stable while a later coherent deployment
publishes a later latest basho.

Where common link behaviour is intended across PAs, it should be represented and
rendered consistently rather than reimplemented independently in each producer
or custom PA renderer.

---

## 14. Migration Classes

| Class | Meaning | Normal migration consequence |
| --- | --- | --- |
| Promoted public Page | Required normal public material | Must satisfy active public specification, selected-data-instance coherence where applicable and shared publication path. |
| Candidate | Potential public material under evaluation | May be developed or previewed without defining normal public contract. |
| Research | Public or semi-public analytical depth where deliberately supported | Requires explicit treatment and status. |
| Diagnostic | Maintainer/testing material | Not ordinary public publication. |
| Legacy | Preserved former output or behaviour | Evidence or explicit legacy exposure only. |
| Superseded | Replaced material | Omitted unless a specific historical need exists. |
| Excluded | Not public material | Shall not enter normal public build. |

Migration shall not promote a Page implicitly simply because work has begun on
it, because its legacy output is visually attractive or because a copyable data
file happens to exist.

---

## 15. Migration of PA Families

Migration should be evaluated by PA requirements rather than solely by former
file/page layout. Candidate families include ordinary table PAs, indexed table
PAs, chart PAs, sectioned table PAs, prose/methodology PAs and justified
custom-artifact PAs.

Migrating real Pages of required families helps establish shared PA-model and
rendering policy. It also exposes where producer/input/data-instance contracts
are missing.

---

## 16. Current Pressure Cases

### 16.1 Basho Results / BRB

Basho Results is a promoted indexed-table case demonstrating direct use of the
selected `History` in `make_site2`. In the reduced-history test it correctly
resolved its latest result to `1980_11`.

It is useful for demonstrating indexed/static data supply, public Filters
selecting data instances, canonical public-view restoration and a coherent
direct History-to-output path.

The settled 7.1 public model is now in `04.5 Basho Results Model.md`. The
current implementation uses a transitional presentation-model renderer for its
recursive reference/before/current-after/comparison table shape. That is a valid
promotion step because it remains inside the PA boundary and consumes coherent
Basho Results rows, but it does not mean the producer/input shape is final:
compact-result parsing, Banzuke Error/RBBP values and some table-model
normalisation remain tracked follow-ups.

### 16.2 Banzuke Changes

Banzuke Changes is now the immediate producer-integration P0 pressure case.

It already tests banzuke-style and scan-style presentation, movement direction,
rank-display semantics, optional visible details and shared readability rules.
It has additionally demonstrated a public data-coherence failure: a build from a
History ending at `1980_11` copied Banzuke Changes material based on current/full
history and displayed 2026 data.

The next integration investigation shall determine whether its producer already
accepts selected `History` input, can be adapted to prepare site-facing data for
such input, or can supply sufficient metadata to validate prepared output before
staging. `make_site2` shall not duplicate Banzuke Changes analysis merely to
avoid defining the producer boundary.

### 16.3 Other Copied Promoted PAs

The Selected History audit records that several other currently promoted PAs are
copied from fixed/current/pre-existing outputs and are either plainly
nonconforming for a reduced-history build or not proven coherent. Producer
integration for these PAs shall follow the enforcement policy chosen for
explicit-History builds and actual public priority.

---

## 17. Suggested Migration Sequence

The immediate sequence is now:

```text
1. Investigate and integrate Banzuke Changes selected-History preparation or
   validation as the first observed coherence failure.

2. Establish enforcement for explicit-History builds so unsupported promoted
   History-dependent PAs cannot silently publish mixed data.

3. Use the Selected History audit to prioritise remaining copied promoted PAs.

4. Continue ordinary table/chart/sectioned/prose PA maturation under real need.

5. Evaluate richer-structure cases only once ordinary PG/PA and coherent-input
   paths are stable.
```

This sequence may be refined after examining producer capabilities, but it shall
not return to treating convenient copied output as adequate evidence of build
coherence.

---

## 18. Migration Completion Criteria

A Page may be regarded as migrated to the normal `make_site2` publication path
when it has:

- a deliberate PageDefinition and PublicStatus;
- intended Navigation/public-selection treatment;
- deliberate producer site-facing input or approved publication source;
- derivation/validation against the selected build data instance where its PA
  depends on History;
- Publication Plan resolution;
- a Public UI Model representation conforming to approved public structure;
- a Published Artifact Model representation;
- shared Rendering Design treatment, with PA-specific rendering declared only at
  the PA boundary;
- required browser runtime/data support;
- static BuildOutput suitable for local inspection and intended deployment;
- successful rendering and data-coherence audit for material public behaviour.

For a promoted Page, completion also normally requires that it no longer relies
on iframe content, copied standalone legacy HTML, private page-shell rendering,
hidden unmodelled presentation rules, or unvalidated data-instance substitution.

---

## 19. Handling Non-Migrated or Incoherent Material

Non-migrated material may remain in the repository or remain useful for
comparison, research, diagnosis or historical reference. It shall not appear as
normal promoted public content merely because it remains available to a build
script or because a link to it would be convenient.

Where a selected-History build cannot prepare or validate an otherwise promoted
PA's required input, the normal public-build outcome is failure until an
explicitly designed policy states otherwise. A reduced inspection/preview build
may eventually omit or mark such material, but must not imply full coherent
public publication.

---

## 20. Integration with Build Modes and Runtime

Different build modes may require different producer preparation or data
staging. A local inspection build might use a deliberately restricted History to
speed iteration or expose data-instance defects; a public build requires
complete coherent promoted material.

Such optimisation is acceptable only when explicit and when it does not confuse
a reduced/partial inspection build with complete public publication.

Producer integration determines which site-facing inputs can be prepared or
validated. `07 Build, Output and Runtime Design.md` owns staging resolved inputs
into static output and runtime loading/restoration behaviour. Browser runtime
does not repair incoherent producer/data preparation.

---

## 21. Integration Failures

Producer integration shall report contradictions directly rather than allowing
invalid public output to be assembled.

Blocking failures include, where applicable:

- a promoted PlannedPage requires an unavailable site-facing input;
- a producer input omits a public semantic fact required by its PA model;
- a required History-dependent promoted input cannot be derived from or
  validated against the Selected History/data instance of the build;
- a producer declares a PA feature or terminal form not supported by active
  model/design without an approved extension;
- a required data input is inconsistent with declared public labels, Filters or
  Notes;
- a planned public Page depends only on legacy rendered HTML where deliberate
  site-facing input is required;
- a producer/runtime dependency required by the plan is unavailable for output.

Failures should identify the Page, PA, producer input and selected-data-instance
relationship concerned so the problem can be corrected at its owning layer.

---

## 22. What Producer Integration and Migration Does Not Own

This layer does not own the public requirements, the definition of `PG`, public
layout/theme policy, Public UI ownership of Filters/PAPanel/Notes, deployment
execution, or arbitrary changes to analytical computation under the guise of
migration.

Its role is to connect producer-owned analytical meaning and data-instance
validity to the deliberate public publication path and migrate real material
without bypassing active design.

---

## 23. Deferred Questions

The following questions remain open or deferred until producer investigation
provides evidence:

- exact common producer-preparation API or command pattern;
- whether normal builds invoke producers or consume already prepared inputs by
  default;
- exact validation identity carried by prepared site-facing input;
- whether explicit-History builds block all unsupported promoted PAs or allow
  omission only in an explicit reduced inspection mode;
- exact interchange/serialization format;
- exact data staging/caching strategy;
- which legacy Pages should remain promoted, be retained under explicit status,
  or be excluded;
- how much comparison tooling is needed during migration.

The requirement for coherent Selected-History material is not deferred. Only its
producer/API/enforcement realisation remains to be implemented.

---

## 24. Summary

Producer Integration and Migration connects analytical computation to deliberate
public publication.

It says:

```text
producers own analytical meaning and History-dependent computation
make_site2 owns coherent public-site publication and rejects incoherent input
promotion requires active models, shared rendering/output paths and coherent
  build-data-instance support where applicable
legacy/prototype/copied output is evidence, not automatically valid input
Basho Results is the current positive direct-History example, now folded into
  the 04.5 model with remaining producer-shape follow-ups tracked separately
Banzuke Changes is the first concrete selected-History integration correction
```

This boundary permits `make_site2` to publish rich analytical material without
allowing producer outputs, legacy pages, stale copied datasets or one-off
migration shortcuts to redefine the public site or combine contradictory data
instances outside the active design.
