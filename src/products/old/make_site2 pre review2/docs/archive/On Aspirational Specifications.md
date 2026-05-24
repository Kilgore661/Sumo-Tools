# Aspirational Specifications and Practical Model Boundaries

## Status

Working design note for `src/products/make_site2`.

This document records a lesson learned during review of the current `make_site2` specification, design and implementation. It is not a new general theory of UI modelling, and it does not attempt to derive this project from an external modelling framework.

Its purpose is narrower and practical:

```text
What does it mean for the make_site2 specification to be aspirational?
How should an implementation use such a specification?
When must a semantic distinction be represented in the model?
When is ordinary implementation detail sufficient?
How should review distinguish a real modelling defect from sensible restraint?
```

---

# 1. The Problem We Encountered

`make_site2` is intentionally model-led.

Its specification and design documents describe a public-site model in which meaningful UI and publication concepts are represented explicitly before rendering. Examples include:

```text
Site
Navigation
Page
ContentPanel
Heading
FilterSection
Filter
PA
Artifact
Note
```

This is the right direction. The public site should not emerge accidentally from scattered HTML, JavaScript and CSS decisions. A page should be known as a page; a filter should be known as a filter; a chart should be known as a chart; an explanatory note should have an identifiable owner.

However, a difficulty follows immediately:

```text
How far down must explicit modelling go?
```

If every visible detail must be represented as a formal semantic entity before it may be rendered, the model becomes unmanageably granular. At the extreme, the specification would need to distinguish every type of displayed primitive value:

```text
an ordinary integer
an Equelo rating represented as an integer
a basho day represented as an integer
a basho month represented as an integer
a count of rikishi represented as an integer
```

That is neither necessary nor desirable merely because those distinctions can be named.

Conversely, if the model is too coarse, the renderer starts inventing meaning. A renderer might silently decide that one control belongs under another, that one page contains several distinct visible artefacts, that a chart and table are interchangeable, or that a warning/title/status should appear without any modelled basis.

The project therefore needs a practical principle for interpreting an aspirational specification without either abandoning it or over-formalising everything.

---

# 2. What “Aspirational Specification” Means Here

An aspirational specification describes the semantic structure the project wants to make explicit, even when the first implementation has not yet needed, settled or materialised every possible distinction.

It is aspirational in this sense:

```text
it states ownership boundaries and modelling intentions
it identifies concepts that should not be hidden in arbitrary rendering code
it anticipates pressure points that may later require model refinement
it is not a requirement to turn every conceivable distinction into a class,
field, grammar production or serialized object immediately
```

This is different from saying that the specification is optional.

A specification commitment that has been deliberately made must be followed, revised or explicitly deferred. Implementation must not simply ignore it because a quicker code path is convenient.

But the specification may legitimately operate at a higher semantic level than the concrete class hierarchy. For example, it can say that pages own framing and artifacts own analytical internals without requiring a dedicated class for every formatted number displayed inside an artifact.

The implementation task is therefore not:

```text
materialise every noun in the design prose as a concrete class
```

It is:

```text
materialise enough of the semantic model that the implemented site does not
invent public meaning, ownership or structure by accident
```

---

# 3. Requirements, Specification, Design and Code

This principle does not weaken the project's normal direction of authority.

The intended order remains:

```text
requirement
  -> specification decision
  -> design
  -> implementation
  -> review against the preceding levels
```

Do not change a requirement merely because existing code has drifted from it.

Where a specification choice is reconsidered, it should be reconsidered on its own merits. If the revised specification then agrees with existing code, that is a useful confirmation, not a justification after the event.

The aspirational nature of the specification matters in a different way. It means that, during implementation or review, the question is not always:

```text
Does a concrete Python class or field exist for every concept mentioned in the specification?
```

The better question is:

```text
Does the implementation preserve the required semantic distinction and ownership
boundary at the level where it affects behaviour or public meaning?
```

---

# 4. Grammar as a Selective Type System

A useful way to think about the UI model is as a grammar or type system.

A simplified grammar might say:

```text
Contents -> FilterSection? PA Note*
PA       -> TableArtifact
          | IndexedTableArtifact
          | ChartArtifact
          | SectionedTableArtifact
          | CustomArtifact
```

This grammar distinguishes types because those distinctions matter to the application.

A table and a chart differ in ways that affect:

```text
valid internal structure
data-binding requirements
renderer selection
runtime behaviour
notes and provenance possibilities
validation rules
```

It is therefore useful and necessary to distinguish them in the model.

But the grammar does not need to descend indefinitely:

```text
ChartArtifact -> Axis Trace DataValue
DataValue     -> EqueloDigitString | BashoDayInteger | OrdinaryInteger | ...
```

A model may stop once the remaining work is ordinary rendering or artifact-local formatting, unless a further distinction becomes meaningful to the public contract.

The question is not whether a finer type could be invented. A finer type almost always can be invented.

The question is whether the distinction needs to be owned, validated, composed or interpreted by `make_site2`.

---

# 5. The Practical Cut-Off Rule

The model-to-render boundary should be expressed as follows:

> The model must represent distinctions that communicate public meaning, analytical structure, visible state, ownership, dependency, validation rules or materially different rendering/runtime contracts. Rendering may apply ordinary representational conventions to already-modelled entities and leaf values, provided it does not invent such distinctions.

This gives two categories.

## 5.1 Semantic or Interpretive Distinctions

These require model or declared-policy provenance.

Examples:

```text
this visible object is a chart rather than a table
this control is a Filter that changes the visible analytical view
this note applies only when a particular feature is visible
this control is meaningful only when another selected source is active
this page is candidate/research/promoted rather than ordinary public content
this visible item is a separate artefact rather than a local rendering choice
```

If these distinctions appear only inside JavaScript or CSS without being represented at the appropriate model/policy layer, the renderer is inventing public meaning.

## 5.2 Ordinary Representational Decisions

These do not normally require a new semantic class or grammar production.

Examples:

```text
escaping a text value before writing HTML
printing an integer as digits
formatting an already-modelled percentage using a percentage formatter
right-aligning ordinary numeric table data under a shared table convention
using site-wide spacing, borders and typography
copying already-declared runtime assets into the output tree
```

These choices realise an already-known entity. They do not, by themselves, assert new public structure or interpretation.

---

# 6. Where the Boundary Can Be Difficult

The boundary is principled, but it is not always mechanically obvious.

A visual distinction may start as harmless representation and later become semantic.

For example:

```text
right-align numeric table cells
```

is normally a renderer/table-style convention. It does not require the UI grammar to contain a production for right-aligned integers.

But:

```text
render uncertain values in grey
render provisional values with a warning marker
render promoted/demoted values in directional colours
```

may carry public analytical meaning. If that meaning matters to interpretation, it needs an owner in the Artifact Model, note/provenance model, or declared rendering policy.

Similarly:

```text
show 2137 as an Equelo rating
```

may require no more than printing a value in a modelled Equelo column.

But:

```text
show 2137 with a special category marker because it corresponds to a public
rating landmark
```

introduces interpretive meaning and should be represented accordingly.

The test is not whether the rendering is visually distinctive. Site-wide typography is visually distinctive too. The test is whether the distinction tells the reader something about structure, meaning, state or interpretation.

---

# 7. Example: PA Was Initially Too Coarse

## 7.1 Earlier Position

At an early stage, `PA` could be treated as a terminal symbol:

```text
Contents -> FilterSection? PA Note*
```

At that level the model said:

```text
there is one visible published analytical object here
```

This was sufficient while the main question was where the object appeared in the page.

## 7.2 Pressure Encountered

As real public pages were brought into the model, it became necessary to distinguish:

```text
indexed tables such as Basho Results
table-like custom displays such as Banzuke Changes
charts such as Finish by Chii
sectioned tables such as Typical Equelo Ratings
```

Those are not merely cosmetic variations. They require different data contracts, rendering behaviours and validation expectations.

## 7.3 Correct Refinement

The model therefore needed to distinguish artifact kinds below the PA slot:

```text
PA -> Artifact
Artifact -> IndexedTableArtifact
          | ChartArtifact
          | SectionedTableArtifact
          | BanzukeChangesArtifact
          | StandingsArtifact
          | ...
```

This was justified model refinement. Treating PA as an opaque leaf would have forced meaningful artifact decisions into bespoke rendering code.

## 7.4 Where Refinement Should Stop for Now

The fact that a chart contains values, labels, axes and formatted numbers does not mean every value domain must be promoted into the site grammar.

The Artifact Model may say enough when it declares, for example:

```text
this is a chart
this is its data source
this is its x-axis field
this is its y-axis field
this is its percentage tick format
```

It does not need to grammar-model every digit rendered on the axis.

---

# 8. Example: G1 and Deferred Richer Filter Structure

## 8.1 Current Simple Model

The current intended ContentPanel grammar is G1:

```text
G1Contents
  FilterSection?
  PA
  Note*
```

This gives a page a flat set of reader-visible filters controlling one visible published artefact.

That is adequate for much of the current public navigation tree.

## 8.2 Known Limitation

A flat FilterSection does not naturally express nested, hierarchical or conditionally applicable controls.

For example, a page may expose:

```text
Source: Observed | Equelo
Error bars: true | false
```

but error bars may be meaningful only when:

```text
Source = Observed
```

Under the simple G1/flat-filter model, the UI may permit:

```text
Source = Equelo
Error bars = true
```

although the latter selection has no effect or no natural meaning for Equelo data.

## 8.3 Correct Current Decision

This does not necessarily require immediate grammar expansion.

The present decision is pragmatic:

```text
keep G1 as the current model
accept that a few pages may expose awkward-but-tolerable flat filter states
defer richer structured-filter or artifact-view modelling until real public
pressure justifies the added complexity
record the richer possibilities in Appendix A
```

This is an example of an aspirational specification being bounded deliberately. The project recognises a more expressive model but does not introduce it merely because it can imagine one.

## 8.4 What Would Trigger Refinement

Refinement would become justified if the simple model causes material public problems, such as:

```text
users are repeatedly misled by invalid combinations
controls must appear/disappear or acquire different ownership based on state
notes or provenance cannot be attached honestly under the flat model
one visible PA can no longer accurately describe what the page presents
renderers accumulate bespoke conditional structure that the model cannot explain
```

At that point, a richer active model should be designed and specified first, then implemented.

---

# 9. Example: Printing a Domain Value Does Not Necessarily Need More Model

Consider three values displayed by public pages:

```text
Equelo rating: 2137
Basho day: 8
Rikishi count: 42
```

These have different domain meanings. It is possible to invent distinct value types for each of them.

But `make_site2` does not need a UI-grammar production for each simply in order to render:

```text
2137
8
42
```

The meaning may already be sufficiently represented by context:

```text
the value appears in an Equelo column
the value appears under a Basho Day label
the value appears in a Rikishi Count chart axis or table column
```

Further formalisation becomes necessary only if behaviour depends on the distinction.

Examples where further ownership might become appropriate:

```text
Basho day 8 is displayed as Nakabi throughout the public site
Equelo ratings receive consistent public threshold labels or caveat markers
rikishi counts are suppressed or qualified below a public support threshold
```

In such cases, the question is not “must every integer be a class?” It is:

```text
where should this stable public interpretation or formatting rule be owned?
```

That owner might be a domain formatter, an Artifact Model field, a note/provenance policy, or a shared renderer convention. It still need not expand the top-level UI grammar.

---

# 10. Example: Titles and Other Renderer Inventions

The same principle applies to framing text such as titles.

A renderer must not add a meaningful title merely because it makes a page look more complete. For example, if a chart renderer adds a source-identifying title such as:

```text
Observed
```

or:

```text
Equelo
```

that may assert a public framing decision. If it is important, it should come from the Page, PA or Artifact model/policy rather than appearing as bespoke renderer decoration.

However, this does not imply that every HTML heading element requires a new grammar concept. Once the model says that a Page has a Heading or that an Artifact has an optional title block, the renderer is free to realize that using appropriate HTML and shared style conventions.

The prohibited step is inventing the meaningful title, not choosing how to mark up a modelled title.

---

# 11. Review Method for Aspirational Specifications

When reviewing implementation against the `make_site2` documentation, avoid both extremes:

```text
Extreme 1:
  Treat any absent class/field as a defect because the prose specification names
  a broader semantic responsibility.

Extreme 2:
  Treat any implementation convenience as acceptable because the specification
  is aspirational.
```

Instead, apply the following questions.

## 11.1 Meaning Test

Does the implementation expose a public distinction, state, relationship or interpretation that matters to what the reader understands?

If yes, it needs an appropriate model or policy basis.

## 11.2 Behaviour Test

Does implementation behaviour vary according to a distinction that the model cannot express?

If yes, model refinement or an explicit declared policy may be required.

## 11.3 Ownership Test

Is meaningful knowledge being decided in the wrong layer?

Examples:

```text
renderer deciding analysis-specific labels
CSS expressing status not present in the model
JavaScript inventing page/control hierarchy
site builder reverse-engineering producer meaning from incidental output files
```

If yes, the boundary needs correction.

## 11.4 Validation Test

Would omission of the distinction allow invalid public states, contradictory artifacts or incoherent output to be generated without detection?

If yes, modelling/validation should probably be strengthened.

## 11.5 Restraint Test

Would introducing a new class, grammar branch or semantic entity change no public behaviour, ownership rule, validation rule or rendering contract?

If yes, do not introduce it merely for completeness.

---

# 12. Implications for Design Documents

The design documents should continue to be explicit about model ownership, but avoid wording that implies exhaustive formalisation of every visual or leaf-level choice.

A useful model-to-render invariant is:

> Rendering must not invent analytical structure, public state ownership, semantic dependency, interpretive emphasis or public distinctions that are absent from the UI Model, Artifact Model or declared rendering policy. Rendering may apply ordinary presentational conventions to already-modelled entities and leaf values, including standard typography, spacing, alignment, escaping and formatting, provided those choices do not introduce new public meaning or imply an undeclared relationship.

This preserves the important discipline:

```text
model meaningful things before rendering them
```

without turning it into the impossible rule:

```text
model every possible representational detail as a semantic type before displaying it
```

---

# 13. Implications for Implementation

The implementation should be allowed to remain pragmatic where the public contract does not require further structure.

Appropriate implementation choices include:

```text
ordinary scalar values inside modelled artifacts
shared table-rendering conventions
shared chart formatting conventions
common CSS/theme/layout tokens
artifact-local formatting details that do not introduce new analytical meaning
```

Implementation should be challenged where it accumulates meaning-bearing decisions without model or policy authority, for example:

```text
hard-coded page framing inside an artifact renderer
unmodelled conditional relationships between filters
special note visibility rules hidden only in JavaScript
status or caveat styling without declared status/caveat ownership
page-specific layout distinctions that imply analytical hierarchy
```

When such pressure appears, the response should be:

```text
identify the missing semantic distinction
choose the smallest appropriate owning layer
revise the specification/design if the active model changes
implement the revised model
```

Do not simply add local rendering patches; do not expand the model pre-emptively beyond demonstrated need.

---

# 14. Summary Principle

`make_site2` should be model-led, not model-maximal.

Its aspirational specification exists to make important public structure and ownership explicit before rendering. It is successful when it prevents semantic decisions from leaking into arbitrary code, not when it gives a bespoke formal type to every value that appears on screen.

The working rule is:

```text
Model the distinction when it changes meaning, ownership, valid composition,
validation, runtime contract or public interpretation.

Use ordinary rendering and shared presentation policy once the remaining work is
simply to display an already-modelled entity or leaf value.
```

The difficult cases will not disappear. The value of this principle is that it tells the project what question to ask when they arise.

