# Table Structure Design Gap

## Status

Focused working note for the table-like Published Artifact model.

This note records a design gap exposed by 7.1 Basho Results. It deliberately
stops short of prescribing the replacement framework. The next design step is
to decide whether and how to introduce a uniform table-structure model.

---

## 1. The Gap

The current `make_site2` table model is partly prototype-derived.

It is good enough to render existing pages, but it does not fully describe what
a table-like analytical object can be. The design has therefore drifted toward
discovering table structure by making code changes rather than by applying a
settled table model.

The immediate pressure case is 7.1 Basho Results:

- it is an indexed table because a selected basho chooses a payload;
- but its main modelling problem is not indexing;
- its main modelling problem is that the visible table has temporal column
  groups such as `Before Basho`, `Current` and `After Basho`.

Indexing and internal table structure are orthogonal.

---

## 2. What Still Looks Correct

The following parts of the current model remain useful and should be
ring-fenced rather than thrown away:

- `PAPanel -> PA . Notes`;
- broad PA terminal forms such as table, indexed table, chart, sectioned table,
  prose and custom artifact;
- the idea that an indexed table selects a visible table instance from an
  indexed set of data instances;
- the distinction between PA-specific visible meaning and shared table
  rendering treatment;
- shared table rendering treatments such as padding, row striping, sticky
  headings, table-body scrolling and sortable heading controls where compatible;
- the rule that custom artifacts remain inside the PA region and do not own
  the surrounding PublicUI shell.

These can stand while the internals of table-like PAs are reconsidered.

---

## 3. What Is Provisional

The current table structure model is provisional.

The docs name `column_model` and `column_group_model`, and the implementation
has a `ColumnGroup` dataclass:

```text
ColumnGroup
  id
  heading
  columns
  always_visible
  controlling_filter_id
```

However, the relationship between columns and groups is not fully specified.
The current implementation stores:

```text
columns: list[TableColumn]
column_groups: list[ColumnGroup]
```

with each column also pointing back to a group by id.

This leaves important questions under-specified:

- does the column list or group list define visible order?
- can a table layout contain both ungrouped columns and grouped columns?
- are groups allowed to nest?
- is a column group a semantic object, a rendering convenience, or both?
- can group headings vary at runtime, such as `Current` versus `After Basho`?
- do groups own notes, visibility, boundaries or sort policy?
- should group membership be defined by the group, by the column, or by a
  single layout tree?

The clean conceptual model may be closer to:

```text
Table
  column_layout: non-empty list of ColumnRef | ColumnGroup

ColumnGroup
  heading
  children: non-empty list of ColumnRef | ColumnGroup
```

This is only a candidate shape. It is not yet adopted.

---

## 4. Existing Pressure Cases

Multiple current pages already show table hierarchy pressure:

```text
2.2 Standings by Wins
  grouped metric columns such as Wins per Basho and Wins per Bout.

7.1 Basho Results
  temporal column groups such as Before Basho and Current/After Basho.

2.1 Banzuke Changes
  banzuke-shaped East/West/rank structure, currently treated as a custom
  artifact but still table-like in rendering.
```

These are not identical needs. That is exactly why the framework should not be
invented casually inside the 7.1 indexed-table renderer.

---

## 5. Prototype Lesson

The current `ColumnGroup` implementation is useful evidence, not a settled
specification.

It has already shown that:

- table column groups are real public structure;
- group visibility can be tied to filter state;
- grouped headings can make duplicate column labels intelligible;
- indexing does not explain grouped table structure; and
- a flat row/column description is not enough for every promoted table-like PA.

The next design should use those lessons while avoiding unnecessary churn.

---

## 6. Next Step

Do not immediately create a new PA terminal form or large abstraction.

The next step is:

1. Sort out the 7.1 model as a concrete pressure case.
2. Decide the minimum table-structure framework needed to express it honestly.
3. Check whether the same framework naturally covers 2.2 and any ordinary
   non-indexed table cases.
4. Only then update the normative table model and implementation.

