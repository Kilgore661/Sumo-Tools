## 7. Rendering `QuickLinks`

### 7.1 QuickLinks Placement

**Owner:** `NavigationContent -> <site caption> . QuickLinks? . Navigation`

**Rule:** When QuickLinks are present, they shall render in the NavigationBar
after the site caption and before the full Navigation tree.

The current shared treatment is a simple ordered list with the caption
`Quick Links`. QuickLinks shall not use the hierarchical numbering of the main
Navigation tree and shall not require public labels to embed ad hoc numbering
text.

---

## 8. Rendering `Navigation`

### 8.1 Hierarchical Numbering

**Owner:** `Navigation -> <hierarchical numbered navigation items>`

**Rule:** Navigation shall display its hierarchy through consistent hierarchical
numbering of navigation items. Grouping nodes and selectable Page destinations
shall preserve their modelled meaning.

Numbering shall arise from the rendered hierarchy or another shared rendering
mechanism; it shall not require public labels to embed ad hoc numbering text.

The Home Navigation node may be rendered as a link to the shell landing view
even though the landing view is not currently a declared material Page. Such a
link is a shell entry point and shall not be treated as a Page-selection link.

### 8.2 Link Decoration

**Owner:** Site-wide public link presentation.

**Rule:** Links shall not be underlined by default, but shall be underlined when
hovered or keyboard-focused. A Page or PA may still use other declared visual
treatments to distinguish links, active Navigation items or unavailable
destinations.

This rule applies site-wide rather than being owned separately by Navigation,
QuickLinks or individual PA renderers.

### 8.3 Navigation-Local Vertical Rhythm

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

### 8.4 Navigation Typography and Status Treatments

Font size, emphasis, selected-state treatment, muted/unavailable-state
treatment and similar Navigation presentation rules shall be declared when they
are intended to carry stable public meaning.

Navigation placeholders, meaning Navigation nodes that group child entries but
are not themselves links, shall be visually muted. The current treatment renders
their labels at about 50% foreground opacity so linked destinations remain the
stronger navigational affordance.

A treatment that merely occurs because of provisional implementation shall not
be treated as settled Navigation policy until recorded here or in a staged
rendering-change decision.

---

## 9. Rendering `ContentPanel` and `Heading`

### 9.1 ContentPanel

**Owner:** `ContentPanel -> Heading . Contents`

**Rule:** The ContentPanel shall visibly present the selected Page's Heading and
its Contents as a coherent page region distinct from the NavigationBar.

The ContentPanel shall not be replaced by a PA-specific page shell. Its Heading
and Contents relationship remains common across PA terminal forms.

### 9.2 Heading Roles

**Owner:** `Heading -> <main heading> . <sub heading>?`

**Rule:** The renderer shall preserve the distinct roles of the main Page
heading and optional sub heading. They shall not be confused with site caption,
PA framing or PA-internal headings.

Typography may be used to convey this hierarchy, but a settled typographic rule
must state whether its owner is the modelled role, the HTML heading hierarchy,
or a declared combination.

Page sub headings may contain trusted inline HTML declared by the Site
Definition, such as links. The shared renderer shall render that declared inline
markup rather than displaying it as escaped text. This is a site-definition
authoring contract, not permission for producer data or arbitrary copied HTML to
replace page structure.

The site caption and selected Page main heading shall have modest top spacing
so they do not sit directly against the viewport edge.

### 9.3 Caption Typography and Spacing

**Status:** Provisional implementation rule under review.

**Rule:** HTML heading levels used for page and PA captions express the visible
hierarchy of captions. They are not requests for browser-default heading
styling.

The current hierarchy is:

- `h2`: ContentPanel main caption
- `h3`: ContentPanel sub-caption
- `h4`: PAPanel/PA main caption
- `h5`: PAPanel/PA sub-caption

All headings at the same level should share the same base visual treatment.
Named selectors such as `content-title`, `content-summary`,
`artifact-title-block` or PA-specific ids are role hooks and exception points;
they should not become the normal source of unrelated typography.

Caption text itself shall not create leading vertical space. Space above a
caption belongs to the container that owns the edge above it, for example the
ContentPanel top inset or PA slot headroom below a dividing rule.

Each caption/sub-caption shall create proportional trailing space before the
next caption level or content. The current trial uses approximately half the
caption text height as the following gap:

- after `h2`: `0.625rem`
- after `h3`: `0.5625rem`
- after `h4`: `0.5rem`
- after `h5`: `0.4375rem`

The boundary line below the ContentPanel caption belongs to the content/body
boundary, not to the optional `h3`; pages with and without sub-captions should
therefore receive the same structural separation.

---

## 10. Rendering `Contents`

### 10.1 Structural Relationship

**Owner:** `Contents -> FilterSection? . PAPanel`

**Rule:** When a FilterSection is present, it shall be visibly separate from the
PAPanel it governs. The PAPanel shall remain identifiable as the region
containing the PA and its Notes.

**Rationale:** Filters change the visible analytical presentation. They do not
own the Published Artifact or the explanatory Notes attached to it.

### 10.2 Layout Freedom Within the Relationship

The grammar does not dictate one exact spatial arrangement for the two sibling
regions. Rendering Design may choose, for example, a side-by-side arrangement
at appropriate widths and a responsive stacked arrangement where needed,
provided that the PAPanel relationship is preserved and Notes are not presented
as belonging to the FilterSection.

Responsive rules shall be declared when they materially affect interpretation or
interaction rather than emerging page-by-page.

---

## 11. Rendering `FilterSection` and `FilterItem`

### 11.1 FilterSection Identity

**Owner:** `FilterSection -> FilterItem*`

**Rule:** A FilterSection shall be presented as a coherent group of
reader-visible controls affecting the associated PAPanel/PA presentation. Its
reader-facing heading may use ordinary wording such as `Options` while the
formal model concept remains `FilterSection`.

### 11.2 Filter Widget Policy

**Owner:** `FilterItem -> BooleanChoice | SingleFiniteChoice`

A `BooleanChoice` may be realised by a checkbox-style control.

A `SingleFiniteChoice` may be realised by a radio-group or selection control
according to shared rendering policy and practical readability. The chosen
widget shall preserve label, allowed values, selected/default state and public
state meaning.

The exact widget-selection threshold or policy shall be recorded when it is
needed as stable shared behaviour.

### 11.3 Structural Lists Do Not Display List Markers

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

## 12. Rendering `PAPanel`

### 12.1 PA-and-Notes Relationship

**Owner:** `PAPanel -> PA . Notes`

**Rule:** PAPanel shall visibly contain the PA and its Notes. When Notes are
visible, their placement shall communicate that they explain or qualify the PA
or visible PA features.

A normal rendering in which Notes span beneath both the sibling FilterSection
and the PA does not conform to this relationship.

### 12.2 PAPanel Layout

The PAPanel may use a layout container appropriate to its PA terminal form and
the available viewport. It shall maintain a place for Notes within the PAPanel
without allowing a specialised PA renderer to take ownership of page-level
layout.

The active runtime constrains each ContentPanel to the available shell height.
Within that space, the PAPanel is a vertical region containing a flexible PA
slot followed by its Notes panel when relevant. The PA slot is the scrollable
artifact region; the surrounding content column shall not require page-level
vertical scrolling for ordinary PA overflow.

The PA slot owns a small top inset so PA captions do not sit directly against
the ContentPanel/body boundary line. PA captions should not carry their own
leading whitespace to solve that container-edge problem.

### 12.3 Notes-Panel Dimension and Toggle Policy

The shared Notes panel shall be positioned at the bottom of its PAPanel,
visible by default when relevant Notes exist, and hideable by a local structural
Hider strip. The Hider strip remains visible when NotesContent is hidden so the
reader can restore the Notes.

The Notes panel shall be visually framed as explanatory material associated
with the PA and constrained to a readable measure. The current shared maximum
width is about `800px`; height is content-driven so the current relevant Notes
are visible without introducing an internal Notes scrollbar.

For the current simple treatment, chevron-like text glyphs may be used: a
downward glyph when NotesContent is visible and an upward glyph when it is
hidden.

NotesContent visibility is a shell/UI preference rather than material PA state.
The runtime may persist it across Page changes so a reader who hides Notes does
not have them reappear merely because a new Navigation item was selected.

When no Note is relevant, the renderer need not display an empty Notes panel or
Notes toggle.

---

## 13. Rendering `Notes`

### 13.1 Visibility and Ownership

**Owner:** `Notes -> <hider> . NotesContent`, within `PAPanel`

**Rule:** The renderer shall display only Notes relevant to the visible PA and
material visible state. When no Note is relevant, it need not display an empty
Notes container.

Notes shall not appear as help text owned by individual Filters unless a
separate Filter-help concept is modelled and declared. A Filter may alter which
Notes are relevant only through its effect on visible PA state.

### 13.2 Visible Notes Treatment

Notes should be visibly distinguishable from PA data while remaining associated
with the PA they explain. Treatment may include a Notes heading, a panel
boundary, a show/hide control, or other shared presentation rules.

Treatments that mute, highlight or otherwise imply differences in Note status or
importance shall have declared meaning before being treated as normative.
