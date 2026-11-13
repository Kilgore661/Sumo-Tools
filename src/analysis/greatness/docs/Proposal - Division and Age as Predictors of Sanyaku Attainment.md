# Division and Age as Predictors of Sanyaku Attainment

This document began as the implementation proposal. It now records the
motivation, requirements, implemented design, and findings of the completed
analysis. Normative language in the design sections describes the contract the
implementation and its outputs are expected to preserve.

## Purpose

The motivating question is practical and prospective:

> When a rikishi appears at a particular division or rank group at a particular
> age, how likely is he eventually to reach san'yaku?

The initial example was a newly promoted Maegashira aged about 27. The working
intuition is that an older new Maegashira is less likely than a younger one to
become a future fixture near the top of the banzuke. Reaching san'yaku is the
first operational proxy for becoming such a fixture.

Earlier exploratory work calculated the age distribution *among rikishi already
known to have reached san'yaku*. That answers a retrospective question:

\[
P(\text{age at first san'yaku} \leq A
  \mid \text{eventually reached san'yaku}).
\]

It does not estimate the prospect facing a rikishi observed at division `D`
and age `A`, because it omits every rikishi who never reached san'yaku. This
analysis defines the two prospective probabilities that are actually wanted.

They do not have equal roles in the investigation. Division-debut probability
is the primary result because it directly answers the original question about
a new Maegashira. Division-state probability is a secondary updating measure:
once a rikishi is no longer a debutant, it describes the historical prospects
of rikishi at his current division and age who have not yet reached san'yaku.

## Required probabilities

Let `S` mean that the rikishi reaches san'yaku at some later basho. Let `D` be
one of the supported pre-san'yaku division/rank groups, and let `A` be completed
age in years at the observation basho.

### 1. Division-debut probability

\[
P(S \mid \text{first appearance in } D \text{ at age } A).
\]

This answers questions such as:

> What proportion of rikishi making their Maegashira debut at age 27 later
> reach san'yaku?

Each rikishi contributes at most one observation to each division-debut cohort:
his first represented appearance in that division or rank group.

### 2. Division-state probability

\[
P(S \mid \text{is in } D \text{ at age } A,
       \text{ has not previously reached san'yaku}).
\]

This answers questions such as:

> What proportion of 27-year-old Maegashira who have not previously reached
> san'yaku later do so?

For this measure, a rikishi contributes at most once to a `(D, A)` cohort even
if he occupies that division in several basho while the same completed age. Use
his earliest qualifying basho at that division and age.

The two probabilities must remain separate. A new 21-year-old Maegashira and a
rikishi who debuted at 18 but remains Maegashira at 21 share the same
division-state cohort, but only the former belongs to the age-21 division-debut
cohort. Remaining in Maegashira for three years is information that the debut
measure deliberately does not contain.

State probability is therefore of interest because it permits reassessment as
a career develops. A rikishi can move into a new division, remain at the same
level while growing older, or fall to a lower division without having reached
san'yaku; each change can place him in a different historical state cohort.
This is an update to the age-and-division cohort prognosis, not a personalised
model of ability. It does not displace division-debut probability as the answer
to the motivating new-Maegashira question.

## Supported divisions and outcome

The implementation supports these starting groups:

| Group | Meaning |
|---|---|
| `M` | Maegashira only |
| `J` | Juryo |
| `Ms` | Makushita |
| `Sd` | Sandanme |
| `Jd` | Jonidan |
| `Jk` | Jonokuchi |

`M` deliberately means Maegashira rather than all Makuuchi. San'yaku positions
are the target outcome and therefore are not risk states.

For this investigation, san'yaku means first reaching any of:

- Komusubi;
- Sekiwake;
- Ozeki;
- Yokozuna.

The event must occur strictly after the qualifying observation. Once a rikishi
has reached san'yaku, none of his later demotions to Maegashira or a lower
division may create new risk observations.

This is intentionally a binary, first-attainment endpoint. For the purposes of
this experiment, the minimal notion of greatness is that san'yaku was achieved
at least once. A second or later entry into san'yaku is not another event and
does not make a success more successful.

Persistence in san'yaku is a valid stronger notion of greatness. It could be
defined by cumulative san'yaku basho, consecutive tenure, repeated entries, or
a higher-rank endpoint. None of those definitions is adopted here; they would
answer a different question and require a separately specified outcome.

Generalising the outcome to arbitrary destination divisions or ranks is out of
scope. It can be considered later if a concrete research question requires it.

## Population: complete represented records

The analysis requires a declared supporting boundary basho, called the epoch.
For the full canonical History this is normally `1958/01`.

Everyone present on the epoch banzuke is a left-boundary incumbent. Their true
career start predates or is indistinguishable from the start of the represented
History, so they must be excluded. A rikishi first appearing on a later banzuke
has a complete represented **ranked** record from that point onward and is
eligible for cohort construction.

This is a conservative rule. A genuine debutant on the epoch banzuke is also
excluded because History alone cannot distinguish him from an incumbent.

Active rikishi first observed after the boundary have complete records from the
left and remain eligible. Their outcomes may, however, be right-censored at the
analysis cutoff.

## Age definition and exact basho dates

Age must mean completed years on Day 1 of the observation basho:

\[
\operatorname{age}(b,d)
= b_{year}-d_{year}
- I[(b_{month},b_{day}) < (d_{month},d_{day})],
\]

where `b` is the exact Day 1 date and `d` is the birth date.

The canonical `History.Date` stores only a basho label such as `1965/07`.
Using the first day of that labelled month is not sufficiently accurate. Some
basho start in the preceding calendar month: the downloaded `1965/07` Day 1
page, for example, records `June 27, 1965`.

The raw daily-result HTML already contains exact dates. The current daily parser
also captures the date components in its header regular expression, but then
discards them and retains only the remaining HTML. Before treating the age
probabilities as final, the parser and persisted model should preserve these
dates.

Preferred implementation:

1. add the parsed civil date to `DailyResults`, or add an equivalent explicit
   day-to-calendar-date mapping to `Summary`;
2. update History persistence to preserve it;
3. use the date attached to Day 1 as the basho start;
4. if Day 1 is unavailable but another day has an exact date, derive Day 1 by
   subtracting `day - 1` days;
5. validate that all available daily dates within a basho imply the same Day 1.

Until this is implemented, exploratory outputs must label the existing value
as `age_at_basho_month_start` and state that it can differ from exact basho age
by one year.

## Birth-date availability

Birth dates come from the parsed rikishi bio data. A cohort observation cannot
be assigned to an age without a full birth date.

Every output must report:

- complete-record rikishi considered;
- rikishi excluded for a missing bio;
- rikishi excluded for a missing or partial birth date;
- qualifying observations retained.

Missing birth dates must not silently become an age or an outcome failure.
Birth-date coverage may vary by historical period, so the exclusions are a
possible source of selection bias.

## Maezumo and the meaning of debut

The ranked History does not include Maezumo (`Mz`) as an ordinary banzuke
position. Bio data may therefore give a `Hatsu Dohyo` one basho earlier than a
rikishi's first ranked History appearance. For example, a May Maezumo debut can
be followed by a first Jonokuchi banzuke in July.

In this analysis, **division debut** means first represented ranked appearance
in `Jk`, `Jd`, `Sd`, `Ms`, `J`, or `M`. It does not mean Hatsu Dohyo or first
Maezumo participation. The output and write-up must use this terminology
consistently.

Makushita and Sandanme tsukedashi entrants are valid division debuts at their
observed starting group; they must not be assigned hypothetical lower-division
observations.

The definition is per division rather than per career. A rikishi can therefore
contribute a debut observation when he first appears in each successive
division. His first represented appearance in a lower division may also follow
direct entry into, or an earlier appearance in, a higher division. The present
cohort does not distinguish upward arrival, direct entry, or downward arrival.
Those are different entry routes, but all satisfy the specified event of first
represented appearance in `D`.

## Outcome classification

For every qualifying observation, classify the future as one of four states:

### Success

The rikishi subsequently appears at Komusubi, Sekiwake, Ozeki, or Yokozuna at
least once. Success is binary and is recorded at first attainment; later
san'yaku appearances are not additional successes.

### Failure

The rikishi is known to have retired without subsequently reaching san'yaku.
Use parsed `Intai` evidence where available. A disappearance from a banzuke by
itself must not automatically be treated as retirement.

### Right-censored

The rikishi has not subsequently reached san'yaku and his career remains active
at the History cutoff. He has not failed; the outcome is not known yet.

### Unknown

The rikishi has no later san'yaku event, is not demonstrably active at the
cutoff, and lacks reliable retirement evidence. Unknown cases must remain
separate from both failures and right-censored active careers.

## Probability reporting

The simplest auditable descriptive estimate is the resolved-outcome proportion:

\[
\widehat P_{resolved}
= \frac{N_{success}}
        {N_{success}+N_{failure}}.
\]

Every row must also publish `success`, `failure`, `right_censored`, `unknown`,
and `resolved` counts. Report conservative identification bounds:

\[
P_{lower}=\frac{N_{success}}{N_{all}},
\qquad
P_{upper}=\frac{N_{success}+N_{right\ censored}+N_{unknown}}{N_{all}}.
\]

The resolved estimate assumes resolved careers are representative of unresolved
careers with the same division and age. That assumption may be poor for recent
or sparsely populated cohorts. The bounds make the uncertainty visible but can
be wide.

A later statistical refinement may use a competing-risk time-to-event model:
san'yaku attainment is the event of interest, retirement without san'yaku is a
competing terminal event, and active careers are censored at the History cutoff.
That is preferable for inference but is not required for the first transparent
descriptive implementation.

## Required atomic dataset

Produce one auditable row per qualifying observation with at least:

| Field | Meaning |
|---|---|
| `cohort_type` | `division_debut` or `division_state` |
| `rikishi_id` | Canonical `RikId` |
| `shikona` | Display name with the project's normal disambiguation |
| `division` | `M`, `J`, `Ms`, `Sd`, `Jd`, or `Jk` |
| `age` | Completed age on exact basho Day 1 |
| `observation_basho` | Canonical `YYYY/MM` basho label |
| `observation_start_date` | Exact civil Day 1 date |
| `observation_chii` | Exact chii at the observation |
| `division_debut_basho` | First represented basho in the division |
| `division_debut_age` | Age at that first represented division appearance |
| `first_sanyaku_basho` | Event basho, blank if none observed |
| `first_sanyaku_chii` | First san'yaku chii, blank if none observed |
| `outcome` | `success`, `failure`, `right_censored`, or `unknown` |
| `follow_up_basho` | Represented basho from observation to event/cutoff |
| `intai` | Parsed retirement basho when available |

The atomic data must make it possible to reconstruct every aggregate count.

## Required aggregate outputs

### `probability_by_division_debut_age.csv`

One row per `(division, age)` for:

\[
P(S \mid \text{division debut at age } A).
\]

### `probability_by_division_state_age.csv`

One row per `(division, age)` for:

\[
P(S \mid \text{in division at age } A,
       \text{ no previous san'yaku}).
\]

Both files must include all outcome counts, resolved probability, lower and
upper bounds, and the analysis cutoff.

### Optional threshold views

Derived files for conditions such as `age > A` are useful, but they must be
calculated directly from unique qualifying rikishi rather than by summing or
averaging exact-age probabilities. For a threshold cohort, use the rikishi's
earliest qualifying observation after the threshold and count him once.

These threshold-conditioned curves are not cumulative distribution functions
and need not be monotonic because the conditioned population changes with the
threshold.

## Implementation architecture

This investigation should be delivered as a small analysis package rather than
as one script containing both production logic and temporary probes. The public
entry point should orchestrate reusable supporting modules and persist the
evidence used to justify every population decision.

A likely package boundary is:

```text
src/analysis/greatness/sanyaku_prospects/
    __init__.py
    __main__.py
    model.py
    population.py
    cohorts.py
    outcomes.py
    probabilities.py
    outputs.py
```

The responsibilities should be:

### `population.py`

- select the represented History from the declared epoch;
- identify and exclude epoch-boundary incumbents;
- identify complete represented ranked records;
- join complete-record rikishi to bio data;
- classify missing bios, missing birth dates, and partial birth dates;
- expose both selected `RikId` sets and audit counts.

This is the authoritative implementation of the phrase **complete represented
record** for this analysis. Other greatness analyses should reuse it rather
than independently reproducing the boundary rule.

### `cohorts.py`

- construct division-debut observations;
- construct division-state-age observations;
- exclude observations at or after first san'yaku;
- enforce one observation per rikishi and division for debut cohorts;
- enforce one observation per rikishi, division, and age for state cohorts;
- retain source dates and exact chii for auditability.

### `outcomes.py`

- locate first later san'yaku appearance;
- distinguish success, known failure, right-censored, and unknown;
- retain event, retirement, cutoff, and follow-up evidence;
- avoid treating disappearance alone as retirement.

### `probabilities.py`

- aggregate atomic observations by cohort type, division, and age;
- calculate resolved probabilities and identification bounds;
- construct optional direct `age > A` cohorts;
- contain no file-system or CLI behaviour.

### `outputs.py`

- write atomic observations, aggregate results, exclusions, coverage audits,
  and a run manifest;
- ensure all outputs reconcile before writing them;
- use stable schemas suitable for later site or narrative consumption.

### `model.py`

- hold immutable row and result dataclasses shared by the supporting modules;
- define outcome and exclusion enums so output labels cannot drift between
  modules.

### `__main__.py`

- load History and bios;
- accept epoch, cutoff, input, and output paths;
- call the pure supporting modules;
- write the complete result bundle;
- print only a concise run summary.

The main product is the probability bundle. The supporting modules and their
persisted audits are part of that product's evidence contract, not optional
development tooling.

## Required persisted audit outputs

The following evidence must be persisted on every production run.

### `population_summary.csv`

One compact reconciliation table containing at least:

| Measure | Meaning |
|---|---|
| `history_rikishi` | All distinct rikishi represented after the epoch |
| `boundary_incumbents` | Rikishi present on the epoch banzuke |
| `complete_record_rikishi` | Represented rikishi after removing boundary incumbents |
| `complete_records_with_bio` | Complete records joined to a parsed bio |
| `complete_records_missing_bio` | Complete records without a parsed bio |
| `complete_records_with_birth_date` | Complete records with a usable full birth date |
| `complete_records_missing_birth_date` | Complete records without a usable full birth date |
| `qualifying_debut_rikishi` | Rikishi contributing at least one debut observation |
| `qualifying_state_rikishi` | Rikishi contributing at least one state observation |

These counts answer questions such as “how many complete careers are
represented?” and “for how many of those is age observable?” without rerunning
an ad hoc probe.

### `population_exclusions.csv`

One row per excluded rikishi and reason, with fields such as:

```text
rikishi_id, shikona, reason, first_basho, first_chii, detail
```

Reasons should include at least:

- `boundary_incumbent`;
- `missing_bio`;
- `missing_birth_date`;
- `partial_birth_date`;
- any future exact-date coverage exclusion.

A rikishi with more than one relevant issue may have multiple explicit reason
rows, or one row containing a stable ordered set of reasons. The chosen policy
must be documented and tested.

### `basho_date_coverage.csv`

One row per represented basho recording:

- canonical `YYYY/MM` label;
- exact Day 1 date;
- whether Day 1 was parsed directly or reconstructed from another day;
- number of daily pages with exact dates;
- whether all available pages imply the same Day 1;
- any exclusion or warning.

This persists the evidence behind exact age calculation and makes historical
date gaps visible.

### `cohort_observations.csv`

The atomic dataset specified above. Both aggregate result files must be fully
reconstructible from it.

### `outcome_summary.csv`

Counts by cohort type and outcome status, including success, failure,
right-censored, and unknown. This makes the impact of unresolved careers
visible independently of the probability tables.

### `manifest.json`

The run manifest should record:

- source History and bio identities where available;
- epoch and analysis cutoff;
- exact-date policy;
- san'yaku definition;
- division definitions;
- population and censoring contracts;
- output schema version;
- headline reconciliation counts;
- paths or names of every produced artifact.

## Reconciliation invariants

The producer must fail rather than silently publish internally inconsistent
outputs. At minimum:

\[
N_{history}
=N_{boundary}+N_{complete},
\]

\[
N_{complete}
=N_{with\ birth\ date}
 +N_{missing\ birth\ date}
 +N_{missing\ bio},
\]

subject to the documented treatment of partial dates, and for every aggregate
probability row:

\[
N_{all}
=N_{success}+N_{failure}+N_{right\ censored}+N_{unknown}.
\]

Every aggregate count must also equal the corresponding count reconstructed
from `cohort_observations.csv`.

## Infrastructure prerequisite: exact dates

Preserving exact daily dates belongs in the core parsing and persistence path,
not solely inside the greatness analysis. The analysis package should consume
persisted exact dates through the core model; it should not reparse raw HTML as
a private workaround.

The initial implementation currently uses a shared infrastructure helper to
read exact dates from the downloaded daily-result HTML. This produces precise
ages and a persisted `basho_date_coverage.csv`, and it verifies that every
available daily page implies the same Day 1. It is nevertheless transitional:
the analysis still initiates raw-source date extraction because the existing
live and archived History artifacts were built before exact dates were
preserved.

The parser and serializer now support `DailyResults.calendar_date`, but the
proper completed architecture should materialize a first-class `BashoCalendar`
or an equivalent core aggregate during History construction. Rebuilt History
artifacts should carry or be accompanied by that calendar, and the prospects
producer should then accept the persisted calendar as an input rather than a
daily-results HTML directory.

The infrastructure change should therefore be implemented and tested
separately, then treated as an input dependency of the final san'yaku-prospects
producer. Until that dependency is satisfied, the producer may support an
explicit exploratory month-start mode, but its manifest and filenames must
identify the approximation and must not present it as exact-age output.

## Assumptions and interpretation

1. Reaching san'yaku once is the deliberately minimal proxy for becoming a
   future "name" or fixture. It does not require sustained or repeated san'yaku
   tenure. Persistence is a valid stronger outcome, but it is not the outcome
   adopted for this experiment.
2. Division and age are descriptive predictors, not a causal model.
3. Exact Maegashira position, recent results, injury, tsukedashi status, heya,
   era, and other career information are intentionally omitted.
4. The state probability pools new division entrants and longer-tenured rikishi
   of the same age. This is the intended distinction from the debut probability,
   not an implementation error.
5. One rikishi may contribute to several state-age cohorts. Rows within and
   between ages are therefore statistically dependent; naive independent-row
   confidence intervals would be misleading.
6. Historical promotion policy, division sizes, and career patterns change over
   the 1958--2026 period. Aggregate probabilities assume those eras are
   sufficiently comparable for the descriptive question.
7. Banzuke coverage, rather than bout-result completeness, defines cohort
   membership and san'yaku attainment. Missing lower-division bout results in
   early history do not by themselves prevent this analysis.

## Validation requirements

Tests must cover at least:

1. exclusion of epoch-boundary incumbents, including an incumbent Yokozuna;
2. one division-debut observation per rikishi and division;
3. one state observation per rikishi, division, and completed age;
4. exclusion of every post-san'yaku demotion from the risk set;
5. a rikishi contributing to both a younger debut cohort and an older state
   cohort when appropriate;
6. success, failure, right-censored, and unknown outcomes;
7. missing bio and missing birth-date exclusions;
8. exact Day 1 parsing, including a basho whose Day 1 lies in the preceding
   calendar month;
9. consistent Day 1 reconstruction from later daily pages;
10. tsukedashi entrants beginning in their actual observed division;
11. direct unique-rikishi construction of optional `age > A` cohorts;
12. reconciliation of atomic observations with every aggregate output row.
13. reconciliation of population summary counts with exclusion rows;
14. stable manifest contracts and schema versioning;
15. refusal to publish when exact-date evidence is inconsistent, unless an
    explicitly selected exploratory approximation policy applies.

## Relationship to current exploratory code

The existing `sanyaku_age_distribution.py` answers the retrospective age-among-
successes question. The existing `sanyaku_transition_probability.py` provides
useful exploratory division-state and censoring machinery, but it currently:

- uses month-start rather than parsed exact Day 1 dates;
- does not publish the division-debut probability as a separate first-class
  output;
- should be refactored around the atomic cohort dataset specified here.

Those modules should inform the implementation, but their current outputs must
not be presented as the final answer to both required probabilities.

## Findings and interpretation

These are descriptive readings of the completed 1958--2026 output. This
section deliberately focuses on the observed proportions rather than attempting
to resolve sampling uncertainty.

### Debut probability is the primary result

Division-debut probability most directly answers the motivating question about
the significance of age when a new Maegashira appears. The Maegashira curve is
broadly decreasing with age. Age 27 is a reasonable operational boundary rather
than a proven discontinuity: debutants older than 27 have an observed resolved
probability of about 10% or less at each populated age through 30.

Juryo shows the same broad pattern at slightly younger ages. Resolved
probability is about 70% at ages 19--20, 34--41% at 21--23, 15--19% at 24--25,
5.6% at 26, and approximately 0--4% from 27 onward. Age 26 is therefore a
reasonable Juryo analogue of the Maegashira age-27 boundary.

### State probability is the natural companion

Division-state probability does not replace the debut result. It follows
naturally once the question changes from assessing a new division entrant to
reassessing an existing rikishi. As he ages or changes division without first
reaching san'yaku, it reports the historical prognosis of the new age-and-
division cohort to which he belongs. It is therefore an updating measure, while
debut probability remains the answer to the original question.

The estimate is still a cohort description rather than a personalised forecast:
it does not use exact rank, recent results, injury, or individual ability.

### Makushita

Makushita debut probability contains useful information, but it is not a
single smooth age effect. The observed probability declines from about 30% at
ages 16--17 to 3.8% at 21, then rises to 11.7% at 22 before declining again.
The age-22 cohort contains many university and makushita-tsukedashi entrants.
The rebound is consequently evidence of a selected entry pathway, not a reason
to conclude that an older ordinary Makushita debutant has better prospects.

Makushita is the strongest candidate for a future result stratified jointly by
age and entry route.

### Sandanme, Jonidan, and Jonokuchi

These debut curves have low absolute attainment probabilities and conspicuous
secondary peaks around ages 22--23. The older cohorts contain a different mix
of university, qualified amateur, foreign, and tsukedashi recruits from the
ordinary school-age intake. The curves are therefore not meaningless or random;
they describe recruitment-pathway mixtures. They are, however, poorly suited
to a simple statement that age alone determines prospects.

For the original scouting question, these debut results are exploratory rather
than equivalent headline age curves alongside Maegashira and Juryo. State
probability remains more directly useful across the lower divisions because it
asks about a rikishi observed at his current level and age.

## Deferred investigations

The downloaded data contains historically surprising very young entrants,
including ranked Jonokuchi observations at completed age 12. These records are
interesting and should be validated and investigated separately. They are not
the purpose of this analysis and should not distract from the Maegashira-age
prospect question.

Entry route is a possible additional cohort parameter. A future extension
could estimate

\[
P(S \mid \text{division debut at age } A, \text{entry route } R).
\]

At minimum, `R` should distinguish ordinary progression from below, direct
Makushita tsukedashi entry, direct Sandanme tsukedashi entry, and first arrival
from above. Further distinctions such as university/amateur background or
foreign recruitment should be added only when the source data supports them
reliably. Entry-route groups would need their own persisted provenance and
audit counts rather than being inferred silently from age.

Another possible presentation is a chart of an individual rikishi's historical
cohort prognosis over time. A state-probability step line could change whenever
his completed age or division changes, with debut-probability markers at first
division appearances, and stop at first san'yaku attainment, retirement, or the
history cutoff. Such a chart must be described as the trajectory of matched
age-and-division cohort probabilities, not as a personalised ability model or
as probabilities that were necessarily available contemporaneously.

Possible later extensions, only if justified by a specific question, include:

- stronger definitions of a fixture, such as multiple san'yaku basho or
  reaching Sekiwake;
- entry route as a cohort parameter, including ordinary progression,
  tsukedashi/direct entry, and first arrival from above;
- per-rikishi charts showing how matched cohort prospects change with age and
  division over time;
- division tenure as an additional predictor;
- exact Maegashira number or broader chii bands;
- era-stratified estimates;
- competing-risk modelling and uncertainty intervals;
- arbitrary destination divisions or rank groups.
