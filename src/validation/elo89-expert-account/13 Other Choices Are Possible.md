# 13. Other Choices Are Possible

> **Draft status:** First continuous-prose draft. This chapter maps coherent
> alternatives and the conditions for comparing them. It is not a literature
> review and does not imply that untested alternatives are already superior.

## A chosen model is not the only possible model

Elo-89 is one explicit answer to a sequence of questions which the results do
not answer automatically. It chooses bout-winning capacity as the target,
represents that capacity by one changing scalar, updates it through an Elo
residual, initialises from chii, varies responsiveness by division and anchors
an open population with common shifts.

Other investigators may reasonably choose differently. That conclusion does
not make every choice equally good or the evidence irrelevant. A useful
alternative must say what it is trying to measure, define how observations
produce its output, expose its assumptions and permit results to count against
it.

The alternative is not “subjective opinion” on one side and “the objective
Elo-89 answer” on the other. Elo-89 itself embodies purposes and judgements.
The scientific advantage of an explicit model is that those commitments can
be inspected and compared.

## Begin by changing the question deliberately

Several quantities can all be interesting without being interchangeable:

- **recent achievement**: wins accumulated over a declared window;
- **success rate**: wins per represented bout;
- **basho production**: credited wins per tournament entered;
- **official standing**: position and status on the banzuke;
- **current bout-winning capacity**: estimated probability against specified
  opponents at a specified time;
- **sustained dominance**: performance maintained over a longer interval;
- **career greatness**: some declared combination of peak, duration,
  achievement and opposition; and
- **historical relative standing**: comparison within or across changing eras
  under a stated anchor.

A rolling win table may be an excellent answer to the first question and a
poor answer to the fifth. A peak Elo rating can answer one definition of peak
strength without settling career greatness. The banzuke can be authoritative
for official standing without supplying cardinal distances between positions.

Before changing the algorithm, an alternative should therefore complete the
sentence:

> This system is intended to estimate or summarise ______, for ______, using
> ______ evidence, over ______ time and population boundaries.

Without that statement, disagreement about the numbers may really be
disagreement about the question.

## Simpler summaries remain legitimate alternatives

The discussion which led to Elo-89 began with apparently simple methods. They
remain useful when their limits are declared.

| Method | Coherent interpretation | Principal limitation |
| --- | --- | --- |
| Wins in the last (n) basho | Recent credited production over a fixed tournament window | Entrants and absentees have unequal opportunities |
| Wins in the last (m) bouts | Recent success rate over an equal bout count | Calendar duration and opponent populations differ |
| Wins per basho | Production per tournament appearance | Definitions of appearance and absence matter |
| Wins per bout | Observed strike rate | Ignores unequal opposition unless extended |
| Follow the stronger chii | Use official ordering as the favourite | Chii gaps have no supplied probability geometry |
| Strength-of-schedule adjustment | Credit wins in relation to opposition | Requires its own weighting, iteration and time policy |

These are not failed attempts merely because they do not collapse into one
unique ranking. Their disagreements reveal that “performance” has multiple
dimensions and denominators. They can serve as independent views and as
baselines for more elaborate models.

The existing chii probe, for example, found that the stronger chii won 52.637%
of eligible unequal-chii bouts on its declared snapshot. That makes chii an
informative baseline. It does not yet supply a calibrated probability model or
a matched comparison showing whether its favourite wins more often than
Elo-89's.

## Alternatives within the Elo family

Many alternatives can retain Elo's expectation-and-update idea while changing
one or more policies.

### Expectation rule

Another system could choose a different q, fit q by division or maturity, use
another monotone link, or add a home-like or contextual term where sumo evidence
supports one. Such a change alters the meaning of a rating gap and must be
evaluated as a new model, not merely a new display scale.

### Responsiveness

K could be constant, based on prior bout count, vary continuously with an
uncertainty estimate, respond to age or career stage, or be learned inside a
dynamic model. Any rule faces the same trade-off between following real change
and chasing random results. An appealing life-cycle story is not a substitute
for later-bout evidence.

### Initialisation

Entrants could start equally, by division, by chii, through a contextual rank
model, from amateur or collegiate evidence, or from a distribution rather than
a point. A prior could be fixed once, estimated only from earlier data at each
forecast origin, or allowed to evolve by era.

Each answer changes both early forecasts and the information entering the
population. A prior fitted from future outcomes can be useful for historical
reconstruction, but it must not be described as prospectively available at
the earlier date.

### Inactivity, departure and return

A system could retain the last rating, decay it, shrink it toward an entrant
prior, archive and restore it, widen uncertainty without moving the point, or
treat specific administrative statuses separately. None follows automatically
from non-appearance. Direction, rate and trigger all require specification.

### Population and anchoring

The scale could be left floating, anchored by a fixed mean, tied to a reference
group, normalised within divisions, linked through bridge bouts, or estimated
in a model with explicit era effects. A current common shift may preserve
current probabilities while still changing relationships with future entrants.
Historical comparability must therefore be evaluated over the whole process,
not inferred from one invariance theorem.

### Uncertainty and additional state

An Elo-family successor could maintain both a point estimate and an uncertainty
coordinate, as Glicko-like systems do, or attach an evidential-support summary
without changing updates. Those are different proposals. If uncertainty
affects updating, the rating path itself changes; if it is merely reported,
the original Elo-89 calculation remains intact.

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
- TrueSkill-like multiplayer or uncertainty-aware constructions adapted to
  the actual pairwise setting;
- opponent-adjusted regression models; and
- ensembles combining distinct signals where the combination is fixed and
  evaluated honestly.

These names identify research directions, not completed alternatives in this
repository. Each introduces its own choices about time, regularisation,
population, missing evidence and interpretation. Greater sophistication does
not guarantee better measurement or forecasting.

The project has not performed a controlled comparison between Elo-89 and a
materially different non-Elo family. It should not claim that Elo won such a
contest.

## What has actually been compared here?

The status of alternatives matters.

| Alternative | Status in this project |
| --- | --- |
| Constant 50--50 probability | Direct scored baseline |
| Basic Elo with common K and common initialisation | Direct scored comparator |
| Constant versus divisional K | Controlled factorial comparison |
| Constant versus informed initialisation | Controlled factorial comparison |
| Older informed prior versus P1 | Retrospective predictive comparison |
| No population adjustment, Expt2 departure redistribution and whole-population preservation | Direct final comparison with fixed P1 |
| Chii-order favourite | Separate descriptive baseline on a later snapshot; not a matched probability comparison |
| Elo-58 historical extension | Separate qualified research model, not a peer final-candidate test |
| Different q values | Historical experiments exist, but no comprehensive final-contract selection grid |
| Inactivity decay or alternative return policies | Discussed or illustrated, not selected by a controlled production comparison |
| Uncertainty-aware Elo family | Not evaluated as a production comparator |
| Style or non-transitive interaction model | Not evaluated systematically |
| Dynamic Bayesian or other non-Elo model | Not evaluated |

This table prevents two symmetrical errors: dismissing Elo-89 because an
imagined alternative might be better, and defending it by implying that every
alternative has already lost.

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
parameters, inactivity, return, population, anchoring and observation stage.
“Use Glicko” or “use recent form” is no more reproducible than “use Elo”.

### 3. Preserve chronological honesty

A forecast at time (t) may use only information declared available before
that forecast. If later history is used to fit a retrospective artifact, say
so and do not call the result out-of-sample.

### 4. Compare on matched evidence

Models should forecast the same selected bouts from the same History snapshot
where their claims permit it. Bout identities, exclusions and source hashes
must be preserved. A different dataset can answer a useful question, but not a
paired superiority claim without further work.

### 5. Use relevant baselines and proper scores

For probability models, include 50--50, Basic Elo and the incumbent Elo-89
where appropriate. Report log and Brier loss, calibration and discrimination
rather than winner accuracy alone. A deterministic favourite rule and a
probability forecast should not be compared through whichever metric flatters
one of them.

### 6. Examine populations concealed by the aggregate

Report maturity, division, cross-boundary, entry, return and historical-period
subgroups fixed in advance where possible. An aggregate gain should not conceal
a practically important population regression.

### 7. Quantify uncertainty and sensitivity

Use paired resampling or another appropriate method for score differences.
Vary reasonable modelling choices which were not identified by the data and
record whether the conclusion survives.

### 8. Preserve artifacts and failure

Save forecasts, parameters, source identities, code identity and evaluation
outputs. Negative results are part of the research record. A model should not
be repeatedly adjusted until a preferred ranking appears and then presented
without its search history.

### 9. Obtain later evidence

After selection, freeze the model and score genuinely later results. A
rolling-origin design can supplement this where enough history exists, but it
must reconstruct every fitted component using only information then available.

## Improvement is multidimensional

A proposed successor can be better in one sense and worse in another.

- Lower log loss may accompany worse calibration in a particular group.
- Faster response may increase rating noise.
- Better entrant forecasts may use more institutional prior information.
- A stable historical scale may require a stronger anchoring assumption.
- Explicit uncertainty may improve honesty while making the model harder to
  explain and maintain.
- A richer matchup model may improve fit but overfit rare pairings.

The decision therefore needs a declared priority order and guardrails. Elo-89
used aggregate log loss as primary, Brier loss as corroboration and subgroup
calibration as a qualification. Another project may choose differently, but
it should choose before inspecting which rule produces the preferred winner.

## When does an alternative need a new name?

A changed system needs a distinct model identity when it can alter admitted
evidence, forecasts, state updates, lifecycle, population operation or the
meaning of the output. A new fitted prior or source snapshot also needs a new
artifact identity even if the abstract model contract remains the same.

Examples include:

- `Elo-89 with a corrected P1 artifact`: potentially the same abstract replay
  contract, but a newly identified fitted artifact and rating release;
- `Elo-89 with archived return ratings`: a different lifecycle model;
- `Elo-89 with uncertainty-dependent K`: a different update model; and
- `Elo-89 ratings rounded to integers`: the same model with a presentation
  change, provided no rounded value is fed back into calculation.

Names should make important differences retrievable. They need not encode the
entire specification, but they must point unambiguously to it.

## An invitation, not a claim of finality

Elo-89 should be used because its present bounded claim is useful and supported,
not because every alternative has been eliminated. Its contract and evidence
make disagreement productive: another investigator can replace one choice,
hold the others fixed and discover whether the result improves.

The most valuable alternatives will not be those which merely produce a more
agreeable all-time list. They will explain what new information or assumption
they add, predict where Elo-89 should fail, and survive a comparison in which
surprising results are allowed to stand.

The final position of this account is therefore:

> Elo-89 is the project's present, explicit and testable model of modern sumo
> performance. It is neither a corrected banzuke nor the inevitable numerical
> meaning of strength. Other choices are possible. They become advances when
> their purposes are clear, their contracts reproducible and their claims
> better supported by relevant evidence.

## Working sources

- `../../analysis/docs/2026 09 11 Strength, Purpose and Model Bias - Lab Note.md`
- `../../analysis/docs/2026 09 26 Chii and the Measurement of Strength.md`
- `../../analysis/docs/story/12 Elo-family Model Lineage and Analysis Triage.md`
- `../../analysis/docs/story/22 Elo-89 Rating System Appraisal.md`
- `../../analysis/elo_model_selection/README.md`
- `../../analysis/chii_prediction/docs/Findings.md`
- `../../analysis/toy_elo/README.md`
- `../../analysis/README.md`
