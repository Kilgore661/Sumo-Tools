# Source Data Freshness and Upstream Revisions

## Status

This document defines the project-level contract for downloaded source data.
It applies to the tracker, downloader, parser, canonical `History`, live store
and downstream products. Component documentation may describe how this
contract is implemented, but must not claim a stronger freshness guarantee.

## The contract

Sumo-Tools downloads source pages from SumoDB and preserves the representation
available at the time of acquisition. It can check that a downloaded page is
structurally usable and that its parsed contents satisfy known semantic rules.

It cannot guarantee that a preserved page remains identical to SumoDB. SumoDB
may correct a page after it has been downloaded. Detecting every such change
would require continually re-downloading and comparing the historical corpus,
which is not a realistic operating policy.

The project therefore distinguishes:

- **validity at acquisition**: the downloaded representation passed the checks
  known and applicable when it was processed; and
- **continuing freshness**: the representation still agrees with the current
  upstream page.

The first is a reasonable system responsibility. The second is not guaranteed.
Terms such as *valid*, *complete*, *current* and *up to date* must be read in
that bounded sense unless a particular artifact states a stronger contract.

## User caveat

Public products which depend on the downloaded results should disclose:

> Results are downloaded from SumoDB during each basho. SumoDB may subsequently
> correct its records, and historical pages are not routinely re-downloaded.
> The data shown here therefore reflects the version available when each page
> was captured and may not include later corrections.

A shorter disclosure is acceptable where space is limited:

> Results are captured daily from SumoDB; later corrections may not be
> reflected here.

This is part of the data contract, not merely a temporary implementation
limitation.

## Validation and attention

Known semantic expectations should still be enforced. A failed expectation is
evidence that a download may have been premature, incomplete, affected by an
upstream format change, or otherwise in need of investigation. The affected
source page should be identified precisely and flagged for re-download or
manual attention rather than silently treated as authoritative.

One established expectation is:

> Every represented binary W/L bout from 1991-07 onward has a recorded
> kimarite.

This is a source-data validation rule, not an Elo eligibility rule. A known
winner and loser remain usable bout evidence for rating purposes even when the
kimarite field is absent. In the post-1991-07 corpus, however, a missing
kimarite is sufficiently anomalous to require attention.

Validation rules will evolve as new consumers need additional fields or new
source behaviour is discovered. Each new rule should record:

- what is required and why;
- the artifacts and date range to which it applies;
- the evidence supporting the rule;
- the action to take on failure; and
- whether existing cached artifacts must be revalidated or re-downloaded.

When a cached page is replaced, the reason for replacement and, where
practical, the old and new content hashes should be retained. This supplies a
change history for deliberate repairs without suggesting that unobserved
upstream changes can be detected automatically.

## Retrieval policy

Daily results are normally acquired during each basho. Existing historical
pages are not routinely re-downloaded merely to discover whether SumoDB has
made a later correction.

The system may make bounded additional checks, such as refreshing the fifteen
daily pages shortly after a basho or re-downloading an artifact which violates
a known rule. Such checks improve the likelihood of capturing prompt
corrections, but do not establish continuing freshness and do not remove the
user caveat.

Checksums also have a limited role. A checksum can identify local corruption
or show that two acquired representations differ. It cannot reveal an upstream
revision unless the upstream page is fetched again.
