# HTML Artefact Inventory Note

This note records the current position on existing HTML artefacts under
`files/output`.

It distinguishes:

* current public-site artefacts;
* next incorporation targets;
* artefacts that exist but are not in scope in their current form;
* artefacts that are not in scope and will not be promoted.

In this note, **not in scope** means:

> this existing HTML artefact is not a public-site candidate and will not become
> one by direct incorporation.

If a related idea is later useful, it must be re-specified and reimplemented as
a new public-site producer output. The old HTML artefact itself remains out of
scope.

This note should be read alongside:

* `2026 05 06 The Site - Provisional Model and Stress Test.md`
* `../current/Producer Writers and Prototype Embeds.md`
* `docs/Project Map.md`

## 1. Current Public-Site Artefacts

These artefacts are already incorporated into `make_site`, either by copying
the existing HTML or by replacing the direct HTML incorporation with a
site-facing producer bundle.

### Banzuke and Rank Structure

```text
files/output/banzuke_division_era_chart.html
files/output/rank_era_chart.html
```

Current position:

* incorporated as public-site pages;
* currently copied as standalone HTML;
* may later be converted to producer-written site bundles if they need shared
  controls, theme, or options.

### Finish by Chii

```text
files/output/misc/finish_by_chii_1958_2026.html
```

Current position:

* incorporated as the current public `Finish by Chii` page;
* copied as standalone HTML for now;
* already has a coherent tool-style layout.

Slice-specific variants are not in scope; see section 4.

### Division Stability

```text
files/output/persistence/division_persistence (1958-2026, num_basho=10).html
```

Current position:

* incorporated as the current public `Division Stability` page;
* `num_basho=10` is the current chosen public value;
* this is the next target for applying the producer-writer policy.

The expected future direction is:

```text
producer emits site-facing persistence bundle
make_site renders a native Division Stability page
num_basho becomes an option
```

Other persistence HTML outputs are not in scope as direct pages; see section 4.

### Win Probability by Standing

Old standalone HTML artefacts:

```text
files/output/probability/matchups/observed_sideless_matchup_traces.html
files/output/probability/matchups/equelo_sideless_matchup_traces.html
```

Current position:

* initially incorporated through an iframe prototype;
* now superseded for public-site purposes by a producer-written site bundle;
* the old standalone HTML files remain analysis artefacts, not the site
  contract.

Current site-facing bundle:

```text
files/output/probability/matchups/site/win_probability_by_standing/page.json
files/output/probability/matchups/site/win_probability_by_standing/observed_trace_points.csv
files/output/probability/matchups/site/win_probability_by_standing/equelo_trace_points.csv
files/output/probability/matchups/site/win_probability_by_standing/metadata.json
```

Current position:

* incorporated as a native `chart_with_options` page;
* this is the first successful test of the additive producer-writer policy.

## 2. Next Target

### Division Persistence / Division Stability

Primary current HTML:

```text
files/output/persistence/division_persistence (1958-2026, num_basho=10).html
```

Next intended work:

* add a site-facing producer writer for persistence;
* render `Division Stability` through `make_site`;
* make `num_basho` an option;
* keep `num_basho=10` as the current/default public view unless a better
  default is specified.

The following HTML variants are not separate public pages:

```text
files/output/persistence/division_persistence (1958-2026, num_basho=1).html
files/output/persistence/division_persistence (1958-2026, num_basho=400).html
```

They may inform the option design, but they are not in scope as direct
artefacts.

## 3. Exists, But Not In Scope In Current Form

These outputs contain derived or human-facing material, but the existing HTML
artefact is not suitable for direct public-site incorporation.

If the idea becomes useful, it needs a new producer-written public-site output.

### First Appearance

```text
files/output/first_app.html
```

Current position:

* demoted;
* exists, but is not in scope in its current form.

Possible future idea:

* a re-specified rank-history or first-appearance exhibit.

### Fixed-v1 Entrant Initial Rating Charts

```text
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v0.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v1.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v2.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v3.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v4.html
files/output/Equelo/fixed_v1/charts/entrant_initial_ratings_v5.html
```

Current position:

* exists;
* interesting as part of the Equelo methodological story;
* not in scope in current form.

Possible future idea:

* an Equelo methodology page produced from a new site-facing writer, after the
  conceptual framing of ratings is settled.

## 4. Not In Scope

These artefacts are not public-site candidates and should not be incorporated
directly.

### Slice-Specific Finish by Chii Outputs

Examples:

```text
files/output/misc/finish_by_chii_1978_1980.html
```

Current position:

* not in scope;
* slice-specific date outputs are not public-site artefacts.

Date ranges may later become parameters for public pages, but these old
slice-specific HTML files are not the route to that feature.

### Non-Default Persistence HTML Variants

Examples:

```text
files/output/persistence/division_persistence (1958-2026, num_basho=1).html
files/output/persistence/division_persistence (1958-2026, num_basho=400).html
```

Current position:

* not in scope as direct artefacts;
* the public direction is a single Division Stability page with `num_basho` as
  an option.

### Expt3 Predicted Distribution

```text
files/output/Equelo/expt3_predicted_distribution.html
```

Current position:

* legacy;
* not in scope.

The conceptual issue is that this chart is a model/research artefact from an
earlier framing. It should not be promoted by direct incorporation.

### Equelo One-Shot Charts

Examples:

```text
files/output/Equelo (q unknown)/one_shot/runs/.../charts/*.html
```

Current position:

* legacy;
* not in scope.

### Division Churn

```text
files/output/division_churn.html
```

Current position:

* legacy;
* not in scope;
* superseded by Division Stability / division persistence for the current
  public-site purpose.

### Diagnostics

```text
files/output/banzuke warnings.html
files/output/file-format weirdness.html
```

Current position:

* not in scope;
* maintainer diagnostics, not public pages.

### Raw Downloaded HTML

Examples:

```text
files/output/HTML results/**/*.html
```

Current position:

* not in scope;
* source/archive material, not a public-site artefact.

### Old Current Standings HTML

Examples:

```text
files/output/current standings/*.html
```

Current position:

* not in scope;
* superseded by the current `Standings by Wins` tool.

## 5. Working Principle

Direct HTML incorporation is acceptable only for prototype stress tests or for
current pages whose standalone form is good enough for the present stage.

When an artefact is promoted toward a proper public page, the preferred path is
now:

```text
producer writes site-facing data/config/metadata
make_site renders the public page
```

The existing HTML file should not become the permanent API.
