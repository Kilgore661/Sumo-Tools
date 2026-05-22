# Site Definition Handoff Memo

This memo records where the site-modelling discussion paused.

It covers the discussion after the question about testing the classes by
choosing values for the "initial state".

## 1. Terminology Correction

The phrase "initial state" was rejected for this purpose.

The better term is:

```text
site definition
```

Reason:

* **site definition** = static intended structure of the public site;
* **UI state** = current runtime/user selections such as selected division,
  selected source, visible traces;
* **build config** = where/how the site is generated and deployed.

The next task is to instantiate a provisional `Site` value, not to model
runtime UI state.

## 2. Existing Data Classes

The provisional classes now live under:

```text
src/products/site/classes/
```

The package is split into three coarse modules:

```text
file_refs.py
  AssetRef
  DataRef
  ViewRef

page_parts.py
  OptionsModel
  OptionSpec
  OptionValue
  OptionKind
  ViewSpec
  StandaloneHtmlView
  HtmlFragmentView
  PlotlyJsonView
  TableAppView
  EssayView
  CustomView

site_model.py
  Site
  SiteBuildConfig
  NavigationTree
  PageRegistry
  Page
```

The classes compiled and exported successfully.

## 3. Chosen Modelling Direction

The first concrete site definition should probably be a Python assignment, not
a config file.

The likely file is:

```text
src/products/site/site_definition.py
```

The reason is that we are still testing whether the algebraic sorts are right.
A config format would add a second problem: parsing, conversion, and
validation.

The site definition can later move to JSON/YAML/TOML or page-bundle manifests
if that becomes useful.

## 4. Provisional Site Values

The suggested site values were:

```text
site id: sumo_lab
site title: Gaspode-san's Sumo Lab
root navigation id: root
root navigation label: Root
root navigation slug: ""
```

The title should include `Gaspode-san's` as the author's one deliberate
concession to marketing/personality.

Likely page ids:

```text
banzuke_changes
standings_by_wins
finish_by_chii
banzuke_division_by_era
makuuchi_rank_by_era
division_stability
win_probability_by_standing
```

## 5. Important Rule: Canonical Model First

The site definition should describe the intended real site model, not the
current disposable prototype.

This matters because the prototype currently uses copied standalone HTML files
and iframe-style incorporation. That may be useful as implementation evidence,
but it must not become the canonical truth.

The agreed rule:

> The site definition is authoritative. Existing artefacts may be used to
> implement it only when they conform to the definition. Compatibility hacks
> are exceptional, local, and temporary.

Reuse is welcome if it falls out naturally.

It is not acceptable to distort the public model merely because an existing
HTML file happens to be convenient.

## 6. Win Probability by Standing

This was the key example.

The prototype currently has two copied pages:

```text
Observed
Equelo
```

But the intended real site model should not treat these as separate navigation
pages.

The intended model is one page:

```text
Ratings & Models
  Observed vs Modelled
    Win Probability by Standing
```

with an option:

```text
source = Observed | Equelo | Combined
```

The future `Combined` option is important, so the page should be modelled as:

```text
Page(
  id="win_probability_by_standing",
  options=OptionsModel(... source ...),
  view=CustomView(kind="standing_win_probability")
)
```

or an equivalent design-conformant view.

It should not be modelled as:

```text
Win Probability by Standing > Observed
Win Probability by Standing > Equelo
```

even though that was useful in the disposable prototype.

## 7. Provisional View Choices

For pages where current artefacts already match the intended public page shape,
`StandaloneHtmlView` may be acceptable provisionally.

Examples may include:

```text
Finish by Chii
Banzuke Division by Era
Makuuchi Rank by Era
Division Stability
```

For pages where the intended public model differs from the current artefacts,
use a design-conformant view such as `CustomView`.

This identifies missing renderer/plumbing work without lying about the page
model.

## 8. Next Step

Next likely task:

```text
Create src/products/site/site_definition.py
```

It should instantiate:

```text
SITE = Site(...)
BUILD_CONFIG = SiteBuildConfig(...)
```

using the intended public model.

When in doubt, prefer the truthful future model over the currently working
prototype shape.
