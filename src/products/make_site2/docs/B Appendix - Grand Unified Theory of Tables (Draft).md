# B Appendix - Grand Unified Theory of Tables (Draft)

## Status

Draft scratchpad for table-shaped presentation ideas in `make_site2`.

This appendix is not an active specification. It records algebraic/model ideas
that may become useful later. The current implementation remains governed by
the main specification and design documents.

The point of this appendix is to provide a safe place for the recurring itch to
define the Grand Unified Theory of Tables without forcing the site to implement
that theory now.

---

## 1. Why This Exists

The presentation of tables is susceptible to an abstract, algebraic account.
There is evidence for this in the treatment of structured tables as in **7.1
Basho Results**, and multi-dimensional charts as in **3.3 Career Comparisons**.

These are rough notes on the subject. They do not have to make full sense yet.
They collect anything that may be relevant to a future general model.

---

## 2. Current Rule

Do not generalise the 7.1 recursive table model into a universal table model
now.

The apparent commonality is real:

- flat tables can be treated as depth-one recursive tables;
- grouped tables resemble shallow hierarchical tables;
- charts can be treated as rendered projections of logical tables.

However, unification would require settled semantics for:

- projection;
- hidden leaves;
- whether group headings collapse or persist when only one child remains
  visible;
- view-specific table specs;
- sort identity across projected leaves;
- section/custom-table boundaries;
- chart trace identity;
- presentation dimensions versus filter/projection dimensions.

That is too much model work for current implementation pressure. Keep 7.1
recursive tables and ordinary/non-7.1 table renderers separate for now. Prefer
shared CSS/helper/rendering policy for genuinely common concerns such as
alignment, typography, padding, row treatment, link styling and sortable-heading
presentation.

Reopen model unification only if repeated styling or behavioural divergence
becomes worse than the cost of defining the general table theory.

---

## 3. Evidence: Basho Results

Basho Results is the monster table.

The active model is in:

```text
04.5 Basho Results Model.md
04.5.1 Basho Results Model - Public Artifact Shape.md
04.5.2 Basho Results Model - Recursive Table Structure.md
04.5.3 Basho Results Model - Public Projections and Analysis.md
04.5.4 Basho Results Model - Temporal Alignment and Sorting.md
```

The key abstract ideas are:

- a table specification can be an ordered recursive keyed structure;
- terminal paths are stable column identities;
- terminal paths play the role that flat column ids play in ordinary table PAs;
- terminal paths resolve to concrete display values or null/empty values;
- public options project or hide parts of the resolved table;
- options do not decide whether values conceptually exist;
- group headings are presentation context, not necessarily sortable values;
- visible leaf headings are the sortable public columns.

The 7.1 docs explicitly keep this local to Basho Results. They do not decide
that ordinary flat table PAs must use the recursive shape.

---

## 4. Evidence: Career Comparisons

Most charts are conceptually tables that happen to be rendered as charts.

For **3.3 Career Comparisons**, the physical source is JSON:

```text
trajectory_master.json
```

But the source is table-like. It can be understood as a logical table:

```text
rikishi_id
date
shikona
chii
equelo
```

The JSON representation:

```text
points_by_rikishi[rid] = [[date, shikona, chii, equelo], ...]
```

is an index-oriented representation of that table, not a fundamentally
different kind of artifact.

The chart view projects the logical table into Plotly traces:

```text
trace = rikishi_id
x = date | basho_index_from_first_appearance
y = equelo | chii_value | both as paired y/y2 series
transform = linear | log/compressed
hover = shikona, date, full_chii, rating
```

Plotly handles one presentation dimension as multiple traces. In the Both view,
one logical selected rikishi becomes two presentation traces: solid chii on the
primary y-axis and dotted Equelo on the secondary y-axis. Other dimensions are
handled by selector controls and options. Bells and whistles are handled by
filters/checks/toggles. The present UI vocabulary is messy: the panel may be
called `FilterPanel`, the heading may say `Options`, and the widgets may mix
projection controls and filters. This appendix does not try to settle that.

---

## 5. Abstract Formulation

A useful middle layer is missing from the casual vocabulary. One purpose of
this draft is to articulate that middle layer: the logical table or dataset
that sits between physical source artifacts and rendered presentation
artifacts.

Low-level source artifacts:

```text
CSV
JSON
family of CSV files
family of JSON files
```

High-level presentation artifacts:

```text
HTML table
Plotly chart
special recursive Basho Results table
```

Middle semantic layer:

```text
logical dataset / logical table
```

A chart is not fundamentally "data shaped like a chart". It is a rendering of a
projected logical table. A table is also a rendering of a projected logical
table. The renderer differs; the data semantics need not.

Possible abstraction levels:

```text
1. Source Artifact
   Physical producer output: CSV, JSON, family of files.

2. Logical Dataset
   Semantic row/column model implied by the source artifact.

3. View Projection
   User-selected slice and derived columns: x, y, trace, hover, labels.

4. Presentation Artifact
   Renderer-specific output: HTML table, Plotly chart, recursive table.
```

Sketch:

```text
Source artifact  ------load------>  Logical dataset
      |                                  |
      | stage/copy                       | project/filter/derive
      v                                  v
Public data file ----runtime load---> View dataset
                                         |
                                         | render
                                         v
                              Presentation artifact
```

For 3.3:

```text
trajectory_master.json
  -> trajectory logical table
  -> selected rikishi + chart mode projection
  -> Plotly trace chart
```

For 7.1:

```text
Basho Results payload
  -> recursive row/terminal-path logical table
  -> selected division + public projection options + sort state
  -> recursive HTML table
```

This is the table/chart commutative diagram itch. It may become useful. It is
not an implementation instruction yet.
