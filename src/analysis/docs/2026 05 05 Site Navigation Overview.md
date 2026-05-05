# Site Navigation Overview

This note sketches the broad site navigation implied by the current project and
the legacy prototype site. It is intentionally inclusive: it records where each
idea would live if the current project delivered its current features plus the
useful ideas from the old prototype.

This is not a build plan and not a priority list. It is a structured contents
map for stress-testing the site information architecture.

## Top-level navigation

```text
Home
Current Sumo
Rikishi
Banzuke & Rank
Performance
Ratings & Models
Sumo History
Data & Methods
Lab / Archive
```

In a real nav bar, only the first one or two levels should usually be exposed.
Deeper levels belong inside page tabs, local sidebars, accordions, or research
detail panels.

## Home

### Welcome / site orientation

* what this site is
* what is new / latest updates
* featured current pages
* known caveats and interpretation warnings

### Quick entry points

* latest standings
* banzuke changes
* rikishi lookup
* rank outcomes
* ratings and models

## Current Sumo

### Latest Tables

* current rating / standings table
* date navigation
* division filters
* sortable columns
* shikona click-through to rikishi pages
* table notes / column definitions

Analyst columns:

* Elo / Equelo
* expected wins
* probability-derived values
* current score
* latest rating
* new / projected chii
* Delta Elo
* Delta banzuke
* Delta chii, only if audited
* rank-relative values such as `vChii`

### Current Standings

* rolling recent-performance standings
* window selector
* division selector
* combined / separated views

### Current Basho

* latest results
* day view
* basho view
* rikishi result links

### Current Banzuke

* current banzuke browser
* division view
* rank slot view
* rikishi links

### Banzuke Changes

* new banzuke change report
* mechanical changes
* promotions
* demotions
* notable changes / headlines
* detailed filtered report

### Current Leaders

* max average wins
* max rating probability
* highest-rated rikishi
* biggest rating movers
* biggest banzuke movers
* unusual current rikishi by expected wins / probability

## Rikishi

### Rikishi Lookup

* search by shikona
* current rank / division
* profile link
* shikona history, if available

### Rikishi Profile

#### Summary

* current chii
* current rating
* career high
* recent record
* current trend

#### Career Timeline

* rank / chii over calendar time
* rank / chii by basho count
* division history
* career high markers

#### Rating Timeline

* Elo / Equelo over calendar time
* daily rating movement
* bout-level rating movement
* rating deltas

#### Combined Career View

* chii + rating on dual y-axes
* rank movement and rating movement together
* calendar-time mode
* basho-count mode

#### Performance Context

* recent form
* rank trend
* rating trend
* expected wins
* observed outcomes from similar chii

### Career Comparisons

* comparable careers
* fast-rising prospects
* journeymen
* newcomer context

### Career Facts

* career high table
* first appearance / debut context
* rank at retirement
* career length

## Banzuke & Rank

### Chii Explained

* what `M3e` means
* division, number, side, annotation
* sideless chii
* chii ordering
* rank movement glossary
* promotion / demotion basics

### Current Banzuke

* official-looking banzuke browser
* division filters
* rank slots
* east / west layout

### Banzuke Changes

* current banzuke change report
* new banzuke headlines
* promotions and demotions
* mechanical fact view
* editorial / interpretation view

### Banzuke Structure Over Time

* division sizes over time
* banzuke population history
* changes to sizes of divisions
* banzuke division by era

### Makuuchi Structure

* makuuchi rank population by era
* rank structure changes
* sanyaku / maegashira population history

### Rank Slot History

* first chii appearance
* Y1e history
* historical / rare ranks
* curated-rank explanation

### Division Movement

* division churn
* promotion / demotion frequency
* movement between divisions

### Retirement and Rank

* rank at retirement
* retirement-rank distribution
* `Bg` / intai ambiguity caveats

## Performance

### Rank Outcomes

* finish by chii
* average finish by chii
* threshold views
* top records from a rank
* bottom records from a rank
* expected record from rank context
* division filters
* sample-size display

### Matchups

* observed matchup probabilities
* sideless chii matchup traces
* pair support / sample size
* confidence intervals
* curated rank domain
* division filters

### Observed Expectations

* what usually happens from this rank?
* what usually happens against this opponent rank?
* rank outcome explorer
* support-aware interpretation

### Performance Patterns

* current form versus historical expectation
* rank trend
* overperformance / underperformance, if method is defined

## Ratings & Models

### Rating Overview

* why ratings?
* what rating is trying to measure
* rating versus banzuke rank
* what ratings do not prove

### Current Ratings

* current Elo / Equelo table
* rating leaders
* rating probability leaders
* rating changes
* date navigation

### Rating and Rank

* Elo / Equelo vs chii
* rating-vs-rank validation
* mean rating by chii
* mean expected wins by chii
* mean probability-derived value by chii
* normalised probability-derived value by chii
* intro rating table / chart

### Observed vs Modelled

* observed matchup traces
* model-implied matchup traces
* difference / residual chart, later
* support-aware comparison
* consistency checks

### Model Diagnostics

* inflation by rank / chii
* rating spread variants
* rating distribution
* estimators
* mean rating vs banzuke size
* calibration reports
* probability calibration
* drift over time

### Methodology

* Elo explanation
* Equelo explanation
* BKQ / legacy model explanation
* formulae
* parameters
* assumptions
* teleological-risk caveats
* why some outputs are research only

### Research Archive

* fixed-v1 rating curve charts
* one-shot simulation charts
* Expt3 predicted probability distribution
* calibration experiments
* model failures and dead ends

## Sumo History

### Population History

* division sizes over time
* changes to sizes of divisions
* banzuke population
* mean rating vs banzuke size

### Career Lifecycle

* career length count
* career length probability
* cumulative career length probability
* retirement-rank distribution

### Rank History

* first chii appearance
* Y1e history
* historical rank slots
* makuuchi rank structure over time

### Recruitment and Retirement

* recruitment patterns, future
* retirement patterns
* division entry / exit patterns

### Historical Exhibits

* banzuke division by era
* makuuchi by era
* long-term rank population charts

## Data & Methods

### Data Source

* where the data comes from
* update policy
* currentness policy
* parsed history
* known source limitations

### Glossary

* basho
* banzuke
* chii
* rikishi
* shikona
* division
* record
* fusen / non-fought outcomes
* east / west
* sideless chii

### Known Limitations

* missing or ambiguous data
* historical rank quirks
* retirement ambiguity
* parser limitations
* model limitations
* what not to infer

### Method Notes

* how historical data is parsed
* how outputs are generated
* how confidence intervals are computed
* how curated domains are chosen
* difference between observed data and model projections

### Technical Appendix

* parser and validation notes
* warning logs summary, not raw logs
* persistence reports if promoted
* data-quality notes

## Lab / Archive

### Experimental Charts

* miscellaneous legacy charts that do not yet have public framing
* old model diagnostics
* prototype charts

### Internal Diagnostics

* parser warning summaries
* weirdness reports, if ever exposed
* raw downloaded HTML should not be public navigation

### Deprecated / Superseded

* broken or unaudited columns
* Delta chii, until fixed
* old ranking/index behavior caveats
* research outputs retained for provenance
