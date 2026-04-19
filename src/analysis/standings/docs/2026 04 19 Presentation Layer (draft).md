# Presentation Layer Position Document

## 1. Status and Prematurity

It should be acknowledged at the outset that this work is, in one sense, premature.

The standings calculation capability is still evolving, and the presentation layer cannot yet be considered a fully constrained downstream requirement because the final data contract is not yet settled.

In particular:

* identity semantics for displayed `shikona` and `chii` remain to be corrected
* exact output artefacts are not yet frozen
* some standings metrics may still evolve
* publication workflow is not yet automated

However, this does **not** make exploratory design work wasteful.

There is practical value in thinking through the presentation layer in advance in order to identify architectural traps and usability issues before implementation hardens.

Examples of useful early discoveries include:

* the desirability of a static-site model rather than server-side execution
* the need for a visible editable template rather than a JS-only shell
* the importance of preserving graceful behaviour when data is unavailable
* layout behaviour when content exceeds viewport height
* layout behaviour when width becomes constrained
* sensible defaults for controls and sorting

Accordingly, this document records what is currently understood about the intended presentation layer and why the chosen direction is sound in principle.

---

## 2. Purpose of the Presentation Layer

The standings capability shall support a presentation-oriented layer whose initial form is a browser-based HTML page presenting multiple-basho standings in a simple and accessible form.

The initial target audience is not users seeking advanced statistical interpretation, but users who want obvious headline standings numbers in a clean and navigable table.

This layer is intentionally narrower than the full analytical outputs already produced by the standings engine.

It is intended to provide:

* an immediately readable standings table
* quick switching between basho-window lengths
* quick switching between divisions
* sortable columns
* desktop-oriented usability
* stable visual presentation

---

## 3. Scope of Initial View

The initial page concerns standings equivalent in concept to:

```text
py -m src.analysis.standings.multiple_basho_main --num-basho N
```

with backwards-looking semantics relative to the current default anchor date unless another anchor date is selected upstream.

The page itself is not responsible for computing standings.

The standings engine computes data elsewhere. The page consumes published outputs.

---

## 4. Core Architectural Decision

The agreed delivery model is:

## Static site with client-side interactivity

Meaning:

* Python standings code runs offline, not on the web server
* precomputed data files are generated separately
* Apache serves static assets only
* browser-side JavaScript handles controls, filtering, sorting, and redraw

No CGI, WSGI, PHP, database, or server-side standings execution is required.

This model is appropriate because the application is fundamentally:

* read-mostly
* data-table oriented
* modestly interactive
* not dependent on per-user server state
* suitable for periodic republising rather than live transaction processing

---

## 5. Why This Architecture Works

## 5.1 Separation of Responsibilities

The architecture separates concerns cleanly:

### Standings engine

Responsible for:

* correctness of rankings
* metric calculations
* generation of outputs

### Publication process

Responsible for:

* generating supported data files
* copying files to hosting locations

### Browser page

Responsible for:

* rendering
* sorting
* filtering
* interaction

This avoids mixing calculation logic with page logic.

## 5.2 Operational Simplicity

Static hosting works on:

* local Apache server
* remote legacy Apache server

with minimal differences beyond copying files and path management.

## 5.3 Robustness

If JavaScript fails or data is unavailable, the page can still remain a page rather than collapsing into nothing.

## 5.4 Low Cost

No runtime server compute is required.

No database is required.

No application server is required.

---

## 6. Template-First Decision

A key design issue explored during planning was whether the site should become a JavaScript-generated shell with no meaningful editable HTML template.

That direction was rejected.

The preferred model is:

## HTML page as real template, enhanced by JavaScript

Meaning:

* the HTML file is a visible page in its own right
* it contains the real layout
* it contains the real headings
* it contains representative demo rows
* JavaScript optionally upgrades it with live data

This preserves the practical advantages of template-based web development:

* tangible editable page source
* compatibility with visual HTML editing tools
* direct inspection in browser
* graceful fallback behaviour
* easier maintenance

This avoids the failure mode where the HTML file is merely an empty vessel awaiting JS reconstruction.

---

## 7. JavaScript Role

JavaScript is therefore treated as a **helper layer**, not the generator of the universe.

On page load:

1. Browser loads HTML template.
2. Browser loads CSS.
3. Browser loads JavaScript helper file.
4. JS decides whether live data is available.
5. If yes, it loads data and replaces dynamic regions.
6. If no, it exits quietly and leaves template content visible.

This is progressive enhancement.

The page exists before JS runs.

JS improves it.

---

## 8. Why Template + Helper JS Is Preferable Here

For this project specifically:

* columns are known in advance
* layout is stable
* interactivity is modest
* data changes periodically, not continuously
* inspectable files are desirable
* maintainability matters more than fashionable tooling

Accordingly, HTML + CSS + modest JS is better suited than a framework-heavy model.

---

## 9. Visual Layout Direction

A prototype page (`two_panel_layout_prototype.html`) has already validated the broad layout.

## 9.1 Desktop-Oriented Layout

The target device is desktop/laptop rather than phone.

The intended browser window shape is approximately A4 portrait: moderate width and as tall as the screen permits.

## 9.2 Overall Structure

The page consists of:

* title bar across top
* left sidebar panel
* right content panel

## 9.3 Sidebar

The sidebar is only as wide as needed to contain its controls.

## 9.4 Content Panel

The content panel fills remaining width.

## 9.5 Scrolling Behaviour

If content exceeds screen height:

* page scrolls normally

Both sidebar and content styling continue for full content height.

This avoids the common defect where a coloured sidebar ends prematurely.

## 9.6 Width Constraint Behaviour

If browser width becomes too narrow:

* two-column layout remains
* browser horizontal scrollbar appears if needed

The content should not collapse underneath the sidebar.

---

## 10. Initial Controls

The page shall provide a **num_basho** selector.

Supported values:

* 1
* 2
* 3
* 4
* 5
* 6 (default)
* 12
* 18
* 24
* 36
* 60

The page shall provide a **division** selector.

Supported values:

* All
* Makuuchi (default)
* Juryo
* Makushita
* Sandanme
* Jonidan
* Jonokuchi

---

## 11. Table Structure

Visible columns:

* blank row-number column
* Shikona
* Chii
* Wins
* Count
* Mean

Column meanings:

* Row Number = display row count after current filter/sort
* Shikona = anchor-basho shikona
* Chii = anchor-basho chii string
* Wins = `all_wins`
* Count = `bout_count`
* Mean = `window_average_all_wins`

---

## 12. Sorting Behaviour

Default sort:

* Mean descending

Clickable headings:

* Shikona
* Chii
* Wins
* Count
* Mean

Chii sorting uses ordinal value, while displaying string value.

Default Chii sort direction:

* ascending

Other default numeric sort directions:

* descending

Secondary sort keys remain undecided.

---

## 13. Division Logic

Division filtering shall be derived from `chii_ordinal`.

Using:

* `0..4` → Makuuchi
* `5` → Juryo
* `6` → Makushita
* `7` → Sandanme
* `8` → Jonidan
* `9` → Jonokuchi

where the value is:

```text
ordinal // 100000
```

---

## 14. Data Supply Model

Current preference is to serve CSV.

Reasons:

* already produced by standings pipeline
* human-readable
* easy to inspect manually
* avoids maintaining CSV + JSON in parallel
* adequate size characteristics

Indicative current sizes:

* one CSV for one N ≈ 177 KB
* ten windows ≈ 1.8 MB before compression

This is acceptable even for a modest legacy host, especially with gzip and browser caching.

JavaScript parsing CSV is considered acceptable.

---

## 15. File Layout (Illustrative)

```text
/standings/
    index.html
    standings.css
    standings.js
    /data/
        standings-1.csv
        standings-2.csv
        ...
        standings-60.csv
```

---

## 16. CSS / JS Relationship

CSS and JavaScript are not directly bound to one another.

Both operate against the HTML / DOM.

Meaning:

* HTML defines structure
* CSS styles matching elements
* JS updates matching elements

This allows:

* style redesign without rewriting data logic
* JS replacement of demo rows with live rows
* reuse of same styles for static and dynamic content

The shared naming contract (IDs, classes) should be kept small and stable.

---

## 17. Why Demo Rows Matter

A blank dynamic table body is technically acceptable but poor for design work.

Therefore the preferred template contains representative demo rows.

Benefits:

* visible page when opened directly
* styling experiments immediately visible
* no-data fallback
* easier visual iteration

When live data loads successfully, JS replaces the demo rows.

---

## 18. Supported Hosting Environments

The page should work identically on:

* local Apache installation
* remote Apache server

Differences should be operational only:

* copying files
* directory paths
* permissions
* compression configuration

---

## 19. Publication Workflow

Preferred verb: **publish**

Typical process:

1. Run standings generation locally.
2. Produce/update CSV artefacts.
3. Copy HTML/CSS/JS/data files to local host.
4. Copy same files to remote host.
5. Refresh browser.

This can later be scripted.

---

## 20. Important Outstanding Domain Issue

Before production release, standings identity semantics should be corrected.

Displayed:

* shikona
* chii

must come from the **anchor basho**, not from the most recent selected basho in which the rikishi happened to appear.

This is a data issue, not a page issue, but materially affects correctness of presentation.

---

## 21. What Is Still TBD

* automated publish script
* exact directory conventions
* cache-busting/versioning approach
* whether data files load lazily or eagerly
* final visual styling refinements
* broader metrics beyond obvious numbers
* secondary sort policy
* final wording of labels
* anchor-date selection controls, if any

---

## 22. Final Position

Although the presentation layer is not yet driven by a fully frozen data contract, the exploratory work has been worthwhile.

It has already established that a coherent and low-risk solution exists:

* static hosting
* editable HTML template
* CSS-driven presentation
* JavaScript helper enhancement
* precomputed CSV data
* desktop-first table interface

This direction avoids unnecessary complexity while preserving future growth.

Most importantly, it preserves a real page that can be inspected, edited, published, and understood.

