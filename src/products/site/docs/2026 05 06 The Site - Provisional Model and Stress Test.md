# The Site - Provisional Model and Stress Test

This note records the first practical stress test of the provisional public
site model.

It should be read alongside:

* `2026 05 03 Presentation Layer.md`
* `2026 05 05 Site Navigation Overview.md`

Those notes describe the desired shape and the broad navigation map. This note
records what happened when existing HTML artefacts from the current project
were tested against that map.

The code used for the test now lives in `src/products/site/old`, but that package is a
prototype only. It exists to test the information architecture and page-fitting
model. It is not intended to become the final site implementation.

## 1. Content Sources

There are three distinct sources of possible public-site content.

### A. Sumo-Tools

This is the current project.

It contains current analysis packages, current generated outputs, and the
emerging public-facing analysis layer.

This was the scope of the first stress test.

### B. Elo v. 9

This is the legacy site/project.

It is legacy, but still active as a source of ideas, product surfaces, and
historical prototype behaviour. It should not be treated as the current site,
but it remains an important content and design source.

### C. Ideas Not Yet Thought Of

The public site should not be limited to what either existing codebase already
generates.

Some future pages may emerge from later questions, later analysis, or better
ways of explaining existing results.

## 2. Relevance Axis

Possible content also has a relevance status relative to Sumo-Tools as a
public-facing entity.

### 1. Directly Relevant

These are current outputs or pages that already answer, or nearly answer, a
clear public-facing question.

They can plausibly sit in the public site with light framing or integration.

### 2. Could Be Relevant

These are outputs, experiments, or ideas that may become public-facing after
more framing, redesign, explanation, or methodological work.

They should be kept visible as candidates, but not forced into public
navigation just because they exist.

### 3. Not Relevant

These are diagnostic files, raw source artefacts, internal pipeline outputs, or
superseded experiments.

They may be important to the project but should not be treated as public-site
content.

## 3. Scope of This Test

The scope of this stress test was mostly **A1**:

```text
current project + directly relevant public-facing artefacts
```

There was a small amount of **A2**, where an artefact looked plausible enough
to include provisionally while acknowledging that its final public framing is
not settled.

The test deliberately did not attempt to integrate the legacy Elo v. 9 site,
except insofar as earlier docs had already imported some of its ideas into the
navigation map.

## 4. Organising Principle Tested

The test reinforced the current official line:

> The site should be organised by subject, not by user type.

Earlier thinking used a user-type axis: casual users, interested users, and
experts. That axis remains useful as a presentation concern, because some users
are number-phobic and should not be forced into dense tables and charts.

However, the navigation itself should be subject-led. Users can self-select by
choosing pages and by using page-level modes, explanations, filters, and
progressive disclosure.

For example, `Finish by Chii` might feel like an "expert" page, but it fits
naturally under:

```text
Performance > Rank Outcomes > Finish by Chii
```

The successful placement of that page was an important stress-test result.

## 5. Artefacts Included

The following existing Sumo-Tools HTML artefacts were incorporated into the
prototype site shell without changing their producer code.

### Current Sumo

```text
Current Sumo > Banzuke Changes
Current Sumo > Standings by Wins
```

These were already first-class browser tools.

### Performance

```text
Performance > Rank Outcomes > Finish by Chii
```

This uses the existing `finish_by_chii_1958_2026.html` output.

It fits because it answers a performance question:

> What results have rikishi at a given chii historically produced?

### Banzuke & Rank

```text
Banzuke & Rank > Banzuke Structure Over Time > Banzuke Division by Era
Banzuke & Rank > Makuuchi Structure > Makuuchi Rank by Era
Banzuke & Rank > Division Movement > Division Stability
```

`Division Stability` currently uses the persistence chart:

```text
division_persistence (1958-2026, num_basho=10).html
```

This supersedes the older `division_churn.html` chart for this purpose.

The `num_basho=10` choice is brittle and should later be replaced by either a
deliberate fixed public default or a control/dropdown.

### Ratings & Models

```text
Ratings & Models > Observed vs Modelled > Win Probability by Standing > Observed
Ratings & Models > Observed vs Modelled > Win Probability by Standing > Equelo
```

The title "Win Probability by Standing" was chosen because "matchups" names
the data relationship rather than the delivered result.

"Standing" is used here as the common axis that can cover both chii and model
rating. "Rank" was avoided because it is heavily overloaded in sumo.

## 6. Artefacts Excluded

### `division_churn.html`

This is treated as legacy and superseded for the present purpose by division
persistence.

"Churn" also suggested entry/exit movement, whereas the preferred public
concept here is continuity or stability.

### `first_app.html`

This is a legacy/historical exhibit candidate but was not needed in the first
stress test.

It may become relevant later, but it is not currently a strong public-page
candidate.

### `current standings/*.html`

These are old per-basho/current-standings HTML files and are treated as
diagnostic or superseded by the current standings tool.

### `banzuke warnings.html` and related warning/weirdness pages

These are diagnostic outputs.

They are useful to the project, but they are not public navigation.

### `HTML results`

This directory contains raw or near-raw source data.

It should not be public-site content.

### Equelo experiment charts

The Equelo charts are important, but not because they are ready-made public
chart pages.

They tell the story of moving from an epistemological, iron-man position:

```text
This is what the data says.
```

to a teleological, pragmatic position:

```text
The numbers should be forced into a shape that makes sense for the model.
```

In particular, the fixed/monotonic Equelo work may eventually support a
published methodology narrative.

That story may belong under `Ratings & Models > Methodology`, or under a more
research-oriented section such as `Ratings & Models > Research Archive`. The
placement is not settled.

## 7. Theme and Presentation Findings

Not all included charts use the same dark theme or page grammar.

For the prototype, this is acceptable. The point was to test whether the pages
fit the navigation and conceptual model, not whether they already look like a
single polished site.

For the final site, this becomes a design requirement:

* either pages must conform to a shared public theme,
* or legacy/research pages must be clearly framed as less-polished artefacts.

## 8. Implementation Finding

Simple copying of existing HTML artefacts into a site output tree was
sufficient for this prototype.

This is useful information, but it should not be overinterpreted. The
`src/products/site/old` package is disposable. The important result is not the
copying mechanism itself, but the fact that the current artefacts can be
assembled into a coherent subject-led navigation without changing their
producer code.

The prototype rule going forward is:

* the site prototype may copy, iframe, wrap, list, and stress-test existing
  artefacts;
* it should not require changes to the packages that produce those artefacts;
* if an artefact does not fit, that is a finding about the future site design
  or future producer contract, not a reason to patch the producer during the
  prototype pass.

## 9. Outcome

The first stress test passed.

The current worthwhile HTML artefacts from Sumo-Tools found natural homes in a
subject-led navigation model.

No new "expert section" or awkward catch-all category was required.

The main remaining issues are presentation polish, shared theme, final page
contracts, and the later integration of legacy Elo v. 9 ideas and future
content not yet imagined.
