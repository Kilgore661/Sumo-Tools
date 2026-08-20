# Initial Rating Policy

## Status

This document records the current project decision produced by the M12
investigation. It governs initial ratings for simulations scoped to 1989
onward. It does not define initial ratings for ranks represented only before
1989.

For the investigation, see the
[consolidated research record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md).
For reproduction details, see the
[experiment catalogue](09%20M12%20Experiment%20Catalogue.md).

## Purpose of initial ratings

Initial ratings are entrant priors. Their purpose is to shorten the adjustment
gap before bout evidence accumulates. They are not claims that each chii has
one timeless, precisely measurable intrinsic rating.

This limited purpose changes the standard of success. The values need to be
sensible and operationally useful; they need not be the unique or exact rating
for each chii. Ratings after entry are free to disagree with chii.

## Scope boundary

The adopted construction uses only history from 1989 onward. It is therefore
an initial-rating policy only for simulations over that scope. Every chii that
occurs in the scoped experimental histories receives a value from the
construction.

Historical chii absent from the 1989-onward scope, including M19--M22 and
J15--J24, are not missing values in this policy. They are outside its domain.
Supplying values for them in a simulation beginning before 1989 would be a
separate historical-completion policy requiring its own artifact, provenance
and account. It must not be added to the 1989-onward producer implicitly.

## Construction

The values deliberately combine epistemic evidence with a small number of
teleological choices made for useful entrant initialisation.

### Experimental evidence

1. The 1989-onward M/J fixed-point experiment represents Makuuchi and Juryo by
   position relative to their contemporaneous boundary, with J1e at index 0.
2. The 1989-onward continuous lower-banzuke experiment represents Juryo as
   negative positions above Ms1e and continues one contextual index through
   Ms, Sd, Jd and Jk.
3. Both contextual maps are resolved back onto the literal chii that occurred
   in their scoped histories.
4. The lower-banzuke result receives one appearance-weighted additive shift so
   that it aligns with the M/J result over their shared Juryo observations.

### Constructive choices

1. M/J supplies the Makuuchi values.
2. Juryo is a linear blend: M/J weight falls from 1 at J1e to 0 at J14w, with
   the aligned lower-banzuke estimate receiving the complementary weight.
3. The aligned lower-banzuke result supplies Ms and lower values through
   Jd100e.
4. Values below Jd100e are held constant at the Jd100e value. This prevents the
   lower-index reversal and avoids claiming distinctions where the contextual
   index mixes materially different literal ranks.
5. East and west estimates are combined by an unweighted mean. A singleton
   retains its sole value.

The resulting paired curve is strictly decreasing over the represented
Makuuchi ranks. Its small M/J reversal is retained rather than hidden: M17 is
approximately 1953.25, M18 1951.48 and J1 1953.53. Below that boundary the
curve is broadly decreasing through the useful lower-rank range despite local
noise.

These choices are partly teleological because broad agreement with chii order
is desirable for presentation and entrant priors. They are not presented as
discoveries that history uniquely determines a monotone chii-to-rating map.

## Why no further smoothing is required

Smoothing remains a reasonable policy. Support-weighted isotonic regression
would reproducibly reduce local noise, enforce ordinal presentation and remove
the small M/J reversal. It would be defensible if exact monotonicity were a
requirement of the initial-rating product.

Not smoothing is also reasonable. The paired contextual construction already
supplies sensible 1989-onward entrant values, has a coherent broad shape and
confines the remaining conspicuous reversal to a very small M/J difference
that can be reported and discussed. Its purpose is only to shorten the
initialisation gap, not to assert the uniquely correct value for every chii.

The project therefore chooses not to smooth. This retains the experimental
shape where it is already adequate and avoids imposing additional structure
without an identified practical need.

## Decision record: final rating normalisation

**Decision (2026-08-20): retain the constructed 1989-onward priors without a
final mean-normalisation step.** This is a decision about the rating origin,
not about the shape of the curve. It does not prevent a future consumer from
applying a documented common shift when integration requires one.

### What is and is not normalised

The source fixed-point maps were each normalised during estimation by one
uniform additive shift. The lower map is then aligned to the M/J map by one
further uniform shift. No final recentering is applied after merging or
pairing.

Consequently, the final 1989-onward priors are not normalised to have mean 1517.
For the retained artifacts under
`files/output/Equelo/boundary_reconciliation/2026-08-19_lower_banzuke_merge/`,
the unweighted mean is approximately 1410.744 over the 965 literal east/west
chii and 1411.087 over the 484 paired ranks. Forcing the paired mean to 1517
would add approximately 105.913 points to every prior.

These figures must not be confused with the mean of approximately 1537.936 in
`files/output/Equelo/fixed_supported/master_chii_initial_rating_map.csv`.
That older artifact is a separately completed 1,005-literal-chii map, includes
historical ranks and is not the retained 1989-onward paired table.

The new mean is much lower partly because the 1989-onward construction contains
many lower-division ranks and assigns the flat Jd100e value to every remaining
rank below its cutoff. Those numerous low-valued rows have substantial weight
in an unweighted mean over chii or rank pairs. This is another reason not to
treat the final mean as a property of the rating evidence: it depends on the
chosen completion rule and how far down the banzuke the output domain extends.

### Why expt2's mean does not transfer automatically

This difference from expt2 is expected. Expt2 normalises the unweighted mean
of the keys in the map being solved. Resolving contextual keys onto literal
chii, blending two maps, holding the lower tail constant, and pairing east and
west all change which values are counted and with what multiplicity. The final
mean therefore depends on the representation and enumerated domain; it is not
an invariant property recovered from the bouts.

This follows the existing completion precedent: the directly estimated map is
anchored, but adding or duplicating operational chii does not trigger another
mean-based shift. A final shift would make published levels depend on how many
historical or unsupported slots happened to be enumerated.

In particular, the two final means above differ merely because one counts 965
side-specific chii and the other counts 484 rank pairs. Neither population is
more naturally the expt2 solver's key population. Choosing one of them as the
normalisation domain would therefore add a new convention after the
experimental construction.

### Why no action is required for the present use

For the present intended use, no final normalisation is required. A uniform
shift has no effect on Elo probabilities when it is applied consistently to
every entrant in a complete simulation: only rating differences matter. If a
future consumer mixes these priors with already established ratings, an
unshifted fallback rating, or a map with incomplete coverage, the relative
origin can affect the initialisation gap. That consumer must then state and
test an explicit anchoring policy at the integration boundary rather than
silently renormalising this retained artifact.

### When future us must reconsider the decision

Reconsider the rating origin before using these priors if any of the following
is true:

- the simulation starts with some rikishi already carrying ratings that were
  not initialised from this same prior table;
- an entrant can fall back to a fixed rating such as 1517 because its chii is
  absent from the table;
- 1989-onward priors are combined with a separately constructed pre-1989 table;
- published values must share an explicit numerical origin with Basic Elo or
  another Equelo series; or
- a prospective test shows sensitivity to a common shift because coverage or
  initialisation is not in fact uniform.

In that situation, do not overwrite the retained artifact. Define the
consumer's anchoring population, calculate one uniform shift, record it in the
consumer's provenance, and test the shifted and unshifted alternatives. Do not
rescale the curve or independently adjust divisions: those operations would
change rating differences rather than merely choose an origin.

## Reproduction

The construction is implemented in `src.analysis.equelo.smoothing` as two
data-producing steps. Chart modules only render persisted CSV outputs.

```powershell
python -m src.analysis.equelo.smoothing.boundary_merge `
  --mj-csv files/output/Equelo/fixed_boundary/2026-08-17_14-49-30/all_chii_prior_comparison.csv `
  --lower-csv files/output/Equelo/fixed_lower_banzuke/2026-08-19_18-52-25/lower_banzuke_chii_comparison.csv `
  --cutoff-chii Jd100e `
  --output-csv files/output/Equelo/boundary_reconciliation/2026-08-19_lower_banzuke_merge/literal_chii_merge_candidate.csv

python -m src.analysis.equelo.smoothing.paired_merge `
  files/output/Equelo/boundary_reconciliation/2026-08-19_lower_banzuke_merge/literal_chii_merge_candidate.csv `
  --output-csv files/output/Equelo/boundary_reconciliation/2026-08-19_lower_banzuke_merge/paired_literal_chii_merge_candidate.csv
```

Each producer writes its data before invoking a separate chart renderer. The
metadata files record input hashes, construction rules and output hashes.

## Public-description boundary

Public material may present selected Makuuchi and lower-division landmarks
rather than the complete table. It should say that the values are sensible
entrant priors informed by contextual fixed-point experiments and chosen to
shorten the initialisation gap.

It may show and discuss the small M/J reversal. It must not imply that:

- the values are precise measurements of the ability associated with chii;
- convergence proves that the contextual categories are correct;
- 1989-onward values automatically apply to earlier banzuke structures;
- the remaining local shape has been causally explained; or
- predictive validity follows merely from the construction.

## Work not included in this decision

- inventing or estimating initial values for pre-1989-only chii;
- running a pre-1989 simulation with completed historical priors;
- replacing the current production initial-rating map;
- claiming a predictive advantage over Basic Elo; and
- writing the shorter public-facing explanation.

Any historical extension must be a separate choice and must state explicitly
which initial values it assigns to chii absent from the 1989-onward evidence.
