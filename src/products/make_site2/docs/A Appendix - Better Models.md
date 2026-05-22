# A Appendix - Better Models

## Status

Deferred model notes for `make_site2`.

This appendix records models that may be more general or more satisfying than
the current implementation model, but which are not being implemented now.

The main design documents define the current model.

This appendix is evidence for future redesign, not a second active
specification.

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



# Lightbulb Moment (or a Bump on the head?)

The idea behind using a grammar like G1 is that layout flows from the model.
The resulting rendering need not visually reflect the underlying semantic
structure, but this is what we want and using a grammar helps us to organise
the rendering. 

Now, in G1, PA is terminal symbol; a PA has no structure, it is a semantic blob.It
follows then that as terminal symbol we can do whatever we like re the 
implementation? Eg an empty display? Re 7.3.1: we can display a table with
or without an Active column;  we could play a different tone when the user
hovers over an active rikishi or an inactive rikishi. Whatever.

I think the issue we encountered with 6.2.1, 6.3.1 and 7.3.1 can all be traced
back to the issue that PA has no structure. (Maximally, I think there is a relationship between types of PA and types of control that is at least context-sensitive; this suggests that the problem of UI specification may be *much* harder than I thought.)

There is also the question of why the LLM keeps sneaking titles into PA when
the grammar does not say there should be one (because PA=blobs). It is just
done this again with 6.3.1; there is nothing to say the PA should say
"Equelo/Observed" source. This bespoke detailing. OTOH, as a blob, there is
nothing to say there can't be a title either. Or a video. It seems to me this
is another aspect of the same problem.
