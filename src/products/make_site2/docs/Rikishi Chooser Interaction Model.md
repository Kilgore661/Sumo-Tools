# Rikishi Chooser Interaction Model for `page=career_comparisons`

## Status

Implemented interaction contract. Automated commitment-rule tests pass;
browser acceptance testing remains to be completed.

## Purpose

This note describes the interaction semantics of the rikishi chooser used on
the `career_comparisons` page, explains why its former behaviour was incorrect,
and records the replacement model based on an explicit user commitment event.

The interaction contract, rather than incidental event-handler details, governs
the implementation.

---

## 1. Former Model

The chooser was implemented as a text input associated with an HTML `datalist`.

Conceptually, it has two responsibilities:

1. Filter the available rikishi as the user types.
2. Add a rikishi to the selected set.

In the former implementation, these responsibilities were coupled.

On every `input` event, the code:

1. Reads the current text.
2. Canonicalises it by trimming and lowercasing.
3. Checks whether it exactly matches the label of an available rikishi.
4. If it does, immediately adds that rikishi.
5. Clears the input and rerenders the chart.

The effective rule is therefore:

> If the text currently in the input is a valid rikishi label, treat that rikishi as chosen.

This treats **text equality** as equivalent to **user commitment**.

### Consequence

Suppose the available names include:

- `Fuji`
- `Fujika`

When the user tries to type `Fujika`, the following occurs:

1. The user types `F`.
2. The user types `u`.
3. The user types `j`.
4. The user types `i`.
5. The input now contains `Fuji`.
6. `Fuji` is an exact valid label.
7. The code immediately selects `Fuji` and clears the input.
8. The user never gets the opportunity to type `ka`.

This is not primarily a browser-specific problem. Browser behaviour may affect how the `datalist` popup looks or how suggestions are presented, but the premature selection follows from the JavaScript event model itself.

---

## 2. Why the Current Model Is Incorrect

Typing and choosing are different user actions.

While typing, the text in the input represents a **provisional query**. It is not yet necessarily the user's final choice.

A valid name appearing in the input can mean several things:

- The user intends to select that exact name.
- The user is still typing a longer name.
- The user has pasted part of a name.
- The browser has temporarily filled the field while navigating suggestions.
- The user is editing or correcting the query.

The current implementation cannot distinguish these cases.

The central semantic error is:

> A valid intermediate input state is being interpreted as a completed selection.

This is especially visible with prefix-related names, but the underlying issue is broader. Selection should not be inferred solely from the current string value.

---

## 3. Correct Interaction Model

The control should distinguish between two kinds of state:

### Query state

The text currently being entered by the user.

Its purpose is to filter or navigate the candidate list.

Changing the query must not, by itself, add a rikishi.

### Committed selection

A deliberate instruction from the user that identifies one candidate as chosen.

A rikishi should be added only after a human-generated commitment event.

The governing rule should be:

> Typing changes the query. A separate commitment action chooses a rikishi.

This is the same general model used by autocomplete, combobox, command-palette, and search-and-select controls.

---

## 4. What Counts as a Commitment Event

The most natural commitment events are:

### Pressing Enter

If the input or highlighted suggestion resolves unambiguously to a valid rikishi, pressing Enter commits that candidate.

Possible behaviour:

- If a suggestion is actively highlighted, select it.
- Otherwise, if the input exactly matches one candidate, select that candidate.
- Otherwise, show an alert explaining that the entry is incomplete or
  ambiguous, preserve the query, and return focus to the input.

### Clicking or tapping a suggestion

Selecting an entry from the displayed candidate list commits that entry.

This is the clearest pointer-based interaction.

### Optional Add button

An explicit **Add** button could commit the currently resolved candidate.

This is not essential if Enter and suggestion selection work reliably, but it can make the commitment step more obvious and improve touch accessibility.

### Optional Tab behaviour

Tab is usually best treated as focus navigation rather than commitment. It should only commit a candidate if that behaviour is deliberately chosen and clearly consistent with the rest of the site.

---

## 5. Recommended Behaviour

A robust interaction sequence would be:

1. The user focuses the chooser.
2. The candidate list appears.
3. Typing filters the list.
4. Typing never adds a rikishi.
5. The user chooses a candidate by:
   - clicking or tapping it, or
   - moving to it with the keyboard and pressing Enter.
6. Only then is the rikishi added.
7. The input is cleared.
8. The selected list, URL state, and chart are updated.
9. Focus returns to the input so another rikishi can be added.

For `Fuji` and `Fujika`, the user can therefore type the complete text `Fujika` without `Fuji` being selected along the way.

---

## 6. Implementation Decision

The following models were considered. The explicit custom combobox is the
implemented design because it can distinguish ordinary typing, keyboard
commitment, and direct pointer activation without relying on browser-specific
`datalist` inference.

## 6.1 Rejected: minimal change to the existing `datalist` model

The existing input and `datalist` can be retained, but selection must no longer occur in the `input` handler.

### Input event

The `input` event should only:

- enable or refresh the candidate list;
- filter candidates;
- update provisional UI state.

It should never call the selection routine.

### Change event

A `change` event may indicate that a browser-mediated datalist choice has been made. If the final value exactly matches an available candidate, it can be committed here.

However, native `datalist` event semantics are not perfectly uniform across browsers, so `change` alone may not provide the most predictable experience.

### Keydown event

A `keydown` handler can detect Enter.

On Enter:

1. Prevent form submission where necessary.
2. Resolve the current value or highlighted candidate.
3. Commit it if valid.
4. Leave the query untouched if it is not valid.

### Strengths

- Small conceptual change.
- Preserves the current markup.
- Retains browser-provided suggestion rendering.

### Limitations

- Native `datalist` behaviour varies between browsers.
- There is limited control over highlighting, suggestion identity, and accessibility details.
- Distinguishing free typing from a clicked datalist option can be awkward.

---

## 6.2 Implemented: explicit custom combobox

A more controlled design would replace the native `datalist` behaviour with an ARIA combobox and a rendered listbox.

The control would maintain explicit state such as:

- current query;
- filtered candidates;
- open or closed list;
- highlighted candidate;
- committed selections.

### Events

- `input`: change query and filtered candidates.
- Arrow Down / Arrow Up: move the highlighted candidate.
- Enter: commit the highlighted candidate.
- Escape: close the list without selecting.
- Mouse click or pointer activation: commit the clicked candidate.
- Blur: close the list, but do not infer selection merely from text.

### Strengths

- Precise and testable semantics.
- Consistent behaviour across browsers.
- Full control over keyboard interaction.
- Candidate identity can remain the rikishi ID even when labels are duplicated or changed.
- Easier to communicate active suggestion state accessibly.

### Limitations

- More code.
- Requires careful accessibility implementation and testing.
- Must manage focus, keyboard navigation, and list positioning explicitly.

This is the implemented model.

---

## 6.3 Rejected: text field plus explicit Add action

A simpler alternative is to retain the filtered suggestions but require an Add button or Enter press to commit.

The control could display a resolved candidate beside the input:

> Add: Fujika

The user then presses Enter or activates Add.

### Strengths

- Very clear separation between query and commitment.
- Easy to reason about and test.
- Less dependence on browser-specific datalist behaviour.

### Limitations

- Slightly more interaction than direct suggestion selection.
- Still needs a rule for resolving ambiguous or partial input.

---

## 7. Candidate Resolution Rules

The commitment mechanism should resolve candidates by stable identity, not merely by display text.

The current option model uses:

- a stable rikishi ID;
- a display label based on the latest shikona;
- searchable prefixes derived from label, shikona, and ID.

A committed choice should carry the candidate's rikishi ID.

The visible label is presentation. The ID is identity.

### Exact-label commitment

If Enter is pressed with no highlighted option, an exact case-insensitive label match may be accepted.

### Highlighted-option commitment

If a candidate is highlighted, Enter should select that candidate regardless of whether the input contains its full label.

This supports efficient keyboard use.

### Ambiguity

If two candidates can have the same visible label, the chooser needs disambiguating text, for example:

- shikona plus rikishi ID;
- shikona plus active years;
- shikona plus highest rank.

The selected value should still be the stable ID.

### Invalid or partial text

Pressing Enter on text that does not resolve to one candidate should not silently select the first prefix match.

Possible responses include:

- leave the text in place;
- keep the candidate list open;
- announce “Choose a rikishi from the list”;
- select the sole remaining match only if that behaviour is deliberately specified.

The safest default is to require an exact or explicitly highlighted candidate.

---

## 8. State Transition Model

The control can be understood as a small state machine.

### Idle

- Query is empty.
- No candidate is highlighted.
- The list may be closed.

### Searching

- Query contains text.
- Matching candidates are shown.
- One candidate may be highlighted.
- No selection has yet occurred.

### Committing

Triggered only by Enter, click, tap, or another explicit Add action.

- Resolve the chosen candidate.
- Add its ID if not already selected.
- Clear any stored visibility override for that ID.
- Clear the query.
- Refresh selected-rikishi UI.
- Update URL state.
- Rerender the plot.

### Invalid commitment

- No unique valid candidate can be resolved.
- Do not add anything.
- Preserve the query.
- Keep focus in the chooser.
- Optionally display or announce guidance.

This state model prevents provisional text from being mistaken for a command.

---

## 9. Accessibility Model

The semantic control is a **multi-value autocomplete combobox**.

Useful accessibility expectations include:

- The text input has combobox semantics.
- The suggestion popup has listbox semantics.
- Each candidate is an option.
- The currently navigated candidate is exposed as active.
- Arrow keys navigate suggestions.
- Enter commits a suggestion.
- Escape closes the popup.
- Selected rikishi are presented as a separate list.
- Removal and visibility controls retain clear accessible labels.
- Adding or failing to add a candidate is announced where appropriate.

The existing selected-rikishi list already gives each chosen rikishi explicit remove and visibility controls. The main semantic improvement is to make candidate commitment explicit rather than value-driven.

---

## 10. Acceptance Criteria

The corrected control should satisfy at least the following tests.

### Prefix names

Given candidates `Fuji` and `Fujika`:

- Typing `Fuji` does not automatically select `Fuji`.
- The user can continue typing `Fujika`.
- Pressing Enter on `Fujika` selects `Fujika`.
- Clicking `Fuji` selects `Fuji`.

### Exact name

Given candidate `Hakuho`:

- Typing `Hakuho` alone does not select it.
- Pressing Enter selects it.
- Clicking its suggestion selects it.

### Partial text

Given several candidates beginning with `Taka`:

- Typing `Taka` filters the list.
- Pressing Enter without an exact or highlighted candidate displays the
  incomplete-or-ambiguous alert and does not arbitrarily select one.
- The query remains available for editing after the alert.

### Blur and Tab

- Moving focus away from the input does not select a rikishi.
- Pressing Tab does not select a rikishi.

### Duplicate selection

- Selecting an already-selected rikishi does not add a duplicate.
- The control remains usable after the attempted duplicate.

### Removal and reselection

- Removing a rikishi makes it available in the candidate list again.
- Reselecting it works through the same commitment mechanism.

### URL state

- The `rikishi` URL parameter changes only after a committed addition or removal.
- Merely typing in the query does not alter URL state.

### Browser behaviour

- Keyboard and pointer commitment behave consistently in supported browsers.
- No browser can trigger selection merely because the input temporarily equals a candidate label.

---

## 11. Implemented Direction

The correction follows this rule:

> Remove selection from the `input` event and perform it only in response to an explicit commitment event.

The chooser is implemented as a custom combobox/listbox with explicit query,
highlighted-candidate and committed-selection state. Return commits the
highlighted candidate or an exact unambiguous label. Clicking or tapping a
candidate commits its rikishi ID immediately. Invalid Return displays an alert
and preserves the query. Blur and Tab do not commit.

The important design decision is independent of the chosen UI technology:

> Text entry is provisional. Selection is an explicit user action.
