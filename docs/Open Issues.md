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

### Resolved: `Date` and `IntDate` were not interoperable History keys

The live parser formerly populated History with an `IntDate` subclass while
newer infrastructure constructed the canonical `Date`. Dataclass equality
requires the same concrete class, so equivalent basho dates did not work as
the same dictionary key. This was exposed by the live-store-first Sumo '89
build.

The parser migration is now complete: integer inputs go through
`Date.from_ints`, parser and tracker publication use canonical `Date` keys,
and `IntDate` has been removed. The temporary string-based lookups in the
Sumo '89 publishers have also been removed. Parser and tracker tests assert
that published keys have the exact canonical type. Existing History ZIPs are
already deserialised as canonical dates; rebuilding them from the parser keeps
the persisted artifacts aligned with the live-store path.

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

This defect also affects the canonical `P1` entrant prior used by Elo-89, even
though the Elo-89 production replay itself already rates binary `W/L` outcomes
without requiring a kimarite. The required `P1` correction, controlled
regeneration, predictive comparison, adoption procedure and `_boot89.ps1`
boundary are recorded in
[`Elo-89 P1 Missing-Kimarite Repair.md`](Elo-89%20P1%20Missing-Kimarite%20Repair.md).

### Analysis-dependent documentation

The experts' accounts, other project documentation and published HTML contain
charts, tables, statistics, examples and incidental factual claims whose truth
depends on project data, analytical methods or both. A claim such as the number
of yokozuna in a period may look like ordinary prose while still being a
derived result. It can become stale when the represented History changes, but
also when rank parsing, population rules, aggregation, weighting, eligibility
rules, parameters, policy choices or other algorithms change.

The project must identify these analysis-dependent documentary elements and
replace manually maintained results with a deterministic documentation-build
mechanism. That mechanism should be driven by persisted, identified inputs,
versioned algorithms, explicit parameters and recorded policy choices. It must
cover prose values and examples as well as conspicuous tables and charts, and
it should support the experts' accounts, project documentation and public HTML
rather than solving the problem separately in only one publisher.

Each generated result should retain enough provenance to identify the data,
code, configuration and method that produced it. The build should detect or
fail on results that are stale, irreproducible or inconsistent with the
currently installed analysis. Required work therefore includes:

- inventorying data- and method-dependent claims across documentation and
  publication outputs;
- ensuring that their required inputs and intermediate analytical results are
  persisted or reproducibly derivable;
- defining a shared way to insert generated charts, tables and inline prose
  values into source documents;
- recording the relevant data, algorithm, parameter, policy and code-version
  provenance; and
- adding build-time checks that expose stale or non-reproducible documentary
  claims.
