# Server Implementation Notes

## 1. Purpose

These notes concern practical deployment of the standings presentation layer as a web site served from Apache environments.

The immediate objective is to publish the initial multiple-basho standings page on:

* a local PC running Apache
* an existing remote legacy server with limited space

The preferred approach is to keep both deployments functionally identical.

---

## 2. Chosen Delivery Model

The agreed model is a **static site with client-side interactivity**.

That means:

* Python standings code runs offline, not on the web server.
* Precomputed data files are generated separately.
* Apache serves static assets only.
* Browser-side JavaScript handles dropdown changes, sorting, filtering, and table redraw.

No CGI, WSGI, PHP, database, or server-side standings execution is required.

---

## 3. Publishing Workflow

Preferred verb: **publish**.

Typical workflow:

1. Run standings generation locally.
2. Produce/update data artefacts for supported `num_basho` values.
3. Copy HTML / CSS / JS / data files into Apache web root.
4. Repeat for remote host.
5. Refresh browser.

This may later be automated by script.

---

## 4. Supported Environments

The page should work the same way on both:

* Local Apache instance
* Remote Apache host

Because the site is static, deployment differences should be operational only (copying files, paths, permissions).

---

## 5. Data Format Direction

Current preference is to keep **CSV** as the served data format.

Reasons:

* already produced by existing standings pipeline
* huma-readable
* easy to inspect manually
* avoids maintaining duplicate CSV + JSON artefacts
* smaller operational footprint than parallel formats

JavaScript parsing of CSV is considered acceptable.

---

## 6. Size Considerations

Indicative current size:

* one CSV for one `N`: ~177 KB
* ten supported windows: ~1.8 MB total before compression

This is likely manageable even on a legacy host, especially if:

* gzip compression is enabled
* data files are cached by browser
* updates are infrequent

Bandwidth is not expected to be a major constraint.

---

## 7. Web Asset Layout (Illustrative)

```text
/standings/
    index.html
    standings.css
    standings.js
    /data/
        standings-1.csv
        standings-2.csv
        standings-3.csv
        ...
        standings-60.csv
```

---

## 8. Browser Behaviour

On page load:

* default `num_basho = 6`
* default division = Makuuchi
* load corresponding CSV
* render table sorted by Mean descending

When controls change:

* load another CSV if needed
* filter rows by division
* sort and redraw table

---

## 9. Dependencies

Minimal preferred stack:

* HTML
* CSS
* vanilla JavaScript
* Apache static hosting

No framework required initially.

---

## 10. Important Outstanding Issue

Before publicatio-quality release, standings identity semantics should be corrected so that displayed:

* shikona
* chii

are sourced from the **anchor basho**, not the latest selected basho in which the rikishi appeared.

---

## 11. TBD

* Exact Apache directory structure
* Whether gzip is configured on both hosts
* CSV file naming conventions
* Automated publish script
* Cache-busting/versioning approach
* Whether all CSVs load on demand or some are preloaded
* Final visual styling

