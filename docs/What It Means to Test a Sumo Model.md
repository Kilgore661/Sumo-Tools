# What It Means to Test a Sumo Model

## Status

Draft introductory account of the standards by which a probabilistic model of
sumo bout outcomes should be understood and judged.

This document begins with an explanation intended for a general reader. The
second section examines what that explanation implies about probability and
prediction. The final section locates the approach more explicitly within
statistical modelling and the philosophy of science.

---

# 1. The practical idea

## What is the model trying to do?

A model of sumo bouts does not have to claim that it has discovered the true
and complete measure of every rikishi. Its more modest task is to use specified
information available before a bout to estimate the chance of each possible
outcome.

For example, a model might say that rikishi A has a 75 per cent chance of
defeating rikishi B. This does not mean that A possesses 75 per cent
"winningness", that A is three times as good as B, or that B cannot win. It
means that, given the information and assumptions built into this particular
model, A is assigned a probability of 0.75 of winning this particular bout.

This distinction matters because words such as *good*, *strong* and *deserving*
can hide several different questions. A model might attempt to estimate:

- the probability of winning the next bout;
- performance across a particular period;
- career achievement;
- present ability after accounting for the strength of opposition;
- future potential.

These are not interchangeable. A model designed to answer one of them should
not be rejected merely because somebody wanted the answer to another. Before
any calculation begins, the target must therefore be stated clearly enough for
the result to be tested.

## An unexpected winner does not disprove a probability

If the wrestler assigned a 25 per cent chance wins, the model has not thereby
contradicted itself. It said that the result was possible but relatively
unlikely. Indeed, if competitors given a 25 per cent chance never won, the
probabilities would deserve suspicion.

Nor does one successful prediction establish that the model works. A model
which assigns 51 per cent to every eventual winner would look excellent if its
predictions were inspected only after the results were known. The serious
question is how its forecasts behave across many bouts whose outcomes were not
available when the forecasts were made.

Individual bouts remain useful evidence, especially when they reveal missing
data or an implausible assumption. They are not, on their own, decisive tests
of a probabilistic claim. The appropriate unit of assessment is a sufficiently
large and genuinely unseen collection of bouts.

## Reputation is not a test result

A model will sometimes rate a popular or accomplished rikishi less highly than
supporters expect. That disagreement should neither be dismissed nor treated
as an automatic failure.

It may mean that:

- the supporter and the model are using different meanings of "good";
- the supporter knows something that is absent from the data;
- recent injury, recovery or changing form is poorly represented;
- the estimate is uncertain because the relevant evidence is limited;
- the model is systematically wrong;
- the model is reasonable and this is simply one surprising case.

The disagreement becomes scientifically useful when it is turned into a claim
that can be examined. If a proposed missing feature really matters, adding it
should improve predictions on later, unseen bouts. A feature should not be
added merely because it moves a favoured rikishi towards a preferred position.
Otherwise the model becomes a complicated way of reproducing the modeller's
prior opinions.

## A careful test

Historical data make it easy to construct a model which explains history.
Enough adjustable choices can accommodate not only persistent relationships
but also accidents peculiar to the sample. The result may look persuasive
while having learned little that survives beyond the data from which it was
built.

A careful study therefore separates the available history by time:

```text
earlier bouts        later bouts             final untouched bouts
     |                    |                            |
     v                    v                            v
construct the model   make justified choices   estimate future performance
```

The earlier bouts may be used to estimate the model. A later validation period
may be used to compare reasonable alternatives and settle modelling choices.
A final test period should remain untouched until those choices, including
data preparation, have been frozen.

This chronological ordering matters. Randomly distributing individual bouts
between training and test sets can allow information from the same tournament,
or from a later stage of a rikishi's career, to help predict an earlier event.
That is not the situation the model will face when making a real forecast.

Once the final test results have been examined, changing the model in response
is legitimate model development, but it changes the status of those results.
The former test period has become part of the development evidence. A fresh
period is required for a new final test.

## What success looks like

A useful model should be judged against explicit alternatives, including
simple ones. Depending on the question, these might include an equal chance for
each rikishi, always choosing the higher-ranked rikishi, or predictions from a
basic Elo model. Complexity earns its place only if it produces a relevant
improvement.

Two qualities are particularly important:

- **Calibration:** Among bouts assigned probabilities near 25 per cent, the
  nominated rikishi should win approximately 25 per cent of the time, allowing
  for ordinary sampling variation.
- **Discrimination:** The model should usually assign higher probabilities to
  winners than to losers and distinguish relatively favourable contests from
  relatively unfavourable ones.

Proper scoring rules such as log loss and the Brier score can assess the whole
probability forecast rather than only whether the favourite won. Results should
also be accompanied by uncertainty and examined across time periods and
relevant groups. A single aggregate score can conceal a model that works well
for established top-division rikishi but poorly for newcomers, returning
rikishi or sparsely observed competitors.

No finite test proves that a model is permanently correct. It provides evidence
about how the model performed on specified data under specified conditions.
That is a limited claim, but it is a claim that can be reproduced, criticised
and improved.

---

# 2. What the practical idea implies

## Probability is conditional on information

The probability produced by a model is better written as

\[
P(\text{A defeats B}\mid I,M),
\]

where \(I\) is the information available to the modeller and \(M\) represents
the model and its assumptions. Writing the conditions explicitly prevents the
forecast from being mistaken for an intrinsic property of a rikishi.

Another observer may possess different information or adopt different
defensible assumptions and therefore assign a different probability. That does
not make every probability equally defensible. The information may be
inaccurate, the assumptions incoherent or the resulting forecasts demonstrably
poor. Conditional does not mean arbitrary.

The information boundary must also be temporal. A genuine pre-bout estimate
may use only information that could have been known before the bout. Rankings,
injury reports, later tournament results and retrospective data corrections
must be treated according to when they became available, not merely according
to whether they appear somewhere in the completed dataset.

## Determinism and predictability are different questions

Sumo may be physically deterministic. Given the complete state of both
wrestlers and their environment, together with the laws governing that state,
perhaps only one outcome is possible. Even so, the outcome can remain
unpredictable to us. We cannot measure every relevant feature, and small
unobserved differences may have large consequences during a bout.

If sumo is deterministic, a hypothetical observer with complete physical
information and unlimited computational ability would assign the outcome a
probability of either zero or one. Intermediate probabilities would express
our incomplete knowledge of which fully specified state is present.

If the physical process contains irreducible indeterminacy, even an ideally
informed observer might assign an intermediate probability. The practical
analysis does not require us to decide between these positions. For an actual
modeller, probability represents uncertainty conditional on necessarily
limited information. That uncertainty may arise entirely from ignorance of a
deterministic process, or it may also reflect objective chance.

Thus a deterministic world need not produce deterministic forecasts. Among
bouts which appear similar at the resolution of the model are many different
underlying states. A calibrated probability describes the outcomes observed
across that partially observed class, even if every individual outcome was
fixed by its complete state.

## Three ways a forecast can appear to fail

It is helpful to distinguish three different phenomena:

1. **Outcome surprise.** An event assigned a low probability occurs. This is
   expected sometimes and is not by itself a defect.
2. **Estimation error.** Limited or noisy evidence makes the estimated
   probability differ from the best estimate that the chosen model could have
   produced with more information.
3. **Model error.** The model's representation or assumptions systematically
   fail to describe relationships needed for useful forecasts.

Only the third is straightforwardly a failure of the model as a model, although
the second may expose a poor estimation procedure or an overly ambitious use
of sparse data. Repeated surprises of the same kind can be evidence of either.
This is why calibration, scoring rules, subgroup analysis and comparison with
alternatives matter more than anecdotes.

## Models answer constructed questions

The outcome of a bout is observed, but the quantity called *strength* usually
is not. It is introduced by a model as a way of organising results. Its meaning
depends on the target, the selected observations, the treatment of time, the
opponents encountered and the mathematical structure imposed upon them.

This does not make a strength estimate useless or fictional in the everyday
sense. It means that the estimate should not silently acquire a stronger claim
than its construction supports. Two models can organise the same bouts in
different ways and both make useful predictions. Conversely, two models can
produce similar rankings while attaching quite different meanings to their
numbers.

The modeller should therefore expose the route from observation to claim:

```text
recorded bouts
  -> selected information and target
  -> modelling assumptions
  -> estimated ratings or probabilities
  -> predictions on unseen bouts
  -> empirical assessment
```

Every arrow is a choice or inference which can be examined. None is made
infallible by expressing its result numerically.

## Success is provisional

Out-of-sample performance is evidence of generalisation, not proof that the
model has discovered an eternal structure. Sumo changes: rikishi enter and
retire, training and medical practice develop, regulations and tournament
conditions may alter, and the observed population moves through different
eras. A relationship may be genuine yet temporary.

This is one form of the problem of induction. Past success gives a reason to
trust a forecasting procedure under sufficiently similar future conditions,
but it cannot guarantee that those conditions will continue. Monitoring later
performance is therefore part of the model's evidential life, not an admission
that its earlier tests were pointless.

---

# 3. Statistical and philosophical position

## Bayesian method and Bayesian interpretation

Bayes' theorem is a mathematical relationship and does not, by itself, settle
the meaning of probability. It can be used without adopting a general
philosophy of science.

The interpretation adopted here is more specific. In a subjectivist Bayesian
account, a probability represents a degree of belief warranted by an agent's
information and assumptions. Evidence changes that degree of belief through
Bayesian conditionalisation. On this view, a probability of 0.25 is not a
physical quantity residing in a rikishi or on the dohyo. It describes the
modeller's uncertainty about the outcome.

Calling the probability subjective does not mean that it is a matter of taste.
Credences are constrained by consistency, by the quality of the evidence, and
by their empirical consequences. Forecasts can be compared using proper
scoring rules and tested for calibration. A modeller cannot rescue consistently
poor predictions merely by declaring them personal beliefs.

Nor does epistemic Bayesianism require a commitment to either physical
determinism or physical indeterminism. The same calculus can represent
uncertainty about a hidden deterministic state or uncertainty which includes
irreducible chance.

## The extent of the anti-realism

Subjective Bayesianism is anti-realist about probabilities in a particular
sense: the numerical probability is treated as a feature of an informed
agent's epistemic position, not as a freestanding physical property of the
bout. That does not entail anti-realism about everything described by science.
A person may regard injuries, forces, intentions and other causal mechanisms
as real while treating probabilities as degrees of belief about them.

The broader attitude taken here is sympathetic to **constructive empiricism**.
The model seeks empirical adequacy: it should organise observed results and
make successful, testable predictions. It is not offered as a literally true
account of every observable and unobservable mechanism producing a bout.

These are related but distinct commitments:

- subjectivist Bayesianism concerns what the probabilities mean;
- constructive empiricism concerns what success licenses us to claim for the
  model as a scientific account.

The second is not a logical consequence of the first. It is an additional act
of epistemic restraint.

## Prediction, explanation and reality

A successful forecasting model need not identify the true causes of victory.
It may exploit a stable observable relationship while representing its causal
origin incompletely or not at all. Conversely, a plausible causal story does
not establish that the associated model predicts well.

This study therefore separates three questions:

1. Does the procedure produce reproducible estimates from the stated data?
2. Do those estimates support useful forecasts of unseen bouts?
3. Do the model's internal quantities correspond to real causal properties of
   rikishi and contests?

The first two can be investigated without settling the third. Good performance
is compatible with several rival explanations, while poor performance may
arise from the data, the estimation procedure, the model assumptions or a
change in the environment. Evidence bears upon the whole construction rather
than isolating one assumption automatically.

This does not make the model unfalsifiable. It makes falsification a matter of
disciplined diagnosis rather than a single dramatic counterexample. The target,
information boundary, evaluation rule and competing baselines should be stated
in advance so that failure cannot always be explained away after the event.

## What kind of study is this?

An analysis of recorded sumo bouts is not a controlled experiment: competitors
and conditions have not been randomly assigned by the modeller. It is an
observational predictive study which can contain carefully controlled
computational experiments.

Its rigour comes from explicit boundaries rather than laboratory control:

- the outcome and target are defined;
- the admissible pre-bout information is stated;
- development and evaluation periods are separated chronologically;
- alternative models and simple baselines are compared;
- evaluation criteria are fixed before the final results are inspected;
- uncertainty, limitations and changes of specification are reported;
- claims are restricted to what the evidence can support.

The aim is neither to turn sumo into a deterministic table nor to shelter every
error beneath the word *probability*. It is to make limited claims under
uncertainty, expose the assumptions behind them, and allow experience to count
for or against them.

## Conclusion

A mathematical model of sumo is not an oracle and not a numerical form of
reputation. It is a specified transformation from limited evidence to claims
about uncertain outcomes. Its probabilities should be read conditionally, its
ratings should be interpreted according to their construction, and its success
should be judged on genuinely unseen bouts rather than memorable examples.

This remains true whether the underlying contests are deterministic,
indeterministic or some combination that the analysis cannot distinguish. The
model earns confidence not by claiming access to hidden truth, but by making
clear commitments and surviving serious attempts to test them.
