# The Sumo Elo-89 Application: Product Account

## Status

This is the skeleton of the application-level account of what the published
Elo-89 website delivers, what its outputs mean, and which significant ideas
were considered but not adopted.

Only the non-appearance-penalty decision has been recorded so far. The rest of
the product account is intentionally deferred.

## Considered but not adopted: non-appearance penalties

The project considered extending Elo-89 so that a rikishi loses rating whenever
he does not appear for an expected contest. This candidate was called
**Elo89a**, where `a` denotes absence. Its simple rule deducted half of the
applicable divisional `K` for every recorded non-appearance, including both a
scheduled fusen-pai (`FP`) and an absence reported in the final `W-L-A` record.
The rule applied equally at every rank: a Yokozuna who did not appear would
also lose rating.

The idea embodies a broader meaning of rating than production Elo-89 currently
uses. If a rating estimates performance conditional on a bout taking place,
non-appearance supplies no new head-to-head result. If it estimates competitive
effectiveness including availability, absence may reasonably count against the
rikishi. Elo itself does not decide between those interpretations.

Elo89a was implemented as an isolated fixed-point experiment. It did not give
the fusen-sho recipient a conventional Elo win: no winning performance occurred,
and an opponentless absence identifies no recipient at all. Instead, the model
deducted the penalty at basho end and allowed Elo-89's population
normalisation to restore the target mean. This implicitly distributed the
deducted rating mass across every active rikishi.

The completed 1989/01--2026/09 experiment counted 3,034 fusen-pai and 77,840
published absences. It deducted 1,310,212.5 rating points before normalisation.
In unusually absence-heavy basho, restoring the mean added about 20 points to
every active rikishi. Both experimental fixed-point arms converged, but the
penalty arm produced a substantially wider and more extreme chii-prior map,
including very large differences at low-support ranks. Convergence therefore
established numerical viability only; it did not establish that the model was
meaningful, predictively better, or suitable for publication.

That experiment also predates the accepted P1-WL initialisation and frozen
rating persistence across departure and return. It is consequently historical
evidence rather than a controlled comparison with the current Elo-89 model.
It did not measure predictive log loss, Brier loss, calibration, or downstream
publication effects.

The application does **not** publish Elo89a. Production Elo-89 treats
represented W/L contests as rating evidence, excludes FS/FP as unperformed
bouts, and applies no invented penalty for opponentless absence. This retained
policy does not claim that availability is unimportant; it says that the
current point rating does not attempt to encode it through an unsupported
one-sided deduction and population-wide transfer.

The experiment, its exact proposal and the fuller assessment are preserved in
[`src/analysis/elo_penalties`](../../../analysis/elo_penalties/README.md).
