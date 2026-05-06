# Presentation Layer Direction

This note records the current target shape for the public-facing analysis
presentation layer.

The immediate goal is not to refactor code. The goal is to name the shape we
are aiming for, so that later refactoring has a product target rather than only
a DRY target.

---

# 1. The general shape

The proposed public surface is a single lab-style page shell:

```text
main title bar
main options | main content
```

The main title bar identifies the overall site, for example:

```text
Gaspode-san's Sumo Lab
```

The main options panel is the site-level navigation. It currently has two
headings:

```text
Tools
Sumo Facts
```

The main content panel initially shows a simple default page. This can be a
plain hello/introduction page rather than a marketing page.

When a main option is selected, the main content panel is replaced by the
selected tool/fact page. That inner page has the same general structure:

```text
page title bar
page options | page content
```

So, in the active state, the browser shows:

```text
main title bar
main options | page title bar
             | page options | page content
```

This means the presentation primitive is composable. A page can contain another
page-shaped object.

---

# 2. Page model

The useful abstraction is not merely "one HTML file".

The useful abstraction is a page-shaped component with:

* title bar
* optional options panel
* content panel

The outer site shell is one such page. Each selected tool or fact is another
such page embedded in the outer shell's content panel.

This suggests a future model along these lines:

```text
HTMLPage
  title
  options
  content

HTMLSite
  title
  navigation
  default_content
  pages
```

The exact class names do not matter yet. The important point is that the layout
grammar is recursive:

```text
title/options/content can contain title/options/content
```

---

# 3. Current main options

## Tools

These are operational tools: pages used to inspect or work with generated sumo
data.

Current candidates:

* Standings
* Banzuke Compare

These already exist as static browser tools with their own page structure and
deployment flow.

## Sumo Facts

These are public-facing exhibits: stable facts, charts, or arguments that are
useful to revisit or point other people to.

Current candidates:

* Finish by Chii
* Average Finish by Chii
* Banzuke Division by Era
* Makuuchi Rank by Era
* First Chii Appearance
* Observed Chii Matchup Probability Distribution

The first five mostly already exist as generated HTML pages, though some need
tidying. The observed chii matchup probability distribution is a desired page:
it should be built from observed chii-pair bout outcomes, not from model
probabilities.

---

# 4. Deliberately excluded for now

The following outputs are not currently first-pick public-facing pages:

* Persistence
* Equelo one-shot outputs
* Equelo fixed-v1 charts
* Expt3 model-predicted probability distribution

They may be useful internally, and some may become public later, but they do
not currently belong in the main public navigation.

If there is ever a public Equelo section, the Expt3 model-predicted probability
distribution can live there. For now it should not be confused with the
observed chii matchup probability distribution, which is the stronger public
fact.

---

# 5. Refactoring implication

The styling refactor should start from the shared page grammar:

```text
title bar
options panel
content panel
```

Then it can add common styling for:

* site navigation
* page options
* radio groups and similar controls
* tables
* Plotly chart containers

The current pages should be treated as existing instances of the same
presentation pattern, even if they were not originally built from a shared
component.

The desired result is not only less duplicated CSS. It is a consistent public
surface where future tools and facts can be added without inventing a new page
style each time.
