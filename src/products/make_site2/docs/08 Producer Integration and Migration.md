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
- When does an existing legacy/prototype output qualify for promotion?
- What legacy evidence must be retained, corrected or rejected during
  migration?

Migration shall not be treated as copying old output into a new shell. A Page is
migrated into normal `make_site2` publication only when it is represented
through the active public specification, models, rendering path and static
output workflow.

---

## 2. Core Boundary

The central responsibility boundary is:

```text
Producer:
  owns analytical computation and domain meaning.

make_site2:
  owns deliberate public publication of that meaning through the specified
  public-site structure.
```

Producers determine matters such as:

- what source data means;
- how analytical results are computed;
- which values, columns, traces, categories or sections are meaningful;
- which public labels and caveats correctly describe the analysis;
- which provenance facts are meaningful to readers;
- which site-facing material can validly support a public PA.

`make_site2` determines matters such as:

- public site identity and Navigation;
- Page declarations and public status;
- publication planning;
- public selection and reproducible view handling;
- resolution into `PG` and the Public UI Model;
- PAPanel, Filter and Notes presentation;
- shared PA-terminal rendering policy;
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
- renderer-kind information where specialised PA rendering is justified.

The exact transport representation is not fixed here. It may be a Python object,
structured generated data, CSV/tabular input, JSON-like material, structured
prose or another deliberate project-local representation.

The decisive test is not format. It is intent and adequacy:

```text
Can this material be used to construct the intended public PA and its declared
public relationships without reverse-engineering meaning from old rendered
output?
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
- legacy JavaScript or CSS associated with a former page.

Such material may be evidence during evaluation or migration. It becomes a
site-facing input only by deliberate adoption under the active requirements and
model boundaries.

---

## 5. Producer Execution and Site Assembly

A public-site workflow may prepare producer material before assembling the
static site.

Conceptually:

```text
prepare or obtain required producer site-facing inputs
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
  produces or refreshes analytical publication inputs.

Site assembly:
  consumes those inputs to construct the planned, modelled and rendered site.
```

Whether the first ordinary build command runs producers, consumes already
prepared inputs, or supports both modes is an implementation decision to be
settled under real workflow pressure.

---

## 6. Publication Planning and Input Resolution

The Site Definition identifies intended Page publication sources. The
Publication Plan resolves which Pages a particular build requires and which
site-facing inputs, data and assets those Pages need.

Producer integration shall supply or validate those required inputs. It shall
not make Page inclusion accidental by scanning for whatever producer outputs
happen to exist.

For an included promoted Page:

```text
Site Definition:
  declares the Page and its intended publication source.

Publication Plan:
  resolves that the Page is included and identifies required inputs.

Producer integration:
  ensures the required intentional inputs are available.

Public UI / Published Artifact model resolution:
  interprets those inputs as a PG-conforming visible page and PA meaning.
```

Where a required promoted input is absent, incomplete or contradictory, the
normal outcome is a blocking build/integration failure rather than guessed or
empty public output.

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
- page-specific global theme/layout rules that escape rendering policy.

Promotion does not require old producer output to be deleted. It requires the
public site to consume a deliberate, model-compatible publication input.

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
7. Which visible behaviours from the old output express real analytical meaning
   and must be retained or considered?
8. Which old behaviours are merely incidental implementation/styling and need
   not be retained?
9. What rendering/audit work is required for the new public presentation?
10. What data, runtime, build and deployment support is needed?

Migration is complete only when the public material travels through the active
publication, model, rendering and output path. A visual resemblance to legacy
output alone does not demonstrate migration.

---

## 9. Legacy `make_site` as Evidence

The old `src/products/old/make_site` product is evidence, not design authority.

It may provide useful evidence about:

- previously available public material;
- reader-visible PA features;
- Navigation or Page candidate ideas;
- producer data sources and orchestration needs;
- public labels, Notes or caveats worth preserving;
- runtime and deployment practicalities;
- regressions introduced in rewriting a Page;
- page-specific styling or architecture problems to avoid.

Legacy evidence must be assessed against the active Requirements,
Specification, Models and Rendering Design.

For example, legacy evidence may reveal that a Banzuke Changes direction feature
was visible in the old public presentation and missing in a rewrite. That is
useful evidence for deciding whether the new PA model/rendering is incomplete.
It does not mean that all old markup, styling or surrounding page structure is
normative.

Code may be copied or adapted only after identifying the active responsibility
it continues to implement.

---

## 10. Archived Documentation and Prototype Evidence

The archived `make_site2` documents and any earlier UI-model experiments are
also evidence rather than competing active specification.

They may help identify:

- known Page and PA candidates;
- useful model concepts;
- earlier implementation decisions;
- deferred pressure cases;
- Notes/Filter relationships;
- already-discovered regressions or workflow needs.

Where archived material conflicts with the active documentation, the active
Requirements, Specification and agreed Design documents govern the new product.
Useful archived ideas should be adopted explicitly rather than inherited by
accident.

---

## 11. Producer-Owned Meaning and Rendering-Owned Presentation

Producer inputs should expose semantic facts needed for public presentation.
They should not generally dictate global site presentation.

### 11.1 Producer-Owned Semantic Material

Examples include:

- a column is rank, direction, rating, rikishi identity or movement magnitude;
- a chart series is observed or modelled data;
- a section represents a particular public analytical grouping;
- a particular label is correct public wording;
- a Note applies to a particular visible feature;
- a link has a particular domain meaning;
- a caveat/provenance fact is required for correct interpretation.

### 11.2 Rendering-Owned Shared Presentation

Examples include:

- NavigationBar and ContentPanel layout;
- Navigation spacing and shared styling;
- shared Page-heading treatment;
- Filter panel presentation;
- Notes-panel treatment;
- shared table cell padding and row differentiation;
- ordinary chart container presentation;
- theme values and general colour/typography policy.

### 11.3 The Grey Area

Some PA-visible treatments are informed by producer-owned meaning but decided in
Rendering Design. For example, a Banzuke Changes PA may declare movement
direction as a visible analytical feature; Rendering Design decides how that
feature is displayed consistently and legibly.

Producer integration shall provide enough meaning for such choices to be made
responsibly. It shall not solve the issue by exporting entire pre-styled pages
whose visual claims cannot be traced to the active model and Rendering Design.

---

## 12. Labels, Notes and Provenance

Labels, Notes and provenance are often producer-owned in meaning because the
producer knows what its analysis says and which caveats apply.

A producer site-facing input should provide public-facing explanatory material
where generic site assembly cannot correctly infer it, including where relevant:

- column or trace labels;
- Notes applying to a PA or visible PA feature;
- caveats associated with Filter-selected views;
- data/source provenance;
- model/method provenance;
- sample-size or reliability limitations;
- definitions needed to interpret the analytical display.

`make_site2` owns the consistent public placement and rendering of Notes and
provenance under the Public UI and Rendering Design. It shall not invent domain
explanations by guessing from internal field names or old markup.

---

## 13. Links and Domain Behaviour

Producer site-facing inputs may declare link meaning where a PA contains
domain-relevant links, for example a rikishi-name link or a link to related
public material.

Where common link behaviour is intended across PAs, it should be represented and
rendered consistently rather than reimplemented independently in each producer
or custom PA renderer.

A legacy link behaviour should be adopted only if it remains intended public
behaviour, not merely because old output included an anchor element or script.

---

## 14. Migration Classes

Not all known material should follow the same path. Candidate migration material
should be classified explicitly.

| Class | Meaning | Normal migration consequence |
| --- | --- | --- |
| Promoted public Page | Required normal public material | Must satisfy active public specification and shared publication path. |
| Candidate | Potential public material under evaluation | May be developed or previewed without defining normal public contract. |
| Research | Public or semi-public analytical depth where deliberately supported | Requires explicit treatment and status. |
| Diagnostic | Maintainer/testing material | Not ordinary public publication. |
| Legacy | Preserved former output or behaviour | Evidence or explicit legacy exposure only. |
| Superseded | Replaced material | Omitted unless a specific historical need exists. |
| Excluded | Not public material | Shall not enter normal public build. |

Migration shall not promote a Page implicitly simply because work has begun on
it or because its legacy output is visually attractive.

---

## 15. Migration of PA Families

Migration should be evaluated by PA requirements rather than solely by former
file/page layout. Candidate families include:

- ordinary table PAs;
- indexed table PAs;
- chart PAs;
- sectioned table PAs;
- prose/methodology PAs;
- justified custom-artifact PAs.

Migrating at least one real Page of each required family helps establish the
shared PA-model and rendering policy for later Pages. It also reveals where a
new PA feature or richer public structure is genuinely necessary.

---

## 16. Current Pressure Cases

The following cases are useful integration/migration pressure tests. Their
status and order are not established merely by inclusion here.

### 16.1 Basho Results / BRB

A likely indexed-table case, useful for demonstrating:

- indexed/static data supply;
- public Filters selecting data instances;
- runtime restoration of a material view;
- shared table rendering;
- complete end-to-end producer-to-public-site flow.

### 16.2 Banzuke Changes

A custom-artifact/table-like case, already useful for revealing migration and
rendering-audit issues, including:

- banzuke-style and scan-style presentation;
- movement direction as a visible PA feature distinct from optional numeric
  magnitude;
- rank-display semantics;
- optional visible detail controlled through Filters;
- shared table readability rules versus PA-specific meaning.

### 16.3 Ordinary Chart Material

At least one ordinary chart Page is needed to establish chart PA input and
shared rendering/runtime requirements without importing standalone chart HTML as
its public contract.

### 16.4 Sectioned or Prose Material

A real sectioned-table or prose PA will test whether the initial PA terminal
forms and Notes/provenance treatment are adequate for explanatory analytical
material.

### 16.5 Richer-Structure Pressure

A legacy/prototype Page that appears to need multiple simultaneous PAs, nested
Filter scope or selected alternative layouts should be treated as pressure on
the specification/model. It shall not be promoted through renderer-local
structure merely to complete migration quickly.

---

## 17. Suggested Migration Sequence

A sensible provisional migration sequence is:

```text
1. Complete and audit the existing promoted/custom-table pressure case:
   Banzuke Changes.

2. Establish an indexed-table end-to-end producer integration case:
   Basho Results / BRB.

3. Establish an ordinary shared table case.

4. Establish an ordinary chart case.

5. Establish a sectioned-table or prose case.

6. Evaluate richer-structure cases only once the ordinary PG/PA path is stable.
```

This sequence is not normative. It should change where real implementation or
public-priority evidence suggests a better route. The principle is to use real
Pages to validate shared boundaries before scaling migration widely.

---

## 18. Migration Completion Criteria

A Page may be regarded as migrated to the normal `make_site2` publication path
when it has:

- a deliberate PageDefinition and PublicStatus;
- intended Navigation/public-selection treatment;
- deliberate producer site-facing input or approved publication source;
- Publication Plan resolution;
- a Public UI Model representation conforming to approved public structure;
- a Published Artifact Model representation;
- shared Rendering Design treatment, with any PA-specific rendering declared at
  the PA boundary;
- required browser runtime/data support;
- static BuildOutput suitable for local inspection and intended deployment;
- successful rendering audit for material visible behaviour.

For a promoted Page, completion also normally requires that it no longer relies
on iframe content, copied standalone legacy HTML, private page-shell rendering
or hidden unmodelled presentation rules.

---

## 19. Handling Non-Migrated Material

Non-migrated material may remain in the repository or remain useful for
comparison, research, diagnosis or historical reference.

It shall not appear as normal promoted public content merely because it remains
available to a build script or because a link to it would be convenient.

Where non-migrated material is deliberately exposed in a development, preview or
legacy context, its PublicStatus and limitations shall be explicit and it shall
not establish normal rendering or public-model precedent.

---

## 20. Integration with Build Modes and Runtime

Different build modes may require different producer preparation or data staging.
For example, a local inspection build might consume a deliberately restricted
set of data instances to speed iteration, while a public build requires complete
promoted material.

Such optimisation is acceptable only when it is explicit and does not confuse a
reduced local test build with complete public publication.

Producer integration may determine which site-facing inputs are prepared or
available. `07 Build, Output and Runtime Design.md` owns the staging of resolved
inputs into static output and runtime loading/restoration behaviour.

---

## 21. Integration Failures

Producer integration shall report contradictions directly rather than allowing
invalid public output to be assembled.

Blocking failures include, where applicable:

- a promoted PlannedPage requires an unavailable site-facing input;
- a producer input omits a public semantic fact required by its PA model;
- a producer declares a PA feature or terminal form not supported by the active
  model/design without an approved extension;
- a required data input is inconsistent with declared public labels, Filters or
  Notes;
- a planned public Page depends only on legacy rendered HTML where deliberate
  site-facing input is required;
- a producer/runtime dependency required by the plan is not available for
  output.

Failures should identify the Page/PA/input relationship concerned so that the
problem can be corrected at its owning layer.

---

## 22. What Producer Integration and Migration Does Not Own

This layer does not own:

- the requirements for the public site;
- the definition of `PG`;
- public-page rendering layout or theme policy;
- the public UI ownership of Filters, PAPanel or Notes;
- deployment execution;
- arbitrary changes to analytical computation under the guise of migration.

Its role is to connect producer-owned analytical meaning to the deliberate
public publication path and to migrate real material without bypassing the
active design.

---

## 23. Deferred Questions

The following questions remain deferred until implementation pressure requires
settled choices:

- exact producer-preparation API or command pattern;
- whether normal `make_site2` commands invoke producers or consume already
  prepared site-facing inputs by default;
- exact site-facing input serialization/interchange format;
- whether a durable manifest-like interchange representation becomes useful;
- exact data staging/caching strategy for public and local inspection builds;
- exact first complete indexed-table/chart/prose integration cases;
- which existing legacy Pages should be promoted, retained under explicit
  status, or excluded;
- how much legacy comparison tooling is needed during migration;
- whether restricted date/data-range producer preparation is provided for local
  iteration.

Deferred questions shall not be answered silently by adopting incidental legacy
file structures or bespoke renderer paths.

---

## 24. Summary

Producer Integration and Migration connects analytical computation to deliberate
public publication.

It says:

```text
producers own analytical meaning and supply intentional site-facing material
make_site2 owns the coherent public-site publication path
promotion requires active models and shared rendering/output paths
legacy/prototype material is evidence, not authority
migration evaluates and represents public meaning rather than copying old pages
```

This boundary permits `make_site2` to publish rich real analytical material
without allowing producer outputs, legacy pages or one-off migration shortcuts
to redefine the public site outside `PG` and the active design documents.