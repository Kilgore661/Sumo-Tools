# Project Map

## Purpose

This document maps the project from the point of view of a public-facing sumo
site.

The repository began as a set of exploratory investigations. Some outputs are
already useful to a fan. Some are internal machinery. Some are research records
that may never become public products. The purpose of this map is to make those
distinctions visible.

The main organising axis is subject matter, not user type. Users will
self-select by choosing pages and options. Individual pages may still expose
basic, advanced, or research views where that helps.

The working product idea is:

> A curated Sumo Lab that makes professional sumo more legible through data.

The site should not publish everything the repository can generate. It should
publish the things that answer a clear question for a clear audience with an
honest interpretation.

## Depth

Depth is a property of a page or view, not a main navigation category.

| Depth | Meaning |
| --- | --- |
| Basic | A fan can understand the result with ordinary sumo knowledge. |
| Advanced | The page assumes comfort with history, rank movement, career context, or comparative tables. |
| Research | The page exposes modelling assumptions, calibration, methodology, or unresolved interpretive questions. |

## Status

| Status | Meaning |
| --- | --- |
| Live candidate | Existing output or page is close to public-facing. |
| Prototype | Existing output works but needs framing, UI polish, or integration. |
| Research | Existing work is valuable but should be presented as experimental or methodological. |
| Internal | Useful to the project but not suitable as a public page. |
| Suggested | Not found as a current deliverable; included as a plausible future page or view. |

## Public Readiness

| Readiness | Meaning |
| --- | --- |
| High | Can plausibly be linked from the public site after light integration. |
| Medium | Useful, but needs stronger framing, UI, or explanation. |
| Low | Needs substantial design, validation, or method work before publication. |
| None | Should remain internal unless its purpose changes. |

## Project Map

| Subject | Page / Output / Idea | Primary Question | Depth | Status | Public Readiness | Source / Evidence | Likely UI Shape | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Current Sumo | Current rolling standings | Who has performed best over a recent rolling period? | Basic, Advanced | Live candidate | High | `src/analysis/standings`, `files/output/standings` | Tool page with options sidebar and sortable table | Strong first public tool. Existing requirements emphasise usefulness, trustworthiness, and progressive disclosure. |
| Current Sumo | Current basho results | What happened today or in this basho? | Basic | Suggested | Medium | Raw scraper archive in `files/output/HTML results`; parsed history in infra | Results page, basho/day selector | The data exists, but a polished public results browser is not yet the current focus. |
| Current Sumo | Current banzuke browser | Who is at each rank now? | Basic | Suggested | Medium | Parser/live-store history; banzuke compare assets | Banzuke-shaped table with division filters | This is a natural companion to standings. It should be official-record-like rather than analytical. |
| Current Sumo | Rikishi lookup | Where is this rikishi now? | Basic | Suggested | Low | `bios.json`, history, standings identity work | Search page leading to rikishi profile | A likely public need, but it needs identity, shikona history, and profile design. |
| Banzuke | Banzuke Change Report | What changed on the new banzuke? | Basic, Advanced | Live candidate | High | `src/analysis/banzuke_compare` | Report page with headline and filtered detail views | Strong first public page. It already fits the "neutral facts before news labels" direction. |
| Banzuke | Banzuke news headlines | What are the notable stories in this banzuke? | Basic, Advanced | Prototype | Medium | `src/analysis/banzuke_compare/docs/Scoping Study.md` | Headline list plus drill-down sections | Needs careful separation between mechanical facts and editorial interpretation. |
| Banzuke | Banzuke structure over time | How has the size and shape of the banzuke changed? | Basic, Advanced | Prototype | Medium | `src/misc/banzuke_by_era.py`, `banzuke_division_era_chart.*` | Chart exhibit with era controls | Public-friendly if framed as descriptive history rather than analysis for its own sake. |
| Banzuke | Makuuchi rank structure over time | How has Makuuchi rank population changed by era? | Basic, Advanced | Prototype | Medium | `src/misc/makuuchi_by_era.py`, `rank_era_chart.*` | Chart exhibit | Similar to banzuke division by era. Could be grouped under "Banzuke Structure". |
| Banzuke | Division churn | How much movement is there between divisions? | Advanced | Prototype | Medium | `src/misc/division_churn.py`, `division_churn.html` | Chart exhibit with division/range options | Potentially useful, but needs a plain-language question and interpretation. |
| Banzuke | Y1e history | Who has held the top east yokozuna slot over time? | Basic, Advanced | Suggested | Medium | Available from parsed history | Timeline/table exhibit | Good example of a historical fact page that begins basic and can gain advanced context. |
| Banzuke | Chii explainer | What does a rank such as `M3e` actually mean? | Advanced, Research | Suggested | Low | Chii model in `src/sumo_core`; banzuke docs and Equelo questions | Essay/exhibit with diagrams and examples | This is central to the deeper project. It needs care because "meaning" spans ordering, prestige, matchmaking, and empirical strength. |
| Rikishi | First chii appearance | When did each rank slot first appear in the data? | Advanced | Prototype | Medium | `src/misc/first_appearance.py`, `first_app.*` | Chart/table exhibit | Interesting as reference information. Needs framing so it is not just a generated table. |
| Rikishi | Career timeline | What is this rikishi's rank path? | Basic, Advanced | Suggested | Medium | History model, standings outputs | Rikishi profile panel with rank-over-time chart | Natural public page. It would make many existing questions easier to answer. |
| Rikishi | Career high | What was this rikishi's highest rank, and when? | Basic | Suggested | Medium | History model | Rikishi profile fact card; table view | Straightforward and likely useful. Could be a first slice of rikishi pages. |
| Rikishi | Newcomer context | Is this makuuchi newcomer a fast-rising prospect or a journeyman? | Advanced | Suggested | Low | History model, possible bios | Banzuke news annotation or rikishi profile section | Valuable public insight, but needs definitions such as rise speed, career length, division transitions. |
| Rikishi | Rank trend / form | Is this rikishi moving up, down, or sideways? | Basic, Advanced | Suggested | Low | Standings, history, current banzuke | Profile chart and recent-window summary | Should avoid implying prediction unless a method is explicit. |
| Performance | Finish by Chii | How do rikishi at a given chii tend to finish? | Advanced | Prototype | Medium | `src/misc/finish_by_chii.py`; local web output target | Chart exhibit | Useful bridge between descriptive facts and expectations. Needs on-page explanation of sample and interpretation. |
| Performance | Average finish by Chii | What is the average outcome from each rank slot? | Advanced | Prototype | Medium | `src/misc/finish_by_chii.py`, `finish_by_chii_charting.py` | Chart exhibit | Could pair with Finish by Chii under "Rank Outcomes". |
| Performance | Observed matchup probabilities | What actually happens when ranks meet? | Advanced, Research | Prototype | Medium | `src/analysis/probability/matchups` | Chart exhibit with rank-pair controls | Stronger public candidate than modelled probabilities because it is descriptive. |
| Performance | Expected outcomes by observed data | What record should we expect from this rank context? | Advanced, Research | Research | Medium | Recent probability charts and matchup work | Research-labelled interactive chart | Should be labelled carefully as empirical expectation, with sample-size visibility. |
| Ratings & Models | Equelo ratings | Who is currently best according to an Elo-like model? | Advanced, Research | Research | Low | `src/analysis/equelo`, `files/output/Equelo` | Research page with rating table, method notes, caveats | Tempting as Type I, but not yet trustworthy enough as a simple fan-facing ranking. Possible Type II/III page. |
| Ratings & Models | Equelo fixed-v1 charts | What does the current fixed model imply about initial rank strength? | Research | Research | Low | `src/analysis/equelo/fixed_v1` | Lab chart page | Useful research record. Not a main public fact unless narrowed to a clear claim. |
| Ratings & Models | Observed vs modelled matchup traces | How does the model compare with observed outcomes? | Research | Research | Medium | `src/analysis/probability/matchups/trace_main.py` | Lab chart with paired views | Good Type III page. It should live under research, not the basic public surface. |
| Ratings & Models | Calibration reports | Are model probabilities calibrated? | Research | Research | Low | `src/analysis/probability`, Equelo run outputs | Technical report page | Important for methodology. Probably not a front-door page. |
| Ratings & Models | Model methodology | What assumptions does Equelo make, and what did the experiments teach? | Research | Suggested | Medium | `src/analysis/docs`, Equelo code and outputs | Essay plus selected charts | This may be more publishable than raw Equelo outputs because it explains the can of worms directly. |
| Data & Methods | Data source and update policy | Where does the data come from, and when is it considered current? | Basic, Advanced | Suggested | Medium | `docs/2023 03 23 Engineering Overview.md`, scraper/parser code | Reference page | Important for public trust. Should explain correctness over completeness. |
| Data & Methods | Known limitations | What should users not infer from these pages? | Basic, Advanced, Research | Suggested | High | Many docs; especially standings and Equelo notes | Reference page linked from all analytical pages | Crucial if ratings, observed expectations, and banzuke interpretation become public. |
| Data & Methods | Parser and validation notes | How is historical data parsed and checked? | Research | Internal | None | `src/infra`, parser docs | Internal or technical appendix | Useful for maintainers and highly technical readers, but not central public navigation. |
| Data & Methods | Persistence reports | How persistent are division/rank positions? | Advanced, Research | Prototype | Low | `src/analysis/persistence` | Chart exhibit or research appendix | Currently not a first-pick public page. Could graduate if the question becomes clear. |
| Internal | Scraped HTML archive | What raw source pages were downloaded? | Internal | Internal | None | `files/output/HTML results`, `files/output/current standings` | None | Essential source material, not a public product. |
| Internal | History zip outputs | What canonical parsed histories exist? | Internal | Internal | None | `files/output/Historys`, `files/output/fsm` | None | Persistence artifact. Public pages should consume it, not expose it. |
| Internal | Warning logs and weirdness reports | What data issues were found? | Internal, Research | Internal | None | parser warning outputs | Maintainer diagnostics | Useful for data integrity but not public unless converted into a quality note. |

## Suggested Navigation Shape

The main navigation should be subject-led:

```text
Current Sumo
Banzuke
Rikishi
Performance
Ratings & Models
Data & Methods
```

This differs from the earlier two-part "Tools / Sumo Facts" division, but it
does not reject it. Instead, each subject can contain both tools and facts.

For example:

```text
Banzuke
  Current Banzuke
  Banzuke Changes
  Structure Over Time
  Chii Explained
```

and:

```text
Ratings & Models
  Equelo Overview
  Expected Outcomes
  Observed vs Modelled
  Calibration
  Methodology
```

## Page Shape

The existing presentation-layer direction still fits:

```text
site title bar
site navigation | page title bar
                | page options | page content
```

The key refinement is that the site navigation should probably be organised by
subject. The page options area can then expose depth:

```text
Basic
Advanced
Research
```

where appropriate.

Not every page needs all depths. A current standings page may have a simple
default table and advanced filters. A model calibration page may begin at
research depth and never pretend to be basic.

## Public Surface Principles

1. Publish questions, not artifacts.

   An output belongs on the site when it answers a question that can be stated
   plainly.

2. Distinguish facts from interpretations.

   Observed historical distributions can be public facts. Modelled probabilities
   are interpretations and should be labelled as such.

3. Keep ratings out of the basic surface until they earn it.

   Equelo may become a useful lens for knowledgeable fans, but it should not be
   presented as "who is best" without strong explanation and confidence.

4. Let users move deeper.

   A basic fan should not have to understand the modelling work. A research
   reader should be able to find the assumptions, diagnostics, and failures.

5. Do not expose raw project history as site structure.

   The public site should be curated by subject and question, not by the order
   in which investigations happened.

## Suggested Additions Not Currently Found As Deliverables

The following ideas are suggestions, not an inventory of current outputs.

| Subject | Suggested Page | Why It Fits |
| --- | --- | --- |
| Current Sumo | Basho day view | Basic fans often want "what happened today?" before any deeper analysis. |
| Rikishi | Rikishi profile | Many subject questions become easier if every rikishi has a canonical page. |
| Rikishi | Comparable careers | Helps explain whether a rise is unusual without jumping straight to ratings. |
| Banzuke | Promotion and demotion explainer | Bridges basic banzuke facts and knowledgeable-fan questions. |
| Banzuke | Rank movement glossary | Explains why "up by N ranks" is not always simple. |
| Performance | Rank outcome explorer | Lets users ask "what usually happens from here?" using observed data. |
| Ratings & Models | Model comparison page | Compares simple baselines, Equelo variants, and observed expectations. |
| Data & Methods | Glossary | Defines basho, banzuke, chii, rikishi identity, shikona, division, record, and related terms. |

## Near-Term Product Candidates

The strongest near-term public site candidates are:

1. Current rolling standings.
2. Banzuke Change Report.
3. Banzuke structure over time.
4. Makuuchi rank structure over time.
5. First chii appearance.
6. Finish by Chii / Average Finish by Chii.
7. Observed chii matchup probability distribution.

The first two are tools. The others are exhibits. Together they are enough to
justify a site shell with real navigation and honest placeholders.

Equelo and modelled probabilities should be kept in a clearly labelled research
area until a narrow public claim emerges.

## Open Decisions

1. Should the top-level site name be "Gaspode-san's Sumo Lab", "Sumo Lab", or
   something else?
2. Should "Performance" and "Ratings & Models" be separate top-level subjects,
   or should ratings live under Performance until the research area is larger?
3. Should the first public shell include placeholder pages, or only pages with
   existing data?
4. Should the public site support stable URLs for each tool/fact from the
   beginning?
5. What minimum explanation is required before any Equelo rating appears on a
   public page?

