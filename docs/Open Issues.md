# Open Issues

## Purpose and status

This is a deliberately after-the-fact bucket for significant project-wide TBD
items that are not recorded adequately elsewhere.

Sumo-Tools grew through several investigations, infrastructure projects,
analyses and publication efforts. Their outstanding work is consequently
distributed across component-specific requirements, open-questions notes,
next-steps documents, deferred-design records and working plans. This document
does not yet reconcile, prioritise or supersede those records. It exists so
that newly recognised cross-project liabilities have somewhere durable to go
instead of remaining only in a conversation or being forced into the backlog
of whichever component happened to expose them.

A separate exercise must audit all existing TBD and open-issues documents,
deduplicate their contents, establish their authority and dependencies, and put
the remaining work into an intelligible order. That exercise should identify
which matters actually require resolution before the project can be considered
done and which are optional improvements. Until then, this document is a
capture bucket, not a roadmap or completion checklist.

## Inclusion rule

Add an item here when all of the following are true:

- it is significant to the project as a whole or crosses component boundaries;
- it is not already recorded adequately in an authoritative component document;
- losing track of it could compromise source data, shared domain semantics,
  multiple analyses or published claims; and
- resolving it now would distract from the active piece of work.

Component-local defects and ordinary feature ideas should remain with their
component. When an existing authoritative record already owns an issue, this
document should link to it rather than create a competing specification.

## Unordered captured items

### `Date` and `IntDate` are not interoperable History keys

The canonical live-store History is still populated by the parser with
`src.infra.parser.parser2_IntDate.IntDate` keys, while newer infrastructure,
including the future-Torikumi snapshot, constructs
`src.sumo_core.History.Date` values. `IntDate` subclasses `Date`, and both
values have the same `YYYY/MM` string form and hash for the same basho, but the
dataclass-generated equality on `Date` requires the same concrete class.
Consequently, a `Date(2026/09)` lookup does not find an existing
`IntDate(2026/09)` History entry.

This was exposed by the live-store-first Sumo '89 build: both the live History
and saved future snapshot represented `2026/09`, but direct dictionary
membership incorrectly reported that the basho was absent. The immediate
site89 compatibility repair resolves the actual History key by its canonical
string value, matching the existing Banzuke Changes approach.

The project-wide repair remains TBD. It should decide whether to:

- complete the parser migration from `IntDate` to `Date`;
- define deliberately interoperable equality and hashing for the date types;
- normalise History keys at a shared publication boundary; or
- provide one canonical History date-lookup operation and remove direct
  cross-boundary dictionary lookups.

Do not change core equality or silently rewrite persisted History keys as a
local site-builder fix. Such a change can affect tracker publication, History
ZIP compatibility, dictionary membership, ordering and other consumers. The
older parser migration records in
[`2026 03 24 FSM Next Steps.md`](2026%2003%2024%20FSM%20Next%20Steps.md) and
`src/infra/parser/FSM/docs/2026 03 24 Migration Issues.md` already identify the
unfinished `IntDate` replacement; this item records the demonstrated
cross-component failure mode and the required semantic decision.

### Mae-zumo presence, banzuke membership and result coverage

The parser intentionally excludes `Mz` because mae-zumo is not a formal
banzuke rank. Source banzuke and results pages may nevertheless contain `Mz`
entries and bouts, so absence from the project's parsed banzuke is not
equivalent to absence from basho activity. This ambiguity may affect parsing,
population inference, ratings, completeness checks and public products.

The history of the decision, interim terminology and required source-to-
product audit are recorded in
[`Mae-zumo (Mz) Data Semantics and Audit.md`](Mae-zumo%20(Mz)%20Data%20Semantics%20and%20Audit.md).

### Historical sub-sekitori bout-count invariant

The project contains several assumptions that rikishi below Juryo have a
normal maximum or expected total of seven bouts per basho. That is not valid
throughout the represented History. Makushita and lower divisions normally
fought eight bouts from March 1953 through May 1960; the seven-bout system began
in July 1960. Exceptional eighth bouts can also occur in the seven-bout era.

The raw daily-results parser does not appear to reject an eighth bout: it parses
the represented bout rows across all fifteen days without imposing a
per-rikishi quota. The invalid invariant does, however, occur in later code,
including absence inference, support denominators and result-display helpers.
There may be further occurrences in acquisition checks, legacy code, generated
artifacts, documentation or code paths not yet inspected.

This is broader than the construction of a ratings model. The acquisition and
representation of historical data support multiple analyses and products, so
the invariant must eventually be audited and corrected everywhere it affects
meaning. The repair must distinguish at least:

- the normal eight-bout era through May 1960;
- the normal seven-bout era from July 1960;
- exceptional eighth bouts in the seven-bout era;
- scheduled rest days represented by `hoshi_yasumi`;
- kyujo and fusen; and
- absence of detailed source results.

The audit should begin at source acquisition and parsing, then follow the data
through persistence, validation, analysis and publication. It should not assume
that a hard-coded seven is harmless merely because its current caller normally
selects post-1988 data. Tests and documentation should state the date-sensitive
domain rule explicitly wherever a bout-count expectation is genuinely needed.

### Missing kimarite is not a missing bout result

Some code excludes a `BoutResult` when its `decision` is `"blank"`, commonly by
grouping `"blank"` with `"fusen"`. This is wrong when `"blank"` means only that
the source has no recorded kimarite. If the paired outcomes are `W/L`, the
winner and loser are known and the bout is a valid observed result for ratings,
probability, bout counts and other result-based analysis.

The daily-results parser currently creates `decision="blank"` when the
kimarite cell is empty while still constructing the `BoutResult` from valid
outcomes. The newer clean-Elo and prediction work explicitly preserves and
tests this interpretation. Several other paths still exclude such bouts,
including legacy Equelo simulation and diagnostics, Equelo population-policy
replays, probability builders and empirical matchups, rising-rikishi analysis,
and an Expt2 delta diagnostic. Some documentation also describes `"blank"` as
a non-fought or non-rating event, contradicting the parser and the newer
contracts.

This issue must eventually be traced from parsing through every consumer. The
repair should establish one shared semantic distinction between:

- a known `W/L` result with an unavailable kimarite;
- a recorded fusen result;
- a draw or other represented non-standard outcome;
- a scheduled bout without a recorded outcome; and
- a genuinely absent bout record.

The audit must cover code, tests, diagnostics, generated statistics and prose.
Correcting only the principal ratings simulator would leave other published or
analytical bout populations inconsistent.
