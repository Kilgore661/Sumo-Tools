# Sumo History Analysis

`analysis/sumo_history` owns analyses and presentation products derived from
the canonical `History` model. History construction itself must preserve the
aggregate contract that represented bout participants belong to the basho
banzuke domain.

## Known History-building defect

The annotated History source
`files/output/Historys/1958_01 to 2026_11.zip` (whose represented results
currently end at 2026/07) contains seven W/L bouts for RikId 13011 in 2026/07,
although RikId 13011 is absent from the 2026/07 banzuke:

```text
day 1:  Pair(12058, 13011)
day 3:  Pair(12783, 13011)
day 5:  Pair(12749, 13011)
day 7:  Pair(12686, 13011)
day 9:  Pair(12882, 13011)
day 11: Pair(12321, 13011)
day 15: Pair(12713, 13011)
```

This is a History-building bug, not a legitimate exception to the History
contract. Downstream code should not silently reinterpret the participant as
having a Chii. Analyses that must retain every represented W/L result should
identify any temporary policy used to accommodate the defect until the
History builder is corrected and the artifact rebuilt.
