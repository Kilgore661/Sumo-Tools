# 11 Notes and Gloss

## Status

Normative support document for the `make_site2` Notes, popover and gloss
treatment.

This document describes what Notes and gloss are for, where they belong, and
how they should be worded. It is not a change log. Deferred or missing work
belongs in `10 Open Issues and Deferred Design.md` and its numbered issue
registers.

For the review procedure, see `How to Review Notes and Gloss.md`.

---

## 1. Purpose

Notes and gloss help readers understand visible analytical material without
turning the public site into a manual.

They are for moments where the visible UI is simple enough to use, but a label,
column, option, chart axis or table convention may not mean quite what the
reader expects.

They should support the reader's context ladder:

```text
Navigation item
  -> page title and subtitle
  -> options / filters
  -> PA caption
  -> table headings, chart axes, legends and values
  -> local gloss or Notes where needed
```

The public UI should remain readable without requiring the reader to study a
separate manual first.

---

## 2. Ownership

### 2.1 Notes

Notes belong to the Published Artifact, not to the whole ContentsPanel.

```text
PAPanel -> PA . Notes
```

A Note explains the visible PA or a visible feature of the PA. Notes may be
relevant only under some option states, but the option does not own the Note.

Notes shall not be used as help text owned by Filters.

### 2.2 Option Gloss

Options may have short popover gloss. The reader should normally be able to
understand an option from the Navigation item, page title and current PA
context. If the option needs a long explanation, the option label or feature
probably needs redesign, or it should point to a wider guide.

Options do not get Notes.

### 2.3 PA Gloss

Table headings, chart axes, legends and compact labels may have short popover
gloss. If the explanation is longer than a small phrase, the popover should
point to Notes or to a wider guide.

---

## 3. Popovers

A popover is hover/focus gloss attached to an existing visible item. It should
not become a separate UI token that the reader must target, although a subtle
marker may indicate that gloss exists.

Preferred popover types:

| Type | Use | Example |
| --- | --- | --- |
| Direct gloss | Explain a short label locally. | `Equelo rating.` |
| Note pointer | Signal a caveat or convention handled in Notes. | `See Notes.` |
| Hybrid gloss | Give a tiny disambiguation and point to Notes. | `Size of movement. See Notes.` |
| External guide gloss | Point outside the PA when the concept is too large. | `See TBD` |

Popover text should be compact, concrete and context-sensitive. It should not
duplicate a Note, contradict a Note, or promise a guide that does not exist
without making the placeholder deliberate.

`See Notes` should only be used when a relevant Note is available in the current
PA state. The desired future behaviour is that `See Notes` opens the Notes panel
if it is hidden and ideally highlights the relevant Note.

---

## 4. Notes

Notes should be short enough to read in place. They may use more words than a
popover, but they should still serve the PA, not become background essays.

Good Notes:

- explain a convention that affects how visible values should be read;
- distinguish similar-looking symbols or labels;
- state caveats that are material to the PA;
- use reader-facing language before technical language.

Poor Notes:

- explain site navigation or option mechanics;
- repeat obvious labels;
- introduce unrelated methodology;
- carry expert detail that belongs in a research or methodology page.

When a Note refers to a visible table heading, option label, axis title or other
UI token, use a distinct token style consistently in prose. Markdown backticks
represent that intent in the source text, for example `Result` or `Bouts`.

---

## 5. Depth and Wording

Each page review should classify the page by depth and likely user type before
wording Notes or gloss.

Depth:

| Depth | Meaning |
| --- | --- |
| Basic | Usable by a reader who can follow a simple UI and knows ordinary sumo context. |
| Basic+ | Basic public use, with a few optional conventions or model terms that need gloss. |
| Advanced | Requires more analytical interest or willingness to interpret derived values. |
| Research | Mainly supports investigation, modelling or methodology. |
| Expert | Depends on specialised knowledge, assumptions or unresolved methodology. |

User types:

| Type | Meaning |
| --- | --- |
| A | General sumo-interested reader looking for usable public information. |
| B | Engaged analyst or fan willing to compare structures, options and derived values. |
| C | Research/methodology reader interested in model assumptions and edge cases. |
| D | Developer/maintainer inspecting implementation or production behaviour. |

The lower the expected depth, the less technical the gloss should be. Research
pages may use heavier terms, but only when the page framing makes that bargain
clear.

---

## 6. Table Result Policy

Where a public table exposes `Result`, prefer the 7.1 Basho Results shape:

```text
W
L
A
Prize
```

That is, display wins, losses, absences and prizes as separate compact terminal
columns where the table structure can support it. Keep movement values distinct
from score/prize values.

Compact result strings such as `10-5 G` are transitional or pragmatic
presentations, not the preferred general public model. Work to migrate remaining
Result columns is tracked in the open issues register.

---

## 7. Navigation and Discovery

The current Navigation tree is not a source of product truth. It contains
deliverables, research/prototype pages, future ideas and navigation experiments.

Glossification should therefore classify each Navigation item before spending
time on local wording. If the item is not a current deliverable worth
glossifying, defer it and record the issue.

Known navigation follow-ups, such as collapsible nested sections, active-item
scrolling and broader restructuring, belong in open issues rather than this
document.

---

## 8. Open Work

This document states the policy. It does not list outstanding tasks.

Use `10 Open Issues and Deferred Design.md` and especially
`10.4 Open Issues - Defects and Deferred Matters.md` for pending work such as
popover text review, Result-column migration, chart axis density, compressed
Chii layout, right-axis orientation, First Chii Appearance data-cliff visibility
and Navigation restructuring.
