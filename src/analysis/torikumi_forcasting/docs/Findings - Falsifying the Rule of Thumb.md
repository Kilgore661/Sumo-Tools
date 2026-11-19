# Can We Falsify the Torikumi Rule of Thumb?

## Question

The forum rule of thumb was:

> Wrestlers are sorted by wins, with rank breaking ties, then paired from the
> top down without repeating an opponent already faced in the basho.

The natural experimental question is whether historical torikumi falsify this
account.  The question is not completely well-defined because the original
claim is informal.  In particular, it does not specify exactly how an
ineligible top-down pairing is replaced, how odd populations are handled, or
whether "the way the last days usually go" is intended as a deterministic
algorithm or only as a broad tendency.

We therefore cannot falsify every interpretation of the words.  We can test
explicit, reasonable operationalisations of them.

## Operationalisations tested

Both experiments forecast Days 11 to 15 from wins known through Day `d - 2`.
Rikishi are sorted by wins and then by chii.  A pair is prohibited if the two
rikishi have already been scheduled against each other in the basho or were in
the same heya at the time.  The experiments do not represent familial
restrictions.

The first experiment applies the rule literally and greedily: take the first
remaining rikishi and pair him with the first eligible rikishi below him.  It
does not reconsider an earlier choice if that leaves later rikishi without a
legal opponent.

The second experiment gives the underlying idea a more favourable test.  It
finds a complete legal matching, where one exists, that minimises the total
distance between paired rikishi in the standings order.  This removes errors
caused merely by the greedy algorithm taking an early edge that blocks a
better complete solution.

The forecast population is conditional on the makuuchi rikishi represented in
the published target-day torikumi.  Cards with more makuuchi-juryo
participants than required by population parity are excluded, because the
experiments do not attempt to forecast the JSA's additional inter-division
selections.  This excluded 710 of 2,055 candidate cards, leaving 1,345 cards
from completed basho between 1958/01 and 2026/09.

## Results

| Measure | Greedy | Constrained |
|---|---:|---:|
| Evaluated cards | 1,345 | 1,345 |
| Mean per-card pair recovery | 11.47% | 12.53% |
| Recovered pairs | 2,846 / 25,039 | 3,111 / 25,039 |
| Pair-weighted recovery | 11.37% | 12.42% |
| Exact reduced cards | 0 | 0 |
| Complete/optimal solutions | 986 | 1,345 |

Pair recovery asks whether the same two rikishi were paired in the forecast
and the published torikumi.  It ignores East/West presentation and bout order.
Thus, recovery near 12% means roughly one actual intra-makuuchi bout in eight
was recovered; it does not mean that 12% of whole cards were correct.  No
forecast reproduced an entire reduced card.

The globally optimised formulation improved mean recovery by only 1.06
percentage points.  All 1,345 constrained problems had a solution proved
optimal, so the poor fit cannot be attributed to greedy dead ends or failure
to find the model's ideal matching.  On the recent 58-card comparison split,
the constrained model recovered 11.78% on average, broadly consistent with
the full historical result.

## Conservative falsification claim

The evidence strongly falsifies the tested rule as an accurate deterministic
procedure for reconstructing late-basho torikumi.  It also shows that replacing
the literal greedy implementation with the most compact global pairing under
the same standings idea does not rescue it.  The historical cards are mostly
different even when the algorithm returns a complete, optimal solution.

That is narrower than claiming that the forum statement is false under every
possible interpretation.  These experiments do **not** establish that:

* wins and rank have no influence on the JSA's choices;
* similarly placed rikishi are not more likely to meet than arbitrarily
  selected rikishi;
* every reasonable top-down algorithm would perform equally poorly;
* an omitted restriction or objective could never improve the fit; or
* the JSA follows, or does not follow, any particular unpublished procedure.

The absence of familial restrictions is a real qualification.  Sibling cases
are believed to be rare, and so are unlikely to explain a discrepancy of this
size, but that has not been measured here.  A single prohibited edge can also
alter several downstream greedy choices.  The safe conclusion is therefore
not that family relationships have no effect, but that the current evidence
gives no reason to expect their addition alone to transform the result.

Nor have we searched a family of adjusted models for the best historical fit.
Other tie-breaking rules, objectives, rank windows, score groupings or
additional inferred preferences might improve recovery.  Trying them after
seeing these results would answer a new model-development question and would
need new evaluation data or an explicit allowance for exploratory fitting.
Without that discipline, repeated adjustment risks converting the exercise
from testing the stated rule into overfitting an increasingly different rule
to the known torikumi.

## Conclusion

The rule of thumb may retain some value as loose commentary: late-basho bouts
often involve rikishi with records relevant to one another.  It is not
supported as a usable pairing algorithm by either of the two precise versions
tested here.  Calling the informal statement itself conclusively falsified
would overstate what an underspecified claim permits; calling these natural
and comparatively charitable operationalisations falsified is justified.

The numerical evidence is preserved in:

```text
files/output/analysis/torikumi_forcasting/greedy_2026-11-19_12-03-14
files/output/analysis/torikumi_forcasting/constrained_2026-11-19_12-24-50
```
