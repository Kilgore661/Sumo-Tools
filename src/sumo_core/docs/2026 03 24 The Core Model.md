## Reconstructed semantics of the codebase

This project models professional sumo history as a hierarchy of typed domain objects, not as loosely structured strings or tables. The key design idea is that display forms may be accepted at the boundaries, but the internal model is meant to be semantic and order-preserving. The most important example is `Chii`, which is the canonical rank object and whose authoritative value is its numeric `ordinal()`. The code says explicitly that comparison, sorting, grouping, indexing, and matrix axes must use the ordinal, never the rank string. 

At the top level, the model is:

`History : Date -> BashoState`

and

`BashoState = Banzuke × Summary`

where `Summary` is the combination of day-indexed results plus per-rikishi performance metadata. `History` is a dictionary-like partial function from `Date` to `BashoState`; `BashoState` contains exactly two fields, `banzuke` and `summary`; and `Summary` is a dictionary-like mapping from `Day` to `DailyResults` with an extra `performances` field of type `Performances`.

## Chii

A `Chii` is the authoritative model of a sumo rank. It has four semantic components:

`level`
`number`
`side`
`ann`

The code defines `level` as `Level = MSD + Division - {MAKUUCHI}`. In other words, makuuchi ranks are not represented by `Division.MAKUUCHI`; they are represented by the finer-grained `MSD` subdivision enum: `YOKOZUNA`, `OZEKI`, `SEKIWAKE`, `KOMUSUBI`, and `MAEGASHIRA`. Lower divisions are represented by `Division.JURYO`, `MAKUSHITA`, `SANDANME`, `JONIDAN`, and `JONOKUCHI`. `Level` rejects `Division.MAKUUCHI` outright.

The string form of a `Chii` is presentation only. The parser accepts display strings such as `M1e`, `Y1wTD`, and `Ms13wHD`, and decomposes them into level abbreviation, rank number, optional side suffix `e` or `w`, and optional annotation suffix. Accepted level tokens in the current code are exactly `Y`, `O`, `S`, `K`, `M`, `J`, `Ms`, `Sd`, `Jd`, and `Jk`. Anything else is rejected. That means the current implementation does not recognize `Mz`; if `Mz` is part of the real domain for mae-zumo, then the current rank grammar is narrower than the intended domain. 

The core semantics of `Chii` are embodied in `ordinal()`. The code says the encoding is effectively `lnnnas`, where `l` is the encoded level, `nnn` the rank number, `a` the annotation code, and `s` the side code. Lower ordinal means stronger rank. Equality, ordering, and hashing are all defined in terms of this ordinal, and `from_ordinal()` is intended as the inverse reconstruction. This is the basis for the requirement that rank strings must not be sorted lexicographically. For example, `M3eHD` is not semantically “a string”; it is a rank whose components are encoded into a fixed-width numeric key that preserves rank order. 

There is one explicit invariant enforced at `Chii` construction: `number` must be positive. The rest is trusted by contract. Internally, the code builds sortable keys so that makuuchi subdivisions come first, lower divisions follow after an offset, side is encoded from the `Side` enum, and annotations are encoded such that an unannotated rank outranks an annotated one with the same underlying level, number, and side. The code explicitly says that the precise ordering among non-empty annotations is artificial, but the important semantic guarantee is that empty annotation is stronger than non-empty annotation at the same base rank.

So the intended semantics of `Chii` are:

A `Chii` is not a display string. It is a semantic rank value object with canonical machine ordering. Display strings are only an input/output syntax layered over the semantic object. All logic that depends on rank order must use `ordinal()` or the `Chii` comparison operators, never string comparison. 

## Banzuke

A `Banzuke` is the rank roster for one basho. It is not modeled as a list of rows. It is modeled as an immutable aggregate with three coordinated components:

`riks : Riks`
`rikchii : RikId -> Chii`
`rikshik : RikId -> Shikona`

The code says its defining structural constraint is that these three have the same domain. In practice that means the set of rikishi IDs present in the basho must exactly match the keys of the rank mapping and the shikona mapping. If any domain differs, construction fails. 

This tells us the intended identity structure: identity is centered on `RikId`. Rank and displayed name are both attributes of that identity, but neither is itself the identity. The `Banzuke` aggregate also provides lookup helpers `get_chii(rid)` and `get_shik(rid)`, membership by rikishi ID, and length as the number of rikishi.

So the intended semantics of `Banzuke` are:

A `Banzuke` is the complete participant set of a basho together with two aligned projections from `RikId`: one to semantic rank (`Chii`) and one to display name (`Shikona`). It is structurally valid only when all three domains are identical. 

## Summary

A `Summary` represents the recorded outcome state of a basho. It is a mapping from `Day` to `DailyResults`, plus a side mapping from `RikId` to `Performance`. The code says explicitly that a `Summary` consists of a partial function from `Day` to `DailyResults` and a partial function from `RikId` to `Performance`.

The main aggregate invariant on `Summary` is temporal continuity. If any days are recorded, they must begin at day 1 and be contiguous with no gaps. The constructor enforces this by checking that the first day is 1 and every subsequent defined day is exactly one greater than the previous one. `last_defined()` returns the greatest defined day, wrapped as a `Day`, or `None` for an empty summary.

So the intended semantics of `Summary` are:

A `Summary` is the day-by-day competitive record of a basho, together with end-result performance metadata. It may be partial, but if partial it must still be a prefix from day 1 onward. 

## DailyResults

`DailyResults` is the per-day result aggregate. It contains:

`torikumi : Torikumi`
`results_lookup : Pair -> BoutResult`

The code explicitly says this class intentionally performs no internal validation because the relevant consistency constraints belong at a higher aggregate level. That is an important design point: lack of validation here does not mean lack of intended structure; it means validation responsibility is deliberately deferred.

So the intended semantics of `DailyResults` are:

It is the container for one day’s scheduled bouts and recorded results, but it is not itself the final enforcer of all schedule/result consistency rules. 

## BoutResult and Decision

A `BoutResult` models one recorded bout. It contains the two rikishi IDs, the two per-rikishi outcomes, the decision mechanism, and a display symbol. The constructor validates two things: the two rikishi must be distinct, and the pair of outcomes must be one of the established valid combinations. Those valid combinations are `{W, L}`, `{FS, FP}`, and `{DRAW, DRAW}`. Distinctness is enforced indirectly by constructing a `Pair`, which canonicalizes and rejects equal participants.

A `Decision` is not a simple enum. It is a constrained union: either a `Kimarite`, or the special string `"fusen"`, or the special string `"blank"`. The code comments say this is intentional because the domain is partly enum-valued and partly special string-valued.

`Kimarite` itself is a generated enum, written by `table_parser.py`, with a large set of known kimarite strings and a `from_string()` that maps unknown strings to `UNCLASSIFIED` rather than rejecting them. This strongly suggests the ingestion/parsing boundary is designed to be tolerant of noisy or incomplete source text. 

There is one noteworthy gap between apparent design and enforcement: `Symbol.inconsistent(out)` exists and clearly encodes the intended coherence rule between a displayed symbol and an `Outcome`, but `BoutResult.__post_init__()` does not call it. So symbol/outcome consistency appears to be part of the model’s intended semantics, but it is not currently enforced at `BoutResult` construction.

So the intended semantics of `BoutResult` are:

A bout result is a two-sided record with exactly two distinct participants, exactly one of the accepted paired outcome patterns, a resolution mechanism, and a display symbol. The current code enforces participant distinctness and outcome-pair validity, and it implies but does not enforce symbol/outcome consistency.

## Performance and Performances

`Performance` captures basho-level awards and status-change metadata for a rikishi. It has two fields: `prizes`, a frozen set of `Prize`, and `updown`, an optional `Direction`. It enforces one explicit invariant: a performance cannot include both `YUSHO` and `JUN_YUSHO`. `Performances` is simply a mapping from `RikId` to `Performance`.

The presence of `Direction.PROMOTION` and `Direction.DEMOTION`, along with `Prize` values such as `YUSHO`, `JUN_YUSHO`, `KANTO`, `SHUKUN`, and `GINO`, shows that `Summary` is meant to carry not only daily bout results but also high-level tournament outcome metadata.

So the intended semantics of `Performance` are:

It records basho-end honors and movement markers that are not naturally encoded in single-day bout records. 

## History, Date, and BashoState

`Date` is a value object for a basho date as `(Year, Month)`. It is immutable, hashable, orderable, and renders as `"YYYY/MM"`. Ordering is lexicographic on year then month. `History` is the partial function `Date -> BashoState`, implemented as a dictionary with call syntax. `BashoState` is the pair `{banzuke, summary}` and enforces that those two fields really are a `Banzuke` and a `Summary`.

There is one implementation wrinkle in `History`: its docstring says `__call__` returns the `BashoState` for a date “or None if undefined,” but the implementation uses `self[date]`, which will raise `KeyError` for an undefined date rather than returning `None`. That is best read as an implementation inconsistency, not as a semantic commitment. 

So the intended semantics are:

A `History` is the whole archive of basho states keyed by official basho dates, and each basho state is exactly the product of the roster/rank state (`Banzuke`) and the tournament-result state (`Summary`).

## Core primitive identity types

The codebase makes heavy use of “value objects” implemented as restricted subclasses of primitive Python types.

`RikId` is a positive integer and is the core identity type for rikishi. `Day` must be in `1..15`. `Month` must be in `1..12` and odd, reflecting the six-basho schedule. `Year` must be at least 1958, the start of the modern six-basho system. `Pair` is an unordered pair of distinct `RikId`s stored in canonical sorted order, so `Pair(a, b) == Pair(b, a)`. `Torikumi` is a set of `Pair`, but it deliberately does not enforce the stronger rule that the same rikishi cannot appear twice; that is reserved for higher-level validation. `Riks` is an immutable set of `RikId`. `Shikona` is a typed string. 

These are not incidental wrappers. They are the project’s way of making illegal states harder to represent. 

## What is strongly inferable from the code

The following points are strongly recoverable from the code itself.

First, `Chii` semantics are the center of the model, and its ordinal encoding is the authoritative rank order. Any LLM reconstructing the project should treat “sort rank strings lexically” as wrong by design. 

Second, `Banzuke` and `Summary` are the two canonical components of a `BashoState`, and `History` is a mapping from `Date` to `BashoState`.

Third, identity is centered on `RikId`, and most relationships are projections from `RikId` to semantic properties like rank, name, or performance.

Fourth, the code distinguishes strongly between local invariants that are enforced immediately and larger cross-record or tournament-wide invariants that are deferred to higher layers. This is stated explicitly for `DailyResults` and `Torikumi`.

## Where the implementation appears narrower or weaker than the intended domain

The clearest domain gap is `Mz`. The current `Chii.from_str()` grammar does not accept it, because the only accepted level abbreviations are `Y`, `O`, `S`, `K`, `M`, `J`, `Ms`, `Sd`, `Jd`, and `Jk`. If `Mz` is required to represent mae-zumo, then the current implementation under-models the domain. 

A second gap is symbol consistency. The code has an explicit `Symbol.inconsistent(out)` method, which implies a design rule tying symbols and outcomes together, but `BoutResult` does not currently enforce that rule.

A third soft spot is `History.__call__()`, whose behavior does not match its own docstring on undefined dates. 
