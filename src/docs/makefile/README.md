# Makefile Docs

This folder contains project-wide notes for turning Sumo-Tools into a more explicit generated-output and build-dependency system.

The immediate purpose is to support a future Makefile-driven build by making the current producer/output/consumer graph visible before encoding it as build rules.

## Documents

- [01 Dependency Graph Model](01%20Dependency%20Graph%20Model.md)
- [02 Output and Module Classification](02%20Output%20and%20Module%20Classification.md)
- [03 Audit Workflow](03%20Audit%20Workflow.md)
- [04 Review Checklists](04%20Review%20Checklists.md)
- [05 PA Runtime Data Contracts](05%20PA%20Runtime%20Data%20Contracts.md)
- [Old Nav Tree](Old%20Nav%20Tree.md)

## Central idea

Generated files do not earn a permanent place merely by existing.

A generated output remains active only if it is canonical data, used by a non-legacy consumer, an unused non-legacy leaf, a declared future input, a selected research record, or an active diagnostic.

The website is one consumer of generated outputs, not a privileged special case. For `make_site2`, however, clickable navigation entries define the current website-output roots.

For clickable `make_site2` pages, the current website-output root includes every material public view reachable through declared Filters/options, not only the default browser view.

## Open issues

- Normalise vocabulary between these makefile audit docs and the existing `make_site2` documentation spine. In particular, reconcile audit terms such as `option axis`, `runtime data contract`, `aggregate payload`, `indexed payload family` and `reachable payload` with spine terms such as `Filter`, `material public state`, `PA data`, `required data reference`, `site-facing input`, `BuildOutput` and `BrowserRuntime`.
