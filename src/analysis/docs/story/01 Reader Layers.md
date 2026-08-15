# Reader Layers

## Principle

The account should use progressive disclosure. A reader should be able to stop
when they have learned enough for their purpose without being forced through
material intended for a more technical audience.

The layers describe what readers need from this account, not fixed categories
of people. The same reader may be casual when looking at a basho table and
critical when reviewing the model.

## Casual reader

The casual reader wants to understand a rating printed beside a rikishi's name
in a headline table or chart.

This layer should explain:

- ratings are running numbers derived from previous results;
- ratings are useful primarily through comparisons;
- a rating difference determines whom the calculation favours and by how much;
- an estimated probability is not a guaranteed result;
- an isolated rating is not an amount of strength;
- historical Basic Elo did slightly better overall than treating every bout as
  50--50, but the improvement was limited.

This layer should avoid formulae, parameter discussions, normalization and
fixed-point terminology.

Current draft:
[Elo Introduction for the Casual Reader](03%20Elo%20Introduction%20for%20the%20Casual%20Reader.md).

## STEM reader

The interested technical reader is willing to read formulae, inspect worked
examples and interpret charts, but should not be assumed to have specialist
knowledge of information theory, stochastic approximation, rating-system
research or statistical calibration.

This layer should explain:

- the Elo expected-score formula;
- why only rating differences matter;
- the role of `q`;
- the update formula and the role of `k`;
- zero-sum updates in ordinary equal-`k` Elo;
- translation invariance;
- fixed-`k` fluctuation rather than everyday permanent convergence;
- entry, retirement, initialization lag and scale drift;
- why those problems motivate Equelo;
- Equelo's initialization, normalization, support and completion mechanics.

The prose must not assume that following the mechanics is the same as
understanding or accepting the system's empirical validity.

Current Elo draft:
[Draft: A Standard Account of Elo](06%20Draft%20Standard%20Elo%20Account%20for%20the%20STEM%20Reader.html).

Current Equelo draft:
[Draft: How Equelo Changes Elo](07%20Draft%20Equelo%20Account%20for%20the%20STEM%20Reader.md).

## Detailed technical reader

The detailed technical reader wants to know exactly what was calculated and
to be able to reproduce it. This layer may assume comfort with mathematical
notation and algorithms, but should still explain project-specific choices
rather than requiring the reader to infer them from code.

It should follow the same order as the STEM account:

1. define the precise Elo model, with formulae, parameter choices, chronology
   and worked examples;
2. define the precise Equelo model, including divisional `k`, both forms of
   normalisation, iterative initialisation, convergence criterion, support and
   completion policies, and the historical-data contract.

This is the layer to which the STEM account can refer an interested reader for
the full details. Its job is exact specification, not yet the strongest
possible defence of the model.

Current status: not started. The maintained specifications and implementation
notes identified in the evidence map provide the source material.

## Expert or critical reader

The critical reader is expected to ask whether the model has earned the
interpretations attached to it.

This layer must make it possible to investigate:

- precisely what normalization does;
- whether low-support chii values are dominated by normalization rather than
  bout evidence;
- whether a fixed-point construction is unique, stable and meaningful;
- sensitivity to initialization, support thresholds and completion rules;
- the origin and interpretation of visible non-monotonicity;
- calibration and discrimination of Elo probabilities;
- calibration and discrimination of Equelo probabilities;
- direct predictive comparison of Basic Elo and Equelo;
- any predictive cost paid for Equelo's intended representational benefits.

This layer should link claims to specifications, generated artifacts and
reproducible experiments. It should state unresolved matters directly.

It is intended ultimately for readers with relevant specialist training. It
may use the language and methods of rating-system theory, statistics and
applied mathematics where those are needed to assess the model rigorously.

Current status: not started. Some of the necessary evidence and open questions
already exist in the project research notes.

## Relationship between the layers

The casual layer explains how to read the display. The STEM layer gives a
conceptual technical account of how the systems are constructed. The detailed
technical layer specifies exactly what is calculated and how. The expert layer
evaluates whether the construction and its outputs justify the proposed
interpretation.

The later layers may qualify earlier simplifications, but should not reveal
that an earlier statement was false. Each layer must be accurate at its own
level of resolution.
