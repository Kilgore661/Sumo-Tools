# Old Nav Tree

## Status

Historical snapshot.

This document preserves the `make_site2` navigation tree as it existed before the generated-output dependency audit reduced the site-builder graph to clickable entries.

For this audit:

```text
Clickable entry = current website output root.
Non-clickable entry = historical planning residue, not a current website output.
```

Clickable entries are marked with **[CLICKABLE]** and include their `page_id`.

## Snapshot

- Root
  - Home
    - What this site is
    - Featured / latest exhibits
    - Notes and caveats
  - Current Sumo
    - **[CLICKABLE] Banzuke Changes** (`page_id=banzuke_changes`)
    - **[CLICKABLE] Standings by Wins** (`page_id=standings_by_wins`)
    - Current Ratings
    - Current Leaders
      - Max average wins
      - Max rating probability
      - Rating movers
      - Banzuke movers
  - Rikishi
    - Rikishi Lookup
    - Rikishi Profile
      - Summary
      - Career rank/chii timeline
      - Rating timeline
      - Combined chii + rating view
      - Daily / bout-level rating movement
    - Career Comparisons
  - Banzuke & Rank
    - Chii Notes
    - Current Banzuke
    - Banzuke Structure Over Time
      - **[CLICKABLE] Banzuke Division by Era** (`page_id=banzuke_division_by_era`)
      - **[CLICKABLE] Makuuchi Rank by Era** (`page_id=makuuchi_rank_by_era`)
    - **[CLICKABLE] Division Stability** (`page_id=division_stability`)
    - Rank History
      - **[CLICKABLE] First chii appearance** (`page_id=first_chii_appearance`)
      - Rare / historical rank slots
    - Retirement Rank
  - Performance
    - **[CLICKABLE] Finish by Chii** (`page_id=finish_by_chii`)
    - Win Probability by Standing
    - Career Outcomes
      - Career length
      - Career length probability
      - Cumulative career length probability
    - Rank Outcomes
      - Average finish by chii
      - Threshold / top-record views
  - Ratings & Models
    - Rating Overview
      - Why ratings?
      - Elo / Equelo explanation
      - Assumptions and caveats
    - Rating and Rank
      - **[CLICKABLE] Typical Equelo Ratings** (`page_id=typical_equelo_values`)
      - Rating vs chii
      - Mean rating by chii
      - Expected wins by chii
      - Probability-derived values by chii
    - Observed vs Modelled
      - **[CLICKABLE] Win Probability by Standing** (`page_id=win_probability_by_standing`)
      - Model consistency checks
      - Residual / difference views, later
    - Model Diagnostics
      - Rating distribution
      - Inflation / drift by chii
      - Estimators
      - Mean rating vs banzuke size
      - Calibration reports
    - Equelo Methodology
      - V5 Landmark Policy
      - Lower-Rank Rating Stability
      - Initial rating curve / fixed-v1 entrant ratings
      - Monotonicity story
      - Experiment / research narrative
  - Sumo History
    - **[CLICKABLE] Basho Results** (`page_id=basho_results_browser`)
    - Population History
      - Division sizes over time
      - Banzuke population
    - Career Lifecycle
      - **[CLICKABLE] Career length** (`page_id=career_length`)
      - **[CLICKABLE] Rank at retirement** (`page_id=rank_at_retirement`)
    - Historical Exhibits
      - Banzuke division by era
      - Makuuchi rank by era
  - Data & Notes
    - Data Sources
    - Glossary
    - Chii / banzuke quirks
    - Known Limitations
    - Method Notes
  - Lab / Archive
    - Research charts not yet promoted
    - Legacy v9 exhibits pending reimplementation
    - Deprecated / superseded outputs

## Clickable Output Roots

The active `make_site2` website-output roots implied by this snapshot are:

```text
banzuke_changes
standings_by_wins
banzuke_division_by_era
makuuchi_rank_by_era
division_stability
first_chii_appearance
finish_by_chii
typical_equelo_values
win_probability_by_standing
basho_results_browser
career_length
rank_at_retirement
```

For the makefile/dependency-graph exercise, these are the current site-builder outputs. Physical files written by the builder are implementation artifacts only if they support one of these clickable outputs.
