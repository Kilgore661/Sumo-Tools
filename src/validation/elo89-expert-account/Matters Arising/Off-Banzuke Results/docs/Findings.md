# Findings: off-banzuke result status and epoch

## Result

The repaired frozen History contains exactly **five** represented bouts with
an endpoint absent from the same-basho parsed banzuke.

The two questions have unambiguous answers:

1. **Are the off-banzuke rikishi actually Mz?** Yes. Each bout has exactly one
   missing endpoint, and the cached SumoDB career page gives that endpoint the
   literal same-basho status `Mz`. There are five missing endpoints, five Mz
   statuses, no other status and no unresolved source row.
2. **Do the bouts occur in the post-1988 era?** No. All five occurred in
   `1974-11`; the post-1988 count is zero.

| Epoch | Off-banzuke bouts | Missing endpoints | Mz endpoints | Other or unresolved |
|---|---:|---:|---:|---:|
| 1958–1988 | 5 | 5 | 5 | 0 |
| 1989–2026/09 | 0 | 0 | 0 | 0 |

The five bouts are:

| Basho/day | Mz rikishi | Ranked opponent |
|---|---|---|
| 1974-11 day 3 | Tatsuwaka (8262) | Ura (8319), Jk17w |
| 1974-11 day 5 | Hinodeshima (8216) | Kotonoshima (8228), Jk18e |
| 1974-11 day 7 | Tochikoma (2151) | Tatsugo# (1499), Jk18w |
| 1974-11 day 7 | Taniguchi (5829) | Takanomine (1366), Jk16w |
| 1974-11 day 7 | Mifuneyama (7470) | Kotonoshima (8228), Jk18e |

All five are ordinary represented W/L results. The retained Elo-89 selector
would rate that result form without consulting banzuke membership, but the
bouts precede the Elo-89 epoch.

## Reconciliation

The census exactly reproduces the five `participant_not_on_banzuke` rows from
the earlier Equelo2 full-history experiment and adds their same-basho source
classification: all are Mz.

The rating-persistence census found only Tatsuwaka because it asked a narrower
question: whether a rikishi who later returned to the ranked banzuke had a
represented bout during the intervening gap. The present census inspects every
result endpoint and therefore also finds Mz participants who do not satisfy
that gap-and-return definition.

The previously documented seven `2026-07` bouts involving RikId 13011 are
also reconciled. All seven remain represented, but the repaired History puts
the rikishi on that basho's parsed banzuke at `Sd80eTD`. They were evidence of
an earlier banzuke-parsing defect, not seven current off-banzuke bouts.

## Consequence for Elo-89

There is no realised off-banzuke-result issue in the represented post-1988
History. An include-versus-exclude historical Elo-89 comparison would compare
identical bout streams and ratings, so it would supply no evidence and has not
been run.

The result does not prove that source pages contain no post-1988 Mz bouts.
Known source-level Mz activity may be omitted before canonical `History` is
formed. That is a separate source-completeness and data-model question. It
must not be described as an off-banzuke result already present in Elo-89.

The prospective contract conflict remains: current code would rate a future
represented off-banzuke W/L result, while older named-model prose says it is
excluded. Nothing in the realised Elo-89 history distinguishes those policies.
Resolving that prospective rule can therefore be deferred until the project
decides whether and how Mz results should be represented upstream.

## Reproduction

From the repository root:

```powershell
py -m src.validation.off_banzuke_results
```

The retained run is beneath
`files/output/validation/elo89-expert-account/Matters Arising/Off-Banzuke
Results/output/` and uses the repaired History through `2026-09`.
