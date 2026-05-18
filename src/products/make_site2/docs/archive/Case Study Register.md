# make_site2 Case Study Register

This register tracks the current public-site page shapes that `make_site2`
must prove before it can replace the old shell model.

The purpose is classification, not full specification. Each row should answer:

- what nav item are we migrating?
- is it G1 or G2?
- what PAs does it contain?
- where do filters belong?
- what makes the migration risky?

## Current Working Partition

| Nav item             | Page id                 | Grammar | PA shape                                   | Filter scope                                                                     | Artifact rendering                                | Notes                                                                  | Migration risk                                                       |
| -------------------- | ----------------------- | -------:| ------------------------------------------ | -------------------------------------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 7.1 Basho Results    | `basho_results_browser` | G1      | One table PA: Basho Results table          | Contents-level filters: basho/date, division, previous context, ratings, nu chii | Indexed table from BRB index and selected payload | Table notes only, shown when relevant table columns/groups are visible | First reference slice; must remove iframe and avoid copied page HTML |
| Division Stability   | `division_stability`    | G1      | One chart PA: Division Stability chart     | No filters in first slice                                                        | Grouped line chart over `persistence.csv`         | None for initial model                                                 | First chart slice; must prove charts do not reintroduce shell behavior |
| Standings by Wins    | `standings_by_wins`     | G1      | One table PA: Standings by Wins table      | Contents-level filters: view, number of basho, active/current, division          | Table over selected standings CSV                 | Table notes only                                                       | First non-indexed table slice; replaces old `TableAppView` path      |
| Career Length        | `career_length`         | G2b     | Branch-selected contents: Chart branch or Table branch | Branch-local filters: chart type for Chart; active/all for Table                 | One selected branch PA: chart or Longest table       | Table notes only when Table branch is selected                       | Replaces original G2; branch-selected, not simultaneous PAs          |
| Finish by Chii       | `finish_by_chii`        | G1      | Multiple chart PAs sharing a content panel | Contents-level shared filters                                                    | Chart group over table-shaped data                | None unless a table PA is later introduced                             | Currently standalone HTML; must avoid permanent legacy exclusion     |

## Grammar Notes

G1 is the normal case:

```text
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA+ . Note*
PA -> Title . Artifact
```

G2 is for PA-specific filters:

```text
ContentPanel -> Heading . Contents
Contents -> PA+ . Note*
PA -> Title . Artifact . FilterSection
```

## Immediate Next Case Study

Start with BRB:

```text
ContentPanel
  Heading: Basho Results
  Contents
    FilterSection
      basho/date
      division
      previous context
      ratings
      nu chii
    PA
      Basho Results table
    Note*
      table-specific notes, filtered by visible table features
```

Acceptance target:

```text
Open generated index.html.
Click 7.1 Basho Results.
Render BRB inside the ContentPanel.
No iframe.
No copied standalone HTML.
Filters, not options, at the make_site2 model boundary.
```
