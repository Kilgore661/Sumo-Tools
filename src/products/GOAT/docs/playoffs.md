# Playoffs: provisional production contract

## 1. Status

Detailed playoff ingestion is unsettled and currently parked because SumoDB is
unavailable. This does not block production work that either does not depend on
playoff bouts or can represent their absence explicitly.

The existing `History` contains no playoff bouts. Its performance markers do,
however, provide a reliable Makuuchi playoff-participant oracle:

- the champion is marked `Y`;
- every other tied leader is marked `D`; and
- tied playoff participants are not marked `J`.

The exploratory whole-history probe found 85 Makuuchi playoffs from 1958/01
through 2026/07: 75 two-way, eight three-way, one four-way and one five-way.
It found no departures from the one-`Y`, remaining-`D` convention.

## 2. Candidate source

Some SumoDB **Current standings** HTML pages contain a **Playoffs** link. It
targets the normal `Results.aspx` endpoint with `d=16`. This appears to be a
transport convention for playoff results, not a sixteenth regulation day.

When SumoDB returns, inspect ordinary two-way playoffs and the known multiway
cases, especially 1996/11 (five rikishi) and 1997/03 (four rikishi). Establish:

- the exact URL convention;
- whether all bouts appear and in what order;
- how winner, loser and kimarite are represented;
- whether repeated or special multiway rounds need more structure; and
- whether the distinct participants reconcile with the `Y`/`D` set.

Raw source provenance should be retained. A source snapshot or digest is
preferable to storing only the URL.

## 3. Assumed `History` extension

Production GOAT code assumes a future enhanced history has a lower-case
`playoffs` attribute with this structural shape:

```text
history.playoffs[basho] -> iterable of playoff-bout objects

playoff-bout object:
    sequence: positive integer
    winner_id: RikId
    loser_id: RikId
    source: non-empty string
```

The parser may own whatever concrete `Playoffs` and playoff-bout classes best
fit the core model. The GOAT consumer does not require their class identity; it
requires only the attributes above. `basho` need not be repeated on each bout
because it is the key of the outer mapping.

Do not add `Day(16)` to `Summary`. The established `Day` domain is 1 through 15
and playoff sequence is not a scheduled basho day.

The consumer contract should remain minimal until the HTML is observed. Add
kimarite or round information only if it is available and a GOAT requirement
actually uses it.

## 4. Current consumer behaviour

`src/goat/playoffs.py` projects any parser-owned objects into a stable internal
record and assigns one of four states to each basho:

| Status | Meaning |
| --- | --- |
| `no_playoff` | No Makuuchi `D` marker; detailed data is not required. |
| `unavailable` | `Y`/`D` identifies a playoff but no detailed entry exists. |
| `incomplete` | Detail exists but does not reconcile with the marked participants. |
| `complete` | Detail exists and its participant set matches the `Y`/`D` set. |

Playoff appearances are calculated from `Y`/`D` and therefore remain available
for old histories. Playoff wins and losses are available only when every
relevant playoff in the selected scope is complete. If any is unavailable or
incomplete, the aggregate wins and losses are unavailable—not zero, and not an
unlabelled partial total.

The same completeness rule applies to metrics that require contested playoff
bouts:

- win rate;
- contested head-to-head;
- strength of opposition;
- record by opponent banzuke level; and
- average level of defeated and defeating opponents.

Until detailed data exists, implementations may expose a clearly labelled
scheduled-contested subtotal, but must not label it as the playoff-inclusive
measure required by the specification.

## 5. Validation rules

At minimum, the eventual producer/consumer path must verify:

- sequence numbers are positive and unique within a basho;
- winner and loser are distinct valid rikishi IDs;
- source provenance is non-empty;
- the distinct bout participants equal the Makuuchi `Y`/`D` participant set;
- all participants were on the relevant Makuuchi banzuke; and
- the recorded overall winner reconciles with the `Y` marker once bout ordering
  has been confirmed from the source.

Sequence contiguity and “last listed winner equals champion” should not become
hard invariants until the `d=16` representation has been checked.

## 6. Resumption checklist

1. Capture representative `d=16` pages and record their URLs.
2. Extend the exploratory probe to parse them without changing the core model.
3. Compare parsed participants with the existing marker oracle.
4. Decide the concrete core `Playoffs` model and serialization format.
5. Extend the parser and both live-store and zip paths.
6. Run whole-history reconciliation and investigate every exception.
7. Promote the data to production and enable dependent GOAT metrics.

The earlier investigative detail and list of multiway basho remain in
`src/analysis/goat/docs/playoff-data.md`.
