# Live Store Refresh Caveat

## Purpose

This note records an accepted operational limitation of the Tracker's live data store.

The Tracker publishes canonical `History` in two forms:

- the durable canonical zip
- the live shared-memory store used by applications

When an update cycle finds new source data, the Tracker rebuilds canonical `History`, writes the canonical zip, and refreshes the live shared-memory store.

## Consumer model

A consumer obtains a snapshot of `History` from the live store. Once the snapshot has been successfully read and deserialised, it is local to that consumer process.

Consequently:

- a consumer that has already obtained `History` continues safely using its existing snapshot when the Tracker refreshes the live store
- that consumer does not automatically see newer data
- a later consumer read, after a successful refresh, obtains the updated snapshot

## Non-atomic refresh limitation

The current live-store implementation refreshes publication by removing and recreating the named shared-memory segment. Refresh is not atomic from the perspective of a consumer attempting to read at the same time.

Therefore, while the Tracker is refreshing the live store:

- a consumer read immediately before replacement may return the previous complete snapshot
- a consumer read after replacement completes returns the new complete snapshot
- a consumer read during replacement may fail because the shared-memory segment is temporarily unavailable or not yet readable

A consumer should not rely on uninterrupted availability during live-store refresh. A one-shot consumer may fail explicitly; a consumer that requires availability should be prepared to retry a failed read.

## Relationship to the update-cycle guarantee

The Tracker's all-or-nothing update guarantee applies at successful update-cycle boundaries: once publication completes, the durable and live forms represent the rebuilt canonical `History`.

It does not mean that concurrent reads during live-store replacement are atomic or guaranteed to succeed.

This limitation is accepted in the current design.