# Draft: Inter-division Equelo updates and rating-mass conservation

## Purpose

This note records the reasoning behind a change to the Equelo bout-update rule for bouts where the two rikishi have different K-factors.

The change is not intended as a redesign of the K-factor policy. It is a correction to how the existing policy is applied. If a rikishi's K-factor represents how responsive that rikishi's rating should be, then each rikishi's own K-factor should be used when updating that rikishi's rating.

The note also explains why the loss of per-bout rating-mass conservation in cross-K bouts is not expected to have a material effect on the overall Equelo system.

## What changed

Before the change, the rating update for a scored bout effectively did this:

```python
expected_a = expect(rating_a, rating_b)
actual_a = 1.0 if rikishi_a_won else 0.0

k = k_factor_for(rikishi_a)
delta = k * (actual_a - expected_a)

rating_a += delta
rating_b -= delta
```

This meant that the same absolute rating movement was applied to both rikishi. The bout was zero-sum: one rikishi gained exactly what the other rikishi lost.

That is fine when K is constant, because both rikishi have the same K-factor. It is also fine for same-K bouts under a divisional K policy.

It is not fine for cross-K bouts. Under the FIDE-style divisional K policy, two rikishi in different divisions can have different K-factors. The old rule selected the K-factor from the first rikishi in the recorded bout pair and applied that K-factor to both rikishi. In an inter-division bout, the size of the rating movement could therefore depend on bout ordering rather than on the rikishi being updated.

After the change, each rikishi is updated with that rikishi's own K-factor:

```python
expected_a = expect(rating_a, rating_b)
actual_a = 1.0 if rikishi_a_won else 0.0

expected_b = 1.0 - expected_a
actual_b = 1.0 - actual_a

k_a = k_factor_for(rikishi_a)
k_b = k_factor_for(rikishi_b)

delta_a = k_a * (actual_a - expected_a)
delta_b = k_b * (actual_b - expected_b)

rating_a += delta_a
rating_b += delta_b
```

With constant K, this is exactly equivalent to the old rule, because `delta_b == -delta_a`. With different K-factors, this is no longer necessarily zero-sum.

## What this change is and is not about

This change is not a justification of constant K versus divisional K. It is about how to apply whichever K policy has already been chosen.

For constant K, the change has no effect on ratings. Every bout remains zero-sum, and the old and new formulae are equivalent.

For FIDE-style divisional K, the change definitely affects ratings in cross-K bouts. This is intentional. The old behaviour contained an ordering artefact: the first recorded rikishi's K-factor controlled both rating updates. The new behaviour removes that artefact.

The main question is therefore not whether the change has any effect. It does. The question is whether the effect matters materially for the overall Equelo system.

## Rating-mass conservation in closed and open systems

Rating-mass conservation can be important in a closed classical Elo system.

By a closed system, this note means a fixed group of competitors: everyone is present from the beginning, no one joins, no one leaves, and all rating changes come from bouts inside that fixed population. In such a system, if every bout is zero-sum, total rating mass is constant. Since the number of competitors is also constant, the population mean is constant.

This helps explain why rating inflation is not expected in the pure closed case. Ratings are only redistributed among a fixed population, and competitors of equal intrinsic skill are equally likely to gain points. There is no entry/exit mechanism that gives later competitors access to more rating mass than earlier competitors of the same intrinsic strength.

That intuition does not carry over to an open system.

In an open pure Elo system with no correction, rating mass enters with new competitors and leaves with departing competitors. The system is mass-conserving only if the rating mass brought in by entrants exactly balances the rating mass removed by leavers. There is no reason for this to be true.

In systems like chess and sumo, the expected net flow is positive. Low-ranking competitors enter the system with fresh rating points. Many lose to established competitors and then leave with fewer points than they brought in. The difference remains with the competitors who stay. Stronger and longer-lasting competitors therefore have repeated access to rating mass brought in by successive cohorts of entrants.

Top competitors eventually leaving removes rating mass, so the real question is the net flow:

```text
net rating-mass flow = rating mass entering with joiners - rating mass leaving with retirees
```

In chess and sumo-like systems, the claim is that this net flow is positive. That is the inflation mechanism: a rating that looked exceptional at one point in the evolution of the system can look less exceptional later because later strong competitors have had access to more accumulated entrant rating mass.

This is why bout-level mass conservation is not the decisive property in an open Equelo system. Even if every bout were zero-sum, entry and exit would still create system-level mass flows.

## Why losing per-bout conservation is acceptable here

The dual-K change creates a second source of rating-mass change:

1. entry/exit mass flow, caused by rikishi joining and leaving the active population;
2. cross-K bout mass flow, caused by using different K-factors for the two rikishi in a bout.

The second source only exists when the two rikishi have different K-factors. In a constant-K run, or in a same-K bout under divisional K, the bout is still zero-sum.

For a cross-K bout, the mass change is:

```text
delta_a + delta_b = (K_a - K_b) * (actual_a - expected_a)
```

Since `actual_a - expected_a` is between `-1` and `1`, the absolute mass change in a single affected bout is bounded by `abs(K_a - K_b)`.

This is not conceptually alarming in Equelo's setting. Equelo is already an open historical system. System-level mass conservation was already absent unless entrant and retiree flows happened to balance exactly. The important issue is therefore not whether each local update is zero-sum. The important issue is whether the rating scale remains stable enough for the intended comparisons.

The change fixes a real local error: using one rikishi's K-factor to update both rikishi in an inter-division bout. The cost is that cross-K bouts are no longer zero-sum. In an open system with mean-preservation machinery, that cost is expected to be very small.

## Expected impact on process ratings

The change definitely alters ratings under FIDE-style divisional K, but the overall effect on process ratings is expected to be very small.

The reason is not that the change is a no-op. It is not. The reason is that the added mass term is limited to cross-K bouts. These bouts are relatively rare compared with all bouts, and the amount of mass created or destroyed in any one affected bout is small compared with the total active rating mass.

The existing closed-mode Equelo machinery already adjusts for open-system mass imbalance. Before the change, the imbalance to be absorbed came from entry and exit. After the change, the imbalance also includes the small amount of rating mass created or destroyed by cross-K bout updates.

The expected result is that the new rule removes the ordering artefact while making only a very small difference to long-run published ratings over the 50+ year history.

This remains a quantitative claim to verify.

## Expected impact on fixed-supported Equelo

The fixed-supported pipeline uses the same bout-update rule while solving for initial ratings. Since the dual-K change is expected to make only small changes to the forward rating process, the fixed-supported solution is also expected to remain stable.

This is an inference, not a measured guarantee. Informally, the fixed point process was tried after the change and appeared to behave normally: there was no obvious instability, divergence, or large visible shift in the resulting ratings. That is encouraging, but it is not a substitute for a before/after audit.

## What needs attention

These are the issues that should be checked before treating the change as fully audited:

- Quantify how many bouts are cross-K / inter-division bouts under the FIDE-style K configuration.
- Quantify the total rating mass created or destroyed by the dual-K rule.
- Compare the size of that mass term with the existing entry/exit mass adjustments.
- Compare before/after process ratings against the `Equelo1` tag.
- Compare before/after fixed-supported initial ratings and final process ratings.
- Check whether any published rankings, landmarks, records, or make_site2 outputs change materially.

## What may need attention

These issues may need follow-up depending on the measured impact:

- Diagnostics that assumed every scored bout should be exactly zero-sum may need to be reframed.
- Documentation that treats per-bout rating-mass conservation as a core Equelo invariant may need to be updated.
- Any downstream metric that normalises movement by K should be checked to ensure it uses the K-factor that was actually applied to the rikishi being measured.

## What does not need attention

These are red herrings for this change:

- Constant-K ratings are not materially affected, because the old and new formulae are equivalent when `K_a == K_b`.
- Same-K bouts under divisional K are not materially affected for the same reason.
- The change should not be rejected merely because cross-K bouts are no longer zero-sum. Equelo is an open historical system, and system-level mass conservation was already absent unless entrant and retiree flows happened to balance exactly.
- The change is not an argument for or against the FIDE-style K policy. It is an argument that, once a K policy assigns different K-factors to different rikishi, each rikishi should be updated using their own K-factor.

## TBD measurements

The following measurements should be made against the `Equelo1` tag and the post-change branch:

1. Count affected bouts:
   - total scored bouts;
   - cross-division bouts;
   - cross-K bouts;
   - cross-K bouts as a percentage of all scored bouts.

2. Measure cross-K mass creation/deletion:
   - per bout;
   - per basho;
   - cumulative over the full history;
   - distribution of positive and negative mass changes.

3. Measure active-population adjustments:
   - before the dual-K change;
   - after the dual-K change;
   - difference between the two distributions.

4. Measure process-rating deltas:
   - per rikishi;
   - per basho;
   - final published ratings;
   - top-N ranking changes.

5. Measure fixed-supported effects:
   - convergence behaviour;
   - solved initial-rating deltas;
   - final process-rating deltas;
   - visible changes in published make_site2 outputs.

## Current conclusion

The dual-K change is the right local rule: each rikishi's rating update should use that rikishi's K-factor.

The change is exactly neutral for constant-K bouts and same-K divisional bouts. It changes cross-K bouts, especially inter-division bouts under the FIDE-style divisional K configuration. That is the intended correction.

The loss of per-bout mass conservation in those cross-K bouts is not a reason to keep the old rule. Per-bout mass conservation is conceptually important in closed classical Elo systems, but Equelo is an open historical system. In an open system, system-level mass conservation is already broken by entry and exit unless those flows exactly balance.

The relevant question is therefore materiality, not purity. The added mass term from cross-K bouts is expected to be very small relative to the existing open-system mass flows and the total active rating mass. The fixed-supported solution is also expected to remain stable, though that still needs a quantitative before/after check.
