# Sidebar Rendering — Draft Notes v2

## Relationship to the Semantic Specification

The semantic specification defines:

```text
Sidebar
    = Caption + Navigation + Hider
```

This document concerns the realization of Sidebar within the standard renderer.

---

# General Sidebar Structure

The standard renderer realizes Sidebar as:

- a fixed-width vertical site-navigation region,
- positioned alongside the ContentPanel.

Sidebar comprises:

- Caption region,
- Navigation region,
- Hider widget.

---

# Sidebar Dimensions

```text
Sidebar.Width = SIDEBAR_WIDTH
```

Sidebar width is fixed by renderer policy.

Sidebar height equals the viewport height.

ContentPanel occupies the remaining horizontal space.

---

# Sidebar Colours

Default Sidebar colours:

```text
Foreground = WHITE
Background = NAVY
Muted      = MUTED
```

These are renderer tokens/constants rather than literal colour values.

---

# Sidebar Typography

Default Sidebar typography:

```text
normal-weight sans
```

Typography scales are referred to using symbolic size names:

```text
h1
h2
h3
h4
h5
```

These refer to renderer typography scales rather than HTML heading semantics.

---

# Sidebar Overflow Behaviour

Sidebar scrolls independently when its contents exceed available vertical space.

Scrolling the Sidebar does not scroll the ContentPanel.

Overflow behaviour belongs to Sidebar renderer policy rather than Navigation semantics.

---

# Caption

## Content

Caption currently consists of:

```text
line 1: "Gaspode-san's"
line 2: "Sumo Lab"
line 3: deployment timestamp
```

Timestamp format:

```text
YYYY/MM/DD HH:MM:SS
```

## Typography

Caption typography:

```text
lines 1–2:
    h1 scale

line 3:
    h4 scale
```

## Colours

Default Caption colours inherit Sidebar defaults.

Timestamp line uses:

```text
foreground = MUTED
```

## Semantics

Caption represents:

- site identity,
- publication identity,
- installation identity.

Caption does not represent:

- current page identity,
- PA identity.

---

# Navigation

## Structure

Navigation is rendered as:

- an indented,
- hierarchically numbered,
- collapsible list.

## Implemented Nodes

Nodes with targets render as links.

## Unimplemented Nodes

Nodes without targets render as:

- non-link labels,
- using MUTED foreground.

## Current Node

The current Navigation node shall be visually distinguished.

Exact realization remains renderer policy.

---

# Hider

## Status

Work in progress.

## Purpose

Hider allows the user to:

- hide,
- collapse,
- restore

the Sidebar.

## Likely Rendering

Hider will likely be realized as:

- a sticky widget,
- attached near the Sidebar/viewport boundary.

Indicative display:

```text
"<" when Sidebar visible
">" when Sidebar hidden
```

## Positioning

Hider will likely be vertically positioned within or near the Caption band.

## Constraint

Hider must not obscure:

- Caption text,
- deployment timestamp,

nor:

- heading/subheading text

when collapsed.

Exact positioning and collapse behaviour remain renderer policy.
