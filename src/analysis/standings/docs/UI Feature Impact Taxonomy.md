# GSSWD: Movement in Metric Configuration Space via the Feature Impact Taxonomy

## Current Fixed Configuration Point

The current browser product is approximately:

* **WinPolicy** = CREDITED
* **BashoBasis** = SELECTED
* **BoutBasis** = EXPECTED

This defines the present meanings of:

* Wins
* Average
* Bouts
* Win %

Any new UI control would allow movement away from this fixed point.

---

# Taxonomy for Movement in Metric Configuration Space

When considering exposing a new configuration dimension, assess:

## A. Upstream Impact

### A0 — None

Already published exactly as needed.

### A1 — Publication Contract Change

Existing capability, but new fields / schema / sidecars required.

### A2 — New Computation

Need new engine logic.

### A3 — New External Data

Need new data sources.

---

## B. Downstream Impact

### B0 — Cosmetic

Labels / display only.

### B1 — Interaction

New control / selector.

### B2 — Semantic

Changes meaning of shown metrics.

### B3 — Cognitive Load

More choices / more complexity.

### B4 — Trust Risk

Could mislead unless clearly explained.

---

## C. Product Value

### C0 — No real demand

### C1 — Niche but valid

### C2 — Broadly useful

### C3 — Core value

---

# Applying the Taxonomy to the Three Existing Dimensions

---

# 1. Move in WinPolicy Dimension

Current:

* CREDITED

Alternative:

* FOUGHT_ONLY

## Upstream

* **A1** likely
  Need additional explicit derived metrics (especially percentages) or browser derivation.

## Downstream

* **B1** add control
* **B2** Wins / Average / Win % meanings change
* **B3** moderate complexity
* **B4** notes must explain fusensho treatment

## Value

* **C1** niche but real
* maybe **C2** among analytical users

## Verdict

Good advanced option, not urgent.

---

# 2. Move in BashoBasis Dimension

Current:

* SELECTED

Alternative:

* CONTAINING

## Upstream

* **A0** already published

## Downstream

* **B1** add control
* **B2** Average / Bouts interpretations change
* **B3** moderate complexity
* **B4** must explain why absences alter averages

## Value

* **C1** niche but legitimate

## Verdict

Cheap technically, moderate explanatory burden.

---

# 3. Move in BoutBasis Dimension

Current:

* EXPECTED

Alternative:

* AVAILABLE

## Upstream

* **A0** already published

## Downstream

* **B1** add control
* **B2** Bouts / Win % meanings change strongly
* **B3** moderate complexity
* **B4** highest trust risk if users miss denominator basis

## Value

* **C1/C2** useful to analytical users

## Verdict

Technically cheap, semantically sensitive.

---

# Comparing the Three Moves

| Dimension  | Upstream Cost | Semantic Risk | User Value | Recommended Exposure |
| ---------- | ------------- | ------------- | ---------- | -------------------- |
| WinPolicy  | Medium        | Medium        | Medium     | Advanced             |
| BashoBasis | Low           | Medium        | Low-Medium | Advanced             |
| BoutBasis  | Low           | High          | Medium     | Advanced             |

---

# Important Combined Insight

A single move is manageable.

Multiple simultaneous moves create combinatorial UX burden:

* 2 × 2 × 2 = **8 metric configurations**

Even if technically easy, user comprehension may collapse.

So movement in metric configuration space should likely be:

* one dimension at a time
* hidden in advanced mode
* accompanied by clear explanatory text
* resettable to defaults

---

# Product Strategy Implication

The current fixed point is probably the right mainstream default because it optimises:

* intuitive standings logic
* accountability across period
* recognisable wins totals

So the key product question is not:

> should users roam freely in configuration space?

but:

> which controlled movements are worth permitting?

---

# My blunt recommendation

Treat Metric Configuration Space as an **expert capability reservoir**.

Default users stay at the current point.

Advanced users may selectively move one dimension when they have a specific question.

That preserves simplicity while leveraging the sophistication already latent in the project.



# Other Features

---

# 1 Feature: User-selectable Anchor Date

Meaning:

Instead of only publishing standings anchored to the current/latest date, allow the user to choose an older basho date and view standings relative to that anchor.

So the user could ask:

- standings as of March 2026

- standings as of September 2024

- six-basho table ending January 2023

That is clearly appealing.

---

# Why It Feels Valuable

From a user perspective this enables:

- historical browsing

- “what did the world look like then?”

- retrospective comparisons

- checking narratives (“was he already rising?”)

- archive exploration

So downstream value is real.

---

# Taxonomy Assessment

# A. Upstream Impact

## Under current static-file model: very high

Right now the publisher emits one anchor point (latest/current) across supported windows.

To support arbitrary anchors statically, you would need datasets for:

- many dates ×

- many retrospective window sizes ×

- possibly future extra dimensions

That scales quickly.

As you said: sets of files for every possible date.

That is classic **A2/A3-ish operational burden**, even if the calculations themselves are possible.

Not mathematically hard, but deployment-hosting-file-management hard.

## Publication explosion example

If you had:

- 100 historical anchor dates

- 5 supported basho windows

That is already 500 dataset pairs + sidecars + config implications.

And that is before policy variants or archives.

So yes: under the current architecture, unattractive.

---

# B. Downstream Impact

Actually modest.

UI-wise it is simple:

- add date selector

- update title

- load matching files

Users would understand it easily.

So downstream:

- B1 interaction change

- low B3 complexity

- high user value for some users

The blocker is upstream, not UX.

---

# Therefore Your Conclusion Is Rational

> nice idea, not going to happen (for now)

Exactly.

This is the right judgement when:

- downstream attractiveness exists

- but upstream architecture makes it disproportionate

That is mature scope control.

---

# Important Nuance: “Not now” ≠ “Bad idea”

This is not a rejected feature.

It is a **deferred feature contingent on architecture**.

Specifically:

> feasible once standings generation happens server-side or via on-demand compute.

That could mean:

## Future architectures

### 1. Remote compute endpoint

User picks anchor date → server generates or retrieves standings.

### 2. Precomputed archive index + lazy fetch

Only popular anchors prebuilt.

### 3. Hybrid

Current anchor static; historical requests dynamic.

---

# Strategic Value of Naming This Clearly

I would record it as:

> Historical Anchor Selection is product-valid but incompatible with current static publication economics.

That prevents revisiting the same debate repeatedly.

---

# My Taxonomy Classification

## Today

- Upstream: **A3 / operationally prohibitive**

- Downstream: **B1**

- Value: **C2**

Result: defer.

## If server-side later

- Upstream: **A1/A2**

- Downstream: **B1**

- Value: **C2/C3**

Result: strong candidate.

---

# One More Observation

This feature is qualitatively different from WinPolicy/BashoBasis/BoutBasis.

Those move within **metric configuration space** while keeping one dataset.

Anchor-date choice moves within **data selection space**.

That often has much larger infrastructure consequences.

That distinction is worth preserving.

---

# My blunt summary

You are right.

Under the current static architecture:

> elegant user feature, wrong engineering trade.

So defer it without apology.



# 2 Potential New UI Control: Retired Rikishi Inclusion

## Control Concept

Allow the user to choose whether rikishi who are no longer on the current banzuke are included in standings results.

### Suggested UI Forms

- **Include retired rikishi:** Yes / No

- **Current rikishi only** / **Include retired rikishi**

- Checkbox: **Show retired rikishi**

My preference:

> **Include retired rikishi: No (default)**

because it states clearly what is being varied.

---

# Domain Definition

For this product, a practical and robust rule is:

> **Retired = not currently on the banzuke**

Given the historical rarity of reappearance after disappearance, this is operationally strong and easy to explain.

So this is not a vague status judgement; it is a concrete roster-membership test.

---

# Why This Control Matters

## Current Behaviour Without Filter

Longer reporting windows can surface historically dominant rikishi whose legacy results remain statistically strong despite retirement.

Examples:

- Hakuhō Shō appearing high in a 60-basho table long after retirement

- Terunofuji Haruo lingering in extended windows after departure

- other former high performers occupying visible positions

Mathematically valid, but often contrary to ordinary user expectation.

## Type A User Expectation

Most users reading a current rolling standings page implicitly expect:

> who is leading among current rikishi?

not:

> which historical residue remains strongest in the selected window?

So default inclusion of retirees can feel surprising or misleading.

---

# Feature Impact Taxonomy Assessment

# A. Upstream Impact

## Likely A0 or A1 (Low)

### A0 — None / Trivial

If current-banzuke membership is already inferable from existing published data.

### A1 — Publication Contract Adjustment

Publisher emits a boolean such as:

```text
is_retired
```

or

```text
is_current_banzuke_member
```

No new analytical computation is required.

## No New Engine Logic Needed

This is a population filter, not a standings-metric redesign.

---

# B. Downstream Impact

## B1 — Interaction Change

Adds one simple filter control.

## B2 — Population Semantics Change

Changes who is eligible to appear, not how metrics are calculated.

## B3 — Cognitive Load: Low

Almost everyone understands what retirement means.

## B4 — Trust / Interpretability Improvement

Likely improves user confidence because results feel more current and intuitive.

---

# C. Product Value

## C2 / Possibly C3

Especially valuable when using larger windows such as:

- 30 basho

- 60 basho

- any future larger retrospective views

Low importance for very short windows; high importance for long windows.

---

# Behavioural Recommendation

## Default Setting

> **Exclude retired rikishi**

This aligns with mainstream user expectation.

## Optional Setting

> **Include retired rikishi**

Allows historians, enthusiasts, and curiosity-driven users to inspect legacy standings.

---

# Interaction with Other Controls

## Basho Count

The longer the window, the more valuable this control becomes.

## Metric Configuration Space

This control is **not** part of metric configuration space.

It does **not** change:

- Wins meaning

- Average basis

- Bout denominator

- Win %

It changes only the **eligible population**.

So it belongs in a separate category:

> **Population Filters**

---

# UI Placement

Best placed near Division and Basho-window controls, not among metric controls.

Suggested control groups:

### Scope Controls

- Basho count

- Division

- Include retired rikishi

### Metric Controls (future advanced)

- WinPolicy

- BashoBasis

- BoutBasis

That separation would be clean.

---

# Risks / Caveats

## 1. Tiny Historical Edge Cases

Rare re-entry cases (e.g. Sokokurai Eikō) may require careful implementation, but do not invalidate the model.

## 2. User Surprise If Hidden Without Explanation

A brief note may help:

> Retired rikishi are excluded by default.

---

# Why This Is a Strong Candidate Feature

Compared with many advanced options, this feature is:

- cheap to implement

- easy to explain

- high practical value

- low cognitive burden

- improves perceived relevance

- preserves optional historical curiosity

---

# Final Judgement

This is one of the best next substantive UI additions available.

> **Simple upstream, simple downstream, real user value.**

I would rank it above most metric-configuration toggles for mainstream product usefulness.
