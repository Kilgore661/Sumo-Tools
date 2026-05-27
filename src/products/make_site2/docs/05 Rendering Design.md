# 05 Rendering Design

## Status

Draft rendering-design document for `src/products/make_site2`.

This document defines how the semantic public page and Published Artifacts are
realised as visible browser output. It is downstream of:

```text
01 Requirements.md
02 Specification.md
03 Architecture and Design Thesis.md
04 Model Design.md and its supporting documents
```

The public page grammar `PG` is defined in `02 Specification.md`. This document
does not redefine that grammar. It specifies its visible realisation and the
chosen presentation rules for modelled entities and Published Artifact terminal
forms.

---

## 1. Purpose

Rendering Design has two purposes:

1. to realise the public structure specified by `PG` faithfully; and
2. to state the shared presentation decisions needed to make that structure
   legible, coherent and usable where the grammar does not uniquely determine a
   visual treatment.

The renderer shall produce a coherent public site rather than allow Pages or
Published Artifacts to accumulate unrelated local layout and styling decisions.

The central rendering obligation is:

```text
The rendered public page shall be an auditable realisation of the modelled
public page.
```

---

## 2. Rendering Boundary

Rendering consumes the Public UI Model and Published Artifact Model.

Conceptually:

```text
PublicUIModel + PublishedArtifactModel + applicable public state
  -> Rendered PublicUI
```

The UI Renderer owns visible realisation of the `PG` entities and relationships:

```text
PublicUI
NavigationBar
Navigation
ContentPanel
Heading
Contents
FilterSection
PAPanel
Notes
```

Published Artifact renderers own internal realisation of PA terminal forms and
declared PA-specific visible features:

```text
<table>
<indexed table>
<chart>
<sectioned table>
<prose>
<custom artifact>
```

A PA renderer shall render within the PA position of a `PAPanel`. It shall not
privately redefine the surrounding page grammar, relocate Notes outside their
PAPanel ownership, or create a page-local shell.

---

## 3. Rendering Policy and the Model Boundary

`PG` determines which visible semantic entities exist and the relationships
that rendering must preserve. Some visible requirements follow strongly from
those relationships. For example:

- `NavigationBar` and `ContentPanel` must appear as distinct top-level public
  regions;
- a `FilterSection`, when present, must be distinct from its sibling `PAPanel`;
- `Notes` must appear as belonging to `PAPanel`, not to `FilterSection`;
- a custom PA must remain within the PA position and not replace page-level
  structure.

Other visible choices are not uniquely determined by `PG`. Examples include:

- colour and contrast treatment;
- typography and font weight;
- line height and spacing;
- exact widths or height caps;
- the widget chosen to realise a `FilterItem`;
- table cell padding and row differentiation;
- chart palette and sizing;
- the detailed visible treatment of a declared PA feature.

These are not outside discipline merely because they are not forced by the
grammar. They are rendering policy: chosen visible realisations of identifiable
modelled owners or PA features.

### 3.1 Routes by Which a Visible Fact Is Justified

A visible authored fact shall be justifiable by one of the following routes:

1. **Specified relationship**: it is required by `PG` or another public/model
   relationship.
2. **Declared rendering rule**: it is a shared or PA-specific visible treatment
   declared for an identifiable modelled owner.
3. **Accepted default behaviour**: it is browser or rendering-library default
   behaviour that has been deliberately accepted because it does not create an
   unwanted visible claim.
4. **Recorded exception or provisional state**: it is explicitly identified for
   review rather than silently becoming public design authority.

Rendering shall not introduce visible public structure or semantic emphasis
whose ownership cannot be traced by one of these routes.

### 3.2 Presentation That May Imply Meaning

Some rendering choices are primarily matters of visual tuning. For example, a
small adjustment to an already agreed background colour may change appearance
without changing what the page claims.

Other choices may imply public meaning. Examples include:

```text
bold or prominent text      -> importance or heading status
muted text                   -> lesser relevance, unavailability or secondary status
warning/accent colour        -> exceptional or selected state
grouping and placement       -> ownership or relationship
hiding/showing a feature     -> relevance or public-state consequence
label or symbol choice       -> analytical meaning
```

Where a rendering treatment may convey such meaning, its intended owner and
rationale shall be stated or it shall remain an open/provisional matter rather
than being incorporated as settled design.

### 3.3 Audit Hook for Rendering Rules

Important rendering rules in this document should, where useful, make the
following facts clear:

```text
Owner       the PG entity or PA feature being rendered
Rule        the visible treatment chosen
Scope       where the rule applies and where it does not
Rationale   why the treatment is appropriate
Value status whether exact values are fixed policy or revisable theme/density tokens
```

Not every minor token adjustment requires its own design argument. The purpose
is to expose structure, ownership and semantic presentation decisions, not to
turn harmless tuning into bureaucracy.

`06 Rendering Audit and Changes.md` defines the audit procedure for applying
this discipline and stages pending or provisional rendering decisions before
they are incorporated here.

---

## 4. Rendering Shape of PG

The renderer shall realise the normal promoted public page according to the
following semantic shape:

```text
PublicUI
  NavigationBar
    site caption
    Navigation
    hider
  ContentPanel
    Heading
      main heading
      sub heading, if present
    Contents
      FilterSection, if present
      PAPanel
        PA
        Notes
```

A conceptual rendered structure may therefore be:

```html
<div class="site-shell">
  <aside class="site-nav">
    <!-- NavigationBar: site caption, navigation and hider realisation -->
  </aside>

  <main class="site-main">
    <section class="content-panel">
      <!-- page Heading -->
      <div class="content-body">
        <!-- optional FilterSection -->
        <section class="pa-panel">
          <!-- PA terminal-form rendering -->
          <!-- Notes when visible -->
        </section>
      </div>
    </section>
  </main>
</div>
```

This markup is illustrative rather than a required literal HTML template. The
required fact is the visible and semantic relationship: `FilterSection` is a
sibling of `PAPanel`, and `PA` and `Notes` belong together inside `PAPanel`.
The illustrative `<aside>` and current `.site-nav` CSS name do not define the
model term: the modelled public region is `NavigationBar`.

---

## 5. Rendering `PublicUI`

### 5.1 Top-Level Regions

**Owner:** `PublicUI -> NavigationBar . ContentPanel`

**Rule:** The public UI shall visibly realise one NavigationBar region and one
ContentPanel region as the primary top-level page areas.

**Scope:** Applies to promoted pages rendered through `PG`, including the
selected page shell regardless of PA terminal form.

**Rationale:** Readers need stable navigation context and a stable selected-page
presentation area. The two regions are part of the specified public page, not
page-local rendering conveniences.

### 5.2 NavigationBar Visibility State

The NavigationBar may be hidden and restored by its modelled hider. When hidden,
the ContentPanel shall occupy the available public-page width without being
pushed below an invisible or collapsed NavigationBar.

Hiding the NavigationBar shall not change:

- selected Page;
- Filter state;
- visible PA meaning;
- Notes relevance;
- public analytical state.

NavigationBar collapse is shell presentation state rather than Filter state.

---

## 6. Rendering `NavigationBar`

### 6.1 Site Caption

**Owner:** `NavigationBar -> <site caption> . Navigation . <hider>`

**Rule:** The site caption shall appear as the visible public identity of the
site within the NavigationBar and shall remain distinct from selected Page
headings and PA framing.

The site caption may use site-level emphasis appropriate to public identity, but
its precise typographic ownership and treatment shall be declared deliberately
rather than inferred accidentally from a convenient HTML heading level.

### 6.2 Hider

**Owner:** `NavigationBar -> ... . <hider>`

**Rule:** The hider shall be visibly associated with showing or hiding the
NavigationBar and shall provide usable interaction state and accessible meaning.

Its glyph, size and positioning are rendering choices. They shall not obscure
the ContentPanel or suggest that the control changes analytical content.

---

## 7. Rendering `Navigation`

### 7.1 Hierarchical Numbering

**Owner:** `Navigation -> <hierarchical numbered navigation items>`

**Rule:** Navigation shall display its hierarchy through consistent hierarchical
numbering of navigation items. Grouping nodes and selectable Page destinations
shall preserve their modelled meaning.

Numbering shall arise from the rendered hierarchy or another shared rendering
mechanism; it shall not require public labels to embed ad hoc numbering text.

### 7.2 Navigation-Local Vertical Rhythm

**Owner:** `Navigation`

**Rule:** Navigation items use navigation-local vertical rhythm so successive
labels and nested entries remain legible. This treatment does not determine
content-table density or other PA-terminal spacing.

**Current treatment:**

```css
.nav-list {
  line-height: 1.45;
}
```

**Value status:** The precise line-height is a revisable navigation presentation
value. The shared rule that Navigation may have its own readability treatment is
settled.

### 7.3 Navigation Typography and Status Treatments

Font size, emphasis, selected-state treatment, muted/unavailable-state
treatment and similar Navigation presentation rules shall be declared when they
are intended to carry stable public meaning.

A treatment that merely occurs because of provisional implementation shall not
be treated as settled Navigation policy until recorded here or in a staged
rendering-change decision.

---

## 8. Rendering `ContentPanel` and `Heading`

### 8.1 ContentPanel

**Owner:** `ContentPanel -> Heading . Contents`

**Rule:** The ContentPanel shall visibly present the selected Page's Heading and
its Contents as a coherent page region distinct from the NavigationBar.

The ContentPanel shall not be replaced by a PA-specific page shell. Its Heading
and Contents relationship remains common across PA terminal forms.

### 8.2 Heading Roles

**Owner:** `Heading -> <main heading> . <sub heading>?`

**Rule:** The renderer shall preserve the distinct roles of the main Page
heading and optional sub heading. They shall not be confused with site caption,
PA framing or PA-internal headings.

Typography may be used to convey this hierarchy, but a settled typographic rule
must state whether its owner is the modelled role, the HTML heading hierarchy,
or a declared combination.

### 8.3 Current Typography Issue

A final heading-typography ownership rule is not yet incorporated into this
Rendering Design. Current implementation may contain provisional size rules.
The decision whether typography is governed by role-specific rendering classes,
HTML heading levels, or an explicit combination shall be carried into
`06 Rendering Audit and Changes.md` until agreed.

---

## 9. Rendering `Contents`

### 9.1 Structural Relationship

**Owner:** `Contents -> FilterSection? . PAPanel`

**Rule:** When a FilterSection is present, it shall be visibly separate from the
PAPanel it governs. The PAPanel shall remain identifiable as the region
containing the PA and its Notes.

**Rationale:** Filters change the visible analytical presentation. They do not
own the Published Artifact or the explanatory Notes attached to it.

### 9.2 Layout Freedom Within the Relationship

The grammar does not dictate one exact spatial arrangement for the two sibling
regions. Rendering Design may choose, for example, a side-by-side arrangement
at appropriate widths and a responsive stacked arrangement where needed,
provided that the PAPanel relationship is preserved and Notes are not presented
as belonging to the FilterSection.

Responsive rules shall be declared when they materially affect interpretation or
interaction rather than emerging page-by-page.

---

## 10. Rendering `FilterSection` and `FilterItem`

### 10.1 FilterSection Identity

**Owner:** `FilterSection -> FilterItem*`

**Rule:** A FilterSection shall be presented as a coherent group of
reader-visible controls affecting the associated PAPanel/PA presentation. Its
reader-facing heading may use ordinary wording such as `Options` while the
formal model concept remains `FilterSection`.

### 10.2 Filter Widget Policy

**Owner:** `FilterItem -> BooleanChoice | SingleFiniteChoice`

A `BooleanChoice` may be realised by a checkbox-style control.

A `SingleFiniteChoice` may be realised by a radio-group or selection control
according to shared rendering policy and practical readability. The chosen
widget shall preserve label, allowed values, selected/default state and public
state meaning.

The exact widget-selection threshold or policy shall be recorded when it is
needed as stable shared behaviour.

### 10.3 Structural Lists Do Not Display List Markers

**Owner:** `FilterSection`

**Rule:** Lists used to realise FilterItems or their available choices are
structural groupings rather than reader-facing enumerated/bulleted content. They
shall not display list markers.

**Current treatment:**

```css
.filter-section ul {
  list-style: none;
}
```

Indentation and internal Filter spacing remain rendering-layout decisions and
may be refined separately.

---

## 11. Rendering `PAPanel`

### 11.1 PA-and-Notes Relationship

**Owner:** `PAPanel -> PA . Notes`

**Rule:** PAPanel shall visibly contain the PA and its Notes. When Notes are
visible, their placement shall communicate that they explain or qualify the PA
or visible PA features.

A normal rendering in which Notes span beneath both the sibling FilterSection
and the PA does not conform to this relationship.

### 11.2 PAPanel Layout

The PAPanel may use a layout container appropriate to its PA terminal form and
the available viewport. It shall maintain a place for Notes within the PAPanel
without allowing a specialised PA renderer to take ownership of page-level
layout.

The active runtime constrains each ContentPanel to the available shell height.
Within that space, the PAPanel is a vertical region containing a flexible PA
slot followed by its Notes panel when relevant. The PA slot is the scrollable
artifact region; the surrounding content column shall not require page-level
vertical scrolling for ordinary PA overflow.

### 11.3 Notes-Panel Dimension and Toggle Policy

The shared Notes panel shall be positioned at the bottom of its PAPanel,
visible by default when relevant Notes exist, and hideable by a local
`Hide notes` / `Show notes` control attached to the panel.

The Notes panel shall be visually framed as explanatory material associated
with the PA and constrained to a readable measure. The current shared maximum
width is about `800px`; height is content-driven so the current relevant Notes
are visible without introducing an internal Notes scrollbar.

When no Note is relevant, the renderer need not display an empty Notes panel or
Notes toggle.

---

## 12. Rendering `Notes`

### 12.1 Visibility and Ownership

**Owner:** `Notes -> Note*`, within `PAPanel`

**Rule:** The renderer shall display only Notes relevant to the visible PA and
material visible state. When no Note is relevant, it need not display an empty
Notes container.

Notes shall not appear as help text owned by individual Filters unless a
separate Filter-help concept is modelled and declared. A Filter may alter which
Notes are relevant only through its effect on visible PA state.

### 12.2 Visible Notes Treatment

Notes should be visibly distinguishable from PA data while remaining associated
with the PA they explain. Treatment may include a Notes heading, a panel
boundary, a show/hide control, or other shared presentation rules.

Treatments that mute, highlight or otherwise imply differences in Note status or
importance shall have declared meaning before being treated as normative.

---

## 13. Rendering `PA` Terminal Forms

### 13.1 General PA Rule

**Owner:** `PAPanel -> PA . Notes`

**Rule:** A PA renderer shall render the terminal form and declared PA-visible
features within the PA region of its PAPanel. It may use terminal-form-specific
structure, but shall not render Page headings, global Navigation, sibling
FilterSection layout or Notes outside the PAPanel ownership relationship.

PA framing distinct from Page Heading shall be rendered consistently where it is
modelled.

When a PA terminal form uses a Plotly chart, the chart should resize to fill the
remaining PA slot space after ordinary layout changes, including Notes-panel
show/hide changes, subject to any chart-specific minimum useful size.

---

## 14. Rendering Table-Like PAs

This section applies to `<table>`, `<indexed table>` and table-like portions of
`<sectioned table>` PAs unless an explicit PA-specific rule justifies an
exception.

### 14.1 Shared Table Container

**Owner:** table-like PA terminal forms

**Rule:** Table-like PAs shall use shared table rendering treatment for ordinary
readability decisions rather than page-specific table styling.

Individual PAs may define column meaning, groups, links, optional visible
features and specialised structure. Those meanings do not prevent shared table
legibility treatment from applying where compatible.

### 14.2 Cell Padding

**Owner:** table-like PA terminal forms

**Rule:** Table cells shall use shared internal padding so adjacent values remain
visually distinguishable and rows have modest breathing room.

**Current treatment:**

```css
.artifact-table th,
.artifact-table td {
  padding: 2px 0.25em;
}
```

**Scope:** Applies to shared table-like PA cells. It does not define spacing in
Navigation, Filters, Notes or charts.

**Value status:** Exact padding values are revisable table-density values. The
shared treatment is settled as a table-rendering rule.

### 14.3 Alternating Data-Row Backgrounds

**Owner:** table-like PA terminal forms

**Rule:** Successive data rows shall use alternating background treatment to help
readers track values across table columns and successive rows. The treatment
shall apply to data rows, not heading rows.

**Current treatment:**

```css
:root {
  --artifact-row-odd-bg: #12234b;
  --artifact-row-even-bg: #1b2c52;
}

.artifact-table tbody tr:nth-child(odd) {
  background: var(--artifact-row-odd-bg);
}

.artifact-table tbody tr:nth-child(even) {
  background: var(--artifact-row-even-bg);
}
```

**Value status:** The existence and scope of data-row differentiation are shared
policy. The exact theme colours are revisable presentation tokens and should be
reviewed when alternative site-context themes are normalised.

### 14.4 Continuous Row Treatment

**Owner:** table-like PA terminal forms

**Rule:** Shared data-row background treatment shall read as a continuous row
rather than as separately tinted cells divided by unintended page-background
gutters.

**Current treatment:**

```css
.artifact-table {
  border-collapse: separate;
  border-spacing: 0;
}
```

This is a shared rendering treatment rather than a semantic claim about table
data.

### 14.5 Sticky Table Context

**Owner:** table-like PA terminal forms

**Rule:** When table content overflows the PA slot vertically, the PA title or
caption and table column headings should remain visible at the top of the PA
slot while data rows scroll.

The current runtime realizes this by making the artifact title block, table
section headings and table header cells sticky within the PA slot scroll
container. This is a rendering treatment for reader orientation; it does not
change table data, sorting semantics or PA ownership.

**Known limitation:** The scrollbar currently belongs to the PA slot as a
whole, so it begins at the top of the PA panel rather than below a dedicated
table-body viewport. A deeper table-artifact structure may later split
non-scrolling table chrome from a scrolling data region.

### 14.6 Alignment, Emphasis and Semantic Signals

Column alignment, link styling, font weight, muted text and status colours may
communicate meaning. Where such treatments are common shared table behaviour,
they shall be declared here. Where they express PA-specific meaning, they shall
be declared with that PA or feature.

Browser-default emphasis shall not be retained merely by accident when it
communicates an unintended semantic distinction.

### 14.7 Sortable Heading Treatment

**Owner:** table-like PA terminal forms

**Rule:** A sortable table column heading shall render as an interactive heading
control. The active sorted heading shall show the current sort direction with a
trailing up/down indicator and expose equivalent accessible sort state.

Row-number headings shall not render as sortable controls.

---

## 15. Rendering Indexed-Table PAs

**Owner:** `PA -> <indexed table>`

An indexed-table PA shall render its currently selected table instance within
the PA region and consume relevant Filter/public state declared for selecting
that instance.

The fact that an indexed table loads or selects among payloads is PA-terminal
behaviour. It shall not cause the PA renderer to redefine ContentPanel,
FilterSection or Notes placement.

Where the visible output is table-like, shared table treatments in Section 14
apply unless a declared exception is required.

---

## 16. Rendering Chart PAs

**Owner:** `PA -> <chart>`

A chart PA shall render declared analytical series, axes, labels and relevant
visible features within its PA region.

Chart-library implementation choices, palette, size, legend position and hover
presentation are rendering choices unless a particular feature carries declared
analytical meaning. Chart Notes remain Notes in the PAPanel rather than ad hoc
Filter help or unrelated footer text.

Shared chart presentation rules shall be added as real promoted chart cases
require them and are agreed.

---

## 17. Rendering Sectioned-Table and Prose PAs

### 17.1 Sectioned Tables

**Owner:** `PA -> <sectioned table>`

A sectioned-table PA shall render its modelled sections within the PA region.
Section labels and local table structure are PA-internal visible features.
Shared table treatment applies to its table-like content where compatible.

### 17.2 Prose

**Owner:** `PA -> <prose>`

A prose PA shall render deliberately published narrative or explanatory material
within the PA region. It shall not function as a route for copied arbitrary HTML
that replaces Page Heading, Filters, PAPanel or Notes ownership.

Prose typography and inline structure shall be specified as promoted prose cases
require a settled shared treatment.

---

## 18. Rendering Custom-Artifact PAs

**Owner:** `PA -> <custom artifact>`

A custom-artifact renderer may realise genuine PA-specific analytical structure
where generic terminal rendering cannot express it honestly. It shall remain
within the PA region of `PAPanel`.

Custom PA rendering may declare feature-specific rendering rules where those
features carry public analytical meaning. Such rules shall identify their PA
owner and shall not be disguised as generic site styling.

### 18.1 Banzuke Changes Movement Direction

**Owner:** Banzuke Changes custom PA visible movement features

**Rule:** Banzuke Changes distinguishes direction of movement from magnitude of
movement. In both banzuke-style and scan-style renderings, movement direction is
a visible feature headed `⇅`, displaying `↑` for upward movement, `↓` for
downward movement and no symbol for neutral movement.

The numeric `Delta` feature is separate. Its visibility may be controlled by the
relevant Filter; that Filter does not remove the direction feature.

**Rationale:** Direction is part of the default public reading of banzuke
change, while numeric magnitude is optional further detail.

### 18.2 Banzuke Changes Rank Treatment Not Yet Settled

Whether central rank values in the banzuke-style rendering are semantic row
headers or ordinary table values is not yet incorporated as a settled rendering
rule. The choice affects both markup semantics and whether bold presentation
would communicate intended meaning. It shall be carried as an action item in
`06 Rendering Audit and Changes.md` until resolved.

---

## 19. Theme and Environment Presentation

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

## 20. Browser Defaults, Libraries and Provisional Implementation

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

## 21. Rendering State and Interaction

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

## 22. Relationship to Rendering Audit and Change Record

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

## 23. Rendering Invariants

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

## 24. Summary

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
