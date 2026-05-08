# TBD Register

This is the canonical open-issues list for the provisional public site and
`make_site` builder.

Older notes contain the context that produced these items. This file is the
working register.

## 1. Navigation and Information Architecture

### 1.1 Final Navigation Depth

The stress-test navigation currently exposes the full subject tree as a large
nested sidebar.

The final public UI probably should not expose every level globally. Decide
which levels are global navigation, which become page-local navigation, and
which become tabs, filters, accordions, or explanatory panels.

### 1.2 Quick Entry Points

The subject-led navigation is the official model, but casual-reader entry
points may still be useful.

Decide whether the home page should include quick links such as latest
standings, banzuke changes, rikishi lookup, rank outcomes, and ratings/model
explanations.

### 1.3 Implemented vs Planned Items

During development, implemented pages should be visually distinguishable from
planned/unimplemented pages.

This distinction should probably disappear, or become much subtler, in a final
public release.

### 1.4 Stable Route Hierarchy

The current route hierarchy is provisional.

Decide which routes should become stable public URLs before external linking,
sharing, or publication becomes important.

## 2. Page Contracts and Bundles

### 2.1 Page Bundle Format

Decide whether page bundles should be declared as Python objects, JSON, YAML,
TOML, generated metadata, or some combination.

The important contract is known: a page bundle must identify its page metadata,
view, assets, data files, and option model. The storage format is not settled.

### 2.2 Route Ownership

Avoid having two independent ways to specify the same public route.

The current design derives public routes from the navigation tree. Keep this
unless a stronger requirement appears.

### 2.3 View Types

The initial view types are enough for current work:

* standalone HTML;
* HTML fragment;
* Plotly/data-driven chart;
* table app;
* essay;
* custom escape hatch.

Do not broaden this list until a real page requires it.

### 2.4 Options Model Semantics

The options model describes page state, not merely widgets.

It must distinguish between:

* exactly-one choices;
* zero-or-more choices;
* boolean choices;
* numeric/range choices;
* future state types justified by real pages.

The renderer may choose dropdowns, radio buttons, checkboxes, sliders, tabs, or
other controls, but that is downstream of the state contract.

### 2.5 Direct Rendering vs Iframes

The prototype currently uses iframes for embedded page content.

Decide whether final pages should be rendered directly into the shell, kept as
standalone iframe pages, or mixed by view type.

Iframes work for stress testing and isolate legacy pages, but they complicate
shared styling, deep-linking, sizing, and communication between the page and
the shell.

### 2.6 Date and Date-Range Parameters

For charts and tables where it makes sense, consider making the date or range
of dates a page parameter.

This may apply to more than one public exhibit, so it should not be solved by
promoting slice-specific HTML files such as `finish_by_chii_1978_1980.html`.
The intended direction is a page-level option backed by producer-written data
or a producer contract that supports the selected range.

This is not an immediate implementation task.

## 3. Browser State and Shareable URLs

### 3.1 Deep Links for Current Display State

The JavaScript should create a URL that takes someone directly to what is being
displayed.

For example, a URL should be able to identify:

* the selected navigation page;
* the selected page options;
* the current standings window/division/sort state, where relevant;
* equivalent state for other interactive pages.

The URL should be displayed in the browser's address bar.

### 3.2 Back and Forward Buttons

The browser back/forward buttons should reflect the sequence of selected pages
and option states.

Selecting a page or changing meaningful options should push or replace browser
history according to an explicit policy.

### 3.3 Shell-to-Page State Contract

The shell knows which page is selected. Individual pages know their internal
options and current view state.

Define the contract by which pages tell the shell their current state, and the
shell tells pages to restore a state from the URL.

This is especially important while pages are embedded in iframes.

## 4. Current App Integration

### 4.1 Banzuke Changes Data Source

The current `make_site` integration consumes Banzuke Changes data from
`files/output/bcr`.

At the time this register was created, that data had to be copied from the
existing local publication because regenerating it depended on a missing
legacy v9 pickle.

Decide whether the Banzuke Changes pipeline should be made fully reproducible
inside Sumo-Tools before this page is treated as final.

### 4.2 Banzuke Changes Default Previous Basho

The default Banzuke Changes view should have previous-basho context turned
off.

Review the page defaults and URL-state handling so this is the initial view
when the page is opened without explicit options.

### 4.3 Standings by Wins Data Source

The current `make_site` integration consumes standings data from
`files/output/standings/publisher/latest_data`.

Confirm that this is the intended producer contract, rather than a convenient
publisher implementation detail.

### 4.4 `.js.txt` JavaScript Files

Some JavaScript is intentionally stored as `.js.txt` because plain `.js` files
are not conveniently readable in the author's current workflow.

The site builder should preserve the filenames expected by source HTML files.
Do not silently normalise them to `.js`.

## 5. Plotly and Interactive Charts

### 5.1 Plotly Legend Double-Click

Plotly's built-in legend double-click behaviour has shown undesirable
behaviour in at least one multi-trace chart: double-clicking some legend
entries can show all traces rather than isolating the clicked trace.

Known workaround:

* set `layout.legend.itemdoubleclick` to `False`;
* define an explicit trace-isolation JavaScript function;
* listen for `plotly_legenddoubleclick`;
* perform the isolation manually;
* return `false` from the event handler.

The implemented reference is:

```text
src/analysis/probability/matchups/charts.py
```

Apply this policy to public Plotly charts unless a chart has a documented
reason to keep Plotly's default double-click behaviour.

### 5.2 Plot Titles vs Page Titles

For final public pages, the page should own the main title and explanatory
context.

Charts should own chart-specific labels, axes, legends, hover text, and
annotations.

Existing standalone Plotly HTML may include chart-owned titles. That is
acceptable during the integration phase, but final public pages should avoid a
confusing double-title structure.

### 5.3 Shared Plotly Page Template

Decide when to stop copying standalone Plotly HTML and instead emit chart data,
chart configuration, and a shared public page template.

Copying works today, but should remain an implementation convenience rather
than the desired long-term contract.

### 5.4 Support and Confidence Presentation

Charts such as matchup traces need support-aware interpretation.

Make sure public charts show sample size, confidence intervals, or equivalent
warnings where low-support points would otherwise look overprecise.

### 5.5 Clearly Distinct Trace Styles

Investigate algorithms for generating `n` clearly different trace line styles
when `n > 20`.

This matters for charts with many selectable traces, where colour alone is not
enough to make traces distinguishable. Candidate dimensions include colour,
dash pattern, marker shape, line width, opacity, and possibly grouped palettes
by division or subject.

The aim is not merely prettier charts. It is to preserve readability and
legend usefulness when many traces are visible or compared.

### 5.6 Legend vs Trace Options

Consider when a multi-trace chart should expose traces through the Plotly
legend, and when each trace should instead be treated as a page option.

A legend is natural when traces are few enough to scan, or when users are
expected to toggle visible lines directly in the chart. An explicit option
control may be better when the trace universe is large, when only one or a
small number of traces should usually be visible, or when trace selection needs
to participate in URL state, presets, or explanatory page grammar.

This decision may depend on whether the chart is an exploratory analysis tool,
a public exhibit, or a comparison page with carefully guided defaults.

### 5.7 Long X-Tick Labels

All charts with longish string x-tick labels should rotate those labels by
45 degrees.

"Longish" includes dates.

This should be treated as a chart readability rule, not as a one-off style
tweak for a single page.

### 5.8 Percentage Chart Defaults

Review all public charts whose y-axis is a percentage, probability, CDF, PMF,
survival curve, proportion, or other bounded 0--100% quantity.

Such charts should default to showing the full 0--100% y-axis unless there is a
documented page-specific reason to auto-scale by default.

### 5.9 Plotly Controls Hint

Think about how to alert users in a non-intrusive way that Plotly charts can be
interacted with through the built-in controls, including zooming, panning,
autoscaling, and resetting axes.

The hint should not clutter every chart or explain Plotly in a technical way.
Possible directions include a small reusable icon/hint near charts, a brief
first-visit affordance, or wording in a shared notes/help area.

## 6. Theme and Page Presentation

### 6.1 Shared Public Theme

Not all currently integrated charts use the same dark theme or page grammar.

For the prototype this is acceptable. For the final public site, pages should
either conform to a shared theme or be clearly framed as legacy/research
artefacts.

### 6.2 Content Shell Chrome

The outer content title bar has been removed because loaded pages generally
own their own title area.

Revisit this only if a page type emerges that needs shell-owned context or
commands.

### 6.3 Page Self-Explanation

If the shell no longer shows page summaries, each loaded page must be
self-explanatory enough to stand on its own.

This does not mean verbose in-page instructions; it means good titles,
controls, labels, and explanatory affordances where needed.

### 6.4 Public vs Research Presentation

Decide how to mark pages that are public-ready, candidate/research, diagnostic,
legacy, or superseded.

This should not produce a separate top-level "expert" section unless later
requirements force that change.

## 7. Browser and CSS Bugs

### 7.1 Firefox Navigation Link Colour

Firefox did not show the implemented navigation links in red, even though the
generated HTML used `class="nav-link"` and the deployed CSS contained the red
link rule.

Chrome displayed the links correctly.

Investigate with developer tools by checking computed colour, loaded CSS, and
possible browser cache or visited-link behaviour.

### 7.2 Iframe Height Regression

Removing the content title bar once caused the embedded page iframe to display
only the top of a chart.

The immediate fix was to restore a full-height one-row grid for `.site-main`.

Keep this in mind when changing shell layout, especially on mobile.

## 8. Deployment and Build Behaviour

### 8.1 Local and Remote Deployment Contract

The builder currently writes to `files/output/make_site` and can deploy to the
local web root. Remote deployment exists as part of the intended package
shape.

Clarify the final contract for:

* build-only;
* local-only deployment;
* remote deployment;
* combined build and deployment;
* required environment variables/secrets.

### 8.2 Deployment Root

The deployed root should be `sumo-tools`, not `site` or `make_site`.

Keep this distinction explicit: `make_site` is the builder package;
`sumo-tools` is the public site root.

### 8.3 Console Output Policy

Per-file "wrote this file" output was removed as noise.

Keep console output high-level unless a verbose/debug mode becomes a real
requirement.

## 9. Content Inclusion Decisions

### 9.1 Division Stability Parameter

The public page currently uses:

```text
division_persistence (1958-2026, num_basho=10).html
```

The `num_basho=10` choice is brittle.

Decide whether this should become a fixed public default, a dropdown, or a
page generated from a more stable producer contract.

### 9.2 Division Churn Supersession

`division_churn.html` is currently treated as legacy and superseded by division
persistence for the public concept of division stability.

Confirm this before deleting, hiding, or documenting the older artefact.

### 9.3 Equelo Experiment Story

Equelo experiment charts are not currently treated as ready-made public pages.

They are important because they help tell the methodological story of moving
from "this is what the data says" to "these numbers are forced to be monotonic
because that is what the practical model requires."

Decide whether that story belongs under methodology, observed-vs-modelled, or a
research archive section.

### 9.4 Excluded Diagnostic HTML

The following were excluded from the first public-site stress test:

* `first_app`;
* old/current standings diagnostic HTML;
* banzuke warnings/weirdness pages;
* raw `HTML results`;
* other internal pipeline artefacts.

Reconsider only if a public question gives one of these a real role.

### 9.5 Legacy Elo v9 B1 Migration

For legacy Elo v9 deliverables that are directly relevant to Sumo-Tools, the
preferred path is to reimplement the computation/output under Sumo-Tools and
emit a Sumo-Tools page bundle.

Old v9 HTML can be reference material or a temporary comparison, but should not
be the permanent delivered artefact.

## 10. Data and Method Pages

### 10.1 Public Explanation of Data Sources

The site needs public-facing explanation of where the data comes from, update
policy, parsed history, and known source limitations.

### 10.2 Glossary

The site needs glossary coverage for terms such as basho, banzuke, chii,
rikishi, shikona, division, record, fusen, east/west, and sideless chii.

### 10.3 Known Limitations

Known limitations should be public-facing where they affect interpretation:

* missing or ambiguous data;
* historical rank quirks;
* retirement ambiguity;
* parser limitations;
* model limitations;
* what not to infer.

### 10.4 Method Notes

The site needs method notes for parsing, output generation, confidence
intervals, curated domains, and the distinction between observed data and
model projections.

## 11. Future Public Feature Ideas

### 11.1 Participation Volume Exhibits

Career length naturally suggests related public exhibits based on participation
volume rather than elapsed time:

* greatest number of bouts;
* greatest number of wins;
* highest win proportion;
* related active/retired breakdowns and leader tables.

Open question: Can you already derive this data from the Standings by Wins
table?

Do not answer or implement this as part of the Career Length page plumbing.

## 12. Shared Presentation and Link Contracts

### 12.1 Generate Qualified Shikona in Sumo-Tools

Qualified shikona for external graph links currently depend on a brittle legacy
`full_shiks.pkl` file outside the Sumo-Tools project.

Sumo-Tools should derive or maintain these qualified names itself, using RikId
and shikona history, so pages with non-unique shikona can link consistently
without depending on a hardcoded legacy path.

### 12.2 Consolidate Qualified-Shikona Access

`standings.publisher` currently opens the legacy qualified-shikona pickle
directly, while other code reaches it through the `banzuke_compare`
`graph_shikona_for` wrapper.

Move all consumers to one shared identity/linking service. That service should
avoid fragile import-time file I/O and should degrade or fail according to an
explicit contract.

### 12.3 Styling Consistency Audit

Review all public tables and charts for styling consistency before treating the
site as public-ready.

This should cover table headers, sticky behaviour, notes, legends, controls,
chart colours, axis ranges, spacing, link behaviour, and responsive layout.

As a site-wide table rule, columns should be no wider than their contents
require, tables should be no wider than their columns require, and tables
should be horizontally centred within the available content area unless a page
has a documented reason for full-width tabular layout.

Also review language and headings across the site. Where possible, public
labels should read naturally for ordinary visitors rather than assuming
statistical vocabulary or implementation knowledge.

Check how full chii values such as `M3eHD` are displayed across the site. In
rating or rating-landmark contexts, apply the v5 policy:

* ignore annotations for v5 lookup;
* canonicalise numbered `Y`, `O`, `S`, and `K` slots to the `1` slot while
  preserving side where present;
* use the curated v5 domain, currently bounded below by `Jd100w`;
* make aggregate labels such as `M3`, `S`, or `J` name their support and
  averaging policy.

Do not apply this as a global historical-display rule. Pages whose purpose is
to show banzuke history may need to display the original annotated or rare chii.

The policy is recorded in `src/analysis/equelo/fixed_v1/docs/V5 Policy.md`.

### 12.4 Embedded Page Migration Assessment

Assess whether currently embedded standalone pages should migrate to native
non-embedded site pages.

The assessment should cover styling consistency, note handling, shared controls,
deep links, shell integration, data contracts, maintenance cost, and whether any
legacy page should remain embedded as a deliberate exception.

### 12.5 Source Layout vs Site Navigation

Consider rearranging source code so public-site feature modules follow the
navigation tree.

For example, `career_length` and `rank_at_retirement` both belong conceptually
under `sumo_history/career_lifecycle`. Assess whether grouping analysis,
bundle generation, renderer support, docs, and tests by public-site section
would make ownership clearer than the current flatter analysis layout.

Initial trial: the `career_length` and `rank_at_retirement` analysis modules
have been moved under `src/analysis/sumo_history/career_lifecycle`. Revisit
after more pages exist to decide whether renderer code, tests, and docs should
follow the same pattern.
