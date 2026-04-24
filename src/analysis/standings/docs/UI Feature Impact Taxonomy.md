# GSSWD Product Feature Taxonomy and Governance

### A Working Framework for Evaluating Controls, Metrics, Modes, and Future Enhancements

---

# 1. Purpose of this Document

This document exists to help guide product decisions for **Grand Sumo Standings by Wins Digest (GSSWD)**.

Its aims are simple:

- to think clearly about what features belong in the product

- to avoid adding controls merely because they are possible

- to preserve a coherent user experience as the project grows

- to record the reasoning behind past and future choices

- to remind future us that not every computable number deserves a dropdown

It is not a formal specification, technical design note, or set of binding rules.

It is a practical working paper for making better decisions.

---

# 2. Current Product Position

GSSWD is currently a browser-based standings page built from precomputed published data.

It aims to answer a practical question:

> Who has performed best over a recent rolling period?

The current product is intentionally lightweight:

- static publication model

- fast browser interaction

- no live server computation

- clear table presentation

- modest number of user controls

The present mainstream control set is:

- **Number of basho**

- **Division**

- **View**

- **Active rikishi only**

This is already enough to be useful without becoming exhausting.

That should not be taken for granted.

---

# 3. Product Principles

These are not laws. They are habits of thought.

## 3.1 Usefulness over Completeness

A smaller product that answers real questions well is better than a sprawling one that answers every theoretical question badly.

## 3.2 Simplicity First

The default experience should make sense quickly.

Users should not need a briefing document before seeing who is winning.

## 3.3 Trustworthiness

Displayed metrics should mean what ordinary users reasonably think they mean, or be clearly explained when they do not.

## 3.4 Coherence over Novelty

A feature being interesting is not yet evidence that it belongs.

## 3.5 Progressive Disclosure

Advanced capabilities may exist, but need not dominate the initial experience.

## 3.6 Preserve Optional Depth

The product should remain friendly to casual fans without boring enthusiasts.

## 3.7 Avoid the Museum of Our Cleverness

The interface should not become a shelf displaying every idea we ever had.

---

# 4. Feature Impact Taxonomy

When considering a new feature, control, mode, metric, or widget, assess it across the following dimensions.

---

## A. Upstream Impact

What must change before the browser can offer the feature?

### A0 — None

Already supported by current published artefacts.

### A1 — Publication Contract Change

Existing capability, but new fields, files, or schemas required.

### A2 — New Computation

Additional engine logic required.

### A3 — New Architecture or Data Source

Requires new systems, services, or external data.

---

## B. Downstream Impact

What changes in the user-facing product?

### B0 — Cosmetic

Labels, wording, styling only.

### B1 — Interaction

New control, selector, toggle, or mode.

### B2 — Semantic

Changes the meaning of displayed metrics or rankings.

### B3 — Cognitive Load

Adds complexity, decisions, or explanation burden.

### B4 — Trust Risk

Likely to mislead unless carefully explained.

---

## C. Product Value

How useful is it likely to be?

### C0 — Little Real Demand

### C1 — Niche but Valid

### C2 — Broadly Useful

### C3 — Core Value

---

## D. Applicability / Coherence

Does it make sense across supported contexts, and alongside other features?

### D0 — Universally Coherent

### D1 — Mostly Coherent with Caveats

### D2 — Combination-Sensitive

### D3 — Hard to Justify Clearly

---

## E. Regime Validity

How does it behave at different scales or settings (for example basho window or division)?

### E0 — Stable Across Range

### E1 — Weakens at Extremes

### E2 — Conceptually Drifts Beyond Threshold

### E3 — Only Makes Sense in Narrow Cases

---

## F. User-Type Sensitivity

Who is it really for?

### F0 — Almost Everyone

### F1 — Segmented but Reasonable

### F2 — Enthusiast / Specialist Leaning

### F3 — Expert Only or Mainstream-Hostile

---

# 5. Current User Types (Working Model)

These are rough thinking tools, not sociological truths.

## Type A — Casual / Mainstream Fan

Wants clear answers quickly.

Likely preferences:

- recent periods

- Makuuchi

- obvious metrics

- minimal controls

## Type B — Enthusiast

Enjoys exploring rankings, divisions, trends, and comparisons.

## Type C — Analyst / Specialist

Interested in assumptions, alternate metrics, methodology, and deeper controls.

A good product can serve all three, but not necessarily with the same interface density.

---

# 6. Applying the Framework to Current Controls

---

## 6.1 Number of Basho

A core control.

- High value (**C3**)

- Broad appeal at smaller values (**F0**)

- More specialist at larger values (**F2**)

- Meaning weakens at extremes (**E1/E2**)

A six-basho view is intuitive recent form.

A 406-basho view may be mathematically valid, but it has wandered into archaeology.

This is why upper bounds matter.

---

## 6.2 Division

Strong control with different audience meanings.

- Makuuchi is mainstream (**F0**)

- Juryo is still accessible (**F1**)

- lower divisions trend specialist (**F2**)

The current broad selector is reasonable so long as defaults remain sensible.

---

## 6.3 View

Current modes:

- Standard

- Percentages

- Combined

Standard is the everyday answer view.

Combined is more analytical.

That is acceptable, provided the product remembers which it is most days.

---

## 6.4 Activity Filter

One of the strongest recent additions.

It changes the eligible comparison population without changing underlying metrics.

Especially valuable at longer windows, where historical ghosts otherwise linger near the top of the table.

Defaulting to current rikishi only is likely the right mainstream choice.

---

# 7. Metric Configuration Space

The current product uses an implicit configuration point approximately like:

- **WinPolicy** = CREDITED

- **BashoBasis** = SELECTED

- **BoutBasis** = EXPECTED

This defines present meanings of:

- Wins

- Average

- Bouts

- Win %

These dimensions are real and analytically interesting.

They are not automatically good mainstream controls.

---

## 7.1 WinPolicy

Example question:

Should fusensho count as wins?

Reasonable topic.  
Usually specialist topic.

---

## 7.2 BashoBasis

Should averages divide by selected basho, containing basho, or some other basis?

Valid question.  
Rarely a first-screen question.

---

## 7.3 BoutBasis

Should percentages use expected bouts or available bouts?

Important analytically.  
High explanation burden.

---

## 7.4 Combined Warning

One advanced toggle may be manageable.

Several at once can create a product that feels like tax software.

---

# 8. Candidate Future Features

These ideas are not commitments.

They are examples of things that should pass through the framework before adoption.

---

## 8.1 Anchor Date Selection

User chooses standings *as of* a past basho.

Strong product value.  
Currently constrained by static publication economics.

Good idea, wrong architecture (for now).

---

## 8.2 User Modes

Examples:

- Simple

- Explore

- Expert

Potentially powerful, but easy to overcomplicate.

---

## 8.3 Search

Likely useful if dataset size or user demand justifies it.

---

## 8.4 Heya Filter

Potential enthusiast feature.

Worth considering only if real use-cases emerge.

---

## 8.5 Rikishi Body Mass Index Widget

The framework exists partly so we pause before adding this.

---

# 9. How to Consider New Features

When a new idea appears, ask:

## 9.1 What user problem does this solve?

If the answer is “none, but it is neat”, caution is advised.

## 9.2 Who is it for?

Type A, B, C, or only ourselves for ten minutes?

## 9.3 What does it cost?

Code, data, UI space, explanation burden, future maintenance.

## 9.4 Does it preserve trust?

Could a normal user misunderstand the result?

## 9.5 Does it crowd the interface?

Every new widget competes with existing clarity.

## 9.6 Is there a lighter version?

Sometimes a note, default, or sort option beats a new control.

---

# 10. Strategic Direction

The current product shape is promising:

- mainstream-friendly shell

- meaningful depth underneath

- room for enthusiasts

- no need yet for expert façade

That balance is worth protecting.

The likely danger is not lack of sophistication.

It is enthusiastic overgrowth.

---

# 11. Appendix: Historical Evolutions

## 11.1 Retirement Filter -> ActivityBasis

The project first considered explicit retirement filtering.

This was later generalised into the better concept of **ActivityBasis**:

Who belongs in the comparison population?

This handles retirement, inactivity, and similar absences more cleanly.

## 11.2 Why the Basho Range Is Bounded

Not every valid number of basho produces a meaningful standings page.

Limits can be product judgement, not mathematical weakness.

## 11.3 Why Some Good Ideas Wait

A feature may be valid but mistimed.

Sometimes the correct answer is:

> later, under a different architecture.

---

# 12. Final Note

If future us is ever tempted to add six new controls in one weekend:

please read this document first.
