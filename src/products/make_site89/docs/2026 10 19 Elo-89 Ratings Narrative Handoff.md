# Elo-89 Ratings Narrative Handoff

## Status

Design handoff recorded on 19 October 2026 after reviewing the current
`make_site89` prose, the Elo89 account drafts, the production model and its
research history.

This document preserves the narrative and conceptual position reached in that
review. It is not yet public prose, does not change the Elo-89 model, and does
not supersede the maintained Elo89 account requirements. Its immediate purpose
is to prevent the reasoning behind the next documentation revision from being
lost or reduced to a page-outline task.

The central conclusion is that the present public sequence is missing a
rationale between **Why ratings?** and the immediate introduction of Elo. That
rationale has three depths:

1. a casual reader needs a short account of what an Elo-89 number is for;
2. an interested reader should see why apparently obvious performance measures
   produce several legitimate but non-definitive answers; and
3. an expert reader needs an explicit account of a rating system as a model of
   sumo, together with the purposes and evidence by which such a model may be
   judged good.

These are depths of one account, not necessarily three labelled audiences or
three independently maintained documents.

## The current gap

The public sequence currently runs:

```text
Why ratings?
    -> Elo Ratings
    -> Elo-89 Ratings
    -> assumptions and comparison material
```

`Why ratings?` usefully distinguishes official chii from a numerical account
of competitive performance. The following generic Elo page explains the
probability and update formulae. The short Elo-89 page then names P1,
`q=400`, divisional K and fixed-mean population restoration.

What is missing is the argument that connects the desire for another view of
performance to the choice of an Elo-like model. The current text can leave the
impression that the project simply decided to use something called Elo-89.
It does not ask what a rating is supposed to measure, why direct summaries of
results are not definitive, or what makes one rating model preferable to
another.

The missing bridge is not merely “opponents have different strengths”. It is
that **there is no neutral, self-defining scalar called performance**. Any
attempt to compress a rikishi's record into one number must decide what
evidence is relevant and how different evidence is to be made comparable.

## Why apparently simple measures are not simple

“Count the wins” initially sounds like a model-free answer. The site's
**Rolling Wins-Based Ranking** demonstrates why it is not definitive.

Rikishi do not all fight the same number of times, so even a win-based account
immediately admits at least two scales:

- **wins per basho**, which uses participation in the selected tournaments as
  its denominator and therefore makes absence part of the result; and
- **wins per bout**, which uses counted competitive opportunities as its
  denominator and treats absence differently.

Neither scale corrects the other. They answer different questions. Wins per
basho is closer to sustained contribution or availability over the selected
period. Wins per bout is closer to success when competing. A reader must still
choose the window, the win policy, the bout-opportunity policy, the comparison
population and the treatment of movement between divisions.

Even after those choices, two rikishi with the same score may have faced
materially different opposition. One may have a better rolling score while
having competed against a weaker schedule. Promotion and demotion can change
the opposition within the selected window. The schedule is not a full round
robin and is not independent of rank, form or tournament circumstances.

This does not make a rolling-wins table defective. It is a useful descriptive
artifact answering a declared question. Its importance in this narrative is
that it makes the measurement problem visible:

> A simple calculation can be completely reproducible while still depending
> on a choice about what is being measured.

The narrative should therefore avoid “wins are crude, while Elo is clever”. A
more durable progression is:

```text
Different direct summaries answer different questions.
    -> No single summary is forced on us by the observations.
    -> We must state what we want the number to represent.
    -> An Elo-like rating is one principled way to combine opponent-relative
       competitive evidence into a common comparison.
```

## What Elo contributes

Elo does not merely attach a more complicated formula to a win count. It uses
the chronological network of bouts. Each result is interpreted through the
opponent's current rating, which in turn embodies earlier results against other
opponents. Information can therefore pass through unequal schedules and across
connected divisions.

An Elo-like rating combines, under declared rules:

- wins and losses;
- the estimated strength of the opposition;
- the chronological order of the evidence;
- connections created by bouts across changing schedules and divisions; and
- earlier competitive evidence carried in opponents' ratings.

Its result is one opponent-sensitive scalar state whose differences can be
translated into model winning probabilities.

This is Elo's real role in the narrative. It provides a way of resolving more
of the variation in the competitive record into a common comparison. It is not
the uniquely correct answer and does not contain every relevant fact about a
rikishi. Elo-89 deliberately does not model injuries, styles, motivation,
bout importance or other contextual explanations.

A suitably bounded statement is:

> Elo-89 combines the represented competitive evidence into one
> opponent-sensitive number under a declared set of rules.

## Three depths of explanation

### Casual depth

The casual reader needs a usable interpretation and a safe stopping point:

> Elo-89 is an opponent-sensitive numerical summary of represented
> performance. Higher means that the model favours that rikishi against a
> lower-rated opponent; the difference between the numbers determines by how
> much.

This layer should say that a probability permits an upset, that a rating is not
an official rank or a direct quantity of true ability, and that the site uses
the model from January 1989 onward. It need not explain fixed points,
normalisation or model selection.

### Interested depth

The interested reader should encounter the measurement problem through
concrete alternatives already available on the site:

| Measure | Question principally answered | Important choices or omissions |
| --- | --- | --- |
| Wins | How many credited wins were accumulated? | Window, participation and win policy |
| Wins per basho | How many wins were accumulated per selected tournament? | Absence affects the denominator; opposition is untreated |
| Wins per bout | How often did the rikishi win per counted opportunity? | Absence is treated differently; opposition is untreated |
| Chii | Where did the JSA officially place the rikishi? | Institutional ordering rather than a cardinal performance scale |
| Elo-89 | What opponent-relative competitive relationship does the model infer? | Depends on the model's evidence, parameters and population policies |

The conclusion is not that the first four are useless. It is that each measure
has a different meaning and none becomes the definitive meaning of
“performance” merely by being obvious or easy to calculate.

This is the right place to link to the six-basho Rolling Wins-Based Ranking.
The artifact supplies a real alternative lens rather than a straw-man system.

### Expert depth

The expert account should begin with the question:

> What, in fact, is a rating system?

A rating is not merely a number calculated from results. It is a state or
coordinate inside a model of the competitive process. Wins, losses,
participants and dates are observations. “This rikishi has rating 2317” is a
model output.

A useful abstract form is:

```text
observed competitive history
    -> assumptions about competitors, results, time and population
    -> estimated competitive state
    -> comparisons, rankings or predictions
```

This makes it possible to distinguish:

- a **count**, which records events;
- a **descriptive statistic**, which aggregates selected observations under a
  chosen denominator;
- an **institutional ordering**, such as chii;
- a **rating**, which is a model state intended to support comparisons; and
- a **forecast**, which is derived from model states under an outcome model.

The expert account must then state what real-world attribute the rating is
intended to represent. Precision in the algorithm does not establish validity
in the claimed attribute. “Strength”, “performance”, “form” and “greatness”
must not be allowed to slide into one another without definition.

## Elo-89 as a model of sumo

At technical depth Elo-89 can be understood as five related models or model
components.

### 1. Observation model

The evidence consists of represented paired binary `W/L` bout results from
January 1989 onward. Fusen and non-binary outcomes are excluded. The model does
not infer an unrepresented bout or directly observe injury, style, motivation
or physical condition.

The represented population for a basho is the banzuke population together with
participants in selected rated bouts. “Active” in the implementation therefore
does not mean “fought today”.

### 2. Performance model

Each represented rikishi has one scalar rating at a given instant. The model
assumes that the difference between two such ratings is sufficient for its
pairwise comparison. This is a deliberately one-dimensional account: it does
not represent non-transitive style relationships or separate dimensions of
competitive performance.

### 3. Outcome model

A logistic function with `q=400` maps a rating difference to a model winning
probability. A 400-point advantage means odds of ten to one; adding the same
constant to both ratings changes no probability.

The probability is a model expectation, not a promise, a confidence interval
or proof that the ratings are well estimated.

### 4. Learning model

After an eligible result, each rating changes by the prediction error
multiplied by that participant's K. Elo-89 uses:

| Rank group | K |
| --- | ---: |
| Yokozuna, Ozeki, Sekiwake and Komusubi | 10 |
| Maegashira | 15 |
| Juryo | 25 |
| Makushita, Sandanme, Jonidan and Jonokuchi | 35 |

K expresses a responsiveness-versus-fluctuation policy. When opponents have
different K values, their changes need not sum to zero.

### 5. Population model

The fixed P1 table supplies chii-informed ratings to the initial January 1989
population, new entrants and returning rikishi. A rikishi is not continually
forced back towards his chii value after entry.

Before a basho's bouts and again after them, the represented population is
shifted uniformly to the fixed target mean. An instantaneous common shift
preserves every contemporaneous rating difference, ordering and model
probability. Across time the policy remains consequential because surviving
ratings later interact with entrants assigned fixed P1 values. The common
shifts can also contribute materially to a displayed rating change.

A rikishi who remains represented but records no eligible bouts receives no
individual bout update. Leaving the represented population discards his
rating; a later return causes reinitialisation from P1.

## The engineering pipeline

The complete model can be summarised as:

```text
represented History from 1989/01
    -> select eligible binary W/L bouts
    -> form each basho's represented population
    -> initialise entrants from frozen P1
    -> shift the population to the target mean
    -> forecast and update each bout chronologically
    -> shift the population back to the target mean
    -> record basho-start, day-end and basho-end observations
    -> publish tools using the observation appropriate to each question
```

Observation stage is part of a publication's meaning. Career Comparisons uses
basho-start values; Basho Results and Rating Changes use normalised basho
endpoints; Highest Elo-89 deliberately uses day-end maxima; Torikumi uses the
most recent available pre-bout snapshot. These are not interchangeable forms
of one universal “current rating”.

## What would make a rating model good?

There is no context-free answer. A rating system is good relative to a declared
purpose. Candidate criteria for Elo-89 include:

- **Definition:** inputs, state transitions and observation stages are exact;
- **Interpretability:** rating differences have a stated meaning;
- **discrimination:** competitively different rikishi are usefully
  distinguished;
- **prediction:** pre-bout probabilities improve on relevant alternatives;
- **calibration:** events assigned a probability occur at a corresponding
  long-run frequency;
- **responsiveness:** meaningful changes can be learned without excessive lag;
- **stability:** ordinary random variation is not mistaken for a large durable
  change;
- **comparability:** the scale remains interpretable across the populations and
  periods for which comparisons are claimed;
- **coverage and connectedness:** the result network supports the comparisons;
- **robustness:** conclusions are not unduly determined by reasonable changes
  in initialisation, K, normalisation or sparse observations;
- **reproducibility:** the same evidence and contract produce the same result;
- **parsimony:** extra mechanisms earn their complexity; and
- **fitness for purpose:** the model answers the question its users actually
  want answered.

Several criteria conflict. Larger K improves responsiveness but increases
fluctuation. Fixed-mean population control improves scale discipline but adds
changes not earned in individual bouts. A richer model could represent more
context while becoming harder to estimate, explain and validate.

A good model cannot be defined merely as one which agrees with the banzuke,
produces plausible historical heroes, moves winners upwards, or beats one weak
baseline. Those are possible diagnostics, not a complete validity criterion.

For Elo-89 the core evaluable claim is deliberately bounded: rating differences
produce probabilities which can be scored against later represented results.
Predictive evidence is especially important because it constrains tuning by an
observable consequence, but prediction is not the only conceivable purpose of
a rating system.

## What the evidence currently establishes

Elo-89 was selected through controlled retrospective comparisons of post-1988
Elo-family models. Whole-population preservation with canonical P1 held fixed
led the tested models under the declared log-loss and Brier criteria.

This is model-selection evidence, not prospective validation. P1 was learned
from the same broad historical period on which retrospective forecasts were
scored. Calibration is also not uniform: ratings with little prior evidence
are a particular weakness when facing established ratings.

The accepted judgement is that Elo-89 is a useful and defensible compact model
of represented competitive performance, with explicit assumptions and
observable failure modes. It has not been shown to reveal true ability, to be
the uniquely appropriate model family, or to make every cross-era comparison
unconditional.

## P1 is a separate construction

P1 is a frozen entrant-initialisation table, not a continually fitted rank
curve and not the output of repeatedly applying the final Elo-89 replay
unchanged.

Its fixed-point producer replays history, aggregates process ratings by
literal chii, applies support-proportional post-iteration recentering and uses
legacy departure redistribution during construction. The subsequent Elo-89
replay holds the resulting P1 table fixed and applies common whole-population
mean shifts. These operations must not be conflated in the technical account.

There is also a known deferred P1 defect: its constructor omitted valid paired
`W/L` results when the kimarite field was blank. The production Elo-89 replay
already rates those results correctly. P1 regeneration must remain a separate,
controlled model-maintenance operation rather than an automatic website-build
step.

## Evolution of the ideas

The eventual public account should present the selected model directly, but
future engineers need a compact lineage so that superseded mechanisms are not
mistaken for Elo-89.

- Early Equelo work explored full-history Elo, divisional K, fixed-point chii
  priors, scale drift, support thresholds and lower-rank instability. Many
  variants used `q=850` or `q=900`; they are evidence and ancestry, not the
  current contract.
- A definitive post-1988 Basic Elo baseline fixed `q=400`, constant `K=35`
  and equal entrant ratings.
- A controlled factorial comparison tested constant versus divisional K and
  equal versus informed initialisation. Divisional K plus an informed prior was
  retained as the strongest successor family.
- The prior construction was rebuilt at `q=400`; support-proportional
  recentering produced canonical P1.
- Population experiments separated entrant initialisation from the population
  operator. Whole-population mean preservation with P1 held fixed was selected
  and the complete contract was named Elo-89.
- A provisional 1958 historical extension was named Elo-58. The name Equelo2
  was reserved for a possible future full-history successor. Elo-58 research
  was paused so Elo-89 could become the operational website model.
- Later appraisal accepted normalisation with disclosure, clarified inactivity
  and return semantics, and identified the absence of individual uncertainty
  estimates.
- The per-chii drift study showed that preserving the overall mean does not
  preserve the rating associated with every chii through historical time.
  This informed the pause in the longer Elo89 account; it did not revoke the
  adopted model.

## Consequences for the public information architecture

The current navigation repeats **Elo-89 Ratings** as both the parent section
and a child page. A clearer working structure is:

1. **Why ratings?** — why chii and direct result summaries do not exhaust the
   questions readers may ask;
2. **Reading an Elo-89 rating** — the casual interpretation;
3. **From simple measures to a rating model** — the interested-reader bridge,
   using Rolling Wins-Based Ranking;
4. **How Elo-89 works** — the advanced overview of the complete pipeline;
5. **Elo-89 technical definition** — the exact engineering contract and
   observation stages;
6. **Evidence, assumptions and open questions** — selection, calibration,
   normalisation, uncertainty and known defects; and
7. **Elo-89 and chii** — their relationship and interpretation.

The parent could become **Ratings** or **Understanding Elo-89**. The duplicated
child should become **How Elo-89 works** or **Elo-89 model overview**.

The public artifact names also require semantic care:

- **Typical Elo-89 Ratings** currently publishes selected P1 entrant values as
  rank landmarks; it is not an empirical table of typical established
  wrestlers' ratings.
- **Win Probability by Ranks** compares observed rank-pair outcomes with a
  curve derived from P1 rank values; it is not a summary of Elo-89's historical
  pre-bout forecasts.
- **Highest Elo-89** uses intrabasho day-end maxima, unlike publications based
  on normalised basho-end observations.

These tools may remain useful, but their questions and observation semantics
must be named accurately.

## Authoring principle

The technical definition should be written first as the semantic authority.
The interested and casual accounts should then be controlled reductions of
that definition. They may omit detail, but must not make claims which later
layers withdraw.

This is compatible with one coherent progressively disclosed account. Reader
layers describe legitimate stopping points, not rigid classifications of
people. A knowledgeable reader may be casual when checking a table and expert
when assessing the model.

The intended narrative progression is:

```text
Why seek another view besides chii?
    -> Why do obvious numerical summaries produce different answers?
    -> What question do we want one number to answer?
    -> A rating system is a model, not merely a formula.
    -> Here is the particular model called Elo-89.
    -> Here is why it is useful, how it was selected and what remains
       conditional.
```

That progression supplies the rationale currently missing between **Why
ratings?** and the immediate introduction of Elo.

## Sources to retain

- [Elo89 account requirements](Elo89%20Account%20Requirements.html)
- [Elo89 account contents](Elo89%20Account%20-%20Contents.html)
- [Documentation handoff](Documentation%20Handoff.md)
- [Production documentation strategy](Production%20Documentation%20Strategy.md)
- [Reader Layers](../../../analysis/docs/story/01%20Reader%20Layers.md)
- [Narrative and Validation Structure](../../../analysis/docs/story/02%20Narrative%20and%20Validation%20Structure.md)
- [Tranche 1: Population Normalisation Policy](../../../analysis/docs/story/15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md)
- [Elo-89 Rating System Appraisal](../../../analysis/docs/story/22%20Elo-89%20Rating%20System%20Appraisal.md)
- [Strength, Purpose and Model Bias](../../../analysis/docs/2026%2009%2011%20Strength,%20Purpose%20and%20Model%20Bias%20-%20Lab%20Note.md)
- [Chii and the Measurement of Strength](../../../analysis/docs/2026%2009%2026%20Chii%20and%20the%20Measurement%20of%20Strength.md)
- [Production replay](../../../analysis/elo89/replay.py)
- [Standings account](../../../analysis/standings/README.md)
- [P1 missing-kimarite repair](../../../../docs/Elo-89%20P1%20Missing%20Kimarite%20Repair.md)

## Next

Agree the authority and intended publication shape before changing public
prose. Then draft the exact **Elo-89 technical definition** from the production
contract and evidence, using this handoff as the narrative checklist. Only
after that definition is reviewed should the interested-reader bridge and the
casual account be written as reductions of it.

As part of that design pass, decide whether the existing unfinished Elo89
account should be resumed and reorganised, or whether a new canonical account
should replace it while preserving the existing drafts as research evidence.
