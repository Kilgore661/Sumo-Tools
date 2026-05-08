# Implementation State

## Status

Current consolidated implementation note for `make_site`.

This document consolidates practical implementation notes from:

* `reference/Make Site Builder Notes.md`
* `reference/Site Definition Handoff Memo.md`

Those notes are preserved unchanged as reference material.

## 1. Terminology

Use:

```text
site definition
```

for the static intended structure of the public site.

Do not call this the "initial state".  That phrase is too easily confused with
runtime UI state.

Distinctions:

* **site definition** = static intended structure of the public site;
* **UI state** = runtime/user selections such as selected division, selected
  source, visible traces, or open controls;
* **build config** = where and how the site is generated and deployed.

## 2. Current Package

The current builder package is:

```text
src/products/make_site
```

The earlier handoff note refers to provisional classes under
`src/products/site/classes/`.  That was part of the modelling path and should be
read as background, not as the current package path.

Current important implementation files include:

```text
src/products/make_site/cli.py
src/products/make_site/site_definition.py
src/products/make_site/render.py
src/products/make_site/files/site-shell.css
```

## 3. Current Builder Behaviour

The builder currently:

* builds/collects page-facing outputs needed by implemented pages;
* renders a static site shell;
* writes output under `files/output/make_site`;
* supports local deployment;
* supports remote deployment.

The current landing/shell has moved beyond the earliest plain stress-test page,
but it should still be treated as an evolving public shell rather than a final
design.

## 4. Current Site Definition

The site definition should describe the intended public model, not merely the
shape of convenient existing artefacts.

When a current artefact already matches the intended public page shape, a
simple view or embedded/copy approach may be acceptable provisionally.

When the intended public model differs from the current artefact, use a
design-conformant view such as a custom renderer or a producer-written bundle.
Do not split or duplicate navigation just because old standalone pages happen
to be split that way.

The old example remains instructive:

```text
Win Probability by Standing
```

should be one page with an option:

```text
source = Observed | Equelo | Combined
```

not separate public navigation pages for `Observed` and `Equelo`, even if that
was convenient in a disposable prototype.

## 5. Current Public Equelo Page

`Typical Equelo Ratings` is currently a public-facing page.

It uses the public Equelo rating-landmark curve:

```text
Mark 3.2.1(2000)
```

The fixed-v1 chart files `entrant_initial_ratings_v0.html` through
`entrant_initial_ratings_v5.html` are diagnostic/audit-trail charts.  They are
not currently public pages.  They may later become exhibits in a narrative
methodology page if the site gains a suitable essay-with-figures pattern.

## 6. Producer Integration

When new analysis outputs become public pages, prefer this path:

```text
analysis package
  computes the analysis
  writes existing diagnostic/debug outputs as before
  also writes site-facing data/config/metadata

make_site
  consumes the site-facing material
  renders the public page consistently
```

The site builder should not parse old generated HTML as the normal way of
recovering page data.

## 7. Plotly Behaviour

Plotly's built-in legend double-click behaviour has shown undesirable behaviour
in at least one multi-trace chart: double-clicking some legend entries can show
all traces rather than isolating the clicked trace.

The known workaround is implemented in:

```text
src/analysis/probability/matchups/charts.py
```

The relevant pattern is:

* set `layout.legend.itemdoubleclick` to `False`;
* define an explicit `isolateTrace(curveNumber)` JavaScript function;
* listen for `plotly_legenddoubleclick`;
* call the isolate function;
* return `false` from the event handler.

In the matchup traces, the custom handler also respects the active division
scope, so double-click isolates the clicked trace within the currently selected
division rather than across the whole hidden trace universe.

Apply this policy to public Plotly charts unless a chart has a documented
reason to keep Plotly's default double-click behaviour.

## 8. Known Browser Issue

Firefox did not show the implemented navigation links in red in one earlier
test, even though the generated HTML used `class="nav-link"` and deployed CSS
contained `.nav-link { color: #ff3030; }`.

Chrome displayed the red links correctly.

This should be investigated later with developer tools by checking the computed
colour of a clickable nav link and confirming whether `site-shell.css` is being
applied, overridden, or ignored.

## 9. Remaining Open Areas

Open implementation areas remain in the `TBD Register.md`, especially:

* styling consistency;
* table sizing and centring;
* Plotly control affordances;
* shikona link consistency and qualified shikona generation;
* embedded-page migration;
* URL/deep-link strategy for page option combinations;
* Equelo methodology/narrative pages.
