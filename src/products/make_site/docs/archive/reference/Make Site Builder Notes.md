# Make Site Builder Notes

This note records implementation observations that arose while exercising the
first `make_site` builder.

## Current Landing Page

The first generated landing page is intentionally plain HTML. That is
acceptable at this stage, but it is incomplete as a navigation stress test.

The landing page should eventually render the full provisional navigation
scope, including planned/unimplemented entries, not only the pages currently
present in `SITE.pages`.

This matters because the page is currently being used to inspect information
architecture as much as to open working pages.

The final UI shell is still open. The current landing page does not yet express
the intended "navigation sidebar plus content" layout.

## Plotly Legend Double-Click

Plotly's built-in legend double-click behaviour has shown undesirable behaviour
in at least one of the multi-trace charts: double-clicking some legend entries
can show all traces rather than isolating the clicked trace.

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

This policy should be applied to every Plotly chart that becomes part of the
public site, unless a specific chart has a documented reason to keep Plotly's
default double-click behaviour.

## Annoying Browser Bugs

Firefox did not show the implemented navigation links in red, even though the
generated HTML used `class="nav-link"` and the deployed CSS contained
`.nav-link { color: #ff3030; }`.

Chrome displayed the red links correctly. Firefox should be investigated later
with developer tools by checking the computed colour of a clickable nav link
and confirming whether `site-shell.css` is being applied, overridden, or
ignored.
