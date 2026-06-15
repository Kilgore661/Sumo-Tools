# Rendering Change Review - 01 Purpose and Status

## Status

Review note for a proposed `make_site2` rendering change set.

This document describes the proposed change set before classifying its likely
design and implementation impact. It is not, by itself, normative rendering
design.

Settled rendering policy should move into `05 Rendering Design.md`. Unresolved
or provisional rendering decisions should be tracked in
`06 Rendering Audit and Changes.md`. Changes that affect table, chart, filter,
control or interaction semantics should update the relevant `04.*` model design
documents before implementation.

Implementation status:

```text
Basho selector redesign: implemented as an interim PA-specific/runtime control.
Clickable Notes popovers: implemented as runtime popover-to-note interaction.
Shikona link affordance: implemented across the shared table helper and Basho Results.
Career Length Longest / Show Active: implemented with produced ranked populations.
Row-number vs ranking semantics: partially implemented across shared table renderers.
Section 6.2.1 side-by-side layout: restored as a custom sectioned-table layout.
General bad-URL handling: minimal current behavior implemented; richer policy TBD.
All other items in this review remain open unless called out separately.
```

## 1. Review Purpose

The current `make_site2` layout is broadly solid, but a review of rendered pages
identified a collection of suboptimal visible treatments.

The purpose of this document is to record the proposed change set in product and
design terms, then classify which parts are:

- pure presentation/token changes;
- shared rendering-policy changes;
- Published Artifact model changes;
- Public UI Model or Filter/control changes;
- runtime interaction changes; or
- build-mode/development-vs-production policy changes.

The main risk is making changes that look like CSS tweaks while silently changing
UI ownership, PA semantics or public interaction contracts.
