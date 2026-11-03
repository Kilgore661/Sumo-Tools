# 13. Other Choices Are Possible

## A chosen model is not the only possible model

Elo-89 is one explicit answer to questions which the results do not answer
automatically. It chooses bout-winning capacity as the target, represents that
capacity by one changing scalar, updates it through an Elo residual, assigns
first ratings from chii, varies responsiveness by division and anchors an open
population with common shifts.

Other investigators may reasonably choose differently. That does not make
every choice equally good or the evidence irrelevant. A useful alternative
must say what it is trying to measure, define how observations produce its
output, expose its assumptions and permit results to count against it.

The alternative is not “subjective opinion” on one side and “the objective
Elo-89 answer” on the other. Elo-89 itself embodies purposes and judgements.
The scientific advantage of an explicit model is that those commitments can
be inspected and compared.

## Begin by changing the question deliberately

Several quantities can all be interesting without being interchangeable:

- **recent achievement**: wins accumulated over a declared window;
- **success rate**: wins per represented bout;
- **basho production**: credited wins per tournament appearance;
- **official standing**: position and status on the banzuke;
- **current bout-winning capacity**: estimated probability against specified
  opponents at a specified time;
- **sustained dominance**: performance maintained over a longer interval;
- **career greatness**: a declared combination of peak, duration, achievement
  and opposition; and
- **historical relative standing**: comparison within or across changing eras
  under a stated anchor.

A rolling win table may be an excellent answer to the first question and a
poor answer to the fifth. A peak Elo rating can answer one definition of peak
strength without settling career greatness. The banzuke can be authoritative
for official standing without supplying cardinal distances between positions.

Before changing the algorithm, an alternative should complete the sentence:

> This system is intended to estimate or summarise ______, for ______, using
> ______ evidence, over ______ time and population boundaries.

Without that statement, disagreement about the numbers may really be
disagreement about the question.

## Simpler summaries remain legitimate alternatives

The discussion which led to Elo-89 began with apparently simple methods. They
remain useful when their limits are declared.

| Method | Coherent interpretation | Principal limitation |
| --- | --- | --- |
| Wins in the last \(n\) basho | Recent credited production over a fixed tournament window | Rikishi have unequal bout opportunities |
| Wins in the last \(m\) bouts | Recent success rate over an equal bout count | Calendar duration and opponent populations differ |
| Wins per basho | Production per tournament appearance | Definitions of appearance and absence matter |
| Wins per bout | Observed strike rate | Ignores unequal opposition unless extended |
| Follow the stronger chii | Use official ordering as the favourite | Chii gaps have no supplied probability geometry |
| Strength-of-schedule adjustment | Credit wins in relation to opposition | Requires its own weighting, iteration and time policy |

These are not failed attempts merely because they do not collapse into one
unique ranking. Their disagreements reveal that “performance” has multiple
dimensions and denominators. They can serve as independent views and as
baselines for more elaborate models.

The chii probe, for example, found that the stronger chii won 52.637% of
eligible unequal-chii bouts on its declared snapshot. That makes chii an
informative baseline. It does not supply a calibrated probability model or a
matched comparison showing whether its favourite wins more often than
Elo-89's.

## Alternatives within the Elo family

Many alternatives can retain Elo's expectation-and-update idea while changing
one or more policies.

### Expectation rule

Another system could choose a different \(q\), fit \(q\) by division or
rating maturity, use another monotone link, or add a contextual term where
sumo evidence supports one. Such a change alters the meaning of a rating gap
and must be evaluated as a new model, not merely a new display scale.

### Responsiveness

\(K\) could be constant, based on prior bout count, vary continuously with an
uncertainty estimate, respond to age or career stage, or be learned inside a
dynamic model. Every rule faces the trade-off between following real change
and chasing random results. An appealing career story is not a substitute for
later-bout evidence.

### Initialisation

First ratings could be equal, depend only on division, depend on chii, use a
contextual rank model, incorporate amateur or collegiate evidence, or begin as
a distribution rather than a point. A first-rating rule could be fixed once,
estimated using only earlier data at each forecast origin, or allowed to vary
by era.

Each answer changes both early forecasts and the information entering the
population. A table fitted from later outcomes can be useful for historical
reconstruction, but it must not be described as prospectively available at an
earlier date.

Elo-89 fixes P1-WL on 30 October 2026 using represented results through the
September 2026 basho. Alternative fitting boundaries can be evaluated
separately, but adopting one would revise the fitted artifact rather than
silently update it.

### Inactivity and uncertainty

A system could leave the point estimate unchanged when no eligible bout
occurs, widen uncertainty without moving the point, shrink an estimate toward
a reference distribution, or model time evolution explicitly. It could also
distinguish administrative statuses where the evidence supports doing so.

None of these policies follows automatically from non-appearance. The
direction, rate and trigger require specification. Elo-89 makes no individual
bout update without an eligible result and does not represent uncertainty
separately. Uncertainty growth, shrinkage and time evolution remain genuine
alternatives because they have not been tested in a comparable sumo model.

### Population and anchoring

The scale could be left floating, anchored by a fixed mean, tied to a reference
group, normalised within divisions, linked through bridge bouts, or estimated
in a model with explicit era effects. A common shift may preserve current
probabilities while still changing relationships with later first ratings.
Historical comparability must therefore be evaluated over the whole process,
not inferred from one invariance theorem.

### Uncertainty and additional state

Elo-89 is a point-rating model. A Glicko-like system maintaining both a point
estimate and an uncertainty coordinate is one possible alternative. Merely
reporting an evidential-support summary without changing updates would be a
different proposal. If uncertainty affects updating, the rating path itself
changes; if it is only reported, the Elo-89 calculation remains intact.

### Matchup structure

A richer system could add style, stable, handedness, injury or head-to-head
interaction terms. It should do so only with chronologically available data,
adequate repeated observations and protection against discovering memorable
patterns after the fact.

## Alternatives outside sequential Elo

The broader paired-comparison problem does not require an Elo recurrence.
Candidate families include:

- batch Bradley--Terry-style fits over declared windows;
- dynamic paired-comparison models with explicit latent evolution;
- Bayesian state-space models which carry distributions rather than points;
- uncertainty-aware constructions adapted to the pairwise setting;
- opponent-adjusted regression models; and
- ensembles combining distinct signals where the combination is fixed and
  evaluated honestly.

These names identify research directions, not completed alternatives in this
repository. Each introduces choices about time, regularisation, population,
missing evidence and interpretation. Greater sophistication does not
guarantee better measurement or forecasting.

Elo-89 has not been compared under a common protocol with a materially
different non-Elo family. It should not be described as having won such a
comparison.

## Which alternatives have actually been evaluated?

The status of an alternative matters.

| Question | Present status |
| --- | --- |
| Does a rating model contain information beyond a neutral 50--50 probability? | Directly scored retrospectively |
| Constant versus divisional \(K\) | Controlled retrospective comparison |
| Equal versus informed first ratings | Controlled retrospective comparison |
| No population adjustment versus whole-population preservation | Direct retrospective comparison with the first-rating input held fixed |
| P1-WL as a first-rating table | Evaluated retrospectively within its fitting history and through the complete Elo-89 calculation |
| Chii order as a favourite | Separate descriptive baseline, not a matched probability comparison |
| Comprehensive \(q\) or expectation-curve search | Not performed for the final contract |
| Uncertainty evolution during inactivity | Not evaluated comparatively |
| Uncertainty-aware Elo family | Not evaluated comparatively |
| Style or non-transitive interaction model | Not evaluated systematically |
| Dynamic Bayesian or another non-Elo family | Not evaluated |

This distinction prevents two symmetrical errors: dismissing Elo-89 because
an imagined alternative might be better, and defending it by implying that
every alternative has already lost.

## A fair comparison protocol

An alternative intended to replace or challenge Elo-89 should be tested under
a common protocol.

### 1. State the target

Define the real-world or operational claim. Is the output a probability for
the next represented bout, a descriptive historical score, an official-policy
aid or a measure of sustained achievement? Different targets need different
evaluation.

### 2. Freeze the complete contract

Specify evidence eligibility, identity, chronology, state, initialisation,
parameters, treatment of inactivity and uncertainty, population, anchoring and
observation stage. “Use Glicko” or “use recent form” is no more reproducible
than “use Elo”.

### 3. Preserve chronological honesty

A forecast at time \(t\) may use only information declared available before
that forecast. If later history is used to fit a retrospective artifact, say
so and do not call the result out-of-sample.

### 4. Compare on matched evidence

Models should forecast the same selected bouts from the same source-data
snapshot where their claims permit it. Bout identities, exclusions and the
input snapshot must be identified. A different dataset can answer a useful
question, but not a paired superiority claim without further work.

### 5. Use relevant baselines and proper scores

For probability models, include 50--50, a simple Elo baseline and the incumbent
Elo-89 where appropriate. Report log and Brier loss, calibration and
discrimination rather than winner accuracy alone. A deterministic favourite
rule and a probability forecast should not be compared through whichever
metric flatters one of them.

### 6. Examine populations concealed by the aggregate

Report rating maturity, division, cross-boundary, first-rating stage,
inactivity and historical-period subgroups fixed in advance where possible.
An aggregate gain should not conceal a practically important population
regression.

### 7. Quantify uncertainty and sensitivity

Use paired resampling or another appropriate method for score differences.
Vary reasonable modelling choices which were not identified by the data and
record whether the conclusion survives.

### 8. Preserve artifacts and failure

Save forecasts, parameters, source identities, implementation version and
evaluation outputs. Negative results are part of the research record. A model
should not be repeatedly adjusted until a preferred ranking appears and then
presented without its search history.

### 9. Obtain later evidence

After selection, freeze the model and score genuinely later results. A
rolling-origin design can supplement this where enough history exists, but it
must reconstruct every fitted component using only information then available.

## Improvement is multidimensional

A proposed alternative can be better in one sense and worse in another.

- Lower log loss may accompany worse calibration in a particular group.
- Faster response may increase rating noise.
- Better first-rating forecasts may use more institutional information.
- A stable historical scale may require a stronger anchoring assumption.
- Explicit uncertainty may improve honesty while making the model harder to
  explain and maintain.
- A richer matchup model may improve fit but overfit rare pairings.

The decision therefore needs a declared priority order and guardrails. Elo-89
used aggregate log loss as primary, Brier loss as corroboration and subgroup
calibration as a qualification. Another investigation may choose differently,
but it should choose before inspecting which rule produces the preferred
winner.

## When does an alternative need a new name?

A changed system needs a distinct model identity when it can alter admitted
evidence, forecasts, state updates, treatment of inactivity, population
operation or the meaning of the output. A new fitted table or source snapshot
also needs a distinct artifact or release identity even if the abstract model
contract remains the same.

Examples include:

- Elo-89 with a refitted P1-WL table: the same abstract first-rating rule with
  a new fitted artifact which must be identified;
- Elo-89 with an uncertainty coordinate: a different state model;
- Elo-89 with uncertainty-dependent \(K\): a different update model; and
- Elo-89 ratings rounded to integers: the same model with a presentation
  change, provided no rounded value is fed back into calculation.

Names should make important differences retrievable. They need not encode the
entire specification, but they must point unambiguously to it.

## An invitation, not a claim of finality

Elo-89 should be used because its bounded claim is useful and supported, not
because every alternative has been eliminated. Its contract and evidence make
disagreement productive: another investigator can replace one choice, hold
the others fixed and discover whether the result improves.

The most valuable alternatives will not be those which merely produce a more
agreeable all-time list. They will explain what new information or assumption
they add, predict where Elo-89 should fail, and survive a comparison in which
surprising results are allowed to stand.

The final position of this account is therefore:

> Elo-89 is the present explicit and testable point-rating account of modern
> sumo performance. It is neither a corrected banzuke nor the inevitable
> numerical meaning of strength. Glicko-like uncertainty, matchup structure,
> alternative responsiveness and the other models discussed here remain open
> subjects. They become advances when their purposes are clear, their
> contracts reproducible and their claims better supported by relevant
> evidence.
