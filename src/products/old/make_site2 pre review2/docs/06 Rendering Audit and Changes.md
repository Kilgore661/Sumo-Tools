# 06 Rendering Audit and Changes

## Status

Draft working document for auditing rendered output against the active
`make_site2` public model and for recording rendering questions or changes that
have not yet been incorporated into `05 Rendering Design.md`.

This document combines two related functions:

1. a stable method for examining visible rendering facts; and
2. a working record of provisional, disputed or newly discovered rendering
   matters.

If the change record eventually becomes large enough to obscure the audit
method, the two functions may later be separated into distinct documents.

---

## 1. Purpose

`05 Rendering Design.md` is the normative home for agreed rendering policy.
This document is its working companion.

It exists to prevent visible implementation details from quietly becoming
public-site design without being understood. In particular, it supports review
of whether a rendered feature:

- realises a relationship specified by `PG`;
- expresses an agreed rendering rule for a modelled owner or PA feature;
- relies acceptably on default behaviour;
- implies unintended meaning;
- reveals a missing or incorrect model relationship;
- or should remain explicitly provisional pending a decision.

The objective is not to require a design debate for every harmless numerical
adjustment. The objective is to catch structural drift and accidental semantic
signals before they accumulate into an incoherent public site.

---

## 2. Relationship to the Active Documentation

The relevant document roles are:

| Document | Role |
| --- | --- |
| `02 Specification.md` | Defines the public contracts and page grammar `PG`. |
| `04.3 Public UI Model.md` | Defines the semantic visible interface that represents `PG`. |
| `04.4 Published Artifact Model.md` | Defines PA-specific analytical meaning and visible feature ownership. |
| `05 Rendering Design.md` | Defines agreed visible realisation and rendering policy. |
| `06 Rendering Audit and Changes.md` | Audits rendered facts and stages unresolved or newly proposed rendering work. |

A settled rendering rule should normally be stated in `05`, not left here
indefinitely. An entry in this document may be removed or reduced to a brief
record after its outcome has been incorporated into the normative design.

---

## 3. What Is Audited

The audit subject is a **visible rendering fact**: something a reader can see or
experience in the rendered public site.

Examples include:

- Sidebar and ContentPanel placement;
- Sidebar hiding/restoration behaviour;
- Navigation hierarchy, numbering and spacing;
- Heading emphasis and hierarchy;
- placement of Filters relative to PAPanel;
- placement, sizing and visibility of Notes;
- PA framing;
- table column visibility, alignment, emphasis, row treatment or links;
- chart traces, labels, legends and annotations;
- PA-specific features such as Banzuke Changes movement direction;
- interaction or state presentation where it materially affects the public
  view.

The audit is primarily concerned with visible facts that are authored,
repeatable or semantically suggestive. It need not record every browser raster
or imperceptible token adjustment.

---

## 4. Audit Method

For each visible rendering fact under review, proceed in order.

### Step 1: State what is visible

Describe the fact in reader-facing terms, without beginning from the CSS or
JavaScript mechanism.

Examples:

```text
Notes appear below both the Options area and the displayed table.

The central Rank values in the Banzuke Changes table are displayed in ordinary
weight.

Successive table data rows have alternating background colours.
```

### Step 2: Identify the owner

Identify the closest semantic owner of the visible fact.

Possible owners include:

- a `PG` entity or relationship, such as `PAPanel -> PA . Notes`;
- a Public UI Model entity, such as `Navigation` or `Heading`;
- a PA terminal form, such as `<table>`;
- a declared PA-specific visible feature, such as Banzuke Changes movement
  direction;
- a theme/runtime context, where the fact genuinely belongs to site-context
  presentation rather than analytical meaning.

If no owner can be identified, the rendering may be an arbitrary patch or a
sign that the model/design is incomplete.

### Step 3: Classify the route of justification

Decide which of the following applies:

1. **Specified relationship**: the fact is required, or prohibited, by `PG` or
   another normative public/model relationship.
2. **Agreed rendering rule**: the fact is a chosen presentation rule stated in
   `05 Rendering Design.md` for the identified owner.
3. **Accepted default behaviour**: the fact is produced by browser or library
   defaults and has been accepted as harmless and consistent with the intended
   public meaning.
4. **Provisional or exceptional behaviour**: the fact exists, but a decision or
   documented exception is still required.
5. **Nonconformance or model gap**: the fact contradicts a specified/modelled
   relationship, or the intended visible meaning has no adequate owner.

### Step 4: Test for implied meaning

Ask whether the visible treatment tells a reader anything beyond ordinary
legibility or theme coherence.

Treatments requiring particular care include:

```text
bold or prominent text      may imply importance or heading status
muted text                   may imply secondary, unavailable or inactive status
warning/accent colour        may imply warning, selection or result meaning
grouping and placement       may imply ownership or association
hiding/showing features      may imply relevance or public-state consequence
icons and symbols            may state analytical meaning
interaction/state persistence may imply a public-view contract
```

Where the treatment implies meaning, verify that the meaning is intended and
owned by the model or PA feature. If it is unintended, the treatment should be
changed even when the code is technically valid.

### Step 5: Decide the outcome

Record one of the following outcomes:

- retain as conforming to `PG` or existing Rendering Design;
- incorporate a settled rendering rule into `05`;
- adjust implementation to comply with a settled rule;
- accept a harmless default explicitly;
- retain as provisional pending a named decision;
- identify a specification/model gap;
- reject as unowned or misleading presentation.

---

## 5. Significance Classification

Not all rendering findings carry the same weight. Use the following categories
to avoid both arbitrary patching and needless bureaucracy.

### 5.1 Structural Nonconformance

A visible relationship contradicts `PG` or another public/model relationship.

Examples:

- Notes visibly span both `FilterSection` and `PAPanel` even though Notes belong
  within `PAPanel`;
- collapsing Sidebar causes ContentPanel to render below it rather than
  occupying the available top-level page region;
- a custom PA renders its own competing Page heading or shell.

Structural nonconformance requires correction or an explicit specification/model
change. It is not ordinary styling work.

### 5.2 Semantic-Presentation Concern

A visual treatment may convey analytical, structural or status meaning that has
not been justified.

Examples:

- bold Rank values implying an importance distinction;
- muted Navigation labels implying unavailability without a corresponding
  status;
- colour used to suggest a result, warning or selected state without declared
  meaning;
- an optional feature displayed or hidden inconsistently with its Filter rule.

These matters require a deliberate decision and an accountable owner.

### 5.3 Shared Readability or Usability Policy

A shared presentation treatment improves legibility or interaction without
normally altering analytical meaning.

Examples:

- table cell padding;
- alternating data-row backgrounds;
- Navigation line height;
- a shared Notes-panel overflow policy;
- removal of unintended cell-spacing gutters.

These decisions should be recorded in `05` with owner, scope and rationale once
agreed. Exact token values may remain adjustable.

### 5.4 Theme or Token Tuning

An existing agreed treatment is refined without changing its semantic or
structural function.

Examples:

- choosing a nearby shade for an already-agreed alternating table-row token;
- fine-tuning a spacing value within an already agreed shared spacing policy.

Such changes generally do not require a new model decision. They require review
only where legibility, contrast, accessibility or implied meaning may materially
change.

### 5.5 Accepted Default Behaviour

Browser or library behaviour is visible but harmless and deliberately left in
place.

A default should be challenged when it creates an unwanted signal or violates
an agreed relationship. Examples already encountered include browser-default
list markers, cell gaps and bold table-header presentation.

---

## 6. Recording a Proposed or Observed Change

An unresolved or newly proposed rendering matter should be recorded using this
compact structure:

```md
### <Issue or change title>

Status:
Proposed | Implemented provisionally | Open decision | Nonconformance |
Resolved and incorporated in 05 | Rejected

Visible fact:
<What a reader sees or would see.>

Owner:
<PG entity/relationship, Public UI entity, PA terminal or PA-specific feature.>

Classification:
<Structural nonconformance | Semantic-presentation concern |
Shared readability policy | Theme/token tuning | Accepted default>

Treatment or question:
<Proposed/implemented treatment, or decision that remains to be made.>

Rationale:
<Why this is appropriate or why it requires review.>

Destination:
<Where it belongs in 05 if/when agreed, or which model/specification document
requires amendment.>
```

For very small token adjustments within an already-settled policy, a full entry
is not required unless the adjustment raises a new concern.

---

## 7. Current Open Rendering Decisions

### 7.1 Heading Typography Ownership

**Status:** Open decision; implementation currently provisional.

**Visible fact:** The current implementation applies typography partly by a
role-specific site-title selector and partly through generic HTML heading-level
selectors.

**Owner:** `Sidebar -> <site caption>` and `Heading -> <main heading> . <sub heading>?`.

**Classification:** Semantic-presentation concern.

**Current provisional implementation:**

```css
.site-title {
  font-size: 24px;
}

h2 {
  font-size: 20px;
}

h3 {
  font-size: 18px;
}
```

**Decision required:** Choose whether intentional heading typography is owned
by:

1. HTML heading hierarchy;
2. modelled rendered roles such as site caption, Page main heading and Page sub
   heading; or
3. an explicit combination, with a documented boundary between general heading
   structure and role-specific treatment.

**Rationale:** Size and prominence communicate heading hierarchy and role. An
inconsistent ownership policy makes it difficult to tell whether visible
emphasis is intentional or merely a side effect of convenient markup.

**Destination:** `05 Rendering Design.md`, Sections 6 and 8, once resolved.

### 7.2 Banzuke Changes Rank-Cell Semantics and Weight

**Status:** Open decision; current implementation avoids boldness but requires
semantic review.

**Visible fact:** The central Rank values in banzuke-style Banzuke Changes rows
are currently shown at ordinary data-cell weight.

**Owner:** Banzuke Changes custom PA, rank-position feature.

**Classification:** Semantic-presentation concern.

**Current implementation concern:** The implementation changed Rank values from
row-header cells to ordinary data cells while retaining `scope="row"`. A
`scope` attribute does not give an ordinary `<td>` row-header semantics.

**Decision required:** Choose whether the central Rank value is:

1. a semantic row header, rendered as `<th scope="row">` with ordinary-weight
   visual treatment where bold emphasis is not intended; or
2. an ordinary data value, rendered as `<td>` without `scope`.

**Rationale:** Using row-header markup is a structural/accessibility decision;
using bold is a visible emphasis decision. They should not be conflated through
browser defaults.

**Destination:** `05 Rendering Design.md`, Banzuke Changes rendering subsection,
and implementation once resolved.

### 7.3 Notes-Panel Layout and Dimension Policy

**Status:** Open rendering decision following identified structural
nonconformance.

**Visible fact:** The desired rendering is for Notes, where present, to form a
panel associated with the PA rather than spanning beneath both Filters and PA.
A candidate maximum Notes-panel height of `170px` has been discussed.

**Owner:** `PAPanel -> PA . Notes`.

**Classification:** Two parts:

- Notes ownership/placement is a structural conformance matter already settled
  by `PG` and `05`: Notes must be within PAPanel rather than under the sibling
  FilterSection.
- The exact panel layout, maximum height and overflow handling are shared
  readability/usability policy still to be agreed.

**Decision required:** Implement the structural correction and decide the shared
Notes-panel visual rule, including whether Notes appear below the PA, whether a
`170px` maximum is appropriate, and how overflow is handled.

**Rationale:** Placement conveys ownership; the height cap is a usability choice
intended to preserve space for the PA while keeping explanatory material
available.

**Destination:** `05 Rendering Design.md`, Sections 11 and 12, once the exact
panel treatment is agreed; implementation correction required for existing
layout.

---

## 8. Rendering Rules Already Incorporated into `05`

The following matters arose during implementation review and have already been
incorporated as agreed rendering rules in `05 Rendering Design.md`. They are
listed here only to maintain continuity with earlier working notes.

### 8.1 Navigation-Local Vertical Rhythm

**Owner:** `Navigation`.

**Rule incorporated in 05:** Navigation uses navigation-local vertical rhythm;
current treatment is `.nav-list { line-height: 1.45; }`, with the exact value
revisable.

### 8.2 Filter Structural Lists Without Markers

**Owner:** `FilterSection`.

**Rule incorporated in 05:** Lists used to realise Filter controls or choices do
not display list markers.

### 8.3 Shared Table Cell Padding

**Owner:** Table-like PA terminal forms.

**Rule incorporated in 05:** Shared internal cell padding separates adjacent
values and gives rows modest breathing room; current treatment is
`padding: 2px 0.25em`.

### 8.4 Alternating Data-Row Backgrounds

**Owner:** Table-like PA terminal forms.

**Rule incorporated in 05:** Successive `tbody` rows receive alternating
background treatment; exact theme colours remain revisable tokens.

### 8.5 Continuous Table Row Background Treatment

**Owner:** Table-like PA terminal forms.

**Rule incorporated in 05:** Unintended cell gaps are suppressed so row
background treatment reads as continuous; current treatment uses collapsed
borders.

### 8.6 Banzuke Changes Movement Direction

**Owner:** Banzuke Changes custom PA visible movement feature.

**Rule incorporated in 05:** The `⇅` movement-direction feature is visible in
both banzuke-style and scan-style presentations independently of the optional
numeric `Delta` feature.

---

## 9. Known Structural Finding Requiring Implementation Work

### Notes Placement in Current `make_site2` Rendering

**Status:** Identified nonconformance; design relationship settled, implementation
correction not yet recorded as completed.

**Visible fact:** In the current rendering structure, Notes are emitted after the
combined content body containing both the FilterSection and PA slot. Visually,
Notes therefore span beneath both regions when Filters are present.

**Owner:** `Contents -> FilterSection? . PAPanel` and
`PAPanel -> PA . Notes`.

**Classification:** Structural nonconformance.

**Required correction:** Render Notes within a PAPanel containing the PA,
separate from the sibling FilterSection. Exact panel sizing and scrolling policy
remains the open decision recorded in Section 7.3.

**Rationale:** This is not merely a preference for a prettier layout. Placement
currently misstates the specified ownership relationship between Notes, PA and
Filters.

**Destination:** Implementation change guided by `05 Rendering Design.md`,
Sections 9, 11 and 12.

---

## 10. Audit Checklist for Future Rendering Work

When evaluating a rendering change or a newly promoted Page/PA, use this short
checklist:

1. What reader-visible fact is being introduced or altered?
2. What `PG` entity, UI-model entity, PA terminal or PA-specific feature owns
   it?
3. Does it preserve the relationships specified by `PG`?
4. Is it already governed by an agreed rule in `05`?
5. Does it imply meaning through emphasis, muting, colour, grouping, placement,
   hiding/showing, labels or symbols?
6. If it is only token tuning, does it remain within an agreed treatment without
   materially affecting readability or implied meaning?
7. If it is unsettled, is it recorded here rather than left as silent
   implementation policy?
8. Once settled, has the rule been incorporated into `05` and the implementation
   brought into conformity?

---

## 11. Summary

Rendering audit exists to keep the visible public site aligned with the model
and with agreed presentation policy as implementation and Published Artifacts
grow.

The audit is strict where visible structure or implied meaning is at stake, and
lightweight where an agreed presentation rule is merely being tuned. Its core
question is always:

```text
What does this visible fact say to the reader, and where is that claim owned?
```

The open issues currently requiring further decision or implementation are:

- ownership of heading typography;
- semantic/visual treatment of Banzuke Changes Rank values;
- correction and final shared treatment of Notes within PAPanel.

Once those matters are settled, their normative rendering rules belong in
`05 Rendering Design.md`.