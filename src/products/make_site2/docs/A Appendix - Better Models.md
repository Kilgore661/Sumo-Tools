# A Appendix - Better Models

## Status

Deferred model notes for `make_site2`.

This appendix records models that may be more general or more satisfying than
the current implementation model, but which are not being implemented now.

The main design documents define the current model.

This appendix is evidence for future redesign, not a second active
specification.

---

# 0. Guide to This Appendix

This appendix is a bin for model ideas that are useful but not active.

If another document says "See Appendix A", it usually means one of these
questions:

```text
Is a flat G1 ContentPanel enough, or does this page need nested structure?
Is this one artifact with views, or several artifacts?
Should controls be flat peers, nested, conditional, or view-local?
Should a control know when it is applicable, ineffective, or empty?
Does PA being terminal hide structure that the renderer keeps wanting to show?
```

The current implementation answer remains:

```text
Use flat G1 unless a promoted page proves it insufficient.
```

The useful bins in this appendix are:

```text
Artifact views
  A single artifact may have several views or payload kinds.
  Pressure case: Career Length / 7.3.1.

View-local options
  A view may want controls that are not global to the whole artifact.
  Current decision: do not implement this yet.

Promotion rule
  If view-local options become a substantial workflow, reconsider the
  navigation tree instead of hiding complexity inside one artifact.

Control applicability
  A flat control can be valid but ineffective for some states.
  Pressure case: Win Probability by Standing / 6.3.1, where Error bars applies
  only to observed source data.

PA terminal-symbol pressure
  G1 treats PA as a terminal symbol. This keeps the content grammar simple, but
  it can hide internal structure such as table-like, chart-like, mixed, titles,
  source labels, and local notes.
```

This appendix is not a promise to implement any of those richer models.

When a richer model becomes necessary, promote the relevant idea into the main
specification or design document and update the implementation accordingly.

---

# 1. Purpose

Some pages expose pressure points where the current model may be a pragmatic
subset of a more general model.

The purpose of this appendix is to preserve those ideas without forcing the
implementation to absorb their full complexity before it is needed.

The current rule remains:

```text
Use the documented implementation model unless and until a real page proves it
insufficient.
```

---

# 2. Career Length and Artifact Views

`Career Length` is the current pressure case.

As a navigation item, `Career Length` makes sense as one analytical subject.

As a rendered artifact, it presents several ways of looking at that subject:

```text
Distribution
PMF
CDF
Survival
Longest
```

Each view is data-backed.

Each view can be understood as a table of data rendered through a selected
payload mode.

The first four views are naturally chart payloads.

`Longest` is naturally table-like.

The difficulty is not that chart and table payloads are different. The
difficulty is deciding whether the selected view is merely an option on one
artifact, or whether each selected view is a sub-artifact.

---

# 3. More General Model

A more general model is:

```text
Artifact
  View+

ArtifactView
  id
  label
  DataBinding
  PayloadKind
  TitleBlock, optional
  Notes, optional
  Options, optional
```

In this model, a single-view artifact is just the simplest case:

```text
Basho Results
  Artifact
    View: default
      PayloadKind: table
```

`Finish by Chii` is also a single-view artifact:

```text
Finish by Chii
  Artifact
    View: default
      PayloadKind: chart
```

`Career Length` becomes:

```text
Career Length
  Artifact
    View: distribution
      PayloadKind: chart
      DataBinding: distribution.csv

    View: pmf
      PayloadKind: chart
      DataBinding: pmf.csv

    View: cdf
      PayloadKind: chart
      DataBinding: cdf.csv

    View: survival
      PayloadKind: chart
      DataBinding: survival.csv

    View: longest
      PayloadKind: table
      DataBinding: longest.csv
```

This model can also handle mixed media artifacts:

```text
Artifact
  View: explanation
    PayloadKind: prose

  View: evidence
    PayloadKind: table

  View: interview
    PayloadKind: video
```

The semantic subject is the Artifact.

The views are representations of that subject.

---

# 4. View-Local Options

The more general model permits view-local options:

```text
Artifact
  View: longest
    PayloadKind: table
    Options:
      active_status
```

This is conceptually valid.

It is not part of the current implementation plan.

Current executive decision:

```text
Career Length / Longest will have no local options for now.
```

This avoids implementing a second-order options system before a real promoted
page requires it.

---

# 5. Promotion Rule

A view with a small local option may still be just a view.

Example:

```text
Career Length
  View: longest
    active_status = all / active / completed
```

A view whose local options become a substantial analytical workflow should be
promoted to its own navigation item or artifact.

Example pressure:

```text
Longest Careers
  basho range
  active/completed
  division
  minimum appearances
  sorting
  grouping
  historical/current mode
```

At that point the question is not how to hide the complexity inside Career
Length.

The question is whether the navigation tree should change.

If the navigation tree no longer fits the analytical structure, redesign the
navigation tree.

---

# 6. Control Applicability and Empty-but-Valid States

`Win Probability by Standing` raises a related but distinct pressure point.

The implemented page is structurally G1:

```text
ContentPanel
  Heading
  Controls
  PA
```

The controls are flat:

```text
Source
Division
Error bars
```

One way to understand the artifact is as a conceptual multi-source dataset. In
that relational framing, all three controls can be read as filters:

```text
Source
  select observed or Equelo rows

Division
  select rows for a division

Error bars
  select or show the CI95 evidence layer where CI95 values exist
```

This avoids treating the page as nested or branch-like.

The unresolved model question is not whether the page is G1. The unresolved
question is whether controls should know when they are ineffective, invalid,
empty, or applicable only to some source states.

For now, the active model does not include conditional control visibility or
control applicability. States such as:

```text
Source = Equelo
Error bars = true
```

are allowed even though there is no CI95 layer to draw for Equelo data. The
renderer should draw what the selected data state permits, not invent a
half-designed conditional-control model.

If future pages require better UX for this, promote control applicability into
the main UI Model Design.

---

# 7. Current Implementation Consequence

The current implementation model should not be rewritten around this appendix.

For now:

```text
Implement Finish by Chii using the current Artifact model.
Implement Career Length later without view-local options.
Keep DataBinding general enough that it does not assume:
  one artifact = one CSV = one payload kind
```

If a future artifact requires view-local options or mixed payload views, this
appendix should be promoted into the main Artifact Model Design.



# 8. PA Terminal-Symbol Pressure

The idea behind using a grammar like G1 is that layout flows from the model.
The resulting rendering need not visually reflect the underlying semantic
structure, but reflecting it is what we want. Using a grammar helps organise
the rendering.

In G1, `PA` is a terminal symbol.

At the content-panel grammar level, PA has no internal structure. It is a
semantic blob.

This creates a tension. If PA is terminal, the artifact renderer can implement
many visible details inside it. For example, in Career Length / 7.3.1, the
renderer can show a table with or without an `Active` column. It could also
invent arbitrary local behaviours.

But this freedom is exactly the risk: visible structure can appear inside PA
without being owned by the content grammar.

I think the issue we encountered with 6.2.1, 6.3.1 and 7.3.1 can all be traced
back to the issue that PA has no structure.

Maximally, there may be a relationship between types of PA and types of control
that is at least context-sensitive. This suggests that the problem of UI
specification may be much harder than it first looked.

There is also the question of why the LLM keeps sneaking titles into PA when
the grammar does not say there should be one (because PA=blobs). It is just
done this again with 6.3.1; there is nothing to say the PA should say
"Equelo/Observed" source.

This may be bespoke detailing. On the other hand, as a blob, there is also
nothing to say there cannot be a title, a source label, a video, or some other
artifact-local element.

This is another aspect of the same problem: PA being terminal keeps the current
grammar simple, but it also hides structure that renderers may want to express.
