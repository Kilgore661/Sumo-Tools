# Rendering Change Review - 03 Design Classification

## 3. First-Pass Design Classification

The proposed change set is understandable and mostly precise enough to begin
design work. It should not be implemented as an undifferentiated CSS pass.

The subsections below classify each proposed change by ownership and
implementation impact. Section 4 then groups the work into likely implementation
streams.

### 3.1 Help/popover marker URL state

The visible info-here marker is no longer primarily a production/development
split. It is proposed as an explicit URL-selected diagnostic mode owned by the
public/runtime state layer:

```text
debug_show_notes=true
```

This is a runtime presentation-state feature. It should be treated similarly to a
reader/reviewer display mode: absent or false hides the indicator; true shows it.

The `--prod` question remains separate. `--prod` may or may not imply removal of
stylistic debugging features, but that is an open build-mode policy decision and
should not be assumed by the `debug_show_notes` design.

### 3.2 Table heading spacing

This is shared table/PA-caption rendering policy. It belongs to table-like PA
presentation and/or PA caption spacing, not to the Public UI Model.

### 3.3 Interim table structure and column groups

The table structure requests are deliberately narrower than a general table
model. The implementation should use an interim, easy-to-remove mechanism for
non-7.1 column-group declarations.

The steer is: choose the approach that is easiest to remove later when a general
table model supersedes it. Avoid spreading table-group theory across unrelated
renderers and avoid migrating ordinary tables into the recursive table model as
part of this change.

### 3.4 Table border and column-group policy

The general table bounding box, lowest-heading underline and suppression of other
grid lines are shared table rendering policy.

Column-group boundary lines require explicit column-group knowledge. For 7.1
Basho Results, that knowledge is already model-driven by the recursive/grouped
table structure. For tables other than 7.1, there shall be a mechanism for
defining column groups. The default is “no groups here”; individual flat columns
must not automatically imply column groups.

### 3.5 Alternating row colours

This is theme/token tuning inside an already accepted shared table rule.

### 3.6 Shikona links

This is runtime interaction and public-link policy, not styling. It should be
implemented as shared shikona-link semantics so all table renderers behave
consistently.

### 3.7 Basho selector redesign

This was implemented as a PA-specific Basho Results runtime control inside the
existing `FilterSection`, rather than as a general new filter-control model.

The implementation changes the control from a single finite basho selector into
a compound Basho block with Year and Month dropdowns plus navigation buttons. The
public URL state is `year` and `month`. Legacy basho date parameters are treated
as compatibility input where practical.

Valid no-basho states are supported only for supported sumo years and the six
sumo months. Bad URL handling remains a separate, broader routing concern.

### 3.8 Section 9.1 vertically spanning headings

This is currently resolved by the interim 9.1 column-group declaration. If a later
general table model is adopted, this rule should be revisited and may become
redundant.

### 3.9 Muted foreground colour

This is a shared theme token, but it carries semantic meaning wherever used. It
needs a declared owner and scope, such as row numbers, navigation placeholders,
unavailable items or secondary metadata.

### 3.10 Row-number column on all tables

This is table model/rendering policy, not merely CSS.

### 3.11 Superlative tables and ordinal/ranking columns

This is part of the same row-number/ranking policy. It needs a table-model
concept or explicit shared table-rendering policy.

### 3.12 Date separator

This is a shared data-formatting/rendering rule for date-like values in public
rendered display. It should not be assumed to change source data, CSV contracts,
filenames, URL parameters, internal identifiers or other non-display contexts
where `/` is normal unless a later requirement says so.

### 3.13 Popovers that mention Notes

This is runtime interaction/state plus a text-triggered popover action rule. The
qualifying condition is exact text occurrence of `Notes`; the whole popover owns
the click.

Status: implemented for Notes popovers. Remaining link/popover work is shikona
Alt-click and shikona link help text.

### 3.14 Conditional x-axis tick rotation

This is shared chart rendering policy. The current behavior may be applying a
fixed artifact value where a dynamic rule is wanted.

### 3.15 Bold axis titles

This is a shared Plotly chart presentation rule. It has low model impact, but it
should still be declared as chart rendering policy.

### 3.16 Specific charts should be line charts

This is a product/PA-form change, not CSS. It changes the PA terminal form or
chart renderer choice, and should be checked against the public analytical
question because bar/column charts and line charts make different claims.

### 3.17 Section 6.3.1 error bars

This is a PA-specific chart rendering rule. Because error bars communicate
uncertainty, the colour choice should be declared as belonging to that PA feature.
