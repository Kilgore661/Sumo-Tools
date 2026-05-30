# make_site2 Documentation

This directory is the active documentation set for `src/products/make_site2`.
It contains normative design documents, current audit records and focused
outcome notes for recent work not yet folded into the spine.

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
| HTML/CSS/runtime realisation | `05 Rendering Design.md` and `06 Rendering Audit and Changes.md` |
| Build output, runtime state, data staging | `07 Build, Output and Runtime Design.md` |
| Producer boundaries and migration | `08 Producer Integration and Migration.md` |
| Local/remote deployment | `09 Deployment and Operations.md` |
| Basho Results 7.1 redesign outcome | `Basho Results (7.1) Outcome.md` |

## Document Authority

| Kind | Documents | Authority |
| --- | --- | --- |
| Normative product contract | `01`, `02` | Defines what the product must do. |
| Normative design | `03`, `04`, `04.1`-`04.4`, `05`, `07`, `08`, `09` | Defines intended model and system behavior. |
| Current issue register | `10` | Records known gaps and deferred decisions. |
| Supporting audit | `06`, `10.1` | Records evidence and verification details; settled rules should move into normative docs. |
| Focused outcome notes | `Basho Results (7.1) Outcome.md` | Current account of a recent design/implementation slice that has not yet been folded into the spine. |
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

## Current Implementation Status

Implemented and verified:

- `Contents`, `PAPanel` and `Notes` are explicitly modelled.
- Notes render within the PA-owned region rather than spanning the
  FilterSection.
- Navigation links use canonical single-shell `?page=...` links.
- The modular browser runtime is active.

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
- Local deployment target-safety validation is still open.
- Some tests lag behind the modular runtime and manifest split.

## Temporary Documentation Gap

`Basho Results (7.1) Outcome.md` is the current account of the recent 7.1
Basho Results redesign. It has not yet been folded into the main documentation
spine.

Until that integration happens, treat the outcome note as authoritative for
7.1-specific table structure, result decomposition, temporal grouping and
Division Change rendering.

Known spine sections needing reconciliation include:

- `02 Specification.md`: confirm the Basho Results / Banzuke Changes boundary
  still says enough about represented-basho comparison.
- `05 Rendering Design.md`: replace older compact previous-result wording with
  the new decomposed result / Division Change model.
- `06 Rendering Audit and Changes.md`: update the Basho Results PA rendering
  audit row.
- `08 Producer Integration and Migration.md`: update the Basho Results / BRB
  pressure-case account to mention the transitional presentation-model
  renderer.
- `10.1 Selected History Coherence Audit.md`: preserve the History-coherence
  finding, but note that 7.1 table rendering has since changed.

## Running make_site2

Quick build from the small local History zip:

```powershell
py -m src.products.make_site2 --build-only --history-zip ".\files\output\Historys\1978_01 to 1980_11.zip"
```

This is useful for fast inspection. Until the Selected-History policy is
implemented, remember that some copied Pages may still represent current/full
producer output rather than the selected zip. Banzuke Changes is the known
example.

Full build using the live store:

```powershell
py -m src.products.make_site2 --build-only
```

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
