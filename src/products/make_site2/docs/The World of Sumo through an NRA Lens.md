# The World of Sumo through an NRA Lens

## Status

Design-thesis note.

This document is not an implementation specification and does not require a
formal Nested Relational Algebra engine. It records a way of thinking about the
public site that should inform future requirements, specifications, page
boundaries, producer boundaries and option design.

The purpose is to explain why apparently cosmetic questions about Records
tables, options and `#` rank columns are actually architectural questions.

---

## 1. Requirement Compass

The broad requirement is:

```text
Allow people to see anything about sumo records that they want to see.
```

Here `see` includes:

- observing raw facts;
- observing raw facts arranged in useful or natural ways;
- observing derived facts computed from raw facts;
- observing combinations of organised and derived facts.

The site will not expose arbitrary SQL-like or algebraic input. The practical
product is a curated set of public views. But the ideal requirement-meeter is:

```text
all sumo data and derived sumo facts in one structured corpus
  -> a principled way to navigate and transform that corpus
  -> rendered public views
```

Nested Relational Algebra is useful here as a design lens because the real
corpus is naturally nested: History contains basho dates; basho contain banzuke
and summaries; summaries contain days; days contain results; results contain
bouts and values.

---

## 2. Corpus

For present purposes, the corpus is `History`.

Biographical data, public shikona data, ratings and similar material expose a
known boundary issue: some facts we want to show are not currently inside
`History`. They may be auxiliary relations, derived relations or future corpus
extensions. That does not change the design lens:

```text
raw/core corpus + derived/enrichment steps -> enriched corpus
```

The important point is that every value the public site displays should be
available before rendering as a raw or derived fact in a deliberate
site-facing relation. A renderer should not perform meaningful analysis to
invent display values.

This principle already exists informally in the project, but it is not yet
explicit enough in the design.

---

## 3. The Hypothetical Everything Tree

Imagine a sumo-stats explorer whose root node is:

```text
History
```

Expanding it reveals basho dates. Expanding a date reveals a banzuke and a
summary. Expanding a summary reveals days. Expanding a day reveals results.
Eventually the user reaches a relation that can be viewed as a table or chart.

In this ideal explorer, every step down the tree is an operation over the
corpus:

```text
select this date
select this branch
select this day
select this division
project these values
derive these values
group/nest/unnest these values
rank/order these values
```

The visible artifact is the result of a composed expression over the corpus:

```text
RenderedArtifact = render(expression(Corpus), appearance_state)
```

The expression may be simple selection and projection, or it may include
derived values, ranking, aggregation, nesting and unnesting.

---

## 4. Navigation and Options

The navigation tree is not merely site furniture. It is the first visible part
of the selection mechanism.

Navigation chooses a major path or public question:

```text
Sumo History > Records > Longest Careers
```

That path corresponds to a curated expression family over the corpus.

The options panel continues the same selection mechanism. It represents the
last few meaningful choices above the leaves of the hypothetical
show-everything tree.

Therefore options are not automatically cosmetic. Some options choose a
different basis for the analytical expression, while others merely change the
appearance of a selected expression result.

This explains why options felt under-modelled in the current UI model. The
project made a Public UI Model, but the model did not fully account for the fact
that options are part of a corpus-expression selection mechanism that begins in
the navigation tree.

---

## 5. Basis Versus Appearance

The useful distinction is:

```text
Basis option
  Changes the analytical expression or the relation being shown.

Appearance option
  Changes only how an already selected relation is presented.
```

Examples:

```text
Basis option:
  Current vs Former rikishi
  Fusensho included vs excluded
  Whole-career records only

Appearance option:
  hide/show a column
  collapse or expand notes
  local sort for inspection
  chart scale
```

This distinction is especially important for Records tables. A `#` column is
not just table chrome. It is a derived record-position value. If an option
changes the population or counting policy, the meaning of `#` may change, and
the relevant rank may need to be computed before rendering rather than inferred
by browser filtering.

---

## 6. The NRA Acid Test

Future artifact and option design should use this acid test:

```text
Can the artifact and its options be understood as a coherent expression over
the corpus or enriched corpus?
```

The project does not need to write a formal expression for every artifact. But
if the intended artifact cannot be described in this way, or if the expression
is strangely contorted, that is evidence that the artifact boundary or option
model is unclear.

Examples of likely user-facing expression roles:

```text
Selection:
  restrict rows, choose a population, choose a date or division

Projection:
  choose visible columns or values

Ranking/order:
  compute record position within a selected basis

Aggregation:
  totals, distributions, averages, probabilities

Nest/unnest:
  grouped tables, sectioned tables, hierarchical chart data
```

If two visible views require materially different expression shapes, they
probably should not be one artifact merely because they share source data. This
was the issue with placing the `Longest Careers` table inside the Career Length
chart page. The charts and the table share a computational root, but they answer
different public questions.

Derived values such as BMI, career length, win rate and Equelo usually belong
to corpus enrichment or producer preparation rather than to the reader's
selection path. The site anticipates that such values may be interesting,
computes them deliberately, and makes them available in the enriched corpus or
site-facing relation. The public UI then selects, joins, projects, ranks or
groups those already-derived values.

An ad hoc calculator UI would be different: there the user would be choosing a
derivation as part of the expression. That is not the current public-site model.

---

## 7. Curated Views

The site should not expose arbitrary algebraic input. It should publish curated
views.

The specification layer should ask:

```text
What do people actually want to see?
What is interesting?
```

`Interesting` has at least two forms:

```text
Organisational:
  existing facts arranged together naturally.

Derived:
  new facts computed from existing facts.
```

Most useful public artifacts combine both.

A curated public view is therefore a named expression or expression family over
the corpus or enriched corpus. Navigation selects the expression family.
Options select basis parameters or appearance settings within that family.

---

## 8. Producers and Preprocessing

In principle, any artifact could be defined as:

```text
raw downloads -> rendered HTML
```

That is not a good implementation. The practical pipeline decomposes the work:

```text
raw source
  -> parsed corpus
  -> shared derived/enriched relations
  -> artifact-facing relation
  -> rendered artifact
```

Some preprocessing is private to one artifact. Some creates shared derived
relations needed by several artifacts. The current project uses the word
`producer`, but this design lens suggests a sharper meaning:

```text
Producer
  The final semantic step that prepares a site-facing relation for a public
  artifact or artifact family.
```

A producer may depend on private preprocessing or shared derived relations. The
renderer should consume the producer's site-facing relation without meaningful
analysis.

---

## 9. Practical Consequence for Records

Records pages should be reviewed with the following questions:

1. What is the public question?
2. What corpus/enriched-corpus relation is the root of the expression?
3. Which controls choose a basis?
4. Which controls are appearance-only?
5. What does `#` mean for each basis?
6. Does the producer already emit the right basis-specific relation?
7. Is the browser currently filtering a relation when it should be selecting a
   precomputed or producer-owned relation?

Do not treat Records-control changes as label tweaks until these questions are
answered.

---

## 10. Restraint

This note is a guide for thinking, not an instruction to implement a Grand
Unified Theory of Structured Data.

The project should promote concepts into code only when repeated implementation
pressure proves they are needed.

For now, the NRA lens should help us recognise when:

- an artifact boundary is wrong;
- an option is basis-changing rather than appearance-only;
- a producer needs to emit a different relation;
- a table rank or derived value belongs upstream of rendering;
- a public page is mixing unrelated expression families.
