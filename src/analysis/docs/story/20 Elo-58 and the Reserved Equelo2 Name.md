# Elo-58 and the Reserved Equelo2 Name

## Status

This is the current restart point for the Elo/Equelo story. It incorporates the
complete-history baseline, the January-1989 and implied-map audits, and the
subsequent divisional-average investigation. Earlier documents remain the
chronological evidential record, but their use of `proto-Equelo2` for the
existing historical reconstruction is superseded by the terminology here.

## The two models now in view

### Elo-89

**Elo-89**, written \(E_{89}\), is the selected operational model for the
sufficiently complete record from January 1989 onward. Its contract comprises:

- canonical P1 chii-based entrant initialisation;
- `q = 400`;
- the selected divisional-`k` schedule;
- all represented binary W/L results, irrespective of whether a kimarite is
  recorded; and
- common whole-population shifts which preserve the initial active mean at
  basho boundaries.

Elo-89 is the candidate to continue forward as new results arrive. Its P1 map
is future-informed relative to part of its construction history, so its
existing predictive scores are retrospective evidence rather than a claim of
prospective validation. Nevertheless, its choices are explicit, empirically
compared and sufficiently defensible for an operational rating model.

### Elo-58

**Elo-58**, written \(E_{58}\), is the provisional historical reconstruction
previously called `proto-Equelo2` or the `Equelo2 full-history baseline`. It
applies the Elo-89 framework from January 1958, completes historical-only chii
from the nearest available chii above, and persists an individual's most
recent rating through missing results and banzuke absence.

Elo-58 exists to permit comparisons between historical and modern rikishi,
such as Taiho and Hakuho. It is not intended to improve post-1988 ratings or
forecasts, and it is not the selected operational model.

The package and artifact paths under `equelo2_baseline` retain their old names
for reproducibility. The internal CSV run key `equelo2_full_history` is also a
legacy identifier; neither changes the model's public name.

## What Elo-58 establishes

The global-average Elo-58 baseline processes 745,206 represented binary bouts.
Its complete-history mean log loss is `0.679354`, against `0.693147` for the
neutral 50--50 predictor, and its Brier loss is `0.243025`, against `0.250000`.
Its post-1988 log loss is `0.675281`, compared with `0.675498` when Elo-89 is
started afresh. Thus the historical reconstruction contains useful rating
information and carrying its state into 1989 does not materially damage the
later account.

Its structural and audience-facing checks are also recognisable rather than
arbitrary. The January-1989 historical and fresh-start ratings have strong
overall rank agreement; the complete-history and P1 chii maps have strong
overall correlation; and the processed peak table contains the familiar
post-1958 candidates for greatest rikishi, headed by Hakuho with Taiho among
the leaders.

These findings make Elo-58 useful as an experiment and historical lens. They
do not give it the same authority as Elo-89.

## The unresolved Elo-58 problem

The global-average replay's implied chii map is displaced relative to P1:

| Division | Elo-58 implied map minus P1 |
|---|---:|
| Makuuchi | +149.273 |
| Juryo | +39.552 |
| Makushita | -35.350 |
| Sandanme | -35.783 |
| Jonidan | -12.624 |
| Jonokuchi | -43.761 |

This is evidence of disagreement, not proof that Elo-58 is wrong or that P1 is
ground truth. The displacement may combine historical information, incomplete
early lower-division evidence and the consequences of preserving only one
global mean. Jonokuchi also remains substantively problematic: its inferred
rating/rank relationship is weak and P1 itself places its unweighted mean
above Jonidan's.

The incompleteness audit supports persisting ratings when evidence is
intermittent, but it cannot remove the ambiguity between unscheduled and kyujo
symbols for sub-sekitori. Nor has the project experimentally quantified rating
uncertainty as a function of missing results.

## Divisional-average investigation

Separate persistent divisional means were investigated as a possible response
to the sekitori/sub-sekitori displacement. A post-1988 prior called P2 was
constructed by fixed-point iteration under that population policy.

Unrestricted literal-chii iteration did not converge usefully. The instability
was concentrated in underidentified deep-Jonokuchi chii whose basho-start
observations mostly or wholly recycled the prior being solved. Reusing the
predeclared Tranche 1 support threshold of 60, and completing unsupported chii
from the nearest supported chii, produced genuine tight convergence. This was
a useful diagnosis, not an a priori requirement for a historical model and not
evidence that the resulting lower-rank curve was correct.

During that work, the new P2 replay was found to exclude binary W/L bouts whose
kimarite field was blank. The defect affected 33,522 post-1988 bouts, almost
all below Juryo. It was corrected so that the P2 and full-history experiments
use the exact 579,426-bout post-1988 binary domain. Corrected threshold-60 P2
converged in 18 iterations at epsilon `0.001`.

The corrected complete-history divisional experiment suppressed the mean-map
displacement, but that result was substantially imposed by separate
divisional recentering. More importantly, it performed materially worse than
the global-average Elo-58 baseline on the same 745,206 bouts:

| Model | Mean log loss | Mean Brier loss |
|---|---:|---:|
| Elo-58, global-average persistence | 0.679354 | 0.243025 |
| Divisional-average experiment | 0.686808 | 0.246723 |

Measured relative to neutral prediction, the divisional experiment loses
roughly half of Elo-58's demonstrated improvement. It also applies very large
start-of-basho corrections: examples exceed 100 points per active rikishi in
Sandanme and Jonokuchi. Division-boundary discontinuities remain and in some
cases worsen.

Divisional-average persistence is therefore not selected. It showed that the
original displacement can be suppressed and clarified a low-support
fixed-point pathology, but it does not provide a satisfactory replacement for
Elo-58's global population policy. Raising support thresholds or adding
further special cases merely to obtain an expected curve would cross the
teleological boundary the investigation was intended to expose.

## Reserved meaning of Equelo2

**Equelo2 does not name a current model.** The name is reserved in case a
future full-history construction resolves enough of Elo-58's problems to
justify treatment as an adopted model rather than an experimental historical
comparison.

There is no obligation to produce such a model. The final public account may
legitimately present two different objects:

1. Elo-89 as the operational rating system for 1989 onward and the candidate
   for processing future results; and
2. Elo-58 as an explicitly qualified experiment for cross-era comparison.

If a future Equelo2 is proposed, it must receive a complete model contract and
new validation. It must not acquire authority merely by inheriting the name or
by being tuned until selected historical rankings look attractive.

## Current conclusion

The project should stop treating successful extension to 1958 as a prerequisite
for adopting Elo-89. Elo-89 and Elo-58 answer different questions and may have
different epistemic status. Elo-58's limitations must be disclosed wherever
its historical comparisons are presented; they need not be disguised as
minor unfinished details of an otherwise selected Equelo2.

The fixed-pool realised-outcome control remains a useful explanatory experiment
about ordinary Elo learning, but it is not a gate that can convert Elo-58 into
Equelo2. Prospective evaluation of frozen Elo-89 is a separate future
validation exercise.
