# Divisional Averages

## Status

This is an experimental analysis package. It starts from the global-mean
Elo-58 checkpoint at commit `244f476`. It must not silently replace that
baseline or P1.

## Why this experiment exists

The first complete-history replay starts in January 1958 from P1-derived
initial ratings and uses the established post-1988 Elo-89 dynamics. Its results
are broadly credible: the complete-history and P1 chii maps have strongly
similar overall and within-division ordering, post-1988 predictive performance
is not materially damaged, and the elite historical ratings are recognisable.

The replay nevertheless produces an important infelicity. Relative to P1, its
one-pass implied chii map places sekitori systematically higher and all four
sub-sekitori divisions lower:

| Division | Mean complete-history minus P1 |
|---|---:|
| Makuuchi | +149.273 |
| Juryo | +39.552 |
| Makushita | -35.350 |
| Sandanme | -35.783 |
| Jonidan | -12.624 |
| Jonokuchi | -43.761 |

The pre-1989 evidence is much more complete for sekitori than for
sub-sekitori. It has therefore occurred to us that persisting one global
average may allow population effects arising in poorly observed lower
divisions to alter the relative rating levels of divisions whose bouts are
well observed. The candidate idea is to persist **divisional averages rather
than only a global average**.

This is a hypothesis about the cause of the observed displacement, not yet an
explanation. The words "inflation" and "deflation" remain provisional until a
mechanism has been demonstrated.

## Questions

The package has two purposes.

### 1. Empirical comparison

Can a principled divisional-average policy give a better match between the
complete-history and post-1988 statistics while retaining the useful
properties of the established model?

At minimum the experiment must compare:

- the 1989-onward control run under global and divisional policies;
- complete-history and P1 chii/rating maps, overall and by division;
- January 1989 boundary ratings;
- predictive log and Brier scores on the same declared bout populations;
- elite and other production-facing sanity checks; and
- the size and destination of every population correction.

A better match must not be declared merely because the six divisional mean
differences become smaller. Within-division ordering, individual ratings,
predictions and behaviour at promotion boundaries also matter.

### 2. The epistemological and teleological boundary

When does a correction represent a defensible model of rating-population
turnover, and when are we making up a mechanism to obtain numbers we already
want?

It is legitimate to notice a possible mechanism, state it independently and
test its consequences. It would be circular to choose separate divisional
anchors or correction rules simply because they reproduce P1 or make a desired
historical ranking. P1 itself is an entrant-initialisation policy, not ground
truth for mature ratings.

The experiment must therefore:

1. specify the policy before examining its detailed results;
2. change one population-accounting principle at a time;
3. retain the global-mean replay as an unchanged control;
4. report adverse and favourable results symmetrically;
5. distinguish a result being closer to P1 from it being better supported; and
6. reject special cases introduced only to repair particular divisions,
   chii or rikishi unless they have an independent sumo or statistical basis.

## First declared experiment: P2

The first experiment obtains an equivalent to P1, provisionally called P2, by
solving a fixed point over the same post-1988 history while persisting six
divisional averages.

The specification is fixed before inspecting P2:

1. each target is the unweighted mean of the literal chii ratings belonging to
   that division in P1;
2. the initial neutral prior assigns every chii its division's target;
3. after entrants, departures, promotions and demotions have established a
   basho's active population, every active member of a division receives one
   common shift which restores that division's target mean;
4. after the eligible bouts, every active division is restored again by one
   common within-division shift;
5. basho-start ratings are aggregated by literal chii exactly as in the P1
   producer;
6. only literal chii with at least 60 observations estimate themselves and
   participate in the repeated map recentering;
7. that supported map is recentered separately within each division, using the
   same support-proportional `alpha = 1` allocation as P1;
8. unsupported chii are completed after every iteration from the nearest
   supported literal chii by ordinal, with ties resolved upward; and
9. convergence is measured over the supported map.

The requested year interval is enforced after loading. This matters for the
live store, which can return the complete History even when the connector is
given a narrower interval; P2 must use the same post-1988 domain as P1.

The fixed targets are:

| Division | P1 unweighted literal-chii mean |
|---|---:|
| Makuuchi | 2196.681392 |
| Juryo | 2030.208687 |
| Makushita | 1805.225395 |
| Sandanme | 1566.466863 |
| Jonidan | 1345.143954 |
| Jonokuchi | 1368.350951 |

This is genuine divisional-mean persistence, not merely delivery of a global
correction within the division that generated it. Within-division differences
are preserved by each basho shift; cross-divisional differences may change.
Because historical division sizes vary, fixing all six divisional means does
not also fix the population-weighted global mean.

Run the full fixed point with:

```powershell
python -m src.analysis.divisional_averages `
  --start 1989 --end 2026 --zip
```

Every iteration is printed. The overall line reports the convergence delta,
the chii responsible and replay scores. Six following lines report the raw map
mean before recentering, the fixed target, mean and absolute P2-minus-P1
difference, and the current prior range. The retained artifacts are under
`files/output/analysis/divisional_averages/p2/`:

- `prior.csv` is the P1-compatible P2 candidate prior;
- `p1_p2_literal.csv` gives the chii-by-chii comparison with P1;
- `iterations.csv` retains the overall console figures;
- `iteration_divisions.csv` retains the six divisional lines;
- `prior_iterations.csv` retains every chii value at every iteration;
- `chii_identifiability_audit.csv` records total, fresh-initialisation and
  carried-rating observations, supported status, completion source and final
  iteration movement for every chii;
- `final_replay_basho_division_adjustments.csv` audits every basho-start and
  basho-end correction in the replay of the final P2 map; and
- `p1_p2_summary.csv`, `manifest.json` and `findings.md` summarise the result.

Other meanings of "divisional averages" remain possible future experiments,
but they are not silently mixed into P2.

## Why the supported domain was reinstated

The first literal-chii implementation iterated every observed chii. With the
loose default tolerance of 10 it appeared to converge after 14 iterations.
A run with tolerance 1 showed that this was only a threshold crossing: the
maximum change reached a minimum of about 5.959 at iteration 41 and then grew
to 13.134 at the 200-iteration limit.

The failure is strongly localised. At iteration 200 the maximum changes in
Makuuchi, Juryo, Makushita and Sandanme were respectively about 0.002, 0.001,
0.004 and 0.008. Jonidan had one singleton chii above 1 point. Jonokuchi had 16
chii above 1 point and supplied all ten chii above 2 points. `Jk73w`, with only
two observations, moved by 13.134 points.

This is not evidence that a rikishi ranked Jk73w has an extraordinary latent
strength. Both Jk73w observations were fresh initialisations: their
basho-start ratings came directly from the prior being solved, followed by
that basho's Jonokuchi start correction. No rating carried forward from an
earlier bout contributed independently to either observation. Consequently
the next Jk73w estimate was approximately its previous value plus the mean of
those start corrections and its share of the post-replay recentering. The
calculation was learning principally from its own input. `Sd101e` is an
analogous singleton, although its correction and hence its drift are much
smaller under the present support-proportional recentering.

The pathology is broader than those two memorable ranks. The iteration-200
audit found 17 chii moving by at least one point: 16 Jonokuchi chii and one
Jonidan singleton. No chii with at least 60 observations moved by one point.
More importantly, 15 literal chii had no carried observations at all: 14 were
Jonokuchi and the other was Sd101e. Raw appearance count is therefore an
imperfect proxy for identifiability, but fresh-versus-carried counts make the
self-reference visible.

The threshold of 60 is not selected after seeing these figures. It is the
numerical support threshold declared and used by the earlier Tranche 1
`fixed_supported` experiment, where the same rare-chii feedback problem was
identified. That earlier experiment counted appearances after its rank-family
collapse; P2 applies 60 to its already-declared literal-chii domain. Thus this
reuses a pre-existing cutoff and completion principle without pretending the
domains are identical. Unsupported chii do not estimate themselves or receive
repeated map corrections; they are completed from the nearest supported chii.
The new audit table preserves the evidence needed for a later comparison
between raw support and a potentially more principled carried-observation
rule.

This change is an investigation, not a conclusion that threshold 60 is the
correct production boundary. The next full run asks whether removing the
known underidentified feedback restores genuine convergence, what structure
is retained in well-supported Jonokuchi, and whether any instability remains
through coupling to the completed tail.

The first thresholded runs exposed and then corrected a bout-domain defect in
this package: binary W/L results whose kimarite field was blank had been
excluded alongside fusen. Approximately 33,522 post-1988 bouts were affected,
almost all in the four lower divisions. A blank kimarite is not a blank result;
the corrected replay excludes fusen but rates these W/L outcomes. Results made
before this correction are retained as diagnostic history, not comparable P2
candidates.

## Initial success criterion

The idea remains worth pursuing if a policy stated on first principles:

1. has no material adverse effect on the complete 1989-onward control;
2. reduces the unexplained sekitori--sub-sekitori displacement in the
   complete-history run;
3. preserves credible within-division structure and production-facing results;
   and
4. admits a clear explanation that does not depend on knowing the desired
   output in advance.

Passing these conditions would justify further investigation, not automatic
adoption as a future Equelo2.

## Next experiment: complete history from P2

Fixed-point convergence was a productive diagnostic, not the goal of this
branch. The threshold-60 calculation showed that unrestricted iteration was
being destabilised by underidentified chii recycling their own priors. It did
not establish that divisional averages are the right population policy, and
raising the threshold to make the lower-rank curve look more plausible would
be teleological tuning.

The direct test of the hypothesis that motivated this package is therefore a
single complete-history replay from the converged threshold-60 P2. It:

1. starts in January 1958 from the completed P2 literal-chii map;
2. completes historical-only chii from the nearest supported P2 chii above in
   the same division;
3. archives individual ratings through banzuke gaps and restores them on a
   later proper-rank appearance;
4. applies the six fixed divisional targets at every basho start and end;
5. rates every represented binary W/L result other than fusen, irrespective of
   whether a kimarite is recorded;
6. constructs the implied full-history literal-chii map from all basho-start
   observations using the same threshold, divisional recentering and
   nearest-supported completion policy as P2; and
7. compares that map with P2 on their common literal-chii domain.

This comparison, rather than the enforced active divisional means, answers
whether sekitori ratings still rise when the pre-1989 results are incorporated.
The experiment also retains predictive scores, every divisional population
correction, division-boundary gaps and each rikishi's last known rating so that
a smaller division-level displacement cannot conceal a new distortion.

Run it from the tight threshold-60 P2 with:

```powershell
python -m src.analysis.divisional_averages.full_history `
  --p2-prior files/output/analysis/divisional_averages/p2_epsilon_0_001_blank_fixed/prior.csv
```

Outputs are written to
`files/output/analysis/divisional_averages/full_history_from_p2_blank_fixed/`.
