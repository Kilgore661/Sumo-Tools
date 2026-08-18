# M12 Experiment Catalogue

## Purpose

This is the reproducibility companion to the
[consolidated M12 research record](08%20M12%20Investigation%20-%20Status%20and%20Next%20Steps.md).
It records the principal experiments in the order in which they changed the
project's understanding. It is not the public explanation of initial ratings.

The current policy derived from this work is recorded separately in
[Initial Rating Policy](10%20Initial%20Rating%20Policy.md).

## Common Equelo settings

Unless a row below says otherwise, the contextual fixed-point experiments used:

| Setting | Value |
|---|---|
| Base rating | 1517 |
| Probability scale `q` | 900 |
| Update policy | Divisional `k` |
| Simulation | Closed-population Equelo |
| Support threshold | 60 key appearances |
| Unsupported keys | Nearest supported key of the same family |
| Map normalisation | One common additive shift to mean 1517 |
| Tight convergence condition | `delta < 0.01` |

Here `delta` is the largest absolute change in any normalised prior between two
successive fixed-point iterations. It is a step-size condition, not a proven
bound on distance from the limiting fixed point.

## 1. Fixed-point literal-chii baseline

### Question

Can a self-consistent chii-to-rating map supply less arbitrary entrant ratings?

### Method and result

Expt2 repeatedly simulated Equelo, aggregated basho-start ratings by
annotation-free literal chii, normalised the map, and used it for the next
iteration. The process converged, but the resulting curve rose from about M12
or M13 towards M17. Very rare chii could be dominated by their recycled prior;
the historical extreme was a Jk73 rating around 3000.

The maintained `fixed_supported` variant addressed the extreme tail by solving
only keys with at least 60 appearances and completing unsupported keys from a
nearby supported key. It removed the Jk73 blow-up but retained the supported
M12--M17 rise.

Sources:

- [`expt2` methodology](../../equelo/expt2/docs/README.md)
- [Initial Rating Audit](../../equelo/docs/2026-06-27%20Initial%20Rating%20Audit.md)
- [Fixed Supported Design](../../equelo/docs/Fixed%20Supported%20Design.md)
- [Lower-Rank Problems](../../equelo/docs/equelo%20docs/lower_rank_problems.md)
- production map:
  `files/output/Equelo/fixed_supported/master_chii_initial_rating_map.csv`

### What it established

- Numerical convergence does not validate the categories being solved.
- Unsupported literal chii need an explicit support/completion policy.
- The M12 pattern is present among directly supported chii and is not removed
  by the Jk73 repair.

## 2. Clean Elo literal-rank and boundary probes

### Question

Does the M12 rise require iterative chii priors, or can it appear in a simpler
rating history?

### Method

The Clean Elo run used a constant entrant rating, persistent ordinary Elo,
divisional `k`, and end-of-basho mean restoration over the complete-results
period beginning in 1989. It compared each rikishi's chii with the rating at
the start of the same basho.

The literal BP4 means rose from 1926.98 at M12 to 2031.73 at M17. The M1--M18
weighted isotonic bootstrap rejected a monotone literal-rank curve under its
naive sampling model (`p = 0.00009999`).

The same ratings were then grouped by paired position above the actual lower
edge of each contemporaneous Makuuchi banzuke. The group nearest Juryo was
9.31 points below the group seven pairs above it, and the boundary-aligned
curve did not reject monotonicity (`p = 0.551945`). Local reversals remained.

Artifacts:

```text
files/output/analysis/clean_elo/rating_probe/2026-07-28_16-47-43
files/output/analysis/clean_elo/monotonicity_probe/2026-07-29_12-34-12
files/output/analysis/clean_elo/boundary_rating_probe/2026-07-29_14-27-29
files/output/analysis/clean_elo/bp4_cutoff_probe/2026-07-30_19-15-08
```

Source: [Clean Elo Rating Probe Findings](../../clean_elo/docs/Rating%20Probe%20Findings.md).

### What it established

- Fixed-point map normalisation cannot be the sole cause of the M12 pattern.
- Literal M numbers are not stable structural positions when banzuke size
  varies.
- Boundary alignment explains much of the large endpoint reversal, but does
  not guarantee an exactly monotone curve.

## 3. Post-1988 Makuuchi--Juryo contextual fixed point

### Question

Does Equelo itself lose the lower-maegashira reversal if priors use position
relative to the contemporaneous M/J boundary?

### Representation

```text
Makuuchi: negative position from the bottom; bottommost is -1
Juryo:    position from the top minus one; J1e is 0
Others:   annotation-free literal chii
```

Keys are assigned from the complete Oracle banzuke before support filtering.

### Reproduction

```powershell
python -m src.analysis.equelo.fixed_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --start-year 1989 `
  --end-year 2026 `
  --epsilon 0.01
```

Matched run:

```text
files/output/Equelo/fixed_boundary/2026-08-17_14-30-30
```

The solve took 55 primary iterations, with final delta
`0.009871514468386522`. Resolved east-side priors fell from approximately 1979
at M12e to 1951 at M18e, whereas the matched literal control retained the tail
rise.

Code: [`fixed_boundary`](../../equelo/fixed_boundary/README.md).

### What it established

- Within the intended post-1988 scope, contextual M/J position removes most of
  the large literal M12--M17 reversal without a monotonicity constraint.
- The initial accidental full-history version answered a different question;
  history scope must be applied before cleaning, assignment, support and solve.

## 4. Post-1988 Juryo--Makushita contextual fixed point

### Question

Can the analogous lower boundary explain the J13/J14/Ms1 shape?

### Representation

```text
Juryo:     negative position from the bottom; bottommost is -1
Makushita: position from the top minus one; Ms1e is 0
Others:    annotation-free literal chii
```

### Reproduction

```powershell
python -m src.analysis.equelo.fixed_jms_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --epsilon 0.01
```

Matched run:

```text
files/output/Equelo/fixed_jms_boundary/2026-08-17_16-07-12
```

The contextual east-side values were approximately J13e 1869.91, J14e
1861.72, Ms1e 1852.91 and Ms2e 1847.87. The literal control placed J14e above
J13e.

Code: [`fixed_jms_boundary`](../../equelo/fixed_jms_boundary/README.md).

### What it established

- The J/Ms boundary coordinate also improved the post-1988 local shape when
  solved independently.
- Independent success at two boundaries did not specify how one Juryo
  observation should contribute to both maps.

## 5. Additive reconciliation of the independent boundary maps

### Question

Can the independently successful M/J and J/Ms maps be merged without changing
their shapes, using only the arbitrary common origin of an Elo scale?

### Method

The reconciliation projected both maps onto their shared post-1988 Juryo
observations. The J/Ms map was permitted one observation-weighted additive
shift; no rank-specific correction was fitted.

### Reproduction

```powershell
python -m src.analysis.equelo.boundary_reconciliation `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --mj-map "files/output/Equelo/fixed_boundary/2026-08-17_14-49-30/master_entrant_prior_map.csv" `
  --jms-map "files/output/Equelo/fixed_jms_boundary/2026-08-17_16-07-12/master_entrant_prior_map.csv"
```

Matched run:

```text
files/output/Equelo/boundary_reconciliation/2026-08-17_21-31-38
```

The best common shift was -7.89 points. After alignment, the mean absolute
residual was 8.78, RMS residual 14.83 and maximum absolute residual 52.60. The
residual changed systematically through Juryo: its top-to-bottom slope was
26.02 points, with top- and bottom-half mean residuals of about -5.24 and
+5.23.

Code: [`boundary_reconciliation.py`](../../equelo/boundary_reconciliation.py).

### What it established

- One common shift cannot reconcile the two independently solved maps.
- A position-dependent fitted correction could make them agree, but would
  replace the desired epistemic merge with another curve-fitting choice.
- This negative result motivated a single joint fixed point in which Juryo
  contributions are defined before solving.

## 6. Joint post-1988 dual-boundary fixed point

### Question

Can the M/J and J/Ms representations be joined using contemporaneous geometry
rather than fitting a merge to the desired curve?

Two rules were tried:

- `nearest`: a Juryo observation contributes to the nearer boundary, splitting
  an exact midpoint equally;
- `linear`: every Juryo observation interpolates between the two boundaries
  according to relative position.

The linear rule is the final version of this experiment.

### Reproduction

```powershell
python -m src.analysis.equelo.fixed_dual_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --start-year 1989 `
  --juryo-weighting linear `
  --epsilon 0.01
```

Matched linear run:

```text
files/output/Equelo/fixed_dual_boundary/2026-08-18_00-08-21
```

The paired curve was close to monotone over the focus range. Selected values
were M17 1948.13, M18 1946.23, J1 1947.37, J13 1856.25, J14 1849.29, Ms1
1845.76 and Ms2 1835.95. A small paired M18--J1 rise remained, while the
J14--Ms1 transition fell in the expected direction.

Code: [`fixed_dual_boundary`](../../equelo/fixed_dual_boundary/README.md).

### What it established

- The two boundary maps can be combined by a declared geometric rule.
- The post-1988 result is encouraging but does not prove that the same mapping
  is stable across historical banzuke regimes.

## 7. Full-history modern-then-combined dual-boundary fixed point

### Question

What happens when the post-1988 map is used to initialise a refinement over all
represented history beginning in 1958, as in Expt2?

### Reproduction

```powershell
python -m src.analysis.equelo.fixed_dual_boundary `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --start-year 1958 `
  --modern-start-year 1989 `
  --juryo-weighting linear `
  --epsilon 0.01
```

Matched tight run:

```text
files/output/Equelo/fixed_dual_boundary/2026-08-18_11-37-18
```

The modern joint solve took 55 iterations and ended at delta
`0.009876162818727607`. The full-history combined refinement took 18 iterations
and ended at delta `0.009574122265`. The literal combined control took 21
iterations and ended at delta `0.008702244042`.

Selected paired joint values were:

| Transition | Change in rating |
|---|---:|
| M15 to M16 | +0.40 |
| M16 to M17 | +1.25 |
| M18 to J1 | -3.42 |
| J10 to J13 | +5.68 |
| J14 to Ms1 | +8.15 |
| Historical J24 to Ms1 | +7.67 |

An earlier run with epsilon 1 is under
`files/output/Equelo/fixed_dual_boundary/2026-08-18_11-30-11`. Tightening the
tolerance altered the paired curve's shape by no more than about 0.22 points
after removing the common level change. The J/Ms reversal is therefore not an
epsilon-1 stopping artefact.

### What it established

- The full-history M/J transition improves, but a material J/Ms reversal
  returns.
- Adding 1958--1988 is not merely adding more observations of one stable
  system. It adds different division sizes, boundary locations, promotion
  flows and bout networks.
- One timeless dual-boundary map does not explain or remove all observed
  non-monotonicity.

## 8. Historical curated monotone landmark curve

### Purpose

The project has already constructed a monotone curve for public rating
landmarks. This work predates the present decision to make the operational
entrant priors monotone and must not be confused with an unimplemented idea.

`InitialRatingCurve.v5()` was originally built over the fixed-v1 entrant map.
The current `fixed_supported.landmarks` producer reuses the same
`InitialRatingCurve.from_ordinal_ratings(...)` machinery with the maintained
fixed-supported master map to generate “Typical Equelo Values”.

### Existing policy

The v5-style construction:

- limits the domain to Jd100w;
- deletes historical J13--J24 and M18--M22 slots;
- masks selected rare sanyaku and lower-division support;
- masks the complete M12e--Ms2e bridge plus Ms3e;
- converts the remaining support values to a strictly decreasing sequence by
  making only the minimum required downward edits; and
- fills the masked positions with a monotonicity-preserving cubic interpolant
  over a dense chii index.

Sources:

- [`fixed_v1/initial_rating.py`](../../equelo/fixed_v1/initial_rating.py)
- [V5 Policy](../../equelo/fixed_v1/docs/V5%20Policy.md)
- [`fixed_supported/landmarks.py`](../../equelo/fixed_supported/landmarks.py)
- [Equelo Version Naming](../../equelo/docs/Equelo%20Version%20Naming.md)

### What it established

- A deterministic, auditable monotone interpretation curve is already
  technically feasible.
- The existing curve is an interpretation/landmark layer, not the entrant
  initialiser used by the maintained Equelo process.
- Its manual deletion and masking policy, and its one-sided downward clamp, are
  materially different from support-weighted least-squares isotonic regression.
- No retained result establishes that using this v5-style curve for entrants
  improves or preserves prospective prediction.

The existing v5-style curve should therefore be a Task C comparator and a
source of reusable interpolation and lookup code. It must not be silently
promoted to the operational entrant curve without provenance and predictive
testing.

## Experiment-wide conclusions

The combined record supports the following claims:

1. The old Jk73 result was an underidentification/support failure and is now
   controlled by the supported-domain policy.
2. The M12 rise is not caused solely by fixed-point map normalisation.
3. Historically variable banzuke structure is a material omitted context in a
   literal-chii map.
4. Boundary-relative representations improve important local shapes but do
   not produce a unique monotone full-history mapping.
5. Convergence establishes self-consistency under the chosen representation;
   it does not establish that the representation is the right one.
6. No further contextual model is currently justified by an independently
   demonstrated practical benefit.

These conclusions motivate a transparent monotone entrant-prior policy and a
prospective predictive comparison, rather than further attempts to explain
every local reversal.
