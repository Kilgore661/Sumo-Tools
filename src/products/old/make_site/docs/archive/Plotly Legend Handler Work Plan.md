# Plotly Legend Handler Work Plan

## Status

Complete for the original chart migration set.

The original legend-handler issue has been fixed for the currently promoted
legend-bearing charts.  Career Length / Distribution, Division Stability,
Banzuke Division by Era, and Makuuchi Rank by Era all disable Plotly's built-in
legend double-click behaviour and install explicit site-owned isolation
handling.

Banzuke Division by Era, Division Stability, and Makuuchi Rank by Era are now
PA-backed site pages rather than copied standalone Plotly HTML pages.

## Problem

Plotly's default legend double-click behaviour is not reliable enough for
public multi-trace charts.  The observed failure mode is that double-clicking
some legend entries can reveal all traces rather than isolating the selected
trace.

The site already has a custom double-click isolation pattern in the Win
Probability by Standing chart.  That pattern should become the required public
chart behaviour for Plotly charts with legends, unless a chart has a documented
reason to use Plotly's default behaviour.

## Scope

This plan covers public Plotly charts with meaningful legends.

The following charts have moved into site-owned rendering:

* Career Length / Distribution;
* Division Stability;
* Banzuke Division by Era;
* Makuuchi Rank by Era.

## Plan

### 1. Update the Plotly Legend Policy

Strengthen the current policy from "apply this policy" to an explicit
requirement:

* public Plotly charts with visible legends shall disable Plotly's built-in
  legend double-click behaviour;
* they shall install the custom double-click isolation handler;
* any exception shall be documented in the chart definition or nearby renderer
  notes.

Keep the existing Win Probability by Standing implementation as the reference
pattern, including scoped isolation where a chart has an active filter such as
division.

### 2. Fix Career Length / Distribution

Add the custom handler to the Career Length distribution chart.

This chart is already a native PA-backed page.  The handler isolates either
`Retired` or `Active` on double-click and leaves ordinary legend
click-to-toggle behaviour unchanged.

The PMF, CDF, Survival, Longest, and Rank at Retirement views do not need the
handler unless they later gain meaningful multi-trace legends.

### 3. Convert Division Stability to a PA Chart

Change the persistence report path from an HTML chart producer into a
site-facing data producer.

The analysis code should write stable data artefacts such as CSV, JSON config,
and metadata.  The public site should then expose Division Stability as a PA
chart, so the shared chart policy, theme, legend behaviour, notes, and URL-state
model live in `make_site` rather than inside standalone generated HTML.

Complete.  The persistence producer writes a site bundle and `make_site`
renders Division Stability as a PA-backed Plotly page.

### 4. Re-implement Banzuke Division by Era In-House

Move Banzuke Division by Era out of standalone HTML incorporation.

The chart producer should emit site-facing data and metadata, and `make_site`
should render it as a native chart or PA chart bundle.  Once migrated, it should
use the standard Plotly legend double-click handler rather than bespoke embedded
HTML behaviour.

Complete.  Banzuke Division by Era now writes a site bundle and `make_site`
renders it as a PA-backed Plotly page.

### 5. Re-implement Makuuchi Rank by Era In-House

Move Makuuchi Rank by Era out of standalone HTML incorporation using the same
model as Banzuke Division by Era.

This keeps the two era charts aligned and avoids preserving one-off Plotly page
templates whose interaction policy can drift away from the rest of the public
site.

Complete.  Makuuchi Rank by Era now writes a site bundle and is rendered by
`make_site` as a PA-backed chart.

## Completion Criteria

The work is complete when:

* the current policy documents state that custom legend double-click handling is
  required for public Plotly charts with visible legends;
* Career Length / Distribution implements the handler;
* Division Stability is no longer incorporated as standalone HTML;
* Makuuchi Rank by Era is no longer incorporated as standalone HTML;
* Banzuke Division by Era is no longer incorporated as standalone HTML;
* each migrated legend-bearing chart has verified ordinary click-to-toggle and
  double-click-to-isolate behaviour.
