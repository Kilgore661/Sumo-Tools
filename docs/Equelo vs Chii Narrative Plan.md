# Equelo vs Chii Narrative Plan

## Status

Active narrative plan. Work paused after agreeing the structure below.

This plan replaces the statistical-enrichment purpose of
`src/products/make_site2/docs/Rating Statistics Work Plan.md`. The proposed
Equelo confidence and volatility additions were abandoned because Equelo does
not contain a principled uncertainty model from which those quantities can be
derived. Section 7 of that older plan remains relevant as background to the
replacement of `Typical Equelo Ratings`.

The first public-facing section has been drafted as:

```text
docs/Equelo vs Chii.html
```

The current `make_site2` prose artifact is intentionally blank while this
account is developed.

## Purpose

Produce one progressively technical account that culminates in an explanation
of why Equelo ratings need not match chii perfectly and why the project will
not modify Equelo merely to force such agreement.

The account should combine and extend material from:

- `src/products/make_site2/prose/Equelo Ratings.html`;
- `docs/What is an Equelo Rating.md`;
- `src/analysis/clean_elo/docs/Rating Probe Findings.md`;
- the legacy `Typical Equelo Ratings` artifact.

It should remain possible for readers to stop after the early sections with a
useful, honest understanding. Later sections may assume progressively more
mathematical maturity.

## Editorial Principle

Do not lead with methodology. Establish the familiar sumo world, then say
directly, “Here is the model.”

Each level of the account should be sufficient for its intended reader. Later
sections should add precision rather than retract misleading simplifications
made earlier.

## Narrative Spine

### 1. How sumo is organised

Use the structural overview already drafted in `docs/Equelo vs Chii.html`.

Its purpose is only to establish common facts and terminology for any reader:

- the basho cycle;
- the banzuke;
- divisions and the sekitori boundary;
- chii notation and ordering;
- tournament records;
- `kyujo`, `fusen`, `fusenpai` and `fusensho`;
- adaptive, non-random bout scheduling;
- promotion and demotion;
- a population that is finite at each basho but open through time.

Do not introduce a model-ready summary or methodological discussion in this
section.

### 2. Ratings in one minute

Explain at the most accessible level:

- a rating is a numerical estimate of demonstrated performance;
- a higher rating means stronger according to the model;
- rating differences, rather than absolute values, carry the main predictive
  meaning.

### 3. A quick guide to the Equelo scale

Show only selected chii, provisionally:

```text
Y1e
M1e
J1e
Ms1e
Sd1e
Jd1e
Jk1e
```

Do not call these values empirical “typical ratings”. They are selected points
from the Equelo entrant-rating scale.

The accompanying qualification should say, in substance:

> These landmarks give a rough sense of the Equelo scale. They are the ratings
> Equelo assigns when it first encounters a rikishi at these chii. They are not
> the observed average ratings of all rikishi occupying those chii. The
> empirical relationship between chii and rating contains some surprises,
> discussed below.

This section should allow a casual reader to stop with a useful but qualified
orientation.

### 4. Here is the Elo model

Introduce the ordinary expected-score and update model without a methodological
preamble:

\[
R' = R + K(S-E)
\]

Use concrete calculations to show at least:

- an expected favourite winning;
- an underdog winning;
- equally rated opponents;
- different K values if they are needed to understand production Equelo.

### 5. Does chii determine a rikishi's rating?

Answer: no.

Chii determines an initial Equelo rating when the system first needs one for a
rikishi. Subsequent bout results move the rikishi away from that value.

Rikishi occupying the same chii can therefore have different process ratings.
Show examples or distributions before moving to averages by chii.

The central distinction is:

> Chii supplies an entrant's initial Equelo rating; it does not thereafter
> determine that rikishi's process rating.

### 6. Here is Equelo, taking its initial values as given

Defer the derivation of the initial-rating map:

> For now, assume that Equelo has a table of initial ratings by chii. We explain
> where that table comes from later.

Then describe the rating process:

- assign the initial rating when required;
- apply Elo-style updates to contested bouts;
- carry the resulting rating forward;
- apply the population-normalisation rule at basho boundaries.

“Elo plus normalisation” is an acceptable first approximation once the initial
values are taken as given. The exact account must also identify the declared K
and scale policies and explain that fusen is not treated as a contested bout.

### 7. What relationship is actually observed?

Present the empirical chii-to-rating evidence using production Equelo.

The primary table should be defined before it is calculated. The provisional
observation is one start-of-basho process rating per rikishi-basho, matched to
the chii from that same basho. State the period, population, aggregation and
support explicitly.

Show and explain:

- broad ordering between chii and rating;
- variation among rikishi occupying the same chii;
- lack of flawless monotonicity in point averages;
- the literal lower-maegashira pattern;
- what changes when observations are aligned by distance from the division
  boundary;
- which earlier findings used Elo-like experimental ratings rather than
  production Equelo.

The legacy monotonic `Typical Equelo Ratings` table may be used as an exhibit:
the tidy correspondence the project expected or wanted to see, but not an
empirical table of historical mean process ratings.

### 8. What the project thinks this means

The decision is not to ignore the issue. It is:

- do not force Equelo into monotonic agreement with chii;
- do not publish constructed landmarks as empirical facts;
- do not label every inversion an anomaly;
- explain disagreements in proportion to the claims being made;
- continue using ratings because rikishi trajectories, comparisons and records
  remain useful independently of perfect chii correspondence;
- treat chii and Equelo as related but non-identical accounts of performance
  and position.

### 9. Where the initial ratings come from

Only after their role is understood, explain:

- why constant initial ratings were considered inadequate;
- incomplete historical lower-division results;
- chii as prior information;
- the fixed-point estimation idea;
- the supported chii domain;
- deterministic completion for unsupported chii;
- the frozen production initial-rating map.

This is the natural point for the account to become substantially more
technical.

## Further Technical Depth

If the account continues beyond the initial-value explanation, advanced
material should map the real unresolved questions rather than pretend to solve
them. Possible subjects include dynamic latent strength, endogenous scheduling,
open-population processes, dependent observations, changing banzuke structure,
identifiability, stationarity and ergodicity.

It is acceptable to identify where a rigorous treatment would require
specialist statistical or rating-theory work.

## Immediate Next Step

Draft section 2, “Ratings in one minute”, immediately after the existing
structural overview. Do not yet write or publish the selected Equelo scale
landmarks until their exact source values and labels have been settled.
