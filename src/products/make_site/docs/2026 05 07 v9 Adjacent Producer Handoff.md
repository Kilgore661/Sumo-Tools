# v9 Adjacent Producer Handoff

This note is the starting point for a future conversation whose task is to
inspect Elo v.9 and decide which legacy ideas should be reimplemented for
Sumo-Tools.

It exists because v9 is large, prototype-shaped, and model-adjacent rather than
model-identical. A future pass through v9 should not begin by trying to
understand every file. It should begin with the Sumo-Tools public-site contract
and ask which v9 artefacts are worth paying the migration cost for.

Related notes:

* `docs/Elo v.9 Site Overview.md`
* `2026 05 06 Public Site Requirements.md`
* `2026 05 06 Public Site Specification.md`
* `2026 05 06 Producer Writers and Prototype Embeds.md`
* `2026 05 06 HTML Artefact Inventory Note.md`
* `2026 05 06 TBD Register.md`

## 1. Current Documentation Assessment

The existing documentation is good enough to explain the current public-site
direction, but it is not quite sharp enough as the sole preamble to a v9 code
inspection.

The useful existing facts are:

* the site is subject-led, not user-type-led;
* public pages are curated exhibits, not a dump of everything that renders in a
  browser;
* legacy v9 material may be product-relevant;
* B1 v9 deliverables should be reimplemented under Sumo-Tools rather than
  permanently copied as old v9 HTML;
* the preferred integration path is an additive producer writer that emits
  site-facing data/config/metadata;
* direct HTML incorporation is acceptable for prototypes and stress tests, but
  is not the desired final contract.

What was missing was a compact intake checklist for a future v9-focused pass:

* what question must be answered before reading code;
* what counts as a deliverable candidate;
* what a v9-adjacent producer must emit;
* what should not be preserved;
* how to handle the fact that the v9 model is not exactly the Sumo-Tools model.

This note supplies that missing bridge.

## 2. Terminology

`v9 artefact`

An existing v9 page, chart, table, route, script output, or product idea.

`v9-adjacent code`

New or modified Sumo-Tools code that reproduces, adapts, or supersedes a v9
idea while satisfying Sumo-Tools contracts.

`B1 candidate`

A v9 idea that appears directly relevant to Sumo-Tools as a public-facing
entity.

`producer`

The package/module that computes the facts for a public page.

`site-facing writer`

An additive writer owned by a producer. It emits intentional inputs for
`make_site`; it does not ask `make_site` to reverse-engineer old HTML.

`page bundle`

The site-facing inputs for one public page or page family. The exact file
format is not final, but the required information is known.

## 3. Migration Principle

For v9 B1 material, the default rule is:

```text
do not import the old v9 page;
do not treat old v9 HTML as an API;
do not preserve v9 implementation shape merely because it exists;

instead:
  identify the public question;
  identify the useful v9 idea/computation/presentation;
  re-specify it for Sumo-Tools;
  implement or adapt a Sumo-Tools producer;
  emit a Sumo-Tools site-facing bundle;
  let make_site render the public page.
```

The old v9 page may be used as:

* evidence of a useful product idea;
* a behavioural reference;
* a data-lineage clue;
* wording to rewrite;
* a comparison output while reimplementing;
* an example of what not to carry forward.

It should not be the permanent delivered artefact.

## 4. First Question for Every Candidate

Every candidate must begin with a public question.

Examples:

* How strong is this rikishi, compared with his banzuke rank?
* What happened to this rikishi over his career?
* Which current rikishi are unusually interesting by rating or expected wins?
* Does the rating system behave sensibly against rank/chii?
* Is the rating population drifting over time?
* What does the sumo population look like over history?
* How long do careers last, and where do they end?

If the candidate cannot be tied to a public question, it is not a B1 candidate.

It may still be:

* an internal diagnostic;
* a methodology note;
* a possible future idea;
* a code archaeology clue.

But it should not be imported into public navigation.

## 5. Candidate Intake Checklist

For each v9 artefact, record:

```text
candidate id:
v9 route/file/function:
public question:
subject/navigation home:
current v9 model assumptions:
Sumo-Tools model equivalent:
data lineage:
minimum public output:
required page options:
required caveats:
must preserve:
must change:
must discard:
migration cost:
recommendation:
```

`recommendation` should be one of:

```text
B1 reimplement now
B1 reimplement later
B2 keep as candidate
methodology/reference only
internal/diagnostic only
not relevant
```

This is intentionally product-first. Do not start by asking "can we run this
script?" Start by asking "what public page would this become?"

## 6. Required Site-Facing Output

A v9-adjacent producer that is promoted to Sumo-Tools must emit enough for
`make_site` to render the page without private v9 knowledge.

For each public page or page family, the producer should provide:

```text
page metadata:
  stable page id
  public title
  short summary
  page status/readiness, when needed

navigation proposal:
  subject-led placement
  preferred label
  note of any competing placement

view contract:
  view type
  required renderer behaviour
  whether this is a chart, table, essay, tool, or custom page

options model:
  page state, not widgets
  exact-one choices
  zero-or-more choices
  booleans
  numeric/date/range parameters, if any
  defaults

data files:
  machine-readable data needed by the view
  stable column names or JSON keys
  documented units and domains
  support/sample-size fields where interpretation needs them

configuration:
  axis labels
  ordering rules
  curated domains
  default visible traces/rows
  display policy that belongs to the page contract

metadata/provenance:
  input data sources
  date range
  model version
  major assumptions
  known caveats
```

The producer may continue to emit legacy/debug/diagnostic outputs separately.
The site-facing writer is additive.

## 7. What make_site Should Own

`make_site` owns:

* public routes derived from the navigation tree;
* the site shell;
* shared navigation;
* shared CSS and JavaScript;
* common page layout;
* copying declared assets/data;
* rendering known view types from producer contracts;
* local and remote deployment mechanics.

`make_site` should not own:

* v9-specific data archaeology;
* rating calculations;
* table-specific business logic;
* chart-specific statistical calculations;
* parsing legacy generated HTML for meaning.

## 8. Model Mismatch Rule

v9 uses a model that is not exactly the current Sumo-Tools model.

Therefore a v9 artefact must not be migrated by assuming that an old Elo value,
old probability value, or old table column has the same meaning in the new
site.

For every rating/model candidate, explicitly classify the relationship:

```text
same concept, same computation
same concept, different computation
similar concept, needs redefinition
legacy-only concept, methodology reference
broken/known-bad concept, do not reuse
```

Examples from the existing notes:

* `Delta Chii` must be audited before reuse because the old site itself says it
  was broken.
* v9 Elo/rating explanations may remain useful even if the final model is
  Equelo.
* v9 model diagnostics may become Equelo diagnostics only after the public
  question and computation are re-specified.

## 9. Likely B1 Candidate Families

These are not approvals. They are the obvious first places to inspect because
the existing v9 overview says they answer public questions.

### Current Tables and Leaderboards

Possible public questions:

* Who is interesting right now?
* How do current records compare with rating expectations?
* Which rikishi have notable rating or expected-win positions?

Likely v9 sources:

* latest Elo table;
* date navigation;
* max average wins;
* max Elo/probability pages.

Special cautions:

* do not preserve dense v9 table shape uncritically;
* audit `Delta Chii`;
* identify which columns are public essentials and which are analyst-only;
* map old Elo-derived quantities to current Sumo-Tools equivalents.

### Individual Rikishi Trajectory

Possible public questions:

* What happened to this rikishi over his career?
* How did rank/chii and rating move together?

Likely v9 sources:

* rank/chii over calendar time;
* rank/chii by basho count;
* Elo over calendar time;
* Elo vs Chii for selected rikishi;
* daily Elo movement;
* desired combined Chii + Elo chart.

Special cautions:

* the combined chart is a successor idea, not necessarily a v9 artefact;
* shikona linking/navigation behaviour is a UI idea, not a data contract;
* rating semantics must be updated for Equelo or clearly labelled.

### Rating vs Rank Calibration

Possible public questions:

* Does the rating system make sense against the banzuke?
* How does rating strength relate to rank/chii?

Likely v9 sources:

* Elo vs Chii;
* intro Elo table/chart;
* mean Elo by Chii;
* mean expected wins by Chii;
* mean probability-derived values by Chii.

Special cautions:

* this family is highly model-sensitive;
* old charts may be methodology reference rather than direct deliverables;
* current Sumo-Tools already has observed-vs-modelled matchup work that may
  supply a stronger framing.

### Model Diagnostics

Possible public questions:

* Is the model drifting?
* Is the rating population behaving sensibly over time?
* Are the estimators stable or interpretable?

Likely v9 sources:

* inflation by rank/chii;
* rating distributions;
* estimators;
* mean rating vs banzuke size.

Special cautions:

* diagnostics are often B2 rather than B1;
* public framing must explain why the reader should care;
* direct migration is unsafe unless the current model has the same diagnostic
  meaning.

### Population and Banzuke Structure

Possible public questions:

* What does the sumo population look like over time?
* How have division sizes changed?

Likely v9 sources:

* division size charts;
* mean rating vs banzuke size.

Special cautions:

* Sumo-Tools already has banzuke/rank era and division persistence pages;
* avoid duplicating existing public pages unless the v9 artefact adds a
  distinct question.

### Career Lifecycle

Possible public questions:

* How long do careers last?
* Where do careers tend to end?

Likely v9 sources:

* career length count;
* career length probability;
* cumulative career length probability;
* rank at retirement.

Special cautions:

* retirement/intai ambiguity must be made explicit;
* old v9 chart grammar is unlikely to be final public presentation.

### Explanatory Pages

Possible public questions:

* What is this model trying to measure?
* Why use ratings beside banzuke rank?
* What assumptions and caveats matter?

Likely v9 sources:

* What is Elo;
* BKQ/model explanation;
* table notes.

Special cautions:

* wording should be rewritten for Equelo/Sumo-Tools;
* old v9 explanations are source material, not final docs.

## 10. Exclusion Rules

Do not migrate a v9 artefact merely because:

* it exists;
* it is HTML;
* it was linked from the old site;
* it looks interesting in isolation;
* it is easy to copy;
* it would be painful to delete from memory.

Exclude or demote candidates that are:

* raw source snapshots;
* parser diagnostics;
* warning/weirdness reports;
* broken known-bad calculations;
* superseded experiments;
* pages whose only public value is "this existed in v9";
* model-specific outputs whose meaning does not survive the move to
  Sumo-Tools.

## 11. Minimum Deliverable for the Next v9 Conversation

The next conversation should not try to reimplement everything.

The minimum useful deliverable is:

```text
ranked list of v9 B1/B2 candidates
  grouped by public question and subject home
  with source files/routes/functions identified
  with model mismatch risks noted
  with recommended Sumo-Tools producer contract for each B1 item
```

Only after that should code migration begin.

For each approved B1 item, the implementation task becomes:

```text
create or extend a Sumo-Tools producer
write existing outputs if still useful
write site-facing bundle
add page to make_site site definition
render with existing or new view type
document caveats and model semantics
```

## 12. Working Stance

The point of reading v9 is not to preserve v9.

The point is to discover which v9 product ideas still answer good public
questions, then make those ideas native to Sumo-Tools.

If reproducing a v9 artefact requires essentially rewriting it, that is not a
failure. It simply means the public question is valuable but the prototype
implementation is not the deliverable.

