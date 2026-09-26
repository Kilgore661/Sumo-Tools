# Mae-zumo (`Mz`) Data Semantics and Audit

## Status

This is a project-wide data-semantics warning and an open investigation. It
records a deliberate early modelling decision whose downstream consequences
have not been audited comprehensively.

Code must not assume that a rikishi absent from the project's parsed banzuke
was absent from all activity at that basho.

## How the ambiguity arose

Early in the project, source data for `Mz` appeared inconsistent across
basho: sometimes mae-zumo information was present and sometimes it was not.
The working interpretation became that `Mz` is not a real banzuke rank. It is
a designation for tryouts or mae-zumo participation, so an `Mz` rikishi should
not be represented as occupying a formal ranked position on the banzuke.

The parser consequently excluded `Mz` from the beginning. `Mz` entries are
not stored in the project's banzuke model or canonical `History` banzuke.
That decision may be correct for the rank model, but it also means that some
source information is discarded at the earliest stage of the main data
pipeline.

## The terminology trap

The expression "on the banzuke" is therefore not well defined in this
project. It may mean any of the following:

1. displayed somewhere on a source `Banzuke.aspx` page;
2. assigned a formal ranked banzuke position;
3. retained in the project's parsed `Banzuke`; or
4. included in a downstream population derived from that parsed banzuke.

In ordinary project discussion, "on the banzuke" has usually meant the third
or second sense: present on the formal banzuke, not counting `Mz`. That
qualification is easy to forget, making apparently simple claims about
presence, absence and population membership unsafe.

Until this is resolved, documentation and code should prefer explicit terms:

- **source-listed** for an entry displayed by the source;
- **formally ranked** for a genuine banzuke rank other than `Mz`; and
- **present in the parsed banzuke** for membership in the project's model.

## Concrete evidence from Torikumi work

The annotated Torikumi work exposed the issue again in September 2026.
SumoDB `Results.aspx` pages for the 2026/09 basho contained `Mz` bouts on Days
3, 4 and 5. Some participants, including new entrant Hajime (`r=13018`), were
absent from both the parsed banzuke and the canonical shikona store.

This is not necessarily bad source data. Mae-zumo rikishi can be called on to
face Jonokuchi rikishi when numbers need making up, and `Mz`-only bouts may
also appear in the results table. Because Elo89 ratings are computed for the
project's ranked population, these `Mz` participants have no Elo89 rating.
The Torikumi artifact therefore preserves their source shikona but displays
`-` for the missing rating and for both win probabilities.

That local presentation rule does not resolve the wider data-model question.

## Why this may matter elsewhere

Any code that treats parsed-banzuke membership as the complete universe of
possible participants may be wrong or incomplete. Areas requiring scrutiny
include:

- parsing and persistence of banzuke, torikumi and results;
- checks phrased as "is/is not on the banzuke";
- active-population and basho-participation inference;
- entrant, debut, absence, return and retirement logic;
- biography and shikona completeness;
- bout and result completeness audits;
- division membership and cross-division bout classification;
- rating-population construction and missing-rating handling; and
- public artifacts that join results to banzuke-derived populations.

The risk is not only omission of mae-zumo bouts. A consumer may incorrectly
interpret an intentionally omitted `Mz` participant as a malformed identity,
an impossible bout, a missing banzuke row, or evidence that the source data is
incomplete.

## Required investigation

A source-to-product audit should answer at least these questions:

1. For which basho do source banzuke pages display `Mz` entries?
2. For which basho do results pages record `Mz` bouts or results?
3. Are `Mz` results recorded if and only if `Mz` entries appear on the source
   banzuke page, or are the two independent?
4. Does the apparent inconsistency reflect genuine historical practice,
   changes in SumoDB coverage, page-layout differences, or parser behaviour?
5. Which combinations occur: `Mz`-`Mz`, `Mz`-Jonokuchi, and `Mz` against any
   higher division?
6. Are all `Mz` participants identifiable by stable rikishi ID and source
   shikona even when absent from the parsed banzuke and biography stores?
7. Which existing invariants and consumers equate parsed-banzuke absence with
   non-participation?

The audit should preserve separate observations for source listing, formal
rank, parsed representation, scheduled bout and completed result. Collapsing
those into one boolean "on the banzuke" field would repeat the original
ambiguity.

## Interim rules

Until the audit establishes a better model:

- Do not add `Mz` to `Chii` or the formal banzuke merely to make a consumer
  work.
- Do not silently discard an `Mz` bout encountered by a consumer that claims
  to represent all scheduled or completed bouts.
- Do not infer non-participation solely from absence from the parsed banzuke.
- Treat a missing rating for a known `Mz` participant differently from a
  missing rating for a formally ranked rikishi; the latter remains a data or
  production error.
- State explicitly whether a population excludes `Mz` whenever that affects
  the meaning of an analysis or public claim.

The eventual resolution may require a separate participation or source-entry
model alongside the formal `Banzuke`, rather than weakening the meaning of the
existing rank model.
