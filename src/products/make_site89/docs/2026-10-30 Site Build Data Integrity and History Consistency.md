# Site Build Data Integrity and History Consistency

## Status and purpose

This internal account records the agreed understanding of how source data,
canonical `History`, derived artifacts and the Elo-89 website relate. It also
records the minimum protocol required to prevent one site build from mixing
different published History generations.

It is site and infrastructure documentation, not part of the public-facing
expert account of the Elo-89 model. The model account explains what Elo-89
calculates from a supplied `History`; this document concerns the integrity of
the surrounding production process.

## End-to-end view

```text
downloaded source data
        |
        v
canonical History --------+---------------------+
        |                  |                     |
        |          frozen P1-prime-WL            v
        |          paired prior          other History analyses
        |                  |                     |
        +------------------+                     v
                           |             other derived artifacts
                           v                     |
                    Elo-89 replay                |
                           |                     |
                           v                     |
                    rating artifacts ------------+
                                                 |
bio data and                                    |
other sources ----------------------------------+
                                                 |
                                                 v
                                       website data bundle
                      |
                      v
                 make_site89
                      |
                      v
              static website tree
```

Canonical `History` is not mutated by this process. P1-prime-WL is a frozen,
source-controlled input rather than something refitted during a site build.
The Elo-89 replay and other analyses produce separately identifiable artifacts
keyed back to History basho, rikishi and bouts. The website combines those
artifacts with other sources and presentation material.

## Source acquisition: intended operating model

Ideally, every downloaded source file is exactly the file expected for its
basho and day, passes the applicable validation and thereafter remains a
correct representation of that source record.

In normal scheduled operation, the tracker:

1. determines the complete set of banzuke and daily-result files which should
   exist by the current time;
2. asks the downloader to ensure those files exist locally;
3. rebuilds and persists canonical `History` when the source collection
   changes;
4. publishes the rebuilt `History` to the live shared-memory store; and
5. resumes waiting for newly expected data.

The planner currently describes the full expected prefix from the project
epoch, while the downloader avoids fetching files which already exist. Newly
fetched pages receive only rudimentary structural checks. More specific
semantic expectations may be added as they become known.

## Source freshness is bounded

SumoDB sometimes changes a result after its first publication. Historical
pages are not continually downloaded and compared, so the project cannot
automatically discover every such revision. When an anomaly reveals a stale
local page, the present repair procedure is manual:

1. inspect the corresponding current SumoDB page;
2. delete the stale local source file; and
3. run the tracker with `--now`, causing the missing file to be fetched and
   `History` to be rebuilt and republished.

`--now` does not itself detect revisions. It bypasses the normal scheduling
gate after the operator has made the stale file missing.

Accordingly, a build should not be described as a complete snapshot of
everything visible at SumoDB on its build date. It represents the project's
locally held source collection as incorporated into the particular `History`
used for that build. Comprehensive automatic detection of upstream revisions
remains TBD. The project-level contract is recorded separately in
[Source Data Freshness and Upstream Revisions](../../../infra/docs/Source%20Data%20Freshness%20and%20Upstream%20Revisions.md).

## History freshness is also bounded

A consumer of the live store loads a complete unpickled `History` snapshot.
That object remains internally stable for the consumer, but the current API
does not identify its data generation or report that the tracker has since
published a newer generation.

This creates a separate freshness issue from upstream SumoDB revision:

```text
consumer loads History generation H1
tracker publishes History generation H2
consumer finishes without knowing that H1 is no longer the latest generation
```

The consumer's result may be internally consistent while still being stale.
Explicit live-store generation identity and consumer freshness checks remain
TBD.

## Rating enrichment

Given a valid `History`, the rating path is conceptually:

```text
frozen P1-prime-WL paired prior
            |
History ----+-- replay Elo-89 over the required interval
                    |
                    +-- rating, forecast and adjustment artifacts
```

The installed P1-prime-WL artifact was derived from:

- the exact input `History`;
- the inclusive `last-prior-basho`; and
- the P1-WL fitting algorithm and configuration; and
- direct support-weighted aggregation of the fitted literal cells.

The production default is 2026/09. It is the final basho included, not the
first basho excluded. The Elo-89 replay may extend beyond that value, and
never-rated rikishi appearing later are still initialised from the frozen
P1-prime-WL table. Routine replay and site builds do not refit it.

Artifact names should be readable, while content hashes provide exact
identity. Manifests should connect a readable build identifier to hashes of
the History, prior, configuration and other material inputs. The final naming
and registry convention remains to be implemented.

## Current website build consistency

`src.analysis.site89` loads `History` once and passes that same object to the
Elo-89 producer, rating-dependent producers and model-independent producers.
That part of the build is therefore internally consistent even if the tracker
publishes a newer live-store value after the initial load.

The complete `_boot89.ps1` sequence is wider. It runs Torikumi and structural
Banzuke-related prerequisites as separate processes before invoking the site
bundle producer. Each process can independently connect to the live store. A
tracker publication between them could therefore make one site bundle contain
artifacts derived from different History generations.

A check which merely asks whether the tracker is updating when the builder
starts is insufficient. The tracker could begin immediately after that check.

## Minimum safe-build protocol

The tracker and complete site build must use one atomic mutual-exclusion
mechanism.

1. The builder acquires the shared production lock before the first
   History-consuming prerequisite.
2. It holds the lock until the coherent site-data bundle has been completed.
3. The tracker acquires the same lock before rebuilding or publishing a new
   `History` generation.
4. If the lock is already held, the other process waits or exits with an
   explicit message according to declared policy.
5. Failure and interruption release the lock automatically.

This protocol guarantees that all History-derived inputs to one bundle see
the same published live-store contents. Holding the lock only around
`make_site89` would be too late: `make_site89` consumes a completed bundle and
does not load `History`.

## Preferred later protocol

A stronger design would hold the production lock only long enough to capture
one immutable History snapshot:

1. acquire the lock;
2. identify and persist the current History generation;
3. release the lock; and
4. require every build subprocess to consume that explicit snapshot.

The tracker could then continue operating during a long site build. This
requires every History-consuming prerequisite to accept the same explicit
snapshot, so the whole-build lock is the simpler initial implementation.

## Safe integrity claim

After the minimum protocol is implemented, the site may safely claim:

> Every History-derived artifact in this site build was calculated from the
> same published History generation.

It may additionally identify the build date, History generation and input
artifact identities. It must not turn that claim into a guarantee that every
locally cached page still matches the current SumoDB page.

## Remaining work

- Implement atomic mutual exclusion between History publication and the
  complete site-data build.
- Add live-store History generation identities and freshness-aware access.
- Bind readable artifact/build identifiers to exact content hashes.
- Decide when production should switch from a whole-build lock to one explicit
  immutable History snapshot per build.
- Continue adding bounded source validation while retaining the upstream-
  revision caveat.
