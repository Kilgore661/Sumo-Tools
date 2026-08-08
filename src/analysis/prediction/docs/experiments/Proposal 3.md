# Proposal 3: Retrospective Chii-based Initialization

## Status

Accepted diagnostic experiment following the population evaluations in
Proposal 2 and Proposal 2b.

## Question

Does the long early underperformance of Basic Elo in the sub-sekitori
population substantially result from the externally imposed equal-rating
initial condition?

## Baseline producer

First run Proposal 1 unchanged over 1989/01 onward. Its immutable forecasts and
ratings supply a retrospective rating surface over chii.

## Prior construction

At the start of each basho, before any current-basho update, associate every
already-rated banzuke participant's carried rating with the participant's exact
`Chii` value.

Translate each basho snapshot to a common mean of 1500 before retaining its
observations. This changes rating location but preserves every within-basho
rating difference and probability.

For each exact Chii:

1. retain its last ten start-of-basho normalized rating observations;
2. take their unweighted arithmetic mean;
3. use that mean as the initial rating for that Chii.

Do not impose monotonicity. Observed reversals between adjacent chii are part
of the retrospective surface and must remain visible.

If a Chii needed for initialization has no retained observation, interpolate
linearly between the nearest observed Chii positions in authoritative Chii
order. Interpolation uses ordered position, not chii strings or numerical
distance between ordinals. Outside the observed range, use the nearest observed
edge.

Because of a known History-building defect, RikId 13011 has seven represented
W/L bouts in 2026/07 despite being absent from that basho's banzuke. With no
Chii to map, temporarily initialize that RikId at the weakest mapped Chii edge
and record the accommodation. This is not a legitimate exception to the
History contract; `analysis/sumo_history/README.md` records the defect.

## Second pass

Run Basic Elo again with q=400 and k=35. Whenever a RikId first enters the
rating registry, initialize it from its pre-bout Chii through the retrospective
surface. All other Proposal 1 eligibility, persistence, chronology and scoring
contracts remain unchanged.

Evaluate:

- all eligible bouts;
- bouts with two sekitori participants;
- bouts with two sub-sekitori participants.

In each subgroup, bouts outside the evaluation domain still update ratings.

## Required audit artifacts

Write:

- a CSV keyed by authoritative chii ordinal containing display chii, derived
  initial rating, source, observation count and contributing date range;
- a CSV of every retained normalized observation behind the trailing means;
- forecast, loss, uncertainty, chart and report artifacts for all three
  evaluation populations;
- direct comparisons with equal initialization.

## Interpretation boundary

The prior uses ratings derived from outcomes later scored by the second pass.
This is therefore a retrospective oracle diagnostic, not an out-of-sample
predictive model and not a candidate selected for deployment.

If the early sub-sekitori underperformance is reduced, the result supports the
hypothesis that uniform initialization erased a consequential rank-shaped
rating structure. It does not establish that this particular retrospective
mapping would be available prospectively.
