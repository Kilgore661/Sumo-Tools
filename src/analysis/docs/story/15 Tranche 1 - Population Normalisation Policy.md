# Tranche 1: Normalisation Policy

## Corrected order of work

The first Tranche 1 implementation compared the legacy departure adjustment
with whole-population mean preservation. That was one step too far. Both
fixed-point calculations retained the existing post-iteration chii-map
normalisation even though earlier work already associated that operation with
absurd ratings at very low-support chii.

Those distorted priors are then used to initialise entrants. They can
contaminate any comparison of population-normalisation policies. The corrected
order is therefore:

1. repair or delimit post-iteration chii-map recentering while keeping the old
   Elo replay fixed;
2. obtain a credible post-1988 prior curve;
3. only then compare departure redistribution with whole-population mean
   preservation.

The reproducible package is
[`src/analysis/equelo_population_policy`](../../equelo_population_policy/README.md).

## Existing recentering

After a replay, Expt2 aggregates basho-start ratings by chii. If the raw map is
`r(c)` over `C` chii and the chosen baseline is `B`, the existing rule adds the
same amount to every chii:

```text
correction_mass = C * B - sum(r(c))
adjustment(c)   = correction_mass / C
```

This restores the unweighted chii-map mean and preserves every rating
difference. But a chii with one entrant-dominated observation receives the
same repeated shift as a chii supported throughout the history. The resulting
prior can therefore be mostly accumulated normalisation rather than bout
evidence.

## Support-weighted proposal

The isolated experiment replaces only the allocation rule:

```text
weight(c)     = support(c) ** alpha
adjustment(c) = correction_mass * weight(c) / sum(weight)
```

The total correction is unchanged, so the unweighted map mean still equals
`B`. At `alpha=0` this is exactly the old common shift. At `alpha=1`, correction
is distributed directly in proportion to support. Intermediate exponents test
whether the low-support ratchet can be reduced without materially changing
rating differences.

The experiment reports two direct measures of distortion:

- maximum change to any pairwise rating difference;
- RMS change over all distinct pairs.

It also compares the final fixed-point maps with the uniform-shift baseline.

## Canonical run

```powershell
python -m src.analysis.equelo_population_policy.run_recentering `
  --start 1989 --end 2026 --zip `
  --epsilon 10 --max-iterations 200
```

Artifacts are under
`files/output/analysis/equelo_population_policy/recentering/`.

## Results: how much do differences change?

| Allocation | Final-step RMS change | Final-step maximum change | Final-map RMS change from uniform | Final-map maximum change |
|---|---:|---:|---:|---:|
| Uniform | 0.000 | 0.000 | 0.000 | 0.000 |
| Support^0.25 | 6.363 | 17.738 | 65.742 | 561.251 |
| Support^0.5 | 20.656 | 52.290 | 128.509 | 914.262 |
| Support^1 | 103.350 | 245.025 | 348.080 | 1507.271 |

Raw support proportionality is therefore not a small relaxation of difference
preservation. At the stopping iteration, that single recentering changes a
typical pairwise difference by about 103 points RMS and some differences by
245 points. Across the solved map, pairwise differences move by 348 points RMS
relative to the uniform baseline.

Restricting the final-map comparison to chii with at least 100 observations
reduces but does not remove the distortion:

| Allocation | Supported-map RMS difference change | Supported-map maximum change |
|---|---:|---:|
| Support^0.25 | 4.78 | 25.72 |
| Support^0.5 | 16.04 | 78.64 |
| Support^1 | 84.06 | 405.67 |

The direct support rule does solve the headline singleton symptom:
`Sd101e` falls from 2787.926 under the uniform rule to 1531.987. But it does so
by moving well-supported ratings substantially: `Y1e`, `O1e`, `S1e`, `K1e`,
`M1e` and `M12e` all move by roughly 199--205 points.

Gentle weighting presents the opposite trade-off. `alpha=0.25` changes the
well-supported curve only modestly, but the largest low-support prior remains
2844.934. `alpha=0.5` lowers singleton `Sd101e` to 1927.049 but still leaves a
nine-observation Jonokuchi chii at 2747.148.

## Recovered earlier evidence

Commit `a250420` contains an abandoned `equelo2` experiment that changed the
population mean-preservation operator rather than the chii-map recentering.
Equal-share active-population correction drove one-observation `Sd101e` to
roughly 65,000 even after solver-level recentering was removed. Support
weighting controlled that singleton but warped the Juryo--Makushita boundary
and lower Maegashira curve.

This confirms that both normalisations can create fixed-point rank evidence.
The isolated experiment above nevertheless shows why chii-map recentering must
be repaired first: its current all-chii common shift already supplies unusable
entrant priors.

## Initial interpretation after the distortion audit

The proposed raw support-proportional shift is too aggressive. It answers the
question “how much do differences change?” with “materially.” A power-law
compromise does not give a clean solution: small exponents preserve the
supported curve but leave low-support extremes; larger exponents remove the
extremes by reshaping the curve.

The promising tailored rule is consequently more discrete:

- define the prior on the already-established supported chii domain;
- apply one common additive shift within that domain, preserving all
  differences between retained priors;
- do not allow unsupported chii to participate in or receive the repeated map
  correction;
- resolve unsupported entrants through the explicit fallback/completion policy
  rather than pretending their fixed-point estimates are evidence.

That approach targets the known failure without unnecessarily changing
differences among the ratings considered reliable. Once it produces a credible
prior curve, the population-normalisation comparison can be rerun without the
present confounder.

The unequal-divisional-K issue remains minor: the earlier controlled replay
found that removing its mass required an average correction of about 0.0385
points per rikishi per basho, with a maximum around 0.170.

## Subsequent decision: retain the alpha=1 curve as a candidate

Visual inspection changed the modelling judgement without changing the
distortion measurements above. Apart from the unsupported deep-Jonokuchi tail,
the `alpha=1` curve has a coherent broad shape through substantially more of
the lower banzuke than the old literal-chii fixed point. It removes the former
M12--M18 rise but retains visible discontinuities at M/J and J/Ms, saw-toothed
rare sanyaku positions, and support-related features such as the `Ms60e`
spike.

The project chose not to interpolate these features away. This repeats the
earlier M12 decision in a stronger form:

- the map is an entrant-initialisation policy, not a timeless measurement of
  intrinsic ability belonging to each chii;
- exact monotonicity is not required, although broad agreement with chii order
  remains desirable;
- a surprising value is neither automatically a model defect nor a discovery
  about sumo; and
- computed anomalies should be disclosed rather than silently replaced by the
  curve expected in advance.

The `alpha=1` result is therefore denoted candidate prior \(P_1\). With the
selected divisional-`k` forecast model it gives candidate \(B_{kP_1}\), called
`BKP1` informally. This is a candidate designation, not a claim that the
distortion audit selected a predictively useful model.

## Retrospective q=400 predictive gate

The source fixed-point diagnostic used legacy Expt2's `q=900`. The predictive
gate deliberately does not revive that value in the rating model. It inserts
the resulting \(P_1\) into the exact `q=400` forecast/update contract of the
established B-family comparison.

For the consumer contract, the 975 side-specific `support_1` values are paired
by an unweighted east/west mean. This produces 484 pairs, including three
singletons. The unranked fallback is the minimum paired candidate value. The
same 574,863 rated bouts, eligibility rules, chronology and divisional-`k`
configuration are used for every model.

Reproduce with:

```powershell
python -m src.analysis.equelo_population_policy.predict_candidate `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07
```

Artifacts are under
`files/output/analysis/equelo_population_policy/prediction_q400/`.

### Aggregate result

| Model | Mean log loss | Mean Brier loss | ECE |
|---|---:|---:|---:|
| \(B\) | 0.682753 | 0.244687 | 0.019192 |
| \(B_k\) | 0.682015 | 0.244355 | 0.013588 |
| \(B_P\) | 0.678055 | 0.242439 | 0.017030 |
| old \(B_{kP}\) | **0.676945** | **0.241968** | **0.013459** |
| \(B_{kP_1}\) | 0.677700 | 0.242241 | 0.014855 |

`BKP1` is the second-best model by aggregate log and Brier loss. Its ECE is
third-best, behind old \(B_{kP}\) and \(B_k\). It beats \(B\), \(B_k\), and
\(B_P\) on aggregate log and Brier loss. Against \(B\), its paired mean
log-loss difference is -0.005053 with a 95% interval of
[-0.005847, -0.004309], and it passes the existing retrospective
non-inferiority gate by a wide margin.

The old \(B_{kP}\) remains better. `BKP1` minus old \(B_{kP}\) is +0.000754
mean log loss with a 95% interval of [+0.000530, +0.000988]. Thus the old
model's advantage is small in absolute terms but clear in this retrospective
comparison.

The maturity breakdown locates the difference where an informed prior should
matter:

| Population | Bouts | `BKP1` minus old \(B_{kP}\) log loss |
|---|---:|---:|
| A new entrant participates | 2,498 | +0.006577 |
| Less-experienced rating has fewer than 30 bouts | 84,716 | +0.003756 |
| 30--59 bouts | 72,282 | +0.000371 |
| 60--119 bouts | 112,652 | +0.000097 |
| 120 or more bouts | 305,213 | approximately +0.0002 to +0.0003 |

### Interpretation

This answers the immediate usefulness question positively. `BKP1` retains
about 87% of the old \(B_{kP}\) aggregate log-loss improvement over Basic Elo
and beats the other previously tested alternatives by aggregate log and Brier
loss. It is therefore a credible model, not merely an attractive chii curve.

It does not replace the old \(B_{kP}\) on predictive evidence: the old prior
performs materially better during the initial rating-maturity range and remains
the aggregate winner. Both prior artifacts use future information from the
period being scored, so this is retrospective model-selection evidence rather
than prospective validation.

The next clean step is to construct \(P_1\) with a maintained `q=400`
fixed-point producer, leaving original Expt2 and its artifacts reproducible.
That new prior must be inspected and passed through the same predictive gate;
the present result cannot be transferred to it automatically.

## Controlled q=400 fixed-point rerun

The same legacy-replay recentering sweep was rerun with only `q` changed from
900 to the B-family value 400:

```powershell
python -m src.analysis.equelo_population_policy.run_recentering `
  --start 1989 --end 2026 --zip --q 400 `
  --epsilon 10 --max-iterations 200 `
  --output files/output/analysis/equelo_population_policy/recentering_q400
```

The `alpha=1` solver converged in 18 iterations, compared with 20 at `q=900`.
Changing `q` compressed the rating scale but did not materially alter the
support-related shape:

| Quantity | `q=900` | `q=400` |
|---|---:|---:|
| Maximum prior | 2882.7 | 2544.4 |
| Minimum prior | 817.3 | 930.7 |
| Final-step RMS difference change | 103.35 | 96.17 |
| Final-map RMS difference from uniform | 348.08 | 329.72 |
| Maximum final-map difference change | 1507.27 | 1461.01 |

Selected `alpha=1` values show that the main discontinuities survive:

| Chii | Support | `q=900` | `q=400` |
|---|---:|---:|---:|
| M12e | 222 | 2191.5 | 2137.3 |
| M15e | 202 | 2141.9 | 2089.3 |
| M18e | 6 | 1948.9 | 1896.3 |
| J1e | 222 | 2160.9 | 2105.5 |
| J14e | 131 | 1921.5 | 1886.7 |
| Ms1e | 222 | 2012.5 | 1978.0 |
| Ms59e | 222 | 1697.3 | 1686.8 |
| Ms60e | 280 | 1795.4 | 1782.0 |
| Sd1e | 222 | 1697.9 | 1687.0 |
| Sd101e | 1 | 1532.0 | 1529.4 |

In particular, the M18e--J1e increase is approximately 212 points at `q=900`
and 209 points at `q=400`. The `Ms60e` spike is also nearly unchanged. These
features are therefore consequences of the support-weighted construction and
the historical support pattern, not consequences of retaining `q=900`.

The broad visual judgement also survives: the former M12--M18 rise is absent,
the curve remains coherent far into Jonidan, and the deep-Jonokuchi region
remains the least credible. The corresponding responsive chart is
`files/output/analysis/equelo_population_policy/recentering_q400/prior_comparison.html`.

This produced the required `q=400` candidate prior map. The next two sections
record its independent reproduction and predictive gate.

## Independent BKP1 producer

Original Expt2 and every legacy `q=900` producer remain untouched. A separate
package, `src.analysis.equelo_bkp1`, reproduces only the candidate model with a
fixed contract:

- `q = 400`;
- `alpha = 1` support-proportional post-iteration recentering;
- the declared divisional-`k` configuration;
- legacy departure redistribution for this controlled stage; and
- annotation-only chii collapse over the post-1988 record.

The implementation does not import the legacy `INITIAL_Q` and exposes neither
`--q` nor `--alpha`. Run it with:

```powershell
python -m src.analysis.equelo_bkp1 --start 1989 --end 2026 --zip
```

Its 975 canonical prior values match the explicit-`--q 400` experimental
control exactly: the maximum absolute difference is zero and there are no
non-zero row differences. The canonical artifacts are under
`files/output/analysis/equelo_bkp1/`.

## q=400-derived BKP1 predictive result

The canonical `prior.csv` was paired by the same unweighted east/west rule and
put directly through the `q=400` predictive gate. Aggregate results are:

| Model | Mean log loss | Mean Brier loss | ECE |
|---|---:|---:|---:|
| \(B\) | 0.682753 | 0.244687 | 0.019192 |
| \(B_k\) | 0.682015 | 0.244355 | 0.013588 |
| \(B_P\) | 0.678055 | 0.242439 | 0.017030 |
| old \(B_{kP}\) | **0.676945** | **0.241968** | **0.013459** |
| q=400-derived \(B_{kP_1}\) | 0.677319 | 0.242086 | 0.014453 |

The q=400-derived candidate improves on the q=900-derived candidate, whose log
loss was 0.677700. It reduces the gap from old \(B_{kP}\) from 0.000754 to
0.000374. The paired 95% interval for the remaining difference is
[+0.000165, +0.000583], so old \(B_{kP}\) remains the retrospective winner.

In practical terms, however, the models have very similar aggregate log and
Brier losses. The new candidate retains about 94% of old \(B_{kP}\)'s
incremental log-loss improvement over Basic Elo. Its remaining disadvantage is
concentrated at initialisation:

| Population | Bouts | q=400 BKP1 minus old \(B_{kP}\) log loss |
|---|---:|---:|
| A new entrant participates | 2,498 | +0.004770 |
| Less-experienced rating has fewer than 30 bouts | 84,716 | +0.002737 |
| 30--59 bouts | 72,282 | -0.000148 |
| 60--119 bouts | 112,652 | -0.000140 |
| 120 or more bouts | 305,213 | approximately -0.000006 to +0.000083 |

Thus the fully q=400 candidate is predictively useful and extremely close to
the old selected model after 30 bouts. It does not improve initial placement as
much as the old contextual prior. Both constructions remain future-informed,
so the comparison is retrospective rather than prospective validation.

## Population policy revisited with the canonical prior

The repaired, canonical q=400, alpha=1 prior makes it possible to return to the
substantive Tranche 1 question without the old uniform-recentering confounder.
The controlled experiment has two parts:

1. replay the history under each population policy while holding the canonical
   BKP1 prior fixed; and
2. solve a separate chii fixed point under each policy, allowing the policy to
   feed back into its own entrant prior.

Two additional controls separate turnover from unequal divisional `k`:

- `legacy_plus_dual_k` adds only an end-of-basho correction for bout mass to
  the legacy departure rule; and
- `whole_population_start_only` preserves the whole-population mean after
  joiners and leavers, but makes no correction for bout mass after the bouts.

Reproduce the comparison with:

```powershell
python -m src.analysis.equelo_population_policy.run_bkp1_population `
  --start 1989 --end 2026 --zip
```

Artifacts are under
`files/output/analysis/equelo_population_policy/bkp1_q400/`.

### Holding the prior fixed

| Policy | Log loss | Brier loss | Mean start correction | Mean end correction |
|---|---:|---:|---:|---:|
| Legacy departure | 0.684404 | 0.245197 | 2.523 | 0.000 |
| Legacy plus dual-`k` | 0.684425 | 0.245206 | 2.522 | 0.036 |
| Whole population, start only | 0.675457 | 0.241232 | 3.976 | 0.000 |
| Whole population, start and end | 0.675458 | 0.241232 | 3.975 | 0.040 |

Under the legacy rule the active mean is, on average, about 159 points from
the initial target by both the start and end of a basho. Whole-population
preservation keeps the start mean at the target to numerical precision. Its
end-of-basho dual-`k` correction averages only 0.040 points per active rikishi,
compared with a 3.975-point average turnover correction at the start.

The whole-population replay differs materially from the legacy replay: across
158,995 basho-start observations, the rating difference is 157.553 points MAE
and 187.021 points RMS. Its much lower replay loss is interesting, but these
values use the fixed-point replay's legacy bout eligibility and are not the
separate B-family predictive gate. They should therefore be treated as a
diagnostic, not as model-selection evidence.

### Letting each policy determine its own prior

| Policy | Iterations | Log loss | Minimum prior | Maximum prior | Prior-map MAE from legacy |
|---|---:|---:|---:|---:|---:|
| Legacy departure | 18 | 0.684404 | 930.7 | 2544.4 | 0.000 |
| Legacy plus dual-`k` | 18 | 0.684424 | 930.5 | 2543.8 | 0.129 |
| Whole population, start only | 71 | 0.689546 | 1056.0 | 3167.8 | 110.269 |
| Whole population, start and end | 71 | 0.689563 | 1056.1 | 3168.9 | 110.266 |

The controls identify the source of the failure. Correcting dual-`k` bout mass
on its own changes the solved prior map by only 0.129 points MAE, with a maximum
change of 0.810 points. Conversely, turnover mean-preservation without any
dual-`k` correction is already almost identical to the full whole-population
policy. Both whole-population fixed points take 71 iterations and give the
two-observation `Jk73w` cell a rating of about 3168.

Thus the renewed low-support pathology is not caused by divisional `k`, nor by
the alpha=1 post-iteration recentering alone. It is caused by feedback between
whole-population turnover correction and chii-based fixed-point estimation.
The correction applied when entrants and leavers change the population becomes
part of the basho-start chii averages; rare chii can repeatedly absorb that
correction and return it as an extreme entrant prior on the next iteration.

### Tranche 1 conclusion

The experiment separates two propositions that had become entangled:

- whole-population mean preservation is a coherent and substantial rating
  operator when the entrant prior is held fixed; but
- requiring that same operator to generate its own literal-chii fixed-point
  prior is unstable in the low-support tail and produces an unacceptable map.

The dual-`k` correction is quantitatively negligible and can be applied at the
end of an iteration without practical consequence. The unresolved design
choice is instead whether BKP1 should use the canonical prior as a fixed,
externally estimated initialisation policy while applying whole-population
mean preservation during the rating replay, or whether a different
turnover-correction rule is needed that remains well behaved inside the
fixed-point loop. The present evidence rules out the naive independently
solved whole-population fixed point; it does not rule out whole-population mean
preservation with a fixed prior.

## Exact predictive gate for the fixed-prior model

The final Tranche 1 gate holds canonical P1 fixed and uses the exact B-family
domain of 574,863 W/L bouts. It exposed an important distinction that the
earlier terminology had obscured: the established B-family forecaster performs
no population-boundary adjustment. It is not an implementation of Expt2's
departure redistribution. The predictive comparison therefore contains three
BKP1 variants:

- no population adjustment, reproducing the already reported q=400 BKP1
  result exactly;
- actual Expt2 departure redistribution over the full banzuke population; and
- whole-population mean preservation over that same population.

The old informed-prior `B_kP` is included as the retained benchmark. Reproduce
with:

```powershell
python -m src.analysis.equelo_population_policy.predict_population_policy `
  --history-zip "files/output/Historys/1989_01 to 2026_11.zip" `
  --end 2026/07
```

### Aggregate result

| Model | Log loss | Brier loss | ECE |
|---|---:|---:|---:|
| BKP1, no population adjustment | 0.677319 | 0.242086 | 0.014453 |
| BKP1, Expt2 departure redistribution | 0.684196 | 0.245148 | 0.017651 |
| BKP1, whole-population preservation | **0.675629** | **0.241362** | 0.014537 |
| old `B_kP` | 0.676945 | 0.241968 | **0.013459** |

Whole-population BKP1 improves mean log loss by 0.001690 over no adjustment,
with a basho-block-bootstrap 95% interval of [-0.002045, -0.001312]. It improves
by 0.008568 over actual Expt2 departure redistribution, interval
[-0.009186, -0.007916]. It also improves by 0.001316 over the previous
retrospective winner, old `B_kP`, interval [-0.001755, -0.000894]. Brier loss
agrees. ECE does not: old `B_kP` retains the lowest aggregate calibration error.

The gain over no adjustment is concentrated in younger ratings:

| Rating maturity | Bouts | Whole minus no-adjustment log loss | Whole minus old `B_kP` |
|---|---:|---:|---:|
| New entrant participates | 2,498 | -0.005893 | -0.001124 |
| Fewer than 30 prior bouts | 84,716 | -0.009773 | -0.007036 |
| 30--59 | 72,282 | -0.001219 | -0.001367 |
| 60--119 | 112,652 | -0.000363 | -0.000503 |
| 120--239 | 148,563 | -0.000357 | -0.000362 |
| 240--359 | 77,499 | -0.000126 | -0.000055 |
| 360--479 | 39,338 | +0.000289 | +0.000372 |
| 480 or more | 39,813 | +0.000922 | +0.000964 |

This pattern is coherent with the role of the operator. A common shift cannot
alter probabilities among the current active rikishi at the instant it is
applied. It does, however, anchor the rating coordinate carried by survivors
relative to the fixed absolute prior subsequently assigned to entrants. The
benefit appearing chiefly in early-career bouts is therefore expected rather
than an unexplained aggregate effect.

### Decision supported by Tranche 1

The evidence now supports whole-population mean preservation with canonical P1
held fixed as the leading candidate replay model. It has the best retrospective
log and Brier loss of the tested models while avoiding the pathological prior
map produced when the same operator is fed back through literal-chii
fixed-point estimation.

This does not rehabilitate Expt2 departure redistribution: on the exact
predictive domain it is substantially worse than both no adjustment and
whole-population preservation. Nor does it justify solving P1 again under the
new operator. The clean separation is:

1. P1 is the fixed, externally produced entrant-initialisation policy; and
2. whole-population mean preservation is the rating replay's population
   operator.

The result remains retrospective and P1 remains future-informed. A prospective
or rolling-origin evaluation is a later validation question, not a remaining
Tranche 1 definition question.
