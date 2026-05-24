# 04 Model Design

## Status

Draft model-design overview for `src/products/make_site2`.

This document identifies the model layers required by the specification and the
architecture. It is intentionally short. Detailed model definitions belong in
the supporting model documents listed below.

---

## 1. Role of the Model Layer

The model layer represents the public publication before it is rendered.

It exists between public declarations and visible output:

```text
Site Definition
  -> Publication Plan
  -> UI Model and Published Artifact Model
  -> Rendering
```

The model layer shall represent meaning and structure needed by the public site.
It shall not be an inventory of HTML elements, CSS selectors, JavaScript
functions or written output files.

The central obligation is that a promoted public page shall be representable as
the public structure specified by `PG` before it is rendered.

---

## 2. Model Documents

The active model design shall be divided as follows:

```text
04.1 Site Definition Model.md
04.2 Publication Plan Model.md
04.3 Public UI Model.md
04.4 Published Artifact Model.md
```

Each document owns a distinct question:

| Document | Question answered |
| --- | --- |
| `04.1 Site Definition Model.md` | What public site is intended? |
| `04.2 Publication Plan Model.md` | What will this build publish, and what does it require? |
| `04.3 Public UI Model.md` | What semantic public interface conforming to `PG` will be rendered? |
| `04.4 Published Artifact Model.md` | What deliberately published analytical object occupies the PA position? |

The documents may specify concepts without requiring that each concept become a
separate Python class.

---

## 3. Site Definition Model

The Site Definition Model declares public intent.

It shall identify, as applicable:

- the site identity and public caption;
- the intended Navigation tree;
- the Page registry;
- Page public statuses;
- declared public assets and site-facing input references;
- site-level defaults required to construct a publication plan.

The Site Definition Model shall not render the site, calculate analytical
outputs, or infer public structure from producer output directories.

---

## 4. Publication Plan Model

The Publication Plan Model resolves public intent for a particular build.

It shall identify, as applicable:

- the Pages included in the build;
- their public status treatment;
- their stable public selection/deep-link references;
- required site-facing inputs, data and assets;
- build-selected defaults or instances;
- pre-render consistency failures and exclusions.

The Publication Plan Model determines what is to be published in this build. It
shall not determine visible page layout or HTML rendering.

---

## 5. Public UI Model

The Public UI Model represents the semantic interface that the renderer shall
realise.

For promoted pages in the initial supported public shape, it shall represent
`PG`:

```text
PublicUI -> Sidebar . ContentPanel
Sidebar -> <site caption> . Navigation . <hider>
ContentPanel -> Heading . Contents
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
Notes -> Note*
```

It shall therefore represent, as applicable:

- the visible Sidebar and ContentPanel relationship;
- site caption, Navigation and hider state/meaning;
- selected-page Heading;
- FilterSection and FilterItems;
- PAPanel;
- the PA placed in that panel;
- Note ownership and visibility relevance.

The Public UI Model owns semantic interface structure. It shall not own detailed
table internals, chart construction, styling values, HTML tag choices or build
output writing.

---

## 6. Published Artifact Model

The Published Artifact Model represents deliberately published analytical
material placed at `PA` in `PG`.

It shall represent, as required by each PA terminal form:

- stable PA identity;
- PA terminal form;
- public framing or labels where applicable;
- site-facing data and artefact inputs;
- meaningful visible features such as columns, groups, traces or views;
- Filter relationships consumed by the PA;
- Note, caveat and provenance ownership;
- public consistency requirements.

It may support specialised artefact structure and rendering. It shall not
redefine the surrounding `PG` structure.

---

## 7. Boundaries and Invariants

The following invariants govern the model layer:

1. A promoted Page shall be represented in the Public UI Model before it is
   rendered.
2. The Public UI Model for an initial supported promoted Page shall conform to
   `PG`.
3. The Sidebar is part of the modelled public page, not unmodelled rendering
   infrastructure.
4. `PAPanel` contains the PA and its Notes; `FilterSection` is a sibling of
   `PAPanel`, not the owner of Notes.
5. A PA renderer may specialise the PA terminal form but shall not invent a
   different surrounding public-page structure.
6. Producers own analytical meaning; model resolution consumes deliberate
   site-facing inputs rather than normally recovering meaning from legacy HTML.
7. Rendering values and visual treatments that are not specified by `PG` belong
   in Rendering Design, not in the semantic model merely because they are
   visible.

---

## 8. Relationship to Adjacent Documents

`02 Specification.md` defines the public contracts and `PG` that these models
must represent.

`03 Architecture and Design Thesis.md` explains why the model layer exists and
why rendering must consume it.

`05 Rendering Design.md` shall define how modelled entities and PA terminal
forms become visible HTML, CSS and interactive browser behaviour.

The four supporting model documents shall now refine the declarations in this
overview without changing the specified public structure silently.