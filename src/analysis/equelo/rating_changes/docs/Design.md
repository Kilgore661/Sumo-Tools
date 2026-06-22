# Rating Changes Design

## 1. Design stance

`Rating Changes` should be designed as a make_site2 UI-model instance, not as a direct translation of the exploratory package.

The exploratory `rating_changes` code is evidence. It helped clarify measures, columns, and reader-facing questions, but it is not a source of truth. The final implementation should follow the requirements, specification, and this design. Existing prototype code may be reused only if it matches the final design closely enough to make reuse simpler than rewriting.

The design goal is to make the page fit the existing make_site2 pattern:

```text
producer data
  -> artifact/data declaration
  -> UI model / presentation bridge
  -> renderer
```

The important design question is therefore:

```text
What is the UI model instance for Rating Changes?
```

Once that is right, rendering should mostly follow established make_site2 patterns.

## 2. UI model position

`Rating Changes` is a page containing one table artifact.

The artifact is not a simple flat generic table. Its raw data may be flat, but its public presentation is a grouped table with two heading levels and projection filters.

The page fits the public UI model as:

```text
ContentPanel
  Heading
  Contents
    FilterSection
    PAPanel
      PA: Rating Changes table
      Notes
```

The table artifact has:

- one main data selector: `n`;
- projection filters: `Basis` and `Normalised`;
- notes explaining the important public measures;
- a grouped presentation table with `Context`, `Expected`, and `Actual` column groups.

## 3. Page and artifact model

The page is a public-facing Equelo analysis page.

Working identity:

```text
page id: rating_changes
title: Rating Changes
```

The artifact is one logical table showing rikishi ranked by Equelo movement over a selected recent-basho window.

The first public version uses the latest represented basho only. It does not expose a basho selector. Historical date selection remains deferred.

The artifact data grain is:

```text
latest represented basho × n
```

Changing `n` selects a different raw data set. Changing `Basis` or `Normalised` changes only the projected table columns.

## 4. Filter model

The filters are part of the artifact contract.

### 4.1 n

`n` is the main data selector.

It selects the number of basho in the rating-change window. Candidate values are:

```text
1, 2, 3, 4, 5, 6, 12
```

The selected `n` determines which raw table is loaded.

### 4.2 Basis

`Basis` is a mutually exclusive projection filter.

Values:

```text
Expected
Actual
Both
```

Default:

```text
Expected
```

`Basis` controls whether the table shows the `Expected` group, the `Actual` group, or both groups. It does not select a different raw data file.

### 4.3 Normalised

`Normalised` is a checkbox projection filter.

Default:

```text
unchecked
```

When unchecked, the table shows ordinary rating-point movement columns. When checked, the table also exposes the K-normalised per-bout movement columns.

The exact public label can be refined later, but the filter concept is stable: it controls whether the reader sees the more technical K-normalised measures.

## 5. Presentation table model

The rendered table has two heading levels.

Top-level groups:

```text
Context
Expected
Actual
```

### 5.1 Context group

`Context` identifies the rikishi and the raw rating movement over the selected window.

Terminals:

```text
rikishi_id
shikona
chii_at_start
chii_at_end
rating_at_start
rating_at_end
delta
```

The chii ordinal fields are not display terminals in the normal view. They are sort support fields:

```text
chii_ordinal_at_start
chii_ordinal_at_end
```

### 5.2 Expected group

`Expected` measures movement against the full opportunity window.

Terminals:

```text
expected_bouts
delta_per_expected_bout
normalised_delta_per_expected_bout
```

`normalised_delta_per_expected_bout` is only visible when `Normalised` is checked.

### 5.3 Actual group

`Actual` measures movement against bouts actually fought.

Terminals:

```text
actual_bouts
delta_per_actual_bout
normalised_delta_per_actual_bout
```

`normalised_delta_per_actual_bout` is only visible when `Normalised` is checked.

## 6. Projection model

Projection is based on `Basis` and `Normalised`.

```text
Basis = Expected
  show Context + Expected

Basis = Actual
  show Context + Actual

Basis = Both
  show Context + Expected + Actual
```

```text
Normalised unchecked
  hide normalised per-bout terminals

Normalised checked
  show normalised per-bout terminals
```

This means the initial public view is simple:

```text
Context + Expected, without normalised columns
```

The reader can then opt into the actual-bout view, both bases, and the more technical normalised measures.

## 7. Data boundary and bridge

The producer should emit enough data to support the public table. The raw producer output does not need to mirror the rendered table structure.

The bridge is responsible for mapping raw rows to presentation terminals.

Conceptually:

```text
raw row
  -> presentation row values
  -> projected terminal paths
  -> grouped table renderer
```

This follows the Basho Results Browser pattern:

```text
flat payload
  -> runtime bridge
  -> recursive/grouped table model
  -> renderer
```

The bridge should keep data selection separate from projection:

- `n` affects which raw data set is loaded;
- `Basis` and `Normalised` affect only visible terminals.

## 8. Rendering pattern

The closest existing pattern is `page=basho_results_browser`.

Relevant similarities:

- flat produced data is transformed before rendering;
- the rendered table has grouped headings;
- projection filters alter visible terminal columns;
- sorting and alignment should come from table/presentation metadata where possible.

Important differences:

- Rating Changes first version has no basho selector;
- Rating Changes has one main data selector, `n`;
- Rating Changes has a smaller table model and should not inherit Basho Results domain names such as `before`, `selected`, or `changes`.

The design should use the Basho Results architecture, not the Basho Results domain model.

## 9. Sorting and alignment

Default sort:

```text
delta descending
```

Visible numeric columns should be sortable.

Chii display fields should sort through their ordinal support fields:

```text
chii_at_start -> chii_ordinal_at_start
chii_at_end   -> chii_ordinal_at_end
```

Alignment follows the settled make_site2 table policy:

```text
headings
  centered

value strings that evaluate to numbers
  right-aligned

special non-numerical value strings
  centered

all other value strings
  left-aligned
```

No special alignment rule is currently required for Rating Changes beyond that shared policy.

## 10. Notes and popovers

The page should have notes for reader-facing concepts that are not obvious from the heading alone.

Likely note topics:

```text
delta
expected vs actual basis
normalised / K-adjusted measures
```

Filter popovers may provide short explanations, but longer explanations should live in Notes.

The page should follow the site-wide popover/notes policy. In particular, note links from popovers should only be used where the target note is present and meaningful for the current artifact.

## 11. Non-goals

The first public version does not include:

- a historical basho selector;
- all historical `(date, n)` raw files;
- a winning/losing streak table;
- a fusen-specific interpretation change;
- a full unification of all table renderers.

The streak question is explicitly separate: `Rating Changes` asks who changed most over a selected window. A later streak table can ask whose rating has moved in the same direction for consecutive basho.

## 12. Deferred questions

Deferred questions include:

- whether a final/final build should include historical `(date, n)` files;
- whether the public page should later add a basho selector;
- how fusen-sho and fusen-pai should be treated in explanation or calculation;
- final reader-facing labels for K-normalised measures;
- whether normalised columns should be shown in addition to, or instead of, raw per-bout columns in a future refined UI;
- whether the grouped-table renderer should be generalized after this page and Basho Results have both exercised the pattern.
