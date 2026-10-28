# Ranked-Banzuke Gap Census

## Result

The reproducible Elo-89 census finds **437 gap-and-return events involving 365
rikishi** between `1989-01` and `2026-09`.

Of those events:

- 436 (99.771%) are `Jonokuchi -> unranked -> Jonokuchi`;
- the remaining event is Sokokurai's `M16e -> Kg/Bg -> M15w` return;
- none contains a represented bout involving the absent rikishi;
- none crosses the sekitori boundary; and
- two have no cached SumoDB career row for the intervening `2026-07` basho.

The two source-status omissions are Kuwae and Daiko. Both leave and return in
Jonokuchi, and both are absent from the July 2026 ranked banzuke. The History
evidence establishes their gap-and-return events; only the administrative
label for the intervening basho is missing from the currently cached career
pages. The census reports this incompleteness rather than inferring a status.

Across the other 435 events, every represented gap basho has a cached career
row. Their intervening status rows comprise:

| Status | Rows |
|---|---:|
| `Bg` | 547 |
| `Mz` | 424 |
| `Kg` | 12 |

The affected rikishi are 8.008% of the 4,558 distinct rikishi appearing on a
ranked banzuke in the selected Elo-89 interval. The percentage is a lifecycle
description, not a measure of rating impact: an individual can generate more
than one event, and nearly every event occurs at the model's least reliable
exact-chii prior boundary.

## Interpretation: most gaps are mae-zumo boundary cycles

The distribution is more informative when expressed per event rather than as
counts of intervening status rows. Of the 436 Jonokuchi-to-Jonokuchi events:

- 424 (97.248%) contain an explicit `Mz` career row;
- 207 are exactly `Jk -> Mz -> Jk`;
- 217 contain one or more `Bg` rows followed by `Mz` before the return;
- 10 contain `Bg` but no `Mz`; and
- 2, Kuwae and Daiko, have no intervening row in the currently cached career
  page.

The parser's treatment of these cases is an inherited model boundary, not a
finding that mae-zumo is outside Grand Sumo. Its documented and implemented
contract excludes `Mz` from the persisted `Banzuke` and `History`, ignores
`Mz`-versus-`Mz` results, and retains an `Mz` participant only transiently when
needed to interpret a bout against a ranked rikishi. Consequently, a rikishi
moving from Jonokuchi into mae-zumo disappears from Elo-89's active population
even though the source describes a continuing administrative and competitive
lifecycle.

This explains nearly the entire apparent disappearance population. The 436
lower-boundary cases are best understood as consequences of the ranked-only
representation; Sokokurai is the sole post-1988 event of a substantively
different kind.

Two policy questions must remain separate:

1. Should Elo-89 preserve an existing rating while a rikishi is absent from
   the ranked representation?
2. Should results between mae-zumo participants become rating evidence?

The first does not depend on the second. Elo-89 can archive a rating across an
unranked interval, continue to ignore `Mz`-versus-`Mz` bouts, and restore the
rating when the rikishi returns. This implements the proposed rule that an
absence of represented competition supplies no new information, without
requiring an `Mz` chii, prior or K value.

Admitting `Mz`-versus-`Mz` bouts would be a larger change to the model's
population boundary. It would require policies for unranked initialisation,
K, population normalisation and the interpretation of very sparse results.
Nothing in this census establishes that such complexity would be useful, and
the known instability of low-support exact-chii evidence makes it unlikely to
be material to the present decision.

Kuwae and Daiko do not weaken this interpretation. Their ranked History
records establish `Jk -> unranked -> Jk` cycles; their cached career pages end
before the intervening July 2026 basho, so the source available to this run
cannot prove the administrative label. The census therefore leaves their
status unresolved rather than inferring `Mz` from the dominant pattern.

## Reproduction of the earlier audit

The same program was run from `1958-01` through `2026-07` to reconstruct the
figures previously recorded without identifiable census code or atomic output.
It reproduced them exactly:

- 679 events;
- 590 affected rikishi;
- 9,071 distinct ranked rikishi;
- 666 `Jonokuchi -> unranked -> Jonokuchi` events;
- 739 intervening `Bg` rows;
- 663 intervening `Mz` rows;
- 67 intervening `Kg` rows;
- 6 intervening `Sj` rows; and
- 2 unresolved `??` rows, both belonging to Muraishi.

This agreement establishes that the new event definition has recovered the
one used in the earlier narrative. It also exposed one historical off-banzuke
bout: Tatsuwaka has a represented bout in `1974-11` while his career status is
`Mz`. That case lies outside the Elo-89 epoch and belongs to the separate
off-banzuke-results matter.

## Sources and retained outputs

Both runs used the repaired frozen History:

```text
files/output/Historys/1958_01 to 2026_11.zip
SHA-256 afddcc2a77aa237d539073008bf46414989eb766cad8b281cf719963141793ca
```

The Elo-89 run used 365 cached `Rikishi.aspx` pages with aggregate SHA-256
`e79557c70f142718b5dd061b3e551d86ce6ad6525d6a984b721b0ba27aac143d`.

The generated evidence is retained beneath:

```text
files/output/validation/elo89-expert-account/Matters Arising/Rating Persistence/output/
```

The two run directories are:

```text
rating-persistence-census_1989-01_to_2026-09_2026-10-28_10-44-17
rating-persistence-census_1958-01_to_2026-07_2026-10-28_10-44-50
```

Each contains the atomic event table, exceptional cases, division transitions,
gap-length and status summaries, readable findings, and a manifest binding the
interpretation to its input fingerprints.

## What this establishes

The census establishes that current Elo-89 repeatedly discards existing
ratings, but that its return population is extraordinarily homogeneous. The
ordinary case is an administrative Jonokuchi cycle. Sokokurai is the only
post-1988 case involving a rikishi ranked above Jonokuchi before or after the
gap.

It does not establish that persistence is better than reinitialisation. The
next tranche will therefore explore what happens when ratings are persisted
across these absences. Its controlled comparison must measure the ratings
discarded under the current rule, the P1-WL values assigned on return, and the
subsequent predictive effects of retaining rather than resetting them.
Aggregate results should report Sokokurai separately from the 436 Jonokuchi
events so that neither population conceals the other. This experiment will
hold the current exclusion of `Mz`-versus-`Mz` bouts fixed: it tests rating
persistence, not an expanded bout domain.
