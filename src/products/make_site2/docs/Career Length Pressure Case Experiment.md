# Career Length Pressure Case Experiment

## Purpose

This experiment tested the original working hypothesis that Career Length was
the G2 pressure case:

```text
Charts
  filter: chart = distribution | PMF | CDF | survival

Longest
  filter: active = all rikishi | active only
```

That hypothesis was wrong.

The first implementation rendered two visible artefacts at once: one chart and
one table. That exposed the logical error in the model. Career Length should
show exactly one visible artefact:

```text
distribution chart
or PMF chart
or CDF chart
or survival chart
or Longest table
```

The correction is to replace original G2 with G2b: branch-selected contents.

## Revised Page Model

```text
Page id: career_length
Grammar: G2b
Status: prototype
Branches:
  Chart
  Table
```

Branch selector:

```text
branch = chart | table
```

Branch-local filters:

```text
Chart:
  chart = distribution | pmf | cdf | survival

Table:
  active = all | active
```

So the visible structure is:

```text
ContentPanel
  Heading
  BranchSelector
    Chart | Table
  Selected Branch
    FilterSection
    PA
  Note*
    table notes only when branch = table
```

## What Changed

The first G2 implementation had:

```text
ContentPanel
  Charts PA
  Longest PA
```

The corrected implementation has:

```text
ContentPanel
  BranchSelector
    Chart | Table
  Branch: Chart
    FilterSection
      chart
    PA
      selected career-length chart
  Branch: Table
    FilterSection
      active
    PA
      Longest Careers table
```

This preserves the important distinction from the old `PASet` framing:

- the page is not five separate flat choices;
- it is not two simultaneous PAs;
- it is a nested branch-selected contents structure;
- the parse tree, not hand-written display logic, determines that only one
  branch PA is visible.

## Build Output

The builder emits:

```text
manifests/career_length.json
data/career-length/distribution.csv
data/career-length/pmf.csv
data/career-length/cdf.csv
data/career-length/survival.csv
data/career-length/longest.csv
data/career-length/metadata.json
data/career-length/page.json
```

The manifest now records:

```text
grammar: G2b
branchSelector:
  branch = chart | table
branches:
  chart
    filters: chart
    pa: career_length_chart
  table
    filters: active
    pa: longest_careers
```

## Browser Checks

Default state:

```text
branch = chart
chart = distribution
visible chart count: 1
visible table rows: 0
notes: 0
table branch filters disabled
```

Table branch:

```text
branch = table
visible chart count: 0
visible table rows: 50
notes: 1
chart branch filters disabled
URL: ?branch=table&chart=distribution&active=all#page=career_length
```

Active-only Longest state:

```text
branch = table
active = active
visible table rows: 16
URL: ?branch=table&chart=distribution&active=active#page=career_length
```

## Model Lesson

This case study changed the model.

The earlier G1/G2 partition was too eager to treat differing filter scopes as
different simultaneous PAs. Career Length shows another shape:

```text
Contents may choose exactly one Branch.
Each Branch owns branch-local filters and one PA.
```

This is not the same as reverting to the old flat implementation term `View`.
The model is nested:

```text
select branch
then apply branch-local filters
then render selected branch PA
```

not about a legacy page-view mechanism.

## Remaining Gaps

This corrected slice is still prototype quality.

Known gaps:

- chart rendering is simple SVG;
- table rendering caps Longest at 100 rows for usability;
- table sorting for Longest is not yet wired;
- chart hover behavior is not implemented;
- G2b semantics need to be merged into the main migration plan;
- automated tests should cover one-visible-artefact behavior.

## Next Experiment

The last original case-study bucket remains:

```text
finish_by_chii
```

Its expected target shape is still G1:

```text
ContentPanel
  Heading
  FilterSection
    shared filters
  PA+
    chart PA
    chart PA
    chart PA
  Note*
    empty
```
