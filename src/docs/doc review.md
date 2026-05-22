I found **165 prose documentation files** in `src.zip` (`.md` / `.txt` / README-like files), totalling about **1.64 MB**. I also made a full path inventory here: [docs_inventory.md](sandbox:/mnt/data/docs_inventory.md).

## Overall state

The project documentation is **extensive, thoughtful, and unusually rich**, but it is also **uneven and in transition**.

The strongest area is `src/products/make_site/docs/current/`, which looks like the current canonical documentation set. It has a clear structure:

* `01 Public Site Model.md`
* `02 Rendering Model.md`
* `03 Implementation State.md`
* `04 Features and Applications.md`
* `05 Open Issues.md`
* `06 UI Model Implementation Contract.md`
* `_README.md`

This set is fresh, consolidated, and explicitly says the docs are meant to define a “constrained semantic publication system”. It also openly records that the implementation is still transitional: a static-site builder with an emerging PA-manifest/runtime model, not yet a finished semantic publication runtime.

## Main documentation clusters

| Area                  | Docs count | Approx. size | State                                                       |
| --------------------- | ---------: | -----------: | ----------------------------------------------------------- |
| `analysis/`           |         90 |       669 KB | Very well documented, but partly exploratory and historical |
| `infra/`              |         23 |       334 KB | Deep design-history docs; less current operational docs     |
| `products/make_site/` |         48 |       597 KB | Best current canonical docs; also large archive             |
| `sumo_core/`          |          4 |        41 KB | Some model docs, but comparatively sparse                   |

## What is good

The docs are not superficial. Many modules have real requirements, design, specification, rationale, implementation-state, and next-step documents.

The public-facing/product analysis tools are especially well covered:

* `analysis/standings/README.md`
* `analysis/banzuke_compare/README.md`
* `analysis/probability/README.md`
* `analysis/persistence/README.md`
* `analysis/sumo_history/basho_results/docs/README.md`

These READMEs explain what each tool is for, what it is not, the current product scope, architecture, main files, and output model. That is a strong sign that the documentation is being used to clarify product boundaries, not just record implementation notes.

`make_site` is the clearest documentation success. It has a current canonical set plus archived drafts, case studies, rendering notes, contracts, and open issues. The docs distinguish between intended semantic model, rendering model, implementation reality, and remaining gaps.

## Main problems

The biggest issue is **documentation lifecycle control**.

There are many old, archived, exploratory, and duplicate-looking docs. Examples include:

* `docs/old/` folders under `analysis/probability` and `analysis/standings`
* `products/make_site/docs/archive/`
* dated “Grand Plan”, “Epilogue”, “Next Steps”, and proposal documents
* placeholder-ish files such as `New Text Document.txt` and `the next bit.txt`
* generated/assistant-comparison notes like `Claude.txt`, `Gemini.txt`, `Grok.txt`, `Copilot.txt`

That is not necessarily bad, but it means a new maintainer could easily read the wrong thing unless each area has a “read this first / canonical vs archive” pointer. `make_site` now has that; many other areas only partly do.

There are also **coverage gaps**. Some code-heavy areas have little or no local docs/README:

* `analysis/equelo/fixed_v2`
* `analysis/sumo_history/career_lifecycle`
* `infra/live_store`
* `misc`
* `products/make_site/classes`
* `products/make_site/pa_manifest`
* `products/make_site/renderers`

Some of those are probably covered indirectly by higher-level docs, but locally they are not self-explanatory.

## Verdict

The documentation is in a **good but not yet mature** state.

It is strong as a design record and working notebook. It is strongest where the project is actively converging, especially `make_site`. It is weaker as a polished maintainer-facing documentation system because there is still too much historical material mixed near live material, and some important implementation packages lack local entry points.

I would describe the state as:

> **High-documentation, high-context, mid-consolidation.**
> The project has captured a great deal of intent and reasoning, but it still needs documentation gardening: canonical indexes, archive boundaries, stale-note cleanup, and local READMEs for implementation subpackages.

