# Revision Provenance

This is the second expert-facing account of Elo-89. It is a successor to the
baseline account first committed as `aa311ee` and subsequently retained under
`src/validation/elo89-expert-account`.

The baseline account is not overwritten. Its `Matters Arising` folder records
the investigations which motivated this edition. The consolidated handoff is:

[`../elo89-expert-account/Matters Arising/Three Matters - Summary and Review Handoff.md`](../elo89-expert-account/Matters%20Arising/Three%20Matters%20-%20Summary%20and%20Review%20Handoff.md)

## Accepted changes incorporated here

This edition describes the intended successor Elo-89 contract:

1. Every represented binary W/L result is eligible whether or not kimarite is
   recorded. The fitted entrant artifact is the accepted epsilon-10 **P1-WL**
   prior rather than canonical P1. This table was fixed on 30 October 2026
   using the represented history through the September 2026 basho. Later
   results do not refit it.
2. A rating and its provenance are frozen outside the represented active
   population and restored on return before the ordinary start-of-basho
   adjustment. An inactive archive receives no updates or common shifts and
   contributes to no active mean.
3. The repaired History contains no represented off-banzuke result in the
   post-1988 interval. The five known cases are Mz bouts from `1974-11` and do
   not affect Elo-89.

## Implementation boundary

These are accepted model decisions, supported by the retained validation
work. At the time this edition was drafted, canonical production promotion
and regeneration of the public artifacts were still outstanding. Therefore:

- normative passages state the accepted successor contract;
- historical passages identify the earlier P1/reset implementation when that
  distinction matters; and
- no candidate validation site is described as the deployed public site.

The account must be checked again against the promoted implementation and
artifact identities before public integration.
