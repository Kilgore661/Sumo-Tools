# 06 Rendering Audit and Changes

## Status

Working document for auditing rendered output against the active `make_site2`
public model and recording rendering questions or changes that have not yet been
incorporated into `05 Rendering Design.md`.

This document has two functions:

1. define a repeatable method for examining visible rendering facts; and
2. record implemented corrections and unresolved rendering choices.

`05 Rendering Design.md` remains the normative home for agreed rendering policy.

---

## 1. Purpose

Rendering must not quietly change the structure or meaning of the public site.
This document exists to test whether a visible treatment:

- realises a relationship specified by `PG`;
- expresses an agreed rendering rule for a modelled owner or PA feature;
- relies acceptably on default browser/library behaviour;
- implies unintended meaning;
- reveals a missing or incorrect model relationship; or
- should remain explicitly provisional pending a decision.

Small token adjustments within an agreed treatment need not become design
debates. Structural drift and accidental semantic signals do need to be caught.

---

## 2. Relationship to the Active Documentation

| Document | Role |
| --- | --- |
| `02 Specification.md` | Defines the public contracts and page grammar `PG`. |
| `04.3 Public UI Model.md` | Defines the semantic visible interface representing `PG`. |
| `04.4 Published Artifact Model.md` | Defines PA-specific meaning and visible feature ownership. |
| `05 Rendering Design.md` | Defines agreed visible realisation and rendering policy. |
| `06 Rendering Audit and Changes.md` | Audits rendered facts and stages unresolved or newly implemented work. |

A settled rule should normally be incorporated into `05`. A completed
implementation correction may remain here as a compact audit record.

---

## 3. What Is Audited

The audit subject is a **visible rendering fact**: something a reader can see or
experience in the rendered public site.

Examples include:

- NavigationBar and ContentPanel placement;
- NavigationBar hiding/restoration behaviour;
- Navigation hierarchy, numbering and spacing;
- Heading emphasis and hierarchy;
- placement of Filters relative to PAPanel;
- placement, sizing and visibility of Notes;
- table alignment, emphasis, row treatment and links;
- chart traces, labels, legends and annotations;
- PA-specific features such as Banzuke Changes movement direction;
- interaction/state presentation where it materially affects the public view.

---

## 4. Audit Method

For each visible fact under review:

1. **State what is visible** in reader-facing terms.
2. **Identify its owner**: a `PG` relationship, Public UI entity, PA terminal,
   PA-specific feature or genuine site/runtime context.
3. **Classify its justification** as specified relationship, agreed rendering
   rule, accepted default, provisional behaviour, or nonconformance/model gap.
4. **Test implied meaning**: emphasis, colour, grouping, placement, symbols,
   hiding/showing and persistent state may tell the reader more than intended.
5. **Record the outcome**: retain, incorporate into `05`, correct the
   implementation, accept a default explicitly, defer a named decision, or
   identify a specification/model gap.

---

## 5. Significance Classification

### 5.1 Structural Nonconformance

A visible relationship contradicts `PG` or another public/model relationship.
It requires correction or explicit model/specification change.

Example: Notes visibly spanning both `FilterSection` and the PA although the
specified owner is `PAPanel -> PA . Notes`.

### 5.2 Semantic-Presentation Concern

A treatment may convey analytical, structural or status meaning that has not
been justified, for example bold Rank values or status-like colour.

### 5.3 Shared Readability or Usability Policy

A shared treatment improves legibility or interaction without normally changing
analytical meaning, for example table padding, alternating row backgrounds or a
shared Notes overflow policy.

### 5.4 Theme or Token Tuning

An agreed treatment is adjusted without changing its structural or semantic
function, for example choosing a nearby shade for alternating rows.

### 5.5 Accepted Default Behaviour

Browser or library behaviour is visible but harmless and deliberately left in
place. Defaults must be challenged where they create an unwanted signal or
violate an agreed relationship.

---

## 6. Recording Template

Use the following compact form for unresolved or newly implemented rendering
matters:

```md
### <Issue or change title>

Status:
Proposed | Implemented and verified | Open decision | Nonconformance |
Resolved and incorporated in 05 | Rejected

Visible fact:
<What a reader sees or would see.>

Owner:
<PG entity/relationship, Public UI entity, PA terminal or PA-specific feature.>

Classification:
<Structural nonconformance | Semantic-presentation concern |
Shared readability policy | Theme/token tuning | Accepted default>

Treatment or question:
<Implemented treatment or remaining decision.>

Rationale:
<Why the treatment is appropriate or why review is required.>

Destination:
<Where the settled rule belongs or which model/specification document requires
amendment.>
```

---

## 7. Implemented and Verified Corrections

### 7.1 Notes Are Now Rendered Within `PAPanel`

**Status:** Implemented and locally verified, May 2026.

**Visible fact:** When Notes are present, they now appear beneath the PA inside
the PA-owned region; on pages with Filters they no longer span beneath the
sibling FilterSection.

**Owner:**

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

**Classification:** Correction of a structural nonconformance.

**Implementation record:**

- `ui_model.py` now represents `Contents`, `PAPanel` and `Notes` directly;
- Pages without Filters use an absent `FilterSection`, not an empty visual
  region;
- runtime manifest construction now builds `PAPanel` explicitly;
- the modular runtime renders Notes inside `.pa-panel` and honours the Note ids
  owned by that PAPanel;
- `.pa-panel` has only the minimal structural layout required for the PA and its
  Notes to stack within the PA column;
- the temporary `G1Contents`/`grammar="G1"` compatibility seam has been removed.

**Audit result:** The user rebuilt/deployed and confirmed the corrected result
works in the local inspection environment. The structural issue is therefore no
longer open.

**Remaining separate question:** Notes-panel visual/dimension policy remains
open under Section 8.3; the correction does not settle a maximum height,
scrolling or additional framing.

---

## 8. Current Open Rendering Decisions

### 8.1 Heading Typography Ownership

**Status:** Open decision; implementation currently provisional.

**Visible fact:** Typography is applied partly by a role-specific `.site-title`
selector and partly through generic `h2`/`h3` selectors.

**Owner:** `NavigationBar -> <site caption>` and
`Heading -> <main heading> . <sub heading>?`.

**Classification:** Semantic-presentation concern.

**Current provisional implementation:**

```css
.site-title { font-size: 24px; }
h2 { font-size: 20px; }
h3 { font-size: 18px; }
```

**Decision required:** Choose whether intentional heading typography is owned by
HTML hierarchy, modelled rendered roles, or an explicit documented combination.

**Destination:** `05 Rendering Design.md`, once resolved.

### 8.2 Banzuke Changes Rank-Cell Semantics and Weight

**Status:** Open decision; the visible weight no longer settles the semantic
question.

**Visible fact:** Central Rank values in banzuke-style Banzuke Changes rows are
shown at ordinary data-cell weight.

**Owner:** Banzuke Changes custom PA, rank-position feature.

**Classification:** Semantic-presentation concern.

**Decision required:** Choose whether the central Rank value is:

1. a semantic row header, rendered as `<th scope="row">` with explicit
   ordinary-weight styling if bold emphasis is not intended; or
2. an ordinary data value, rendered as `<td>` without `scope`.

**Rationale:** Markup semantics/accessibility and visible emphasis are separate
choices and should not be conflated through browser defaults.

**Destination:** `04.4 Published Artifact Model.md` if semantic clarification is
needed and `05 Rendering Design.md` for its visible realisation.

### 8.3 Notes-Panel Visual and Dimension Policy

**Status:** Implemented shared rendering decision.

**Visible fact:** Notes belong visibly to the PA region and appear in a framed
bottom panel within `PAPanel` when relevant. The panel is visible by default,
uses a local `Hide notes` / `Show notes` control, and is constrained to a
readable width of about `800px`.

**Owner:** `PAPanel -> PA . Notes`.

**Classification:** Shared readability/usability policy.

**Decision recorded:** Notes are content-height by default rather than capped at
the earlier discussed `170px`. If no Note is currently relevant, no empty Notes
panel or toggle is rendered. Showing or hiding Notes changes the available PA
slot space; Plotly charts are resized after the toggle.

**Rationale:** Ownership is already correctly communicated by placement. Height,
overflow and framing govern usability and use of screen space.

**Destination:** Incorporated into `05 Rendering Design.md`.

### 8.3.1 Table-Body Scrollbar Boundary

**Status:** Deferred model/rendering refinement discovered during Notes-panel
implementation.

**Visible fact:** The current runtime keeps PA titles and table headings sticky
inside the PA slot, but the scrollbar still belongs to the whole PA slot rather
than a distinct table-data body viewport. This means the scrollbar begins at
the top of the PA panel rather than below the table headings.

**Owner:** Table-like PA terminal structure inside `PAPanel -> PA`.

**Classification:** Rendering-grammar / PA-structure refinement.

**Decision required:** Decide whether table-like PAs should expose explicit
non-scrolling table chrome and a separate scrolling data region in the model or
runtime grammar.

**Destination:** Deferred in `10 Open Issues and Deferred Design.md`; if
accepted, incorporate into `04.4 Published Artifact Model.md` and `05 Rendering
Design.md`.

### 8.4 Site-Context Colour Treatment

**Status:** Implemented provisionally; decision not yet recorded in normative
Rendering Design.

**Visible fact:** Local, remote and preview runtime contexts use different page
background colours.

**Owner:** Site/runtime context presentation, not analytical PA meaning.

**Classification:** Semantic-presentation concern or accepted operational cue,
pending decision.

**Decision required:** Accept, revise or remove this treatment deliberately and
record its intended message to users/reviewers.

---

## 9. Rendering Rules Already Incorporated into `05`

The following agreed rules remain implemented and are listed here for continuity:

| Owner | Incorporated rule |
| --- | --- |
| `Navigation` | Navigation-local vertical rhythm; current `.nav-list { line-height: 1.45; }`. |
| `FilterSection` | Structural Filter lists display without list markers. |
| Table-like PAs | Shared cell padding; current `padding: 2px 0.25em`. |
| Table-like PAs | Alternating `tbody` row background treatment. |
| Table-like PAs | Continuous row colouring through suppression of unintended cell gaps. |
| Table-like PAs | Sticky PA title/caption and table headings inside the PA slot. |
| `PAPanel -> PA . Notes` | Bottom Notes panel, visible by default when relevant, with local show/hide control. |
| Banzuke Changes PA | Visible `⇅` movement direction in both banzuke-style and scan-style views independently of optional numeric `Delta`. |

---

## 10. Audit Checklist for Future Work

When evaluating a rendering change or newly promoted Page/PA:

1. What reader-visible fact is introduced or altered?
2. What `PG` entity, UI-model entity, PA terminal or PA-specific feature owns
   it?
3. Does it preserve `PG` relationships?
4. Is it already governed by an agreed rule in `05`?
5. Does it imply meaning through emphasis, muting, colour, grouping, placement,
   hiding/showing, labels or symbols?
6. If it is token tuning, does it remain within an agreed treatment?
7. If unsettled, has it been recorded here rather than left as silent policy?
8. Once settled, has it been incorporated into `05` and implemented/audited?

---

## 11. Summary

The first structural audit finding has now been corrected: Notes are modelled
and rendered within `PAPanel`, rather than spanning beneath Filters and PA.

The current open rendering choices are:

- ownership of heading typography;
- semantic/visual treatment of Banzuke Changes Rank values;
- table-body-only scrolling for table-like PAs; and
- deliberate acceptance or rejection of context-colour presentation.

The audit remains strict where visible structure or implied meaning is at stake,
and lightweight where an already agreed treatment is merely being tuned.
