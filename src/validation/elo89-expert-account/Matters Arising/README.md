# Matters Arising from the Elo-89 Expert Account

## Status

This folder begins the next tranche of Elo-89 work.

The thirteen-chapter expert account committed as `aa311ee` is the baseline for
this tranche. Its chapters are not being revised while the first matters
arising are investigated. The investigations may confirm the present model,
identify simple code corrections or require changes to the model contract and
its account.

This README records the questions, present intuitions and agreed common method.
Individual matter folders contain the analysis, tests, evidence and conclusions
as that work proceeds; an investigation is not concluded merely because its
first descriptive audit has been run.

## Epoch boundary

All matters in this tranche concern the published Elo-89 line beginning at
`1989-01`. The available `History` may represent records from `1958-01`, and
older analysis code commonly assumes that earlier epoch, but those facts do
not expand the scope of this validation work.

The move away from the 1958 epoch was an accumulated modelling conclusion,
not a single readily identifiable repository event. The attempt to preserve
the earlier epoch led to progressively larger compromises in the treatment of
incomplete lower-division evidence. The expert account describes the model
which resulted after the project accepted that those compromises were not a
suitable basis for the ratings now intended for publication.

Consequently, every matter must recompute its descriptive evidence for the
interval beginning `1989-01`. A count or conclusion inherited from older code
is only a lead until its epoch has been identified and the result has been
checked on the Elo-89 interval. Full-history results may be retained as
historical or comparative evidence, but they must not be presented as the
answer to an Elo-89 validation question.

## Purpose

The expert account has made the Elo-89 contract and its evidential gaps clear
enough to generate focused questions. Each question will now be treated as a
mini-project in its own right until the project can say:

- exactly what the current behaviour is;
- what principle the behaviour is intended to express;
- how many records and outputs are affected;
- what alternative rule is proposed;
- what would change mechanically and interpretively;
- what controlled evidence says about the consequences; and
- whether the rule should be retained, corrected or replaced.

The expected outcome is that the first three matters may prove to be simple
code corrections with no significant practical effect. That is a hypothesis,
not a conclusion. A small numerical effect would not by itself make a semantic
correction unnecessary, and a large effect would not by itself determine which
rule expresses the intended rating model.

The governing question is:

> Given the account of performance Elo-89 claims to provide, what information
> should its state preserve and which represented events should count as
> evidence?

## The first three matters

### 1. Results without kimarite

**Question:** Is a represented W/L result valid rating evidence when no
kimarite is recorded?

**Present view:** Yes. If the winner, loser and all other required bout
attributes are known, absence of kimarite should not disqualify the result.
Kimarite is not an input to the Elo-89 model and there was never an intention
to model technique.

The recollection to verify is that exclusion of `decision="blank"` was an
arbitrary expedient inherited from earlier work rather than a considered
definition of valid competitive evidence. If so, the model should positively
select represented W/L outcomes everywhere and treat the kimarite field as
irrelevant to rating eligibility.

This could expand the observation set used to fit P1 and affect every rating
which depends on that fitted prior. The likely size of the effect is expected
to be small, but must be measured rather than assumed.

### 2. Disappearance and reappearance

**Question:** Should a rikishi who leaves the represented active population
and later reappears retain his previous rating or be reinitialised from P1?

**Present view:** He should retain it. Absence of competition supplies no new
bout evidence, so it should neither update nor erase the existing estimate.

The investigation must distinguish:

- missing bouts while the rikishi remains on the banzuke;
- absence from the represented banzuke population;
- administrative movement below the ranked banzuke;
- genuine departure followed by an exceptional return; and
- uncertainty about current condition versus the retained point estimate.

It must also resolve what “the rating stays the same” means in an anchored open
population. An archived literal number receives none of the common shifts
applied while the rikishi is absent. Restoring that number later may place an
old coordinate into a population whose shared coordinate has moved. Carrying
the archived rating through those common shifts would preserve its relation to
the scale but would change its numerical value without individual bout
evidence. That choice is part of the model contract.

The numerical effect is less predictable than for missing kimarite and may be
concentrated in a small number of lifecycle episodes.

### 3. Results involving off-banzuke rikishi

**Question:** Should a represented W/L result be rated when one or both
participants are absent from the current banzuke representation?

**Present view:** Undecided. The case is thought to be unusual, but its nature
and frequency must be established before a policy is chosen.

The evidence review must identify:

- how many such results exist and in which periods;
- what statuses “off-banzuke” represents in the source data;
- whether the participants and outcomes are otherwise reliable;
- whether an affected rikishi has a carried or archived rating;
- which chii-based prior and K value the current implementation uses;
- whether the participant enters the active population for normalisation; and
- how the cases overlap with disappearance and reappearance.

This matter may be almost empty, a data-quality problem, or a genuine test of
the rating population's boundary. No position should be inferred from its
expected rarity.

## Common investigation method

Each mini-project will follow the same sequence.

### 1. Establish the current contract

Trace the rule through data preparation, P1 production, experimental replays,
production Elo-89, evaluation tools and website consumers. Distinguish current
production behaviour from historical experiment behaviour and from prose
which may no longer match either.

### 2. Audit the affected evidence

Before changing code, freeze and identify one History snapshot and state the
selected interval beginning at the `1989-01` Elo-89 epoch. Count the affected
observations and inspect their important attributes, periods, divisions,
participants and lifecycle contexts. The audit must determine whether the
proposed category is coherent or conceals several different cases. If earlier
evidence used another epoch, preserve that fact and rerun or restrict it before
adoption.

### 3. Map the consequences

Record every likely downstream effect, including:

- selected bout counts and exclusions;
- P1 support, convergence and paired prior values;
- entrant and returning-rikishi initialisation;
- active-population membership and normalisation;
- forecast probabilities and bout updates;
- basho-start, day-end and basho-end ratings;
- log loss, Brier loss and calibration;
- division, maturity, entry, return and cross-boundary subgroups;
- published rankings, peaks, changes and career histories; and
- the interpretation and wording of the expert account.

This impact map should be written before the result is known.

### 4. State the proposed rule

Express the replacement as a model rule, not only a code edit. State the
principle it is intended to realise and any unresolved variants. Identify what
evidence could count against the proposed implementation without allowing a
preferred ranking to define success.

### 5. Produce a controlled comparison

On the same frozen inputs, preserve an old-rule baseline and change only the
matter under investigation. Regenerate every fitted artifact whose inputs have
changed rather than patching its output. Compare exact bout identities and
trace differences from the first divergence through final publications.

### 6. Evaluate scale and location of change

Aggregate differences are not sufficient. Determine whether changes are
concentrated in particular periods, chii, divisions, maturity levels or
lifecycle cases, and whether any apparently small average conceals a material
individual result.

### 7. Decide and classify

The conclusion should say whether the matter is:

- a semantic correction required by the intended evidence contract;
- an evidence-led model change;
- an accepted modelling judgement;
- an implementation or documentation repair;
- insignificant in the tested history but still prospective policy; or
- unresolved pending further work.

Predictive scores inform this decision but do not alone decide what constitutes
a known fought result or what information a rating is intended to preserve.

### 8. Adopt explicitly

If a change is accepted, update code, focused contract tests, provenance,
artifacts and documentation together. Routine website production must not
silently refit P1 or change historical ratings. Model-maintenance changes need
an explicit generation, evaluation and promotion step.

## Order and interaction

The initial working order is:

```text
results without kimarite
    -> disappearance and reappearance
    -> off-banzuke results
    -> combined accepted contract
```

The issues should first be isolated so that a changed result can be attributed
to one rule. A final combined run is still required because the rules interact:
an off-banzuke result may arrive during what the current model treats as an
absence, while persistence may provide the rating needed to process that bout
coherently.

## Proposed mini-project structure

As each matter becomes active, give it a numbered subfolder containing its own
orientation, evidence audit, experiment specification, findings and decision:

```text
Matters Arising/
    README.md
    Kimarite/
    02 Disappearance and Reappearance/
    03 Off-Banzuke Results/
```

Folders should be created when work begins rather than filled in advance with
speculative conclusions.

## Versioning the expert account

The baseline account should not be overwritten as conclusions accumulate. It
is both a readable draft and a record of the model understanding which exposed
these matters.

The preferred policy is:

1. keep `elo89-expert-account` as the first committed baseline;
2. conduct and preserve its matters-arising investigations here;
3. when a coherent set of conclusions is ready, create a new complete sibling
   account folder rather than editing the baseline in place;
4. apply the accepted revisions to that new copy;
5. give the new account its own `Matters Arising` folder for questions exposed
   by the revised account; and
6. retain links between account versions, decisions and the exact model and
   fitted artifacts they describe.

The final sibling name is deliberately not fixed yet. A simple
`elo89-expert-account-2` is clearer than silently replacing the original;
a date or explicit model/artifact version may prove better once the nature of
the first revisions is known.

Concluded investigation records should remain with the account version which
raised them. A successor's `Matters Arising` folder should begin with any
unresolved items carried forward and new questions generated by the revised
text, rather than pretending the earlier reasoning never occurred.

## Completion condition for this tranche

The first tranche of matters arising is complete when all three questions have
explicit decisions, their individual and combined consequences have been
measured on frozen inputs, accepted changes have been implemented and
identified, and a successor expert account can be generated without rewriting
the history of how those decisions were reached.
