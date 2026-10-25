# Kimarite

## Status

Active validation record for the first matter arising from the Elo-89 expert
account.

This folder investigates the treatment of represented results for which no
kimarite is recorded. The descriptive audit and controlled P1/P1-WL prior
comparison have now been run. The provisional prior-level findings are
recorded in
[`P1-WL Prior Comparison - Findings.md`](P1-WL%20Prior%20Comparison%20-%20Findings.md).
No production rating-code change or final model decision has been made.

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

## The issue as presently understood

Some represented bouts identify a winner and loser but do not record a
kimarite. Parts of the project treat those W/L outcomes as valid rating
evidence; at least one earlier process has excluded records whose decision
field is `blank`.

That creates a possible inconsistency. Elo-89 uses the identities of the
competitors and the result of the bout. It does not otherwise use kimarite. If
the missing field means only that the winning technique was not recorded, it
is not yet clear why that omission should disqualify an otherwise known
result.

The present intuition is therefore:

> A represented W/L result should count as rating evidence whether or not its
> kimarite is recorded, provided that it has the same required attributes and
> reliability as other represented W/L results.

This is a starting view, not the conclusion of the mini-project.

## What is not yet settled

Before specifying work, we need to understand what “missing kimarite” means in
the actual sources and code. Questions include:

- Does `decision="blank"` consistently mean that winner and loser are known
  but kimarite is absent?
- Are there several kinds of blank or missing record concealed by that label?
- Are all other bout attributes present and reliable?
- Which current and historical calculations include or exclude these bouts?
- Was exclusion a deliberate evidence rule or an expedient inherited from an
  earlier task?
- If the rule changes, which fitted artifacts, replays, evaluations and
  published outputs would need to be regenerated?

These questions indicate why the issue matters. They do not yet constitute an
approved investigation plan.

## Working approach

The next step is to orient ourselves within this bounded issue before writing
an experiment specification. That orientation should establish:

1. the meanings carried by the relevant source fields;
2. the current behaviour of each affected pipeline;
3. the scale and character of the affected observations;
4. the dependency chain from bout eligibility through P1 and Elo-89 outputs;
   and
5. which questions are semantic, empirical or merely implementation details.

Only then should this folder acquire separate audit, proposal, findings or
decision documents.

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

## Relationship to the parent tranche

This mini-project follows the common method in
[`Matters Arising/README.md`](../README.md). Its eventual conclusion must say
not only whether numerical outputs change, but whether the accepted rule
matches the kind of performance evidence Elo-89 claims to use.

The likely hypothesis is that consistent inclusion will be a simple semantic
and code correction with little practical effect. The work must remain capable
of rejecting that expectation.
