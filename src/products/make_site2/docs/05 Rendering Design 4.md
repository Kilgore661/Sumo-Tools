### 19.2 Banzuke Changes Rank Treatment Not Yet Settled

Whether central rank values in the banzuke-style rendering are semantic row
headers or ordinary table values is not yet incorporated as a settled rendering
rule. The choice affects both markup semantics and whether bold presentation
would communicate intended meaning. It shall be carried as an action item in
`06 Rendering Audit and Changes.md` until resolved.

---

## 20. Theme and Environment Presentation

Theme values may provide coherent visual identity and distinguish relevant site
contexts where that distinction is intentionally public or useful for safe
inspection.

Exact colour values generally belong to theme/rendering configuration rather
than to `PG`. A colour rule shall receive greater scrutiny when colour is used
to communicate selection, warning, availability, result meaning or another
semantic status rather than ordinary visual coherence.

Current table-row colours are incorporated above as revisable theme tokens for
the settled shared row-differentiation rule. Broader site-context colour policy
shall be stated once its intended public/preview meaning is settled.

---

## 21. Browser Defaults, Libraries and Provisional Implementation

Browser and rendering-library defaults may supply ordinary presentation where
that default has been deliberately accepted and does not communicate unintended
meaning or violate a specified relationship.

Defaults require review when they create visible claims. Examples include:

- browser-default bold rendering of header cells;
- default list markers on structural Filter lists;
- default cell spacing becoming visible as unintended table gutters;
- default heading sizing being used inconsistently across distinct modelled
  roles.

A provisional implementation treatment may remain in code while a rendering
choice is being evaluated. It shall not become normative merely by existing in
CSS or JavaScript. Pending decisions belong in `06 Rendering Audit and
Changes.md` and are incorporated here only when agreed.

---

## 22. Rendering State and Interaction

The browser runtime may apply public selection and Filter state to determine the
visible Page and PA presentation. It shall preserve the ownership relationships
in `PG` while doing so.

The following distinctions apply:

- NavigationBar Hider state affects shell visibility, not analytical public
  state.
- Filter state affects visible PA presentation and may affect Notes relevance.
- PA-local transient interactions need not become public state merely because
  they are interactive.
- Deep-link/public-state restoration shall be consistent with the Specification
  and runtime design.

A runtime renderer shall not branch into page-local public layouts that are not
represented by the model or declared custom-PA boundaries.

---

## 23. Relationship to Rendering Audit and Change Record

Rendering Design is the normative home for agreed visible presentation policy.
It shall be read together with:

```text
06 Rendering Audit and Changes.md
```

That working document defines how a rendered fact is traced to:

- a specified/modelled owner;
- a declared rendering rule;
- accepted default behaviour;
- or an explicit recorded exception/provisional state.

It also contains:

- proposed rendering rules not yet incorporated here;
- implemented but unsettled presentation choices;
- action items such as heading typography ownership or unresolved semantic
  emphasis;
- migration/regression observations awaiting incorporation or rejection.

A change should move from the change record into this document when its owner,
scope and intended visible rule have been agreed.

---

## 24. Rendering Invariants

A conforming normal rendering of a promoted Page under `PG` shall satisfy:

1. `PublicUI` visibly realises a NavigationBar and a ContentPanel.
2. NavigationBar realises site caption, Navigation and Hider meaning.
3. Hiding NavigationBar does not change analytical Page/Filter/PA meaning.
4. ContentPanel realises Heading and Contents.
5. FilterSection, where present, is visually distinguishable as a sibling of
   PAPanel.
6. PAPanel visibly owns the PA and its relevant Notes.
7. Notes are not laid out as belonging to or spanning the sibling FilterSection.
8. PA renderers remain within the PA region and do not redefine surrounding PG
   structure.
9. Shared terminal-form rendering rules are applied consistently unless an
   explicit PA-specific rule or exception is declared.
10. Significant emphasis, muting, hiding, grouping or labelling has a traceable
    model/PA owner or is explicitly awaiting resolution.

---

## 25. Summary

`PG` defines the semantic public page. The Public UI Model and Published
Artifact Model represent the page and analytical material before rendering.
This Rendering Design specifies how those modelled entities are made visible.

Some rendering facts are strongly constrained by `PG`, such as Notes belonging
inside PAPanel rather than under Filters. Other facts are informed presentation
choices, such as table row treatment or navigation line-height. Those choices
are valid when they are declared against an accountable modelled owner, preserve
specified relationships and avoid accidental semantic claims.

The purpose of this discipline is practical: it prevents a growing public site
from being shaped by unrelated local patches and ensures that its visible
presentation remains coherent, reviewable and justifiable.
