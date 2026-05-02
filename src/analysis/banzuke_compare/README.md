# Banzuke Change Report

The Banzuke Change Report publishes a static browser page for inspecting a new
banzuke against the previous basho.

The practical question it answers is:

> What changed on this banzuke, and how much context do I want while looking at it?

The tool is deliberately split into two parts:

- Python code loads the current banzuke, previous banzuke, previous basho
  results, and fixed v1 Equelo ratings, then publishes browser-ready CSV and
  JSON data.
- A static browser page loads the published data and lets the user switch
  division, layout, and optional explanatory columns.

The browser does not parse banzuke pages, read raw history, or compute Equelo
ratings.

## Current Product

The current public page supports:

- selecting a division
- showing or hiding previous-basho context
- switching between a traditional two-column banzuke layout and a one-column
  scan layout
- showing or hiding local movement delta
- showing or hiding fixed v1 Equelo ratings
- opening rikishi pages on SumoDB, with an alternate graph link on Alt-click
- shareable URL state for non-default options

The default view is intentionally simple and familiar:

- traditional east/west banzuke shape
- previous-basho context shown
- delta values hidden
- Equelo ratings hidden

The more analytical columns are available through explicit options.  This is a
deliberate progressive-disclosure design: a casual or first-time user should be
able to read the page as a recognisable banzuke, while a more demanding user can
turn on the gory details.

## Display Semantics

The two-column view uses a central `Rank` spine.  That value is a display rank
such as `M3`, derived from the full current `Chii` by removing the east/west
side while preserving annotations.

The one-column view uses `Chii`, because each row represents one rikishi in one
actual banzuke slot such as `M3e` or `M3w`.

Previous-basho context contains:

- previous chii, when the rikishi appeared on the previous banzuke
- previous final result and prizes, when available
- division-change arrows when the rikishi moved into the displayed division

Delta is a pair-local observed-slot movement metric.  It is useful for this
specific banzuke comparison, but it is not a historical rank-distance metric.

Equelo ratings are fixed v1 model values:

- existing rikishi use the latest completed fixed v1 day-end rating before the
  current banzuke date
- new unrated rikishi use the fixed v1 entrant rating implied by their current
  `Chii`

Ratings are displayed to the nearest integer.

## Architecture

The current architecture is a static publication pipeline.

1. Resolve the current banzuke date.
2. Load the current banzuke.
3. Load `History` and find the previous completed basho.
4. Build neutral banzuke-change facts keyed by `RikId`.
5. Derive browser-facing rows, previous-result context, local delta classes,
   graph shikona, and Equelo display ratings.
6. Write `data/banzuke_change_report.csv`.
7. Write `site_config.json`.
8. Copy the static HTML, CSS, JS, and shared layout files into the web root.

This keeps hosting simple.  The deployed page is static files plus precomputed
data.

## Main Files

- `banzuke_source.py` loads the publication source data.
- `banzuke_diff.py` compares current and previous banzuke.
- `report_view.py` turns neutral change facts into browser-facing rows.
- `equelo_ratings.py` adapts fixed v1 Equelo ratings for BCR display.
- `publisher_reports.py` writes the browser CSV and `site_config.json`.
- `publisher.py` orchestrates the static publication run.
- `deploy.py` copies static files and uploads the published page.
- `files/index.html` is the editable browser page shell.
- `files/banzuke_change_report.css` is the browser stylesheet.
- `files/banzuke_change_report.js.txt` is the browser behaviour layer.

## Published Data Contract

The browser expects:

- `site_config.json`
- `data/banzuke_change_report.csv`

The CSV is one row per displayed two-column banzuke row.  Each side has its own
fields:

- rikishi id
- full current chii
- shikona
- graph shikona
- previous chii
- previous result
- delta value
- delta class
- Equelo rating

The one-column browser view is derived from the same CSV by rendering the east
and west sides as separate rows.

## HTML As Template

The checked-in HTML is intentionally more than a disposable shell.  It is a
template that can be opened in a WYSIWYG editor and edited without running the
publisher.

That design choice constrains the implementation.  The browser JavaScript
updates the table shape at runtime, but the static HTML remains a meaningful
sample of the published page.  The one-column view currently reuses much of the
two-column table vocabulary and styling.  This is a pragmatic prototype: if the
one-column view becomes permanent, it deserves a cleaner first-class HTML/CSS
design rather than being treated as an implicit projection of the two-column
template.

## What This Is Not

The current product is not a full banzuke-news engine.  It does not currently
publish:

- separate entrants and exits sections
- career-high or return stories
- headline promotion/demotion summaries
- historical movement records
- prediction or expected-banzuke analysis
- arbitrary comparison between two selected banzuke

The current table is a useful first report over a broader banzuke-news problem.

## Running

Generate fixed v1 Equelo ratings first when they are stale:

```powershell
py -m src.analysis.equelo.fixed_v1
```

Then publish BCR:

```powershell
py -m src.analysis.banzuke_compare.publisher
```

Be careful with the publisher command: when `publisher.py` is run as a script,
it performs the publisher run and then invokes remote upload via `deploy.py`.
Remote deployment requires `MY_SFTP_PASS` to be set.

## Documentation Map

- `docs/Scoping Study.md` describes the wider banzuke-news problem.
- `docs/Banzuke Display Specification.md` specifies the original two-column
  enriched banzuke display.
- `docs/One Column Prototype.md` records why the one-column view currently
  reuses the two-column template/styling machinery.
- `src/analysis/equelo/fixed_v1/docs/Specification & Design.md` defines the
  fixed v1 rating artefacts consumed by BCR.
- `src/analysis/standings/docs/Requirements.md` is not a BCR requirement
  document, but it captures related product principles: simplicity first,
  progressive disclosure, trustworthy metrics, and honest explanations.

When docs and code appear to disagree, treat this README as the current product
map, `docs/Banzuke Display Specification.md` as the original display contract,
and the code as the best statement of current implementation detail.
