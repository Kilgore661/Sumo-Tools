# Kimarite

## Status

Concluded validation record for the first matter arising from the Elo-89
expert account.

This folder investigates the treatment of represented results for which no
kimarite is recorded. The descriptive audit and controlled P1/P1-WL prior
comparison and stopping-threshold sensitivity work have now been run. The
prior-level findings are
recorded in
[`P1-WL Prior Comparison - Findings.md`](P1-WL%20Prior%20Comparison%20-%20Findings.md).
The model decision is recorded below. Promotion into production rating code
and regeneration of the published artifacts remain separate implementation
work.

## Decision

P1-WL is accepted as the replacement for P1. A represented binary W/L result
is rating evidence whether or not its kimarite is recorded. Kimarite is not an
input to Elo-89, and absence of that descriptive field is not a reason to
discard otherwise usable evidence about who fought and who won.

The accepted fit retains epsilon 10. A broad sweep found negligible raw-score
improvements at iterations 20 and 21, selected by epsilon 8.5 and 8
respectively, but no practically persuasive advantage over epsilon 10 at
iteration 18. Tighter thresholds then deteriorated rapidly because sparse
literal-chii cells became extreme. Epsilon 10 therefore remains the simple,
tested early-stopping rule; it is understood as material regularisation, not
as proof of numerical convergence.

This closes the P1-variant exploration. Its conclusion is that P1-WL is good
enough for the intended role and, unlike P1, consistently includes all
otherwise valid represented results, with or without kimarite.

The next tranche followed the accepted prior through the site-data publication
boundary. Its specification and completed findings are in
[`P1-WL Site Bundle Comparison/`](P1-WL%20Site%20Bundle%20Comparison/README.md).
That work treated P1-WL as fixed, found no invariant violations, and concluded
that a complete non-deployed web site should now be generated with P1-WL for
page-level inspection. It did not reopen model selection or install the
candidate as the canonical production prior.

The website-build and shared-preview tranche is completed and recorded in
[`P1-WL Website Build/`](P1-WL%20Website%20Build/README.md). It assembled the
accepted candidate beneath the validation package and served it at the
workspace-standard `http://localhost:8766/`, avoiding the inaccessible
production mapping on `A:`. The user inspected the working site and found no
obvious problem. No deployment was performed and the canonical P1 prior was
not changed.

This completes the Kimarite matter. The retained evidence supports using
P1-WL as the replacement prior in a separate production change.

The first audit is implemented by `src.validation.kimarite`. It counts each
represented binary W/L result whose decision is `"blank"`, assigning a
cross-division bout to the higher-ranked participant's division. Run it from
the repository root for the Elo-89 validation interval with:

```powershell
py -m src.validation.kimarite --start 1989-01
```

The live History is used by default. An explicit annotated snapshot can be
selected with `--history-zip PATH`. Timestamped CSV output is retained in this
folder's `output` directory.

## Epoch correction and adopted descriptive result

The first audit was run on 24 October 2026 against the live store `history4`
and the explicit snapshot
`files/output/Historys/1958_01 to 2026_11.zip`. The snapshot's SHA-256 is
`21e836c0caddfe1395bf1f39f9b8ec778bb75fb05490080be56fc7c3791b33ec`.
Both sources represented 411 basho from `1958-01` through `2026-09`. The first
program inherited that full-history scope and reported 107,022 missing
kimarite. That was a useful diagnostic result, but it was not the answer to the
Elo-89 question because Elo-89 begins at `1989-01`.

The audit was therefore given explicit date bounds and rerun against the
refreshed live store for `1989-01` through its represented endpoint,
`2026-09`. It was then repeated against the repaired canonical snapshot:

- [adopted Elo-89-epoch run](output/missing_kimarite_by_basho_division_1989-01_to_2026-09_2026-10-24_15-45-47.csv)
- [explicit-snapshot confirmation](output/missing_kimarite_by_basho_division_1989-01_to_2026-09_2026-10-24_16-11-34.csv)

The two scoped CSVs are byte-identical, with SHA-256
`a028f437dd1ac9e57c0871054b48dc772deb9f597bdd2335cdeefdb8a5610ed`.
The repaired `files/output/Historys/1958_01 to 2026_11.zip` used for the
confirmation has SHA-256
`afddcc2a77aa237d539073008bf46414989eb766cad8b281cf719963141793ca`.

| Division | Missing kimarite |
|---|---:|
| Makuuchi | 0 |
| Juryo | 0 |
| Makushita | 6,148 |
| Sandanme | 9,964 |
| Jonidan | 13,679 |
| Jonokuchi | 3,730 |

### Descriptive validation conclusion

> In the post-1988 era there were 33,521 missing kimarite, all of which
> occurred against results in Makushita and below.

Here *post-1988* means the declared Elo-89 interval beginning `1989-01`; the
counting unit is one represented binary W/L bout; and a cross-division bout is
assigned to the higher-ranked participant's division. Every affected bout
occurs from `1989-01` through `1991-05`.

The initial scoped run reported one additional blank in Juryo in `2026-07`.
Inspection showed that the cached Day 3 page had no kimarite for Asasuiryu's
win over Kyokukaiyu, while the current SumoDB page recorded `katasukashi`.
After that source page was re-downloaded and History rebuilt, the anomaly
disappeared. This both establishes the 33,521 count and demonstrates why a
validation interval and a precisely identified source snapshot are part of the
finding rather than incidental command details.

## The issue and adopted interpretation

Some represented bouts identify a winner and loser but do not record a
kimarite. Parts of the project treat those W/L outcomes as valid rating
evidence; at least one earlier process has excluded records whose decision
field is `blank`.

That created an inconsistency. Elo-89 uses the identities of the
competitors and the result of the bout. It does not otherwise use kimarite. If
the missing field means only that the winning technique was not recorded,
that omission does not disqualify an otherwise known result.

The adopted rule is therefore:

> A represented W/L result should count as rating evidence whether or not its
> kimarite is recorded, provided that it has the same required attributes and
> reliability as other represented W/L results.

This view was tested and is now the adopted conclusion of the mini-project.

## Questions investigated

The investigation was framed by the following questions about what “missing
kimarite” means in the actual sources and code:

- Does `decision="blank"` consistently mean that winner and loser are known
  but kimarite is absent?
- Are there several kinds of blank or missing record concealed by that label?
- Are all other bout attributes present and reliable?
- Which current and historical calculations include or exclude these bouts?
- Was exclusion a deliberate evidence rule or an expedient inherited from an
  earlier task?
- If the rule changes, which fitted artifacts, replays, evaluations and
  published outputs would need to be regenerated?

The audit and controlled comparisons resolved the rating-policy question.
Promotion still needs to trace and regenerate every production consumer
identified by the final question.

## Investigation approach followed

The work first oriented itself within this bounded issue and established:

1. the meanings carried by the relevant source fields;
2. the current behaviour of each affected pipeline;
3. the scale and character of the affected observations;
4. the dependency chain from bout eligibility through P1 and Elo-89 outputs;
   and
5. which questions are semantic, empirical or merely implementation details.

Those steps produced the audit, comparison, sensitivity and decision records
retained in this folder and the related P1 exploration folders.

## P1-WL comparison code

The controlled prior-fit comparison is implemented by
`src.validation.kimarite.p1_wl`. It preserves canonical P1 eligibility as the
control and fits a separate `P1-WL` candidate which positively selects every
represented binary W/L result. Both variants use the same selected History,
K configuration, fixed-point parameters and implementation; bout eligibility
is the declared controlled difference.

The selected History is first passed through the same `annotation_only` oracle
preprocessing as the canonical P1 producer. This removes rank annotations and
applies the established post-1988 bout-domain checks before either fit; it is
part of the shared control, not a difference between P1 and P1-WL.

Run the full comparison only as an explicit model-maintenance operation, using
the repaired frozen History snapshot:

```powershell
py -m src.validation.kimarite.p1_wl `
  --history-zip "files/output/Historys/1958_01 to 2026_11.zip" `
  --start 1989-01 `
  --output "src/validation/elo89-expert-account/Matters Arising/Kimarite/output/p1-wl-comparison"
```

The command refuses to overwrite an existing comparison directory. It writes
separate `p1` and `p1-wl` prior, iteration and manifest artifacts, followed by
a chii-level comparison table, summary statistics and a run manifest binding
the selected-History fingerprint and K configuration. Non-convergence returns
a non-zero process status. Each variant's manifest records the convergence
threshold, maximum permitted iterations, iterations actually taken, final
maximum prior change and convergence outcome. The console reports the
threshold, iterations taken and final maximum change, together with the
outcome, for both variants. The root manifest and console also report the
total wall-clock run time in seconds.

The complete historical determination was run on 25 October 2026. Both fits
converged in 18 iterations. See the findings document for the provenance,
results, interpretation and proposed next step.

The downstream tests are specified in
[`P1-WL Evaluation/README.md`](P1-WL%20Evaluation/README.md) and their results
are recorded in
[`P1-WL Evaluation/Findings.md`](P1-WL%20Evaluation/Findings.md). P1-WL retains
the case for informed initialisation and produces small, controlled but
non-zero downstream changes in exact Elo-89. The evidence supports adoption
of the positive binary-W/L rule followed by regeneration of dependent
artifacts; no production artifact has yet been changed.

A sensitivity run with epsilon reduced from 10 to 3 is recorded separately in
[`P1-WL Evaluation/P1WL3 Findings.md`](P1-WL%20Evaluation/P1WL3%20Findings.md).
Although both epsilon-3 variants meet their numerical stopping rule, sparse
literal-rank cells become extreme and predictive performance deteriorates
materially. P1WL3 is rejected; this does not alter the acceptance of the
epsilon-10 P1-WL repair, but it shows that the current stopping threshold acts
as de facto regularisation rather than mere numerical precision.

The subsequent broad sweep and local refinement are recorded in
[`../P1 Epsilon Sweep/README.md`](../P1%20Epsilon%20Sweep/README.md). They
confirm that the useful stopping region is iterations 18--21 and do not supply
a material reason to replace the established epsilon-10 rule.

## Relationship to the parent tranche

This mini-project follows the common method in
[`Matters Arising/README.md`](../README.md). Its eventual conclusion must say
not only whether numerical outputs change, but whether the accepted rule
matches the kind of performance evidence Elo-89 claims to use.

The likely hypothesis is that consistent inclusion will be a simple semantic
and code correction with little practical effect. The work must remain capable
of rejecting that expectation.
