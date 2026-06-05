# How to Review Notes and Gloss

## Purpose

Use this procedure when reviewing Notes, popovers, table headings, chart labels
and option gloss for a `make_site2` page.

This is a working procedure, not a record of page changes. Decisions that become
policy should move to the relevant model/rendering document or to `11 Notes and
Gloss.md`. Unfinished work should be recorded in `10 Open Issues and
Deferred Design.md`.

---

## Review Procedure

1. Classify the Navigation item.

Decide whether the item is a public deliverable, research/prototype deliverable,
future product idea, placeholder or navigation experiment.

2. Stop or defer if needed.

If the item is not a current deliverable worth glossifying, do not polish it
locally. Record the issue in the open-issues register.

3. Identify the reader moment.

State how a likely reader arrives, what context they already have, and what they
are trying to understand.

4. Classify depth and user type.

Use the depth and user-type vocabulary from `11 Notes and Gloss.md`.
This controls how plain or technical the wording should be.

5. Review page framing.

Check the Navigation label, page title, subtitle and PA caption. The PA should
be understandable as a standalone artifact together with its Notes.

6. Review options.

For each option, ask what a reader might need to know after understanding the
Navigation item and page title. Prefer clearer labels. Use short popover gloss
only when needed. Options do not get Notes.

7. Review PA-internal labels.

Inspect table headings, grouped headings, chart axes, legends, tick labels,
hover text, captions and empty states under the current option context.

8. Choose the explanation mechanism.

For each confusing feature, choose one:

```text
better primary wording
short popover
local PA Note
external guide pointer
open issue / defer
no explanation needed
```

9. Keep popovers short.

If a popover becomes paragraph-like, move the explanation into Notes or a guide.
Use `See Notes` only when the relevant Note exists for that PA state.

10. Capture deferred issues.

Anything beyond the pass goes to open issues, especially chart axis density,
compressed Chii layout, right-axis orientation, unclear data-cliff presentation
and broader Navigation restructuring.

---

## Close-Out Checklist

Before finishing a review pass:

- update implemented labels, popovers and Notes;
- update tests where the manifest or renderer contract changed;
- build enough output to inspect the affected page state;
- record unresolved work in `10.4 Open Issues - Defects and Deferred Matters.md`;
- remove stale candidate/open-question wording from active docs when a decision
  has become policy.
