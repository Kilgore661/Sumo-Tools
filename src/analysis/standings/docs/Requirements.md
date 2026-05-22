# Grand Sumo Standings by Wins Digest (GSSWD) Requirements

## 1. Purpose

The product shall provide an accessible, trustworthy, and regularly updated browser-based view of recent professional sumo standings.

It shall allow users to answer the practical question:

> Who has performed best over a recent rolling period?

without requiring specialist tools, direct access to raw data, or technical knowledge of the underlying data model.

---

## 2. Core User Need

A user shall be able to open the page and quickly understand:

* who is doing well
* over what period the standings apply
* how rankings are determined
* how to change the reporting window
* how to narrow the view to divisions of interest

The product shall favour practical usefulness over theoretical completeness.

---

## 3. Intended Users

The initial product shall primarily serve:

### 3.1 Interested Fans

Users who follow sumo and wish to inspect recent form, compare rikishi, and explore standings beyond a single basho result.

### 3.2 Casual Fans

Users with lighter knowledge who want a simple answer to:

* who is winning lately?
* who is rising?
* how has my favourite rikishi done recently?

### 3.3 Expert / Analytical Users (Secondary)

More demanding users may inspect deeper metrics if available, but the initial product shall not optimise primarily for them.

---

## 4. Product Principles

## 4.1 Simplicity First

The default experience shall be understandable without study.

The page shall not confront first-time users with unnecessary controls or intimidating density.

---

## 4.2 Trustworthiness

Displayed rankings and metrics shall be derived consistently from published rules.

The page shall not imply meanings the calculations do not support.

---

## 4.3 Responsiveness

The product shall feel immediate and lightweight in normal browser use.

Routine interactions such as sorting, filtering, and changing published windows shall not require slow recomputation.

---

## 4.4 Stability

The product shall present stable behaviour and terminology across updates.

Users should be able to learn the interface once and return confidently.

---

## 5. Functional Requirements

## 5.1 Published Rolling Standings

The application shall present standings over predefined retrospective basho windows.

Users shall be able to choose among supported periods.

---

## 5.2 Division Browsing

Users shall be able to restrict the table to relevant divisions.

At minimum, major professional divisions shall be supported.

---

## 5.3 Activity Filtering

Users shall be able to choose whether displayed standings include:

* only rikishi appearing on the terminal banzuke of the selected reporting period
* all rikishi represented in the selected standings window

The default behaviour shall favour current rikishi only.

Changing the activity filter shall update the displayed table without requiring regeneration of standings data.

---

## 5.4 Sortable Standings Table

Users shall be able to reorder visible data by meaningful visible columns.

Sorting shall behave predictably.

---

## 5.5 Clear Period Labelling

The page shall clearly state the reporting period represented by the current standings.

No user should need to infer the covered dates.

---

## 5.6 Interpretable Metrics

Displayed metrics shall be comprehensible enough that a reasonable interested fan can understand what they broadly mean.

Where ambiguity exists, explanatory notes shall be available.

---

## 5.7 Recent Identity Representation

Rows shall identify rikishi using recognisable current or near-current names/ranks rather than opaque historical identifiers.

---

## 6. Non-Functional Requirements

## 6.1 Static Deployment Preferred

The product should be publishable as static web artefacts where practical.

This keeps hosting simple and robust.

---

## 6.2 Low Operational Complexity

Routine updates should be achievable through offline generation rather than maintaining a live server computation system.

---

## 6.3 Cross-Browser Practicality

The product shall work in mainstream desktop browsers.

Mobile usability is desirable but not the primary initial optimisation target.

---

## 6.4 Maintainability

The system should remain understandable to a single maintainer.

Excessive architectural complexity should be avoided unless justified by clear value.

---

## 7. UX Requirements

## 7.1 Low Cognitive Friction

The default page shall not overwhelm users with numbers, controls, or jargon.

---

## 7.2 Progressive Disclosure

More detailed comparative metrics may be available, but need not dominate the initial view.

---

## 7.3 Honest Explanations

Where metrics depend on conventions (for example expected bouts or representative rank), those conventions shall be explainable on-page.

---

## 7.4 Direct Manipulation

Users should be able to change key views directly from visible controls rather than hidden menus or command syntax.

---

## 8. Scope Boundaries (Initial Release)

The product is **not initially required** to provide:

* arbitrary custom date ranges
* user-defined formulas
* live predictive analytics
* opponent-strength adjustment
* exhaustive historical query tooling
* full mobile-native redesign
* advanced statistical dashboards

These may be future enhancements.

---

## 9. Data Integrity Requirements

The published standings shall be based on authoritative historical tournament data as available to the project.

If data is incomplete or unavailable, the product should fail clearly rather than silently mislead.

---

## 10. Evolution Requirements

The product shall permit later extension in areas such as:

* alternate metric views
* additional explanatory controls
* advanced user options
* richer filtering
* comparative analytics

without requiring total redesign.

---

## 11. Success Criteria

The first version shall be considered successful if an interested fan can:

1. open the page
2. understand the current standings period
3. identify leading rikishi
4. change the basho window
5. filter by division
6. understand at a high level why rankings appear as shown

within a few minutes and without external instruction.

---

## 12. Governing Principle

When trade-offs arise between elegance, completeness, and usefulness:

> usefulness to real users viewing recent sumo standings shall take priority.
