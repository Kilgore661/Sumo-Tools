# Elo Penalties

## Status

Historical experimental home for research into possible Elo-89 penalties for
rikishi who do not appear.

A fixed-point experiment has been proposed to assess the viability of a
candidate rating model named **Elo89a**, where `a` denotes absence. Elo89a uses
a basho-end `k/2` deduction for each non-appearance. The fixed-point experiment
was implemented and run, but the model was not adopted and none of this code is
on the production rating path. Elo-89 continues to exclude fusen results and
does not penalise opponentless absences.

## Summary and conclusion

### The candidate idea

The motivating rule was simple: if the rating measures competitive
effectiveness including availability, a rikishi who does not appear should
lose rating even when he is a Yokozuna. Elo89a represents each recorded
non-appearance as the equivalent of losing to a hypothetical equally rated
opponent, and therefore deducts half of the applicable divisional `k`.

This is not an automatic consequence of Elo. It changes the quantity being
estimated. A rating of performance conditional on a bout taking place has no
new head-to-head evidence when somebody is absent. A rating of broader
competitive effectiveness may instead regard availability as part of the
thing being measured. The experiment did not resolve which interpretation
Elo-89 ought to adopt.

### What counts as a non-appearance

The evidence contains two different events:

- `FP` (fusen-pai): the rikishi was named on the torikumi but did not appear,
  and a named opponent received `FS`; and
- published `A`: the rikishi was absent from the torikumi and the final record
  reports a missed opportunity, without identifying an opponent.

Daily blanks cannot simply be counted, particularly below Juryo where most
days are ordinary unscheduled days. The experiment therefore counted explicit
`FP` results and the published final `W-L-A` totals. It did not infer absences
from blank days. `FS` received no direct rating credit because an unperformed
bout demonstrates no winning skill.

### The transfer problem

A one-sided deduction removes rating mass. An `A` supplies no opponent to
receive it, while crediting the named `FS` rikishi would make an unsupported
claim about demonstrated performance. Elo89a therefore applies all deductions
at basho end and lets Elo-89's whole-population normalisation restore the
target mean.

This is mathematically defined, but it implicitly transfers the deducted mass
to every active rikishi. Uninvolved rikishi consequently gain rating because
other rikishi were absent. That common shift also affects coordinates carried
past later population changes and fixed entrant priors; it is not merely a
presentational detail.

### What the completed run found

The run covering 225 basho from 1989/01 through 2026/09 counted:

- 3,034 `FP` events;
- 77,840 published absences; and
- 1,310,212.5 rating points deducted before normalisation.

The aggregate effect was not small. For example, the common basho-end
normalisation adjustment in the Elo89a arm was approximately `+20.37` for
every active rikishi in 2022/07 and `+20.07` in 2021/01. These large values
show that a rule phrased as an individual penalty can become a material
population-wide intervention.

Both fixed-point arms converged at the selected epsilon of 10, so Elo89a passed
the narrow numerical-viability test. The control converged in 73 iterations
and Elo89a in 87. Convergence did not make the resulting prior unproblematic:

- the control prior ranged from about 1,006 to 3,275;
- the Elo89a prior ranged from about 873 to 3,952;
- at familiar upper ranks Elo89a was commonly about 85 to 160 points above
  the control; and
- at very low-support chii, Elo89a-minus-control differences exceeded 600
  points.

The low-support extremes reproduce a known weakness of chii fixed-point
estimation and are magnified by the penalty policy. More importantly, even the
experimental control differed substantially from the canonical prior. The run
therefore established that the proposed equations can converge, not that the
result is an acceptable Elo-89 initialisation or a better rating model.

### Why this is not a current Elo-89 comparison

The experiment predates later model decisions. In particular, it:

- uses the earlier canonical P1 reference rather than the adopted P1-WL
  initialisation;
- deletes ratings when rikishi leave the active population and reinitialises
  them on return, rather than applying the subsequently adopted frozen-rating
  persistence rule; and
- evaluates fixed-point behaviour only, without predictive log loss, Brier
  loss, calibration, or downstream site-artifact comparisons.

Its results are therefore historically informative but cannot be read as a
controlled comparison between Elo89a and current Elo-89. A renewed experiment
would have to begin from current P1-WL, persistence, bout eligibility and
normalisation semantics, and would still need to justify why availability is
part of the rating's estimand.

### Retained decision

Elo89a was not adopted. The experiment exposed a real possible alternative
meaning for a sumo rating, but the simple `k/2` rule does more than penalise an
individual missed appearance: through normalisation it moves the whole active
population, produces large cumulative effects, and relies on a semantic claim
about availability which has not been accepted. Production Elo-89 therefore
continues to treat only represented W/L contests as rating evidence.

## Documentation

- [`docs/Excursus on Penalty Transfers.md`](docs/Excursus%20on%20Penalty%20Transfers.md)
  records why transferring a non-appearance penalty is attractive, why the
  missing opponent remains a modelling problem, and what the existing absence
  research establishes about the adequacy of the historical record.
- [`docs/Non-appearance Penalty Experiment Proposal.md`](docs/Non-appearance%20Penalty%20Experiment%20Proposal.md)
  specifies the paired fixed-point experiment assessing Elo89a's viability: a
  basho-end `k/2` deduction followed by Elo-89 whole-population normalisation.
- [`docs/Elo89a Implementation Design.md`](docs/Elo89a%20Implementation%20Design.md)
  assigns the experiment's ledger, replay, solver and persisted-output
  contracts to concrete modules.

## Run

From the repository root:

```powershell
python -m src.analysis.elo_penalties
```

The default run uses the explicit post-1988 History zip, selects the latest
basho having published final records, independently solves the control and
Elo89a arms, and writes reproducible artefacts under
`files/output/analysis/elo_penalties/elo89a`.

## Next

No production action follows from this package. If non-appearance penalties
are reconsidered, write a new proposal against the then-current Elo-89 model
and treat this experiment as background evidence rather than a reusable
control.
