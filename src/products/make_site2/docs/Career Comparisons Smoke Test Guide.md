# Career Comparisons Smoke Test Guide

Draft guide for manual review while the Career Comparisons chart is still under
active construction.

This is not a formal acceptance test plan. It is a checklist for noticing
obvious nonsense before promoting the chart shape.

## 1. Empty State

Open **3.3 Career Comparisons** with the default options:

- Skill / x mode: `Chii / Date`.
- Scale: `Log` checked.
- No rikishi selected.

Expected:

- The page should not render an empty Plotly chart with invented axes.
- It should show a simple prompt to select one or more rikishi.
- The filter/options panel should remain stable.
- The Rikishi text box should receive focus when the page opens.
- Selecting a rikishi from suggestions should add that rikishi, clear the text
  box, close the suggestion popup and leave the text box ready for another
  entry.

## 2. Known-Rikishi Sanity Checks

Pick one rikishi whose career shape is familiar.

Suggested checks:

- Does a famous Yokozuna rise toward the top of the chii chart over time?
- Does an ordinary lower-division rikishi remain in the lower compressed region?
- Does the Equelo trace broadly rise and fall in the expected career phases?
- Are obvious peak years in roughly the right location?

If the result looks impossible, first check that the selected rikishi id is the
intended rikishi. Shikona are not unique; a label such as `Hakuho (8206)` is not
necessarily the famous Hakuho.

## 3. Two-Rikishi Comparison

Select two rikishi.

Expected:

- Both traces appear.
- The x-axis range covers both careers.
- Adding the second rikishi after plotting the first should immediately
  recalculate the visible x/y ranges.
- Hover text shows shikona, date, full chii and Equelo.
- The legend names identify the selected rikishi clearly enough to notice
  shikona collisions.

## 4. Chart-Mode Matrix

For the same selected rikishi, check all six mode choices:

- `Chii / Date`
- `Chii / Basho`
- `Equelo / Date`
- `Equelo / Basho`
- `Both / Date`
- `Both / Basho`

For each mode, toggle `Log`.

Expected:

- Date mode uses date-like x ticks and the x-axis title `Date`.
- Basho mode starts at zero for each rikishi.
- Chii mode uses human chii labels and keeps full chii in hover text.
- Equelo mode omits points with no rating rather than inventing a value.
- Both mode draws chii on the primary left y-axis and Equelo on the secondary
  right y-axis.
- In Both mode, each rikishi has a solid chii line and a dotted Equelo line in
  the same colour.
- Switching modes should redraw the chart immediately, not preserve a stale axis
  range from the previous view.

## 5. Chii Compression

In `Chii` + `Log` mode:

- Sanyaku through Juryo should occupy the top part of the chart.
- Makushita through Jonokuchi should occupy the lower compressed part.
- Lower-division detail is allowed to be compressed heavily.
- The top/lower split is controlled by `TOP_CHART_PROP`.

## 6. Selector Checks

Try selector searches for:

- a unique shikona;
- a reused shikona;
- a partial string that matches many rikishi;
- a numeric rikishi id.

Expected:

- Already-selected rikishi are not offered again.
- Choosing an exact candidate immediately adds that rikishi to the selected list
  and clears/closes the search box.
- The selected list can grow without moving the chart-mode controls.
- `X` removes the intended rikishi.
- Adding or removing a rikishi redraws the chart immediately.

## 7. Link Sharing

Expected:

- The URL encodes `skill`, `x_base`, `log` and selected rikishi ids.
- Opening the URL reconstructs the same chart.
- The selector list and Plotly traces agree with the URL state.
- `skill=both` URLs reconstruct the dual-axis Both view.
