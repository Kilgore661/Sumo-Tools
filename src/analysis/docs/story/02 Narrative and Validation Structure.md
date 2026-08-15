# Narrative and Validation Structure

## Decision

Prediction will be treated as a separate axis of evaluation rather than as
either the definition of a rating system or a footnote at the end of the
Elo-to-Equelo story.

The account must answer two different questions:

1. **Construction:** How are the numbers produced, and what problems is Equelo
   designed to address?
2. **Validation:** What evidence is there that the numbers are useful?

Initialization, inflation and normalization belong primarily to construction.
Predictive performance belongs to validation. They interact, but one does not
establish the other.

## Why prediction is not the opening definition

A rating system may be intended to forecast contests, order competitors,
summarize past performance, compare performances over time, provide a stable
descriptive scale, or combine several of these purposes.

Prediction is especially important for Elo because Elo explicitly converts
rating differences into expected outcomes. It is nevertheless too restrictive
to begin by declaring that a good rating system is necessarily a good
predictive system. Doing so would decide in advance how every possible Equelo
trade-off must be judged.

A suitable opening position is:

> A rating system turns contest evidence into numbers that can be compared.
> Different rating systems may be judged by different properties. One
> particularly important test is whether their ratings help predict later
> results.

## Proposed narrative route

The route below is also a progressive-disclosure sequence. Section 1 belongs
to the casual narrative. Sections 2--6 provide the conceptual STEM narrative
and the Elo-then-Equelo spine for the planned detailed-technical account.
Sections 7--8 lead into the eventual expert/critical account, where
construction is assessed rather than merely specified.

### 1. Elo for the casual reader

Explain ratings, differences, favourites, estimated probabilities, surprising
results and the limited historical improvement over 50--50.

### 2. For the Interested Reader

Introduce Equelo as the system used by the project. Explain that Equelo is based
on Elo and was designed to address rating inflation and initialization lag. Link
to the [draft fuller standard account of Elo](06%20Draft%20Standard%20Elo%20Account%20for%20the%20STEM%20Reader.html).

Provisional transition:

> In our work we use an alternative to Elo called *Equelo*. Equelo is based on
> Elo but is designed to address two important problems: *rating inflation*
> and *initialisation lag*. To understand Equelo, it is first necessary to
> understand Elo in more detail. If these ideas are unfamiliar, see our fuller
> account of Elo, which explains the standard calculation with worked examples.

The fuller account referred to in that provisional transition now exists as a
working draft. Final site prose should link to it only after editorial and
source review and publication in an appropriate public form.

The final wording should define initialization lag and should say "designed to
address" unless the relevant avoidance claim has been demonstrated.

### 3. How Elo works

Cover:

- ratings and rating differences;
- the expected-score equation;
- the probability-scale parameter `q`;
- the result-update equation;
- the update-rate parameter `k`;
- worked examples;
- equal-`k` zero-sum transfers;
- translation invariance and the arbitrary absolute level.

At this stage, the probability formula is a definition within the mechanics.
Whether the probabilities describe actual sumo well remains unanswered.

### 4. Difficulties applying Elo to historical sumo

Separate the following problems:

- arbitrary common initialization;
- initialization lag;
- entry and retirement;
- inflation or deflation in an open population;
- incomplete historical results;
- a changing population;
- changing individual performance;
- selective and incomplete comparison graphs;
- continuing fixed-`k` fluctuation even in an ideal stationary world.

This section motivates Equelo but must state which problems Equelo actually
addresses. It must not imply that Equelo solves the entire list.

### 5. What Equelo changes

Explain:

- chii-informed initialization;
- the iterative or fixed-point construction;
- normalization;
- scale preservation;
- support filtering;
- completion of unsupported chii;
- the relationship between individual ratings and typical chii values.

The STEM draft gives the conceptual account of the three headline changes:
divisional `k`, normalisation and chii-informed initialisation. The exact
support, completion, convergence and data-handling rules are deferred to the
detailed-technical account.

### 6. What Equelo is intended to achieve

State intended properties separately from empirical findings:

- less arbitrary entrant ratings;
- reduced initialization lag;
- control of historical scale drift;
- a reproducible rating surface across the banzuke;
- continued use of an Elo-like result-update mechanism.

### 7. Do the ratings predict results?

Use a common validation chapter with parallel treatments.

For Basic Elo, give the precise tested model, its 50--50 comparator, the modest
aggregate improvement, population differences and the limits of the claim.

For Equelo, use the same forecast/evaluation protocol and report calibration,
Brier loss, log loss, population splits and direct comparison with Basic Elo.
This part remains incomplete until the appropriate experiment is run.

### 8. Problems and open questions

Split Equelo concerns into two groups.

#### Mechanics

- normalization at low-support chii;
- values dominated by normalization rather than results;
- non-monotonicity at the maegashira tail;
- completion rules;
- sensitivity to model choices;
- the danger of refining the model merely to enforce an expected shape.

#### Predictive utility

- whether Equelo preserves Elo's limited predictive information;
- whether chii-based initialization improves early forecasts;
- whether normalization affects probabilities;
- whether Equelo is materially worse than Basic Elo;
- what independently useful property would justify a predictive loss.

## Comparison framework

| Question | Basic Elo | Equelo |
|---|---|---|
| How are entrants initialized? | Common arbitrary rating | Chii-informed rating |
| What happens to the scale over time? | Can drift in an open population | Normalization is intended to control drift |
| Do ratings settle permanently? | No, not with fixed nonzero `k` | Not established merely by the Equelo construction |
| Does it reproduce chii order? | Not necessarily | Not necessarily; low-support behaviour is under investigation |
| Does it beat 50--50? | Slightly in the tested historical aggregate | Must be tested comparably |
| Are probabilities well calibrated? | Only limited evidence | Must be tested |
| What is its intended role? | Running outcome-based rating and forecast | Historically stabilized, chii-informed rating construction |
| Main unresolved concern | Limited predictive improvement and unstable individual ratings | Normalization/support behaviour and comparative predictive performance |

## Standard for any defence of Equelo

The defence must not be:

> Equelo predicts poorly, but Elo predicts poorly too.

The relevant question is:

> Basic Elo has a small demonstrated predictive advantage. Does Equelo
> preserve, improve or sacrifice that advantage? If it sacrifices some of it,
> what independently valuable property is obtained in exchange?

A small predictive loss might be a defensible trade-off for a stable historical
representation. A substantial loss would be a serious problem, particularly if
Equelo ratings continue to be interpreted through Elo-derived probabilities.

## Documentation levels and current position

| Level | Purpose | Current position |
|---|---|---|
| Casual | Explain how to interpret displayed ratings and differences | Elo draft written |
| STEM | Give an accessible technical construction account | Separate Elo and Equelo drafts written |
| Detailed technical | Specify the exact calculations and implementation choices | Not started; write Elo first, then Equelo |
| Expert/critical | Test foundations, interpretations and empirical utility | Not started as a unified account; source evidence and open investigations exist |

The next writing stage is the detailed-technical account. It should retain the
same Elo-then-Equelo order as the STEM material so that readers can move between
the two levels without encountering a different conceptual structure. The
expert/critical account comes after that specification and should distinguish
mathematical questions from empirical evaluation.
