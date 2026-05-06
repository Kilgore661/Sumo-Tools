# Site Overview

This note describes the legacy Sumo Elo web site as a product/idea map rather
than as a build or pipeline map. Its purpose is to help a future pass through
the project understand what the site was trying to do, what it delivered, and
which ideas are worth stealing for a new site or app.

The site is a personal sumo ratings and analysis workbench. It is not just a
public-facing explanation of Elo, and it is not just a table dump. It combines:

- current basho/rating tables,
- individual rikishi performance charts,
- model validation and explanation,
- rating-system diagnostics,
- banzuke/population history,
- career lifecycle charts,
- a small research-notebook area for charts that did not fit elsewhere.

The old UI is dense and sometimes clunky, but many of the ideas are good. The
main design challenge for a successor is presentation: the old site exposes a
lot of useful state at once, often in the language of the analysis code.

## Why the Site Exists

The site exists to answer a few related questions:

- How strong is a rikishi, by rating rather than by banzuke rank alone?
- How does rating strength relate to rank/chii?
- How has a rikishi's career moved through rank, rating, and time?
- Which current rikishi are unusually interesting by rating, expected wins, or
  probability-derived measures?
- Is the rating system behaving sensibly over history, or is it drifting?
- What larger patterns exist in sumo careers, divisions, recruitment, and
  retirement?

The author's stance is practical and personal: this is what was calculated,
with the assumptions made explicit enough that readers can accept, reject, or
adapt them. Even if a new project uses Equelo rather than plain Elo, the site
still contains useful explanatory material because Equelo inherits much of its
conceptual ancestry from Elo.

## Main Delivered Surfaces

### Home

The home page is mostly a landing/update page. It is useful for archaeology
because the update notes mention fixes and known issues, but it is not itself a
major analysis surface.

Known useful archaeology from the home notes:

- Click/alt-click shikona interactions were added for performance navigation.
- `piE` was added as a major table/rating idea.
- The `Delta Chii` table column was noted as broken.
- Rikishi indices/ranks may be wrong when sorting on columns other than Chii.

### Latest Tables

The latest tables are one of the site's strongest ideas. They present current
basho/rating state with date navigation and sortable, link-rich rows.

Notable UI ideas:

- Date navigation for browsing historical tables.
- Click and alt-click semantics on shikona links.
- Dense but powerful columns combining banzuke position, Elo, expected wins,
  probability-derived values, score, and deltas.
- Explanatory notes that attempt to define the table columns.

The old table is too geeky as a direct template for a new UI, but much of the
data is worth preserving. Some columns are mandatory; others may belong behind
expansion, tooltips, alternate views, or analyst mode.

Important caution:

- `Delta Chii` should be audited before reuse. The old site itself says it was
  broken.

### Elo Tables / About

The "What is Elo" and "BKQ model" material is explanatory rather than purely
interactive. These pages explain what the project is trying to measure and why
ratings are useful beside the banzuke.

These explanations are worth preserving or rewriting for a successor site:

- plain-English motivation for a rating model,
- Elo formula background,
- limits and assumptions,
- relationship between rating, rank/chii, and prediction,
- BKQ/model-specific reasoning.

The exact model may change, but the need for an explanation does not.

### Performance Charts

The performance chart area provides individual-rikishi exploration. The old UI
is clunky, but the core idea is strong: choose one or more rikishi and view
their careers through rank/chii and rating time series.

The most important unrealised/part-realised goal is a combined Chii and Elo
view, using two y-axes, so rank movement and rating movement can be compared in
one chart.

### Other Stuff

The "Other Stuff" area is a mixed bag, but the individual ideas are mostly
keepers:

- maximum average wins,
- maximum Elo probability,
- miscellaneous population/model/career charts.

These should probably not remain one menu bucket in a new site. They group more
naturally by analytical purpose, as listed below.

## Chart and Table Families

### Individual Rikishi Trajectory

These charts answer: "What happened to this rikishi?"

| Chart/View                       | Old Route or Artifact                   | Notes                                                    |
| -------------------------------- | --------------------------------------- | -------------------------------------------------------- |
| Rank/Chii over calendar time     | `graph_type=by_time`                    | Main career-shape chart.                                 |
| Rank/Chii by basho count         | `graph_type=by_basho`                   | Normalizes a career to basho number rather than date.    |
| Elo over calendar time           | `graph_type=elo_by_time`                | Rating history for selected rikishi.                     |
| Elo vs Chii for selected rikishi | `graph_type=elo_vis`                    | Also functions as rating/rank validation.                |
| Daily Elo movement               | `elo delta_skel.txt` / `daily_elo(...)` | Click-through daily/bout rating movement from the table. |
| Combined Chii + Elo              | desired successor chart                 | A key idea to carry forward, likely with dual y-axes.    |

Primary data lineage:

- `banzukes.pkl`
- per-basho `YYYY MM elo ratings035.pkl`
- `YYYY results.pkl`
- `full_shiks.pkl`

### Current Tables and Leaderboards

These views answer: "Who is interesting right now?"

| View                | Old Route or Artifact                    | Notes                                                     |
| ------------------- | ---------------------------------------- | --------------------------------------------------------- |
| Latest Elo table    | `make_table.elo_table(...)`              | Core current-state table.                                 |
| Date navigation     | table route parameters                   | Strong UI idea; presentation needs rethinking.            |
| Max average wins    | likely `max_mu2.html`                    | Keeper, even if a new app expands ranking-by-wins.        |
| Max Elo probability | likely `max_elo.html` / `max_elo_b.html` | Keeper for now; may later merge into richer rating views. |

Main table data lineage:

- `dates.pkl`
- `YYYY banz.pkl`
- `run_av.pkl`
- `YYYY MM elo ratings035.pkl`
- `YYYY results.pkl`
- `YYYY MM rik_info.pkl`
- `YYYY elo_prop 1957 normed.pkl`
- `max_chii.pkl`

Notable table concepts:

- rank/chii,
- Elo,
- `muE`,
- `piE`,
- current score,
- latest Elo,
- new/projected Chii,
- Delta Chii,
- Delta Elo,
- Delta Banzuke,
- rank-relative values such as `vChii`.

### Rating vs Rank Calibration

These charts answer: "Does the rating system make sense against the banzuke?"

| Chart/View             | Old Route or Artifact  | Notes                                                    |
| ---------------------- | ---------------------- | -------------------------------------------------------- |
| Elo vs Chii            | `graph_type=elo_vis`   | A validation chart for doubters and for model intuition. |
| Intro Elo table/chart  | `intro_Elo_table.html` | Explanatory/calibration material.                        |
| Mean Elo by Chii       | `E_2-poly_*.html`      | One chart per division/rank band.                        |
| Mean muE by Chii       | `muE_2-poly_*.html`    | Expected-win/rank calibration family.                    |
| Mean piE by Chii       | `piE_2-poly_*.html`    | Probability/rank calibration family.                     |
| Normalized piE by Chii | `piEn_2-poly_*.html`   | Normalized probability/rank variant.                     |

The generated filenames use Greek-letter variants in places. This note uses
ASCII names for readability.

### Model Diagnostics

These charts answer: "Is the model behaving properly over time?"

| Chart/View                      | Old Route or Artifact                            | Notes                                                    |
| ------------------------------- | ------------------------------------------------ | -------------------------------------------------------- |
| Inflation by rank/chii          | `spreads/E_graph_rolling_by_chii 1957-2025.html` | Important diagnostic; also appears in Misc Charts.       |
| Other inflation/spread variants | `spreads/E_hack_graph_by_chii *.html`            | Experimental but relevant.                               |
| Elo distribution                | `frequency_distribution_plot*.html`              | Shape of rating population.                              |
| Estimators                      | `estimators.html`                                | Method/model diagnostic chart.                           |
| Mean Elo rating vs banzuke size | `elo vs banz2.html`                              | Misc Chart; connects model behaviour to population size. |

### Population and Banzuke Structure

These charts answer: "What does the sumo population look like over time?"

| Chart/View                                | Old Route or Artifact   | Notes                                                                          |
| ----------------------------------------- | ----------------------- | ------------------------------------------------------------------------------ |
| Changes to sizes of divisions             | `rids_by_div_exp2.html` | Misc Chart; strong keeper.                                                     |
| Division sizes over time, simpler variant | `rids_by_div.html`      | Related/older simpler version.                                                 |
| Mean Elo rating vs banzuke size           | `elo vs banz2.html`     | Cross-listed with diagnostics because it is both population and model-related. |

### Career Lifecycle

These charts answer: "How long do rikishi careers last, and where do they end?"

| Chart/View                           | Old Route or Artifact            | Notes                                         |
| ------------------------------------ | -------------------------------- | --------------------------------------------- |
| Career length count                  | `career.html`                    | Misc Chart.                                   |
| Career length probability            | `prob career.html`               | Misc Chart.                                   |
| Cumulative career length probability | `cum prob career.html`           | Misc Chart.                                   |
| Rank at retirement                   | `retirement_histogram_plot.html` | Misc Chart; affected by `Bg`/intai ambiguity. |

### Research Notebook / Miscellaneous

The old "Miscellaneous Charts" page is not actually random. It mostly contains:

- population/banzuke structure,
- career lifecycle,
- model diagnostics.

Charts currently itemised there:

- Mean Elo Rating v. Banzuke Size,
- Changes to Sizes of Divisions,
- Career Length,
- Career Length Probability,
- Cumulative Career Length Probability,
- Inflation,
- Rank at Retirement.

For a successor site, this material should probably be promoted into clearer
sections rather than kept as one miscellaneous drawer. A smaller "lab" or
"archive" area may still be useful for experimental charts that are worth
preserving but not ready for the main UI.

## Things to Carry Forward

High-value ideas:

- individual rikishi career charts,
- combined rank/chii and rating chart,
- Elo/rating vs Chii validation,
- date navigation on current tables,
- click/alt-click shikona navigation semantics,
- explanatory table notes,
- max average wins,
- max rating/probability leaders,
- career length and retirement charts,
- division-size history,
- rating inflation diagnostics.

Needs redesign or audit before reuse:

- dense table presentation,
- `Delta Chii`,
- rank/index behaviour after sorting,
- distinction between public user view and analyst/research view,
- clearer grouping of chart families.

## Successor Site Shape

A cleaner successor could organise the material around user questions:

1. Current: tables, date navigation, leaders, current basho state.
2. Rikishi: individual career/rating/rank trajectories.
3. Rankings: wins, rating probabilities, peak/maximum views.
4. Model: rating-vs-rank validation, inflation, distributions, estimators.
5. Sumo History: division sizes, career length, retirement rank.
6. About: explanation of Elo/Equelo, assumptions, formulae, and caveats.

This preserves the old site's useful ideas while separating polished product
surfaces from research diagnostics.
