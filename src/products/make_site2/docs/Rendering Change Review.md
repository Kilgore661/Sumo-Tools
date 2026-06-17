# Rendering Change Review

This review has been split into smaller documents so each part can be read and updated without fetching the entire long file.

## Parts

- Rendering Change Review - 01 Purpose and Status.md
- Rendering Change Review - 02 Proposed Changes.md
- Rendering Change Review - 03 Design Classification.md
- Rendering Change Review - 04 Work Groups and Routing.md

## Current implementation status

Basho selector redesign: implemented as an interim PA-specific/runtime control.

Clickable Notes popovers: implemented as runtime popover-to-note interaction. Notes validation/tightening remains TBD.

Shikona link affordance: implemented across the shared table helper and Basho Results.

Career Length Longest / Show Active: implemented with produced ranked populations.

Row-number vs ranking semantics: resolved for the current table model and shared renderers.

Reviewed table visual-language, row-number/ranking and simple-chart rendering items are complete for the reviewed slice.

General bad-URL handling: minimal current behavior implemented. Richer handling policy is resolved but not implemented: bad deep URLs should alert and land on Home, while bad in-site navigation should alert and preserve the current view.

Remaining known work: Notes validation/tightening and a separate 3.3 Rikishi History follow-up.

## Notes

Settled rendering policy should move into 05 Rendering Design.md. Unresolved or provisional rendering decisions should be tracked in 06 Rendering Audit and Changes.md. Changes that affect table, chart, filter, control or interaction semantics should update the relevant 04.* model design documents before implementation.