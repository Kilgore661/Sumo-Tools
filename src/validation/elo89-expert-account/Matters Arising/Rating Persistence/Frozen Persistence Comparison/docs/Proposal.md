# Proposal: frozen rating persistence across represented absences

## 1. Purpose

Determine the mechanical, predictive and publication-relevant consequences of
preserving a rikishi's last Elo-89 rating while he is absent from the
represented active population.

The present Elo-89 replay deletes a departing rikishi's rating. If he later
returns, he is indistinguishable from a first entrant and is initialised from
the prior associated with his current chii. The completed census shows that
this happens 437 times in the selected Elo-89 interval. Almost every case is
an administrative cycle at the Jonokuchi/mae-zumo boundary rather than a
retirement followed by a new career.

The experiment will test a narrower rule:

> Absence from the represented active population supplies no new rating
> evidence. Preserve the last rating unchanged until the rikishi returns or
> remains absent permanently.

The experiment is not intended to select a general inactivity or injury model.
It compares one explicit persistence rule with the current reset rule.

## 2. Established inputs

This work follows the cumulative validation sequence. It will use:

- the Elo-89 epoch beginning `1989-01`;
- the repaired frozen History through `2026-09`;
- all represented binary W/L results accepted by the Kimarite work;
- the accepted epsilon-10 P1-WL prior;
- the existing Elo-89 q, divisional K, forecasting, update and normalisation
  equations; and
- the existing exclusion of mae-zumo-versus-mae-zumo results.

P1-WL is a fixed input to this experiment. Its derivation, epsilon and
comparison with P1 will not be reopened.

The intended frozen sources are:

```text
History:
files/output/Historys/1958_01 to 2026_11.zip
SHA-256 afddcc2a77aa237d539073008bf46414989eb766cad8b281cf719963141793ca

P1-WL:
files/output/validation/elo89-expert-account/Matters Arising/Kimarite/
  output/p1-wl-comparison-2026-10-27-canonical/p1-wl/prior.csv
SHA-256 6f5a3bc59dcdbd279e150f53ef0848ae658f2ee72b1371174976c6387cb70486
```

The implementation must verify and record the actual identities rather than
silently relying on these prose values.

## 3. Controlled policies

Run two chronological replays over identical basho and bouts.

### 3.1 Control: reset on return

Reproduce the present Elo-89 lifecycle policy:

1. remove a rikishi's rating when he leaves the active population;
2. remove his rating initialisation source while retaining the existing
   cumulative rated-bout counter; and
3. if he returns, initialise him from P1-WL at his current represented chii.

This must reproduce the accepted P1-WL exact replay, not merely approximate
its behaviour.

### 3.2 Candidate: frozen archival persistence

At departure:

1. copy the rikishi's rating and its provenance into inactive archive state;
2. remove him from the active population; and
3. leave the archived rating numerically unchanged for the entire absence.

The cumulative rated-bout counter follows the same rule in both replays: it is
retained across absence but cannot increase without a selected bout. Rating
support accounting is therefore not an additional controlled difference.

While absent, the rikishi:

- is excluded from active means and all population normalisation;
- receives no bout update;
- receives no common rating shift; and
- cannot affect forecasts or other ratings.

If he returns, restore the archived rating and provenance before the ordinary
start-of-basho active-population adjustment. His already retained cumulative
bout counter continues unchanged. From that point he participates normally in
normalisation, forecasts and bout updates. If he never returns, the archive
remains inert and has no numerical effect on the replay.

For a repeated gap, archive the newly informed rating at the later departure;
do not restore the value from an earlier gap.

### 3.3 Why the archive is literally frozen

At disappearance the data do not say whether the rikishi has retired,
temporarily entered banzuke-gai or mae-zumo, or will later return. Applying
subsequent population shifts would assume continuing membership in a
population from which he is absent. A frozen archive instead preserves the
last evidence-based point estimate without making a claim about continuing
competition.

Staleness and uncertainty are distinct from the point estimate. This tranche
will not introduce decay, confidence intervals or volatility parameters.

## 4. Population and event definitions

Use the exact Elo-89 active-population definition: ranked banzuke members plus
any additional participants admitted by the unchanged rated-bout selection.

A *return* for the comparison is an active rikishi who has archived candidate
state but was absent from the immediately preceding active population. The
event must be linked to the corresponding ranked-gap census observation where
possible. Any mismatch between replay returns and the 437 census events must
be explained; it must not be normalised away.

The epoch begins with no earlier rating state. A rikishi whose pre-1989 career
is not represented inside the replay is a first entrant, not a returnee. This
experiment will not import ratings from before the declared epoch.

## 5. Phase A: implementation and equivalence controls

Implement the experiment beneath `src.validation`, leaving the canonical
`src.analysis.elo89` and `src.products.make_site89` behaviour unchanged.

Before assessing persistence, prove that the control replay is equivalent to
the accepted P1-WL replay:

- identical selected bout identities, order and outcomes;
- identical initial ratings and initialisation sources;
- identical forecasts and updates;
- identical start, daily and end rating snapshots;
- identical active counts and population adjustments; and
- identical raw, rated, fusen, draw and other exclusion counts.

Any difference in this equivalence check is an implementation failure, not an
experimental result.

Add focused synthetic tests covering:

- a permanent departure whose archived rating never matters again;
- a one-basho absence and return;
- a multi-basho absence;
- repeated gaps for one rikishi;
- a first entrant who must still receive P1-WL;
- identical cumulative rated-bout counters under both policies;
- exclusion of inactive archives from active means;
- no shift or update to archived ratings;
- restoration before the ordinary return-basho start adjustment; and
- deterministic output from identical inputs.

## 6. Phase B: event-level mechanical comparison

Write one row for every return event, including:

- event and rikishi identity;
- departure and return basho;
- departure and return chii and division;
- gap length and intervening source-status classification from the census;
- rated-bout support at departure;
- frozen candidate rating at departure and immediately before restoration;
- P1-WL control initialisation at the return chii;
- raw control-versus-candidate difference before return-basho normalisation;
- ratings under both policies after the common start adjustment;
- first post-return rating difference; and
- whether the event is Sokokurai or a Jonokuchi boundary cycle.

This table should reveal whether the principal differences arise from an
informative established rating, an unstable exact-Jonokuchi prior, or both.
Report distributions as well as the largest inspectable cases. Do not average
Sokokurai into the Jonokuchi population without also showing him separately.

## 7. Phase C: predictive comparison

Pair forecasts by basho, day and competitors and calculate log loss and Brier
score under both policies.

Report at least:

1. the complete replay;
2. every returnee's first rated bout;
3. the first three rated bouts after each return;
4. the first seven rated bouts after each return;
5. the return basho;
6. subsequent returnee bouts while the two policies remain materially
   different;
7. all Jonokuchi-cycle events; and
8. Sokokurai as a single inspectable case.

The event windows must be defined before inspecting scores. If a returnee has
fewer than the requested number of bouts, retain the available observations
and report the denominator. A bout must not be duplicated accidentally when
return windows overlap or a rikishi has repeated gaps; produce both
event-weighted and unique-bout summaries if those answer different questions.

Aggregate whole-history scores are expected to dilute a small lifecycle
effect among many unaffected bouts. They are a safety check, not the only
decision statistic.

## 8. Phase D: propagation and convergence of the difference

Measure how the return policy affects more than the returnee:

- absolute rating difference for the returnee after each subsequent basho;
- basho or rated bouts until that difference first falls below declared
  practical thresholds such as 10, 5 and 1 rating point;
- opponent-rating differences created by post-return bouts;
- per-basho maximum, mean and selected quantiles of absolute differences
  across the active population;
- maximum and mean differences among Makuuchi, Juryo and all sekitori;
- changes to population-normalisation adjustments; and
- the largest individual differences with enough identity information to
  inspect them.

Do not describe disappearance of a difference as mathematical convergence
unless exact equality is actually obtained. Threshold crossings are practical
descriptions of the remaining effect.

The analysis must distinguish direct restoration effects from common shifts
applied to the active population after the return. Archived inactive ratings
must never appear in population-wide difference summaries until restored.

## 9. Invariants

The comparison fails if any of the following is false:

1. both policies use the same History, P1-WL prior, bouts, q and K values;
2. the control exactly reproduces the accepted P1-WL replay;
3. first entrants are identical under both policies;
4. candidate archives receive no updates or shifts while inactive;
5. inactive archives do not contribute to active means;
6. the sole controlled difference is reset versus frozen persistence;
7. every restored rating is linked to a prior active rating for the same
   rikishi identity;
8. the bout domain still excludes `Mz`-versus-`Mz` results;
9. no canonical prior, Elo-89 output or site artifact is overwritten; and
10. all outputs are provenance-bound and reproducible.

## 10. Interpretation and decision

The candidate need not demonstrate a large global predictive improvement.
The substantive case for persistence is that the system should not discard
existing bout evidence merely because its ranked-only representation omits a
continuing administrative stage.

The evidence should support adoption if frozen persistence:

- behaves exactly as specified;
- causes no meaningful predictive deterioration in return-focused or global
  comparisons;
- avoids implausible reset values in inspectable return events;
- creates no unexplained population or sekitori disturbance; and
- leaves any remaining trade-off explicit.

A predictive improvement strengthens the case but is not required to pretend
that sparse return data can determine a universal inactivity model. A material
deterioration, extreme propagation or unexplained invariant failure requires
investigation before a decision.

## 11. Outputs to retain

The full run should write a new timestamped or explicitly named directory
beneath:

```text
files/output/validation/elo89-expert-account/Matters Arising/
  Rating Persistence/Frozen Persistence Comparison/output/
```

Retain at least:

- a manifest with source hashes, parameters, runtime and Git/worktree state;
- control-equivalence results;
- return events with both initialisation treatments;
- paired forecast observations;
- predictive score summaries with denominators;
- per-basho population and sekitori difference summaries;
- largest-difference and threshold-duration tables;
- invariant violations, including an empty table on success; and
- readable findings and a policy recommendation.

The runner must refuse to overwrite an existing complete run and must return a
non-zero status for an implementation failure or invariant violation.

## 12. Non-goals

This experiment will not:

- compare P1 with P1-WL;
- refit or tune P1-WL;
- add, reconstruct or rate `Mz`-versus-`Mz` bouts;
- give Mz a formal chii, ordinal, prior or K value;
- decay ratings or model uncertainty during absence;
- carry active-population shifts into an inactive archive;
- import pre-1989 rating history;
- modify canonical production behaviour;
- build or deploy the website; or
- decide the separate treatment of off-banzuke bout participants.

If frozen persistence is accepted, tracing it through the complete site-data
and website build will be a subsequent tranche, following the pattern already
used for P1-WL.
