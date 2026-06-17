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
    hider
    NavigationContent
      site caption
      QuickLinks, if present
      Navigation
  ContentPanel
    Heading
      main heading
      sub heading, if present
    Contents
      FilterSection, if present
      PAPanel
        PA
        Notes
          hider
          NotesContent
```

A conceptual rendered structure may therefore be:

```html
<div class="site-shell">
  <aside class="site-nav">
    <!-- NavigationBar: hider plus NavigationContent realisation -->
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

The NavigationBar content region may be hidden and restored by its modelled
hider. When hidden, the NavigationBar's hider strip remains visible and the
ContentPanel shall occupy the remaining available public-page width without
being pushed below an invisible NavigationBar content region.

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

**Owner:** `NavigationBar -> <hider> . NavigationContent`, where
`NavigationContent -> <site caption> . QuickLinks? . Navigation`

**Rule:** The site caption shall appear as the visible public identity of the
site within the NavigationBar and shall remain distinct from selected Page
headings and PA framing.

The site caption may use site-level emphasis appropriate to public identity, but
its precise typographic ownership and treatment shall be declared deliberately
rather than inferred accidentally from a convenient HTML heading level.

### 6.2 Hider

**Owner:** `NavigationBar -> <hider> . NavigationContent`

**Rule:** The hider shall occupy a thin structural strip within the NavigationBar
and shall be visibly associated with showing or hiding NavigationContent. The
strip remains visible when NavigationContent is hidden and shall provide usable
interaction state and accessible meaning.

Its glyph, size and precise positioning are rendering choices. It shall not
obscure NavigationContent, the ContentPanel or selected Page heading, and it
shall not suggest that the control changes analytical content.

---
