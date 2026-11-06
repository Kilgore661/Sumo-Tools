# 1989--1998 Bout-Data Completeness Audit

## Purpose

Elo-89 begins in January 1989. Its calculation requires the banzuke and the
identity and result of every bout between rikishi on the banzuke. SumoDB's
public description says that lower-division bouts are complete only from 1999,
so the first ten years of the Elo-89 period required a direct check rather
than reliance on that general description.

This audit records the check performed during the November 2026 review of the
Elo-89 expert account. It concerns the sixty basho from January 1989 through
November 1998 inclusive.

## Audit question

For each basho:

1. which rikishi and chii appear on the banzuke;
2. which lower-division result symbols appear in their career records; and
3. whether those results are accounted for by opponent-paired daily bout
   records.

The relevant test is not whether every daily results page contains a
lower-division bout. Lower-division rikishi ordinarily fight on only seven of
the fifteen days. The test is whether the banzuke population's recorded
results are present as paired bouts across the basho.

## Source and method

The audit used the repository's current SumoDB-derived banzuke, daily-result
and rikishi-career material. For each of the sixty basho, lower-division daily
records were paired by opponent and compared with the corresponding career
result symbols.

A basho passed the strict comparison when the paired daily data accounted for
the career symbols for every relevant rikishi. Fusen and exceptional outcome
symbols were retained separately rather than forced into ordinary W/L pairs.
Blank kimarite did not make a known W/L bout incomplete because Elo-89 does
not use kimarite when selecting an eligible result.

This was a direct audit of the current source snapshot. It was not packaged as
a reusable analysis command, so its numerical totals should be regenerated if
the upstream source or parser changes.

## Results

All sixty basho contain opponent-paired lower-division bout data.

- Fifty-nine basho match the corresponding career result symbols exactly.
- The sole mismatch is Sasaki (`r=386`) in November 1998. His cached career
  symbols show the basho as all absences, while the published score is 2--5
  and the daily results contain all seven of his bouts. The daily paired data
  are therefore present despite the anomalous career symbols.
- The checked period contains 148,262 eligible W/L bouts involving at least
  one lower-division rikishi.
- It also contains 628 fusen results, one draw and two malformed double-FP
  records. These are recorded-data classifications, not missing ordinary
  W/L bouts.
- Blank kimarite occur only in the first fifteen basho, from January 1989
  through May 1991. They do not affect Elo-89 bout eligibility.

## Conclusion

For January 1989 through November 1998, the current SumoDB-derived record
contains the banzuke and the paired bout evidence required by Elo-89 for
rikishi on the banzuke. Combined with the later record, this supports using
January 1989 as the model's direct operational data boundary.

This conclusion is narrower than claiming that every item SumoDB might record
about lower-division sumo is complete. In particular, it does not require a
complete record of Mae-zumo against Mae-zumo, because Mae-zumo participants
are not rikishi on the ranked banzuke. The separate
[Mae-zumo data audit](Mae-zumo%20%28Mz%29%20Data%20Semantics%20and%20Audit.md)
documents that distinction and the remaining source-model questions.

## Reproducibility limitation

The audit result is now preserved, but the audit itself is not yet a permanent
runner with a saved manifest and machine-readable output. If this conclusion
becomes a release gate, the appropriate next step is to package the comparison
against a declared source snapshot and retain its per-basho results.
