# 8. From Elo to Elo-like Systems

> **Draft status:** First continuous-prose draft. This chapter proposes working
> terminology for this account; it does not claim that “Elo-like” has one
> universally agreed technical definition.

## “Elo” names an idea before it names a complete system

Chapter 5 described ordinary Elo as a compact mathematical object. Current
ratings determine an expected score, and the difference between the observed
and expected score moves the ratings. Chapter 7 showed that this is not enough
to run a historical rating system. The equations do not select the evidence,
initialise the recurrence, define the population or decide what happens when a
competitor leaves and returns.

Those surrounding choices are sometimes described as implementation details.
That description is unsafe. Change the entrant rating, the K policy or the
population operation and later ratings can change. Change the admissible bouts
or their order and the recurrence processes different evidence. The resulting
systems may all inherit the Elo idea, but they are not the same model.

This account therefore uses **ordinary Elo** for the binary, logistic,
common-K equations studied in Chapter 5, and **Elo-like system** for a complete
rating system built around recognisably the same expectation-and-update idea.

## A working definition

For the purposes of this account, a system is Elo-like when it has at least
the following structure:

1. each competitor has a numerical state carried from one represented contest
   to the next;
2. the competitors' current states determine an expected score for their
   contest;
3. the observed score is compared with that expectation; and
4. the state is updated in the direction of the resulting surprise: doing
   better than expected raises it and doing worse lowers it.

The familiar Elo equations are the clearest instance. Members of the wider
family can vary the expectation curve, the size of the update, the initial
state and the treatment of uncertainty or population change while retaining
that organising idea.

This is a working boundary, not a claim about ownership of a name. A rolling
win count is not Elo-like in this sense because it does not use the opponents'
current states to form an expectation. A static paired-comparison fit may use
the same logistic relationship as Elo, but without the sequential
observed-minus-expected recurrence it is a related statistical model rather
than an Elo-like rating process in the sense used here. Systems such as Glicko
are commonly treated as members of the wider Elo family because they retain
the paired expectation-and-update structure while adding an uncertainty
state.

The boundary matters less than the contract. Calling a method “Elo-like” does
not tell a reader exactly what was calculated.

## The complete model is a bundle of choices

An operational rating model must answer every question needed to turn source
records into a sequence of states. Its main choice axes include the following.

| Axis | Question which the contract must answer | Why the answer matters |
| --- | --- | --- |
| Evidence domain | Which contests and results are represented? | It defines what the rating is evidence about and which updates occur. |
| Epoch | When does the recurrence begin? | It creates the initial-state problem and limits the history the model can have learned. |
| Identity | What counts as the same continuing competitor? | Merged or split identities alter the state carried into later contests. |
| Outcome representation | Are wins, losses, draws, absences and administrative results distinct? | The numerical score supplied to the update depends on this classification. |
| Expectation rule | How do state differences become expected scores, and what scale parameter is used? | It determines the meaning of a rating gap. |
| Update policy | Is K constant, divisional, experience-dependent or otherwise variable? | It controls responsiveness and may change conservation properties. |
| Initialisation | What state is assigned at the epoch and on later entry? | It determines the forecast before contest evidence has accumulated. |
| Chronology | In what order are contests processed, and are updates immediate or grouped into rating periods? | Sequential Elo is generally order-dependent. |
| Persistence | What happens during absence, departure and return? | It determines which old evidence survives and when a competitor is treated as new. |
| Population | Who belongs to the rated population at each point? | Entry and removal affect population summaries and any population-level operation. |
| Scale control | Is the scale allowed to float, or is some location or distribution anchored? | It affects longitudinal interpretation and, through later entry, can affect future differences. |
| Uncertainty | Is there only a point state, or is evidential precision represented separately? | Equal printed ratings need not be equally well supported. |
| Observation | At what stage is a rating exposed: before a bout, after a bout, at basho end or at another boundary? | Different snapshots can all be correct states of the same recurrence. |

The list separates questions which are easily conflated. Initialisation says
where a competitor starts. Population policy says who is present. Scale
control says whether and how the population is moved. Observation says which
already-calculated state is published. One numerical output can depend on all
four.

Nor are these axes necessarily exhaustive. A richer system might add explicit
time decay, surface or style effects, home advantage, team structure or a
latent development process. Such additions require further contract clauses;
the word Elo does not supply them.

## The choices interact

The table is a checklist, not a set of independent switches.

The expectation scale and K are expressed in rating units. Rescaling the
rating coordinate while transforming both consistently can describe the same
dynamics, whereas changing only one changes the model.

Common K makes each ordinary two-player update zero-sum. Giving the two
competitors unequal gains generally removes that theorem. A policy introduced
to make one group more responsive can therefore also alter population
accounting.

An entrant prior and a population anchor also interact. A common additive
shift applied to every current rating preserves all current rating differences
and hence all current Elo probabilities. It is not necessarily neutral over
the whole future history. If later entrants continue to receive ratings from a
fixed external prior, their differences from the shifted incumbents change.

Evidence and fitting interact as well. A prior estimated using later career
information may be useful for retrospective reconstruction, but it cannot be
treated as a prospectively available forecast without qualification. If the
same contests help construct a parameter and then assess it, the evaluation
must account for that information reuse.

These interactions are why a model cannot safely be described by mentioning
only its most conspicuous modification, such as “divisional K” or “rank-based
initialisation”.

## When does a choice make a different model?

For this project, a change defines a materially different model when it can
change at least one of the following:

- which evidence is admitted or how it is represented;
- the forecast assigned before a represented contest;
- the state produced after it;
- the state carried across entry, absence, departure or return; or
- the intended interpretation of the resulting number.

This criterion is intentionally stricter than asking whether two runs happen
to print different values in one table. A correction to code may change the
output while restoring the same intended model contract. Conversely, two
policies may produce identical values on a particular dataset but remain
different models because they would diverge when the triggering condition
occurred.

Presentation alone need not define a new rating model. Rounding a displayed
value or choosing a chart colour changes the publication, not the recurrence.
But selecting a pre-bout instead of post-bout state changes which model state
the publication claims to show and must be named in the observation contract.

The practical rule is simple: if a choice could change the evidence, forecast,
update, persistence or meaning, it belongs in the specification and should be
versioned deliberately.

## Three things must be frozen

A reproducible published rating requires more than a model name.

| Layer | What must be frozen | Examples |
| --- | --- | --- |
| Model contract | The rules which map admissible history and parameters to states | evidence domain, expectation equation, K policy, entry and population rules |
| Fitted artifact | Numerical inputs learned or selected outside the recurrence | an entrant-prior table, fitted coefficients, source-data and code identity |
| Run and observation contract | The concrete history processed and the state exposed | data cut-off, ordering, snapshot boundary, rounding and release identifier |

The distinction prevents several ambiguities.

A fitted prior table is not the general rule which says how the table will be
used. Re-estimating that table under the same fitting procedure may create a
new artifact and new ratings without changing the abstract model contract. A
publication can also select a different valid observation point without
changing the internal recurrence, although it has changed what readers see.

For serious comparison, all three layers need identities. A convenient short
name can point to them, but it cannot replace them.

## Names are claims about contracts

“Elo” is therefore too broad to be a reproducible model name. Even a compact
label such as “divisional-K plus prior” identifies a family unless the values,
construction and surrounding population policies are fixed.

The repository's research lineage illustrates the point. Basic Elo and the
experimental variants which added divisional K, informed initialisation or
both were valuable comparators. They established that the choice of prior had
a material effect in the tested history and that the K policy had a smaller
but still model-defining effect. They did not thereby define every later
population, persistence or publication rule.

Research names should accordingly preserve lineage without pretending that
an experiment is the current production contract. A candidate can be the
ancestor of a published model without being interchangeable with it. Evidence
obtained from a candidate remains evidence about that candidate unless the
relevant equivalence has been shown.

## Elo-89 is one specified member of the family

Elo-89 retains the recognisable Elo core: a current rating difference produces
an expected result, and each represented result updates the competitors'
states according to its surprise. Its identity, however, comes from the whole
contract rather than from that core alone.

The epoch, bout domain, rating scale, divisional K policy, entrant prior,
population normalisation, departure and return rules, chronology and
observation stages together determine what an Elo-89 rating is. Some of those
choices respond to the difficulties identified in Chapter 7. Others are
pragmatic judgements or boundaries of the available evidence. None follows
merely from writing down the ordinary Elo equations.

Chapter 9 states that exact contract. Chapter 10 then asks why those choices
were made and distinguishes empirical selection from modelling judgement,
inheritance and unresolved work.

## Working sources

- `../../../../analysis/docs/Elo-family Named Model Table.html`
- `../../../../analysis/docs/story/12 Elo-family Model Lineage and Analysis Triage.md`
- `../../../../analysis/docs/story/15 Tranche 1 - Population Normalisation Policy.md`
- `../../../../analysis/elo_model_selection/README.md`
- `../../../../analysis/elo_model_selection/docs/Results 1.md`
- `../../../../analysis/README.md`
