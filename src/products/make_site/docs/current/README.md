# Current make_site Docs

This directory contains the current working documentation for the generated
public site.

## Core Documents

| Document                                   | Role                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `Public Site Contract.md`                  | Consolidated current requirements, system contract, and design guardrails.                 |
| `Public UI Grammar.md`                     | Target page grammar: Heading + Options + PA manifest, with explicit URL-state policy.      |
| `PA Manifest Classes.md`                   | Target class model for PA manifests: TablePA, ChartPA, MultiViewPA, and EssayPA.           |
| `Implementation State.md`                  | Current implementation notes and known builder/site-definition state.                      |
| `Producer Writers and Prototype Embeds.md` | Policy for moving analysis outputs into the public site.                                   |
| `Table App Bundle Migration.md`            | Migration plan for turning current standalone table apps into make_site PA manifest writers. |
| `Remove Adapter Layer Proposal.md`         | Proposal for retiring deep-link adapters by moving promoted pages into the PA runtime model. |
| `Basho Results Browser Design Notes.md`    | Working design notes for the proposed Sumo History > Basho Results page.                   |
| `BRB Implementation Start Brief.md`         | Short handoff note for beginning BRB implementation from a fresh conversation.             |
| `Public Table Behaviour Inventory.md`      | Inventory of existing public table behaviours and BRB table precedents.                    |
| `Equelo Version Naming.md`                 | Canonical naming for Equelo model versions, diagnostic chart stages, and rating landmarks. |
| `TBD Register.md`                          | Live backlog of unresolved site, presentation, data, and documentation work.               |

## Reference Notes

The `reference/` directory preserves source notes that were consolidated into
`Public Site Contract.md` and `Implementation State.md`.

These files are retained deliberately:

* `reference/Public Site Requirements.md`
* `reference/Public Site Specification.md`
* `reference/Public Site Design.md`
* `reference/Make Site Builder Notes.md`
* `reference/Site Definition Handoff Memo.md`

## Reading Rule

These documents are allowed to overlap.

The priority order is:

1. explicit current policy notes, especially `Public UI Grammar.md`, `PA Manifest Classes.md`, and `Equelo Version Naming.md`;
2. `Public Site Contract.md`;
3. `Implementation State.md`;
4. `TBD Register.md` for open questions and known inconsistencies.
5. `reference/` notes for the full source trail behind consolidated material.

If a current document conflicts with archived material, prefer the current
document and preserve the archive as background.
