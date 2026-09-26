# Chii and the Measurement of Strength

## Status and purpose

This note records the position reached in discussion on 26 September 2026. It
is a conceptual argument about the foundations of a statistics of sumo, not a
new empirical investigation and not a claim that chii contain no information
about strength.

The intended purpose of the current modelling work is to investigate who is
strongest under stated, measurable notions of strength. The question addressed
here is whether chii can themselves provide the numerical foundation for such
a measure.

## Position

Chii are informative institutional labels, but they do not constitute a
coherent numerical scale of sumo strength. They should be treated as an
informal institutional indication of competitive standing, not as the ground
truth against which a formal strength model is judged.

This is not an argument that chii are useless. They may be used to describe the
banzuke, study JSA decisions, provide context, supply a predictor or entrant
prior, and compare institutional standing with an independently constructed
outcome model. The objection is to using chii as the primary formal metric of
strength.

## Chii give an order, not a distance

It is commonplace to present chii in a single conventional order, beginning
with Yokozuna and continuing through the numbered ranks of Jonokuchi. This is
useful for orientation and banzuke display. It does not establish that all
positions lie on an interval scale.

Enumerating the occupied positions as 1, 2, 3, and so on provides an ordinal
ordering. Treating differences between those numbers as meaningful would add
the assumption that every adjacent step represents the same difference in
strength. The banzuke system supplies no such assumption.

The repository's `Chii.ordinal()` is likewise an authoritative machine
ordering and serialization value, not a strength metric. Its numerical gaps
encode level, number, annotation and side so that chii can be compared and
reconstructed. Arithmetic differences between those codes do not measure
strength.

## Chii do not all have the same kind of meaning

The banzuke appears to combine several kinds of institutional object:

- Yokozuna is a conferred, permanent status with a particular cultural and
  historical meaning.
- Ozeki is a conferred status with special retention and demotion rules.
- Sekiwake and Komusubi are distinct formal ranks, but it is not established
  that they define distinct empirical strength classes. For some analysis a
  combined lower-sanyaku category may be more appropriate.
- Maegashira, Juryo, Makushita, Sandanme, Jonidan and Jonokuchi contain numbered
  positional lists.
- Division boundaries have institutional meanings of their own. The
  Juryo--Makushita boundary, for example, separates sekitori from non-sekitori
  status.
- East and west provide a further ordering within nominal positions without
  necessarily representing a substantial difference in strength.

A useful provisional description is therefore:

```text
special statuses:       Y | O
lower sanyaku:          S/K
numbered divisions:     M | J | Ms | Sd | Jd | Jk
```

The vertical boundaries in this display are not presumed to be numerical gaps
of the same kind or size. Chii form a structurally heterogeneous hierarchy,
partly categorical and partly ordinal.

## Rank is path-dependent

Present chii do not depend only on present strength. Yokozuna cannot be
demoted, and Ozeki retention and demotion are governed by special rules. More
generally, a rikishi's next position depends on his previous position, recent
record, the records of other rikishi, retirements, available places and the
JSA's application of institutional conventions.

Two rikishi of similar current bout-winning ability can consequently hold
different chii because they arrived by different historical routes. Chii
preserve information about status and career history that need not be a measure
of current strength.

Ozeki promotion also does not give Sekiwake a uniquely defined role from which
a separate strength class follows. The conventional benchmark concerns
sustained wins at Komusubi or Sekiwake, is not an automatic rule, and historical
promotion decisions sometimes include a strong first result at Maegashira.

## The banzuke has no fixed numerical geometry

The number of sanyaku positions is not fixed, and there is no institutional
upper bound that supplies a permanent width for each class. This prevents a
simple fixed scalar construction from having all of the following properties:

1. unbounded class sizes;
2. equal non-zero spacing within each class;
3. finite offsets between classes; and
4. a permanent ordering in which every member of an upper class precedes every
   member of the next class.

An ordinal obtained by enumerating the currently occupied banzuke is instead
relative to that particular roster. It can change when a rikishi retires or an
extra sanyaku position is created even though another rikishi's own chii has
not changed.

One can avoid that movement by inventing fixed blocks, maximum class sizes,
shrinking within-class intervals or other coordinate conventions. Those are
features of a new model, not meanings supplied by chii.

## A numerical chii model is underdetermined

It is possible to construct a class-structured chii model. For example, one
might assign a unit difference within a class and additional offsets at the
Yokozuna--Ozeki, Ozeki--lower-sanyaku and divisional boundaries. Such a model
would be an interpretation of what the classes mean, not a direct reading of
the banzuke.

The JSA system does not determine the offsets, within-class slopes or even the
appropriate common unit. Many incompatible numerical models could preserve the
same conventional ordering. The intended use of the model would have to decide
how these parameters were chosen:

- If they were tuned to reproduce JSA decisions, the model would describe JSA
  decision-making rather than independently measure strength.
- If they were tuned until the resulting rankings looked intuitively right,
  the model would risk encoding the modeller's preferred conclusions through
  magic numbers.
- If they were estimated from their ability to predict bouts, the result would
  be an outcome-calibrated interpretation of chii. Chii would supply the
  categories, while recorded outcomes and the chosen statistical specification
  would constrain their numerical placement.

The third is a legitimate predictive model, but it answers how much predictive
information chii carry. It does not discover an intended JSA cardinal scale,
and there may be no such scale to discover.

## Circularity as a validation problem

Chii can inform an entrant prior or another policy in an Elo-like system. When
they do, agreement between the resulting ratings and chii is partly built into
the construction. It cannot serve as independent validation of either system.

Earlier work sometimes treated failure to reproduce chii as a problem for Elo
that required explanation. That framing places Elo in the dock while leaving
the institutional system unexamined. A disagreement may instead arise because
the systems use different time horizons, preserve different information or
answer different questions.

Chii should therefore not be treated as a perfect target, and an Elo-like model
should not be adjusted merely until it produces the expected banzuke shape.

## What can be investigated about chii

Rejecting chii as a cardinal strength scale does not prevent empirical study of
the labels. Treating each class or chii as a category permits questions such as:

- What results tend to precede entry into a class?
- What subsequent win and tournament-score distributions do its occupants
  have?
- How long do rikishi remain there, and where do they move next?
- How does a class perform against each other class?
- Does class or within-division position add predictive information?
- Is Sekiwake empirically distinguishable from Komusubi as a strength class?
- Where does the conventional ordering imply probable superiority, and where
  does it not?

For example, the limited proposition that Yokozuna are "mostly greater" than
Ozeki might be expressed as a probability of victory in contemporaneous Y--O
bouts, a comparison after standardising over a common opponent population, or
a comparison of subsequent performance distributions. These are different,
testable claims. None requires every Yokozuna to be stronger than every Ozeki
or requires Y and O to have fixed scalar values.

## From the critique of chii to model choice

The inadequacy of chii as a cardinal strength scale does not establish that an
Elo-like system is the answer. The next question must be asked without assuming
its conclusion:

> If chii are not an adequate formal measure, what properties should a
> statistical model of sumo strength have?

Only after stating those properties should candidate model families be
considered. The purpose of the discussion below is to put the project's choice
to investigate Elo-like systems in context. It does not pronounce Elo the best
possible model or claim that non-Elo alternatives have been ruled out.

## What a statistical strength model should do

A workable operational definition is:

> A rikishi's strength at time \(t\) is the information-supported capacity to
> win a bout against specified opponents under the conditions represented by
> the data.

This is narrower than greatness, achievement, institutional standing or worth.
A model of this particular notion of strength should have the following
properties.

1. **Outcome-grounded.** Its estimates should ultimately be constrained by
   recorded bouts, not by whether its rankings look plausible or agree with
   chii.
2. **Probabilistic.** It should estimate uncertain outcomes rather than assert
   that the stronger rikishi must win. An upset must be compatible with the
   model.
3. **Comparative.** Results should be interpreted in relation to the opponents
   faced. Raw win percentages are insufficient when schedules differ.
4. **Time-indexed.** Strength can change. The model should make explicit how
   older evidence persists, decays or is displaced by later evidence.
5. **Chronologically honest.** An estimate or prediction at time \(t\) may use
   only the information available before \(t\).
6. **Applicable to an open population.** The system must address entry,
   retirement, absence, return and movement among incompletely connected
   populations.
7. **Explicit about scale and anchoring.** Relative strength may be identifiable
   when an absolute rating level is not. Comparisons across distant times need
   additional justification.
8. **Aware of evidential support.** An estimate based on five recorded bouts
   should not silently acquire the same status as one based on hundreds.
   Preferably the model should quantify uncertainty.
9. **Schedule-aware.** Torikumi are not random. Claims should remain within the
   matchup populations supported by the observed schedule unless further
   assumptions are defended.
10. **Structurally falsifiable.** Evidence must be allowed to count against such
    assumptions as a single scalar strength, a universal probability curve or
    common responsiveness for every rikishi.
11. **Empirically testable.** The model should make forecasts that can be tested
    for calibration and predictive loss on genuinely later, untouched bouts.
12. **Reproducible and robust.** Its data rules, parameters and versions should
    be explicit, and consequential sensitivity to reasonable alternatives
    should be reported.

A broad mathematical form is:

\[
P(i\text{ beats }j\text{ at }t)
=g\bigl(s_i(t)-s_j(t),x_{ijt}\bigr),
\]

where \(s_i(t)\) is time-varying latent strength, \(g\) maps comparative
strength to probability, and \(x_{ijt}\) represents any separately justified
matchup or contextual information. A complete model also needs a rule for how
strength changes through time.

## Possible model families

Several kinds of model might address some or all of these requirements:

- opponent-adjusted win statistics;
- Bradley--Terry and related paired-comparison models;
- sequential Elo-like rating systems;
- uncertainty-aware systems such as Glicko and Glicko-2;
- TrueSkill-like systems;
- dynamic or Bayesian latent-strength models; and
- richer models containing justified context or matchup interactions.

This is not intended as an exhaustive literature review. It establishes only
that an Elo-like system is one candidate family among several.

## Why begin with an Elo-like system?

An Elo-like system is a natural first candidate because it provides a relatively
simple and transparent way to turn pairwise results into changing comparative
ratings and estimated probabilities. It is outcome-grounded, opponent-adjusted,
probabilistic, sequential and capable of making claims that later results can
contradict.

There is also an informal but relevant external precedent. Arpad Elo was a
physicist who taught physics at Marquette University. The United States Chess
Federation first implemented his system in 1960, and FIDE adopted it for
international chess ratings in 1970. FIDE continues to operate an evolved Elo
rating system. See FIDE's
[account of Elo and adoption](https://www.fide.com/anniversary-of-arpad-elo-rating-system-that-changed-chess-world/)
and its account of
[subsequent rating changes](https://www.fide.com/fide-seeks-public-discussion-about-proposed-rating-changes/).

The system was therefore not developed at FIDE's request, and Elo was not a
professor of mathematics. The relevant point is the weaker one: a system
developed by a quantitatively trained chess expert has survived long-term use
by the world governing body of a major pairwise competitive activity.

Sumo is sufficiently similar to chess to make this precedent worth taking
seriously. Both present repeated pairwise contests in which a changing but
unobserved capacity is inferred from results. The analogy is not proof. Sumo
has no ordinary draws, has a highly structured and selectively formed schedule,
short tournaments, injury and absence problems, promotion institutions and a
changing divisional population. FIDE's continued use therefore supplies a
reasonable prior reason to investigate Elo, not evidence that the same model
must work for sumo. In informal terms, either Elo is a promising place to start
or FIDE has made a very durable mistake; the statistical work must decide what
the precedent is worth here.

The repository already contains extensive work on Elo-like systems. That is
also a legitimate practical reason to continue the investigation. A research
programme does not have to compare every conceivable family before developing
one plausible candidate thoroughly.

## What "Elo-like" means here

There is no single model called *Elo* whose suitability has already been
settled. The discussion should distinguish:

1. **The Elo-like idea:** infer comparative strength from pairwise outcomes and
   turn rating differences into expected results or winning probabilities.
2. **A specified model:** choose exact rules for probability scale, updating,
   initialisation, eligible bouts, population treatment and every other policy.
3. **The current candidate:** Elo-89, which combines one particular set of those
   choices.

The first is a promising framework. Most of the difficult research questions
occur in moving from the first to the second. The third is the project's current
candidate rather than a settled conclusion.

## Strengths of Elo-like systems

Relative to chii as a proposed formal strength scale, an Elo-like system has
several important advantages:

- its central quantity has an explicit comparative interpretation;
- it derives changes from bout outcomes;
- it adjusts a result according to the opponent's estimated strength;
- it produces probabilistic claims rather than categorical certainties;
- it operates sequentially without requiring the final historical ordering;
- its predictions can be scored and tested for calibration;
- its assumptions, parameters and model versions can be published;
- disagreement with expectation need not be repaired merely to preserve an
  institutional ordering; and
- it can fail in observable ways.

The relevant advantage is not freedom from tuning. It is the possibility of
constraining tuning by a declared empirical claim. If the model concerns
bout-winning capacity, its probabilities can be tested on later bouts against
simple and relevant alternatives.

## Recurring weaknesses of Elo-like systems

The same family also has substantial weaknesses and unresolved assumptions:

- a single scalar rating may not represent style interactions or non-transitive
  matchup relationships;
- the probability curve and its scale are model choices;
- the update rate controls a trade-off between responsiveness and noise;
- common initialisation creates an artificial early-career period;
- informed initialisation introduces additional assumptions and possible
  circularity;
- an ordinary point rating does not express uncertainty or amount of support;
- inactivity does not automatically weaken a rating or increase its
  uncertainty;
- fixed non-zero updates produce continuing fluctuation even in a stable world;
- entry and retirement can affect the population scale;
- incomplete historical results can distort ratings and comparisons;
- observed torikumi do not constitute a random sample of possible matchups;
- ratings relative to different populations or eras are not automatically
  comparable; and
- the many policies available to repair these issues create researcher degrees
  of freedom and opportunities for overfitting.

If parameters are chosen because ratings reproduce chii, place favoured
rikishi appropriately or otherwise look satisfactory, the same epistemic
problem identified in the critique of numerical chii models returns.

## What the model variants have and have not resolved

The variety of Elo-like models studied in this repository is evidence that the
framework leaves important matters unresolved. Each variant attempts to improve
one aspect of the model without necessarily improving the others:

- chii-informed or other entrant priors address the consequences of starting
  everyone at the same rating;
- alternative update policies alter responsiveness;
- normalisation policies address population-level drift;
- historical extensions increase the available evidence; and
- population policies address entry and departure.

An improvement in one respect does not establish improvement overall. An
informed prior may reduce initialisation lag while importing future information
or stronger assumptions. Normalisation may stabilize an aggregate scale while
changing predictive behaviour. Greater responsiveness may reduce lag while
increasing noise.

Elo-89 is the current candidate produced by the investigations undertaken so
far. It incorporates several individually motivated responses to known
weaknesses and has survived the comparisons so far applied. That does not yet
amount to a complete justification for its exact combination of policies. The
reasons for selecting the candidate family, the trade-offs among its parts, its
robustness and its remaining weaknesses must still be presented together.

There is a difference between showing that Elo-89 led a bounded comparison and
showing that it is a good model of sumo strength. Nothing has been resolved
merely by giving the current candidate a name.

## Glicko-like systems as a natural extension

If Elo-89 or a similar system proves to be a credible point-rating model, a
Glicko-like extension is an obvious subsequent investigation. New entrants,
sparse records, absences and returning rikishi make differing levels of
uncertainty especially relevant to sumo.

Glicko is conceptually close to Elo, but it does more than report additional
metrics beside an otherwise unchanged rating. Rating deviation participates in
the calculation of rating updates; Glicko-2 additionally models volatility.
See Mark Glickman's specifications for
[Glicko](https://www.glicko.net/glicko/glicko.pdf) and
[Glicko-2](https://www.glicko.net/glicko/glicko2.pdf).

A post-hoc uncertainty statistic attached to an unchanged Elo calculation would
be a simpler extension. A Glicko-like system instead retains the broad
paired-comparison idea while changing the update model so that evidential
uncertainty affects ratings.

This is a point in favour of beginning within the Elo family: substantial
research already exists on a natural route beyond bare point ratings. It is not
an automatic reason to adopt Glicko. Rating periods, initial uncertainty,
uncertainty growth, volatility and the treatment of absences would introduce
new modelling choices. Additional complexity should have to demonstrate a
relevant improvement under the same frozen evaluation protocol.

## Why not begin with a non-Elo model?

The immediate answer is a statement of research scope: the project has not
finished investigating Elo-like systems. This is not evidence that a non-Elo
model would be inferior.

The honest position is:

> The project is investigating whether an Elo-like system can provide a
> satisfactory account of bout-winning strength. It has not exhausted that
> investigation and therefore does not yet need to select among fundamentally
> different model families. This restriction of scope is not a claim that
> Elo-like models are uniquely appropriate or ultimately optimal.

If the common structural assumptions of the Elo family fail, or if another
family later offers a relevant and demonstrable improvement, the model choice
should be reopened. "We have to start somewhere" justifies an order of
investigation, not the final answer.

## Conclusion

Chii are an informative but informal and structurally heterogeneous account of
competitive standing. Their conventional ordering is useful, but it supplies
neither stable distances nor a uniform interpretation across statuses, classes
and divisions. Turning the complete chii system into a cardinal strength scale
would require numerous assumptions that are not determined by the banzuke
itself.

The appropriate next step is to state what a formal statistical model of
strength should do and then assess candidate families against those
requirements. Elo-like systems satisfy many of the requirements, provide a
tractable and historically established starting point, and possess a developed
path towards uncertainty-aware extensions. They also contain serious recurring
weaknesses and numerous tunable policy choices.

The project's choice is therefore to investigate Elo-like systems, not to
pronounce Elo the uniquely correct approach. Elo-89 is the current candidate,
not a completed proof of model quality. Chii remain valuable as institutional
context, evidence, a possible predictor and an independent object of
comparison, but not as the definition of strength or the ground truth of the
rating model.
