# Elo Documentation Rummage

This note records a review of the Markdown and HTML documentation that explains
what Elo is for, the problems involved in applying it to Grand Sumo, and the
package-specific experiments that investigate its properties. Equelo-only
material is treated as secondary, except where it illuminates an underlying
Elo problem.

## Best starting points

1. [Elo Ratings](../../products/make_site2/prose/Elo%20Ratings.html)  
   The clearest current introduction. It explains:

   - why opponent-sensitive ratings are useful in sumo;
   - rating differences, expected probabilities, `q`, `k`, and zero-sum
     updates;
   - why absolute rating levels are arbitrary;
   - common-start distortion;
   - missing pre-sekitori history;
   - scale drift caused by entry and retirement;
   - factors Elo does not model, such as injuries, style matchups, and
     absences.

2. [A Defence of Elo for Sumo (Sketch)](../prediction/docs/A%20Defence%20of%20Elo%20for%20Sumo%20%28Sketch%29.md)  
   The best statement of what can presently be claimed. Its deliberately
   narrow conclusion is that one precisely specified Basic Elo model has
   demonstrable predictive information in post-1988 sumo. It also clearly
   separates:

   - discrimination from calibration;
   - effect size from statistical evidence;
   - an existential "this Elo works somewhat" claim from "this is the optimal
     or true rating system."

3. [Basic Elo Predictive Findings](../prediction/docs/experiments/Findings.md)  
   The most useful empirical summary. Basic Elo beats a 50% forecast modestly
   overall, performs better among sekitori, and has a long initial weakness
   largely located in lower-division bouts. It also contains the initialization
   experiments and their limitations.

4. [Toy Elo README](../toy_elo/README.md)  
   The best map of experiments addressing Elo's structural assumptions,
   especially incomplete comparison graphs and weak links between divisions.

5. [Clean Elo README](../clean_elo/README.md)  
   An unusually valuable negative-result document. It reports that Elo broadly
   agrees with chii but does not produce a clean monotonic rank-to-rating
   relationship, and that the discrepancy could not be given a complete
   principled explanation.

## What the documents say Elo is about

The recurring interpretation is narrower and better disciplined than "a
measure of true ability":

> Elo converts relative past results into opponent-sensitive estimates of
> comparative performance and pre-bout probability.

The main attractions are:

- A win is weighted according to how surprising it was.
- Differences between ratings have a probabilistic interpretation.
- Bout updates are transparent and, in ordinary Elo, zero-sum.
- It provides information not contained in simple win counts when schedules
  differ.
- An outcome-only Elo system can be compared against chii without building
  chii into the calculation.

The strongest current empirical claim is modest but real: Basic Elo with
`q=400`, `k=35`, equal entrant ratings, and persistent chronological updates
improves on a 50% forecast over the represented 1989--2026 results. The
improvement is larger for sekitori than for lower-division bouts.

## The principal issues

Across the documents, the important problems are:

- **Initialization:** Giving everyone the same initial rating is obviously
  unrealistic and creates a warm-up period. Retrospective chii-based
  initialization only partly fixes this.

- **Open population and drift:** Bouts are zero-sum, but careers are not.
  Entrants inject their assigned rating and retirees remove their final rating.
  This can move the rating scale over time and undermine cross-era comparisons.

- **Missing historical evidence:** Complete lower-division results begin only
  in 1989. Earlier sekitori arrived with an unobserved lower-division career,
  so plain Elo cannot reconstruct their pre-sekitori information.

- **Incomplete comparison graphs:** Sumo bouts are overwhelmingly local.
  Disconnected divisions can recover internal differences but not their
  relative offsets. Sparse cross-division bouts are therefore crucial.

- **Fixed-`K` fluctuation:** Even if ratings begin at their true values in a
  stationary correctly specified world, fixed-`K` Elo does not settle
  permanently. Ratings continue fluctuating around the underlying structure.

- **Changing strength:** Real rikishi improve, decline, become injured, return
  from absence, and retire. The clean convergence story assumes a much more
  stationary world.

- **Schedule selection:** Torikumi are not random. They are rank-local and may
  depend on current records. Elo predicts the bouts that were arranged; this
  is not the same as modelling how they were selected.

- **Rank disagreement:** Mean Elo is not perfectly monotonic through the
  banzuke. Some apparent lower-maegashira anomalies disappear when positions
  are aligned relative to the actual division boundary, but other reversals
  remain.

- **Lower-division churn:** Very short careers and rapid passage through the
  lowest divisions weaken the connected, persistent rating population that
  Elo implicitly wants.

- **Meaning versus prediction:** A model may predict successfully without
  giving a true or institutionally meaningful measure of ability. Conversely,
  a rank-informed system may provide an interpretable representation while
  being partly circular if used to explain rank.

- **Omitted causes:** Plain Elo describes results but does not explain injuries,
  styles, motivation, importance of a bout, or administrative constraints.

## Experiment packages worth reading

### Prediction

[Prediction README](../prediction/README.md) is the package map.

The experiments establish:

- Overall log-loss improvement of about 1.5% over 50%.
- Better performance for sekitori than sub-sekitori.
- The long apparent warm-up is primarily a lower-division phenomenon.
- Exact-chii retrospective initialization gives only a small benefit and
  worsens sekitori prediction.
- Broad division membership appears to carry more durable initialization
  information than exact chii.
- A fair-coin-history experiment found none of 2,000 simulated histories
  matching the historical probability-staked result.
- Numerical calibration remains a separate open question.

The specifications under
[prediction/docs/experiments](../prediction/docs/experiments) are detailed and
audit-friendly, particularly Proposals 1--6.

### Probability and calibration

[Probability README](../probability/README.md) leads to the calibration work.

This package asks whether Elo-derived probabilities match observed frequencies,
using Brier scores and calibration bins. Its current claim is that simple
rating-derived probabilities behave meaningfully in the well-supported central
probability range. The more detailed result is in
[Results and Findings](../probability/docs/5%20Results%20%26%20Findings.md).

### Toy Elo and comparison-graph structure

[Toy Elo README](../toy_elo/README.md) covers a particularly useful sequence:

- correctly specified full round robin;
- convergence methodology;
- disconnected divisions;
- artificial cross-division bridges;
- historically measured interdivision scheduling;
- evidence-shaped toy bridges;
- boundary-monotonicity experiments.

The important finding is that disconnected divisions cannot share an
identified scale, while a sparse bridge can make them commensurate in the
tested toy worlds. However, the empirically shaped Makuuchi--Juryo bridge does
not reproduce the nearly flat historical lower-Makuuchi rating curve.

Read alongside:

- [What Ratings Might Say About Grand Sumo](../toy_elo/docs/What%20Ratings%20Might%20Say%20About%20Grand%20Sumo.md),
  which contains the best interpretive guardrails;
- [Boundary Monotonicity README](../toy_elo/boundary_monotonicity/README.md),
  the detailed schedule-distortion experiment;
- [Baseline Elo Toy Model](../toy_elo/docs/Baseline%20Elo%20Toy%20Model.md);
- [Incomplete Comparison Progress](../toy_elo/docs/Incomplete%20Comparison%20Progress.md);
- [Evidence Aligned Bridge Model](../toy_elo/docs/Evidence%20Aligned%20Bridge%20Model.md).

### Clean Elo and chii comparison

[Rating Probe Findings](../clean_elo/docs/Rating%20Probe%20Findings.md) is the
detailed report behind the package README.

It documents:

- persistent outcome-only ratings;
- mean restoration to suppress scale drift;
- a strong rejection of a simple monotonic literal-rank relationship;
- disappearance of the headline M12--M18 reversal when ranks are aligned by
  actual distance from the division boundary;
- unsuccessful attempts to make the remaining ordering fully monotonic by
  deleting lower-maegashira observations.

This package explicitly calls itself a failed experiment in the limited sense
that it did not find a complete explanation or uniquely defensible correction.
That makes it one of the most informative documents here.

## More theoretical HTML notes

- [Elo Bottom Line 2](2026%2008%2010%20Elo%20Bottom%20Line%202.html) explains
  why fixed-`K` Elo keeps fluctuating even when initialized at known true
  strengths. It also discusses the Cortez--Tossounian small-`K` result and why
  its explicit sufficient bound is impractically restrictive for ordinary Elo
  parameters.

- [Elo kmax/q continuation](elo-kmax-q-continuation.html) is a more specialized
  examination of the allowed small-`K` bound as `q` changes.

- The HTML plots in
  [Cortez and Tousounian](../Cortez%20and%20Tousounian) appear to be supporting
  parameter/bound visualizations rather than explanatory documents.

## Historical and duplicate material

[Archived Elo Ratings](../../products/make_site2/prose/archive/Elo%20Ratings.html)
is much longer than the current introduction. It contains useful discussion of
inflation, convergence, prediction, banzuke objections, and alternatives such
as Glicko. It is also more speculative and autobiographical, so it should be
treated as research history rather than the current position.

[Elo](../equelo/docs/equelo%20docs/Elo.html) is essentially another polished
copy of the current basic Elo explanation, with a stray `TBD` at the end.

The dated notes [WTF Is This](2026%2004%2016%20WTF%20Is%20This.md) and
[The Grand Plan(s)](2026%2004%2017%20The%20Grand%20Plan%28s%29.md) are useful
for understanding the intellectual development, especially the split between
prediction and representation. They contain conversational and sometimes
stronger claims that the newer prediction and toy-Elo documents qualify.

## Secondary Equelo material

The most Elo-relevant Equelo note is
[Lower-Rank Problems in Equelo](../equelo/docs/equelo%20docs/lower_rank_problems.md).
Although framed around Equelo, it identifies a likely underlying Elo weakness:
high churn and weak connectivity in Jonokuchi and low Jonidan.

[What Is an Equelo Rating?](../../../docs/What%20is%20an%20Equelo%20Rating.md)
is the current project-level statement, but it is mainly useful after reading
the plain-Elo and experimental material.

## Suggested reading order

1. Current `Elo Ratings.html`.
2. `A Defence of Elo for Sumo`.
3. Prediction `Findings.md`.
4. Toy Elo README.
5. `What Ratings Might Say About Grand Sumo`.
6. Clean Elo README and `Rating Probe Findings`.
7. `Elo Bottom Line 2.html`.
8. Equelo documents only where they address initialization, drift, or
   lower-rank problems.
