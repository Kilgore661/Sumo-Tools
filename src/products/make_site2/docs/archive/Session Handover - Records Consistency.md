# Session Handover - Records Consistency

## Status

Handover note for the Records consistency discussion after moving Longest
Careers out of Career Length and into Sumo History > Records.

The implementation work completed in commit:

```text
8b0beed Move Longest Careers into Records
```

Two open-issue documents have uncommitted follow-up notes from the later
conversation:

```text
10.4(2) Open Issues - Defects and Deferred Matters.md
10.5 Open Issues - Priority View and Summary.md
```

Those notes record the deferred options/checkbox grammar and Records population
direction.

---

## Completed Implementation

Longest Careers is now a promoted Records page:

```text
Sumo History > Records > Longest careers
```

It is no longer a `Longest` view inside Career Length. Career Length now owns
only chart views:

```text
distribution
pmf
cdf
survival
```

Longest Careers uses a Records table artifact and reads:

```text
sumo-history/records/longest-careers/data/longest.csv
```

The public staged path was moved from the Career Length output tree into the
Records output tree. `make_site2` still derives the Records CSV from the Career
Length producer source material.

Focused verification passed for:

```text
test_make_site2_data_output.py
test_make_site2_table_sorting.py
targeted Longest Careers manifest checks
Python syntax checks on touched make_site2 modules and tests
node --check on touched runtime modules
```

Known unrelated stale root tests remain around older expectations for Standings
navigation, BRB filter naming, and GOATs quick-link host.

---

## Records Vocabulary Direction

The Records pages are inconsistent because they came from different places at
different times. Current population vocabulary should be standardised as:

```text
Current
Former
```

rather than:

```text
retired
non-retired
active
inactive
```

The provisional Records population control is:

```text
Rikishi
[x] Current
[x] Former
```

Both checked is default and means the combined all-rikishi population.

This should apply consistently to all five Records artifacts:

```text
Most Consecutive Bouts
Most Career Wins
Most Career Losses
Highest Equelo
Longest Careers
```

Additional provisional wording:

- Most Consecutive Bouts: replace `Clean only?` with `Whole career`.
- Most Career Wins: replace `Count fusen results?` with `Fusensho`, false by
  default.
- Most Career Losses: replace `Count fusen results?` with `Fusenpai`, false by
  default.

For Most Consecutive Bouts, add Current/Former population selection for
consistency. The visible active/clean-status column probably becomes
unnecessary if the filter selects that record population.

---

## Important Deferred Issue: Ranking

The apparent UI-label cleanup is not merely cosmetic.

For superlative tables, the `#` column is not ordinary display chrome. It is a
record position. If a control changes the population or counting policy, then
the ranked result may need to be produced for that selected basis rather than
filtered after the fact in the browser.

The ranking question is deliberately deferred:

```text
When population or policy options are selected, should # mean:

1. rank within the selected population/policy basis;
2. rank in the all-rikishi basis after filtering;
3. some other explicitly modelled record-position concept?
```

Do not implement Current/Former or fusen-control changes as simple UI label
tweaks until this question is classified for each Records artifact.

---

## Basis Versus Appearance

The useful distinction from the conversation:

```text
Appearance option
  Changes only how the selected result is displayed.
  Examples: hide/show columns, local sorting, collapse notes, chart scale.

Basis option
  Changes the analytical claim or the universe/policy under which it is made.
  Examples: Current vs Former, fusensho included/excluded, whole-career only.
```

Both kinds of controls may appear in the same visible `Options` panel, but they
belong to different architectural layers.

Basis options often belong upstream of the renderer. Appearance options often
belong to the runtime/view.

---

## Artifact Family Lens

The emerging organising concept is not intended as an implementation target yet.
It is a design lens for avoiding bad local moves.

Possible vocabulary:

```text
ArtifactFamily
  A parameterised public question.

Basis
  A selected vector of analytical parameters.

ArtifactInstance
  The concrete result of applying a Basis to an ArtifactFamily.

AppearanceState
  Presentation-only choices over an ArtifactInstance.
```

In shorthand:

```text
ArtifactInstance = ArtifactFamily(Basis)
RenderedView = render(ArtifactInstance, AppearanceState)
```

For example:

```text
ArtifactFamily:
  Most Career Wins

Basis:
  population = current
  fusensho = excluded

ArtifactInstance:
  ranked table of current rikishi by career wins excluding fusensho
```

The practical rule:

```text
Shared computational roots do not imply one public artifact.
Public artifact identity follows the public question and claim.
Basis variants instantiate a family of claims under the same public question.
Appearance variants do not change the claim.
```

This explains why Longest Careers was awkward inside Career Length. The charts
and Longest Careers share a computational root, but they are different public
artifacts.

---

## Structured Data GUT Restraint

The conversation circled a possible Grand Unified Theory of Structured Data,
similar to the earlier Grand Unified Theory of Tables pressure.

The agreed restraint:

```text
Use the theory as a design lens, not as a demand to implement a giant ontology.
```

For the immediate Records work, use the theory only as a checklist:

1. Does this control change the basis or just appearance?
2. If it changes the basis, does the staged data already contain the right
   basis-specific result?
3. If there is a `#` column, what basis is it ranked within?
4. Is the answer producer-owned, renderer-owned, or currently ambiguous?
5. Should this page be changed now, deferred, or documented as needing producer
   work?

Promote model concepts into code only when repeated implementation pressure
proves they are needed.

---

## Suggested Next Step

Before changing the five Records controls, inspect each artifact's producer
output and answer:

```text
Which basis variants already exist?
Which basis variants are merely browser projections?
What does # currently mean for each variant?
Can the producer produce basis-specific ranks without changing the public
artifact contract?
```

Then update the Records specifications before changing code.
