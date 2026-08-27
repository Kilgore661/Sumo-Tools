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
