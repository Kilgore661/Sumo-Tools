# Implementation Approach - Fastest Risers Site Artifact

## Status

This document records the intended implementation approach for adding the
Fastest Risers artifact to `make_site89`. It is a design decision, not an
implementation. The producer contract and visible UI requirements are recorded
separately in this package.

The first website version is a proof of concept using the `1989/01` supporting
boundary and admitting starter cohorts from `1989/03`. The implementation must
disclose that scope, but must not attempt to repair the wider site-production
architecture as part of this work.

## Decision

Implement Fastest Risers as a deliberately specialised table page within the
existing site shell.

It will use:

```text
ordinary PageDefinition
ordinary ContentPanel shell
kind="table"
renderer="fastest_risers_table"
purpose-built Fastest Risers content-panel orchestration
purpose-built Fastest Risers Options renderer
purpose-built Fastest Risers presentation model and table renderer
```

It will not introduce a new top-level artifact kind alongside `table`, `chart`,
and the other existing kinds. It will also not generalise the shared filter
model merely to support this one page.

The page id is `fastest_risers`. It is published under **Records**, immediately
after **Longest careers**, with the menu label **Fastest risers** and the page
title **Fastest and Slowest Risers**.

## Why the page needs specialised behaviour

Existing generic table pages normally consume flat CSV, expose independent
filters, use a static artifact heading, and apply simple artifact-specific row
filters. Fastest Risers instead needs one coordinated state transition:

1. select a starting division;
2. derive the valid higher destination divisions;
3. repair the destination if it is not valid for the selected start;
4. select the complete fastest or slowest historical ranking;
5. take the first 10, 20, 50, or all records;
6. optionally hide retired rikishi within that already selected range;
7. retain the original historical positions;
8. construct a route- and state-dependent heading and cohort subtitle; and
9. allow the resulting visible rows to be sorted without recalculating their
   historical positions.

No existing generic table renderer expresses that sequence.

## Relationship to existing practice

This approach is specialised, but it does not break a defined site rule.

The site has a coherent structural page model:

```text
PageDefinition
    -> ContentPanel
        -> FilterSection or specialised Options content
        -> artifact panel
        -> notes
```

It does not yet have a coherent declarative model for interactive page
behaviour such as dependent choices, invalid-state repair, data projection,
dynamic headings, or the ordering of limiting and filtering operations. Those
responsibilities are already distributed between shared utilities and
artifact-specific JavaScript.

Existing precedents cover parts of the required behaviour:

- **Finish Chances by Wins** is a `ChartArtifact` whose available Chii values
  depend on the selected division. Its content-panel orchestration resolves a
  valid dependent choice before invoking its specialised chart renderer.
- **Career Comparisons** uses a bespoke Options panel whose selected-rikishi
  controls change dynamically.
- **Rating Changes** uses a specialised table presentation model and renderer,
  including dynamic headings, row projection, grouped columns, sorting, and
  standard page-shell integration.

Fastest Risers is the first non-chart page to combine a dynamic Options panel
with a table result. That is a new combination of existing practices, not a
violation of a rule that table Options must be static.

## Exact Options presentation

The specialised Options renderer will render the agreed controls directly:

| Control | Presentation | Default |
|---|---|---|
| Starting division | Data-derived radio buttons in rank-group order | `Jk` |
| Division of interest | Dropdown populated with valid higher groups | `M` |
| Direction | `Fastest` / `Slowest` radio buttons | `Fastest` |
| Ranking range | Dropdown: `Top 10`, `Top 20`, `Top 50`, `All` | `Top 10` |
| Hide retired rikishi | Checkbox | Unchecked |

The destination remains a dropdown regardless of how many choices are valid.
It must not switch between radio buttons and a dropdown when the starting
division changes.

The `1989/01` proof-of-concept data currently supplies three starting cohorts:
`Jk`, `Sd`, and `Ms`. There is no post-boundary Jd-start cohort. Starting
choices must therefore be derived from produced routes rather than hard-coded
as four buttons. This also permits a future `1958/01` build to expose `Jd`
without changing the renderer.

The page should continue to use declared filter IDs, defaults, and URL keys so
that its state is linkable. The specialised renderer, rather than the shared
cardinality rule, controls the widgets' presentation.

## Data and presentation boundary

The artifact consumes the producer-owned `rankings.json` directly. The
producer remains authoritative for:

- cohort membership;
- route populations and counts;
- elapsed basho;
- fastest and slowest historical positions;
- deterministic ordering of equal elapsed values;
- exact starting and destination chii and dates; and
- active status at the latest represented banzuke.

The browser is responsible only for selecting and presenting those produced
facts. It must not recalculate positions, milestones, elapsed basho, cohort
membership, or active status.

The UI applies operations in this order:

```text
route selection
    -> fastest/slowest ordering
    -> ranking-range selection
    -> optional retired-rikishi hiding
    -> optional user table sort
```

User sorting only reorders the visible rows. The position column continues to
show the producer-supplied position in the selected complete historical
ranking.

The standard published path is
`sumo-history/records/fastest-risers/data/rankings.json`. Upstream production
may also create the milestone matrix and missing-bio audit in its work area,
but only `rankings.json` is copied into and declared by the site-data bundle.

Routes with a non-empty starter cohort remain selectable even when nobody
reached the destination. The presentation model supplies a route-specific
empty-state message while retaining the producer's starter and reached counts.

## What remains standard

The page will reuse the existing site facilities for:

- navigation and routing;
- the page title and summary shell;
- URL-state reading and writing;
- data fetching and cache busting;
- HTML escaping;
- help popovers and Notes;
- rikishi links;
- table styling and low-level sorting utilities;
- panel layout; and
- bundle declaration, validation, assembly, and publication.

Special code should be kept together under a clearly named Fastest Risers UI
module. Shared utilities should be used where they already fit, but must not be
expanded speculatively to make the page appear generic.

## Locked presentation details

The page summary is:

> Rikishi ranked by the number of basho taken to progress between selected
> rank groups.

The table heading follows “Fastest promotions from Makushita to Maegashira,”
substituting direction and group labels from state. The subtitle reports the
selected range, reached population, and starter cohort; when retired rikishi
are hidden it explicitly reports how many active records remain within the
already selected range.

The grouped columns are `#`, `Shikona`, `Start` (`Chii`, `Basho`),
`Destination` (`Chii`, `Basho`), and `Elapsed Basho`. The default sort is
historical position ascending. User sorting is applied last and leaves the
position values unchanged.

The URL keys are `start`, `finish`, `direction`, `range`, and `hide_retired`.
Invalid state is repaired to the declared defaults or the first valid produced
choice, and the canonical state is written back to the URL.

## Advantages of this approach

### It implements the agreed page precisely

The dependent destination, fixed widget types, range-before-filter semantics,
dynamic subtitle, and preserved historical positions can be expressed
directly rather than approximated through generic table behaviour.

### It limits regression risk

The existing filter renderer and generic table pages do not need behavioural
changes. In particular, the automatic radio-versus-dropdown rule remains
unchanged for existing pages.

### It matches the proof-of-concept scope

The artifact itself is intentionally being published with the temporary
post-1988 epoch. A contained implementation is proportionate to a page whose
historical scope and surrounding production architecture may later change.

### It uses concrete existing precedents

The implementation can borrow dependent-choice resolution from Finish Chances
by Wins, bespoke control rendering from Career Comparisons, and table
presentation structure from Rating Changes without claiming that those pieces
already form one general framework.

### It preserves a clear analytical boundary

The producer supplies all substantive rankings and cohort facts. Specialised
browser code selects and presents them but does not become a second analysis
implementation.

## Disadvantages and accepted debt

### It adds another artifact-specific branch

The content-panel dispatcher will need to recognise the Fastest Risers
renderer and invoke purpose-built orchestration. This continues the existing
case-by-case runtime structure rather than simplifying it.

### It duplicates some interaction plumbing

The page will need its own state normalisation, Options rendering, heading
construction, filtering pipeline, empty-state handling, and sorting wiring.
Some of that will resemble code used by existing interactive pages.

### The behaviour is not declarative

The relationship between starting and destination divisions and the ordering
of ranking-range selection and retired-rikishi filtering will live in the
specialised presentation code rather than a reusable page-behaviour model.

### Tests must protect a one-off contract

Generic table tests will not be sufficient. The page needs focused tests for
dependent destinations, URL-state repair, operation ordering, position
preservation, headings, cohort counts, sorting, and empty states.

### A later generalisation may require rework

If another non-chart artifact needs dependent controls and a similarly rich
presentation pipeline, the common abstraction will have to be extracted from
working specialised pages. Some names, state shapes, and module boundaries may
then change.

## Why the debt is acceptable for now

There is only one concrete dynamic table requirement. Designing a general
interactive-page model from that single example would require guessing which
parts are genuinely reusable and could impose unnecessary concepts on existing
pages.

The chosen implementation makes the exception explicit, local, and testable.
It solves the current page without changing established behaviour elsewhere.
That is adequate for the proof of concept, provided the special code is not
misrepresented as a general solution.

## Refactoring trigger

Revisit the design when a second table-like artifact requires dependent
options or a comparable ordered selection/filtering pipeline. At that point,
compare the two implemented presentation models and extract only the behaviour
that is demonstrably shared.

Until then, Fastest Risers remains a standard table page structurally and a
purpose-built interactive page behaviourally.
