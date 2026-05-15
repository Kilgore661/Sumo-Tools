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

### 1.5 Production Cache Policy

Development builds currently add a visible `cb` query parameter to generated
site URLs and runtime data fetches. Production builds can be created without
that development cache-busting behaviour.

Remaining decision: define the final production cache policy for generated
HTML, shared assets, manifests, and data payloads. The likely direction is to
cache versioned or content-stamped assets aggressively while keeping entry HTML
and current data easy to refresh after publication.

### 1.6 Resolve Positioning of Show/Hide Nav Bar Icon

The generated shell includes a show/hide navigation control for the sidebar.
Its position should be reviewed across desktop and mobile layouts so it is
discoverable, does not overlap navigation text, and remains usable when the
sidebar is collapsed or expanded.

Decide whether this control belongs attached to the nav edge, inside the title
bar, or in another stable shell location. Apply the same placement policy to the
PA runtime and normal site shell.

## 2. Page Contracts and Bundles

### 2.1 PA Manifest Contract Coverage

The bundle storage question is settled for now: Python dataclasses are the
canonical in-repo representation until a producer has a real need for another
format. Route ownership is also settled: `make_site` derives canonical public
routes from the navigation tree.

The remaining open question is whether the current PA manifest dataclasses
expose all metadata needed by promoted public pages as the runtime absorbs more
tables, charts, multi-view pages, essays, and migrated legacy artefacts.

Current policy is recorded in `Public UI Grammar.md` and
`PA Manifest Classes.md`.

### 2.2 Page Option Coverage

The options model is settled as page state rather than widget declarations.

Remaining work: add option kinds, URL-state metadata, validation rules, or
presentation hints only when a real promoted page exposes a concrete gap in the
current model.

Current policy is recorded in `Public UI Grammar.md`.

### 2.3 View and PA Type Rationalisation

The old view-type question has narrowed. The target architecture is PA
manifests rendered by `make_site`, with static HTML and custom renderers kept
as explicit temporary or exceptional paths.

Remaining work: remove or narrow legacy view types as pages migrate into the PA
runtime model. Do not add new view types unless a real page cannot be expressed
through the existing PA classes or a deliberately local custom renderer.

### 2.4 Direct Rendering and Embedded Artefacts

The target architecture is direct `make_site` rendering from PA manifests.
Iframes and copied standalone HTML remain compatibility mechanisms for legacy
or prototype artefacts, not promoted-page architecture.

Remaining work is tracked under `3.4 Remove Deep-Link Adapters`.

### 2.5 Date and Date-Range Parameters

For charts and tables where it makes sense, consider making the date or range
of dates a page parameter.

This may apply to more than one public exhibit, so it should not be solved by
promoting slice-specific HTML files such as `finish_by_chii_1978_1980.html`.
The intended direction is a page-level option backed by producer-written data
or a producer contract that supports the selected range.

This is not an immediate implementation task.

BRB is the current example. Its selected basho date should remain page state
backed by generated data/config rather than multiplying one-date HTML
artefacts.

## 3. Browser State and Shareable URLs

### 3.1 Deep Links for Current Display State

The site now has first-pass deep-link support using a shell-owned `page`
parameter plus page-owned option parameters.

Remaining work: complete the move from shell `?page=...` URLs toward the target
route/query model described in `Public UI Grammar.md`, and ensure every
promoted page publishes all meaningful display state through the shared
runtime rather than through page-specific adapters.

### 3.2 Back and Forward Buttons

The first-pass shell and participating pages update browser history for page
selection and option changes.

Remaining work: define the final push-vs-replace policy for routine option
changes, default-state normalisation, and rapid control changes such as table
sorting or chart toggles.

### 3.3 Shell-to-Page State Contract

The shell knows which page is selected. Individual pages know their internal
options and current view state.

The current contract distinguishes shell-owned state from page-owned state.
The shell may always own the selected page and development cache-bust token.
It may only inject page-owned query parameters into pages that declare they
accept shell/runtime parameters.

Remaining work: replace page-specific adapter contracts with the PA runtime
contract described in `3.4 Remove Deep-Link Adapters`.

### 3.4 Remove Deep-Link Adapters

The current deep-link adapters are temporary scaffolding, not a target
architecture.

Remove them by migrating promoted public pages into the PA-runtime ownership
model, where `make_site` owns option rendering, URL state, cache-busting,
styling, and shared table/chart behaviour from a PA manifest or equivalent
site-owned page contract.

The working proposal is recorded in
`src/products/make_site/docs/current/Remove Adapter Layer Proposal.md`.

## 4. Current App Integration

### 4.1 Banzuke Changes Data Source

The current `make_site` integration consumes Banzuke Changes data from
`files/output/bcr`.

At the time this register was created, that data had to be copied from the
existing local publication because regenerating it depended on a missing
legacy v9 pickle.

Decide whether the Banzuke Changes pipeline should be made fully reproducible
inside Sumo-Tools before this page is treated as final.

### 4.2 Standings by Wins Data Source

The current `make_site` integration consumes standings data from
`files/output/standings/publisher/latest_data`.

Confirm that this is the intended producer contract, rather than a convenient
publisher implementation detail.

### 4.3 `.js.txt` JavaScript Files

Some JavaScript is intentionally stored as `.js.txt` because plain `.js` files
are not conveniently readable in the author's current workflow.

The site builder should preserve the filenames expected by source HTML files.
Do not silently normalise them to `.js`.

### 4.4 Single Source of Truth for Page Defaults

Banzuke Changes currently has defaults in more than one layer: the legacy
standalone HTML/JavaScript app, the producer-written page bundle, and the
native `make_site` PA manifest.

This is probably a transitional artefact from the period when analysis modules
were also runnable as standalone browser apps. Decide the intended ownership
model and remove duplicated product defaults. The preferred direction for new
features such as BRB is that the producer/page contract owns defaults once and
the browser/runtime consumes them, with hardcoded JavaScript values used only
as defensive fallbacks.

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

### 5.4 Migrate Era Charts Before Shared Chart Styling

Banzuke Division by Era and Makuuchi Rank by Era are generated by repo Python,
but `make_site` still consumes them as complete standalone Plotly HTML pages.

Bring these charts into the site project before designing site-wide chart
styling. They should become either site-facing chart bundles or native
`make_site` chart views, so the shared styling work is based on real migrated
charts rather than an abstract target.

### 5.5 Chart Model Before Site-Wide Chart Styling

Consider what site-wide chart styling should mean only after the chart/page
model can describe the semantics that styling depends on.

The site-wide table styling work was difficult because the table model did not
always expose enough information about column roles, value types, interaction
states, and page-specific intent. Avoid repeating that with charts. Before
settling a shared chart skin, make sure chart definitions can express things
such as axis value types, trace roles, confidence/support displays, legend
policy, hover text policy, and whether a chart is a public exhibit,
comparison view, or diagnostic tool.

When styling is addressed, prefer calmer chart palettes over the current
garish standalone colours. A blue-to-grey spectrum may be a useful starting
point, with stronger colours reserved for explicit emphasis rather than used as
the default for every trace.

### 5.6 Support and Confidence Presentation

Charts such as matchup traces need support-aware interpretation.

Make sure public charts show sample size, confidence intervals, or equivalent
warnings where low-support points would otherwise look overprecise.

### 5.7 Clearly Distinct Trace Styles

Investigate algorithms for generating `n` clearly different trace line styles
when `n > 20`.

This matters for charts with many selectable traces, where colour alone is not
enough to make traces distinguishable. Candidate dimensions include colour,
dash pattern, marker shape, line width, opacity, and possibly grouped palettes
by division or subject.

The aim is not merely prettier charts. It is to preserve readability and
legend usefulness when many traces are visible or compared.

### 5.8 Legend vs Trace Options

Consider when a multi-trace chart should expose traces through the Plotly
legend, and when each trace should instead be treated as a page option.

A legend is natural when traces are few enough to scan, or when users are
expected to toggle visible lines directly in the chart. An explicit option
control may be better when the trace universe is large, when only one or a
small number of traces should usually be visible, or when trace selection needs
to participate in URL state, presets, or explanatory page grammar.

This decision may depend on whether the chart is an exploratory analysis tool,
a public exhibit, or a comparison page with carefully guided defaults.

### 5.9 Long X-Tick Labels

All charts with longish string x-tick labels should rotate those labels by
45 degrees.

"Longish" includes dates.

This should be treated as a chart readability rule, not as a one-off style
tweak for a single page.

### 5.10 Percentage Chart Defaults

Review all public charts whose y-axis is a percentage, probability, CDF, PMF,
survival curve, proportion, or other bounded 0--100% quantity.

Such charts should default to showing the full 0--100% y-axis unless there is a
documented page-specific reason to auto-scale by default.

### 5.11 Plotly Controls Hint

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

### 6.2 Page Self-Explanation

If the shell no longer shows page summaries, each loaded page must be
self-explanatory enough to stand on its own.

This does not mean verbose in-page instructions; it means good titles,
controls, labels, and explanatory affordances where needed.

### 6.3 Public vs Research Presentation

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

### 7.2 Consider Possible Mojibake Issues

Review public UI text and manifest/runtime-generated labels for possible
character-encoding issues.

This is not currently confirmed as a defect. The prompt for this item was a
code/read-through observation that some symbols appeared as mojibake-like text
in one view of the source or command output. Check the actual generated site,
source file encodings, and browser rendering before making any corrective
changes.

## 8. Deployment and Build Behaviour

### 8.1 Local and Remote Deployment Contract

The builder currently writes to `files/output/make_site` and can deploy to the
local web root. Remote deployment also exists.

The CLI already supports build-only, local-only, and combined local/remote
deployment modes. Remaining work is to document the intended publication
defaults, required environment variables/secrets, and any operator-facing
release checklist.

### 8.2 Deployment Root

The deployed root should be `sumo-tools`, not `site` or `make_site`.

Keep this distinction explicit: `make_site` is the builder package;
`sumo-tools` is the public site root.

### 8.3 Script Defaults Should Match Publication Defaults

The top-level `_run.ps1` should not need to override ordinary publication
parameters merely to produce the standard current-site build.

> Added 2026-05-12: change producer script defaults so the normal publication
> path is the no-surprises path.  For example, if the current banzuke date and
> output root are the normal Banzuke Changes publication settings, they should
> be the command defaults rather than explicit `_run.ps1` arguments.  Keep
> explicit arguments for genuine alternatives, diagnostics, and one-off local
> experiments.

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

### 11.0 Equelo Records

Consider a public Equelo Records feature family.

#### 11.0.1 Highest Rating

Add a candidate page or exhibit for the highest Equelo ratings observed in the
data.

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

### 11.2 Career Length Row Number

Career Length tables need an initial muted row-number column for orientation.

The row number should be visually quieter than the data columns and should not
be sortable.

### 11.3 Career Length Years Note

Review and rewrite the `Years` note for Career Length.

The current note is too long, but still does not cover an important point: how
to describe rikishi whose careers began before the canonical history epoch.
This may be because bio data was not available when the note was written. Now
that `get_bios` is available, reassess whether the page can use bio/hatsu
data to explain or qualify pre-epoch careers more clearly.

### 11.4 Career Length Active Display Option

Replace the visible `Active` column in the Longest Career table with an option
named `Show Active`.

The aim is to keep the default table simpler while preserving the ability to
inspect active status when that is the user's question.

## 12. Shared Presentation and Link Contracts

### 12.1 Generate Qualified Shikona in Sumo-Tools

Qualified shikona for external graph links currently depend on a brittle legacy
`full_shiks.pkl` file outside the Sumo-Tools project.

For now, accept this pickle as a legacy graph-module compatibility artefact.
It should be treated as part of the build input set, not as a well-founded
project identity source.

The legacy code that produces the pickle is:

```text
H:/Code/Sumo/Elo/v. 9/parser.py
```

The underlying mess still needs sorting out. The legacy graph module uses
shikona tokens rather than RikId, so duplicate shikona have to be
disambiguated outside the graph module. The legacy pickle appears to encode a
policy based on each rikishi's final/canonical shikona plus a year qualifier
when that final shikona is not unique. That policy is not yet validated, may
not be the right display policy for the current app, and should not be allowed
to determine how Sumo-Tools models rikishi identity.

The preferred long-term fix is to change the graph module to use RikId. Until
then, keep the compatibility boundary explicit and revisit whether any
Sumo-Tools-owned derived mapping is worth implementing.

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

The original policy is recorded in
`src/analysis/equelo/fixed_v1/docs/V5 Policy.md`; fixed_v2 currently reuses
the same landmark-cleaning idea on the Brierless rating scale.

### 12.3a Site-Wide CSS Rationalisation

The current renderer code contains repeated inline CSS for tool shells, option
panels, table panels, notes, links, and dark-theme variables.  Some duplication
is a transitional result of standalone app/page integration, but promoted
public pages should not each carry their own private copy of the same site
chrome.

Extract shared page, tool, table, chart, control, note, and link styling into
site-wide CSS assets where possible.  Page-specific CSS should describe genuine
local layout or visualization needs, not restate the public shell grammar.

This should be coordinated with the direct-rendering and PA-runtime work so
that new pages such as BRB inherit shared styling by default rather than adding
another bespoke inline stylesheet.

### 12.4 Sortable Public Tables

All public table columns should be sortable where sorting makes sense.

Use the interaction style from "Grand Sumo Standings by Wins Digest" as the
reference. Non-data columns such as row numbers should not be sortable.

Chii-like values must sort by their model/order ordinal, not alphabetically.
This matters for full chii values, sideless chii labels, and any table where
alphabetical order would put values such as `J10` before `J2`.

### 12.5 Table Scrolling Policy

As part of site review, inspect each public table and decide whether it should
be constrained to the content panel.

For long tables, make an explicit page-level decision about whether scrolling
should happen inside the table/content panel with sticky column headers, or in
the browser window with the whole page moving. Use Career Length -> Longest as
the reference pattern for the constrained-table option: the table body scrolls
while column headers remain visible. The right answer may differ between dense
tools, chart-and-table pages, and legacy embedded artefacts.

### 12.6 Table Header Wording and Wrapping

Review public table column headings for readable display names and compact
layout.

Do not expose implementation-style headings with underscores, such as
`after_basho_chii`. Use separate words such as "After Basho Chii". When
headings are long, prefer centre-justified line breaks inside the header cell
so the header becomes taller rather than forcing the table wider.

### 12.7 Equelo Landmark vs Process Rating Validation

When BRB has its first rating lookup table, compare actual fixed_v2 process
ratings against the illustrative `Typical Equelo Ratings` landmarks for the
corresponding chii.

The goal is not to force the two to agree.  The landmarks are illustrative only.
The goal is to understand how wide the gap is in real data, especially around
division boundaries, fast-rising rikishi, absences, protected ranks, and noisy
lower-support chii areas.  Use the result to decide whether public wording
needs stronger caveats.

> Updated 2026-05-12: this validation should use fixed_v2 process ratings and
> fixed_v2 public landmarks.  Brier/fixed_v1 comparisons remain useful as
> historical diagnostics, but they are no longer the current public-site scale
> contract.

### 12.8 Chii and ChiiLabel Naming Policy

Put the Chii naming policy front and centre in the main project/site docs.

Use `Chii` for the class/object, `chii` for full human-facing chii values such
as `M3eHD`, and `ChiiLabel` for project-defined chii-like labels such as `M3`,
`O`, or `Jd100`.

Avoid using "rank" as a substitute for these concepts in technical docs, page
contracts, generated metadata, code comments, and policy notes. This matters
especially for Equelo rating landmarks, where the distinction between a chii,
a `ChiiLabel`, and a rating must stay explicit.

### 12.9 Source Layout vs Site Navigation

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

### 12.10 Semantic Table Column Styling

Consider implementing semantic table column styling metadata.

Current table styling is often attached to local column ids or page-specific
CSS. This lets the same kind of value drift between pages: chii values,
chii-like Banzuke Changes rank/context strings, Equelo ratings, row numbers,
records, movement markers, and previous/context columns can each receive
different alignment, colour, or typography depending on the table that happens
to render them.

The proposed direction is to add semantic column metadata such as `value_kind`
and possibly `role`, then emit shared classes like `value-chii`,
`value-rating`, `value-row-number`, and `role-previous`. Site-wide CSS can then
define the default presentation of each value kind, while page-specific CSS is
reserved for documented local exceptions.

The working proposal is recorded in
`src/products/make_site/docs/current/Semantic Table Column Styling Proposal.md`.

### 12.11 Date Type Boundary Policy

Use the canonical `sumo_core.History.Date` type for basho dates wherever the
project is doing domain work.

The parser currently has an `IntDate` convenience type. If possible, replace
`IntDate` with `Date(Year(...), Month(...))` throughout the parser and related
code so there is one project date type rather than two nearly equivalent
forms.

Dates loaded from CSV, JSON, or other serialized artefacts need explicit review
at the load boundary. The strict default should be to cast basho dates back to
`Date` immediately. A string date may be acceptable only when it is genuinely
being carried straight through as display/output text and not used for domain
logic, ordering, lookup, identity, joins, or page-state contracts.
