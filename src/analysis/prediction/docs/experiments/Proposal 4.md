# Proposal 4: Randomized Chii-prior Placebo

## Status

Accepted proof-of-concept experiment following Proposal 3.

## Question

Does the genuine association between Chii and the retrospective initial ratings
used in Proposal 3 improve prediction, or would an arbitrary association between
the same Chii positions and the same set of ratings perform similarly?

This experiment also shows how equal initialization compares with arbitrary
rating differentiation. It does not presume a single complete definition of
"better".

## Fixed inputs

Use the same annotated History, 1989/01 epoch, bout eligibility, chronology and
Basic Elo producer as Proposals 1 and 3:

```text
q = 400
k = 35
eligible result = W/L, irrespective of kimarite
rating identity = RikId
forecast = before the bout update
ratings persist for the complete pass
```

Use Proposal 3's completed `chii_prior.csv` as the prior table. The table is
keyed by authoritative Chii ordinal. Chii strings remain display values and
must not participate in the permutation or lookup.

## Producers

Compare three kinds of initialization:

1. **Equal:** initialize every previously unseen RikId at 1500, as in Proposal
   1.
2. **Genuine Chii:** initialize from the unaltered Proposal 3 Chii-prior table.
3. **Globally randomized Chii:** randomly permute the complete set of prior
   rating values among the complete set of Chii ordinals.
4. **Within-division randomized Chii:** randomly permute prior rating values
   only among Chii belonging to the same actual division.

Each randomized replicate must use one permutation consistently for the whole
chronological pass. Thus every entrant at a particular Chii receives the value
assigned to that Chii in that replicate. Do not draw a new rating for each
rikishi or bout.

For the within-division placebo, the computational groups are Makuuchi, Juryo,
Makushita, Sandanme, Jonidan and Jonokuchi. Every MSD level (Yokozuna, Ozeki,
Sekiwake, Komusubi and Maegashira) belongs to the single Makuuchi group. Derive
the group from the authoritative Chii value; do not infer it from a chii string.
This placebo preserves the complete multiset of prior ratings within each
division while destroying their association with exact rank, number, side and
annotation inside that division.

Permute the completed table, including values that Proposal 3 obtained by
interpolation or an edge rule. Do not reconstruct or re-interpolate the prior
after permutation. A permutation therefore preserves the exact number, mean,
spread and irregularities of the Proposal 3 rating values while destroying
their association with ordered Chii positions.

Run 100 replicates of each placebo with seed `20260807`. Sort the Chii ordinals
in authoritative order and take the corresponding genuine rating values as the
base sequence. The global placebo uses one `random.Random(20260807)` stream;
for each replicate, copy the base sequence and apply `shuffle` once. The
within-division placebo uses a separate `random.Random(20260807)` stream; for
each replicate, copy the base sequence, visit division groups in the order of
their first Chii ordinal, and shuffle the values at each group's positions once.
Assign the resulting values back to the sorted ordinals. Replicates of each
placebo are numbered 1 through 100 in generation order. Record the placebo,
seed and permutation index in the manifest and output.

The known no-Chii History defect for RikId 13011 retains Proposal 3's temporary
rule: use the value attached to the weakest mapped Chii edge in the relevant
mapping. In a randomized replicate this is the randomized value attached to
that edge, not the numerically lowest rating.

## Evaluation populations

Score every producer over the three already-defined populations:

- all eligible bouts;
- bouts in which both participants are sekitori;
- bouts in which both participants are sub-sekitori.

Population membership affects evaluation only. Every eligible bout continues
to update the producer's ratings.

Log loss is primary and Brier loss is secondary. All comparisons are paired in
the sense that every producer forecasts the same represented bouts within an
evaluation population.

## Proof-of-concept summaries

For each population and score, calculate cumulative mean loss from 1989/01
through every basho. Express the genuine and randomized results both as raw
loss and as a difference from equal initialization, where a negative difference
favours the alternative initialization.

Report a compact table at these predeclared horizons:

```text
6 basho
12 basho
30 basho
60 basho
complete represented epoch
```

At each horizon report:

- equal loss;
- genuine-Chii loss and its difference from equal;
- global-random and within-division-random median, 5th percentile and 95th
  percentile;
- for each placebo, the number of replicates with loss lower than genuine Chii;
- for each placebo, the number of replicates with loss lower than equal.

"Lower" in both counts means strictly lower. Define the randomized median as
the mean of ordered values 50 and 51. Define the 5th and 95th percentiles as
ordered values 5 and 95 respectively. This simple order-statistic convention
avoids an implementation-dependent interpolation rule in the proof of concept.

These horizons are descriptive landmarks, not competing definitions from
which the most favourable result may be selected.

## Required artifacts

Write:

- a manifest recording the source History, source prior table, their digests,
  model definition, replicate count and seed;
- a CSV containing every permutation's Chii-ordinal-to-rating assignment;
- a CSV containing per-replicate results at every declared horizon;
- a CSV containing the cumulative genuine, equal and randomized-envelope
  series by basho and evaluation population;
- a responsive Plotly CDN chart showing the genuine difference from equal
  against both randomized medians and 5th-to-95th-percentile bands;
- an execution-time text artifact containing the measured total wall-clock
  duration;
- a short Markdown report describing the comparisons without selecting a
  preferred horizon after seeing the results.

The permutation-assignment CSV is an audit artifact. It must use Chii ordinal
as data and may include a Chii string only as a human-readable aid.

## Interpretation

The randomized distribution is a placebo distribution for the association
between Chii and prior rating. It is not a sampling confidence interval for the
historical bouts and must not be labelled as one.

If genuine Chii performs better than most randomized mappings, that is evidence
that the association between Chii and the prior values carries predictive
information. If equal initialization performs better than most randomized
mappings, arbitrary differentiation is harmful. These two findings can both be
true.

With only 100 replicates per placebo, ranks and percentile bands are
exploratory. This
proof of concept will not add a basho bootstrap, simultaneous bands, a formal
significance threshold or a fitted definition of warm-up. Those refinements
should be considered only if the randomized comparison proves informative.

The command-line run must print progress after every completed Elo pass. The
progress line must include completed and total pass counts, percentage, elapsed
wall-clock time and an estimated remaining duration. On completion it must
print the total execution time and write the same duration to
`execution_time.txt` in the output directory.

As in Proposal 3, the genuine ratings and every placebo permutation retain the
same retrospective use of future outcomes. The experiment isolates the value
of the Chii-to-rating association within that oracle construction; it does not
turn the prior into an out-of-sample model.
