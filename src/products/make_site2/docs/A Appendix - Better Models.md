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

# 6. Current Implementation Consequence

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

