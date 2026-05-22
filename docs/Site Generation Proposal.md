# Site Generation Proposal

## Purpose

This document proposes the technical approach for building the public-facing
sumo site once the list of public pages and their navigation structure has been
chosen.

The goal is to keep the public site simple to host while allowing the project
to generate rich static pages, datasets, charts, and browser tools from Python.

## Recommendation

Build the site as a static generated site.

The build process should run locally or in an offline job:

```text
Python analysis and site-generation code
  -> generated HTML, CSS, JavaScript, CSV, and JSON
  -> one deployable static site directory
  -> upload/copy to the web server
```

The public web server should only serve static files. It should not need
Python, Jinja, Flask, Django, Node, or a live application process.

## Build-Time Templating

Use Jinja2, or a similarly small Python template engine, at build time.

Jinja should not run on the web server. It should only turn templates and page
metadata into finished `.html` files during the site build.

For example:

```text
templates/shell.html
templates/page.html
site_map.py
analysis-generated data
```

become:

```text
build/public/index.html
build/public/current/standings/index.html
build/public/current/standings/data/*.csv
build/public/banzuke/changes/index.html
build/public/site.css
build/public/site.js
```

## Why Static Generation Fits

Static generation matches the shape of this project.

The heavy work is offline:

* scraping and parsing historical data
* generating canonical history
* computing standings
* comparing banzuke
* building charts and model outputs
* writing CSV and JSON data contracts

The public site should mainly present those outputs.

Static generation gives:

* simple hosting
* reproducible builds
* inspectable generated files
* low operational risk
* no live database requirement
* no server-side runtime dependency
* a natural fit with existing publisher code

It also keeps the project maintainable for a single maintainer.

## Proposed Project Shape

A future site layer could look like:

```text
src/site/
  build.py
  deploy.py
  site_map.py
  pages.py
  templates/
    shell.html
    page.html
  static/
    site.css
    site.js
```

The exact names can change. The important point is that there should be one
central site-generation layer responsible for assembling the public site.

Analysis packages should not each become independent mini-sites with unrelated
navigation, styling, and deployment assumptions.

## Site Map as Data

The public site should have an explicit site map.

That site map should describe:

* page id
* title
* route
* subject/navigation group
* depth, such as Basic, Advanced, or Research
* publication status
* builder function or source bundle
* required data files and assets

For example:

```python
Page(
    id="standings",
    title="Current Rolling Standings",
    route="current/standings/",
    subject="Current Sumo",
    depth=("Basic", "Advanced"),
    status="public",
    builder=build_standings_page,
)
```

This makes the public structure explicit instead of implicit in folder names or
ad hoc deploy scripts.

## Page Bundles

Each public analysis package should eventually produce a page bundle rather
than a complete standalone website.

A page bundle is the material needed by the central site builder:

```text
title and metadata
HTML fragment or template context
page-specific data files
page-specific JavaScript if needed
page-specific CSS only if truly needed
references to shared assets
```

The central site builder then places the bundle into the shared site shell.

This preserves the useful pattern already present in the project:

```text
Python computes static data
browser page presents and filters it
```

while avoiding fragmentation of the public surface.

## Page Types

The site can use light conventions for page types.

| Page Type | Purpose | Examples |
| --- | --- | --- |
| Tool page | Lets a user inspect or work with generated data. | Standings, Banzuke Change Report |
| Exhibit page | Presents a stable fact, chart, or table. | Banzuke structure over time, First chii appearance |
| Research page | Presents modelling, methodology, diagnostics, or unsettled interpretation. | Equelo, observed vs modelled outcomes, calibration |

These types do not need to become heavy abstractions immediately. They are
useful because they clarify expectations for layout, explanation, and public
readiness.

## Browser Interactivity

Use plain browser JavaScript where interactivity is needed.

Recommended defaults:

* shared plain CSS for the site shell
* plain JavaScript modules for page behavior
* CSV or JSON for generated datasets
* Plotly for interactive charts where it is already useful
* no bundler unless the project clearly outgrows plain static assets

This keeps the build simple and keeps generated output easy to inspect.

## Build and Deploy Separation

Build and deploy should be separate commands.

For example:

```text
python -m src.site.build
python -m src.site.deploy
```

The build command should generate the full static site into a local output
directory.

The deploy command should upload or copy that already-built directory to the
public web root.

This separation keeps two questions distinct:

```text
Can the site be built?
Can the built site be published?
```

## Possible Output Directory

A generated site might look like:

```text
build/public/
  index.html
  site.css
  site.js
  current/
    standings/
      index.html
      data/
        site_config.json
        *.csv
        *.json
  banzuke/
    changes/
      index.html
      data/
        banzuke_change_report.csv
  performance/
    finish-by-chii/
      index.html
  ratings-and-models/
    observed-vs-modelled/
      index.html
      data/
        *.csv
        *.json
```

The exact routes should follow the final Project Map. The important feature is
that there is one generated site tree ready to upload.

## Migration Direction

The existing publishers should not be replaced all at once.

A practical migration path is:

1. Create the site shell and site map.
2. Add placeholder pages for agreed navigation targets.
3. Integrate the current standings publisher as the first page bundle.
4. Integrate the Banzuke Change Report as the second page bundle.
5. Move selected misc charts into exhibit pages.
6. Add research pages only where the framing is clear.
7. Retire or simplify old standalone deploy paths once the central site build
   owns them.

This keeps the work product-led rather than refactor-led.

## Non-Goals

The initial public site generation system should not require:

* a live application server
* a database-backed public API
* server-side rendering at request time
* a Node or React build pipeline
* a heavy component framework
* dynamic user accounts or saved preferences

Those can be reconsidered later if the public product genuinely needs them.

## Governing Principle

The site generator should make the public surface coherent without hiding the
data-driven nature of the project.

In short:

> Generate static pages from explicit data, then serve them simply.

