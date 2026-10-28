# Findings: frozen rating persistence

## Result

The frozen-persistence candidate passed the controlled historical comparison
and is adopted as the replacement for resetting returning rikishi from P1-WL.
The observed predictive evidence also favours persistence.

The full replay covered `1989-01` through `2026-09` and used the accepted
P1-WL prior. It produced 581,634 rated-bout forecasts and 437 return events for
365 rikishi. Every return matched the earlier ranked-gap census, the reset
control exactly reproduced canonical Elo-89, and there were no invariant
violations.

Negative score differences favour frozen persistence:

| Scope | Observations | Log-loss difference | Brier difference |
|---|---:|---:|---:|
| Complete replay | 581,634 | -0.000511568 | -0.000259660 |
| First return bout | 396 | -0.015474126 | -0.007857711 |
| First seven return bouts | 2,729 | -0.005485247 | -0.001915892 |
| Return basho | 2,624 | -0.005829219 | -0.001899456 |
| Full observed active spell after return | 59,772 | -0.006190155 | -0.002781311 |

The candidate therefore did not merely avoid a meaningful deterioration. It
improved both scoring rules in the complete replay and in every aggregate
return-focused window.

## Large differences

The largest active-rating difference was 854.53 points in `2024-05`, for
Higohikari at `Jk20e`: reset gave 1432.44 and persistence gave 577.91. This is
an informative result rather than an unexplained failure. Higohikari had a
long, heavily observed low-rated career, while reset discarded that evidence
and substituted an unstable exact-Jonokuchi-rank prior. The largest sekitori
difference in the same basho was 24.67 points.

The sole non-Jonokuchi event, Sokokurai, was kept separate. Persistence was
worse on his first bout and over the full later active spell, but better over
his first seven bouts and return basho. It is one event and supplies no basis
for overriding the aggregate result or the information-preservation rule.

## Conclusion

Absence from the represented active population supplies no bout evidence.
Deleting an established rating nevertheless discards evidence, and the reset
prior can introduce much larger distortions than preserving the last observed
point estimate. The controlled comparison found no compensating predictive or
sekitori-level reason to retain reset-on-return.

The adopted Elo-89 lifecycle rule is therefore:

> Preserve a departing rikishi's rating unchanged outside the active
> population and restore it if he returns. While absent, exclude it from all
> means, shifts, forecasts and updates.

This conclusion does not introduce decay or an uncertainty model, add
mae-zumo-versus-mae-zumo bouts, or change P1-WL. Tracing the accepted lifecycle
rule through production artifacts remains a separate implementation step.

## Reproduction

Run:

```powershell
py -m src.validation.rating_persistence_comparison
```

The runner writes a new provenance-bound directory below
`files/output/validation/elo89-expert-account/Matters Arising/Rating
Persistence/Frozen Persistence Comparison/output/`. The completed run used
for these figures is timestamped `2026-10-28_11-18-04`.
