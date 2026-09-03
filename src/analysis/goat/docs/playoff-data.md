# Playoff data: findings and parked follow-up

Status: parked on 2026-09-03 pending the return of SumoDB.

## What the existing `History` data tells us

The stored basho records do not contain playoff bouts. They do contain the
administrative result markers attached to a rikishi's tournament performance:

- `Y` (`Prize.YUSHO`) for the champion;
- `D` (`Prize.DOTEN_YUSHO`) for a playoff participant who did not win the
  yusho; and
- `J` (`Prize.JUN_YUSHO`) for a runner-up who was not in the playoff.

The exploratory probe in `src/analysis/goat/playoffs.py` examined every
Makuuchi basho in the live `History`, from 1958/01 through 2026/07. It found 85
basho in which two or more rikishi shared the leading regulation win total:

| Number tied | Basho |
| ---: | ---: |
| 2 | 75 |
| 3 | 8 |
| 4 | 1 |
| 5 | 1 |

In all 85 cases there was exactly one `Y`, and every other tied leader was
marked `D`. None of the tied leaders was marked `J`. This validates `Y` and `D`
as a reliable way to identify the complete set of playoff participants in the
available data.

The multi-rikishi playoffs found by the probe were:

- 1961/09, 1965/09, 1990/03, 1993/07, 1994/03, 2022/11, 2025/01 and 2026/07:
  three rikishi;
- 1997/03: four rikishi; and
- 1996/11: five rikishi.

The probe writes its detailed tables to
`files/output/analysis/goat/playoffs/`.

## Potential source for the missing bouts

Some SumoDB **Current standings** HTML pages contain a link labelled
**Playoffs**. The link uses the ordinary `Results.aspx` endpoint with the day
parameter set to `d=16`.

This is probably sufficient to recover the actual playoff bouts, including the
ordering and winner of each bout, but it has not yet been verified because
SumoDB is currently unavailable.

`d=16` should be treated as a SumoDB transport convention for playoff results,
not as a sixteenth regulation day. The core `History` model deliberately
restricts `Day` to 1 through 15. If the page supplies the expected information,
playoff bouts should therefore be held as supplementary GOAT data rather than
forced into the existing day model.

The `Y`/`D` markers remain useful even after this source is added: they give us
an independent completeness check on the participants parsed from the playoff
page.

## Work to resume when SumoDB is available

1. Inspect a normal two-rikishi playoff page and examples of three-, four- and
   five-rikishi playoffs. In particular, use 1996/11 and 1997/03 to expose any
   multiway formatting differences.
2. Confirm the exact URL/query convention and the structure of the returned
   HTML.
3. Establish whether the page records every bout's participants, result order
   and kimarite, and whether any special multiway-playoff events are represented
   differently.
4. Parse the pages initially in the analysis probe and reconcile the distinct
   participants against the tournament's one `Y` plus all `D` rikishi.
5. Preserve source provenance and add fixtures/tests before promoting the
   parser into production code under `src/goat`.

A minimal supplementary record is likely to need:

- basho date;
- playoff-bout sequence number;
- winner rikishi ID;
- loser rikishi ID;
- kimarite, if supplied; and
- source URL (and, preferably, a retained source snapshot or digest).

## Production consumer contract

Production analysis can proceed without waiting for the parser. The adapter in
`src/goat/playoffs.py` assumes that a future enhanced history exposes a
lower-case `playoffs` mapping:

```text
history.playoffs[basho] -> iterable of playoff bouts

playoff bout:
    sequence
    winner_id
    loser_id
    source
```

This is a structural contract: the parser remains free to own and name its
concrete `Playoffs` and playoff-bout classes. No dependency on a parser class is
required so long as these attributes are supplied.

An old history, or an enhanced history lacking an entry for a known playoff,
is treated as having **unavailable** detail. Playoff appearances can still be
reported from the `Y`/`D` markers, but wins and losses are reported as
unavailable rather than zero. Supplied details are checked against the marked
participant set and classified as complete or incomplete.

The `d=16` source investigation is still parked until the pages can be
examined. At that point the parser's output can be matched to this consumer
contract; the contract should only be expanded if the HTML proves that another
field is both available and required.
