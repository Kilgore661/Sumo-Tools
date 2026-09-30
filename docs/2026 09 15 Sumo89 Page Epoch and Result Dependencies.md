# Sumo '89 Lab: page epochs and bout-result dependencies

## Scope and evidence

Audit date: 15 September 2026.

This analysis inventories the distinct `page=` destinations exposed by the live
[Sumo '89 Lab](http://192.168.0.146/sumo-tools89/index.html), and traces their data
dependencies through the checked-in producers. It concerns data coverage and
calculation semantics, not a visual or interaction test of every page.

The live navigation and [runtime manifest](http://192.168.0.146/sumo-tools89/runtime/site-manifest.json)
exposed **23 distinct page values**. The
[published bundle manifest](http://192.168.0.146/sumo-tools89/runtime/site-data-bundle.json)
identified the source as `files\output\Historys\1989_01 to 2026_11.zip`, but its
actual represented coverage was **1989/01 through 2026/07**. Archive filenames
must not be used as evidence of the represented endpoint.

**Currently, none of these views uses pre-1989 bout results.** The classification
below asks: **would extending the view back to 1958 require pre-1989 bout results?**

## Current production boundary

The site builder lives under `src/products/make_site89`, and consumes an
already-produced site-data bundle. The production chain currently applies the
1989 boundary beyond ratings:

1. `src/analysis/site89/producer.py` requires a History beginning at `1989/01`.
2. It passes the same History to the Elo89 producer and model-independent analyses.
3. `src/products/make_site89/bundle.py` independently requires the bundle History
   to begin at `1989/01`.

Thus, "model-independent" does not mean either "uses the 1958 epoch" or
"independent of bout-result completeness".

The older `make_site2` references 1958-based career datasets and banzuke-era
charts. That is consistent with the recollection of a broader historical scope,
but it is not the current `make_site89` production contract.

## Data pages

| `page=` link | Needs pre-1989 bout results for historical extension? | Reason |
|---|---|---|
| [banzuke_division_by_era](http://192.168.0.146/sumo-tools89/index.html?page=banzuke_division_by_era) | **No** | Counts banzuke entries by division and era. |
| [makuuchi_rank_by_era](http://192.168.0.146/sumo-tools89/index.html?page=makuuchi_rank_by_era) | **No** | Counts banzuke appearances at each Makuuchi rank. |
| [division_stability](http://192.168.0.146/sumo-tools89/index.html?page=division_stability) | **No** | Tracks division membership across banzukes. |
| [career_length](http://192.168.0.146/sumo-tools89/index.html?page=career_length) | **No** | Elapsed time between first and last observed banzuke appearances. |
| [longest_careers](http://192.168.0.146/sumo-tools89/index.html?page=longest_careers) | **No** | Ranks the banzuke-derived career lengths. |
| [rank_at_retirement](http://192.168.0.146/sumo-tools89/index.html?page=rank_at_retirement) | **No** | Uses final observed banzuke rank; excludes those present at the latest basho. |
| [first_chii_appearance](http://192.168.0.146/sumo-tools89/index.html?page=first_chii_appearance) | **Yes, as implemented** | Finds the first recorded bout involving each chii. A banzuke-first-appearance version would not need results. |
| [most_career_wins](http://192.168.0.146/sumo-tools89/index.html?page=most_career_wins) | **Yes** | Counts recorded wins. Missing earlier results understate career totals. |
| [most_consecutive_bouts](http://192.168.0.146/sumo-tools89/index.html?page=most_consecutive_bouts) | **Yes** | Needs daily appearance evidence to establish and count streaks. |
| [finish_by_chii](http://192.168.0.146/sumo-tools89/index.html?page=finish_by_chii) | **Yes** | Ranks finishes by recorded wins, then aggregates by chii. Missing results affect rankings and probabilities. |
| [win_probability_by_standing](http://192.168.0.146/sumo-tools89/index.html?page=win_probability_by_standing) | **Yes for historical observations** | Empirical probabilities count bout outcomes between ranks. The comparison curve uses Elo89's rank priors. |
| [standings_by_wins](http://192.168.0.146/sumo-tools89/index.html?page=standings_by_wins) | **Only for earlier windows** | Requires results within the selected window. Currently published recent windows need no pre-1989 results. |
| [basho_results_browser](http://192.168.0.146/sumo-tools89/index.html?page=basho_results_browser) | **Mixed** | Historical scores need results; ranks and rank changes need only banzukes. Elo89 ratings would remain unavailable before 1989. |
| [career_comparisons](http://192.168.0.146/sumo-tools89/index.html?page=career_comparisons) | **Mixed** | The chii trajectory can extend to 1958 using banzukes. The rating trajectory remains 1989 onwards under Elo89. |
| [banzuke_changes](http://192.168.0.146/sumo-tools89/index.html?page=banzuke_changes) | **No for this current view** | Shows the latest banzuke. Rank movements use banzukes; result context and optional ratings use recent/post-1988 evidence. |
| [highest_rating](http://192.168.0.146/sumo-tools89/index.html?page=highest_rating) | **Outside Elo89's scope** | Uses maximum Elo89 ratings. Extending ratings before 1989 would require a historical rating model and earlier result evidence. |
| [rating_changes](http://192.168.0.146/sumo-tools89/index.html?page=rating_changes) | **No for current Elo89 windows** | Compares recent Elo89 ratings. Earlier rating windows would require an extended model. |

## Explanatory pages

These are static prose, rather than views calculated from historical bout records.

| `page=` link | Pre-1989 bout-result dependency |
|---|---|
| [what_this_site_is](http://192.168.0.146/sumo-tools89/index.html?page=what_this_site_is) | **Not applicable** — site introduction |
| [why_ratings](http://192.168.0.146/sumo-tools89/index.html?page=why_ratings) | **Not applicable** — motivation |
| [elo_explanation](http://192.168.0.146/sumo-tools89/index.html?page=elo_explanation) | **Not applicable** — Elo explanation |
| [elo89_explanation](http://192.168.0.146/sumo-tools89/index.html?page=elo89_explanation) | **Not applicable** — Elo89 explanation |
| [elo89_assumptions](http://192.168.0.146/sumo-tools89/index.html?page=elo89_assumptions) | **Not applicable** — modelling assumptions |
| [elo89_vs_chii](http://192.168.0.146/sumo-tools89/index.html?page=elo89_vs_chii) | **Not applicable** — explanatory comparison |

Two additional definitions exist in source but were absent from the live page
manifest: `most_career_losses` (result-dependent, like wins) and
`typical_rating_values` (Elo89 prior values). Produced data or a source page
definition alone does not establish a live page destination.

The GOATs shortcut reuses `career_comparisons` with rating and wrestler filters;
it is not another `page=` value.

## Important interpretation details

### First Chii Appearance

`src/misc/first_appearance.py:first_app` traverses recorded bouts, then obtains
each participant's chii from the banzuke. Its meaning is therefore:

> First recorded bout involving someone at each exact chii, within the supplied History.

It does not compute the first occurrence of a chii on a banzuke.

The live [appearances CSV](http://192.168.0.146/sumo-tools89/banzuke-rank/rank-history/first-chii-appearance/data/appearances.csv)
gave Y1e and Y1w first appearances as January 1989. The chart encodes dates as
months since January 1958, so these dates have value 372. **The 1958 encoding
origin is not evidence of 1958 data coverage.**

### Six-basho wins and other rolling windows

`src/analysis/standings/multiple_basho.py` counts wins from recorded individual
bouts. Missing results mean missing wins. Its window resolver truncates a
requested window at the boundary of the available History rather than rejecting
a shorter window.

The site89 standings producer publishes windows ending at the latest basho,
including a six-basho window. It does not search all historical six-basho windows
for an all-time record. Changing the epoch to 1958 would not change underlying
win totals for an unchanged recent window.

A historical record search would need to distinguish:

- a full six-basho window from a truncated window; and
- complete result evidence from incomplete result evidence within that window.

### Career boundaries

Banzuke-only calculations can use the 1958 history without earlier bout results,
but a wrestler already present at the first available basho may have an earlier
career outside the dataset. First observed appearance is not necessarily debut.
Similarly, absence from a banzuke does not by itself establish permanent retirement.

The current career-length analysis already records partial starts and gaps.
Those issues also matter to any fastest-rises producer.

### Result completeness is not a single universal date

The repository's [pre-1989 completeness audit](../src/analysis/docs/story/17%20Pre-1989%20Bout-Data%20Completeness%20and%20Rating%20Persistence.md)
reports complete daily source records for Makuuchi and Juryo throughout its
audited 1958-onwards interval, and varying lower-division coverage, including
exceptions after 1989.

That audit concerns source daily records; it does not certify every corresponding
bout in a produced History. January 1989 is the selected Elo89 boundary, not a
universal switch from incomplete to complete evidence.

## Implications for future data contracts

Six existing pages can use the 1958 banzuke history without requiring earlier
bout results. The chii component of Rikishi History and the proposed fastest-rises
analysis can do so as well. This would require changing the current single-epoch
site89 production/bundle contract, not merely changing chart labels.

Keep four concepts separate:

| Concept | Meaning |
|---|---|
| History coverage | Available banzukes and results |
| Rating coverage | Dates for which Elo89 is calculated |
| Artifact coverage | Dates and population included in a particular view |
| Completeness policy | Evidence required for inclusion in that calculation |

This allows 1958-based banzuke analysis alongside 1989-based ratings without
implying that every view has identical evidence or coverage.

## Code references

- [Site89 producer](../src/analysis/site89/producer.py)
- [Model-independent producers](../src/analysis/site89/model_independent.py)
- [Bundle validation](../src/products/make_site89/bundle.py)
- [Page definitions](../src/products/make_site89/site_definition.py)
- [Navigation](../src/products/make_site89/navigation.py)
- [First-appearance calculation](../src/misc/first_appearance.py)
- [Career-length calculation](../src/analysis/sumo_history/career_lifecycle/career_length.py)
- [Standings calculation](../src/analysis/standings/multiple_basho.py)
- [Site89 standings publication](../src/analysis/site89/standings.py)
- [Career-comparisons producer](../src/analysis/site89/career_comparisons.py)
- [Win-probability producer](../src/analysis/site89/win_probability.py)

This document records an audit and conceptual recommendations. No producer,
site code, or published data was changed as part of the analysis.
