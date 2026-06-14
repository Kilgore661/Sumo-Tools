# make_site2 Documentation

This directory is the active documentation set for `src/products/make_site2`.
It contains normative design documents, current audit records and supporting
outcome notes for recent work.

`make_site2` is a static publication layer. It assembles curated, precomputed
sumo analysis into a coherent public site. Producers own analytical computation;
`make_site2` owns public structure, planning, validation, rendering, output and
deployment.

## Current Reading Order

For orientation, read:

1. `01 Requirements.md`
2. `02 Specification.md`
3. `03 Architecture and Design Thesis.md`
4. `04 Model Design.md`
5. `10 Open Issues and Deferred Design.md`

Then read the detailed model/design document for the area being changed:

| Area | Read |
| --- | --- |
| Site declaration, navigation, page registry, status | `04.1 Site Definition Model.md` |
| Planning, inclusion, public view links, dependencies | `04.2 Publication Plan Model.md` |
| Visible page structure, filters, PAPanel, notes | `04.3 Public UI Model.md` |
| Tables, charts, artifact forms, PA-local meaning | `04.4 Published Artifact Model.md` |
| Basho Results (7.1) recursive table model | `04.5 Basho Results Model.md` |
| Most Consecutive Bouts (7.4.1) page contract | `02.6 Specification - Most Consecutive Bouts.md` |
| HTML/CSS/runtime realisation | `05 Rendering Design.md` and `06 Rendering Audit and Changes.md` |
| Build output, runtime state, data staging | `07 Build, Output and Runtime Design.md` |
| Producer boundaries and migration | `08 Producer Integration and Migration.md` |
| Local/remote deployment | `09 Deployment and Operations.md` |
| Notes, popovers and gloss policy | `11 Notes and Gloss.md` |
| Notes/gloss review procedure | `How to Review Notes and Gloss.md` |

## Document Authority

| Kind | Documents | Authority |
| --- | --- | --- |
| Normative product contract | `01`, `02` | Defines what the product must do. |
| Normative design | `03`, `04`, `04.1`-`04.5`, `05`, `07`, `08`, `09` | Defines intended model and system behavior. |
| Current issue register | `10` | Records known gaps and deferred decisions. |
| Supporting audit | `06`, `10.1` | Records evidence and verification details; settled rules should move into normative docs. |
| Supporting outcome notes | `Basho Results (7.1) Outcome.md` | Historical/supporting account of the 7.1 redesign now folded into `04.5`. |
| Supporting review procedure | `How to Review Notes and Gloss.md` | Describes how to review Notes/gloss without keeping a change diary. |
| Supporting policy | `11 Notes and Gloss.md` | Summarises reusable Notes/gloss rules and points unresolved work to `10`. |
| Background / style | `A Appendix - Better Models.md`, `House Style.md` | Useful context, not the main contract. |
| Historical | `archive/` | Evidence only; do not treat as current unless active docs say so. |

## Current Baseline

The active page grammar is:

```text
PublicUI -> NavigationBar . ContentPanel
NavigationBar -> <hider> . NavigationContent
NavigationContent -> <site caption> . QuickLinks? . Navigation
ContentPanel -> Heading . Contents
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
Notes -> <hider> . NotesContent
NotesContent -> Note*
```

The active public-link policy is:

```text
one static application shell
canonical link = selected Page + all applicable material Filter values
Navigation link = canonical default view of the selected Page
```

The active build/data policy is:

```text
An explicit History input selects the History/data instance for the whole built
site.

Every included promoted PA whose meaning depends on History must be derived
from, or validated against, that selected History.
```

The active Basho Results (7.1) policy is now in:

```text
04.5 Basho Results Model.md
```

Basho Results uses a specialised recursive/hierarchical table model because its
public meaning requires grouped reference, before, current/after and comparison
structure. This does not decide that ordinary flat table PAs should be recast
into the same shape.

## Current Implementation Status

Implemented and verified:

- `Contents`, `PAPanel` and `Notes` are explicitly modelled.
- Notes render within the PA-owned region rather than spanning the
  FilterSection.
- Navigation links use canonical single-shell `?page=...` links.
- The modular browser runtime is active.
- Basho Results (7.1) uses the recursive presentation-table model for the
  settled transitional slice, including leaf-heading sorting and Shikona links.
- Most Consecutive Bouts (7.4.1) is a promoted ordinary table PA under
  Sumo History > Records, with a `Clean only?` option and SumoDB-linked
  shikona values.

Known gaps:

- Selected-History coherence is the active production P0. `build_site(...)`
  accepts an explicit `History`/`history_zip`, but only Basho Results is
  currently derived from that resolved History. Other promoted PA inputs are
  copied from existing producer outputs without selected-History validation.
  Normal public/production output must not silently present those copied inputs
  as coherent. Quick inspection/development output may temporarily allow
  reduced or clearly caveated scope, but that policy still needs to be made
  explicit in code and visible output.
- Some Plotly line-chart pages have been observed with empty chart frames and
  need reproduction/triage.
- Basho Results table heading/data horizontal alignment revealed a broader table
  alignment modelling question recorded in `10 Open Issues and Deferred Design.md`.
- Local deployment target-safety validation is still open.
- Some tests lag behind the modular runtime and manifest split.

## Folded 7.1 Outcome Note

`Basho Results (7.1) Outcome.md` records the working outcome of the recent 7.1
redesign. Its settled model content has now been folded into
`04.5 Basho Results Model.md`. Treat the outcome note as supporting evidence, not
as an active authority competing with the spine.

## Running make_site2

Quick build from the small local History zip:

```powershell
py -m src.products.make_site2 --build-only --short
```

This is useful for fast inspection. `--short` is an alias for the standard small
History zip at `files/output/Historys/1978_01 to 1980_11.zip`. Until the
Selected-History policy is implemented, remember that some copied Pages may
still represent current/full producer output rather than the selected zip.
Banzuke Changes is the known example.

Full build using the live store:

```powershell
py -m src.products.make_site2 --build-only
```

To inspect structural whitespace, add `debug_layout=true` to a site URL. This
enables a development-only layout overlay that tints and labels the main
Navigation, ContentPanel, FilterSection, PAPanel, PA, table/chart and Notes
regions.

Avoid `--local-only` from Codex unless the local deployment target is visible.
The user's local web root may be on mapped drive `A:`, which Codex normally
cannot access.

## Running Tests

Use the repo-local virtual environment from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -s <test paths>
```

Use `-s` because this environment has previously shown pytest capture teardown
problems.
