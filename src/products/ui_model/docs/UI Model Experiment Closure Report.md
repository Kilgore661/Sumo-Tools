# make_site2 UI Model Experiment: Closure Report

## Status

This document closes the make_site2 UI Model experiment.

The experiment produced a working model and prototype renderer for a representative set of public-site pages. It did not produce a full replacement for `make_site`. In particular, make_site2 currently assembles existing generated artefacts; it does not yet own the upstream data build pipeline, live-store/zip history selection, production cache policy, or full deployment/cutover process.

The next phase should therefore be an incremental migration of `make_site` itself, using the UI Model proven here.

## Governing Principle

The central purpose of make_site2 was to formalise public-page structure before rendering it.

A new UI feature should not begin as a local HTML/CSS/JS patch to one page. It should begin by asking whether the desired structure is already expressible as an instance of an existing grammar. If it is, the shared renderer should be extended or corrected. If it is not, the grammar should be modified or a new grammar should be introduced.

Page-specific renderers are still allowed, but only inside an established structural slot, such as the renderer for a particular chart or table artefact. They should not redefine the surrounding page structure.

This rule exists for two reasons. First, rendering should flow from the parsed structure of the data that is to be published, so that the model explains what the user sees. Second, shared structural behaviour should not be reimplemented repeatedly in bespoke page code, because that leads to CSS and JavaScript drift.

## Original Aim

make_site2 was created to test whether the public site could be rendered from a small number of formal UI grammars rather than from a miscellany of bespoke page shells.

The key questions were:

- Can existing public pages be represented as instances of known structural grammars?
- Can rendering flow from the parsed structure rather than from page-specific shell code?
- Can iframe-based rendering, `TableAppView`, and `StandaloneHtmlView` be avoided for migrated pages?
- Can existing PA manifests be reused as the source of artefact-level truth?
- When a page looks wrong, can we diagnose the problem as a modelling/parsing problem rather than simply patching the HTML or CSS?

The experiment succeeded on these questions for the selected case studies.

## Current Model Vocabulary

The current model distinguishes these conceptual entities:

- `NavigationBar`: the persistent site navigation area, including caption, navigation tree, and collapse capability.
- `ContentPanel`: the selected page area, containing heading, contents, filters, artefacts, and notes.
- `Contents`: the structural body of a page.
- `FilterSection`: one or more controls that select or constrain content.
- `PA`: the selected published analytical artefact.
- `Artifact`: the concrete chart, table, indexed table, or similar display object inside a PA.
- `Note`: explanatory text associated with the page, selected branch, filter state, or artefact.

The renderer may place DOM elements differently from their conceptual ownership. For example, the `NavigationBar` hider logically belongs to the navigation bar, but is physically rendered as an outer-layout control so that it remains available when the navigation panel is hidden.

## Final Grammar Set

The experiment now needs only two live grammar shapes.

### G1: Single Visible Artefact

G1 describes pages whose content consists of one visible PA/artifact, optionally controlled by filters and accompanied by notes.

In outline:

```text
ContentPanel -> Heading . Contents
Contents -> FilterSection . PA . Note*
PA -> Artifact
```

Most migrated pages are G1 pages.

### G2: Selected Alternative

G2 describes pages where a selector chooses between alternative branches, and only the selected branch contributes a visible PA/artifact.

In outline:

```text
ContentPanel -> Heading . Contents
Contents -> BranchSelector . Branch+ . Note*
Branch -> FilterSection . PA
PA -> Artifact
```

The important point is that G2 does not mean multiple simultaneous artefacts. It means one visible alternative chosen from a structured set.

Historical breadcrumb: earlier notes used `G2` for a simultaneous-multiple-PA candidate, then refined that through `G2b`. In this report, `G2` means the final selected-alternative grammar. The older candidate names are retained only as audit history in the archived working notes.

## Case Studies

The experiment migrated these cases:

| Nav item | Page id | Grammar | Artefact |
| --- | --- | --- | --- |
| 2.1 Banzuke Changes | `banzuke_changes` | G1 | Banzuke changes table |
| 2.2 Standings by Wins | `standings_by_wins` | G1 | Standings table |
| 4.3.1 Banzuke Division by Era | `banzuke_division_by_era` | G1 | Stacked bar chart |
| 4.3.2 Makuuchi Rank by Era | `makuuchi_rank_by_era` | G1 | Stacked bar chart |
| 4.4 Division Stability | `division_stability` | G1 | Grouped line chart |
| 4.5.1 First Chii Appearance | `first_chii_appearance` | G1 | Ordered bar chart |
| 5.1 Finish by Chii | `finish_by_chii` | G1 | Threshold probability chart |
| 6.3.1 Win Probability by Standing | `win_probability_by_standing` | G1 | Filtered probability chart |
| 7.1 Basho Results | `basho_results_browser` | G1 | Indexed results table |
| 7.3.1 Career Length | `career_length` | G2 | Chart/table selected alternative |
| 7.3.2 Rank at Retirement | `rank_at_retirement` | G1 | Category bar chart |
| Typical Equelo Ratings | `typical_equelo_values` | G1 | Sectioned table |

These cases were enough to test ordinary charts, ordinary tables, indexed tables, filtered charts, sectioned tables, a banzuke-shaped table, and the selected-alternative pressure case.

## Important Findings

G1 covered more of the site than expected. Most pages have one visible artefact with optional filters and notes.

Career Length was the decisive pressure case. The first attempted structure implied that several widgets and artefacts were simultaneously present. The UI looked wrong because the parse was wrong. Once Career Length was modelled as selected alternatives, the rendering made sense.

Banzuke Changes showed that page-specific artefact renderers are still legitimate. The page is structurally G1, but the artefact renderer must genuinely switch between banzuke-style two-column rows and expanded one-column rows. That is not a CSS-only concern.

Finish by Chii clarified that producer outputs are not automatically public artefacts. The producer may emit additional diagnostic or legacy outputs, but the public page should expose only the artefact selected by the model.

Win Probability by Standing clarified that data fields with legacy names may have display-order semantics rather than true measurement semantics. The renderer should preserve the modelled category ordering without overinterpreting such fields.

The `NavigationBar` can be derived from the existing `make_site` navigation tree. Entries can be marked clickable when their page id is present in the make_site2 manifest registry, while non-migrated entries remain visible but inactive.

## What Worked

The prototype now renders migrated pages directly inside a shared `ContentPanel`.

The old iframe/page-shell dependency is removed for those pages.

Existing PA manifests were mostly reusable as artefact descriptions.

The shared renderer now owns common page structure: headings, filters, content placement, notes, navigation state, and branch selection.

The model was strong enough to expose modelling errors. In particular, Career Length was fixed by changing the structure rather than by hiding unwanted controls after rendering.

## What Remains Prototype-Only

make_site2 is not yet a full application version of `make_site`.

Current limitations include:

- It assembles existing generated output rather than rebuilding all required upstream data.
- It does not choose between live-store and history-zip data sources.
- It does not yet provide full CLI parity with `make_site`.
- It does not yet generate every manifest/envelope from a single production registry.
- Some artefact renderers are still prototype implementations.
- Styling and responsive behaviour are sufficient for model testing, not final publication polish.
- Deployment support exists only as a prototype wrapper over the existing `make_site` deployment helper.

These are make_site migration issues, not UI Model issues.

## Conclusion

The UI Model experiment is complete.

It demonstrated that public-page structure can be formalised through a small grammar set, that rendering can flow from the parsed structure, and that common UI behaviour can be shared instead of repeatedly hand-coded per page.

The working result is a model and renderer prototype, not a production replacement for `make_site`.

The next task is to plan and implement an incremental migration of `make_site` itself: build orchestration, data source selection, manifest generation, deployment policy, parity checks, and eventual cutover.

