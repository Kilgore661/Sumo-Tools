# 10 Styling Review

## Status

Working review notes.

This document captures side-by-side observations from comparing `make_site2`
with the old `make_site` public site.

At this stage, the notes are issue capture rather than implementation
instructions. They record what should be considered, not what has already been
decided in code.

---

# 1. Initial Styling Review

## 1.1 Reference Point

For this review, the old `make_site` site is the sole styling reference.

The intended comparison is:

```text
make the new site like the old one
```

This is appropriate because `make_site2` styling was intentionally minimal while
the model and page coverage were being established.

## 1.2 Typography

The old site appears to use smaller font sizes than `make_site2`.

The smaller old-site typography is preferred.

The old site's vertical text spacing also appears better.

The font family itself is not the main difference. Both sites use:

```text
Arial, Helvetica, sans-serif
```

The differences to review are therefore likely:

```text
font sizes
line-height
heading defaults
heading margins
list spacing
control spacing
table spacing
```

Old `make_site` explicitly sets body `line-height: 1.35`; `make_site2`
currently does not. This is a useful first comparison point.

## 1.3 Links

The old site does not underline links by default.

That behaviour is preferred for the generated public site.

This is a chrome / affordance issue, not a content-panel layout issue.

## 1.4 Generated Timestamp

The old site has a visible `Generated ...` string in the site title area.

`make_site2` should also expose this build/generated metadata, but not beside
the site heading.

A preferred candidate location is:

```text
at the end of the Options area
after a blank line
in tiny but readable text
```

This touches content placement inside the `FilterSection` / Options region, but
the styling of the string itself is chrome.

## 1.5 Navigation Item State

The old site's navigation tree uses different text colours depending on whether
a navigation node is implemented.

This should be treated as a semantic category with styling attached, not as an
arbitrary colour choice.

Avoid calling this style `muted`, because that term has become overloaded.

Use a term such as:

```text
unimplemented
```

or:

```text
unavailable
```

The initial styling idea for unimplemented navigation items is transparency
rather than choosing a separate colour. Try about 50% opacity.

## 1.6 Active Navigation Item

The currently active navigation item should have a subtle visible state.

A small box or similar treatment may be appropriate, but the effect should be
quiet rather than visually dominant.

This is a semantic state with chrome attached:

```text
NavigationItem[current]
```

## 1.7 Navigation Collapse Control

Neither old `make_site` nor current `make_site2` has the navigation hider quite
right.

The issue is shell / `NavigationBar` layout, not G1 content-panel layout.

The current control behaves like an overlaid widget. This can let it cover or
compete with the heading and navigation text.

The preferred direction is to reserve a small amount of horizontal space for the
hide/show control so that the icon:

```text
has a stable position
does not cover the heading
does not cover navigation text
remains available when the navigation content is hidden
```

One possible conceptual shape is:

```text
NavigationBar
  LeftPart
    collapse_control
  RightPart
    heading
    navigation_tree
```

This exact formal structure is not yet proposed as a model change. The important
point is that the collapse control should occupy layout space rather than float
over content.

## 1.8 Shell Grammar Observation

`G1` describes the content panel, not the whole page shell.

The relevant concept for the navigation hider is `NavigationBar`, or possibly a
more explicit shell grammar around `PublicSiteShell`.

The current model already has:

```text
PublicSiteShell
  NavigationBar
  ContentPanel*
```

and:

```text
NavigationBar
  heading
  navigation_tree
  collapse_control
```

The rendering currently realizes the collapse control as a sibling of the nav
element rather than as occupied space inside the navigation layout. This may be
defensible for implementation, but the semantic owner remains the
`NavigationBar` / shell, not G1.

---

# 2. Content Panel Review

## 2.1 Site-Level Typography and Links

The font-size, line-spacing, and link-styling observations from the navigation
review should apply at site level, including within the content panel.

Candidate site-level directives:

```text
Use old make_site-like font sizes.
Use old make_site-like line spacing.
Do not underline links by default.
```

These should not be treated as local content-panel tweaks unless a specific
artifact or content region later needs an exception.

## 2.2 Vertical Scrolling

There is an odd vertical scrolling issue in the current content panel.

Visible symptom:

```text
two vertical scrollbars can appear, not counting the nav panel scrollbar
```

Initial diagnosis:

```text
one scrollable extent may belong to the artifact, especially table-like artifacts
another may belong to the containing content panel or notes region
```

This needs more thought before implementation.

Desired direction for table-like artifacts:

```text
tables should be renderable so that column headings do not scroll away
```

This is probably more than chrome. It may touch artifact layout, content-panel
scroll ownership, and table-like artifact behaviour.

## 2.3 Notes Width

Notes should be constrained to a readable measure.

Candidate rule:

```text
Notes max-width: 800px
```

## 2.4 Options Panel and Boxes

There are unresolved model-related questions about whether the Options panel
should have different visual treatment from the background, such as:

```text
different background colour
box / panel treatment
other visual separation
```

No decision yet.

The next step is to see what the simpler site-level styling changes look like
before deciding whether the Options panel needs a stronger visual container.

## 2.5 Artifact-Specific Work

Most remaining table-like artifact issues are expected to be specific to
individual artifacts rather than table-like artifacts as a whole.

Functionality issues, such as sortable columns, are out of scope for this
styling pass and should be handled later.

Charts were reviewed as a type of artifact. No chart-type styling change was
identified in this pass.

Individual chart tweaks may still be needed later.

## 2.6 Content Panel Heading Background

The content panel heading area should have a background colour that differs from
the default page background.

Preferred direction:

```text
slightly paler than the default navy background
```

One way to think about this is "navy with about 20% transparency relative to
white", but the actual implementation may need literal colours per site context
because transparency over different backgrounds can produce different results.

This colour choice remains a detail for later.

## 2.7 Dropdowns

Dropdown controls look too tall relative to inline text.

Candidate adjustment:

```text
reduce top and bottom spacing by a couple of pixels
```

The goal is for dropdowns to sit more comfortably with surrounding text.

## 2.7a Dropdowns and Radio Button Groups

Dropdowns and radio button groups should be understood as alternative renderings
of the same semantic control:

```text
single choice from a finite set of values
```

Policy:

```text
Dropdowns are always single-select widgets.
A dropdown is therefore functionally equivalent to a radio button group.
Both dropdowns and radio button groups naturally have a label or caption.
The app shall render a single finite choice as a radio button group unless
there are more than 7 items.
If there are more than 7 items, render the choice as a dropdown.
```

Model implication:

```text
The semantic control is "single finite choice", not "dropdown" or "radio group".
```

The renderer may choose the widget from the number of values using the threshold
above. A later pressure case may justify an explicit model override, but no
such override is needed yet.

## 2.8 Row Number Columns

Row-number columns should be visually secondary.

Candidate rule:

```text
row-number column heading and values: 50% opacity
```

This is a table-like artifact styling rule, not an individual table data rule.

---

# 3. Styling Lens Sticky Notes

## 3.1 Styling Should Follow Structure

The best lens for this review is:

```text
does styling follow model structure?
```

A visible styling distinction should usually correspond to a structural or
semantic distinction in the model.

The reason is user-facing, not merely internal neatness:

```text
users infer structure from what they see
```

Good UI design and harmonious UX depend on those visible cues matching the
underlying structure.

## 3.2 PA Is Currently Terminal

In the current content grammar, a `PA` is a terminal symbol.

From the content-panel grammar's point of view, the PA is a blob. Artifact
renderers may do structured work inside that blob, but G1 does not currently
model the PA's internal structure.

Useful distinction:

```text
ContentPanel-level styling
  heading
  options / controls
  PA slot
  notes

Artifact-level styling
  whatever the PA or artifact internally owns
```

## 3.3 Table-Like and Chart-Like Are Tempting but Not Yet Clean

It may be useful to subdivide PAs or artifacts into categories such as:

```text
table-like
chart-like
mixed
```

This would help avoid repeated styling logic across artifact renderers.

However, cases such as Career Length / 7.3.1 create pressure immediately: a
single artifact may have chart-like and table-like views.

So these categories may be useful as rendering categories or artifact-view
categories, but they are not yet clean top-level grammar categories.

## 3.4 Notes Width Is Readability, Not Structure

The proposed notes width constraint is mostly about readable prose, not about
representing structure.

Rule of thumb:

```text
a horizontal line of prose should not contain too many words
```

The exact number is not settled, but roughly 15 words per line is the current
intuition.

This makes notes width a `Notes` presentation/readability rule rather than a
new structural distinction.

## 3.5 Avoiding DRY Violations Without Over-Modelling

If PA types are never formalised, repeated concerns may leak into individual
artifact renderers.

Likely repeated concerns include:

```text
table density
sticky table headings
row-number styling
shikona alignment
chart sizing
Plotly theme defaults
mixed chart/table artifacts
```

That would create DRY pressure.

However, the current working slogan is:

```text
informed non-perfectionism
```

Do not invent a full artifact taxonomy before the repeated patterns are clear
enough. Some temporary duplication is acceptable while the model continues to
teach us what it wants to become.

Current working stance:

```text
style from explicit structure first
use light shared rendering categories where already obvious
accept some duplication until stronger categories emerge
```
