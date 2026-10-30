# 3. What is a Rating System?

> **Draft status:** First continuous-prose draft. It proposes a working
> definition for this account and identifies where the interpretation of
> Elo-89 remains conditional rather than settled.

## A working definition

A rating system is a model which turns selected evidence about a set of
subjects into comparable numerical states for a declared purpose.

Each number is a **rating**. It is not simply another observation about its
subject. It is a coordinate inside the model: a compact estimate constructed
from observations according to the model's assumptions and rules. Its meaning
comes from what the model says can legitimately be done with it.

That definition is intentionally broad. A rating system may be designed to
order competitors, summarise past performance, compare them at a particular
time, track change or help forecast later contests. Some systems serve several
of these purposes. Prediction is especially important when a model explicitly
turns rating differences into probabilities, as Elo does, but predictive
success is not the definition of every possible rating system.

A complete account therefore has at least five parts:

```text
selected observations
    -> assumptions about the process which produced them
    -> estimated numerical states
    -> rules for interpreting or using those states
    -> evidence about whether those uses succeed
```

The calculation alone is not the whole system. Without the intended
interpretation and the grounds on which it can be assessed, a precisely
computed number may still be conceptually empty.

## Observation, statistic, ranking, rating and forecast

Several related objects are easily called “ratings” in casual discussion. It
helps to separate them.

| Object | What it does | Sumo example |
| --- | --- | --- |
| **Observation** | Records an event or attribute | A defeated B on day 6; A was M3e |
| **Count** | Totals selected observations | A recorded 47 credited wins |
| **Descriptive statistic** | Summarises observations under a stated rule | A won 63% of counted bouts |
| **Ranking or ordering** | Says who or what comes before whom | A appears above B on a list |
| **Rating** | Places a subject at a numerical coordinate inside a model | A's current model state is 2,214 |
| **Forecast** | Assigns an uncertain future outcome using available information | The model gives A a 64% chance against B |

These categories can overlap in use without becoming identical. Sorting a set
of ratings produces a ranking, but the ranking discards the sizes of the
differences. A rating model may generate a forecast, but the forecast also
requires an outcome rule which says what a difference means. A win percentage
is numerical and comparable, but it remains a descriptive statistic unless it
is made a state in a wider model with a declared interpretation.

The distinction is not a contest over which object is most sophisticated. A
count may answer its question exactly. The point is that each object answers a
different question, and calling all of them “strength” does not make those
questions the same.

## A rating is a coordinate, not a substance

Suppose a rikishi has an Elo-89 rating of 2,214. Nothing measurable inside his
body or technique has the value 2,214. The rating locates him on the scale
constructed by this model after it has processed the represented evidence.

The coordinate is useful because of its relations to other coordinates. In an
Elo-like model, the difference between two ratings is mapped to an expected
result or win probability. Adding the same constant to every contemporaneous
rating leaves those differences and probabilities unchanged. This shows that
the individual absolute number is not the fundamental competitive claim. It
is a convenient coordinate from which the model's pairwise claims can be
formed.

This does not make ratings fictional or arbitrary. Latitude is also a
coordinate, and a temperature scale depends on conventions. A coordinate is
useful when its construction is coherent, its interpretation is clear and the
relationships it expresses are supported for the intended use. The danger is
allowing the convenience and precision of the coordinate to suggest that the
model has directly observed the real-world property it was designed to
represent.

## Every rating system contains a model

A model is a selective representation. It retains some features of the world,
omits others, and asserts relationships among those it retains. For a sumo
rating system, decisions are required about at least the following:

- **target:** the aspect of performance or ability the ratings are intended to
  represent;
- **evidence:** which bouts, outcomes, ranks, dates or other information are
  admitted;
- **competitor state:** whether one number per rikishi is sufficient and what
  that number means;
- **opposition:** how the identity or estimated level of an opponent affects
  the interpretation of a result;
- **time:** how quickly new evidence changes the state and how old evidence
  persists;
- **population:** how entry, departure, absence, return, divisions and weakly
  connected groups are handled;
- **outcome:** how states become expectations or probabilities;
- **uncertainty:** whether the amount and quality of supporting evidence are
  represented; and
- **observation point:** when the state is recorded for publication or
  comparison.

Even the simplest rating system answers these questions somehow. Leaving an
issue implicit does not leave the model neutral; it merely makes the answer
harder to inspect.

The system also need not reproduce the complete causes of winning. A useful
model can omit injury, style, tactics, psychology and physical detail while
still organising the represented outcomes successfully. But its claims must
remain commensurate with that abstraction. One scalar rating cannot silently
become a complete account of a rikishi.

## What is the target in this project?

Terms such as *strength*, *form*, *performance*, *achievement* and *greatness*
are not interchangeable.

Greatness might include championships, rank attained, longevity, dominance
and cultural significance. Achievement concerns what happened, not simply the
capacity inferred from it. Form often suggests short-term condition.
Performance may refer either to realised results or to an inferred level after
allowing for opposition. None of these meanings is fixed merely by choosing a
formula.

The narrowest defensible target for the present project is comparative
bout-winning capacity under the conditions represented by the data. A useful
working formulation is:

> A rikishi's competitive strength at time *t* is his
> information-supported capacity to win a bout against specified opponents,
> under the conditions represented by the available evidence.

This formulation is deliberately conditional. “Against specified opponents”
prevents strength from being treated as a free-standing quantity independent
of the comparison population. “At time *t*” allows competitive capacity to
change. “Information-supported” distinguishes an estimate from hidden true
ability. “Conditions represented by the evidence” limits the claim to what
the model can see.

Even this is not a completed empirical finding about Elo-89. Elo-89 makes a
more exact internal assertion: at a given observation point, a specified
rating difference maps to a specified model win probability. Whether those
probabilities are well supported, and whether the one-dimensional state
deserves the broader interpretation “competitive strength”, must be examined
rather than assumed.

## What makes a rating system good?

There is no context-free answer. A system is good relative to its stated
purpose, population and conditions of use. A model intended to seed a
tournament might properly be judged differently from one intended to compare
careers or forecast tomorrow's bouts.

For this project, the relevant standards fall into four groups.

### 1. Definition and internal coherence

The target, admissible evidence, population, state transitions and observation
points should be exact. The stated interpretation of a difference must follow
from the mathematics. Exceptional cases should have specified behaviour, and
the same input under the same model version should produce the same result.

These are minimum requirements for a well-defined system. They do not show
that the system represents sumo well.

### 2. Fitness of the representation

The structure should be plausible for the declared target. For the working
notion of competitive strength, that means taking account of opposition,
change through time and an open population. It also means treating
probabilities as uncertain claims and recognising that schedules are selective
rather than a random sample of every possible matchup.

Structural assumptions must remain open to challenge. One scalar per rikishi,
a universal probability curve and fixed update policies are hypotheses or
design commitments, not truths secured by notation.

### 3. Empirical adequacy

Where the system makes probabilistic claims, later results can test them. A
useful forecasting model should discriminate favourable from unfavourable
matchups and should be calibrated: events assigned a probability should occur
at approximately that long-run frequency. Proper scoring rules can compare
the complete forecasts with simple baselines and alternative models.

Evaluation must respect time. A pre-bout state may use only information that
would have been available before the bout. Performance should be examined not
only in aggregate but across relevant periods and populations, especially
where entrants, returning rikishi or sparse records may behave differently.
Sensitivity to reasonable modelling alternatives should also be reported.

Prediction is powerful evidence because the claim can be contradicted by new
outcomes. It is not, by itself, proof that the rating is the true cause or
complete measure of winning.

### 4. Fitness for human use

The scale should be interpretable enough for its intended users, and its
limitations should travel with its outputs. A rating based on little evidence
should not silently acquire the same authority as a mature estimate. Historical
comparisons should not be asserted merely because numbers from two dates share
the same printed scale. Added complexity should earn its place through a
declared benefit.

These standards can conflict. A highly responsive system may track change
quickly but fluctuate with ordinary noise. A stable system may lag genuine
change. A richer model may represent more of sumo while becoming harder to
estimate, explain and test. There is rarely one design which maximises every
desirable property.

## What does not make a system good?

A rating model is not validated merely because it:

- places famous champions at the top;
- usually agrees with the banzuke;
- moves winners upward and losers downward;
- produces a plausible-looking historical chart;
- is complicated or mathematically precise; or
- defeats one deliberately weak comparator.

Any of these may be a useful diagnostic. None is a sufficient account of
validity. If a feature is added because it moves a favoured rikishi, rank or
era towards an expected position, preference can enter the model under the
appearance of improved measurement.

This is why purpose must precede optimisation. A modelling choice can be
supported by an independently stated requirement, an empirical comparison or
a demonstrated data problem. It should not be justified only by liking the
ranking it produces.

## The question carried forward

We can now say what is being proposed. Elo-89 is not simply a table of sums and
not an automated banzuke. It is a particular one-dimensional, time-indexed
model whose numerical states support opponent-relative comparisons and
probabilities. Its rules can be made explicit and its forecasts can be tested.
Whether it is a *good* model depends on how well those rules serve the bounded
purpose above and on what the evidence establishes.

This definition does not yet explain why we should prefer a model of this kind
to an apparently simpler summary of results. Before turning to Elo, we should
take those simpler possibilities seriously. What, for example, would it mean
to rate rikishi by the wins accumulated over the last six basho?

That is the subject of the next chapter.

## Working sources

- `../../analysis/docs/story/02 Narrative and Validation Structure.md`
- `../../analysis/docs/2026 09 11 Strength, Purpose and Model Bias - Lab Note.md`
- `../../analysis/docs/2026 09 26 Chii and the Measurement of Strength.md`
- `../../../docs/What It Means to Test a Sumo Model.md`
